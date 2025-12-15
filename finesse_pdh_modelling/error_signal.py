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

colors = ['gray', 'navy', 'maroon', 'red', 'purple']
Ls = [0.25, 0.3] #
for i in range(2):
    L = Ls[i]

    FSR = c / (2 * L) 
    F = np.pi * np.sqrt(R) / (1 - R)
    linewidth = FSR/F

    g = 1 - L/RoC
    omega_0 = np.sqrt(L*wl/np.pi*np.sqrt(g/(1-g)))
    print("beam waist radius at the first mirror:", np.round((omega_0)*1e3, 4), "mm")

    code.laser("L1", 0.25, "n0")
    code.space("s0", 1, "n0", "n1")
    code.modulator("EOM", f_mod, 1.08, 5, "pm", "n1", "n2")          
    code.space("s1", 1, "n2", "n3")   

    code.mirror("M1", R, T, 0, "n3", "n4")
    #code.gauss("beam1", "L1", "n0", omega_0, 0)
    code.space("s_cav", L, "n4", "n5")
    code.mirror("M2", R, T, 0, "n5", "n6")
    
    code.attr("M2", "Rc", RoC) # set the radius of curvature for M2
    code.cav("cavity1", "M1", "n4", "M2", "n5") # compute cavity eigenmodes
    code.maxtem(3)

    code.photodiode("reflected", freqs=[f_mod], phases=[90], nodes=["n3"])         
    code.photodiode("reflected2", freqs=[f_mod], phases=[0], nodes=["n3"])                                        
    code.photodiode("transmitted", freqs=[f_mod], phases=[0], nodes=["n4"])

    x_scaling = 0.01
    code.xaxis("L1", "f", "lin", -f_mod*x_scaling, f_mod*x_scaling, 5000)
    code.yaxis("abs")                 

    code.save("error_signal.kat")	
    kat = finesse.kat() 
    kat.parse(code.get_lines())
    out = kat.run()
    code.clean_lines()

    frequencies = out.x                # in Hz or offset units 
    error_signal = out["reflected"]    # assuming complex, just use real part
    error_signal2 = out["reflected2"]    # assuming complex, just use real part
    transmitted = out["transmitted"]    # assuming complex, just use real part
    ax1.plot(frequencies/1e3, error_signal.real, label="Error Signal, L: " + str(L) + " m", color=colors[i])
    #ax1.plot(frequencies/1e3, error_signal2.real, label="Error Signa, inphase, L: " + str(L) + " m", color=colors[i])
    #ax1.plot(frequencies, transmitted.real, label="Transmitted stuff, L: " + str(L) + " m", color=colors[1])

    print("FSR: ", np.round(FSR/1e6, 2) , "MHz")
    print("linewidth: ", np.round(linewidth/1e3, 2), "kHz")
    print("Finesse: ", np.round(F, 2))
    ax1.axvspan(-linewidth/2e3, linewidth/2e3, color=colors[i], alpha=0.3)

plt.grid()
plt.xlabel("Frequency offset [kHz]")
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