import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.constants import c


if True:
    wavelength = 1064*10**-9
    frequency = c / wavelength
    dT = 1 / frequency / 2.5 * 80000
    nr_cyc = 50000000000
    f_mod = 2.4*10**9
    mod_depth1 = 0.15
    mod_depth2 = 0.15
    t = np.arange(0, nr_cyc * 2 * np.pi / frequency, dT)
    LO = mod_depth2 * np.cos(2 * np.pi * (f_mod + 10**6) * t)

    #noise = 10 * np.random.normal(0, 0.1, len(t))
    carrier_diff = 10**7
    beatnote = np.cos(2 * np.pi * frequency * t + mod_depth1*np.cos(2 * np.pi * f_mod * t) - (2 * np.pi * (frequency + carrier_diff) * t + LO))

    N = len(t)
    L_mod_fft = fft(beatnote)[1:N//2] * 2 / N
    freqs = fftfreq(len(t), dT)[1:N//2]

    fig, ax = plt.subplots(2, figsize=(10,12))
    ax[0].plot(freqs, np.real(L_mod_fft), color="r")
    ax[1].plot(freqs/10**6, np.real(L_mod_fft), color="r")

    ax[1].set_xlim(0, 15)

    ax[0].set_xlabel("Frequency (Hz)")
    ax[1].set_xlabel("Frequency (MHz)")
    ax[0].set_ylabel("Amplitude")
    ax[0].grid()
    ax[1].grid()
    plt.savefig("LO_mod.png", transparent=False, dpi=300)

# v_receiver is added to c if the receiver is moving towards the source
# v_emitter is added to c if the source is moving away from the receiver
def doppler_shift(f0, v_emitter=-5, v_receiver=5):
    return (c+v_receiver)/(c+v_emitter)*f0

if False:
    wl = 1064*10**-9
    clk = 2.401*10**9
    f_carrier = c/wl
    print(np.round((doppler_shift(f_carrier)-f_carrier)*10**-6, 3), "MHz")