"""
Moku:Pro Phasemeter – multi-channel plotter
============================================
Reads three .npy data files (one per Moku device) together with their
matching .txt metadata files, then plots detrended phase and mean-subtracted
frequency time-series for all 6 channels (2 inputs × 3 devices).

Processing applied:
  • Frequency  → subtract channel mean  (shows fluctuations only)
  • Phase      → remove linear trend via least-squares fit
                 The fitted slope (cyc/s = Hz) is compared to:
                   - the measured mean frequency
                   - the set frequency from the metadata column

Expected column layout of each .npy array (11 columns):
  0  Time (s)
  1  Input A Set Frequency (Hz)
  2  Input A Frequency (Hz)
  3  Input A Phase (cyc)
  4  Input A I (V)
  5  Input A Q (V)
  6  Input B Set Frequency (Hz)
  7  Input B Frequency (Hz)
  8  Input B Phase (cyc)
  9  Input B I (V)
  10 Input B Q (V)
"""

import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# USER SETTINGS
# ──────────────────────────────────────────────────────────────────────────────

# Folder that contains both the .txt and .npy files
DATA_DIR = Path("data\\")

# Base filenames (without extension) for the three phasemeter files
FILES = [
    "Carrier_20260526_134721",
    "USB_20260526_134721",
    "LSB_20260526_134722",
    "CLK_20260526_134723",
]

# Crop: remove this many seconds from the START of each channel's data
CROP_START_S = 0.0   # e.g. 5.0  -> skip the first 5 seconds

# Crop: remove this many seconds from the END of each channel's data
CROP_END_S   = 0.0   # e.g. 2.0  -> skip the last 2 seconds

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def parse_acquisition_time(txt_path: Path) -> datetime:
    """Extract the acquisition datetime from the Moku metadata header."""
    pattern = re.compile(
        r"#\s*%\s*Acquired\s+(\d{4}-\d{2}-\d{2})\s+T\s+(\d{2}:\d{2}:\d{2})\s+([+-]\d{4})"
    )
    with open(txt_path, encoding="utf-8") as fh:
        for line in fh:
            m = pattern.search(line)
            if m:
                date_str, time_str, tz_str = m.groups()
                tz_colon = tz_str[:3] + ":" + tz_str[3:]
                return datetime.fromisoformat(f"{date_str}T{time_str}{tz_colon}")
    raise ValueError(f"Could not find 'Acquired' timestamp in {txt_path}")


def parse_channel_labels(txt_path: Path):
    """Return (label_A, label_B) from the '# % A - ..., B - ...' header line."""
    pattern = re.compile(r"#\s*%\s*A\s*-\s*(.+?),\s*B\s*-\s*(.+)", re.IGNORECASE)
    with open(txt_path, encoding="utf-8") as fh:
        for line in fh:
            m = pattern.search(line)
            if m:
                return m.group(1).strip(), m.group(2).strip()
    return "Input A", "Input B"


def load_npy(npy_path: Path) -> np.ndarray:
    """Load .npy, handling plain-2D, structured, and 1-D-of-tuples formats."""
    raw = np.load(npy_path, allow_pickle=True)
    if raw.dtype.names:
        return np.column_stack([raw[n] for n in raw.dtype.names]).astype(float)
    if raw.ndim == 1:
        return np.array([list(r) for r in raw], dtype=float)
    return raw.astype(float)


