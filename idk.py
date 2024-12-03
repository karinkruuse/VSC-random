import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.constants import c

wl0 = 1064*10**-9
p = 2*np.pi


def eta():
    return