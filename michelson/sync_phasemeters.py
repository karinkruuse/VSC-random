"""
Sync the 3 Moku phasemeter files (SC1/SC2/SC3) onto a common timebase, using
each file's last *recorded* channel -- a signal common to all 3 instruments,
wired into whichever input happens to be last that day -- to find the time
offset of each file. SC1 is the reference: its own native sample times are
used as the output grid, untouched. SC2 and SC3 are shifted onto that grid
by their offset (via interpolation, since the offsets aren't whole samples).

Which physical input carries the sync signal (and how many inputs are
recorded at all) can change between recordings: inputs get switched on/off,
and the header's comma-separated label line isn't always kept in sync with
that (e.g. a channel dropped from acquisition but left in the label list).
So the label list is matched positionally to whichever "Input N" columns are
actually present in the .npy file, and the *last of those* is always treated
as the sync tap, regardless of what it's labeled -- it may double as a
regular reference channel too (e.g. labeled "REF3"), in which case it's
saved under both names.

Output: data/synced_phasemeter_data.npz containing, for each slot (keyed by
its filename prefix, e.g. "sc1", "sc2") and each of its recorded data
channels (keyed by the channel's header label, e.g. "c12", "sb12"):
    time_s                  -- common time axis (s)
    <slot>_<label>          -- Input phase (cyc), detrended
    <slot>_<label>_freq     -- Input frequency (Hz), raw
    <slot>_sync             -- alias for whichever <slot>_<label> is that
                                slot's sync tap (same physical signal in all
                                3 slots -- kept per-slot, under this stable
                                name, so any two slots' sync channels can be
                                directly cross-correlated to check/refine
                                their relative clock sync)
    <slot>_sync_freq        -- alias for that channel's frequency (Hz), raw
"""
import glob
import json
import os
import re

import matplotlib.pyplot as plt
import numpy as np
from pytdi.dsp import timeshift as lagrange_timeshift
from scipy.interpolate import interp1d
from scipy.optimize import minimize_scalar
from scipy.signal import csd, detrend, welch

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUT_NPZ = os.path.join(DATA_DIR, "synced_phasemeter_data.npz")
OUT_PLOT = os.path.join(os.path.dirname(__file__), "synced_overview.png")
OUT_PLOT_RAW = os.path.join(os.path.dirname(__file__), "unsynced_sync_channels.png")
OFFSET_CACHE = os.path.join(DATA_DIR, "sync_offsets_cache.json")

MAX_OFFSET_S = 3.0  # search window for inter-instrument start delay
FMIN = 5e-4  # Hz -- cost = residual PSD integrated over [FMIN, FMAX]
FMAX = 0.1  # Hz
COARSE_STEP_S = 0.1
SYNC_WINDOW_S = 100.0  # only use this much data to find the offset -- much faster,
# and the offset is a single scalar so it doesn't need the full record to pin down
ZOOM_WINDOW_S = 100.0  # width of the sync-check zoom plot

# Recordings where the sync tone's dither modulation is switched off partway
# through carry their own, much stronger sync fiducial than the PSD search
# below: the same physical on/off event is stamped into every slot's sync
# channel, just at a different point on each instrument's own local clock.
# Window width (s) and high/low-plateau amplitude ratio used to find it --
# see find_amplitude_transition().
TRANSITION_WINDOW_S = 0.25
TRANSITION_MIN_RATIO = 2.0

# Where to look for that on/off transition, in minutes into the recording --
# restricting the search avoids picking up spurious amplitude dips elsewhere
# in the record. Each slot's own local (unsynced) clock is used, same as
# TRANSITION_WINDOW_S above.
TRANSITION_SEARCH_START_MIN = 48.4
TRANSITION_SEARCH_WINDOW_MIN = 1

# Manual override: known instrument start times (s, on a common clock) from
# the experiment log, used only if neither the transition detector above nor
# the PSD search below can pin down an offset. Specific to one recording
# session -- update (or clear to {}) before reusing across sessions.
MANUAL_START_TIMES_S = {}

