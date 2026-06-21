"""
Publication-quality Frequency ASD plot
Same data pipeline as first_analysis.py, polished figure output.
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
    npy_path = pathlib.Path(sys.argv[1])
else:
    npy_path = pathlib.Path(
        "Transponder_lock_8_point_three_sec_delay_20260512_173827.npy"
    )

if not npy_path.exists():
    sys.exit(f"[ERROR] Cannot find {npy_path}")

# ── 2. Load ────────────────────────────────────────────────────────────────
raw = np.load(npy_path, allow_pickle=False)
if raw.dtype.names:
    data = np.column_stack([raw[n] for n in raw.dtype.names]).astype(float)
else:
    data = raw.astype(float) if raw.ndim > 1 else raw.reshape(1, -1).astype(float)

t      = data[:, 0]
fs_nom = 1.0 / np.median(np.diff(t))

channels = {}
for ch, base in enumerate([1, 6, 11, 16], start=1):
    channels[ch] = {
        "freq_dev"  : data[:, base + 1] - data[:, base],
        "phase_rad" : detrend(data[:, base + 2], type="linear") * 2 * np.pi,
    }

# ── 3. Signals (same as first_analysis.py) ────────────────────────────────
signals = [
    ("Photodetector 1", channels[2]["freq_dev"], (215/255, 27/255, 47/255),  1.4),
    ("Photodetector 2", channels[3]["freq_dev"], (41/255,  95/255, 36/255),  0.9),   # thinner – sits on top of red
    ("Mixed signal",    channels[4]["freq_dev"], (130/255, 23/255, 112/255), 1.4),
    ("Photodetector 1 - Photodetector 2",    channels[2]["freq_dev"]-channels[2]["freq_dev"], (70/255, 70/255, 170/255), 1),
    
]

# ── 4. Welch ───────────────────────────────────────────────────────────────
nperseg = min(len(t), max(256, int(fs_nom / 1e-4)))

def asd(x):
    f, psd = welch(x, fs=fs_nom, nperseg=nperseg, window="hann", detrend="linear")
    return f[1:], np.sqrt(psd[1:])

# ── 5. Figure ──────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4.8))

for lbl, sig, c, lw in signals:
    f, a = asd(sig)
    ax.loglog(f, a, color=c, lw=lw, label=lbl)

# Axis limits & labels
ax.set_xlim(1e-4, fs_nom / 2)
ax.set_xlabel("Fourier frequency (Hz)")
ax.set_ylabel(r"Frequency ASD $\left(\mathrm{Hz}\,/\,\sqrt{\mathrm{Hz}}\right)$")

# Minor ticks on log axes
ax.xaxis.set_minor_locator(ticker.LogLocator(subs="all", numticks=10))
ax.yaxis.set_minor_locator(ticker.LogLocator(subs="all", numticks=10))
ax.tick_params(which="minor", length=2.5, width=0.6)

# Grid: subtle major only
ax.grid(True, which="major", color="#e0e0e0", linewidth=0.6, linestyle="--")
ax.grid(False, which="minor")

# Legend inside, upper right
ax.legend(loc="upper right", frameon=True, fancybox=False)

# Tight but with a little breathing room
fig.subplots_adjust(left=0.13, bottom=0.13, right=0.97, top=0.95)

out = "phasemeter_freq_asd_pub.png"
fig.savefig(out, dpi=300, bbox_inches="tight")
print(f"Saved: {out}")
plt.show()