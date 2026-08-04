"""
Estimate the physical delay-line delay from the synced phasemeter data, done
separately for the carrier and the sideband:

    carrier delay:   delayer_carrier  vs  carrier
    sideband delay:  delayer_sb       vs  sb

Same spectral approach as DL Baseline/analysis_w_delay_minimization.py: for a
trial delay tau, time-shift the delayed channel by tau, form the residual
(direct - delayed_shifted), and compute its PSD. The correct tau is the one
that minimizes residual power in [FMIN, FMAX] -- i.e. the delay that makes
the two channels cancel best, since they're the same underlying signal split
across two paths.

Each slot's own Input B is its DDS/pilot tone: since it's a known, stable
reference, any apparent phase wander recorded on B is really timing jitter of
that instrument's own sampling clock, not signal. We extract that jitter
(jitter = phase_b / freq_b, in seconds) and remove its effect from the same
slot's Input A phase (correction = freq_a * jitter, in cycles) before doing
the delay estimate, and compare against the uncorrected result.

Input:  data/synced_phasemeter_data.npz  (produced by sync_phasemeters.py)
Output: data/delay_estimates.npz, delay_estimates_overview.png
"""
import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import minimize_scalar
from scipy.signal import detrend, welch

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
IN_NPZ = os.path.join(DATA_DIR, "synced_phasemeter_data.npz")
OUT_NPZ = os.path.join(DATA_DIR, "delay_estimates.npz")
OUT_PLOT = os.path.join(os.path.dirname(__file__), "delay_estimates_overview.png")

PAIRS = [
    ("carrier", "delayer_carrier", "carrier"),
    ("sideband", "delayer_sb", "sb"),
]

FMIN = 5e-4  # Hz -- cost = residual PSD integrated over [FMIN, FMAX]
FMAX = 0.1  # Hz
PROGRAMMED_DELAY_S = 4.3  # known approximate delay -- search is centered here
SEARCH_RANGE_S = 0.1  # coarse scan window, +/- this many seconds around PROGRAMMED_DELAY_S
COARSE_STEP_S = 0.005


def clock_noise_correct(phase_a, freq_a, phase_b, freq_b):
    """Remove this instrument's own sampling-clock jitter (extracted from its
    pilot-tone channel B) from its Input A phase."""
    jitter = phase_b / freq_b  # s
    correction = freq_a * jitter  # cyc
    return phase_a - correction, jitter


def residual_for_delay(t, direct_sig, delayed_sig, delay, dt):
    """direct(t) - delayed(t + delay), edge-cropped, detrended."""
    delayed_interp = interp1d(t, delayed_sig, kind="cubic", bounds_error=False, fill_value=np.nan)
    delayed_shifted = delayed_interp(t + delay)

    n_crop = int(np.ceil(abs(delay) / dt)) + 5
    sl = slice(n_crop, -n_crop)
    return detrend(direct_sig[sl] - delayed_shifted[sl])


def compute_asd(x, fs, fmin=FMIN):
    nperseg = min(int(fs / fmin), len(x))
    f, psd = welch(x, fs=fs, nperseg=nperseg, detrend="constant")
    return f, np.sqrt(psd), psd


def cost(delay, t, direct_sig, delayed_sig, dt, fs):
    residual = residual_for_delay(t, direct_sig, delayed_sig, delay, dt)
    f, _, psd = compute_asd(residual, fs)
    mask = (f >= FMIN) & (f <= FMAX)
    return np.trapezoid(psd[mask], f[mask])


def estimate_delay_seconds(t, direct_sig, delayed_sig, center=PROGRAMMED_DELAY_S):
    dt = np.median(np.diff(t))
    fs = 1.0 / dt

    # coarse scan (tightly bracketed around the known approximate delay) to
    # bracket the global minimum, then refine
    taus = np.arange(center - SEARCH_RANGE_S, center + SEARCH_RANGE_S + COARSE_STEP_S, COARSE_STEP_S)
    costs = np.array([cost(tau, t, direct_sig, delayed_sig, dt, fs) for tau in taus])
    tau0 = taus[np.argmin(costs)]
    print(f"  coarse scan minimum: tau0={tau0:+.4f} s (cost={costs.min():.4e}, "
          f"vs cost at tau={center}: {costs[np.argmin(np.abs(taus - center))]:.4e})")

    result = minimize_scalar(
        cost, bounds=(tau0 - COARSE_STEP_S, tau0 + COARSE_STEP_S), method="bounded",
        args=(t, direct_sig, delayed_sig, dt, fs), options={"xatol": 1e-6},
    )
    delay = result.x
    print(f"  refined delay = {delay:+.6f} s (cost={result.fun:.4e})")
    return delay, taus, costs


