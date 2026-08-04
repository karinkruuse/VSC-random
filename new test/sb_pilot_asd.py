"""
ASD of the delayed sideband signal (Input A), its pilot tone (Input B), and
the delayed carrier (Input A) -- both as frequency noise and as timing
jitter. Timing jitter = phase / freq, using each signal's OWN frequency.

Input:  data/synced_phasemeter_data.npz  (produced by sync_phasemeters.py)
Output: sb_pilot_asd.png
"""
import os

import matplotlib.pyplot as plt
import numpy as np

from delay_estimates import IN_NPZ, compute_asd

OUT_PLOT = os.path.join(os.path.dirname(__file__), "sb_pilot_asd.png")

CHANNELS = [
    ("delayed sideband (Input A)", "delayer_sb", "delayer_sb_freq"),
    ("pilot tone (Input B)", "delayer_sb_b", "delayer_sb_b_freq"),
    ("delayed carrier (Input A)", "delayer_carrier", "delayer_carrier_freq"),
]


def main():
    data = np.load(IN_NPZ)
    t = data["time_s"]
    dt = np.median(np.diff(t))
    fs = 1.0 / dt

    fig, (ax_freq, ax_jit) = plt.subplots(1, 2, figsize=(12, 4.5))

    for label, phase_key, freq_key in CHANNELS:
        phase, freq = data[phase_key], data[freq_key]
        jitter = phase / freq  # s, using this signal's OWN frequency
        print(f"jitter RMS: {label} = {np.std(jitter)*1e9:.2f} ns")

        f_freq, asd_freq, _ = compute_asd(freq, fs)
        f_jit, asd_jit, _ = compute_asd(jitter, fs)

        ax_freq.loglog(f_freq, asd_freq, label=label)
        ax_jit.loglog(f_jit, asd_jit, label=label)

    ax_freq.set_xlabel("Frequency (Hz)")
    ax_freq.set_ylabel("Frequency ASD (Hz / sqrt(Hz))")
    ax_freq.set_title("Frequency noise")
    ax_freq.grid(True, which="both", ls="--", alpha=0.5)
    ax_freq.legend(fontsize=8)

    ax_jit.set_xlabel("Frequency (Hz)")
    ax_jit.set_ylabel("Timing jitter ASD (s / sqrt(Hz))")
    ax_jit.set_title("Timing jitter (phase / own frequency)")
    ax_jit.grid(True, which="both", ls="--", alpha=0.5)
    ax_jit.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT_PLOT, dpi=150)
    print(f"Saved {OUT_PLOT}")


if __name__ == "__main__":
    main()
