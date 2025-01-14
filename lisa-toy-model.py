import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.constants import c

from elements.signal_generator import LaserSignal

laser1 = LaserSignal()
laser1.generate_signal()
#laser.plot_spectrum()
laser_signal1, t1 = laser1.get_signal()


laser2 = LaserSignal()
laser2.generate_signal()
#laser.plot_spectrum()
laser_signal2, t2 = laser2.get_signal()

freqs2, fft_values2 = laser2.calculate_fft()

delay = 0

freqs2_del = 0
# Time-Shifting Property of Fourier Transform
