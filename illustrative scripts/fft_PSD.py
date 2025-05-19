import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

# Parameters
fs = 1000  # Sampling frequency (Hz)
duration = 2  # Signal duration (seconds)
n_samples = int(fs * duration)
t = np.linspace(0, duration, n_samples, endpoint=False)
f_carrier = 50  # Carrier frequency (Hz)

# Generate phase noise
phase_noise_std = 0.1  # Random walk step size
low_freq_noise = 0.2 * np.sin(2 * np.pi * 1 * t)  # Low-frequency noise at 1 Hz
random_walk = np.cumsum(np.random.normal(scale=phase_noise_std, size=n_samples)) / fs
phase_noise = low_freq_noise + random_walk

# Signal with phase noise
signal = np.cos(2 * np.pi * f_carrier * t + phase_noise)

# Compute PSDs
frequencies_noise, psd_noise = welch(phase_noise, fs, nperseg=256)
frequencies_signal, psd_signal = welch(signal, fs, nperseg=256)

# Total power for verification
power_noise = np.sum(psd_noise) * (frequencies_noise[1] - frequencies_noise[0])
power_signal = np.sum(psd_signal) * (frequencies_signal[1] - frequencies_signal[0])

# Plot
plt.figure(figsize=(12, 8))

# PSDs
plt.subplot(2, 1, 1)
plt.semilogy(frequencies_signal, psd_signal, label="Signal+Noise PSD")
plt.semilogy(frequencies_noise, psd_noise, label="Noise-Only PSD", linestyle="--", color="orange")
plt.xlabel("Frequency (Hz)")
plt.ylabel("PSD (Power/Hz)")
plt.title("Comparison of Signal+Noise PSD vs. Noise-Only PSD")
plt.grid(True)
plt.legend()

# Total power comparison
plt.subplot(2, 1, 2)
plt.bar(["Noise-Only Power", "Signal+Noise Power"], [power_noise, power_signal], color=["orange", "blue"])
plt.ylabel("Total Power")
plt.title("Integrated Power Comparison")
plt.grid(True)

plt.tight_layout()
plt.show()
