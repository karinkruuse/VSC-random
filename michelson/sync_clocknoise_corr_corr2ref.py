"""
Sync the 2 Moku clock-noise-correlation files (corr1/corr2) onto a common
timebase, using each file's "dds" channel -- a signal common to both
instruments -- to find the relative clock offset. corr2 is the reference:
its own native sample times are used as the output grid, untouched. corr1 is
shifted onto that grid by the estimated offset (via interpolation, since
the offset isn't a whole number of samples).

This is the mirror-image of sync_clocknoise_corr.py, which keeps corr1 as
the reference grid and shifts corr2 -- everything else (offset-estimation
methods, gating logic, output format) is identical, just with the two
slots' roles swapped.

Offset is estimated using only the first WINDOW_S seconds of the dds
channels, from THREE independent methods that are cross-checked against
each other (see find_phase_step / estimate_offset / refine_offset_csd):

  1. A "clapboard" fiducial: both dds channels carry a single, sharp,
     shared phase step in this window (a deliberate one-off kick injected
     into the dds source) -- by far the single largest sample-to-sample
     jump in either channel, ~50-100x anything else nearby. Locating it on
     each instrument's own clock and differencing gives a direct,
     unambiguous offset with no fitting involved.
  2. A coarse band-limited cross-correlation (same idea sync_phasemeters.py
     uses on its sync tap, just scoped to this fixed start-of-record window
     instead of its "last recorded channel" convention -- these files don't
     share that wiring convention, so each file's channel map is given
     explicitly below, from its own .txt header comment "% chN: name").
  3. A cross-spectral phase-slope refinement of (2), for sub-sample
     precision.

Method 3 turns out NOT reliable on this data: the [OFFSET_FMIN, OFFSET_FMAX]
Hz band's phase-vs-frequency relationship isn't perfectly linear here, so
np.unwrap can lock onto the wrong branch -- a self-consistent but wrong
slope, off by a whole cycle at some frequency inside the band (observed:
~1 cycle at ~1.5 Hz, i.e. a ~0.67 s error that method 2's coarse estimate
alone doesn't have, and that method 1 -- unrelated to spectral fitting --
independently confirms is wrong). So method 3's result is only trusted when
it agrees with method 1 to within CSD_MAX_DISAGREEMENT_S; otherwise method 1
is used as the final offset. See main() for the actual gating logic.

Unlike sync_phasemeters.py's 3 slots, corr1 and corr2 are NOT on a shared
clock: per each file's own .txt header, corr1 (Moku:Delta) is locked to an
external 10 MHz + 1 PPS reference, while corr2 (Moku:Pro) runs on its own
free-running internal 10 MHz clock. So the single constant offset applied
here only removes the *fixed* start-time misalignment seen near the start
of the record -- it deliberately leaves the two instruments' real relative
clock drift over the rest of the ~2h record untouched, since that drift is
the physical clock-noise signal this experiment is measuring, not a sync
error to correct out. Don't expect the dds channels to stay coherent over
the full record after this correction; growing decoherence away from t=0
is expected.

Channel maps:
    corr1 (Moku:Delta): ch1 eta12, ch2 zeta_L_12, ch3 zeta_U_12, ch4 dds,
                         ch5 SYSREF1, ch6 SYSREF2
    corr2 (Moku:Pro):   ch1 eta21, ch2 zeta_U_21, ch3 dds

Output: data/no sb/synced_clocknoise_corr_corr2ref.npz containing:
    time_s              -- common time axis (s), corr2's native grid
    <slot>_<label>       -- Input phase (cyc), detrended
    <slot>_<label>_freq  -- Input frequency (Hz), raw
"""
import os
import re

import matplotlib.pyplot as plt
import numpy as np
from pytdi.dsp import timeshift as lagrange_timeshift
from scipy.interpolate import interp1d
from scipy.signal import butter, correlate, correlation_lags, csd, detrend, sosfiltfilt, welch

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "no sb")
OUT_NPZ = os.path.join(DATA_DIR, "synced_clocknoise_corr_corr2ref.npz")
OUT_PLOT = os.path.join(os.path.dirname(__file__), "synced_clocknoise_overview_corr2ref.png")
OUT_PLOT_RAW = os.path.join(os.path.dirname(__file__), "unsynced_clocknoise_dds_corr2ref.png")

