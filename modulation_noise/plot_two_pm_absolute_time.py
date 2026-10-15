"""Plot two raw phasemeter recordings against their acquisition clock times."""
from pathlib import Path
from datetime import datetime
import argparse
import re

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import detrend


PHASE_COUNTER_PERIOD_CYCLES = 2**22


def recording_metadata(path):
    path = Path(path).resolve()
    header = path.with_suffix(".txt").read_text(encoding="utf-8")
    match = re.search(
        r"Acquired\s+(\d{4}-\d{2}-\d{2})\s+T\s+(\d{2}:\d{2}:\d{2})\s+([+-]\d{4})",
        header,
    )
    if not match:
        raise ValueError(f"No acquisition timestamp found in {path.with_suffix('.txt')}")
    acquired = datetime.strptime(" ".join(match.groups()), "%Y-%m-%d %H:%M:%S %z")
    role_match = re.search(
        r"^#\s*%\s*(carrier|LSB)\s*,\s*USB(?:\s*,.*)?$", header,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if not role_match:
        raise ValueError(f"No carrier/USB or LSB/USB role label found in {path.with_suffix('.txt')}")
    role = "carrier" if role_match.group(1).lower() == "carrier" else "lsb"
    return acquired, role


def discover_pairs(search_dir, maximum_start_difference=10):
    """Find raw carrier/USB and LSB/USB files acquired together."""
    search_dir = Path(search_dir).resolve()
    if not search_dir.is_dir():
        raise ValueError(f"Search directory does not exist: {search_dir}")
    candidates = []
    for path in search_dir.rglob("*.npy"):
        if path.stem.endswith("_synced") or not path.with_suffix(".txt").is_file():
            continue
        try:
            acquired, role = recording_metadata(path)
        except (OSError, UnicodeError, ValueError):
            continue
        candidates.append((path.resolve(), acquired, role))

    pairs = []
    parents = sorted({path.parent for path, _, _ in candidates})
    for parent in parents:
        carriers = sorted((item for item in candidates
                           if item[0].parent == parent and item[2] == "carrier"),
                          key=lambda item: item[1])
        remaining_lsb = [item for item in candidates
                         if item[0].parent == parent and item[2] == "lsb"]
        for carrier in carriers:
            compatible = [item for item in remaining_lsb
                          if item[1].utcoffset() == carrier[1].utcoffset()]
            if not compatible:
                continue
            lower = min(compatible, key=lambda item: abs(item[1] - carrier[1]))
            if abs((lower[1] - carrier[1]).total_seconds()) > maximum_start_difference:
                continue
            pairs.append((carrier[0], lower[0], min(carrier[1], lower[1])))
            remaining_lsb.remove(lower)
    return sorted(pairs, key=lambda pair: pair[2], reverse=True)


def choose_pair(search_dir):
    pairs = discover_pairs(search_dir)
    if not pairs:
        raise ValueError(
            f"No usable two-phasemeter pairs found under {Path(search_dir).resolve()}\n"
            "Each raw NPY needs a same-name TXT containing an acquisition time and "
            "a carrier,USB or LSB,USB role line."
        )
    root = Path(search_dir).resolve()
    print(f"Two-phasemeter measurements under {root}:")
    for number, (carrier, lower, acquired) in enumerate(pairs, start=1):
        location = carrier.parent.relative_to(root)
        print(f"  [{number}] {acquired.strftime('%Y-%m-%d %H:%M:%S %z')}  {location}")
        print(f"      carrier/USB: {carrier.name}")
        print(f"      LSB/USB:     {lower.name}")
    while True:
        try:
            choice = input(f"Select measurement [1-{len(pairs)}]: ").strip()
        except EOFError as error:
            raise SystemExit("No selection received") from error
        try:
            selected = int(choice)
        except ValueError:
            selected = 0
        if 1 <= selected <= len(pairs):
            return pairs[selected - 1][:2]
        print(f"Enter a number from 1 to {len(pairs)}.")


def unwrap_phase_counter(phase, frequency_residual, seconds):
    """Remove the Moku phase-counter rollover before detrending.

    Samples whose circular phase average is corrupted while crossing the counter
    boundary are advanced using the simultaneously measured frequency residual.
    """
    dt = np.diff(seconds)
    expected_step = (frequency_residual[:-1] + frequency_residual[1:]) * dt / 2
    measured_step = np.diff(phase)
    measured_step -= np.rint(
        (measured_step - expected_step) / PHASE_COUNTER_PERIOD_CYCLES
    ) * PHASE_COUNTER_PERIOD_CYCLES
    corrupt = np.abs(measured_step - expected_step) > PHASE_COUNTER_PERIOD_CYCLES / 8
    measured_step[corrupt] = expected_step[corrupt]
    unwrapped = np.empty_like(phase, dtype=float)
    unwrapped[0] = phase[0]
    unwrapped[1:] = phase[0] + np.cumsum(measured_step)
    return unwrapped


def load_recording(path):
    path = Path(path).resolve()
    acquired, _ = recording_metadata(path)
    data = np.load(path, allow_pickle=False)
    seconds = np.asarray(data["Time (s)"])
    if not np.all(np.isfinite(seconds)) or not np.all(np.diff(seconds) > 0):
        raise ValueError(f"Invalid time data in {path}")
    clock_time = mdates.date2num(acquired) + seconds / 86400.0
    frequency_residuals = {}
    detrended_phases = {}
    for channel in ("A", "B"):
        frequency = np.asarray(data[f"Input {channel} Frequency (Hz)"])
        set_frequency = np.asarray(data[f"Input {channel} Set Frequency (Hz)"])
        phase = np.asarray(data[f"Input {channel} Phase (cyc)"])
        if not all(np.all(np.isfinite(values))
                   for values in (frequency, set_frequency, phase)):
            raise ValueError(f"Non-finite input-{channel} data in {path}")
        frequency_residuals[channel] = frequency - set_frequency
        unwrapped_phase = unwrap_phase_counter(
            phase, frequency_residuals[channel], seconds)
        detrended_phases[channel] = detrend(unwrapped_phase, type="linear")
    return acquired, clock_time, frequency_residuals, detrended_phases


def save_timeseries(rows, acquired_1, acquired_2, zoom_seconds, ylabel,
                    title, processing_note, output):
    all_times = [clock_time for _, traces in rows
                 for clock_time, _, _, _ in traces]
    start = min(clock_time[0] for clock_time in all_times)
    end = max(clock_time[-1] for clock_time in all_times)
    zoom_start = max(start, end - zoom_seconds / 86400)
    timezone = acquired_1.tzinfo

    fig, axes = plt.subplots(3, 2, figsize=(14, 9), sharex="col")
    for row, (row_title, traces) in enumerate(rows):
        for column in range(2):
            ax = axes[row, column]
            for clock_time, values, label, color in traces:
                if column == 1:
                    visible = clock_time >= zoom_start
                    plot_time, plot_values = clock_time[visible], values[visible]
                else:
                    plot_time, plot_values = clock_time, values
                ax.plot(plot_time, plot_values, "-", linewidth=.45,
                        color=color, label=label, rasterized=True)
            ax.set_title(row_title, fontsize=10)
            ax.set_ylabel(ylabel)
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
    axes[0, 1].set_title(rows[0][0] + f" — final {zoom_seconds:g} s", fontsize=10)
    for ax in axes[-1]:
        ax.set_xlabel(f"Local time ({acquired_1.strftime('%z')})")
    fig.suptitle(
        f"{title}\n"
        f"PM1 acquired {acquired_1.isoformat()}; PM2 acquired {acquired_2.isoformat()}\n"
        f"{processing_note}",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, .91))
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=200)
    plt.close(fig)
    print(f"Saved: {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carrier_usb", nargs="?", type=Path,
                        help="Recording whose inputs A/B are carrier/USB")
    parser.add_argument("lsb_usb", nargs="?", type=Path,
                        help="Recording whose inputs A/B are LSB/USB")
    parser.add_argument(
        "--search-dir", type=Path,
        default=Path(__file__).resolve().parent / "data",
        help="Directory searched recursively in interactive mode (default: modulation_noise/data)",
    )
    parser.add_argument("--zoom-seconds", type=float, default=180,
                        help="Duration shown in the right column (default: 180 s)")
    parser.add_argument("--output", type=Path, help="Frequency-plot output path")
    parser.add_argument("--phase-output", type=Path, help="Phase-plot output path")
    args = parser.parse_args()

    if (args.carrier_usb is None) != (args.lsb_usb is None):
        parser.error("Supply both NPY files, or neither to use the interactive menu")
    if args.carrier_usb is None:
        args.carrier_usb, args.lsb_usb = choose_pair(args.search_dir)

    acquired_1, time_1, frequency_1, phase_1 = load_recording(args.carrier_usb)
    acquired_2, time_2, frequency_2, phase_2 = load_recording(args.lsb_usb)
    if acquired_1.utcoffset() != acquired_2.utcoffset():
        raise ValueError("Recordings use different UTC offsets")

    def rows(values_1, values_2):
        return [
        ("Carrier — PM1 input A", [(time_1, values_1["A"], "PM1", "black")]),
        ("LSB — PM2 input A", [(time_2, values_2["A"], "PM2", "#295f24")]),
        ("USB — input B on both phasemeters", [
            (time_1, values_1["B"], "PM1 USB", "#821770"),
            (time_2, values_2["B"], "PM2 USB", "tab:blue"),
        ]),
        ]

    frequency_output = args.output or args.carrier_usb.with_name(
        args.carrier_usb.stem + "_two_pm_absolute_timeseries.png")
    if args.phase_output:
        phase_output = args.phase_output
    elif args.output:
        phase_output = args.output.with_name(args.output.stem + "_phase" + args.output.suffix)
    else:
        phase_output = args.carrier_usb.with_name(
            args.carrier_usb.stem + "_two_pm_absolute_phase_timeseries.png")
    save_timeseries(
        rows(frequency_1, frequency_2), acquired_1, acquired_2,
        args.zoom_seconds, "Frequency − setpoint (Hz)",
        "Two-phasemeter frequency time series",
        "no synchronization, detrending, or filtering", frequency_output,
    )
    save_timeseries(
        rows(phase_1, phase_2), acquired_1, acquired_2,
        args.zoom_seconds, "Linearly detrended phase (cycles)",
        "Two-phasemeter phase time series",
        "phase-counter unwrapping and linear detrending per trace; "
        "no synchronization or filtering", phase_output,
    )


if __name__ == "__main__":
    main()
