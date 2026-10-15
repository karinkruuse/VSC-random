"""Diagnose linear amplitude-to-frequency coupling in synchronized PM data."""
from pathlib import Path
import argparse

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import coherence, welch


ROLE_COLORS = {
    "Carrier": "black",
    "LSB": "#295f24",
    "USB": "#821770",
    "Sideband common": "tab:blue",
    "Sideband differential": "tab:orange",
    "(USB - LSB) / 2": "tab:blue",
}


def resolve_synced(path):
    path = Path(path).resolve()
    if path.is_file():
        return path
    matches = sorted(path.glob("*_synced.npy"))
    if len(matches) != 1:
        raise ValueError(f"Expected one synchronized NPY file in {path}, found {len(matches)}")
    return matches[0]


def asd(series, fs, nperseg, noverlap):
    frequency, density = welch(
        series, fs=fs, window="hann", nperseg=nperseg,
        noverlap=noverlap, detrend="linear", scaling="density",
    )
    return frequency, np.sqrt(density)


def analyse(path, welch_seconds, band_limits):
    path = resolve_synced(path)
    data = np.load(path, mmap_mode="r", allow_pickle=False)
    time = np.asarray(data["Time (s)"])
    dt = np.median(np.diff(time))
    fs = 1 / dt
    if not np.all(np.isfinite(time)) or not np.allclose(
            np.diff(time), dt, rtol=1e-5, atol=1e-9):
        raise ValueError(f"Nonuniform time data in {path}")

    channels = [int(name.split()[1]) for name in data.dtype.names
                if name.startswith("Input ")
                and name.endswith(" Frequency (Hz)")
                and "Set Frequency" not in name]
    if len(channels) != 3:
        raise ValueError(f"Expected three frequency channels in {path}")
    lower, carrier, upper = sorted(
        channels, key=lambda ch: np.median(data[f"Input {ch} Frequency (Hz)"]))
    role_channels = {"Carrier": carrier, "LSB": lower, "USB": upper}

    frequencies = {
        role: np.asarray(data[f"Input {channel} Frequency (Hz)"])
        for role, channel in role_channels.items()
    }
    amplitudes = {}
    relative_amplitudes = {}
    for role, channel in role_channels.items():
        amplitude = np.hypot(
            np.asarray(data[f"Input {channel} I (V)"]),
            np.asarray(data[f"Input {channel} Q (V)"]),
        )
        median = np.median(amplitude)
        if not np.isfinite(median) or median <= 0:
            raise ValueError(f"Invalid {role} amplitude in {path}")
        amplitudes[role] = amplitude
        relative_amplitudes[role] = amplitude / median - 1

    relative_amplitudes["Sideband common"] = (
        relative_amplitudes["LSB"] + relative_amplitudes["USB"]) / 2
    relative_amplitudes["Sideband differential"] = (
        relative_amplitudes["USB"] - relative_amplitudes["LSB"]) / 2
    modulation = (frequencies["USB"] - frequencies["LSB"]) / 2
    modulation_phase = (
        np.asarray(data[f"Input {upper} Phase (cyc)"])
        - np.asarray(data[f"Input {lower} Phase (cyc)"])
    ) / 2

    nperseg = min(len(time), int(round(welch_seconds * fs)))
    if nperseg < 256:
        raise ValueError(f"Need at least 256 samples in {path}")
    noverlap = nperseg // 2
    step = nperseg - noverlap
    segments = 1 + (len(time) - nperseg) // step
    if segments < 2:
        raise ValueError(f"Need at least two Welch windows in {path}; shorten --welch-seconds")
    coherence_95 = 1 - 0.05 ** (1 / (segments - 1))

    frequency_asds = {}
    for role, values in frequencies.items():
        spectral_frequency, frequency_asds[role] = asd(values, fs, nperseg, noverlap)
    _, frequency_asds["(USB - LSB) / 2"] = asd(
        modulation, fs, nperseg, noverlap)
    _, direct_phase_asd = asd(modulation_phase, fs, nperseg, noverlap)
    derived_phase_asd = np.full_like(direct_phase_asd, np.nan)
    positive_phase = spectral_frequency > 0
    derived_phase_asd[positive_phase] = (
        frequency_asds["(USB - LSB) / 2"][positive_phase]
        / (2 * np.pi * spectral_frequency[positive_phase])
    )
    amplitude_asds = {}
    for role, values in relative_amplitudes.items():
        _, amplitude_asds[role] = asd(values, fs, nperseg, noverlap)

    modulation_coherence = {}
    for role, values in relative_amplitudes.items():
        _, modulation_coherence[role] = coherence(
            modulation, values, fs=fs, window="hann", nperseg=nperseg,
            noverlap=noverlap, detrend="linear",
        )
    channel_coherence = {}
    for role in ("Carrier", "LSB", "USB"):
        _, channel_coherence[role] = coherence(
            frequencies[role], relative_amplitudes[role], fs=fs,
            window="hann", nperseg=nperseg, noverlap=noverlap,
            detrend="linear",
        )

    positive = spectral_frequency > 0
    band = ((spectral_frequency >= band_limits[0])
            & (spectral_frequency <= band_limits[1]))
    if not np.any(band):
        raise ValueError(f"Diagnostic band {band_limits} is outside the spectrum for {path}")
    band_indices = np.flatnonzero(band)
    modulation_peak_index = band_indices[np.argmax(
        frequency_asds["(USB - LSB) / 2"][band])]
    phase_ratio = direct_phase_asd / derived_phase_asd

    prefix = path.with_suffix("")
    figure_path = prefix.with_name(prefix.name + "_amplitude_frequency_coupling.png")
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), sharex=True)
    for role in ("Carrier", "LSB", "USB", "(USB - LSB) / 2"):
        axes[0, 0].loglog(
            spectral_frequency[positive], frequency_asds[role][positive],
            label=role, color=ROLE_COLORS[role], linewidth=1,
        )
    axes[0, 0].set_ylabel(r"Frequency ASD (Hz/$\sqrt{Hz}$)")
    axes[0, 0].set_title("Frequency noise")
    axes[0, 0].text(
        .02, .03,
        f"Direct/derived phase ASD at band peak: "
        f"{phase_ratio[modulation_peak_index]:.3f}",
        transform=axes[0, 0].transAxes, fontsize=8,
        bbox={"facecolor": "white", "alpha": .75, "edgecolor": "none"},
    )

    for role in ("Carrier", "LSB", "USB"):
        axes[0, 1].loglog(
            spectral_frequency[positive], amplitude_asds[role][positive],
            label=role, color=ROLE_COLORS[role], linewidth=1,
        )
    axes[0, 1].set_ylabel(r"Fractional-amplitude ASD (1/$\sqrt{Hz}$)")
    axes[0, 1].set_title(r"Beat amplitude $\sqrt{I^2+Q^2}$")

    for role in ("Carrier", "LSB", "USB", "Sideband differential"):
        axes[1, 0].semilogx(
            spectral_frequency[positive], modulation_coherence[role][positive],
            label=role, color=ROLE_COLORS[role], linewidth=1,
        )
    axes[1, 0].set_ylabel("Magnitude-squared coherence")
    axes[1, 0].set_title("Modulation-frequency estimate vs amplitude")

    for role in ("Carrier", "LSB", "USB"):
        axes[1, 1].semilogx(
            spectral_frequency[positive], channel_coherence[role][positive],
            label=role, color=ROLE_COLORS[role], linewidth=1,
        )
    axes[1, 1].set_ylabel("Magnitude-squared coherence")
    axes[1, 1].set_title("Each beat frequency vs its own amplitude")

    for ax in axes.flat:
        ax.axvspan(*band_limits, color="gray", alpha=.08)
        ax.grid(True, which="both", alpha=.25)
        ax.legend(fontsize=8)
        ax.set_xlim(spectral_frequency[positive][0], spectral_frequency[-1])
    for ax in axes[1]:
        ax.axhline(coherence_95, color="gray", linestyle=":", linewidth=1,
                   label="approx. 95% null threshold")
        ax.set_ylim(0, 1)
        ax.set_xlabel("Fourier frequency (Hz)")
    # Add threshold labels after the other curves so it appears once per legend.
    for ax in axes[1]:
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, fontsize=8)
    fig.suptitle(
        f"{path.parent.name}: amplitude/frequency coupling diagnostic\n"
        f"{welch_seconds:g} s Welch windows, {segments} windows; shaded band "
        f"{band_limits[0]:g}–{band_limits[1]:g} Hz",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, .94))
    fig.savefig(figure_path, dpi=200)
    plt.close(fig)

    lines = [
        f"Source: {path.name}",
        f"Samples: {len(time)}; duration: {time[-1]-time[0]:.9g} s; fs: {fs:.12g} Hz",
        f"Welch/coherence: {nperseg} samples ({nperseg/fs:.6f} s), 50% overlap, "
        f"{segments} windows, Hann, linear detrend",
        f"Diagnostic band: {band_limits[0]:g}-{band_limits[1]:g} Hz",
        f"Approximate 95% zero-coherence threshold: {coherence_95:.6g}",
        "The threshold is pointwise and approximate; isolated crossings can occur by chance.",
        "",
        "Amplitude statistics:",
    ]
    for role in ("Carrier", "LSB", "USB"):
        median = np.median(amplitudes[role])
        rel_std = np.std(amplitudes[role]) / median
        amp_peak = band_indices[np.argmax(amplitude_asds[role][band])]
        lines.append(
            f"{role}: median={median:.9g} V; relative std={rel_std:.9g}; "
            f"band ASD peak={amplitude_asds[role][amp_peak]:.9g} 1/sqrt(Hz) "
            f"at {spectral_frequency[amp_peak]:.9g} Hz"
        )
    lines.extend([
        "",
        f"Modulation-frequency ASD band peak: "
        f"{frequency_asds['(USB - LSB) / 2'][modulation_peak_index]:.9g} Hz/sqrt(Hz) "
        f"at {spectral_frequency[modulation_peak_index]:.9g} Hz",
        f"Direct modulation-phase ASD at that frequency: "
        f"{direct_phase_asd[modulation_peak_index]:.9g} cycles/sqrt(Hz)",
        f"Phase ASD derived from frequency at that frequency: "
        f"{derived_phase_asd[modulation_peak_index]:.9g} cycles/sqrt(Hz)",
        f"Direct/derived phase ASD ratio at peak: "
        f"{phase_ratio[modulation_peak_index]:.9g}; "
        f"band median ratio: {np.median(phase_ratio[band]):.9g}",
        "",
        "Coherence of (USB-LSB)/2 frequency with amplitude:",
    ])
    for role in ("Carrier", "LSB", "USB", "Sideband common", "Sideband differential"):
        values = modulation_coherence[role]
        lines.append(
            f"{role}: at modulation peak={values[modulation_peak_index]:.6g}; "
            f"band median={np.median(values[band]):.6g}; band max={np.max(values[band]):.6g}; "
            f"bins above threshold={np.mean(values[band] > coherence_95):.3%}"
        )
    lines.extend(["", "Coherence of each beat frequency with its own amplitude:"])
    for role in ("Carrier", "LSB", "USB"):
        values = channel_coherence[role]
        lines.append(
            f"{role}: at modulation peak={values[modulation_peak_index]:.6g}; "
            f"band median={np.median(values[band]):.6g}; band max={np.max(values[band]):.6g}; "
            f"bins above threshold={np.mean(values[band] > coherence_95):.3%}"
        )
    summary_path = prefix.with_name(prefix.name + "_amplitude_frequency_summary.txt")
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    spectrum_path = prefix.with_name(prefix.name + "_amplitude_frequency_asd.npz")
    np.savez(
        spectrum_path,
        frequency_Hz=spectral_frequency,
        frequency_asd_modulation_Hz_per_sqrtHz=frequency_asds["(USB - LSB) / 2"],
        phase_asd_modulation_direct_cycles_per_sqrtHz=direct_phase_asd,
        phase_asd_modulation_from_frequency_cycles_per_sqrtHz=derived_phase_asd,
        fractional_amplitude_asd_carrier=amplitude_asds["Carrier"],
        fractional_amplitude_asd_LSB=amplitude_asds["LSB"],
        fractional_amplitude_asd_USB=amplitude_asds["USB"],
        fractional_amplitude_asd_sideband_common=amplitude_asds["Sideband common"],
        fractional_amplitude_asd_sideband_differential=amplitude_asds["Sideband differential"],
        coherence_modulation_carrier_amplitude=modulation_coherence["Carrier"],
        coherence_modulation_LSB_amplitude=modulation_coherence["LSB"],
        coherence_modulation_USB_amplitude=modulation_coherence["USB"],
        coherence_modulation_sideband_common_amplitude=modulation_coherence["Sideband common"],
        coherence_modulation_sideband_differential_amplitude=modulation_coherence["Sideband differential"],
    )
    return {
        "name": path.parent.name,
        "path": path,
        "frequency": spectral_frequency,
        "modulation_asd": frequency_asds["(USB - LSB) / 2"],
        "common_amplitude_asd": amplitude_asds["Sideband common"],
        "common_coherence": modulation_coherence["Sideband common"],
        "threshold": coherence_95,
        "segments": segments,
        "duration": time[-1] - time[0],
        "peak_index": modulation_peak_index,
        "phase_ratio_peak": phase_ratio[modulation_peak_index],
        "band": band,
        "figure": figure_path,
        "summary": summary_path,
    }