CORR1_PREFIX = os.path.join(DATA_DIR, "clocknoise_corr1_20260813_155159")
CORR2_PREFIX = os.path.join(DATA_DIR, "clocknoise_corr2_20260813_155157")

CORR1_CHANNELS = {1: "eta12", 2: "zeta_L_12", 3: "zeta_U_12", 4: "dds", 5: "SYSREF1", 6: "SYSREF2"}
CORR2_CHANNELS = {1: "eta21", 2: "zeta_U_21", 3: "dds"}
SYNC_LABEL = "dds"

MAX_OFFSET_S = 5.0  # search window for inter-instrument start delay
WINDOW_S = 600.0  # 10 min from the start of the record -- offset is estimated
# from this window only (a single scalar, doesn't need the full ~2h record)

# Fractional-offset refinement (refine_offset_csd): band where dds is
# coherent between instruments *and* a constant delay has leverage
# (residual phase grows linearly with f) -- uses the same WINDOW_S-limited
# data via the cross-spectral phase slope, so it resolves the offset far
# finer than one sample without needing the full record either.
OFFSET_FMIN = 1.0  # Hz
OFFSET_FMAX = 8.0  # Hz
OFFSET_COHERENCE_MIN = 0.95
OFFSET_CSD_NPERSEG = 2 ** 16

# Clapboard step fiducial (find_phase_step): a jump smaller than this is
# just normal sample-to-sample noise/drift, not the shared dds kick (which
# in practice is ~0.45 cyc, i.e. ~50-100x any other diff in the window).
STEP_MIN_JUMP_CYC = 0.05

# If the CSD refinement's answer disagrees with the step-fiducial offset by
# more than this, it's treated as an unwrap cycle-slip (see module
# docstring) and discarded in favor of the step-fiducial offset. Comfortably
# above the step fiducial's own ~1-sample localization uncertainty (~0.03 s)
# and comfortably below the ~0.67 s cycle-slip error actually observed.
CSD_MAX_DISAGREEMENT_S = 0.1

# Fractional resampling (apply_offset): order for the Lagrange-interpolated
# fractional-sample shift, and how many samples to crop off each end
# afterward to discard its edge transient.
RESAMPLE_ORDER = 31
EDGE_CROP_SAMPLES = 16

ZOOM_WINDOW_S = 100.0  # width of the sync-check zoom plot


def parse_rate(txt_path):
    with open(txt_path) as f:
        for line in f:
            m = re.match(r"#\s*%\s*Acquisition rate:\s*([\d.eE+-]+)", line)
            if m:
                return float(m.group(1))
    raise ValueError(f"{txt_path}: no acquisition rate found")


def load_slot(file_prefix, channel_map, name):
    npy_path = f"{file_prefix}.npy"
    txt_path = f"{file_prefix}.txt"
    rate = parse_rate(txt_path)
    data = np.load(npy_path)

    channels = {}
    for i, label in channel_map.items():
        channels[label] = {
            "phase": data[f"Input {i} Phase (cyc)"].astype(float),
            "freq": data[f"Input {i} Frequency (Hz)"].astype(float),
        }

    return {
        "path": npy_path,
        "name": name,
        "rate": rate,
        "t": data["Time (s)"].astype(float),
        "labels": list(channel_map.values()),
        "channels": channels,
        "sync_label": SYNC_LABEL,
        "sync_phase": channels[SYNC_LABEL]["phase"],
        "sync_freq": channels[SYNC_LABEL]["freq"],
    }


def detrend_linear(t, x):
    """Remove a best-fit linear ramp (e.g. from the set-frequency not
    exactly matching the real signal frequency) and return (residual, slope_hz)."""
    slope, intercept = np.polyfit(t, x, 1)
    return x - (slope * t + intercept), slope


def find_phase_step(t, phase, fs, window_s=WINDOW_S, min_jump=STEP_MIN_JUMP_CYC):
    """Locate a single-sample "clapboard" discontinuity in `phase` within
    the first window_s seconds -- the single largest sample-to-sample jump
    in the window, taken as a shared fiducial only if it clears min_jump
    (well above normal drift/noise). Returns (t_step, jump_cyc), the local
    time (s, midpoint between the two bracketing samples -- as precise as a
    single-sample-wide transition allows) and signed jump size, or
    (None, None) if nothing clears min_jump.

    Only searched for on the phase channel, not frequency: frequency should
    show the same kick even more sharply (it's the derivative), but on this
    data corr1's frequency channel has a second, unrelated glitch elsewhere
    in the window that's actually larger than the real shared event there,
    so a blind max-deviation search on frequency finds the wrong thing.
    Phase doesn't have that problem -- the real event's *cycle* jump is
    unambiguously the largest anomaly by a wide margin.
    """
    window_n = int(window_s * fs)
    tt, pp = t[:window_n], phase[:window_n]
    d = np.diff(pp)
    i = int(np.argmax(np.abs(d)))
    jump = d[i]
    if abs(jump) < min_jump:
        return None, None
    return 0.5 * (tt[i] + tt[i + 1]), jump


