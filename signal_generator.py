import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, ifft, fftfreq
from scipy.constants import c



class LaserSignal:

    def __init__(self, wavelength=1064e-9, nr_cyc=10000, f_mod=0.01, mod_depth=0.15, noise_std=0.1, noise_amplitude=15):
        self.wavelength = wavelength
        self.frequency = c / wavelength
        self.dT = 1 / self.frequency / 2.5
        self.t = np.arange(0, nr_cyc * 2 * np.pi / self.frequency, self.dT)
        self.noise_std = noise_std
        self.noise_amplitude = noise_amplitude
        self.f_mod = f_mod
        self.mod_depth = mod_depth
        self.laser = None
        self.N = len(self.t)
        self.generate_signal()
        
    def generate_signal(self):
        # Calculate parameters for modulation
        LO = self.mod_depth * np.sin(2 * np.pi * self.f_mod * self.t)
        noise = self.noise_amplitude * np.random.normal(0, self.noise_std, len(self.t))
        self.laser = np.exp(1j * (2 * np.pi * self.frequency * self.t + LO + noise))
    
    def get_signal(self):
        return self.laser, self.t
    
    def plot_spectrum(self):
        L_mod_fft = fft(self.laser)[1:self.N//2]*2/self.N
        freqs = fftfreq(len(self.t), self.dT)[1:self.N//2]
        
        plt.figure(figsize=(10, 6))
        plt.plot(freqs, np.abs(L_mod_fft), color="r")
        plt.title("Spectrum of the Laser Signal")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude")

        #plt.xlim(self.frequency - 3 * self.modulation_frequency_ratio * self.frequency, self.frequency +  3 * self.modulation_frequency_ratio * self.frequency)

        plt.grid()
        plt.show()

