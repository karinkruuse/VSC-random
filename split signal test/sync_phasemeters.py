"""
Sync the 4 Moku phasemeter files onto a common timebase, using Input A (the
carrier signal common to all 4 instruments) to find the time offset of each
file, then interpolating everything onto one shared time grid.

Each file's header carries one comment line "LABEL_A, LABEL_B" (e.g.
"carrier, USB" or "carrier, LSB") naming the physical signal on Input A and
Input B respectively -- both labels come from that line, not from the
"Input A (on), ..."/"Input B (on), ..." set-up lines above it.

Output: data/synced_phasemeter_data.npz containing every Input A and Input B
stream from all 4 slots (keyed by its comment-line label, numbered on
collision -- e.g. 4x "carrier"/"carrier_1"/"carrier_2"/"carrier_3", 2x
"USB"/"USB_1", 2x "LSB"/"LSB_1" -- so nothing is discarded even though only
the A streams are used below to find the sync offsets):
    time_s              -- common time axis (s)
    <label>             -- phase (cyc), detrended
    <label>_freq        -- frequency (Hz), raw
"""
import glob
import json
import os
import re

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import minimize_scalar
from scipy.signal import detrend, welch

DATA_DIR = os.path.join(os.path.dirname(__file__), "data/mod_1input")
OUT_NPZ = os.path.join(DATA_DIR, "synced_phasemeter_data.npz")
OUT_PLOT = os.path.join(os.path.dirname(__file__), "synced_overview.png")
OFFSET_CACHE = os.path.join(DATA_DIR, "sync_offsets_cache.json")

MAX_OFFSET_S = 10.0  # search window for inter-instrument start delay
FMIN = 5e-4  # Hz -- cost = residual PSD integrated over [FMIN, FMAX]
FMAX = 0.1  # Hz
COARSE_STEP_S = 0.1
SYNC_WINDOW_S = 100.0  # only use this much data to find the offset -- much faster,
# and the offset is a single scalar so it doesn't need the full record to pin down


# the header's label line is a bare "LABEL_A, LABEL_B" comment -- distinguish
# it from the other "# % ..." lines (Moku:Pro Phasemeter, Input A/B (on)...,
# Acquisition rate, Advanced settings, Output A/B..., Internal clock, Acquired
# ..., Time (s), ...) by excluding their known prefixes. (A regex lookahead
# for this was tried first, but `\s*` backtracking off the space it had
# matched let it slip past the excluded prefixes -- plain string checks here
# instead.)
_LABEL_LINE_EXCLUDE = ("Moku:Pro", "Input", "Output", "Acquisition",
                       "Advanced", "Internal", "Acquired", "Time")
_TWO_FIELD_RE = re.compile(r"([^,]+),\s*([^,]+)$")


def parse_header(txt_path):
    label_a, label_b, rate = None, None, None
    with open(txt_path) as f:
        for line in f:
            content = line.strip().lstrip("#").strip()
            if content.startswith("%"):
                content = content[1:].strip()
            if not content.startswith(_LABEL_LINE_EXCLUDE):
                m = _TWO_FIELD_RE.match(content)
                if m:
                    label_a, label_b = m.group(1).strip(), m.group(2).strip()
            m = re.match(r"Acquisition rate:\s*([\d.eE+-]+)", content)
            if m:
                rate = float(m.group(1))
    if label_a is None or label_b is None:
        raise ValueError(f"{txt_path}: no 'label_a, label_b' comment line found")
    return label_a, label_b, rate


def sanitize_key(label, used):
    base = re.sub(r"\s+", "_", label.strip().lower())
    base = re.sub(r"[^a-z0-9_]", "", base)
    n = used.get(base, 0)
    key = base if n == 0 else f"{base}_{n}"
    used[base] = n + 1
    return key


def load_slot(npy_path):
    txt_path = npy_path.replace(".npy", ".txt")
    label_a, label_b, rate = parse_header(txt_path)
    data = np.load(npy_path)
    return {
        "path": npy_path,
        "label_a": label_a,
        "label_b": label_b,
        "rate": rate,
        "t": data["Time (s)"],
        "a_phase": data["Input A Phase (cyc)"],
        "b_phase": data["Input B Phase (cyc)"],
        "a_freq": data["Input A Frequency (Hz)"],
        "b_freq": data["Input B Frequency (Hz)"],
    }