# Fractional-offset refinement (refine_offset_csd): band where the sync
# channel is coherent between instruments *and* a constant delay has
# leverage (residual phase grows linearly with f) -- deliberately separate
# from FMIN/FMAX above, which target the slow, non-coherent drift the PSD
# fallback search looks at. This uses the whole record via the cross-
# spectral phase slope, not a short window, so it resolves offsets far
# finer than one sample.
OFFSET_FMIN = 1.0  # Hz
OFFSET_FMAX = 8.0  # Hz
OFFSET_COHERENCE_MIN = 0.95
OFFSET_CSD_NPERSEG = 2 ** 16

# Fractional resampling (apply_offset): order for the Lagrange-interpolated
# fractional-sample shift, and how many samples to crop off each end
# afterward to discard its edge transient.
RESAMPLE_ORDER = 31
EDGE_CROP_SAMPLES = 16


def parse_header(txt_path):
    """Return (channel_labels, input_nums, rate) for a phasemeter .txt header.

    channel_labels is the comma-separated list on the line right before the
    "# % Time (s), ..." column-names line (e.g. ["c12", "sb12", ..., "REF3"]
    for SC1, or ["c", "SB", "Sync"] for SC2/SC3). input_nums is the actual
    "Input N" column numbers present on that column-names line, in order
    (some inputs may be switched off and so have no columns at all -- e.g.
    input 3 off, input 4 on -- so this doesn't always run 1..n).

    labels is matched to input_nums positionally. If a channel was dropped
    from acquisition but the label comment wasn't updated to match, there
    will be more labels than columns -- assume it's stale trailing labels
    and drop them, since inputs are switched off from the end in practice.
    """
    lines = []
    rate = None
    with open(txt_path) as f:
        for line in f:
            lines.append(line.rstrip("\n"))
            m = re.match(r"#\s*%\s*Acquisition rate:\s*([\d.eE+-]+)", line)
            if m:
                rate = float(m.group(1))
    time_idx = next(i for i, l in enumerate(lines) if re.match(r"#\s*%\s*Time\s*\(s\)", l))
    labels_line = lines[time_idx - 1]
    labels = [s.strip() for s in re.sub(r"^#\s*%\s*", "", labels_line).split(",")]

    input_nums = []
    for n in re.findall(r"Input (\d+) Phase \(cyc\)", lines[time_idx]):
        n = int(n)
        if n not in input_nums:
            input_nums.append(n)

    if len(labels) > len(input_nums):
        labels = labels[:len(input_nums)]
    elif len(labels) < len(input_nums):
        raise ValueError(
            f"{txt_path}: {len(input_nums)} data channels recorded but only "
            f"{len(labels)} labels given ({labels})"
        )

    return labels, input_nums, rate


def sanitize_key(label, used):
    key = re.sub(r"\s+", "_", label.strip().lower())
    key = re.sub(r"[^a-z0-9_]", "", key)
    if key in used:
        key = f"{key}_{used[key]}"
    used[label] = used.get(label, 0) + 1
    return key


def load_slot(npy_path):
    txt_path = npy_path.replace(".npy", ".txt")
    labels, input_nums, rate = parse_header(txt_path)
    data = np.load(npy_path)

    channels = {}
    for label, i in zip(labels, input_nums):
        channels[label] = {
            "phase": data[f"Input {i} Phase (cyc)"],
            "freq": data[f"Input {i} Frequency (Hz)"],
        }

    # the last *recorded* channel is always the common-mode sync tap, by
    # wiring convention -- regardless of what it happens to be labeled (it
    # may double as a regular reference channel, e.g. "REF3")
    sync_label = labels[-1]

    return {
        "path": npy_path,
        "name": os.path.basename(npy_path).split("_")[0],  # e.g. "SC1"
        "rate": rate,
        "t": data["Time (s)"],
        "labels": labels,  # all recorded data channels, including the sync tap
        "channels": channels,
        "sync_label": sync_label,
        "sync_phase": channels[sync_label]["phase"],
        "sync_freq": channels[sync_label]["freq"],
    }


