import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, ifft, fftfreq
from scipy.constants import c

from signal_generator import LaserSignal

# The PDH frequency stabilization is accomplished by modulating the laser
# phase using an electro-optical modulator with MHz side-bands

class PDHLocking:
    def __init__(self, R=0.9, n=1, m=1, wavelength=1064e-9, fsr_ratio=1e-3, lp_filtering=False, cutoff_ratio=0.1):
        self.R = R
        self.r = np.sqrt(R)
        self.T = 1 - R
        self.n = n
        self.m = m
        self.wavelength = wavelength
        self.frequency = c / wavelength
        self.L = 2 * wavelength / n * m
        self.const = 2 * n * self.L
        self.fsr = c / (2 * self.L)
        self.delta_f = fsr_ratio * self.fsr
        self.lp_filtering = lp_filtering
        self.cutoff_ratio = cutoff_ratio
        self.error_signal = []

    def reflection_coef(self, freq):
        ex = np.exp(-1j * self.const * 2 * np.pi / c * freq)
        return -self.r * (ex - 1) / (1 - self.R * ex)

    def _compute_error_for_frequency(self, f, t, fLO, LO, xf, LP_filter=None):
        # Generate modulated laser signal for a specific frequency
        L_mod = np.exp(1j * (2 * np.pi * f * t + LO))
        E0 = fft(L_mod)
        
        # Reflect through cavity and compute error signal
        E_ref = self.reflection_coef(xf) * E0
        E_time = ifft(E_ref)
        I = np.real(E_time) ** 2 + np.imag(E_time) ** 2
        mixed_signal = np.multiply(np.sin(2 * np.pi * fLO * t), I)
        mixed_spectrum = fft(mixed_signal)
        
        if LP_filter is not None:
            filt_spec = LP_filter * mixed_spectrum
            filt_P = ifft(filt_spec)
            return np.mean(filt_P)
        else:
            return mixed_spectrum[0]
        
    def calculate_error_signal(self, t):
        N = len(t)
        dT = t[1] - t[0]
        xf = fftfreq(N, dT)
        
        fs = np.arange(self.frequency - self.delta_f, self.frequency + self.delta_f, 2 * self.delta_f / 50)
        
        fLO = 0.00004 * self.fsr
        LO = np.sin(2 * np.pi * fLO * t)
        
        LP_filter = None
        if self.lp_filtering:
            f_cutoff = self.cutoff_ratio * fLO
            LP_filter = f_cutoff / (xf + f_cutoff)
        
        for f in fs:
            error_value = self._compute_error_for_frequency(f, t, fLO, LO, xf, LP_filter)
            self.error_signal.append(np.real(error_value))
        
        
        plt.plot(fs/self.fsr, self.error_signal)
        plt.title("FSR = " + str(self.fsr))
        plt.xlabel("Frequency (FSRs)")
        plt.show()
        return self.error_signal

# Usage Example
laser = LaserSignal()
#laser.plot_spectrum()
laser_signal, t = laser.get_signal()

pdh = PDHLocking()
error_signal = pdh.calculate_error_signal(t)