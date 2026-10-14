"""Plot two raw phasemeter recordings against their acquisition clock times."""
from pathlib import Path
from datetime import datetime
import argparse
import re

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np


def load_recording(path):
    path = Path(path).resolve()
    header = path.with_suffix(".txt").read_text(encoding="utf-8")
    match = re.search(
        r"Acquired\s+(\d{4}-\d{2}-\d{2})\s+T\s+(\d{2}:\d{2}:\d{2})\s+([+-]\d{4})",
        header,
    )
    if not match:
        raise ValueError(f"No acquisition timestamp found in {path.with_suffix('.txt')}")
    acquired = datetime.strptime(" ".join(match.groups()), "%Y-%m-%d %H:%M:%S %z")
    data = np.load(path, allow_pickle=False)
    seconds = np.asarray(data["Time (s)"])
    if not np.all(np.isfinite(seconds)) or not np.all(np.diff(seconds) > 0):
        raise ValueError(f"Invalid time data in {path}")
    clock_time = mdates.date2num(acquired) + seconds / 86400.0
    residuals = {}
    for channel in ("A", "B"):
        frequency = np.asarray(data[f"Input {channel} Frequency (Hz)"])
        set_frequency = np.asarray(data[f"Input {channel} Set Frequency (Hz)"])
        residuals[channel] = frequency - set_frequency
    return acquired, clock_time, residuals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carrier_usb", type=Path,
                        help="Recording whose inputs A/B are carrier/USB")
    parser.add_argument("lsb_usb", type=Path,
                        help="Recording whose inputs A/B are LSB/USB")
    parser.add_argument("--zoom-seconds", type=float, default=180,
                        help="Duration shown in the right column (default: 180 s)")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    acquired_1, time_1, pm1 = load_recording(args.carrier_usb)
    acquired_2, time_2, pm2 = load_recording(args.lsb_usb)
    if acquired_1.utcoffset() != acquired_2.utcoffset():
        raise ValueError("Recordings use different UTC offsets")
    timezone = acquired_1.tzinfo
    end = max(time_1[-1], time_2[-1])
    start = min(time_1[0], time_2[0])
    zoom_start = end - args.zoom_seconds / 86400

    rows = [
        ("Carrier — PM1 input A", [(time_1, pm1["A"], "PM1", "black")]),
        ("LSB — PM2 input A", [(time_2, pm2["A"], "PM2", "#295f24")]),
        ("USB — input B on both phasemeters", [
            (time_1, pm1["B"], "PM1 USB", "#821770"),
            (time_2, pm2["B"], "PM2 USB", "tab:blue"),
        ]),
    ]
    fig, axes = plt.subplots(3, 2, figsize=(14, 9), sharex="col")
    for row, (title, traces) in enumerate(rows):
        for column in range(2):
            ax = axes[row, column]
            for clock_time, residual, label, color in traces:
                ax.plot(clock_time, residual, "-", linewidth=.45,
                        color=color, label=label, rasterized=True)
            ax.set_title(title, fontsize=10)
            ax.set_ylabel("Frequency − setpoint (Hz)")
            ax.grid(True, alpha=.25)
            if len(traces) > 1:
                ax.legend(fontsize=8)
        axes[row, 0].set_xlim(start, end)
        axes[row, 1].set_xlim(zoom_start, end)
    formatter = mdates.DateFormatter("%H:%M:%S", tz=timezone)
    for ax in axes.flat:
        ax.xaxis.set_major_formatter(formatter)
        ax.tick_params(axis="x", rotation=25)
    axes[0, 0].set_title(rows[0][0] + " — full recording", fontsize=10)
    axes[0, 1].set_title(rows[0][0] + f" — final {args.zoom_seconds:g} s", fontsize=10)
    for ax in axes[-1]:
        ax.set_xlabel(f"Local time ({acquired_1.strftime('%z')})")
    fig.suptitle(
        "Raw two-phasemeter frequency time series\n"
        f"PM1 acquired {acquired_1.isoformat()}; PM2 acquired {acquired_2.isoformat()}; "
        "no synchronization, detrending, or filtering",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, .94))
    output = args.output or args.carrier_usb.with_name(
        args.carrier_usb.stem + "_two_pm_absolute_timeseries.png")
    output = output.resolve()
    fig.savefig(output, dpi=200)
    plt.close(fig)
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
