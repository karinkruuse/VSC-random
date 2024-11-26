import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.constants import c


wavelength = 1064*10**-9
frequency = c / wavelength
dT = 1 / frequency / 2.5 * 80000
nr_cyc = 50000000000
f_mod = 2.4*10**9
mod_depth1 = 0.2
mod_depth2 = 0.75
t = np.arange(0, nr_cyc * 2 * np.pi / frequency, dT)
LO = mod_depth2 * np.cos(2 * np.pi * (f_mod + 10**6) * t)

#noise = 10 * np.random.normal(0, 0.1, len(t))
carrier_diff = 10**7
beatnote = np.cos(2 * np.pi * frequency * t + mod_depth1*np.cos(2 * np.pi * f_mod * t) - (2 * np.pi * (frequency + carrier_diff) * t + LO))

N = len(t)
L_mod_fft = fft(beatnote)[1:N//2] * 2 / N
freqs = fftfreq(len(t), dT)[1:N//2]

plt.figure(figsize=(10, 6))
plt.plot(freqs, np.abs(L_mod_fft), color="r")

#if lim_on: plt.xlim(frequency - lim_on*f_mod, frequency + lim_on*f_mod)

plt.title("Spectrum of the Laser Signal")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.grid()
plt.show()