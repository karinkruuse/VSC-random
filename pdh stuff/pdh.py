import numpy as np
from scipy.fft import fft, ifft, fftfreq
from scipy.constants import c
import matplotlib.pyplot as plt

np.seterr(divide='ignore')

# Constants
p = 2 * np.pi
wavelength = 1064e-9
f = c / wavelength

# Time domain
dT = 1 / f / 3.3
print("Sample spacing", dT)
t = np.arange(0, 300000 * p / f, dT)
N = len(t)
print(N, "samples")

# Mirror reflectivity and cavity parameters
R = 0.995 # NOTICE THIS IS CAPITALIZED
r = np.sqrt(R)
T = 1 - R

# Geometry and cavity definition
n = 1
m = 5000
L = 2 * wavelength / n * m
print("L is", L, "m")
const = 2 * n * L
fsr = c / (2 * L)
print("FSR is", np.round(fsr * 1e-12, 3), "THz")

# Modulation
fLO = 0.04 * fsr
mod_depth = 0.15
LO = mod_depth * np.sin(p * fLO * t)
print("Laser frequency", np.round(f * 1e-12, 1), "THz")
print("Modulation frequency", np.round(fLO * 1e-9, 1), "GHz")

# Cavity finesse
finesse = np.pi * np.sqrt(R) / (1 - R)
print("Finesse is", finesse)

# Cavity reflection coefficient
def reflection_coef(f):
    ex = np.exp(-1j * const * p / c * f)
    return -r * (ex - 1) / (1 - R * ex)

# Frequency sweep for error signal (coarse)
n_points_error = 1000
delta_f = 0.1 * fsr
fs_error = np.linspace(f - delta_f, f + delta_f, n_points_error)

# Frequency sweep for reflectance/transmittance (fine)
n_points_fine = 10000
n_fsr = 3
delta_f_fine = n_fsr * fsr
fs_fine = np.linspace(f - delta_f_fine, f + delta_f_fine, n_points_fine)

# Time-frequency variables
xf = fftfreq(N, dT)
error_signal = []

# Loop for error signal only (coarse)
for f_i in fs_error:
    print(f_i)
    #noise_L = np.random.normal(0, 0.5, N)
    L_mod = np.exp(1j * (p * f_i * t + LO))#L_mod = np.exp(1j * (p * f_i * t + LO + noise_L))
    E0 = fft(L_mod)
    E_ref = reflection_coef(xf) * E0
    E_time = ifft(E_ref)
    I = np.real(E_time)**2 + np.imag(E_time)**2
    mixed_signal = np.multiply(np.sin(p * fLO * t), I)
    mixed_spectrum = fft(mixed_signal)
    error_signal.append(mixed_spectrum[0])

# Reflectance and transmittance (fine resolution)
refl_coef_vals = reflection_coef(fs_fine)
reflectance = np.abs(refl_coef_vals)**2
transmittance = 1 - reflectance

# Plotting
fig, axs = plt.subplots(2, 1, figsize=(8, 6), sharex=False)

# --- Error signal and Re{r(f)} ---
axs[0].plot((fs_error - f) / fsr, np.real(reflection_coef(fs_error)), color="black", label="Re[Reflection Coefficient]")
axs[0].set_ylabel("Re[r(f)]")
ax2 = axs[0].twinx()
ax2.plot((fs_error - f) / fsr, np.real(error_signal), color="navy", label="PDH Error Signal")
ax2.set_ylabel("Error Signal", color="navy")
ax2.tick_params(axis='y', labelcolor="navy")
axs[0].grid()
axs[0].set_title(f"PDH Error Signal and Reflection Coefficient\nm = {m}, Modulation frequency = {np.round(fLO * 1e-9, 1)} GHz")

# --- Reflectance and Transmittance (fine) ---
axs[1].plot((fs_fine - f) / fsr, reflectance, label="Reflectance", color="firebrick")
axs[1].plot((fs_fine - f) / fsr, transmittance, label="Transmittance", color="green")
axs[1].set_xlabel("Detuning [FSR]")
axs[1].set_ylabel("Power Ratio")
axs[1].legend()
axs[1].grid()

plt.tight_layout()
plt.show()
