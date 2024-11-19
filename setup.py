import numpy as np
import matplotlib.pyplot as plt

from scipy.constants import c
from signal_generator import LaserSignal

wavelength = 1064e-9
f_PDH_EOM = 50*10**8


laser = LaserSignal(nr_cyc=300000, f_mod=f_PDH_EOM)

laser.plot_spectrum()

