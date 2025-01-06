import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.constants import c

class LaserSignal:

    def __init__(self, wavelength=1064e-9, nr_cyc=500000, f_mod=2.4*10**9, mod_depth=0.15, noise_std=0.1, 
                 noise_amplitude=15, modulation_type='analog'):

        self.wavelength = wavelength
        self.frequency = c / wavelength
        self.dT = 1 / self.frequency / 2.5
        self.t = np.arange(0, nr_cyc * 2 * np.pi / self.frequency, self.dT)
        self.noise_std = noise_std
        self.noise_amplitude = noise_amplitude
        self.f_mod = f_mod
        self.mod_depth = mod_depth
        self.modulation_type = modulation_type
        self.laser = None
        self.N = len(self.t)

    def generate_signal(self):
        # Generate modulation signal based on type
        if self.modulation_type == 'analog':
            LO = self.mod_depth * np.sin(2 * np.pi * self.f_mod * self.t)
        elif self.modulation_type == 'digital':
            LO = self.mod_depth * np.sign(np.sin(2 * np.pi * self.f_mod * self.t))  # Square wave
        
        noise = self.noise_amplitude * np.random.normal(0, self.noise_std, len(self.t))
        self.laser = np.exp(1j * (2 * np.pi * self.frequency * self.t + LO + noise))
    
    def get_signal(self):
        return self.laser, self.t

    def calculate_fft(self):
        fft_values = fft(self.laser) * 2 / self.N
        freqs = fftfreq(len(self.t), self.dT)
        return freqs, fft_values

    def write_to_file(self, filename):
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
    
    def plot_spectrum(self, lim_on=20):
        L_mod_fft = fft(self.laser)[1:self.N//2] * 2 / self.N
        freqs = fftfreq(len(self.t), self.dT)[1:self.N//2]
        
        plt.figure(figsize=(10, 6))
        plt.plot(freqs, np.abs(L_mod_fft), color="r")

        if lim_on: plt.xlim(self.frequency - lim_on*self.f_mod, self.frequency + lim_on*self.f_mod)

        plt.title("Spectrum of the Laser Signal")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude")
        plt.grid()
        plt.show()

    def plot_modified_spectrum(self, mod_signal):
        L_mod_fft = fft(mod_signal)[1:self.N//2] * 2 / self.N
        freqs = fftfreq(len(self.t), self.dT)[1:self.N//2]
        
        plt.figure(figsize=(10, 6))
        plt.plot(freqs, np.abs(L_mod_fft), color="r")

        #plt.xlim(self.frequency - 20*self.f_mod, self.frequency + 20*self.f_mod)
        plt.xlim(0, 150*10**6)

        plt.title("Spectrum of the Laser Signal")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude")
        plt.grid()
        plt.show()

    
    @classmethod
    def read_from_file(cls, filename):
        """
        Read the signal and parameters from a file and recreate a LaserSignal object.
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


    

N = 2*10**7

laser1_digital = LaserSignal(wavelength=1064e-9, nr_cyc=N, f_mod=2.4*10**9, mod_depth=0.15, noise_std=0.1, 
                 noise_amplitude=10, modulation_type='analog')
print("gen L1")
laser1_digital.generate_signal()
print("L1 gen done")
laser1_digital.write_to_file("L1_data.txt")


# 1 MHz higher
diff = 10*10**6
l_LO = c/(c/1064e-9+diff)
print("gen LO")
LO_digital = LaserSignal(wavelength=l_LO, nr_cyc=N, f_mod=2.401*10**9, mod_depth=0.15, noise_std=0.1, 
                 noise_amplitude=10, modulation_type='analog')
LO_digital.generate_signal()
print("LO gen done")

LO_digital.write_to_file("LO_data.txt")