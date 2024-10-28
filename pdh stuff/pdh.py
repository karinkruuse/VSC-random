import numpy as np
from scipy.fft import fft, ifft, fftfreq
from scipy.constants import c
import matplotlib.pyplot as plt

from collections.abc import Iterable

np.seterr(divide='ignore')

p = 2*np.pi

wavelength = 1064*10**-9
f = c/wavelength

dT = 1/f/3.3
print("Sample spacing", dT)
t = np.arange(0, 10000*p/f, dT)
N = len(t)
print(N, "samples")


R = 0.9
r = np.sqrt(R)
T = 1 - R

M = 4*R/T**2
n = 1
m = 1
L = 2 * wavelength/n*m
const = 2*n*L
fsr = c/2/L
print("FSR is", np.round(fsr*10**-12, 3), "THz")

fLO = 0.00004 * fsr
print("laser frequency", np.round(f*10**-12, 1), "THz")
print("modulating frequency", np.round(fLO*10**-9, 1), "GHz")
LO = 0.7*np.sin(p*fLO*t)


# the reflection for E
def reflection_coef(f):
    ex = np.exp(-1j*const*p/c*f)
    return -r*(ex - 1)/(1-R*ex)


noise_switch = True
if noise_switch:
    noise_L = np.random.normal(0, 0.1, N)
    # Miks see ei toota hasti, kui siin on sin
    L_mod = np.exp(1j *(p*f*t + LO + noise_L))
else:
    L_mod = np.exp(1j *(p*f*t + LO))


xf = fftfreq(N, dT)

delta_f = 1 * fsr * 10**-3
fs = np.arange(f - delta_f, f + delta_f, 2 * delta_f / 500)
error_signal = []

LP_filtering = False

if LP_filtering:
    f_cutoff = 0.1 * fLO
    LP_filter = lambda f: f_cutoff/(f + f_cutoff)
    filter_response = LP_filter(xf)
    #plt.plot(xf[:N//2], filter_response[:N//2])
    #plt.grid()
    #plt.show()

for f in fs:
    noise_L = 0# np.random.normal(0, 0.5, N)
    L_mod = np.exp(1j *(p*f*t + LO + noise_L))
    # Modulated laser spectrum
    E0 = fft(L_mod)

    # Add cavity reflection coef
    E_ref = reflection_coef(xf) * E0
    # Now go back to time domain
    E_time = ifft(E_ref)
    # Find power (PD reading essentially)
    I = np.real(E_time)**2 + np.imag(E_time)**2
    # And find its spectrum :)
    I_spec = 2.0/N*np.abs(fft(I))

    # The mixing
    mixed_signal = np.multiply(np.sin(p*fLO*t), I)
    # Spectrum after mixing
    mixed_spectrum = fft(mixed_signal)

    if LP_filtering:
        #filter spectrum
        filt_spec = filter_response * mixed_spectrum
        filt_P = ifft(filt_spec)
        error_signal.append(np.mean(filt_P))

    else:
        # And only the DC (LP filter :))
        error_signal.append(mixed_spectrum[0])
   


plt.title("Modulating frequency is " + str(np.round(fLO*10**-12, 1)) + " THz")
plt.plot(fs/fsr, np.real(reflection_coef(fs)), color="black")
ax2 = plt.twinx()
ax2.plot(fs/fsr, np.real(error_signal), color="navy")
ax2.tick_params(axis='y', labelcolor="navy")
plt.grid()
plt.xlabel("Frquency [FSR]")
plt.show()


