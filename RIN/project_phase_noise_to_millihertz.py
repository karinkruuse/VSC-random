"""Project the measured 5 MHz additive-noise phase floor into the mHz band.

This is an extrapolation, not a direct mHz measurement: the 30 s RIN records
and the full-band Welch configuration do not resolve millihertz offsets around
the hypothetical beat note.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


FOLDER = Path(__file__).resolve().parent / "power issue"
INPUT = FOLDER / "RIN_20261013_amplitude_to_phase_5MHz_PLL10kHz.npz"
OUTPUT = FOLDER / "RIN_20261013_phase_noise_millihertz_projection.png"
WAVELENGTH_M = 1064e-9
REFERENCE_READOUT_FLOOR_CYCLES = 1.3e-6


def main() -> None:
    data = np.load(INPUT)
    measured_offset = data["offset_frequency_Hz"]
    representative = (measured_offset >= 10) & (measured_offset <= 1000)
    curves = {
        "PD dark + ADC/electronics": np.median(
            data["dark_phase_asd_before_pll_rad_per_sqrt_Hz"][representative]
        ) / (2 * np.pi),
        "Reference laser": np.median(
            data["reference_laser_phase_asd_before_pll_rad_per_sqrt_Hz"][representative]
        ) / (2 * np.pi),
        "Laser 1": np.median(
            data["laser1_phase_asd_before_pll_rad_per_sqrt_Hz"][representative]
        ) / (2 * np.pi),
    }
    colors = {
        "PD dark + ADC/electronics": "0.2",
        "Reference laser": "#4C78A8",
        "Laser 1": "#F58518",
    }

    frequency_mHz = np.logspace(np.log10(0.05), np.log10(100), 500)
    frequency_Hz = frequency_mHz * 1e-3
    pll_bandwidth = float(data["pll_bandwidth_Hz"])
    pll_response = 1 / np.sqrt(1 + (frequency_Hz / pll_bandwidth) ** 2)

    fig, ax = plt.subplots(figsize=(11, 6), constrained_layout=True)
    for label, floor in curves.items():
        linestyle = "--" if label.startswith("PD dark") else "-"
        ax.loglog(frequency_mHz, floor * pll_response, color=colors[label],
                  linestyle=linestyle, linewidth=1.8,
                  label=rf"{label}: {floor:.2e} cycles/$\sqrt{{Hz}}$")
    ax.axhline(REFERENCE_READOUT_FLOOR_CYCLES, color="#8172B2", linestyle=":",
               linewidth=1.8,
               label=r"Earlier quoted readout floor: $1.3\times10^{-6}$ cycles/$\sqrt{Hz}$")
    ax.axvspan(0.1, 10, color="0.7", alpha=0.12, label="0.1–10 mHz region")
    ax.set(
        xlabel="Fourier frequency (mHz)",
        ylabel=r"Projected phase ASD (cycles/$\sqrt{\mathrm{Hz}}$)",
        title="Projected 5 MHz beat-note amplitude-noise limit in the mHz band",
        xlim=(frequency_mHz[0], frequency_mHz[-1]),
        ylim=(1e-8, 3e-6),
    )
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(loc="best")
    ax.text(
        0.015,
        0.025,
        "White-floor extrapolation from measured 10–1000 Hz offsets around 5 MHz\n"
        "500 mV RMS beat; 10 kHz PLL response is unity to plotting precision in this band",
        transform=ax.transAxes,
        fontsize=9,
        va="bottom",
        bbox={"facecolor": "white", "alpha": 0.9, "edgecolor": "0.75"},
    )

    # For a single-pass 1064 nm conversion, cycles * wavelength gives metres.
    secondary = ax.secondary_yaxis(
        "right",
        functions=(lambda cycles: cycles * WAVELENGTH_M * 1e12,
                   lambda pm: pm / (WAVELENGTH_M * 1e12)),
    )
    secondary.set_ylabel(r"Equivalent displacement ASD at 1064 nm (pm/$\sqrt{\mathrm{Hz}}$)")
    fig.savefig(OUTPUT, dpi=200)
    plt.close(fig)

    numeric = FOLDER / "RIN_20261013_phase_noise_millihertz_projection.npz"
    np.savez(
        numeric,
        frequency_mHz=frequency_mHz,
        pll_response=pll_response,
        dark_cycles_per_sqrt_Hz=curves["PD dark + ADC/electronics"] * pll_response,
        reference_laser_cycles_per_sqrt_Hz=curves["Reference laser"] * pll_response,
        laser1_cycles_per_sqrt_Hz=curves["Laser 1"] * pll_response,
        reference_readout_floor_cycles_per_sqrt_Hz=REFERENCE_READOUT_FLOOR_CYCLES,
        wavelength_m=WAVELENGTH_M,
        projection_source_min_offset_Hz=10.0,
        projection_source_max_offset_Hz=1000.0,
    )
    for label, floor in curves.items():
        print(f"{label}: {floor:.6g} cycles/sqrt(Hz), "
              f"{floor * WAVELENGTH_M * 1e12:.6g} pm/sqrt(Hz)")
    print(f"Saved: {OUTPUT}")
    print(f"Saved: {numeric}")


if __name__ == "__main__":
    main()
