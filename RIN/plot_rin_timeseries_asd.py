"""Plot a Moku RIN time series and its relative-intensity-noise ASD.

The input is the structured NumPy array exported alongside a Moku text header.
Large recordings are processed in bounded-memory batches. For an AC-coupled
recording, supply the independently measured DC photodetector voltage.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import welch


def metadata_value(text: str, pattern: str, name: str) -> float:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not find {name} in the matching text metadata")
    return float(match.group(1))


def minmax_envelope(
    y: np.ndarray, sample_rate: float, start_time: float, points: int = 25_000
):
    """Return a plotting-sized envelope without hiding short excursions."""
    block = max(1, int(np.ceil(len(y) / points)))
    complete = len(y) // block * block
    rows = complete // block
    low = np.empty(rows + (complete < len(y)))
    high = np.empty_like(low)
    mean = np.empty_like(low)

    # Limit each reduction to roughly 128 MiB of contiguous voltage values.
    rows_per_batch = max(1, (128 * 2**20) // (8 * block))
    for row0 in range(0, rows, rows_per_batch):
        row1 = min(rows, row0 + rows_per_batch)
        values = np.ascontiguousarray(y[row0 * block : row1 * block]).reshape(-1, block)
        low[row0:row1] = np.min(values, axis=1)
        high[row0:row1] = np.max(values, axis=1)
        mean[row0:row1] = np.mean(values, axis=1)

    if complete < len(y):
        tail = np.ascontiguousarray(y[complete:])
        low[-1] = np.min(tail)
        high[-1] = np.max(tail)
        mean[-1] = np.mean(tail)

    sample_centers = np.arange(len(low), dtype=float) * block + 0.5 * (block - 1)
    sample_centers[-1] = min(sample_centers[-1], 0.5 * (complete + len(y) - 1))
    center = start_time + sample_centers / sample_rate
    return center, low, high, mean


def streaming_welch(
    y: np.ndarray,
    sample_rate: float,
    nperseg: int,
    noverlap: int,
    batch_segments: int = 16,
):
    """Compute the mean Welch PSD in bounded memory, including every segment."""
    step = nperseg - noverlap
    segment_count = 1 + (len(y) - nperseg) // step
    psd_sum = None
    frequency = None
    completed = 0
    next_report = 10

    while completed < segment_count:
        count = min(batch_segments, segment_count - completed)
        start = completed * step
        stop = start + nperseg + (count - 1) * step
        values = np.ascontiguousarray(y[start:stop], dtype=np.float64)
        frequency, batch_psd = welch(
            values,
            fs=sample_rate,
            window="hann",
            nperseg=nperseg,
            noverlap=noverlap,
            detrend="constant",
            return_onesided=True,
            scaling="density",
            average="mean",
        )
        if psd_sum is None:
            psd_sum = batch_psd * count
        else:
            psd_sum += batch_psd * count
        completed += count
        percent = completed * 100 // segment_count
        if percent >= next_report or completed == segment_count:
            print(f"Welch progress: {completed:,}/{segment_count:,} windows ({percent}%)", flush=True)
            next_report = (percent // 10 + 1) * 10

    return frequency, psd_sum / segment_count, segment_count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("npy", type=Path, help="Moku structured .npy recording")
    parser.add_argument(
        "--dc-voltage",
        type=float,
        action="append",
        help=("Photodetector DC voltage in V; repeat to compare normalizations "
              "(default: parse '<value> mV mean' from .txt)"),
    )
    parser.add_argument(
        "--fraction",
        type=float,
        default=1.0,
        help="Analyze this leading fraction of the recording (default: 1)",
    )
    parser.add_argument("--tag", help="Suffix added to output filenames")
    parser.add_argument(
        "--nperseg",
        type=int,
        default=2**20,
        help="Samples per Hann window for Welch ASD (default: 1048576)",
    )
    parser.add_argument(
        "--batch-segments",
        type=int,
        default=16,
        help="Welch windows per memory-bounded batch (default: 16)",
    )
    args = parser.parse_args()
    if not 0 < args.fraction <= 1:
        parser.error("--fraction must be in (0, 1]")
    if args.batch_segments < 1:
        parser.error("--batch-segments must be positive")

    npy_path = args.npy.resolve()
    txt_path = npy_path.with_suffix(".txt")
    metadata = txt_path.read_text(encoding="utf-8", errors="replace")
    sample_rate = metadata_value(
        metadata, r"Acquisition:.*?([0-9.eE+\-]+)\s*Hz", "sample rate"
    )
    dc_voltages = args.dc_voltage
    if dc_voltages is None:
        dc_mv = metadata_value(metadata, r"([0-9.eE+\-]+)\s*mV\s+mean", "DC voltage")
        dc_voltages = [dc_mv * 1e-3]
    if any(value <= 0 for value in dc_voltages):
        raise ValueError("DC normalization voltages must be positive")

    data = np.load(npy_path, mmap_mode="r")
    if data.dtype.names is None or "Time (s)" not in data.dtype.names:
        raise ValueError(f"Expected a 'Time (s)' field; found {data.dtype.names}")
    voltage_fields = [name for name in data.dtype.names if re.search(r"Input \d+ \(V\)", name)]
    if len(voltage_fields) != 1:
        raise ValueError(f"Expected exactly one voltage field; found {voltage_fields}")

    sample_count = min(len(data), max(2, int(np.floor(len(data) * args.fraction))))
    t = data["Time (s)"][:sample_count]
    voltage = data[voltage_fields[0]][:sample_count]
    output_stem = npy_path.stem + (f"_{args.tag}" if args.tag else "")
    print(
        f"Analyzing {sample_count:,}/{len(data):,} samples ({sample_count/len(data):.3%}), "
        f"field '{voltage_fields[0]}'",
        flush=True,
    )

    print("Building time-series envelope...", flush=True)
    center, low, high, mean = minmax_envelope(voltage, sample_rate, float(t[0]))
    # Cap the raw detail panel at 20,000 points so multi-MHz traces remain legible.
    detail_samples = min(len(voltage), 20_000, max(2, int(round(0.020 * sample_rate))))
    detail_ms = (detail_samples - 1) / sample_rate * 1e3
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), constrained_layout=True)
    axes[0].fill_between(center, low * 1e3, high * 1e3, color="#4C78A8", alpha=0.35,
                         linewidth=0, label="min–max envelope")
    axes[0].plot(center, mean * 1e3, color="#1F4E79", linewidth=0.7,
                 label="block mean")
    axes[0].set(xlabel="Time (s)", ylabel="AC voltage (mV)", title="Analyzed recording")
    axes[0].grid(alpha=0.25)
    axes[0].legend(loc="best")
    detail_time_ms = (np.asarray(t[:detail_samples]) - float(t[0])) * 1e3
    axes[1].plot(detail_time_ms, voltage[:detail_samples] * 1e3,
                 color="#1F4E79", linewidth=0.55)
    axes[1].set(xlabel="Time (ms)", ylabel="AC voltage (mV)",
                title=f"First {detail_ms:.3f} ms (raw samples)")
    axes[1].grid(alpha=0.25)
    fig.suptitle(f"{npy_path.stem}: photodetector time series")
    timeseries_path = npy_path.with_name(output_stem + "_timeseries.png")
    fig.savefig(timeseries_path, dpi=200)
    plt.close(fig)

    nperseg = min(args.nperseg, len(voltage))
    if nperseg < 256:
        raise ValueError("Need at least 256 samples for the Welch estimate")
    noverlap = nperseg // 2
    frequency, voltage_psd, segments = streaming_welch(
        voltage, sample_rate, nperseg, noverlap, args.batch_segments
    )
    voltage_asd = np.sqrt(np.maximum(voltage_psd, 0.0))
    positive = frequency > 0

    colors = ["#C44E52", "#4C78A8", "#55A868", "#8172B2"]
    fig, ax = plt.subplots(figsize=(11, 6), constrained_layout=True)
    rin_curves = []
    for index, dc_voltage in enumerate(dc_voltages):
        rin_asd = voltage_asd / dc_voltage
        rin_curves.append(rin_asd)
        qualifier = "primary" if index == 0 and len(dc_voltages) > 1 else None
        label = f"{dc_voltage:g} V DC" + (f" ({qualifier})" if qualifier else "")
        ax.loglog(frequency[positive], rin_asd[positive], color=colors[index % len(colors)],
                  linewidth=0.75, label=label)
    ax.set(
        xlabel="Frequency (Hz)",
        ylabel=r"RIN ASD (1/$\sqrt{\mathrm{Hz}}$)",
        title=f"{npy_path.stem}: relative intensity noise",
        xlim=(frequency[positive][0], sample_rate / 2),
    )
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(loc="best")
    ax.text(
        0.015,
        0.025,
        f"Welch: Hann, {nperseg:,} samples, 50% overlap, {segments:,} windows\n"
        f"$f_s$ = {sample_rate/1e6:g} MSa/s; raw voltage ASD / stated DC voltage",
        transform=ax.transAxes,
        fontsize=9,
        va="bottom",
        bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "0.75"},
    )
    asd_path = npy_path.with_name(output_stem + "_rin_asd.png")
    fig.savefig(asd_path, dpi=200)
    plt.close(fig)

    spectrum_path = npy_path.with_name(output_stem + "_rin_asd.npz")
    results = {
        "frequency_Hz": frequency[positive],
        "voltage_asd_V_per_sqrt_Hz": voltage_asd[positive],
        "sample_rate_Hz": sample_rate,
        "normalization_voltages_V": np.asarray(dc_voltages),
        "welch_nperseg": nperseg,
        "welch_noverlap": noverlap,
        "welch_segment_count": segments,
        "analyzed_sample_count": sample_count,
        "analyzed_fraction": sample_count / len(data),
    }
    for index, rin_asd in enumerate(rin_curves):
        results[f"rin_asd_{index}_per_sqrt_Hz"] = rin_asd[positive]
    np.savez(spectrum_path, **results)

    duration = (sample_count - 1) / sample_rate
    print(f"Duration: {duration:.6f} s; fs: {sample_rate:g} Hz", flush=True)
    print(f"RIN normalizations: {', '.join(f'{value:g} V' for value in dc_voltages)}", flush=True)
    print(f"Welch: {nperseg:,} samples/window, 50% overlap, {segments:,} windows", flush=True)
    print(f"Saved: {timeseries_path}", flush=True)
    print(f"Saved: {asd_path}", flush=True)
    print(f"Saved: {spectrum_path}", flush=True)


if __name__ == "__main__":
    main()
