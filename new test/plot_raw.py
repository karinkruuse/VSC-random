"""
Quick look at the 4 raw Moku phasemeter files, each on its own relative time axis.
Run this first to sanity-check the data before syncing.
"""
import glob
import os
import re

import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def parse_label(txt_path):
    """Pull the '# % input N, <label>' comment out of the header file."""
    with open(txt_path) as f:
        for line in f:
            m = re.match(r"#\s*%\s*input\s*\d*,\s*(.+)", line, re.IGNORECASE)
            if m:
                return m.group(1).strip()
    return os.path.basename(txt_path)


def load_slot(npy_path):
    txt_path = npy_path.replace(".npy", ".txt")
    data = np.load(npy_path)
    label = parse_label(txt_path) if os.path.exists(txt_path) else os.path.basename(npy_path)
    return {
        "path": npy_path,
        "label": label,
        "t": data["Time (s)"],
        "a_phase": data["Input A Phase (cyc)"],
        "b_phase": data["Input B Phase (cyc)"],
    }


def main():
    npy_files = sorted(glob.glob(os.path.join(DATA_DIR, "MokuPhasemeterSlot*Data_*.npy")))
    if not npy_files:
        raise SystemExit(f"No Moku phasemeter .npy files found in {DATA_DIR}")

    slots = [load_slot(p) for p in npy_files]

    fig, (ax_a, ax_b) = plt.subplots(2, 1, sharex=True, figsize=(11, 7))

    for s in slots:
        ax_a.plot(s["t"], s["a_phase"], label=f"{os.path.basename(s['path'])} ({s['label']})")
        ax_b.plot(s["t"], s["b_phase"], label=f"{os.path.basename(s['path'])} ({s['label']})")

    ax_a.set_ylabel("Input A phase (cyc)")
    ax_a.set_title("Channel A (unique signal per slot) -- raw, own relative time axis")
    ax_a.legend(fontsize=8)

    ax_b.set_ylabel("Input B phase (cyc)")
    ax_b.set_xlabel("Time since each file's own acquisition start (s)")
    ax_b.set_title("Channel B (should be the SAME signal in all 4 files) -- raw, own relative time axis")
    ax_b.legend(fontsize=8)

    fig.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), "raw_overview.png")
    fig.savefig(out_path, dpi=150)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
