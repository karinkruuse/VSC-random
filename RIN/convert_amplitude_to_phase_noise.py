"""Estimate additive-noise-limited phase ASD around a heterodyne beat note.

The input voltage ASD is sampled at the upper and lower sidebands around the
carrier. The sidebands are combined as independent additive voltage noise and
referred to the RMS carrier voltage. A first-order closed-loop PLL response is
then applied to show the tracked output phase noise.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


DEFAULT_DATA = Path(__file__).resolve().parent / "power issue" / "RIN_20261013_asd_comparison.npz"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--beat-frequency", type=float, default=5e6, help="Carrier frequency in Hz")
    parser.add_argument("--pll-bandwidth", type=float, default=1e4, help="PLL bandwidth in Hz")
    parser.add_argument("--signal-rms", type=float, default=0.5, help="Beat-note RMS voltage in V")
    parser.add_argument(
        "--max-offset",
        type=float,
        help="Maximum Fourier offset in Hz (default: 4x PLL bandwidth or available data)",
    )
    args = parser.parse_args()
    if min(args.beat_frequency, args.pll_bandwidth, args.signal_rms) <= 0:
        parser.error("beat frequency, PLL bandwidth, and signal RMS voltage must be positive")

    data_path = args.data.resolve()
    data = np.load(data_path)
    measurement_frequency = data["frequency_Hz"]
    spectra = {
        "PD dark + ADC/electronics": data["dark_voltage_asd_V_per_sqrt_Hz"],
        "Reference laser": data["reference_voltage_asd_V_per_sqrt_Hz"],
        "Laser 1": data["laser1_voltage_asd_V_per_sqrt_Hz"],
    }
    colors = {
        "PD dark + ADC/electronics": "0.2",
        "Reference laser": "#4C78A8",
        "Laser 1": "#F58518",
    }

    available_offset = min(
        args.beat_frequency - measurement_frequency[0],
        measurement_frequency[-1] - args.beat_frequency,
    )
    requested_offset = args.max_offset or 4 * args.pll_bandwidth
    max_offset = min(requested_offset, available_offset)
    bin_width = float(np.median(np.diff(measurement_frequency)))
    offset = np.arange(bin_width, max_offset + 0.5 * bin_width, bin_width)
    if len(offset) < 2:
        raise ValueError("Not enough spectrum exists on both sides of the requested carrier")

    # With one-sided voltage-noise spectra on both sides of the carrier,
    # S_phi = (S_V,lower + S_V,upper) / (2 * V_carrier,rms**2).
    phase_input = {}
    phase_output = {}
    pll_response = 1 / np.sqrt(1 + (offset / args.pll_bandwidth) ** 2)
    for label, voltage_asd in spectra.items():
        lower = np.interp(args.beat_frequency - offset, measurement_frequency, voltage_asd)
        upper = np.interp(args.beat_frequency + offset, measurement_frequency, voltage_asd)
        phase_input[label] = np.sqrt((lower**2 + upper**2) / 2) / args.signal_rms
        phase_output[label] = phase_input[label] * pll_response

    fig, axes = plt.subplots(2, 1, figsize=(11, 9), sharex=True, constrained_layout=True)
    for label in spectra:
        style = "--" if label.startswith("PD dark") else "-"
        axes[0].loglog(offset, phase_input[label], color=colors[label], linestyle=style,
                       linewidth=0.85, label=label)
        axes[1].loglog(offset, phase_output[label], color=colors[label], linestyle=style,
                       linewidth=0.85, label=label)

    axes[0].set(ylabel=r"Phase ASD (rad/$\sqrt{\mathrm{Hz}}$)",
                title="Equivalent phase-detector noise before PLL filtering")
    axes[1].set(xlabel="Fourier offset from 5 MHz beat note (Hz)",
                ylabel=r"Phase ASD (rad/$\sqrt{\mathrm{Hz}}$)",
                title="Phase noise at PLL output (first-order 10 kHz bandwidth)")
    axes[1].axvline(args.pll_bandwidth, color="0.45", linestyle=":", linewidth=1.0,
                    label="10 kHz PLL bandwidth")
    for ax in axes:
        ax.grid(True, which="both", alpha=0.25)
        ax.legend(loc="best")
    fig.suptitle(
        f"Amplitude-noise-equivalent phase noise: "
        f"{args.beat_frequency/1e6:g} MHz beat, {args.signal_rms*1e3:g} mV RMS signal"
    )
    axes[1].text(
        0.015,
        0.025,
        r"$S_\phi^{1/2}=\sqrt{(S_{V,-}+S_{V,+})/2}/V_{beat,rms}$; "
        r"$|H_{PLL}|=[1+(f/f_{BW})^2]^{-1/2}$",
        transform=axes[1].transAxes,
        fontsize=9,
        va="bottom",
        bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "0.75"},
    )

    output_stem = (
        f"RIN_20261013_amplitude_to_phase_"
        f"{args.beat_frequency/1e6:g}MHz_PLL{args.pll_bandwidth/1e3:g}kHz"
    )
    plot_path = data_path.with_name(output_stem + ".png")
    fig.savefig(plot_path, dpi=200)
    plt.close(fig)

    numeric_path = data_path.with_name(output_stem + ".npz")
    results = {
        "offset_frequency_Hz": offset,
        "pll_response": pll_response,
        "beat_frequency_Hz": args.beat_frequency,
        "pll_bandwidth_Hz": args.pll_bandwidth,
        "signal_voltage_rms_V": args.signal_rms,
    }
    key_names = {
        "PD dark + ADC/electronics": "dark",
        "Reference laser": "reference_laser",
        "Laser 1": "laser1",
    }
    for label, key in key_names.items():
        results[f"{key}_phase_asd_before_pll_rad_per_sqrt_Hz"] = phase_input[label]
        results[f"{key}_phase_asd_at_pll_output_rad_per_sqrt_Hz"] = phase_output[label]
    np.savez(numeric_path, **results)

    print(f"Offsets: {offset[0]:.6g} to {offset[-1]:.6g} Hz ({len(offset):,} bins)")
    print(f"Assumed signal: {args.signal_rms:g} V RMS at {args.beat_frequency:g} Hz")
    print(f"PLL: first-order low-pass, {args.pll_bandwidth:g} Hz bandwidth")
    print(f"Saved: {plot_path}")
    print(f"Saved: {numeric_path}")


if __name__ == "__main__":
    main()
