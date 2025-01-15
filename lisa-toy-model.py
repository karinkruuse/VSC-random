import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.constants import c

from elements.signal_generator import LaserSignal

wl = lambda f: c / f



# f1 has to be bigger here
f1 = 15 * 10**6 # MHz order
wl1 = wl(f1)

f_mod1 = 10 * 10**3

laser1 = LaserSignal.from_duration(wavelength=wl1, duration=1)
laser1.generate_signal(f_mod=f_mod1)
laser1.plot_spectrum()

N = laser1.N
f2 = 10 * 10**6 # MHz order
wl2 = wl(f2)
f_mod2 = 10 * 10**3

laser2 = LaserSignal.from_duration_and_N(N=N, wavelength=wl2, duration=1)
laser2.generate_signal(f_mod=f_mod2)
laser2.plot_spectrum()




"""
1) Generate like reasonable USO frequencies, but at like maybe on the order of kHz?
2) Add that to the lasers
3) The lasers have a way lower frequency, like 10s MHz maybe

then
4) delay one signal
5) PD
6) ADC -- HOW????
"""


