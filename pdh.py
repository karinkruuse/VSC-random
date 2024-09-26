import numpy as np
from scipy.fft import fft, ifft, fftfreq
from scipy.constants import c
import matplotlib.pyplot as plt

from collections.abc import Iterable

p = 2*np.pi

wavelength = 1064*10**-9
f = c/wavelength

dT = 1/f/4.2
print("Sample spacing", dT)
t = np.arange(0, 100*p/f, dT)
N = len(t)
print(N, "samples")

div = np.random.uniform(1.1, 7)
fLO = f/div
print("laser frequency", np.round(f*10**-12, 1), "THz")
print("modulating frequency", np.round(fLO*10**-12, 1), "THz")
LO = 0.4*np.sin(p*fLO*t)

noise_switch = True
if noise_switch:
    noise_L = np.random.normal(0, 0.2, N)
    L_mod = np.sin(p*f*t + LO + noise_L)
else:
    L_mod = np.sin(p*f*t + LO)

"""cavity"""   
R = 0.99
T = 1 - R

M = 4*R/T**2
n = 1
m = 1
L = 2 * wavelength/n*m

const = 2*n*L
F = np.pi*np.sqrt(R)/T
#print("Finesse", F)

# Returns the intensity
def cavity(f, plot=False):
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
 

show_laser = True
if(show_laser):
    fig, (ax2, ax3, ax1) = plt.subplots(3, 1, figsize=(12, 8))


    
    yf = fft(L_mod)[:N//2]
    xf = fftfreq(N, dT)[:N//2]

    lower_bound = (f - fLO) * 0.8
    upper_bound = (f + fLO) + (f - fLO) * 0.2

    slice_indices = np.where((xf > lower_bound) & (xf < upper_bound))
    cropped_xf = xf[slice_indices]
    cropped_yf = yf[slice_indices]

    ax2.plot(cropped_xf, 2.0/N * np.abs(cropped_yf))
    #print(slice_indices)
    #ax2.vlines(xf[slice_indices[0][0]], 0, 1, color="red")
    #ax2.vlines(xf[slice_indices[0][-1]], 0, 1, color="red")
    #ax2.vlines(f, 0, 1, color="black", linestyle="--")
    #ax2.vlines(f+fLO, 0, 1, color="black", linestyle="--")
    #ax2.vlines(f-fLO, 0, 1, color="black", linestyle="--")
    ax2.set_xlabel("Frequency (Hz)")
    ax2.grid()

    PD_I = np.multiply(1 - cavity(cropped_xf), cropped_yf)
    ax3.plot(cropped_xf, cavity(cropped_xf))
    f2wl = lambda x : c/x 
    wl2f = lambda x : c/x
    secax = ax3.secondary_xaxis('top', functions=(f2wl, wl2f))
    secax.set_xlabel('wavelength [nm]')
    ax3.grid()

    ax1.plot(cropped_xf, PD_I)
    ax1.grid()


    plt.tight_layout()
    plt.show()