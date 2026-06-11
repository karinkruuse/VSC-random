"""
Moku:Pro Phasemeter data plotter
  Figure 1 – Frequency ASD: Ch1, Ch3, Ch4, Ch1-Ch3
  Figure 2 – Phase ASD:     Ch1, Ch3, Ch4, Ch1-Ch3
"""

import sys
import pathlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch, detrend

# ── 1. Locate the data file ────────────────────────────────────────────────
if len(sys.argv) > 1:
    npy_path = pathlib.Path(sys.argv[1])
else:
    default = "Transponder_lock_8_point_three_sec_delay_20260512_173827.npy"
    npy_path = pathlib.Path(default)

if not npy_path.exists():
    sys.exit(f"[ERROR] Cannot find data file: {npy_path}\n"
             f"Usage: python plot_phasemeter.py [path/to/data.npy]")

# ── 2. Load ────────────────────────────────────────────────────────────────
raw = np.load(npy_path, allow_pickle=False)
print(f"Raw shape : {raw.shape},  dtype : {raw.dtype}")

if raw.dtype.names:
    print(f"Fields : {raw.dtype.names}")
    data = np.column_stack([raw[name] for name in raw.dtype.names]).astype(float)
else:
    data = raw.astype(float) if raw.ndim > 1 else raw.reshape(1, -1).astype(float)

print(f"Working array : {data.shape[0]} samples x {data.shape[1]} columns")

# ── 3. Unpack columns ─────────────────────────────────────────────────────
t      = data[:, 0]
fs_nom = 1.0 / np.median(np.diff(t))
print(f"Duration : {t[-1] - t[0]:.3f} s   |   Sample rate : {fs_nom:.4f} Hz")

channels = {}
for ch, base in enumerate([1, 6, 11, 16], start=1):
    phase_cyc = data[:, base + 2]
    channels[ch] = {
        "set_freq"  : data[:, base],
        "freq_dev"  : data[:, base + 1] - data[:, base],
        "phase_rad" : detrend(phase_cyc, type="linear") * 2 * np.pi,
    }

# ── 4. Build the four signals to plot ─────────────────────────────────────
subs = 3
diff_freq  = channels[2]["freq_dev"] - channels[subs]["freq_dev"]
diff_phase = detrend(
    channels[2]["phase_rad"] - channels[subs]["phase_rad"], type="linear"
)

# blue (45/255,19/255,180/255)
signals = [
    ("Photodetector 1",      channels[2]["freq_dev"], channels[2]["phase_rad"], (215/225,27/225,47/225)),
    ("Photodetector 2",      channels[3]["freq_dev"], channels[3]["phase_rad"], (41/255,95/255,36/255)),
    ("Mixed signal",      channels[4]["freq_dev"], channels[4]["phase_rad"], (130/255,23/255,112/255)),
    #(f"Ch1 - Ch{subs}",diff_freq,               diff_phase,               "#9467bd"),
]

# ── 5. Welch helper ────────────────────────────────────────────────────────
# nperseg drives the lowest resolvable frequency: f_min = fs / nperseg
# To reach 1e-4 Hz we need nperseg >= fs / 1e-4
nperseg = min(len(t), max(256, int(fs_nom / 1e-4)))
    
def asd(x):
    f, psd = welch(x, fs=fs_nom, nperseg=nperseg, window="hann", detrend="linear")
    return f[1:], np.sqrt(psd[1:])

# ── 6. Figure 1 – Frequency ASD ───────────────────────────────────────────
fig1, ax1 = plt.subplots(figsize=(9, 6))
for lbl, freq_sig, _, c in signals:
    f, a = asd(freq_sig)
    ax1.loglog(f, a, color=c, lw=1.3, label=lbl)

ax1.set_title("Frequency ASD", fontsize=13, fontweight="bold")
ax1.set_xlabel("Fourier frequency (Hz)")
ax1.set_ylabel("Freq. ASD  (Hz / sqrt(Hz))")
ax1.legend(fontsize=10)
ax1.grid(True, which="both", alpha=0.3)
ax1.set_xlim(1e-4, fs_nom / 2)
fig1.tight_layout()
fig1.savefig("phasemeter_freq_asd.pdf", dpi=150, bbox_inches="tight")
print("Saved: phasemeter_freq_asd.pdf")

# ── 7. Figure 2 – Phase ASD ───────────────────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(9, 6))
for lbl, _, phase_sig, c in signals:
    f, a = asd(phase_sig)
    ax2.loglog(f, a, color=c, lw=1.3, label=lbl)

ax2.set_title("Phase ASD  [detrended]", fontsize=13, fontweight="bold")
ax2.set_xlabel("Fourier frequency (Hz)")
ax2.set_ylabel("Phase ASD  (rad / sqrt(Hz))")
ax2.legend(fontsize=10)
ax2.grid(True, which="both", alpha=0.3)
ax2.set_xlim(1e-4, fs_nom / 2)
fig2.tight_layout()
fig2.savefig("phasemeter_phase_asd.pdf", dpi=150, bbox_inches="tight")
print("Saved: phasemeter_phase_asd.pdf")

plt.show()