import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import c
from scipy.interpolate import interp1d

from pykat import finesse
from pykat.commands import * 
from simple_finesse_wrapper import FinesseGenerator

from laser_noise_PSD import LaserFrequencyNoisePSD


code = FinesseGenerator()

f_mod = 10e6
print("f_mod: ", np.round(f_mod/1e6), "MHz")
R = np.round(0.99986**2, 5)
T = np.round(1 - R, 5) # otherwise it is 0.00014000000029

RoC = 0.5

wl = 1064e-9
f0 = c / wl

fig, ax1 = plt.subplots()

colors = ['gray', 'navy', 'green', 'red', 'purple']
Ls = [0.26]#, 0.33
for i in range(2):
    L = Ls[i]

    FSR = c / (2 * L) 
    F = np.pi * np.sqrt(R) / (1 - R)
    linewidth = FSR/F

    code.laser("L1", 0.25, "n0")
    code.space("s0", 1, "n0", "n1")
    code.modulator("EOM", f_mod, 1.08, 5, "pm", "n1", "n2")          
    code.space("s1", 1, "n2", "n3")   

    code.mirror("M1", R, T, 0, "n3", "n4")
    code.space("s_cav", L, "n4", "n5")
    code.mirror("M2", R, T, 0, "n5", "n6")

    code.photodiode("PDinphase", freqs=[f_mod], phases=[90], nodes=["n3"])                                        

    x_scaling = 0.01
    code.xaxis("L1", "f", "lin", -f_mod*x_scaling, f_mod*x_scaling, 50000)
    code.yaxis("abs")                 

    code.save("error_signal.kat")	
    kat = finesse.kat() 
    kat.parse(code.get_lines())
    out = kat.run()
    code.clean_lines()

    frequencies = out.x                # in Hz or offset units 
    error_signal = out["PDinphase"]    # assuming complex, just use real part
    ax1.plot(frequencies, error_signal.real, label="Error Signal, L: " + str(L) + " m", color=colors[i])

    print("FSR: ", np.round(FSR/1e6, 2) , "MHz")
    print("linewidth: ", np.round(linewidth/1e3, 2), "kHz")
    print("Finesse: ", np.round(F, 2))
    ax1.axvspan(-linewidth/2, linewidth/2, color=colors[i], alpha=0.3)

plt.grid()
plt.legend()
plt.show()

"""
plt.loglog(f, np.sqrt(Pxx))
plt.xlabel("Frequency [Hz]")
plt.ylabel("ASD [Hz/√Hz]")
plt.title("Laser Frequency Noise (1/f)")
plt.grid(True, which="both")
plt.show()
"""