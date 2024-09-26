import numpy as np
from scipy.fft import fft, ifft, fftfreq
from scipy.constants import c
import matplotlib.pyplot as plt

p = 2*np.pi


wavelength = 1064*10**-9
f = c/wavelength

T = 1/f/5
N = 1000
t = np.arange(0, N*T, T)

fLO = f/2.7
LO = 0.3*np.sin(fLO*t)
L_mod = np.sin(f*t + LO)

noise_switch = True
if noise_switch:
    noise_L = np.random.normal(0, 0.2, N)
    L_mod = np.sin(f*t + LO + noise_L)

show_laser = False
if(show_laser):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    ax1.plot(t, L_mod)
    ax1.set_xlabel("Time (s)")
    ax1.grid()

    x = np.linspace(0.0, N*T, N, endpoint=False)
    yf = fft(L_mod)
    xf = fftfreq(N, T)[:N//2]
    ax2.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
    ax2.set_xlabel("Frequency (Hz)")
    ax2.grid()
    plt.tight_layout()
    plt.show()

"""cavity"""   
R = 0.97
T = 1 - R

M = 4*R/T**2
n = 1
m = 45
def cavity(f, plot=False):
    _wavelength = c/f
    _L = 2 * _wavelength/n*m
    phi = p*n*_L/_wavelength
    _I = 1/(1+M*np.sin(phi)**2)

    # entrance angle 0
    show_cavity = True
    if show_cavity:
        delta_wl = 500*10**-9/m
        wl = np.arange(_wavelength-delta_wl, _wavelength+delta_wl, 10**-11)
        phi = p*n*_L/wl
        I = 1/(1+M*np.sin(phi)**2)
        fig, ax = plt.subplots(constrained_layout=True)
        ax.plot(phi/np.pi, -I)
        phi2wl = lambda x : 2*n*_L/x * 10**9
        wl2phi = lambda x : 2*n*_L/x * 10**-9
        secax = ax.secondary_xaxis('top', functions=(phi2wl, wl2phi))
        secax.set_xlabel('wavelength [nm]')
        #plt.xlabel("wavelength (nm)")
        plt.show()
    
    return -_I
 
print(cavity(f))
