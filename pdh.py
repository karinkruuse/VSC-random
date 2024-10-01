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
t = np.arange(0, 1500*p/f, dT)
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

fLO = f/60
print("laser frequency", np.round(f*10**-12, 1), "THz")
print("modulating frequency", np.round(fLO*10**-9, 1), "GHz")
LO = 0.3*np.sin(p*fLO*t)


noise_switch = True
f = 0.99*f
if noise_switch:
    noise_L = np.random.normal(0, 0.1, N)
    # Miks see ei toota hasti, kui siin on sin
    L_mod = np.exp(1j *(p*f*t + LO + noise_L))
else:
    L_mod = np.exp(1j *(p*f*t + LO))



# Returns the intensity that is transmitted
def cavity(f, plot=False):
    F = np.pi*np.sqrt(R)/T
    print("Finesse", F)

    _wavelength = c/f
    _phi = p*n*L/_wavelength
    _I = 1/(1+M*np.sin(_phi)**2)

    # entrance angle 0
    if plot and not isinstance(f, Iterable):
        delta_wl = 500*10**-9/m
        wl = np.arange(_wavelength-delta_wl, _wavelength+delta_wl, delta_wl/N)
        phi = p*n*L/wl
        I = 1/(1+M*np.sin(phi)**2)

        fig, ax = plt.subplots(constrained_layout=True)
        ax.plot(phi/np.pi, 1-I)
        phi2wl = lambda x : const/x * 10**9
        wl2phi = lambda x : const/x * 10**-9
        secax = ax.secondary_xaxis('top', functions=(phi2wl, wl2phi))
        secax.set_xlabel('wavelength [nm]')
        plt.show()
    
    return _I
 

# the reflection for E
def reflection_coef(f):
    ex = np.exp(-1j*const*p/c*f)
    return -r*(ex - 1)/(1-R*ex)

show_laser = True
if(show_laser):
    fig, (ax3, ax1, ax2) = plt.subplots(3, 1, figsize=(12, 8))

    E0 = fft(L_mod)
    xf = fftfreq(N, dT)


    E_ref = reflection_coef(xf) * E0
    E_time = ifft(E_ref)
    I = np.real(E_time)**2 + np.imag(E_time)**2

    I_spec = 2.0/N*np.abs(fft(I))
    xf2 = fftfreq(len(I), dT)
    ax1.set_title("spectrum of the PD reading?")
    ax1.plot(xf[1:N//2], I_spec[1:N//2])
    ax1.set_xlabel("Frequency [Hz?]")
    ax1.grid()

    lower_bound = (f - fLO) * 0.8
    upper_bound = (f + fLO) + (f - fLO) * 0.2

    slice_indices = np.where((xf > lower_bound) & (xf < upper_bound))
    cropped_xf = xf[slice_indices]
    cropped_yf = 2/N*E0[slice_indices]

    ax2.set_title("E Spectrum after reflection")
    ax2.plot(cropped_xf, 2/N*np.real(E_ref[slice_indices]))
    ax2.plot(cropped_xf, 2/N*np.imag(E_ref[slice_indices]), color='gray', linestyle="--")
    ax2.grid()


    ax3.set_title("PM spectrum")
    ax3.plot(cropped_xf, np.real(cropped_yf))
    ax3.plot(cropped_xf, np.imag(cropped_yf), color='gray', linestyle="--")
    ax3.set_xlabel("Frequency (Hz)")
    ax3.grid()

    plt.tight_layout()
    plt.show()

