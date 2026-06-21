"""
Publication-quality Frequency ASD plot  –  CSV input version
Same data pipeline as plot1.py, but reads a .csv file instead of .npy.

Expected CSV layout (same column order as the .npy file):
  col 0       : time
  cols 1–5    : channel 1  (col 2 and col 3 used → freq_dev, phase_rad)
  cols 6–10   : channel 2  (col 7 and col 8)
  cols 11–15  : channel 3  (col 12 and col 13)
  cols 16–20  : channel 4  (col 17 and col 18)

The first row may optionally be a header line (detected automatically).
Delimiter is auto-detected (comma or whitespace).
"""

import sys
import pathlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.signal import welch, detrend

# ── matplotlib style ───────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family"        : "sans-serif",
    "font.sans-serif"    : ["Helvetica", "Arial", "DejaVu Sans"],
    "mathtext.fontset"   : "custom",
    "mathtext.rm"        : "Helvetica",
    "mathtext.it"        : "Helvetica:italic",
    "mathtext.bf"        : "Helvetica:bold",
    "axes.spines.top"    : True,
    "axes.spines.right"  : True,
    "axes.linewidth"     : 0.8,
    "xtick.direction"    : "in",
    "ytick.direction"    : "in",
    "xtick.major.size"   : 4,
    "ytick.major.size"   : 4,
    "xtick.minor.size"   : 2.5,
    "ytick.minor.size"   : 2.5,
    "xtick.major.width"  : 0.8,
    "ytick.major.width"  : 0.8,
    "xtick.labelsize"    : 10,
    "ytick.labelsize"    : 10,
    "axes.labelsize"     : 11,
    "legend.fontsize"    : 9,
    "legend.framealpha"  : 0.92,
    "legend.edgecolor"   : "#cccccc",
    "legend.handlelength": 2.0,
    "figure.dpi"         : 150,
})

# ── 1. Data file ───────────────────────────────────────────────────────────
if len(sys.argv) > 1:
    csv_path = pathlib.Path(sys.argv[1])
else:
    csv_path = pathlib.Path(
        "Transponder_lock_8_point_three_sec_delay_20260512_173827.csv"
    )

if not csv_path.exists():
    sys.exit(f"[ERROR] Cannot find {csv_path}")

# ── 2. Load ────────────────────────────────────────────────────────────────
# Peek at first line to decide whether there is a header
with open(csv_path, "r") as fh:
    first_line = fh.readline().strip()

# Detect delimiter: comma-separated or whitespace-separated
delimiter = "," if "," in first_line else None  # None → numpy treats any whitespace

# Detect header: if the first field cannot be parsed as a float it's a header
try:
    float(first_line.split("," if delimiter else None)[0])
    skip_header = 0
except ValueError:
    skip_header = 1

data = np.loadtxt(csv_path, delimiter=delimiter, skiprows=skip_header, dtype=float)

if data.ndim == 1:
    data = data.reshape(1, -1)

t      = data[:, 0]
fs_nom = 1.0 / np.median(np.diff(t))

channels = {}
for ch, base in enumerate([1, 6, 11, 16], start=1):
    channels[ch] = {
        "freq_dev"  : data[:, base + 1] - data[:, base],
        "phase_rad" : detrend(data[:, base + 2], type="linear") * 2 * np.pi,
    }

# ── 3. Signals ─────────────────────────────────────────────────────────────
signals = [
    ("Photodetector 1",                  channels[2]["freq_dev"],
     (215/255,  27/255,  47/255), 1.4, 1.0),
    ("Photodetector 2",                  channels[3]["freq_dev"],
     ( 41/255,  95/255,  36/255), 0.9, 1.0),
    ("Mixed signal",                     channels[4]["freq_dev"],
     (130/255,  23/255, 112/255), 1.4, 1.0),
    ("Photodetector 1 - Photodetector 2",
     channels[2]["freq_dev"] - channels[3]["freq_dev"],
     ( 70/255,  70/255,  70/255), 0.7, 0.7  ),
]

# ── 4. Welch ───────────────────────────────────────────────────────────────
nperseg = min(len(t), max(256, int(fs_nom / 1e-4)))

def asd(x):
    f, psd = welch(x, fs=fs_nom, nperseg=nperseg, window="hann", detrend="linear")
    return f[1:], np.sqrt(psd[1:])

# ── 5. Figure ──────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4.8))

for lbl, sig, c, lw, al in signals:
    f, a = asd(sig)
    ax.loglog(f, a, color=c, lw=lw, label=lbl, alpha=al)

ax.set_xlim(1e-4, fs_nom / 2)
ax.set_xlabel("Fourier frequency (Hz)")
ax.set_ylabel(r"Frequency ASD $\left(\mathrm{Hz}\,/\,\sqrt{\mathrm{Hz}}\right)$")

ax.xaxis.set_minor_locator(ticker.LogLocator(subs="all", numticks=10))
ax.yaxis.set_minor_locator(ticker.LogLocator(subs="all", numticks=10))
ax.tick_params(which="minor", length=2.5, width=0.6)

ax.grid(True,  which="major", color="#e0e0e0", linewidth=0.6, linestyle="--")
ax.grid(False, which="minor")

ax.legend(loc="upper right", frameon=True, fancybox=False)

fig.subplots_adjust(left=0.13, bottom=0.13, right=0.97, top=0.95)

out = "phasemeter_freq_asd_pub.png"
fig.savefig(out, dpi=300, bbox_inches="tight")
print(f"Saved: {out}")
plt.show()