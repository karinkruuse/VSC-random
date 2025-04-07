import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

# Simulation parameters
fs = 10000  # sampling rate in Hz
duration = 10  # seconds
t = np.linspace(0, duration, int(fs * duration), endpoint=False)

# Nominal laser frequency (we use RF-scale here for tractability)
f0 = 1000  # Hz (simulated laser center frequency)

# Generate frequency noise: white noise with 30 Hz/√Hz spectral density
np.random.seed(0)
df_rms_density = 30  # Hz/√Hz
df_white_noise = np.random.normal(0, df_rms_density * np.sqrt(fs / 2), size=t.shape)

# Integrate to get phase: φ(t) = 2π ∫ δf(t) dt
phi = 2 * np.pi * np.cumsum(df_white_noise) / fs

# Generate electric field with frequency noise
E = np.cos(2 * np.pi * f0 * t + phi)

# Compute PSD of instantaneous frequency deviation
instantaneous_freq = f0 + df_white_noise
f_psd, Pxx = welch(instantaneous_freq - f0, fs=fs, nperseg=1024)

# Plot the electric field (zoomed in), instantaneous frequency, and PSD
fig, axs = plt.subplots(3, 1, figsize=(10, 10))

# Electric field zoomed view
zoom_idx = slice(0, int(fs * 0.01))
axs[0].plot(t[zoom_idx], E[zoom_idx])
axs[0].set_title("Simulated 'Laser' Electric Field (Zoomed In)")
axs[0].set_xlabel("Time [s]")
axs[0].set_ylabel("E(t)")

# Instantaneous frequency
axs[1].plot(t, instantaneous_freq)
axs[1].set_title("Instantaneous Frequency")
axs[1].set_xlabel("Time [s]")
axs[1].set_ylabel("Frequency [Hz]")

# PSD of frequency noise
axs[2].loglog(f_psd, np.sqrt(Pxx), label=r'$\sqrt{S_{\delta f}}(f)$')
axs[2].axhline(df_rms_density, color='red', linestyle='--', label='Target: 30 Hz/√Hz')
axs[2].set_title("PSD of Frequency Fluctuations")
axs[2].set_xlabel("Fourier Frequency [Hz]")
axs[2].set_ylabel("Frequency Noise [Hz/√Hz]")
axs[2].legend()
axs[2].grid(True, which='both')

plt.tight_layout()
plt.show()
