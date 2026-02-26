import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

# ----------------------------
# Choose a *manageable* carrier for simulation
# (same algebra as optics; just scaled down so fs and N are feasible)
# ----------------------------
f0   = 1.0e6     # "carrier" (Hz)  <-- change to e.g. 5e6 if you want
fSB  = 100e3     # sideband/modulation frequency (Hz)
beta = 0.2       # phase modulation index (rad)
phi_bias = np.pi/6

# Sampling: must satisfy fs > 2*(f0 + few*fSB)
fs = 50e6        # Hz
T  = 0.05        # seconds (sets resolution ~ 1/T = 20 Hz)
N  = int(fs*T)
t  = np.arange(N)/fs

sigma_dphi = 2e-4   # rad per sample step (tune this!)
phi_fiber = np.cumsum(sigma_dphi * np.random.randn(N))

A_ref = 1.0
A_mod = 0.8*A_ref

print(f"fs = {fs/1e6:.1f} MHz, N = {N}, df = {fs/N:.1f} Hz")
print(f"f0 = {f0/1e6:.3f} MHz, fSB = {fSB/1e3:.1f} kHz")

# ----------------------------
# Fields: explicitly include the carrier
# ----------------------------
E_ref = A_ref*np.exp(1j * 2*np.pi*f0*t)
E_mod = A_mod*np.exp(1j * (2*np.pi*f0*t + phi_fiber + beta*np.sin(2*np.pi*fSB*t) + phi_bias))

# "addition in time, then square"
I = np.abs(E_ref + E_mod)**2
I -= np.mean(I)  # remove DC so the spectrum isn't dominated by it

# ----------------------------
# Spectrum
# ----------------------------
F = fftfreq(N, 1/fs)
S = np.abs(fft(I)) / N

m = F >= 0
Fpos, Spos = F[m], S[m]

# Plot: show low-frequency content (harmonics of fSB) and around the carrier
plt.figure()
plt.semilogy(Fpos/1e3, Spos + 1e-30)
plt.xlim(0, 800)  # kHz: shows fSB, 2fSB, ...
plt.xlabel("Frequency (kHz)")
plt.ylabel("|FFT{ |E_ref + E_mod|^2 }| (arb)")
plt.grid(True)
plt.tight_layout()
plt.show()

"""
plt.figure()
plt.semilogy(Fpos/1e6, Spos + 1e-30)
plt.xlim(max(0, (f0-0.5e6)/1e6), (f0+0.5e6)/1e6)  # MHz around "carrier"
plt.xlabel("Frequency (MHz)")
plt.ylabel("|FFT{ |E_ref + E_mod|^2 }| (arb)")
plt.grid(True)
plt.tight_layout()
plt.show()
"""