def load_channel(npy_path: Path, channel: str, t0: datetime,
                 crop_start: float, crop_end: float) -> dict:
    """
    Load, crop, and process one channel from the .npy file.

    Returns a dict with:
      t_rel         - relative time in hours (post-crop)
      t_abs         - list of absolute datetimes (post-crop)
      freq_fluct    - frequency fluctuations after mean subtraction (Hz)
      freq_mean     - mean frequency before subtraction (Hz)
      phase_det     - linearly detrended phase (cyc)
      slope_hz      - linear trend slope in Hz (= cyc/s)
      set_freq      - set frequency from metadata column (Hz)
      n_crop_start  - samples removed at start
      n_crop_end    - samples removed at end
      dt_crop_start - seconds cropped at start
      dt_crop_end   - seconds cropped at end
    """
    data  = load_npy(npy_path)
    t_raw = data[:, 0]

    # ── Crop ─────────────────────────────────────────────────────────────────
    mask = np.ones(len(t_raw), dtype=bool)
    if crop_start > 0:
        mask &= t_raw >= t_raw[0] + crop_start
    if crop_end > 0:
        mask &= t_raw <= t_raw[-1] - crop_end

    n_cs = int(np.sum(t_raw < t_raw[0] + crop_start)) if crop_start > 0 else 0
    n_ce = int(np.sum(t_raw > t_raw[-1] - crop_end))  if crop_end   > 0 else 0

    data  = data[mask]
    t_raw = data[:, 0]

    ch = channel.upper()
    if ch == "A":
        set_freq = float(data[0, 1])
        freq     = data[:, 2]
        phase    = data[:, 3]
    else:
        set_freq = float(data[0, 6])
        freq     = data[:, 7]
        phase    = data[:, 8]

    t_rel = (t_raw - t_raw[0]) / 3600.0
    t_abs = [t0 + timedelta(seconds=float(s)) for s in t_raw]

    # ── Frequency: subtract mean ──────────────────────────────────────────────
    freq_mean  = float(np.mean(freq))
    freq_fluct = freq - freq_mean

    # ── Phase: linear detrend ─────────────────────────────────────────────────
    t_s       = t_raw - t_raw[0]              # seconds from first kept sample
    coeffs    = np.polyfit(t_s, phase, 1)     # slope in cyc/s = Hz
    slope_hz  = float(coeffs[0])
    phase_det = phase - np.polyval(coeffs, t_s)

    return dict(
        t_rel=t_rel, t_abs=t_abs,
        freq_fluct=freq_fluct, freq_mean=freq_mean,
        phase_det=phase_det, slope_hz=slope_hz,
        set_freq=set_freq,
        n_crop_start=n_cs, n_crop_end=n_ce,
        dt_crop_start=crop_start, dt_crop_end=crop_end,
    )


def make_twin_xaxis(ax, t_abs):
    """Add a top x-axis showing absolute HH:MM:SS at the same tick positions."""
    ax_top = ax.twiny()
    ax_top.set_xlim(ax.get_xlim())
    ticks_rel = ax.get_xticks()
    t0_abs    = t_abs[0]
    tick_dts  = [t0_abs + timedelta(hours=float(h)) for h in ticks_rel]
    ax_top.set_xticks(ticks_rel)
    ax_top.set_xticklabels(
        [dt.strftime("%H:%M:%S") for dt in tick_dts],
        fontsize=7, rotation=30, ha="left",
    )
    ax_top.set_xlabel("Local time", fontsize=8, labelpad=4)
    return ax_top


def add_crop_annotation(ax, d: dict):
    """Write a small note in the lower-left corner about how much was cropped."""
    parts = []
    if d["n_crop_start"] > 0:
        parts.append(
            f">> cropped {d['dt_crop_start']:.1f} s "
            f"({d['n_crop_start']} samples) from start"
        )
    if d["n_crop_end"] > 0:
        parts.append(
            f"<< cropped {d['dt_crop_end']:.1f} s "
            f"({d['n_crop_end']} samples) from end"
        )
    if not parts:
        return   # nothing to say
    note = "\n".join(parts)
    ax.text(
        0.01, 0.03, note,
        transform=ax.transAxes,
        fontsize=7, color="saddlebrown",
        va="bottom", ha="left",
        bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="peru", alpha=0.85),
    )


def fmt_freq(hz: float) -> str:
    """Format a frequency value with appropriate SI prefix."""
    if abs(hz) >= 1e6:
        return f"{hz/1e6:.6f} MHz"
    if abs(hz) >= 1e3:
        return f"{hz/1e3:.6f} kHz"
    return f"{hz:.6f} Hz"