def save_comparison(results, output, band_limits):
    fig, axes = plt.subplots(3, 1, figsize=(10, 11), sharex=True)
    lines = [
        f"Shared Welch window: comparison spectra use the per-run settings reported below.",
        f"Diagnostic band: {band_limits[0]:g}-{band_limits[1]:g} Hz",
        "",
    ]
    for result in results:
        f = result["frequency"]
        positive = f > 0
        axes[0].loglog(f[positive], result["modulation_asd"][positive],
                       label=result["name"], linewidth=1)
        axes[1].loglog(f[positive], result["common_amplitude_asd"][positive],
                       label=result["name"], linewidth=1)
        axes[2].semilogx(f[positive], result["common_coherence"][positive],
                         label=result["name"], linewidth=1)
        peak = result["peak_index"]
        band = result["band"]
        lines.append(
            f"{result['name']}: duration={result['duration']:.6g} s; "
            f"windows={result['segments']}; modulation peak="
            f"{result['modulation_asd'][peak]:.6g} Hz/sqrt(Hz) at {f[peak]:.6g} Hz; "
            f"common-amplitude coherence at peak={result['common_coherence'][peak]:.6g}; "
            f"band median coherence={np.median(result['common_coherence'][band]):.6g}; "
            f"approx95={result['threshold']:.6g}; "
            f"direct/derived phase ASD={result['phase_ratio_peak']:.6g}"
        )
    axes[0].set_ylabel(r"Modulation frequency ASD (Hz/$\sqrt{Hz}$)")
    axes[0].set_title(r"$(USB-LSB)/2$ frequency noise")
    axes[1].set_ylabel(r"Common sideband amplitude ASD (1/$\sqrt{Hz}$)")
    axes[1].set_title("Common fractional-amplitude noise of LSB and USB")
    axes[2].set_ylabel("Magnitude-squared coherence")
    axes[2].set_xlabel("Fourier frequency (Hz)")
    axes[2].set_ylim(0, 1)
    axes[2].set_title("Modulation frequency vs common sideband amplitude")
    for ax in axes:
        ax.axvspan(*band_limits, color="gray", alpha=.08)
        ax.grid(True, which="both", alpha=.25)
        ax.legend(fontsize=8)
    fig.suptitle("Multi-phasemeter amplitude/frequency comparison", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, .97))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=200)
    plt.close(fig)
    output.with_suffix(".txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", nargs="*", type=Path,
                        help="Synchronized NPY files or measurement directories")
    parser.add_argument("--welch-seconds", type=float, default=32,
                        help="Welch/coherence window duration (default: 32 s)")
    parser.add_argument("--band", nargs=2, type=float, default=(.3, 1.5),
                        metavar=("LOW", "HIGH"),
                        help="Frequency band used for diagnostics (default: 0.3 1.5 Hz)")
    parser.add_argument("--comparison-output", type=Path,
                        help="Combined PNG path; defaults to multi_PM/comparisons")
    args = parser.parse_args()
    if args.welch_seconds <= 0 or args.band[0] <= 0 or args.band[1] <= args.band[0]:
        parser.error("Welch duration and ordered positive band limits are required")

    script_root = Path(__file__).resolve().parent
    multi_pm = script_root / "data" / "multi_PM"
    if args.data:
        paths = args.data
    else:
        paths = sorted(p.parent for p in multi_pm.glob("mod*/*_synced.npy"))
    if not paths:
        parser.error("No synchronized measurements found")

    results = []
    for path in paths:
        result = analyse(path, args.welch_seconds, args.band)
        results.append(result)
        print(f"Saved: {result['figure']}")
        print(f"Saved: {result['summary']}")
    output = args.comparison_output or (
        multi_pm / "comparisons" / "multi_pm_amplitude_frequency_comparison.png")
    save_comparison(results, output.resolve(), args.band)
    print(f"Saved: {output.resolve()}")


if __name__ == "__main__":
    main()