def detrend_linear(t, x):
    """Remove a best-fit linear ramp (e.g. from the set-frequency not
    exactly matching the real signal frequency) and return (residual, slope_hz)."""
    slope, intercept = np.polyfit(t, x, 1)
    return x - (slope * t + intercept), slope


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
    estimate: for a trial offset, shift other's A channel and form the
    residual against ref's A channel. A carries no physical delay -- it's
    the same carrier signal in every slot -- so the true offset is the one
    where the residual PSD collapses to near-nothing (a much sharper, more
    reliable signal than a plain cross-correlation, which the large
    non-linear shared drift between slots can easily swamp).
    """
    dt = 1.0 / ref["rate"]
    fs = ref["rate"]

    other_a_on_ref_t = interp1d(other["t"], other["a_phase"], kind="cubic",
                                 bounds_error=False, fill_value=np.nan)(ref["t"])
    mask = ~np.isnan(other_a_on_ref_t)
    t = ref["t"][mask]
    ref_sig = ref["a_phase"][mask]
    other_sig = other_a_on_ref_t[mask]

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
    npy_files = sorted(glob.glob(os.path.join(DATA_DIR, "MokuPhasemeterSlot*Data_*.npy")))
    if not npy_files:
        raise SystemExit(f"No Moku phasemeter .npy files found in {DATA_DIR}")

    slots = [load_slot(p) for p in npy_files]
    ref = slots[0]

    cached_offsets = load_cached_offsets(npy_files)
    if cached_offsets is not None:
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

    # each slot's samples, expressed in the shared reference-frame time axis
    for s, off in zip(slots, offsets):
        s["t_ref_frame"] = s["t"] + off

    t_start = max(s["t_ref_frame"][0] for s in slots)
    t_end = min(s["t_ref_frame"][-1] for s in slots)
    dt = 1.0 / ref["rate"]
    common_t = np.arange(t_start, t_end, dt)

    # every Input A and Input B stream from every slot is kept, keyed by its
    # comment-line label (numbered on collision -- e.g. carrier appears 4x,
    # USB and LSB 2x each). Frequency channels are saved too (raw, not
    # detrended) so a downstream script can do clock-noise correction:
    # jitter = phase / freq [s], correction = freq_other * jitter [cyc].
    used_keys = {}
    out = {"time_s": common_t}
    stream_keys = []
    for s in slots:
        a_phase_interp = interp1d(s["t_ref_frame"], s["a_phase"], kind="cubic")
        b_phase_interp = interp1d(s["t_ref_frame"], s["b_phase"], kind="cubic")
        a_freq_interp = interp1d(s["t_ref_frame"], s["a_freq"], kind="cubic")
        b_freq_interp = interp1d(s["t_ref_frame"], s["b_freq"], kind="cubic")

        key_a = sanitize_key(s["label_a"], used_keys)
        key_b = sanitize_key(s["label_b"], used_keys)

        out[key_a] = a_phase_interp(common_t)
        out[f"{key_a}_freq"] = a_freq_interp(common_t)
        out[key_b] = b_phase_interp(common_t)
        out[f"{key_b}_freq"] = b_freq_interp(common_t)

        s["key_a"], s["key_b"] = key_a, key_b
        stream_keys += [key_a, key_b]

    # the set frequency never exactly matches the real signal frequency, so
    # each phase channel has a linear ramp on top of the interesting signal
    # -- remove it with a best-fit line
    print()
    for key in stream_keys:
        out[key], slope = detrend_linear(common_t, out[key])
        print(f"{key}: removed linear ramp of {slope:.6f} cyc/s ({slope:.6f} Hz)")

    np.savez(OUT_NPZ, **out)
    print(f"\nSaved {OUT_NPZ}")
    print("Keys:", list(out.keys()))

    # --- sync-check plot ---
    fig, (ax_a, ax_b, ax_zoom) = plt.subplots(3, 1, figsize=(11, 10))

    for s in slots:
        ax_a.plot(common_t, out[s["key_a"]],
                   label=f"{os.path.basename(s['path'])} ({s['key_a']})")
        ax_a.plot(common_t, out[s["key_b"]], ls="--",
                   label=f"{os.path.basename(s['path'])} ({s['key_b']})")
    ax_a.set_ylabel("Phase (cyc), detrended")
    ax_a.set_title("All synced data streams -- 4x carrier, 2x USB, 2x LSB (as saved)")
    ax_a.legend(fontsize=8)

    # channel A has an arbitrary per-instrument DC phase offset, so remove
    # each slot's mean before overlaying -- if sync worked these should
    # overlap tightly over the *entire* duration, not just near t=0
    for s in slots:
        a_on_common = np.interp(common_t, s["t_ref_frame"], s["a_phase"])
        ax_b.plot(common_t, a_on_common - a_on_common.mean(),
                   label=f"{os.path.basename(s['path'])} ({s['label_a']})")
    ax_b.set_ylabel("Input A phase (cyc), mean-removed")
    ax_b.set_title("Channel A (sync signal), full duration, DC offset removed per slot")
    ax_b.legend(fontsize=8)

    mid = common_t[0] + 0.5 * (common_t[-1] - common_t[0])
    zoom_mask = (common_t >= mid) & (common_t <= mid + 20)
    for s in slots:
        a_on_common = np.interp(common_t[zoom_mask], s["t_ref_frame"], s["a_phase"])
        ax_zoom.plot(common_t[zoom_mask], a_on_common - a_on_common.mean(),
                     label=f"{os.path.basename(s['path'])} ({s['label_a']})")
    ax_zoom.set_ylabel("Input A phase (cyc), mean-removed")
    ax_zoom.set_xlabel("Common time (s)")
    ax_zoom.set_title("Channel A, 20 s zoom mid-record -- fine structure should overlap if sync worked")
    ax_zoom.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT_PLOT, dpi=150)
    print(f"Saved {OUT_PLOT}")


if __name__ == "__main__":
    main()
