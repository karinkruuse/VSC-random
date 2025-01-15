import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.constants import c

class LaserSignal:


    def __init__(self, name, wavelength=1064e-9, nr_cyc=500000, dT=0):

        self.name = name
        self.wavelength = wavelength
        self.frequency = c / wavelength
        if dT == 0: self.dT = 1 / self.frequency / 2.5
        else: self.dT = dT
        print(f"{name}: dT: {self.dT*1000000} us")
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
        print(f"{name}: laser wavelegth: {np.round(wavelength)}")
        print(f"{name}: Number of cycles: {nr_cyc}")
        return cls(name, wavelength, nr_cyc, dT=dT)
    

    def generate_signal(self, mod_depth=0.15, f_mod=2.4*10**9, laser_noise_amplitude=0.01, laser_noise_std=0.1, clock_noise_amplitude=0, clock_noise_std=0.01, modulation_type='analog'):
        
        """
        if modulation_type == 'analog':
            sideband = mod_depth * np.sin(2 * np.pi * f_mod * self.t)
        elif modulation_type == 'digital':
            sideband = mod_depth * np.sign(np.sin(2 * np.pi * f_mod * self.t))  # Square wave
        """
        
        self.f_mod = f_mod

        # Clock noise
        # GAUSSIAN-ish
        self.clock_jitter = np.cumsum(clock_noise_amplitude * np.random.normal(0, clock_noise_std, len(self.t)))
        sideband = mod_depth * np.sin(2 * np.pi * f_mod * self.t + self.clock_jitter)

        # Add GAUSSIAN noise to the signal
        # GAUUSIAN-ish
        self.laser_noise = np.cumsum(laser_noise_amplitude * np.random.normal(0, laser_noise_std, len(self.t)))
        self.laser = np.exp(1j * (2 * np.pi * self.frequency * self.t + sideband + self.laser_noise))
    
    def get_signal(self):
        """
        Get the generated laser signal and time array.
        
        Returns:
        tuple: (laser signal, time array)
        """
        return self.laser, self.t

    def add_noise():
        """
        Generate your desired power spectral density in the frequency domain (for example Gaussian, 1/f, etc).
        Randomize phase.
        FFT back to the time domain.
        """
        #the spectrum doesnt really matter that much? 
        return

    def calculate_fft(self):
        """
        Calculate the FFT of the laser signal.
        
        Returns:
        tuple: (frequencies, FFT values)
        """
        fft_values = fft(self.laser) * 2 / self.N
        freqs = fftfreq(len(self.t), self.dT)
        return freqs, fft_values

    def plot_spectrum(self, lim_on=20):
        """
        Plot the spectrum of the laser signal.
        
        Parameters:
        lim_on (int): Limit for the x-axis around the modulation frequency.
        """
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

    def plot_modified_spectrum(self, mod_signal):
        """
        Plot the spectrum of a modified signal.
        
        Parameters:
        mod_signal (array): The modified signal to plot.
        """
        L_mod_fft = fft(mod_signal)[1:self.N//2] * 2 / self.N
        freqs = fftfreq(len(self.t), self.dT)[1:self.N//2]
        
        plt.figure(figsize=(10, 6))
        plt.plot(freqs, np.abs(L_mod_fft), color="r")

        plt.xlim(0, 150*10**6)

        plt.title("Spectrum of the Laser Signal")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude")
        plt.grid()
        plt.show()

    def write_to_file(self, filename):
        """
        Write the laser signal and its FFT to a file.
        
        Parameters:
        filename (str): Name of the file to write to.
        """
        freqs, fft_values = self.calculate_fft()
        with open(filename, 'w') as f:
            # Write parameters as a comment
            f.write(f"# wavelength={self.wavelength}, nr_cyc={len(self.t)}, f_mod={self.f_mod}, "
                    f"mod_depth={self.mod_depth}, noise_std={self.noise_std}, "
                    f"noise_amplitude={self.noise_amplitude}, modulation_type={self.modulation_type}\n")
            # Write time, signal, and FFT to the file
            for i in range(len(self.t)):
                f.write(f"{self.t[i]:.6e}, {self.laser[i].real:.6e}, {self.laser[i].imag:.6e}, "
                        f"{freqs[i]:.6e}, {fft_values[i].real:.6e}, {fft_values[i].imag:.6e}\n")
    
    @classmethod
    def read_from_file(cls, filename):
        """
        Read the signal and parameters from a file and recreate a LaserSignal object.
        
        Parameters:
        filename (str): Name of the file to read from.
        
        Returns:
        LaserSignal: A new LaserSignal object with the data from the file.
        """
        with open(filename, 'r') as f:
            # Read the parameters from the first line
            param_line = f.readline()
            if not param_line.startswith("#"):
                raise ValueError("File does not contain parameter metadata in the first row.")
            param_line = param_line[1:].strip()  # Remove the leading '#' and whitespace
            
            # Parse parameters
            params = {}
            for param in param_line.split(","):
                key, value = param.split("=")
                key = key.strip()
                value = value.strip()
                params[key] = float(value) if '.' in value or 'e' in value.lower() else value
            
            # Read the signal data
            data = np.loadtxt(f, delimiter=",")
            t = data[:, 0]
            real_signal = data[:, 1]
            imag_signal = data[:, 2]
            laser_signal = real_signal + 1j * imag_signal
            
            # Create a new LaserSignal object
            obj = cls(wavelength=params['wavelength'], f_mod=params['f_mod'], 
                      mod_depth=params['mod_depth'], noise_std=params['noise_std'], 
                      noise_amplitude=params['noise_amplitude'], modulation_type=params['modulation_type'])
            obj.t = t
            obj.laser = laser_signal
            obj.N = len(t)
            return obj
