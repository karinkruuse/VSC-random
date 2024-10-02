import numpy as np
from scipy.constants import c

class Cavity:


    def __init__(self, wl, r1, r2, t1, t2, n, m):    
        self.wl = wl
        self.R = r1**2
        self.r = r1
        self.L = 2 * wl/n*m
        self.const = 2 * n * self.L

    def reflection(self, f):
        ex = np.exp(-1j * 2*np.pi * self.const / c * f)
        return -self.r * (ex - 1) / (1 - self.R * ex)
