import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.constants import c

from elements.laser import LaserSignal

laser1 = LaserSignal.from_duration("Laser1", wavelength=1064e-9, duration=0.000000001, dT=0)
laser1.generate_signal()
laser1.plot_spectrum(lim_on=0)
laser1.plot_laser_noise_psd()
laser1.plot_clock_noise_psd()
laser1.plot_rin_psd()

