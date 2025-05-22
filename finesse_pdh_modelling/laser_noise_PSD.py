import numpy as np
from scipy.signal import welch
from scipy.constants import c

class LaserFrequencyNoisePSD:
    def __init__(self, wavelength_nm=1064, beta=1.0, fs=10e3, seed=None):
        """
        Parameters:
        - wavelength_nm: laser wavelength in nanometers (default 1064 nm)
        - beta: exponent for 1/f^beta noise
        - fs: sampling rate in Hz
        - seed: random seed for reproducibility
        """
        self.lambda0 = wavelength_nm * 1e-9
        self.f0 = c / self.lambda0
        self.beta = beta
        self.fs = fs
        self.seed = seed

    def generate_time_series(self, duration):
        N = int(self.fs * duration)
        if self.seed is not None:
            np.random.seed(self.seed)

        freqs = np.fft.rfftfreq(N, d=1 / self.fs)
        freqs[0] = freqs[1]  # avoid div by zero

        amplitude = 1.0 / freqs**(self.beta / 2)
        phases = np.random.uniform(0, 2 * np.pi, len(freqs))
        spectrum = amplitude * (np.cos(phases) + 1j * np.sin(phases))

        # Hermitian symmetry
        full_spectrum = np.zeros(N, dtype=np.complex128)
        full_spectrum[:len(spectrum)] = spectrum
        full_spectrum[len(spectrum):] = np.conj(spectrum[-2:0:-1])

        freq_noise = np.fft.ifft(full_spectrum).real * self.fs
        t = np.arange(N) / self.fs
        return t, freq_noise

    def compute_psd(self, duration, nperseg=2**12):
        """
        Computes the PSD of the generated frequency noise.

        Parameters:
        - duration: total time in seconds
        - nperseg: segment length for Welch's method

        Returns:
        - f: frequency array
        - Pxx: power spectral density [Hz^2/Hz]
        """
        t, freq_noise = self.generate_time_series(duration)
        f, Pxx = welch(freq_noise, fs=self.fs, nperseg=nperseg)
        return f, Pxx
