import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.constants import c
from scipy.signal import welch

class LaserSignal:


    def __init__(self, name, wavelength=1064e-9, nr_cyc=500000, dT=0):

        self.name = name
        self.wavelength = wavelength
        self.frequency = c / wavelength
        if dT == 0: 
            print(f"{name}: Choosing dT as laser 1 / (frequency * 2.5)")
            self.dT = 1 / self.frequency / 2.5
        else: self.dT = dT
        print(f"{name}: dT: {self.dT*1e6} us")
        self.t = np.arange(0, nr_cyc * 2 * np.pi / self.frequency, self.dT)
        self.laser = None
        self.laser_noise = None
        self.clock_jitter = None
        self.N = len(self.t)
        print(f"{name}: Number of samples: {self.N}")

    @classmethod
    def from_duration(cls, name, wavelength=1064e-9, duration=1.0, dT=0):
        """
        Alternative constructor to initialize the LaserSignal object with the length of the data stream in seconds.
        """
        frequency = c / wavelength
        nr_cyc = duration * frequency / (2 * np.pi)
        print(f"{name}: laser wavelegth: {np.round(wavelength*1e9, 2)} nm")
        print(f"{name}: Number of cycles: {nr_cyc}")
        return cls(name, wavelength, nr_cyc, dT=dT)
    

    def __generate_1_f_noise(self, N, alpha=1):
        """
        Generate 1/f^alpha noise using frequency-domain shaping.
        """
        f = np.fft.rfftfreq(N)
        f[0] = f[1]  # Avoid division by zero
        magnitude = 1 / f**(alpha / 2)

        white_noise = np.random.normal(size=N)
        fft_vals = np.fft.rfft(white_noise)
        fft_vals *= magnitude
        shaped_noise = np.fft.irfft(fft_vals, n=N)
        return shaped_noise
    
    def __generate_integrated_white_noise(self, N, dt, scale=1e-4):
        """
        Generate clock jitter by integrating white noise (1/f² PSD in frequency).
        """
        white_noise = np.random.normal(scale=scale, size=N)
        phase_noise = np.cumsum(white_noise) * dt  # integrate to get phase
        return phase_noise
    
    def __generate_rin_noise(self, N, alpha=0, scale=1e-3):
        """
        Generate relative intensity noise (RIN) with PSD ~ 1/f^alpha.
        """
        f = np.fft.rfftfreq(N)
        f[0] = f[1]
        magnitude = 1 / f**(alpha / 2)

        white = np.random.normal(size=N)
        rin_fft = np.fft.rfft(white)
        rin_fft *= magnitude * scale
        rin = np.fft.irfft(rin_fft, n=N)
        return rin


    def generate_signal(self, mod_depth=0.15, f_mod=2.4*10**9, laser_noise_amplitude=10**-14, clock_noise_amplitude=0.001, clock_noise_std=0.01, modulation_type='analog'):
        
        """
        if modulation_type == 'analog':
            sideband = mod_depth * np.sin(2 * np.pi * f_mod * self.t)
        elif modulation_type == 'digital':
            sideband = mod_depth * np.sign(np.sin(2 * np.pi * f_mod * self.t))  # Square wave
        """

        print(f"{self.name}: Generating noise and the laser time series..")
        
        self.f_mod = f_mod
        print(f"{self.name}: modulating frequency: {self.f_mod/1e9} GHz")

        # Clock noise
        # GAUSSIAN-ish
        self.clock_jitter = self.__generate_integrated_white_noise(len(self.t), self.dT)
        cumulative_clock_error = np.cumsum(self.clock_jitter) * clock_noise_amplitude
        self.sideband = mod_depth * np.sin(2 * np.pi * f_mod * self.t + cumulative_clock_error)

        # RIN noise: applies multiplicative intensity noise
        rin_noise = self.__generate_rin_noise(len(self.t), alpha=0.5, scale=1e-3)  # 1/f⁰.⁵ is a decent approximation
        self.rin_modulation = rin_noise
        rin_amplitude = 1.0 + rin_noise  # multiplicative amplitude variation

        # Add GAUSSIAN noise to the signal
        # GAUUSIAN-ish
        self.laser_noise = self.__generate_1_f_noise(len(self.t), alpha=1)
        cumulative_laser_phase_error = np.cumsum(self.laser_noise) * laser_noise_amplitude
        self.laser = rin_amplitude * np.exp(1j * (2 * np.pi * self.frequency * self.t + self.sideband + cumulative_laser_phase_error))
    
    def get_signal(self):
        return self.laser, self.t

    def get_laser_noise(self):
        return self.laser_noise, self.t

    def get_clock_jitter(self):
        return self.clock_jitter
    

    def plot_spectrum(self, lim_on=20):
        L_mod_fft = fft(self.laser)[1:self.N//2] * 2 / self.N
        freqs = fftfreq(len(self.t), self.dT)[1:self.N//2]
        
        plt.figure(figsize=(10, 6))
        plt.plot(freqs, np.abs(L_mod_fft), color="r")

        if lim_on: plt.xlim(self.frequency - lim_on*self.f_mod, self.frequency + lim_on*self.f_mod)

        plt.title(f"{self.name}: Spectrum of the Laser Signal")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude")
        plt.grid()
        plt.show()



    def plot_clock_noise_psd(self, fs=None, nperseg=1024):
        """
        Plot the Power Spectral Density (PSD) of the clock jitter.
        """
        if self.clock_jitter is None:
            print(f"{self.name}: Clock jitter not yet generated.")
            return

        if fs is None:
            fs = 1 / self.dT

        freqs, psd = welch(self.clock_jitter, fs=fs, nperseg=nperseg)

        plt.figure(figsize=(10, 6))
        plt.loglog(freqs, np.sqrt(psd), label="Clock Noise PSD")
        plt.xlabel("Frequency [Hz]")
        plt.ylabel("Amplitude Spectral Density [units/√Hz]")
        plt.title(f"{self.name}: Clock Jitter PSD")
        plt.grid(True, which='both', ls='--')
        plt.legend()
        plt.show()

    def plot_laser_noise_psd(self, fs=None, nperseg=1024):
        """
        Plot the Power Spectral Density (PSD) of the laser noise.
        """
        if self.laser_noise is None:
            print(f"{self.name}: Laser noise not yet generated.")
            return

        if fs is None:
            fs = 1 / self.dT

        freqs, psd = welch(self.laser_noise, fs=fs, nperseg=nperseg)

        plt.figure(figsize=(10, 6))
        plt.loglog(freqs, np.sqrt(psd), label="Laser Noise PSD")
        plt.xlabel("Frequency [Hz]")
        plt.ylabel("Amplitude Spectral Density [units/√Hz]")
        plt.title(f"{self.name}: Laser Noise PSD")
        plt.grid(True, which='both', ls='--')
        plt.legend()
        plt.show()


    def plot_rin_psd(self, fs=None, nperseg=1024):
        """
        Plot the Power Spectral Density (PSD) of the RIN modulation.
        """
        if not hasattr(self, "rin_modulation"):
            print(f"{self.name}: RIN not generated.")
            return

        if fs is None:
            fs = 1 / self.dT

        freqs, psd = welch(self.rin_modulation, fs=fs, nperseg=nperseg)

        plt.figure(figsize=(10, 6))
        plt.loglog(freqs, np.sqrt(psd), label="RIN PSD")
        plt.xlabel("Frequency [Hz]")
        plt.ylabel("Amplitude Spectral Density [1/√Hz]")
        plt.title(f"{self.name}: Relative Intensity Noise PSD")
        plt.grid(True, which='both')
        plt.legend()
        plt.show()
