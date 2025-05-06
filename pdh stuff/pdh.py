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
dT = 1 / f / 2.4
print(f"Sample spacing {np.round(dT*1e-15, 3)} fs")
signal_length = 5000000 # random fking units
t = np.arange(0, signal_length * p / f, dT)
N = len(t)
print(N, "samples")

# Mirror reflectivity and cavity parameters
R = 0.9995 # NOTICE THIS IS CAPITALIZED
r = np.sqrt(R)
T = 1 - R

# Geometry and cavity definition
n = 1
m = 1
L = 1e5 * wavelength # wl on minigi 1e-6 m
print("L is", L, "m")
const = 2 * n * L
fsr = c / (2 * L)
print("FSR is", np.round(fsr * 1e-6, 3), "MHz")

# Modulation
fLO = 0.1 * fsr
mod_depth = 0.15
LO = mod_depth * np.sin(p * fLO * t)
print("Laser frequency", np.round(f * 1e-12, 1), "THz")
print("Modulation frequency", np.round(fLO * 1e-6, 1), "MHz")

# Cavity finesse
finesse = np.pi * np.sqrt(R) / (1 - R)
print("Finesse is", finesse)

# Cavity reflection coefficient
def reflection_coef(f):
    ex = np.exp(-1j * const * p / c * f)
    return -r * (ex - 1) / (1 - R * ex)

# Frequency sweep for error signal (coarse)
n_points_error = 50
delta_f = 1.1 * fLO
fs_error = np.linspace(f - delta_f, f + delta_f, n_points_error)
print("Frequency range for error signal (THz)", np.round((fs_error[0])*1e-12, 6), np.round((fs_error[-1])*1e-12, 6))
print("step size for the error signal", (fs_error[1] - fs_error[0])*1e-6, "MHz (this should be smaller than the mod frequency)")



# Time-frequency variables
xf = fftfreq(N, dT)
print("FFT frequency resolution is", np.round((xf[1] - xf[0]) * 1e-6, 3), "MHz (This has to be smaller than the modulating frequency)")
error_signal = []

L_mod = np.exp(1j * (p * f * t + LO))#L_mod = np.exp(1j * (p * f_i * t + LO + noise_L))
E0 = fft(L_mod)[1:N//2] * 2 / N
freqs = xf[1:N//2]

plt.figure(figsize=(10, 6))
plt.plot(freqs, np.abs(E0), color="r")
plt.xlim(f - 2*fLO, f + 2*fLO)
plt.show()

# Loop for error signal only (coarse)
for i in range(n_points_error):
    f_i = fs_error[i]
    print("On iteration", i+1, "of", n_points_error)
    #noise_L = np.random.normal(0, 0.5, N)
    L_mod = np.exp(1j * (p * f_i * t + LO))#L_mod = np.exp(1j * (p * f_i * t + LO + noise_L))
    E0 = fft(L_mod)
    E_ref = reflection_coef(xf) * E0
    E_time = ifft(E_ref)
    I = np.real(E_time)**2 + np.imag(E_time)**2
    mixed_signal = np.multiply(np.sin(p * fLO * t), I)
    mixed_spectrum = fft(mixed_signal)
    error_signal.append(mixed_spectrum[0])

"""    
# Frequency sweep for reflectance/transmittance (fine)
n_points_fine = 10000
n_fsr = 3
delta_f_fine = n_fsr * fsr
fs_fine = np.linspace(f - delta_f_fine, f + delta_f_fine, n_points_fine)
# Reflectance and transmittance (fine resolution)
refl_coef_vals = reflection_coef(fs_fine)
reflectance = np.abs(refl_coef_vals)**2
transmittance = 1 - reflectance
"""
# Plotting
#fig, axs = plt.subplots(1, 1, figsize=(8, 6), sharex=False)

# --- Error signal and Re{r(f)} ---
plt.plot((fs_error - f) *1e-6, np.real(reflection_coef(fs_error)), color="black", label="Re[Reflection Coefficient]")
plt.ylabel("Re[r(f)]")
ax2 = plt.twinx()
ax2.plot((fs_error - f) *1e-6, np.real(error_signal), color="navy", label="PDH Error Signal")
ax2.set_ylabel("Error Signal", color="navy")
ax2.tick_params(axis='y', labelcolor="navy")
plt.grid()
plt.title(f"PDH Error Signal and Reflection Coefficient\nm = {m}, Modulation frequency = {np.round(fLO * 1e-6, 3)} MHz")
plt.xlabel("Frequency around Carrier [MHz]")

"""
# --- Reflectance and Transmittance (fine) ---
axs[1].plot((fs_fine - f) *1e-6, reflectance, label="Reflectance", color="firebrick")
axs[1].plot((fs_fine - f)*1e-6, transmittance, label="Transmittance", color="green")
axs[1].set_xlabel("Frequency around Carrier [MHz]")
axs[1].set_ylabel("Power Ratio")
axs[1].legend()
axs[1].grid()
"""
plt.tight_layout()
plt.show()
