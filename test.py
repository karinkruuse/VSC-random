import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

# Parameters
fs = 1000        # Sampling frequency [Hz]
T = 10           # Duration [s]
N = fs * T       # Total samples
amp = 1e-6       # Micro-level amplitude

# Generate noise (Gaussian white noise)
time = np.arange(N) / fs
noise = amp * np.random.randn(N)

# --- Method 1: Welch PSD ---
f_welch, psd_welch = welch(noise, fs=fs, nperseg=1024)

# --- Method 2: Direct FFT PSD ---
fft_vals = np.fft.rfft(noise)
freqs = np.fft.rfftfreq(N, 1/fs)

psd_fft = (1/(fs*N)) * np.abs(fft_vals)**2
psd_fft[1:-1] *= 2   # one-sided correction

# --- Convert PSD to ASD ---
asd_welch = np.sqrt(psd_welch)
asd_fft = np.sqrt(psd_fft)

# --- Plot PSD and ASD ---
fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# PSD
axs[0].loglog(f_welch, psd_welch, label="Welch PSD", linewidth=2)
axs[0].loglog(freqs, psd_fft, label="FFT PSD", alpha=0.7)
axs[0].set_ylabel("PSD [V²/Hz]")
axs[0].set_title("Noise PSD Comparison")
axs[0].grid(True, which="both", ls="--")
axs[0].legend()

# ASD
axs[1].loglog(f_welch, asd_welch, label="Welch ASD", linewidth=2)
axs[1].loglog(freqs, asd_fft, label="FFT ASD", alpha=0.7)
axs[1].set_xlabel("Frequency [Hz]")
axs[1].set_ylabel("ASD [V/√Hz]")
axs[1].set_title("Noise ASD Comparison")
axs[1].grid(True, which="both", ls="--")
axs[1].legend()

plt.tight_layout()
plt.show()
