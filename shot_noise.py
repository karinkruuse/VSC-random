import matplotlib.pyplot as plt
import numpy as np



q = 1.602e-19  # elementary charge in Coulombs

def shot_noise_current(photocurrent_amps):
    return np.sqrt(2 * q * photocurrent_amps)

# Frequency range (log scale)
frequencies = np.logspace(4, 8, 1000)  # 10 kHz to 100 MHz

# Compute constant shot noise current density for a given photocurrent
photocurrent = 1e-3  # 1 mA
i_shot = shot_noise_current(photocurrent)

# Convert to dB/Hz
shot_noise_db = 20 * np.log10(i_shot) * np.ones_like(frequencies)

# Plot
plt.figure(figsize=(8, 5))
plt.semilogx(frequencies, shot_noise_db, label="Shot Noise (1 mA)")
#plt.ylim(-170, -100)
plt.xlim(1e4, 1e8)
plt.xlabel("Frequency [Hz]")
plt.ylabel("Noise Current [dB/Hz]")
plt.title("Shot Noise Spectrum (1 mA Photocurrent)")
plt.grid(True, which='both', linestyle='--')
plt.legend()
plt.tight_layout()
plt.show()