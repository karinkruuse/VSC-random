"""Compare the modulation-frequency ASD of two synchronized measurements."""
# python modulation_noise/proper_3signal.py modulation_noise/data/multi_PM/mod19_20261014_1358 --welch-seconds 128 --debug --exclude-spikes --direct-phase
from pathlib import Path
import argparse

import matplotlib.pyplot as plt
import numpy as np

from proper_3signal import frequency_asd


def modulation_trace(path):
    data = np.load(path, allow_pickle=False)
    t = data["Time (s)"]
    fs = 1 / np.median(np.diff(t))
    inputs = [int(name.split()[1]) for name in data.dtype.names
              if name.startswith("Input ")
              and name.endswith(" Frequency (Hz)")
              and "Set Frequency" not in name]
    lower, _, upper = sorted(
        inputs, key=lambda channel: np.median(data[f"Input {channel} Frequency (Hz)"]))
    modulation = (data[f"Input {upper} Frequency (Hz)"]
                  - data[f"Input {lower} Frequency (Hz)"]) / 2
    return t, modulation, fs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("comparison", type=Path)
    parser.add_argument("--welch-seconds", type=float, default=32)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    t_ref, x_ref, fs_ref = modulation_trace(args.reference)
    t_new, x_new, fs_new = modulation_trace(args.comparison)
    if not np.isclose(fs_ref, fs_new, rtol=1e-8):
        raise ValueError("Measurements have different sampling rates")
    nperseg = int(round(args.welch_seconds * fs_ref))
    if min(len(x_ref), len(x_new)) < nperseg:
        raise ValueError("Welch window is longer than one of the measurements")
    f_ref, asd_ref = frequency_asd(x_ref, fs_ref, nperseg)
    f_new, asd_new = frequency_asd(x_new, fs_new, nperseg)
    if not np.array_equal(f_ref, f_new):
        raise ValueError("Welch frequency grids differ")
    positive = f_ref > 0
    f, asd_ref, asd_new = f_ref[positive], asd_ref[positive], asd_new[positive]
    ratio = asd_new / asd_ref

    fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1]})
    axes[0].loglog(f, asd_ref, label="13:16 run", color="tab:blue")
    axes[0].loglog(f, asd_new, label="13:45 run", color="tab:orange")
    axes[0].set_ylabel(r"Frequency ASD (Hz/$\sqrt{Hz}$)")
    axes[0].set_title(r"19 MHz modulation estimate: $(USB-LSB)/2$")
    axes[0].grid(True, which="both", alpha=.25)
    axes[0].legend()
    axes[1].semilogx(f, ratio, color="black", linewidth=.8)
    axes[1].axhline(1, color="gray", linestyle=":")
    axes[1].set(xlabel="Fourier frequency (Hz)",
                ylabel="13:45 / 13:16", xlim=(f[0], f[-1]))
    axes[1].grid(True, which="both", alpha=.25)
    fig.tight_layout()
    output = args.output.with_suffix(".png")
    fig.savefig(output, dpi=200)
    plt.close(fig)

    lines = [
        f"Reference: {args.reference.name}; duration={t_ref[-1]-t_ref[0]:.6f} s",
        f"Comparison: {args.comparison.name}; duration={t_new[-1]-t_new[0]:.6f} s",
        f"Welch window: {nperseg} samples = {nperseg/fs_ref:.6f} s; linear detrending",
        f"Frequency spacing: {f[0]:.9g} Hz",
        "",
        "Median modulation-frequency ASD and comparison ratio:",
    ]
    for low, high in ((.03, .1), (.1, 1), (1, 10)):
        select = (f >= low) & (f < high)
        if np.any(select):
            old = np.median(asd_ref[select])
            new = np.median(asd_new[select])
            lines.append(f"{low:g}-{high:g} Hz: 13:16={old:.9g}, 13:45={new:.9g} Hz/sqrt(Hz), ratio={new/old:.6g}")
    args.output.with_suffix(".txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
