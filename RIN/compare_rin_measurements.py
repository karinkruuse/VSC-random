"""Compare the three 2026-10-13 RIN recordings and their dark reference."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


FOLDER = Path(__file__).resolve().parent / "power issue"
RECORDINGS = {
    "dark": "RIN_20261013_173926",
    "reference": "RIN_20261013_180059",
    "laser1": "RIN_20261013_180231",
}
REFERENCE_DC_V = 1.43
LASER1_DC_V = 1.156


def load_spectrum(stem: str):
    path = FOLDER / f"{stem}_rin_asd.npz"
    data = np.load(path)
    return data["frequency_Hz"], data["voltage_asd_V_per_sqrt_Hz"]


def main() -> None:
    frequency, dark_voltage = load_spectrum(RECORDINGS["dark"])
    f_reference, reference_voltage = load_spectrum(RECORDINGS["reference"])
    f_laser1, laser1_voltage = load_spectrum(RECORDINGS["laser1"])
    if not (np.array_equal(frequency, f_reference) and np.array_equal(frequency, f_laser1)):
        raise ValueError("The three saved spectra do not share the same frequency grid")

    fig, ax = plt.subplots(figsize=(11, 6), constrained_layout=True)
    ax.loglog(frequency, dark_voltage, color="0.2", linewidth=0.8,
              label="PD dark + ADC/electronics")
    ax.loglog(frequency, reference_voltage, color="#4C78A8", linewidth=0.8,
              label="Reference laser")
    ax.loglog(frequency, laser1_voltage, color="#F58518", linewidth=0.8,
              label="Laser 1")
    ax.set(xlabel="Frequency (Hz)", ylabel=r"Voltage ASD (V/$\sqrt{\mathrm{Hz}}$)",
           title="2026-10-13 photodetector voltage-noise comparison",
           xlim=(frequency[0], frequency[-1]))
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(loc="best")
    ax.text(0.015, 0.025,
            "Welch: Hann, 1,048,576 samples, 50% overlap, 575 windows per trace",
            transform=ax.transAxes, fontsize=9, va="bottom",
            bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "0.75"})
    voltage_path = FOLDER / "RIN_20261013_voltage_asd_comparison.png"
    fig.savefig(voltage_path, dpi=200)
    plt.close(fig)

    reference_rin = reference_voltage / REFERENCE_DC_V
    laser1_rin = laser1_voltage / LASER1_DC_V
    dark_as_reference_rin = dark_voltage / REFERENCE_DC_V
    dark_as_laser1_rin = dark_voltage / LASER1_DC_V

    fig, ax = plt.subplots(figsize=(11, 6), constrained_layout=True)
    ax.loglog(frequency, reference_rin, color="#4C78A8", linewidth=0.85,
              label=f"Reference laser / {REFERENCE_DC_V:g} V")
    ax.loglog(frequency, dark_as_reference_rin, color="#4C78A8", linestyle="--",
              linewidth=0.8, alpha=0.9,
              label=f"Dark-equivalent floor / {REFERENCE_DC_V:g} V")
    ax.loglog(frequency, laser1_rin, color="#F58518", linewidth=0.85,
              label=f"Laser 1 / {LASER1_DC_V:g} V")
    ax.loglog(frequency, dark_as_laser1_rin, color="#F58518", linestyle="--",
              linewidth=0.8, alpha=0.9,
              label=f"Dark-equivalent floor / {LASER1_DC_V:g} V")
    ax.set(xlabel="Frequency (Hz)", ylabel=r"RIN ASD (1/$\sqrt{\mathrm{Hz}}$)",
           title="2026-10-13 RIN with PD-dark + electronics reference",
           xlim=(frequency[0], frequency[-1]))
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(loc="best")
    ax.text(0.015, 0.025,
            "Solid: illuminated measurement   Dashed: measured dark voltage ASD / illuminated DC\n"
            "Raw comparison; no quadrature subtraction",
            transform=ax.transAxes, fontsize=9, va="bottom",
            bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "0.75"})
    rin_path = FOLDER / "RIN_20261013_rin_asd_comparison.png"
    fig.savefig(rin_path, dpi=200)
    plt.close(fig)

    numeric_path = FOLDER / "RIN_20261013_asd_comparison.npz"
    np.savez(
        numeric_path,
        frequency_Hz=frequency,
        dark_voltage_asd_V_per_sqrt_Hz=dark_voltage,
        reference_voltage_asd_V_per_sqrt_Hz=reference_voltage,
        laser1_voltage_asd_V_per_sqrt_Hz=laser1_voltage,
        reference_rin_asd_per_sqrt_Hz=reference_rin,
        laser1_rin_asd_per_sqrt_Hz=laser1_rin,
        dark_equivalent_reference_rin_asd_per_sqrt_Hz=dark_as_reference_rin,
        dark_equivalent_laser1_rin_asd_per_sqrt_Hz=dark_as_laser1_rin,
        reference_dc_voltage_V=REFERENCE_DC_V,
        laser1_dc_voltage_V=LASER1_DC_V,
    )
    print(f"Saved: {voltage_path}")
    print(f"Saved: {rin_path}")
    print(f"Saved: {numeric_path}")


if __name__ == "__main__":
    main()
