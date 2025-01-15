import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.constants import c

from elements.signal_generator import LaserSignal

wl = lambda f: c / f


duration = 1

# f1 has to be bigger here
f1 = 15 * 10**6 # MHz order
wl1 = wl(f1)

f_mod1 = 22 * 10**3

laser1 = LaserSignal.from_duration("SC1", wavelength=wl1, duration=duration)
laser1.generate_signal(f_mod=f_mod1)
#laser1.plot_spectrum()

dT = laser1.dT
f2 = 12 * 10**6 # MHz order
wl2 = wl(f2)
f_mod2 = 13 * 10**3

laser2 = LaserSignal.from_duration("SC2", wavelength=wl2, duration=duration, dT=dT)
laser2.generate_signal(f_mod=f_mod2)
#laser2.plot_spectrum()

"""
f3 = 10 * 10**6 # MHz order
wl3 = wl(f3)
f_mod3 = 10 * 10**3

laser3 = LaserSignal.from_duration_and_N(N=N, wavelength=wl3, duration=duration)
laser3.generate_signal(f_mod=f_mod3)
laser3.plot_spectrum()
"""

l1, t1 = laser1.get_signal()
l2, t2 = laser2.get_signal()

N_to_delay = int(laser1.N / 5)
delay = N_to_delay * dT
print(f"Delay: {delay*1000} ms")

# In the beginning of the array are older values
temp = l1[N_to_delay:] + l2[:-N_to_delay]
PD1 = np.real(temp) ** 2 + np.imag(temp) ** 2


n = len(PD1)
L_mod_fft = fft(PD1)[1:n//2] * 2 / n
freqs = fftfreq(n, dT)[1:n//2]

plot_PD = False
if plot_PD:
    plt.figure(figsize=(10, 6))
    plt.plot(freqs/10**6, np.abs(L_mod_fft), color="r")

    #plt.xlim(1, 10)

    plt.title("Spectrum of the beatnote")
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Amplitude")
    plt.grid()
    plt.show()