def estimate_offset(ref, other):
    """Return a coarse time offset (s) that `other`'s clock lags `ref`'s
    clock by, estimated from the first WINDOW_S seconds of the dds channel.

    The dds phase is dominated by slow, broadband drift -- both a plain
    time-domain cross-correlation and sync_phasemeters.py's PSD-minimization
    search (which assumes the *low*-frequency band [5e-4, 0.1] Hz is where a
    delay has leverage) turn out too flat here to localize a delay: shifting
    by anywhere within several seconds barely changes either metric. What
    actually discriminates a shift is the same [OFFSET_FMIN, OFFSET_FMAX] Hz
    band the CSD refinement below uses, where the two dds channels are
    genuinely coherent (verified separately) -- so this band-pass filters
    both channels to that band first, then cross-correlates. This coarse
    estimate only needs to land within refine_offset_csd's capture range
    (empirically a few seconds around the true offset here) for that
    refinement to find the precise, sub-sample answer -- it doesn't need to
    be exact itself.
    """
    fs = ref["rate"]

    other_sync_on_ref_t = interp1d(other["t"], other["sync_phase"], kind="cubic",
                                    bounds_error=False, fill_value=np.nan)(ref["t"])
    mask = ~np.isnan(other_sync_on_ref_t)
    t = ref["t"][mask]
    ref_sig = ref["sync_phase"][mask]
    other_sig = other_sync_on_ref_t[mask]

    window_n = int(WINDOW_S * fs)
    if window_n < len(t):
        t, ref_sig, other_sig = t[:window_n], ref_sig[:window_n], other_sig[:window_n]

    ref_d, _ = detrend_linear(t, ref_sig)
    other_d, _ = detrend_linear(t, other_sig)

    sos = butter(4, [OFFSET_FMIN, OFFSET_FMAX], btype="band", fs=fs, output="sos")
    ref_bp = sosfiltfilt(sos, ref_d)
    other_bp = sosfiltfilt(sos, other_d)

    corr = correlate(ref_bp, other_bp, mode="full")
    lags_s = correlation_lags(len(ref_bp), len(other_bp), mode="full") / fs
    search = np.abs(lags_s) <= MAX_OFFSET_S
    corr_search = np.abs(corr[search])
    best = np.argmax(corr_search)
    coarse = lags_s[search][best]
    print(f"    band-limited [{OFFSET_FMIN}, {OFFSET_FMAX}] Hz xcorr coarse offset: "
          f"{coarse:+.4f} s (peak |corr|={corr_search[best]:.3e}, "
          f"median over search range={np.median(corr_search):.3e})")
    return coarse