def add_slope_box(ax, d: dict):
    """
    Annotation box on the phase plot comparing the linear-trend slope to the
    measured mean frequency and the set frequency.

    Physically:
      d(phase)/dt  [cyc/s] = instantaneous frequency [Hz]
    So the slope of a linear phase fit equals the mean frequency of the signal.
    Any mismatch between slope and set_freq reveals a frequency offset.
    """
    sl   = d["slope_hz"]
    mean = d["freq_mean"]
    sf   = d["set_freq"]

    diff_mean = sl - mean   # should be ~0 (self-consistency check)
    diff_set  = sl - sf     # frequency offset from set point

    lines = [
        "--- phase trend vs frequency ---",
        f"Slope  (d_phi/dt) : {fmt_freq(sl)}",
        f"Freq mean         : {fmt_freq(mean)}",
        f"Set frequency     : {fmt_freq(sf)}",
        f"Slope - freq mean : {fmt_freq(diff_mean)}",
        f"Slope - set freq  : {fmt_freq(diff_set)}",
    ]
    note = "\n".join(lines)
    ax.text(
        0.99, 0.97, note,
        transform=ax.transAxes,
        fontsize=7, color="navy",
        va="top", ha="right", family="monospace",
        bbox=dict(boxstyle="round,pad=0.4", fc="aliceblue", ec="steelblue", alpha=0.88),
    )


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    # ── Collect all channel data ──────────────────────────────────────────────
    channels = []

    for base in FILES:
        txt_path = DATA_DIR / f"{base}.txt"
        npy_path = DATA_DIR / f"{base}.npy"

        if not txt_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {txt_path}")
        if not npy_path.exists():
            raise FileNotFoundError(f"Data file not found: {npy_path}")

        t0 = parse_acquisition_time(txt_path)
        label_a, label_b = parse_channel_labels(txt_path)

        for ch, label in [("A", label_a), ("B", label_b)]:
            d = load_channel(npy_path, ch, t0, CROP_START_S, CROP_END_S)
            d["label"] = label
            d["file"]  = base
            d["ch"]    = ch
            channels.append(d)

    # ── Figure: n rows × 2 columns  (phase | frequency) ──────────────────────
    n = len(channels)
    fig, axes = plt.subplots(n, 2, figsize=(17, 3.8 * n), constrained_layout=True)
    if n == 1:
        axes = [axes]

    fig.suptitle(
        "Moku:Pro Phasemeter – all channels\n"
        "(Phase: linearly detrended  |  Frequency: mean subtracted)",
        fontsize=13, fontweight="bold",
    )

    for row, d in enumerate(channels):
        label = d["label"]
        src   = f"{d['file']}  .  Input {d['ch']}"

        # ── Phase (left) ──────────────────────────────────────────────────────
        ax_ph = axes[row][0]
        ax_ph.plot(d["t_rel"], d["phase_det"], lw=0.8, color="steelblue")
        ax_ph.axhline(0, color="gray", lw=0.5, ls="--")
        ax_ph.set_ylabel("Phase residual (cyc)", fontsize=9)
        ax_ph.set_xlabel("Elapsed time (h)", fontsize=9)
        ax_ph.set_title(f"{label}  -  Phase (detrended)", fontsize=9) # \n({src})
        ax_ph.grid(True, alpha=0.3)
        make_twin_xaxis(ax_ph, d["t_abs"])
        add_crop_annotation(ax_ph, d)
        add_slope_box(ax_ph, d)

        # ── Frequency (right) ─────────────────────────────────────────────────
        ax_fr = axes[row][1]
        ax_fr.plot(d["t_rel"], d["freq_fluct"], lw=0.8, color="darkorange")
        ax_fr.axhline(0, color="gray", lw=0.5, ls="--")
        ax_fr.set_ylabel("Frequency fluctuation (Hz)", fontsize=9)
        ax_fr.set_xlabel("Elapsed time (h)", fontsize=9)
        ax_fr.set_title(
            f"{label}  -  Frequency fluctuations\n"
            f"(mean = {fmt_freq(d['freq_mean'])})", #   .  ({src})
            fontsize=9,
        )
        ax_fr.grid(True, alpha=0.3)
        make_twin_xaxis(ax_fr, d["t_abs"])
        add_crop_annotation(ax_fr, d)

    out_path = DATA_DIR / "phasemeter_all_channels.pdf"
    fig.savefig(out_path, dpi=150)
    print(f"Saved -> {out_path}")
    #plt.show()


if __name__ == "__main__":
    main()