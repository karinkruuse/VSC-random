import numpy as np
from scipy.constants import c

class OpticalCavity:
    
    def __init__(self, name, wavelength=1064e-9, linewidth=30e3, L=0.25, radius1=np.inf, radius2=0.5):

        self.name = name
        self.wavelength = wavelength 

        self.L = L
        self.FSR = c / (2 * self.L)
        print("FSR is", self.FSR / 1e6, "MHz")

        self.linewidth = linewidth

        self.finesse = self.FSR / self.linewidth
        print("Finesse is", self.finesse)

        self.calculate_reflectivity()

        self.radius1 = radius1
        self.radius2 = radius2

        self.mode_offset = np.arccos(np.sqrt((1-self.L/radius1)*(1-self.L/radius2)))
        print("Mode offset times FSR is", self.FSR*self.mode_offset / 1e6, "MHz")

    def calculate_reflectivity(self):
        a = - self.finesse/np.pi
        b = - 1
        d = self.finesse/np.pi
        #R1 = (-b + np.sqrt(b**2 - 4*a*d))/(2*a) # this one seems to be the "wrong one" ie its always negative
        R2 = (-b - np.sqrt(b**2 - 4*a*d))/(2*a)

        self.R = R2
        self.r = np.sqrt(self.R)


    def reflection_coef(self, freq):
        temp = np.exp(-1j * self.L * 4 * np.pi / c * freq)
        return -self.r * (temp - 1) / (1 - self.R * temp)


    

