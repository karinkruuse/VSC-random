"""
Moku:Pro Phasemeter data plotter
Reads a .npy data file (same basename as the .txt header) and produces:
  Figure 1 – Time series: frequency deviation and phase for all four inputs
  Figure 2 – Amplitude Spectral Density (ASD) of phase and frequency
"""

import sys
import pathlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend, welch

# ── 1. Locate the data file ────────────────────────────────────────────────
if len(sys.argv) > 1:
    npy_path = pathlib.Path(sys.argv[1])
else:
    default = "Transponder_lock_8_point_three_sec_delay_20260512_173827.npy"
    npy_path = pathlib.Path(default)

if not npy_path.exists():
    sys.exit(f"[ERROR] Cannot find data file: {npy_path}\n"
             f"Usage: python plot_phasemeter.py [path/to/data.npy]")

# ── 2. Load and normalise to a plain 2-D float array ──────────────────────
raw = np.load(npy_path, allow_pickle=False)
print(f"Raw array shape : {raw.shape}")
print(f"Raw array dtype : {raw.dtype}")

if raw.dtype.names:
    # Structured / record array – Moku's typical export format
    print(f"Fields : {raw.dtype.names}")
    data = np.column_stack([raw[name] for name in raw.dtype.names]).astype(float)
else:
    if raw.ndim == 1:
        data = raw.reshape(1, -1)
    else:
        data = raw.astype(float)

print(f"Working array shape : {data.shape}  ({data.shape[0]} samples x {data.shape[1]} columns)")

# ── 3. Column layout (matches the .txt header) ────────────────────────────
# Col 0  : Time (s)
# Cols 1-5  : Ch1  set_freq, freq, phase(cyc), I, Q
# Cols 6-10 : Ch2  set_freq, freq, phase(cyc), I, Q
# Cols 11-15: Ch3  set_freq, freq, phase(cyc), I, Q
# Cols 16-20: Ch4  set_freq, freq, phase(cyc), I, Q

t      = data[:, 0]
fs_nom = 1.0 / np.median(np.diff(t))
print(f"Duration        : {t[-1] - t[0]:.3f} s")
print(f"Sample rate     : {fs_nom:.4f} Hz")

channels = {}
for ch, base in enumerate([1, 6, 11, 16], start=1):
    channels[ch] = {
        "set_freq"  : data[:, base],
        "freq"      : data[:, base + 1],
        "phase_cyc" : data[:, base + 2],
        "phase_rad" : data[:, base + 2] * 2 * np.pi,
        "freq_dev"  : data[:, base + 1] - data[:, base],
    }

labels = {
    ch: f"Ch{ch}  ({np.median(channels[ch]['set_freq']) * 1e-6:.4f} MHz)"
    for ch in channels
}
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

# ── 4. Figure 1 – Time series ──────────────────────────────────────────────
fig1, axes1 = plt.subplots(2, 4, figsize=(18, 8), sharex=True)
fig1.suptitle("Moku:Pro Phasemeter - Time Series", fontsize=14, fontweight="bold")

for i, ch in enumerate(channels):
    c = colors[i]
    d = channels[ch]

    ax_ph = axes1[0, i]
    ax_ph.plot(t, d["phase_cyc"], color=c, lw=0.7)
    ax_ph.set_title(labels[ch], fontsize=9)
    ax_ph.set_ylabel("Phase (cycles)" if i == 0 else "")
    ax_ph.grid(True, alpha=0.3)
    ax_ph.ticklabel_format(useOffset=False)

    ax_fr = axes1[1, i]
    ax_fr.plot(t, d["freq_dev"], color=c, lw=0.7)
    ax_fr.set_xlabel("Time (s)")
    ax_fr.set_ylabel("Freq. deviation (Hz)" if i == 0 else "")
    ax_fr.grid(True, alpha=0.3)
    ax_fr.ticklabel_format(useOffset=False)

fig1.tight_layout()
fig1.savefig("phasemeter_timeseries.pdf", dpi=150, bbox_inches="tight")
print("Saved: phasemeter_timeseries.pdf")

# ── 5. Figure 2 – ASD ─────────────────────────────────────────────────────
nperseg = min(len(t), max(256*256*4, int(fs_nom / 0.01)))

fig2, (ax_ph_asd, ax_fr_asd) = plt.subplots(2, 1, figsize=(10, 10))
fig2.suptitle("Moku:Pro Phasemeter - Amplitude Spectral Density", fontsize=14, fontweight="bold")

for i, ch in enumerate(channels):
    c = colors[i]
    d = channels[ch]

    f_ph, psd_ph = welch(detrend(d["phase_rad"]), fs=fs_nom, nperseg=nperseg,
                         window="hann", detrend="linear")
    f_fr, psd_fr = welch(detrend(d["freq_dev"]),  fs=fs_nom, nperseg=nperseg,
                         window="hann", detrend="linear")

    ax_ph_asd.loglog(f_ph[1:], np.sqrt(psd_ph[1:]), color=c, lw=1.2, label=labels[ch])
    ax_fr_asd.loglog(f_fr[1:], np.sqrt(psd_fr[1:]), color=c, lw=1.2, label=labels[ch])

for ax, ylabel, title in [
    (ax_ph_asd, "Phase ASD  (rad/sqrt(Hz))", "Phase Noise ASD"),
    (ax_fr_asd, "Freq. ASD  (Hz/sqrt(Hz))",  "Frequency Noise ASD"),
]:
    ax.set_title(title, fontsize=12)
    ax.set_xlabel("Fourier frequency (Hz)")
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, which="both", alpha=0.3)

fig2.tight_layout()
fig2.savefig("phasemeter_asd.pdf", dpi=150, bbox_inches="tight")
print("Saved: phasemeter_asd.pdf")

#plt.show()