def main():
    data = np.load(IN_NPZ)
    t = data["time_s"]
    dt = np.median(np.diff(t))
    fs = 1.0 / dt

    delays = {}
    fig, axes = plt.subplots(len(PAIRS), 2, figsize=(12, 4.5 * len(PAIRS)))

    for row, (name, delayed_key, direct_key) in enumerate(PAIRS):
        print(f"{name}: {delayed_key} vs {direct_key}")

        direct_sig_raw = data[direct_key]
        delayed_sig_raw = data[delayed_key]

        direct_sig, direct_jitter = clock_noise_correct(
            direct_sig_raw, data[f"{direct_key}_freq"], data[f"{direct_key}_b"], data[f"{direct_key}_b_freq"])
        delayed_sig, delayed_jitter = clock_noise_correct(
            delayed_sig_raw, data[f"{delayed_key}_freq"], data[f"{delayed_key}_b"], data[f"{delayed_key}_b_freq"])
        print(f"  clock jitter RMS: {direct_key}={np.std(direct_jitter)*1e9:.2f} ns, "
              f"{delayed_key}={np.std(delayed_jitter)*1e9:.2f} ns")

        print("  raw (uncorrected):")
        delay_raw, _, _ = estimate_delay_seconds(t, direct_sig_raw, delayed_sig_raw)
        print("  clock-noise corrected:")
        delay, taus, costs = estimate_delay_seconds(t, direct_sig, delayed_sig)

        delays[f"{name}_delay_s"] = delay
        delays[f"{name}_delay_s_raw"] = delay_raw
        print(f"  -> {name} delay estimate: {delay:+.6f} s (raw, uncorrected: {delay_raw:+.6f} s)\n")

        ax_scan, ax_asd = axes[row]
        ax_scan.plot(taus, costs, "-o", ms=3)
        ax_scan.axvline(delay, color="r", label=f"delay = {delay:+.4f} s")
        ax_scan.set_yscale("log")
        ax_scan.set_xlabel("Trial delay (s)")
        ax_scan.set_ylabel(f"Residual PSD, integrated [{FMIN:.0e}, {FMAX:.0e}] Hz")
        ax_scan.set_title(f"{name}: cost landscape")
        ax_scan.legend(fontsize=8)

        f_before, asd_before, _ = compute_asd(residual_for_delay(t, direct_sig, delayed_sig, 0.0, dt), fs)
        f_after, asd_after, _ = compute_asd(residual_for_delay(t, direct_sig, delayed_sig, delay, dt), fs)
        ax_asd.loglog(f_before, asd_before, alpha=0.7, label="residual, no delay correction")
        ax_asd.loglog(f_after, asd_after, lw=1.5, label=f"residual, delay = {delay:+.4f} s")

        # the raw input/output signals themselves, unprocessed -- no delay shift,
        # no differencing, no clock correction -- for reference
        f_direct_raw, asd_direct_raw, _ = compute_asd(direct_sig_raw, fs)
        f_delayed_raw, asd_delayed_raw, _ = compute_asd(delayed_sig_raw, fs)
        ax_asd.loglog(f_direct_raw, asd_direct_raw, ls=":", alpha=0.6, label=f"{direct_key} (raw, unprocessed)")
        ax_asd.loglog(f_delayed_raw, asd_delayed_raw, ls=":", alpha=0.6, label=f"{delayed_key} (raw, unprocessed)")

        ax_asd.set_xlabel("Frequency (Hz)")
        ax_asd.set_ylabel("ASD (cyc / sqrt(Hz))")
        ax_asd.set_title(f"{name}: residual ASD before/after delay correction")
        ax_asd.grid(True, which="both", ls="--", alpha=0.5)
        ax_asd.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT_PLOT, dpi=150)
    print(f"Saved {OUT_PLOT}")

    np.savez(OUT_NPZ, **delays)
    print(f"Saved {OUT_NPZ}")
    print("\nSummary:")
    for k, v in delays.items():
        print(f"  {k}: {v:+.6f} s")


if __name__ == "__main__":
    main()