def coherent_phase_slope(ref, other, coarse_offset):
    """Cross-spectral phase slope between the two dds channels, in a band
    where they're coherent and a constant delay has leverage, after
    shifting `other` by `coarse_offset`. Restricted to the first WINDOW_S
    seconds, same as estimate_offset.

    Returns (slope [rad/Hz], n_coherent_bins).
    """
    fs = ref["rate"]
    window_n = int(WINDOW_S * fs)

    other_shifted = interp1d(other["t"] + coarse_offset, other["sync_phase"], kind="cubic",
                              bounds_error=False, fill_value=np.nan)(ref["t"])
    mask = ~np.isnan(other_shifted)
    ref_sig = ref["sync_phase"][mask]
    other_sig = other_shifted[mask]
    if window_n < len(ref_sig):
        ref_sig, other_sig = ref_sig[:window_n], other_sig[:window_n]

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
    cross-spectral phase slope between the two dds channels (see
    coherent_phase_slope). Falls back to the coarse offset, unchanged, if
    there aren't enough coherent bins in [OFFSET_FMIN, OFFSET_FMAX] to fit
    a slope.

    Sign convention (same as sync_phasemeters.py): delta = +slope / (2*pi).
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
    sample Lagrange-interpolated shift (order RESAMPLE_ORDER)."""
    n = int(round(offset / dt))
    frac = offset / dt - n
    shifted = lagrange_timeshift(channel, -frac, order=RESAMPLE_ORDER)
    return np.roll(shifted, n)


def main():
    # only difference from sync_clocknoise_corr.py: corr2 is loaded as `ref`
    # (untouched output grid) and corr1 as `other` (the one that gets
    # shifted) -- everything downstream is generic over ref/other and needs
    # no other changes
    ref = load_slot(CORR2_PREFIX, CORR2_CHANNELS, "corr2")
    other = load_slot(CORR1_PREFIX, CORR1_CHANNELS, "corr1")
    slots = [ref, other]

    if ref["rate"] != other["rate"]:
        raise ValueError(f"sample rates differ: corr2={ref['rate']}, corr1={other['rate']}")

    # raw dds channels on each slot's own local clock, before any offset
    # correction -- just the first WINDOW_S seconds, the window the offset
    # is actually estimated from
    fig_raw, ax_raw = plt.subplots(figsize=(11, 5))
    for s in slots:
        n = int(WINDOW_S * s["rate"])
        detrended, _ = detrend_linear(s["t"][:n], s["sync_phase"][:n])
        ax_raw.plot(s["t"][:n], detrended, label=f"{s['name']} ({s['sync_label']})")
    ax_raw.set_xlabel("Own local time (s), unsynced")
    ax_raw.set_ylabel("dds channel phase (cyc), linear ramp removed")
    ax_raw.set_title(f"dds channels, first {WINDOW_S:.0f} s, raw local time -- before offset correction")
    ax_raw.legend(fontsize=8)
    fig_raw.tight_layout()
    fig_raw.savefig(OUT_PLOT_RAW, dpi=150)
    print(f"Saved {OUT_PLOT_RAW}")

    print(f"Estimating corr2<->corr1 offset from the first {WINDOW_S:.0f} s of the dds channels:")

    print("  locating the shared dds phase-step (clapboard) fiducial:")
    t1_step, jump1 = find_phase_step(ref["t"], ref["sync_phase"], ref["rate"])
    t2_step, jump2 = find_phase_step(other["t"], other["sync_phase"], other["rate"])
    if t1_step is None or t2_step is None:
        raise RuntimeError(
            "no shared dds phase-step fiducial found in one or both files "
            f"(need a jump >= {STEP_MIN_JUMP_CYC} cyc) -- can't cross-check the CSD refinement"
        )
    step_offset = t1_step - t2_step
    print(f"    {os.path.basename(ref['path'])}: step at t={t1_step:.4f} s (jump {jump1:+.4f} cyc)")
    print(f"    {os.path.basename(other['path'])}: step at t={t2_step:.4f} s (jump {jump2:+.4f} cyc)")
    print(f"    step-fiducial offset = {step_offset:+.4f} s")

    coarse_offset = estimate_offset(ref, other)
    print(f"{os.path.basename(other['path'])}: coarse offset = {coarse_offset:+.4f} s "
          f"relative to {os.path.basename(ref['path'])}")

    print(f"Refining offset via cross-spectral phase slope in [{OFFSET_FMIN}, {OFFSET_FMAX}] Hz:")
    csd_offset = refine_offset_csd(ref, other, coarse_offset)
    print(f"{os.path.basename(other['path'])}: {coarse_offset:+.6f} s -> {csd_offset:+.6f} s")

    # cross-check the CSD refinement against the independent step fiducial
    # (see module docstring) -- reject it if they disagree by more than a
    # cycle-slip-scale amount
    disagreement = csd_offset - step_offset
    if abs(disagreement) > CSD_MAX_DISAGREEMENT_S:
        print(f"  CSD refinement ({csd_offset:+.4f} s) disagrees with the step "
              f"fiducial ({step_offset:+.4f} s) by {disagreement:+.4f} s "
              f"(> {CSD_MAX_DISAGREEMENT_S} s) -- treating this as an unwrap "
              f"cycle-slip and using the step-fiducial offset instead")
        offset = step_offset
    else:
        print(f"  CSD refinement agrees with the step fiducial to {disagreement:+.4f} s -- keeping it")
        offset = csd_offset

    offsets = [0.0, offset]
    for s, off in zip(slots, offsets):
        s["t_ref_frame"] = s["t"] + off

    dt = 1.0 / ref["rate"]

    # use corr2's own native sample times as the output grid, cropped to
    # where both slots have data after the offset is applied -- corr2
    # (offset 0 by definition) is never resampled/touched, only corr1 gets
    # shifted (via apply_offset) onto corr2's grid
    t_start = max(s["t_ref_frame"][0] for s in slots)
    t_end = min(s["t_ref_frame"][-1] for s in slots)
    ref_mask = (ref["t"] >= t_start) & (ref["t"] <= t_end)
    j_start = int(np.argmax(ref_mask))
    j_end = j_start + int(ref_mask.sum())
    common_t = ref["t"][j_start:j_end]

    out = {"time_s": common_t}
    data_keys = []
    for s, off in zip(slots, offsets):
        prefix = s["name"]
        is_ref = s is ref
        for label in s["labels"]:
            phase_raw = s["channels"][label]["phase"]
            freq_raw = s["channels"][label]["freq"]
            if is_ref:
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
            key = f"{prefix}_{label}"
            out[key] = phase_vals
            out[f"{key}_freq"] = freq_vals
            data_keys.append(key)

    # discard the Lagrange fractional-shift's edge transient, consistently
    # on every channel including corr2's (which wasn't itself shifted, but
    # must stay the same length/alignment as the shifted channels)
    common_t = common_t[EDGE_CROP_SAMPLES:-EDGE_CROP_SAMPLES]
    out = {k: v[EDGE_CROP_SAMPLES:-EDGE_CROP_SAMPLES] for k, v in out.items()}

    # the set frequency never exactly matches the real signal frequency, so
    # each phase channel has a linear ramp on top of the interesting signal
    # -- remove it with a best-fit line
    print()
    for key in data_keys:
        out[key], slope = detrend_linear(common_t, out[key])
        print(f"{key}: removed linear ramp of {slope:.6f} cyc/s ({slope:.6f} Hz)")

    sync_keys = [f"{s['name']}_{SYNC_LABEL}" for s in slots]

    # verify the thing that actually matters: that the corr2<->corr1 offset
    # was applied correctly. NOT via the CSD phase-slope residual -- that
    # method has the same unwrap cycle-slip failure mode noted in the module
    # docstring, so it can't be trusted as a verification of itself either.
    # Instead, re-locate the dds step fiducial in the now-synced data (both
    # slots on the common time axis) and confirm it lands at the same common
    # time on both -- should agree to about a sample if the offset is right.
    print()
    print("Verifying resampling via the dds step fiducial, now on the common time axis:")
    fs = ref["rate"]
    t1_step_synced, _ = find_phase_step(common_t, out[sync_keys[0]], fs)
    t2_step_synced, _ = find_phase_step(common_t, out[sync_keys[1]], fs)
    if t1_step_synced is None or t2_step_synced is None:
        print("  could not re-locate the step fiducial in the synced data -- skipping check")
    else:
        residual = t1_step_synced - t2_step_synced
        print(f"  {sync_keys[0]} step at t={t1_step_synced:.4f} s, {sync_keys[1]} step at "
              f"t={t2_step_synced:.4f} s (residual {residual:+.4f} s, should be ~0)")

    np.savez(OUT_NPZ, **out)
    print(f"\nSaved {OUT_NPZ}")
    print("Keys:", list(out.keys()))

    # --- sync-check plot ---
    fig, (ax_a, ax_b) = plt.subplots(2, 1, figsize=(11, 8))

    for key in data_keys:
        ax_a.plot(common_t, out[key], label=key)
    ax_a.set_ylabel("Phase (cyc), detrended")
    ax_a.set_title("Data channels -- both slots, synced + linear ramp removed (as saved)")
    ax_a.legend(fontsize=8)

    zoom_mask = common_t <= common_t[0] + ZOOM_WINDOW_S
    for key in sync_keys:
        ax_b.plot(common_t[zoom_mask], detrend(out[key][zoom_mask]), label=key)
    ax_b.set_ylabel("dds phase (cyc), window-detrended")
    ax_b.set_xlabel("Common time (s)")
    ax_b.set_title(f"dds channel, {ZOOM_WINDOW_S:.0f} s zoom near start of record "
                    f"-- not expected to overlap (real differential drift; see the step-fiducial "
                    f"check above for the actual constant-offset verification)")
    ax_b.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT_PLOT, dpi=150)
    print(f"Saved {OUT_PLOT}")


if __name__ == "__main__":
    main()
