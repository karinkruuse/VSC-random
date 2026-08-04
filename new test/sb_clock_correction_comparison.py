"""
Sideband only: apply the already-known delay (FIXED_DELAY_S) directly and
compare the residual (delayer_sb vs sb) with and without clock-noise
correction. Unlike delay_estimates.py, this does NOT re-estimate the delay --
it's purely a before/after comparison at a fixed, known tau, same style as
DL SB/SB_BL_meas.py (delay_s hardcoded from a prior estimate).

Input:  data/synced_phasemeter_data.npz  (produced by sync_phasemeters.py)
Output: sb_clock_correction_comparison.png
"""
import os

import matplotlib.pyplot as plt
import numpy as np

from delay_estimates import IN_NPZ, clock_noise_correct, compute_asd, cost, residual_for_delay

OUT_PLOT = os.path.join(os.path.dirname(__file__), "sb_clock_correction_comparison.png")

FIXED_DELAY_S = 4.2993


def main():
    data = np.load(IN_NPZ)
    t = data["time_s"]
    dt = np.median(np.diff(t))
    fs = 1.0 / dt

    direct_raw = data["sb"]
    delayed_raw = data["delayer_sb"]

    direct_corr, direct_jitter = clock_noise_correct(
        direct_raw, data["sb_freq"], data["sb_b"], data["sb_b_freq"])
    delayed_corr, delayed_jitter = clock_noise_correct(
        delayed_raw, data["delayer_sb_freq"], data["delayer_sb_b"], data["delayer_sb_b_freq"])
    print(f"clock jitter RMS: sb={np.std(direct_jitter)*1e9:.2f} ns, "
          f"delayer_sb={np.std(delayed_jitter)*1e9:.2f} ns")

    cost_raw = cost(FIXED_DELAY_S, t, direct_raw, delayed_raw, dt, fs)
    cost_corr = cost(FIXED_DELAY_S, t, direct_corr, delayed_corr, dt, fs)
    print(f"\nAt fixed delay = {FIXED_DELAY_S} s:")
    print(f"  residual PSD (integrated), no clock correction:   {cost_raw:.4e}")
    print(f"  residual PSD (integrated), clock-noise corrected: {cost_corr:.4e}")
    print(f"  improvement: {cost_raw / cost_corr:.1f}x")

    residual_raw = residual_for_delay(t, direct_raw, delayed_raw, FIXED_DELAY_S, dt)
    residual_corr = residual_for_delay(t, direct_corr, delayed_corr, FIXED_DELAY_S, dt)
    print(f"  residual RMS, no clock correction:   {np.std(residual_raw):.4e} cyc")
    print(f"  residual RMS, clock-noise corrected: {np.std(residual_corr):.4e} cyc")

    f_raw, asd_raw, _ = compute_asd(residual_raw, fs)
    f_corr, asd_corr, _ = compute_asd(residual_corr, fs)

    # single-delay differencing transfer function |1 - e^(i*2*pi*f*delay)| = 2|sin(pi*f*delay)| --
    # divide it out of the uncorrected residual ASD to get the equivalent single-channel noise level.
    # near its nulls (f = n/delay) this blows up to spikes that are a division artifact, not real
    # signal, so mask those points out (purely cosmetic -- gaps instead of spikes)
    transfer_fn = 2 * np.abs(np.sin(np.pi * f_raw * FIXED_DELAY_S))
    with np.errstate(divide="ignore", invalid="ignore"):
        asd_raw_equalized = asd_raw / transfer_fn
    asd_raw_equalized[transfer_fn < 0.15 * transfer_fn.max()] = np.nan

    fig, (ax_asd, ax_time) = plt.subplots(1, 2, figsize=(12, 4.5))

    ax_asd.loglog(f_raw, asd_raw, alpha=0.8, label="no clock correction")
    ax_asd.loglog(f_raw, asd_raw_equalized, alpha=0.8, label="no clock correction, /transfer fn")
    ax_asd.loglog(f_corr, asd_corr, lw=1.5, label="clock-noise corrected")

    # the raw input/output signals themselves, unprocessed -- no delay shift,
    # no differencing, no clock correction -- for reference
    f_direct_raw, asd_direct_raw, _ = compute_asd(direct_raw, fs)
    f_delayed_raw, asd_delayed_raw, _ = compute_asd(delayed_raw, fs)
    ax_asd.loglog(f_direct_raw, asd_direct_raw, ls=":", alpha=0.6, label="sb (raw, unprocessed)")
    ax_asd.loglog(f_delayed_raw, asd_delayed_raw, ls=":", alpha=0.6, label="delayer_sb (raw, unprocessed)")

    ax_asd.set_xlabel("Frequency (Hz)")
    ax_asd.set_ylabel("ASD (cyc / sqrt(Hz))")
    ax_asd.set_title(f"sideband residual ASD at fixed delay = {FIXED_DELAY_S} s")
    ax_asd.grid(True, which="both", ls="--", alpha=0.5)
    ax_asd.legend(fontsize=8)

    t_res = t[: len(residual_raw)]
    zoom_n = min(2000, len(t_res))
    ax_time.plot(t_res[:zoom_n], residual_raw[:zoom_n], alpha=0.8, label="no clock correction")
    ax_time.plot(t_res[:zoom_n], residual_corr[:zoom_n], lw=1.2, label="clock-noise corrected")
    ax_time.set_xlabel("Common time (s)")
    ax_time.set_ylabel("residual phase (cyc)")
    ax_time.set_title("residual time series (zoom, start of record)")
    ax_time.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT_PLOT, dpi=150)
    print(f"\nSaved {OUT_PLOT}")


if __name__ == "__main__":
    main()