def detrend_linear(t, x):
    """Remove a best-fit linear ramp (e.g. from the set-frequency not
    exactly matching the real signal frequency) and return (residual, slope_hz)."""
    slope, intercept = np.polyfit(t, x, 1)
    return x - (slope * t + intercept), slope


def find_amplitude_transition(t, phase, rate):
    """Find the local time of the rising edge of the first prominent burst
    in a rolling peak-to-peak amplitude of `phase` -- e.g. a brief
    dither-modulation pulse on the sync tone. Returns None if nothing
    clearly stands out above the baseline noise floor (e.g. no modulation
    in this window).

    This is a much stronger sync fiducial than the spectral offset search
    below when it's available: it's a single sharp, shared physical event,
    not a statistical property of noisy drift that a short recording may
    not resolve well. The burst's *edges* are used rather than its peak --
    the plateau on top of a burst can ripple (e.g. a beat pattern), so the
    location of its max sample isn't a stable fiducial, but the edges
    where amplitude crosses the halfway threshold are sharp (~1 sample).
    """
    if len(t) < 2:
        return None
    detrended, _ = detrend_linear(t, phase)
    win = max(1, int(TRANSITION_WINDOW_S * rate))
    step = max(1, win // 8)
    idxs = np.arange(0, len(detrended) - win, step)
    if len(idxs) < 20:
        return None
    amp = np.array([np.ptp(detrended[i:i + win]) for i in idxs])
    t_centers = t[idxs] + 0.5 * win / rate

    baseline = np.median(amp)
    peak = np.max(amp)
    if peak < TRANSITION_MIN_RATIO * max(baseline, 1e-12):
        return None
    thresh = 0.5 * (peak + baseline)

    above = amp > thresh
    rise_idx = next((i for i in range(1, len(above)) if not above[i - 1] and above[i]), None)
    if rise_idx is None:
        return None

    a0, a1 = amp[rise_idx - 1], amp[rise_idx]
    t0, t1 = t_centers[rise_idx - 1], t_centers[rise_idx]
    frac = 0.5 if a0 == a1 else (thresh - a0) / (a1 - a0)
    return t0 + frac * (t1 - t0)


def residual_for_offset(t, ref_sig, other_sig, offset, dt):
    """ref(t) - other(t + offset), edge-cropped, detrended."""
    other_interp = interp1d(t, other_sig, kind="cubic", bounds_error=False, fill_value=np.nan)
    other_shifted = other_interp(t + offset)

    n_crop = int(np.ceil(abs(offset) / dt)) + 5
    sl = slice(n_crop, -n_crop)
    return detrend(ref_sig[sl] - other_shifted[sl])


def cost(offset, t, ref_sig, other_sig, dt, fs):
    residual = residual_for_offset(t, ref_sig, other_sig, offset, dt)
    nperseg = min(int(fs / FMIN), len(residual))
    f, psd = welch(residual, fs=fs, nperseg=nperseg, detrend="constant")
    mask = (f >= FMIN) & (f <= FMAX)
    return np.trapezoid(psd[mask], f[mask])


def estimate_offset(ref, other):
    """Return the time (s) that `other`'s clock lags `ref`'s clock by.

    i.e. a sample recorded by `other` at its own time `u` was really taken
    at reference-frame time `u + offset`.

    Same spectral (PSD-minimization) method used for the physical delay
    estimate: for a trial offset, shift other's Sync channel and form the
    residual against ref's Sync channel. Sync carries no physical delay --
    it's the same signal in every slot -- so the true offset is the one
    where the residual PSD collapses to near-nothing (a much sharper, more
    reliable signal than a plain cross-correlation, which the large
    non-linear shared drift between slots can easily swamp).
    """
    dt = 1.0 / ref["rate"]
    fs = ref["rate"]

    other_sync_on_ref_t = interp1d(other["t"], other["sync_phase"], kind="cubic",
                                    bounds_error=False, fill_value=np.nan)(ref["t"])
    mask = ~np.isnan(other_sync_on_ref_t)
    t = ref["t"][mask]
    ref_sig = ref["sync_phase"][mask]
    other_sig = other_sync_on_ref_t[mask]

    # only need a short window to pin down a single scalar offset -- using
    # the full multi-thousand-second record here is needlessly slow, since
    # cost() reruns an interpolation + Welch PSD for every trial offset
    window_n = int(SYNC_WINDOW_S * fs)
    if window_n < len(t):
        start = (len(t) - window_n) // 2
        sl = slice(start, start + window_n)
        t, ref_sig, other_sig = t[sl], ref_sig[sl], other_sig[sl]

    # coarse scan to bracket the global minimum, then refine
    taus = np.arange(-MAX_OFFSET_S, MAX_OFFSET_S + COARSE_STEP_S, COARSE_STEP_S)
    costs = np.array([cost(tau, t, ref_sig, other_sig, dt, fs) for tau in taus])
    tau0 = taus[np.argmin(costs)]

    result = minimize_scalar(
        cost, bounds=(tau0 - COARSE_STEP_S, tau0 + COARSE_STEP_S), method="bounded",
        args=(t, ref_sig, other_sig, dt, fs), options={"xatol": 1e-6},
    )
    print(f"    coarse min at tau={tau0:+.2f} s, refined tau={result.x:+.6f} s "
          f"(cost={result.fun:.3e}, cost at tau=0: {costs[np.argmin(np.abs(taus))]:.3e})")

    # residual_for_offset uses ref(t) - other(t + tau), i.e. other(u) ~= ref(u - tau)
    # => other's own time u maps to reference-frame time (u - tau) => offset = -tau
    return -result.x


def coherent_phase_slope(ref, other, coarse_offset):
    """Cross-spectral phase slope between the two sync channels, in a band
    where they're coherent and a constant delay has leverage, after
    shifting `other` by `coarse_offset`.

    Returns (slope [rad/Hz], n_coherent_bins). A constant residual time
    offset appears as a *linear* phase slope vs frequency in the
    cross-spectrum (phase = -2*pi*f*offset); restricting to bins with high
    coherence keeps the fit from being dragged around by bins where the
    two channels aren't actually measuring the same thing (e.g. outside
    the sync tone's own bandwidth). Uses the whole record via csd/welch,
    not a short window.
    """
    fs = ref["rate"]
    other_shifted = interp1d(other["t"] + coarse_offset, other["sync_phase"], kind="cubic",
                              bounds_error=False, fill_value=np.nan)(ref["t"])
    mask = ~np.isnan(other_shifted)
    ref_sig = ref["sync_phase"][mask]
    other_sig = other_shifted[mask]

    nperseg = min(OFFSET_CSD_NPERSEG, len(ref_sig))
    f, Pxy = csd(ref_sig, other_sig, fs=fs, nperseg=nperseg)
    _, Px = welch(ref_sig, fs=fs, nperseg=nperseg)
    _, Py = welch(other_sig, fs=fs, nperseg=nperseg)
    coh = np.abs(Pxy) ** 2 / (Px * Py)

    band = (f >= OFFSET_FMIN) & (f <= OFFSET_FMAX) & (coh > OFFSET_COHERENCE_MIN)
    if band.sum() < 3:
        return None, int(band.sum())

    slope = np.polyfit(f[band], np.unwrap(np.angle(Pxy[band])), 1)[0]
    return slope, int(band.sum())


def refine_offset_csd(ref, other, coarse_offset):
    """Refine a coarse time offset to sub-sample precision via the
    cross-spectral phase slope between the two sync channels (see
    coherent_phase_slope). Falls back to the coarse offset, unchanged, if
    there aren't enough coherent bins in [OFFSET_FMIN, OFFSET_FMAX] to fit
    a slope -- e.g. the sync tone isn't actually coherent there for this
    recording.

    Sign convention (empirically verified against find_amplitude_transition
    on real data, converging to the same refined offset from multiple,
    independently-noisy coarse starting points): delta = +slope / (2*pi).
    """
    slope, n_bins = coherent_phase_slope(ref, other, coarse_offset)
    if slope is None:
        print(f"    only {n_bins} coherent bins in [{OFFSET_FMIN}, {OFFSET_FMAX}] Hz "
              f"(need >=3, coherence > {OFFSET_COHERENCE_MIN}) -- keeping coarse offset")
        return coarse_offset

    delta = slope / (2 * np.pi)
    print(f"    CSD refinement: {n_bins} coherent bins, phase slope={slope:.6e} rad/Hz, "
          f"delta={delta:+.6e} s")
    return coarse_offset + delta


def apply_offset(channel, offset, dt):
    """Shift `channel` (uniformly sampled at spacing `dt`) by `offset`
    seconds, split into an exact integer-sample re-index plus a fractional-
    sample Lagrange-interpolated shift (order RESAMPLE_ORDER) -- instead of
    a single cubic interpolation over the whole (possibly many-sample)
    offset, which needlessly smooths/blurs a shift that's mostly just a
    re-indexing operation.
    """
    n = int(round(offset / dt))
    frac = offset / dt - n
    shifted = lagrange_timeshift(channel, -frac, order=RESAMPLE_ORDER)
    return np.roll(shifted, n)


def files_signature(npy_files):
    return [{"name": os.path.basename(p), "size": os.path.getsize(p)} for p in npy_files]


def load_cached_offsets(npy_files):
    if not os.path.exists(OFFSET_CACHE):
        return None
    try:
        with open(OFFSET_CACHE) as f:
            cache = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    if cache.get("files") != files_signature(npy_files):
        return None
    return cache.get("offsets")


def save_offset_cache(npy_files, offsets):
    with open(OFFSET_CACHE, "w") as f:
        json.dump({"files": files_signature(npy_files), "offsets": offsets}, f, indent=2)


def main():
    npy_files = sorted(glob.glob(os.path.join(DATA_DIR, "SC*_*.npy")))
    if not npy_files:
        raise SystemExit(f"No Moku phasemeter .npy files found in {DATA_DIR}")

    slots = [load_slot(p) for p in npy_files]
    ref = slots[0]

    # each slot's sync channel on its own raw, un-shifted local clock -- i.e.
    # before any offset correction, so the raw start-time misalignment (and
    # each channel's own label, e.g. SC1's is really "REF3") is visible
    fig_raw, ax_raw = plt.subplots(figsize=(11, 5))
    for s in slots:
        detrended, _ = detrend_linear(s["t"], s["sync_phase"])
        ax_raw.plot(s["t"], detrended, label=f"{s['name']} ({s['sync_label']})")
    ax_raw.set_xlabel("Own local time (s), unsynced")
    ax_raw.set_ylabel("Sync channel phase (cyc), linear ramp removed")
    ax_raw.set_title("Sync channels, raw local time -- before any offset correction")
    ax_raw.legend(fontsize=8)
    fig_raw.tight_layout()
    fig_raw.savefig(OUT_PLOT_RAW, dpi=150)
    print(f"Saved {OUT_PLOT_RAW}")

    search_start_s = TRANSITION_SEARCH_START_MIN * 60.0
    search_end_s = search_start_s + TRANSITION_SEARCH_WINDOW_MIN * 60.0
    print(f"Looking for the sync transition in [{TRANSITION_SEARCH_START_MIN:.1f}, "
          f"{TRANSITION_SEARCH_START_MIN + TRANSITION_SEARCH_WINDOW_MIN:.1f}] min "
          f"({search_start_s:.0f}-{search_end_s:.0f} s) of each slot's own local clock")
    transitions = []
    for s in slots:
        win_mask = (s["t"] >= search_start_s) & (s["t"] <= search_end_s)
        transitions.append(find_amplitude_transition(s["t"][win_mask], s["sync_phase"][win_mask], s["rate"]))

    if all(tr is not None for tr in transitions):
        offsets = [transitions[0] - tr for tr in transitions]
        print("Found a modulation on/off transition in every slot's sync channel -- "
              "using it as the sync fiducial, not the spectral search:")
        for s, tr, off in zip(slots[1:], transitions[1:], offsets[1:]):
            print(f"{os.path.basename(s['path'])}: transition at local t={tr:.4f} s, "
                  f"offset = {off:+.4f} s relative to {os.path.basename(ref['path'])}")
    elif all(s["name"] in MANUAL_START_TIMES_S for s in slots):
        offsets = [MANUAL_START_TIMES_S[s["name"]] - MANUAL_START_TIMES_S[ref["name"]] for s in slots]
        print("Using manually specified start-time offsets (MANUAL_START_TIMES_S), "
              "not the automatic search:")
        for s, off in zip(slots[1:], offsets[1:]):
            print(f"{os.path.basename(s['path'])}: offset = {off:+.4f} s relative to {os.path.basename(ref['path'])}")
    elif (cached_offsets := load_cached_offsets(npy_files)) is not None:
        offsets = cached_offsets
        print(f"Reusing cached sync offsets from {OFFSET_CACHE} "
              f"(same input files as last time -- delete this file to force a recompute):")
        for s, off in zip(slots[1:], offsets[1:]):
            print(f"{os.path.basename(s['path'])}: offset = {off:+.4f} s relative to {os.path.basename(ref['path'])}")
    else:
        offsets = [0.0]
        for s in slots[1:]:
            off = estimate_offset(ref, s)
            offsets.append(off)
            print(f"{os.path.basename(s['path'])}: offset = {off:+.4f} s relative to {os.path.basename(ref['path'])}")
        save_offset_cache(npy_files, offsets)
        print(f"Saved offsets to {OFFSET_CACHE} for reuse next time")

    # whatever produced the coarse offsets above, refine them to sub-sample
    # precision via the cross-spectral phase slope in the coherent band --
    # this uses the whole record and is far more precise than any of the
    # coarse methods (see refine_offset_csd)
    print(f"Refining offsets via cross-spectral phase slope in "
          f"[{OFFSET_FMIN}, {OFFSET_FMAX}] Hz:")
    for i, s in enumerate(slots[1:], start=1):
        coarse = offsets[i]
        offsets[i] = refine_offset_csd(ref, s, coarse)
        print(f"{os.path.basename(s['path'])}: {coarse:+.6f} s -> {offsets[i]:+.6f} s")

    # each slot's samples, expressed in the shared reference-frame time axis
    for s, off in zip(slots, offsets):
        s["t_ref_frame"] = s["t"] + off

    dt = 1.0 / ref["rate"]

    # use SC1's own native sample times as the output grid, cropped to where
    # all 3 slots have data after their offsets are applied -- SC1 (offset
    # 0 by definition) is never resampled/touched, only SC2 and SC3 get
    # shifted (via apply_offset: exact integer re-index + fractional
    # Lagrange interpolation) onto SC1's grid. j_start/j_end are absolute
    # indices into SC1's own array -- apply_offset's output stays on that
    # same absolute index basis (a roll, not a re-interpolation onto a new
    # array), so slicing every slot's shifted channel with the same
    # [j_start:j_end] is what actually lines them up.
    t_start = max(s["t_ref_frame"][0] for s in slots)
    t_end = min(s["t_ref_frame"][-1] for s in slots)
    ref_mask = (ref["t"] >= t_start) & (ref["t"] <= t_end)
    j_start = int(np.argmax(ref_mask))
    j_end = j_start + int(ref_mask.sum())
    common_t = ref["t"][j_start:j_end]

    # save every slot's own sync tap too (not just slot 1's) -- it carries
    # no physical delay, so a downstream script can cross-correlate any two
    # slots' sync channels directly to check/refine their relative clock
    # sync, instead of only having it available relative to slot 1. It's
    # exposed under a stable "<slot>_sync" name in addition to its own
    # label (they're the same key when the label literally is "Sync"; kept
    # separate, as an alias onto the same array, when it doubles as a named
    # reference channel like "REF3").
    # Frequency channels are saved too (raw, not detrended) so a downstream
    # script can do clock-noise correction: jitter = phase_sync / freq_sync
    # [s], correction = freq_data * jitter [cyc].
    out = {"time_s": common_t}
    data_keys = []
    extra_sync_keys = []
    for s, off in zip(slots, offsets):
        prefix = s["name"].lower()
        used_keys = {}
        label_to_key = {}
        is_ref = s is ref
        for label in s["labels"]:
            phase_raw = s["channels"][label]["phase"]
            freq_raw = s["channels"][label]["freq"]
            if is_ref:
                # SC1 is the reference grid itself -- just slice, no
                # resampling needed (or wanted: it's the one slot with no
                # offset/shift applied)
                phase_vals = phase_raw[j_start:j_end]
                freq_vals = freq_raw[j_start:j_end]
            else:
                if len(phase_raw) < j_end:
                    raise ValueError(
                        f"{s['path']}: only {len(phase_raw)} samples, need >= {j_end} "
                        f"for the shift+crop to land on valid (non-wrapped) data"
                    )
                phase_vals = apply_offset(phase_raw, off, dt)[j_start:j_end]
                freq_vals = apply_offset(freq_raw, off, dt)[j_start:j_end]
            key = f"{prefix}_{sanitize_key(label, used_keys)}"
            out[key] = phase_vals
            out[f"{key}_freq"] = freq_vals
            data_keys.append(key)
            label_to_key[label] = key

        sync_key = f"{prefix}_sync"
        if sync_key != label_to_key[s["sync_label"]]:
            out[sync_key] = out[label_to_key[s["sync_label"]]]
            out[f"{sync_key}_freq"] = out[f"{label_to_key[s['sync_label']]}_freq"]
            extra_sync_keys.append(sync_key)

    # discard the Lagrange fractional-shift's edge transient (order//2 + 1
    # samples on each side), consistently on every channel including SC1's
    # (which wasn't itself shifted, but must stay the same length/alignment
    # as the shifted channels)
    common_t = common_t[EDGE_CROP_SAMPLES:-EDGE_CROP_SAMPLES]
    out = {k: v[EDGE_CROP_SAMPLES:-EDGE_CROP_SAMPLES] for k, v in out.items()}

    # the set frequency never exactly matches the real signal frequency, so
    # each phase channel has a linear ramp on top of the interesting signal
    # -- remove it with a best-fit line
    print()
    for key in data_keys + extra_sync_keys:
        out[key], slope = detrend_linear(common_t, out[key])
        print(f"{key}: removed linear ramp of {slope:.6f} cyc/s ({slope:.6f} Hz)")

    # by now every slot's "<slot>_sync" key exists (either set directly
    # above, or already in data_keys because the label literally is "Sync")
    sync_keys = [f"{s['name'].lower()}_sync" for s in slots]

    # verify the thing that actually matters: NOT that the sync channels
    # visually overlap (they won't -- there's real differential wander at
    # low f that's the sideband stage's job to remove later), but that the
    # *constant* offset was removed to full precision -- i.e. the
    # cross-spectral phase between them has ~zero residual linear slope
    # in the coherent band after resampling. A non-zero slope here means a
    # leftover constant time offset; everything else in this band is jitter.
    print()
    print(f"Verifying resampling via residual cross-spectral phase slope in "
          f"[{OFFSET_FMIN}, {OFFSET_FMAX}] Hz (should be ~0; sync channels "
          f"themselves are not expected to overlap):")
    fs = ref["rate"]
    for key in sync_keys[1:]:
        nperseg = min(OFFSET_CSD_NPERSEG, len(out[sync_keys[0]]))
        f, Pxy = csd(out[sync_keys[0]], out[key], fs=fs, nperseg=nperseg)
        _, Px = welch(out[sync_keys[0]], fs=fs, nperseg=nperseg)
        _, Py = welch(out[key], fs=fs, nperseg=nperseg)
        coh = np.abs(Pxy) ** 2 / (Px * Py)
        band = (f >= OFFSET_FMIN) & (f <= OFFSET_FMAX) & (coh > OFFSET_COHERENCE_MIN)
        if band.sum() < 3:
            print(f"  {sync_keys[0]} vs {key}: only {band.sum()} coherent bins -- can't verify")
            continue
        slope = np.polyfit(f[band], np.unwrap(np.angle(Pxy[band])), 1)[0]
        print(f"  {sync_keys[0]} vs {key}: residual phase slope {slope:+.3e} rad/Hz "
              f"({slope / (2 * np.pi):+.3e} s equivalent, {band.sum()} coherent bins)")

    np.savez(OUT_NPZ, **out)
    print(f"\nSaved {OUT_NPZ}")
    print("Keys:", list(out.keys()))

    # --- sync-check plot ---
    fig, (ax_a, ax_b, ax_zoom) = plt.subplots(3, 1, figsize=(11, 10))

    for key in data_keys:
        ax_a.plot(common_t, out[key], label=key)
    ax_a.set_ylabel("Phase (cyc), detrended")
    ax_a.set_title("Data channels -- all slots, synced + linear ramp removed (as saved)")
    ax_a.legend(fontsize=8)

    # each instrument demodulates the sync channel at a slightly different
    # set frequency, so the raw sync phase has a different linear ramp per
    # slot that would otherwise swamp this comparison -- use the
    # linear-detrended version (out[sync_key], same as saved to the npz).
    # NB these are *not* expected to overlap even with a perfect constant-
    # offset sync: the wander here is real, differential low-frequency
    # jitter (from the sideband stage), not a sync error -- see the
    # residual cross-spectral phase-slope check printed above for the
    # actual verification that the constant offset was removed correctly.
    for key in sync_keys:
        ax_b.plot(common_t, out[key], label=key)
    ax_b.set_ylabel("Sync channel phase (cyc), detrended")
    ax_b.set_title("Sync channel (common to all slots), full duration, linear ramp removed per slot")
    ax_b.legend(fontsize=8)

    # the full-record linear detrend still leaves a slow, non-linear
    # residual drift (visible in the panel above) whose level at this
    # particular moment differs slot to slot -- detrend again, just over
    # this window, so that offset doesn't swamp the fine structure we
    # actually want to compare here.
    # zoom on the same window used to search for the modulation transition
    # (the most informative place to check sync worked), falling back to a
    # window mid-record if that search window falls outside this recording
    zoom_start = TRANSITION_SEARCH_START_MIN * 60.0
    zoom_width = TRANSITION_SEARCH_WINDOW_MIN * 60.0
    zoom_label = f"transition-search window [{TRANSITION_SEARCH_START_MIN:.1f}-{TRANSITION_SEARCH_START_MIN + TRANSITION_SEARCH_WINDOW_MIN:.1f}] min"
    if zoom_start > common_t[-1] or zoom_start + zoom_width < common_t[0]:
        zoom_start = common_t[0] + 0.5 * (common_t[-1] - common_t[0])
        zoom_width = ZOOM_WINDOW_S
        zoom_label = "mid-record (transition-search window outside this recording)"
    zoom_mask = (common_t >= zoom_start) & (common_t <= zoom_start + zoom_width)
    for key in sync_keys:
        ax_zoom.plot(common_t[zoom_mask], detrend(out[key][zoom_mask]), label=key)
    ax_zoom.set_ylabel("Sync channel phase (cyc), window-detrended")
    ax_zoom.set_xlabel("Common time (s)")
    ax_zoom.set_title(f"Sync channel, {zoom_width:.0f} s zoom on {zoom_label} "
                      f"-- ripple/edges should line up (see phase-slope check above for the real verification)")
    ax_zoom.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT_PLOT, dpi=150)
    print(f"Saved {OUT_PLOT}")


if __name__ == "__main__":
    main()
