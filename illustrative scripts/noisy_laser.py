import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

def generate_noise(beta, N=2**20, fs=1.0, seed=None):
    if seed is not None:
        np.random.seed(seed)

    freqs = np.fft.rfftfreq(N, d=1/fs)
    freqs[0] = 1e-6 

    amplitude = 1e6 / freqs**(beta / 2)

    # Random phases
    phases = np.random.uniform(0, 2*np.pi, len(freqs))
    real = amplitude * np.cos(phases)
    imag = amplitude * np.sin(phases)
    spectrum = real + 1j * imag

    # Hermitian symmetry for real-valued signal
    full_spectrum = np.zeros(N, dtype=np.complex128)
    full_spectrum[:len(spectrum)] = spectrum
    full_spectrum[len(spectrum):] = np.conj(spectrum[1:-1][::-1])

    y = np.fft.ifft(full_spectrum).real

    t = np.arange(N) / fs
    return t, y

fs = 10e3  # 10 kHz sampling
duration = 1.0  # seconds
N = int(fs * duration)
beta = 1.0 # while 2 would be the simple theoritical, for Mephisto it looked like 1

t, freq_noise = generate_noise(beta=beta, N=N, fs=fs, seed=43)

# Plot
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(t, freq_noise, lw=0.5)
plt.title(f'Simulated 1D Laser Frequency Noise (1/f^{beta})')
plt.xlabel('Time [s]')
plt.ylabel('Frequency noise [a.u.]')

# PSD
f, Pxx = welch(freq_noise, fs=fs, nperseg=2**12)
plt.subplot(2, 1, 2)
plt.loglog(f, Pxx)
plt.xlabel('Frequency [Hz]')
plt.ylabel(r'$S_f(f)$')
plt.grid(True)
plt.tight_layout()
plt.show()
