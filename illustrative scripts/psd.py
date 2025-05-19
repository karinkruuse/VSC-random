import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

# Simulation parameters
fs = 10000  # sampling rate in Hz
duration = 10  # seconds
t = np.linspace(0, duration, int(fs * duration), endpoint=False)

# Laser optical frequency
f0 = 2.82e14  # Hz

# Simulated fractional frequency fluctuations (white noise)
target_sqrt_Sy = 1e-12  # 1/√Hz
np.random.seed(0)
y = np.random.normal(0, target_sqrt_Sy * np.sqrt(fs / 2), size=t.shape)

# Remove DC (optional)
y_prime = y - np.mean(y)

# Calculate PSD using Welch's method
f, S_y = welch(y_prime, fs=fs, nperseg=2048)
sqrt_S_y = np.sqrt(S_y)
sqrt_S_df = f0 * sqrt_S_y  # Convert to absolute frequency noise

# Plot fractional and absolute frequency noise PSDs
plt.figure(figsize=(10, 6))
plt.loglog(f, sqrt_S_y, label=r'$\sqrt{S_y(f)}$ [1/$\sqrt{\mathrm{Hz}}$]')
plt.loglog(f, sqrt_S_df, label=r'$\sqrt{S_{\delta f}(f)}$ [Hz/$\sqrt{\mathrm{Hz}}$]')
plt.axhline(target_sqrt_Sy, color='blue', linestyle='--', label='Target $\sqrt{S_y}$')
plt.axhline(f0 * target_sqrt_Sy, color='orange', linestyle='--', label='Target $\sqrt{S_{\delta f}}$')
plt.xlabel('Fourier Frequency [Hz]')
plt.ylabel('Spectral Density')
plt.title('PSD of Relative and Absolute Frequency Fluctuations')
plt.grid(True, which='both')
plt.legend()
plt.tight_layout()
plt.show()
