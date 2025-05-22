import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import c
from scipy.interpolate import interp1d

from pykat import finesse
from pykat.commands import * 
from simple_finesse_wrapper import FinesseGenerator

from laser_noise_PSD import LaserFrequencyNoisePSD


kat = finesse.kat()
code = FinesseGenerator()

f_mod = 10e6
print("f_mod: ", np.round(f_mod/1e6), "MHz")
R = np.round(0.99986**2, 5)
T = np.round(1 - R, 5) # otherwise it is 0.00014000000029
L = 0.26

FSR = c / (2 * L) 
F = np.pi * np.sqrt(R) / (1 - R)
linewidth = FSR/F
print("FSR: ", np.round(FSR/1e6, 2) , "MHz")
print("linewidth: ", np.round(linewidth/1e3, 2), "kHz")
print("Finesse: ", np.round(F, 2))

code.laser("L1", 0.25, "n0")
code.space("s0", 1, "n0", "n1")
code.modulator("EOM", f_mod, 0.15, 5, "pm", "n1", "n2")          
code.space("s1", 1, "n2", "n3")   

# Inject signals here for delta L noise
code.mirror("M1", R, T, 0, "n3", "n4")
code.space("s_cav", L, "n4", "n5")
code.mirror("M2", R, T, 0, "n5", "n6")

code.photodiode("PDinphase", freqs=[f_mod], phases=[180], nodes=["n3"])                                  

#code.photodiode("quadrature", freqs=[f_mod], phases=[pha+180], nodes=["n3"])                           
#code.photodiode("though",nodes=["n6"])         

x_scaling = 0.01
code.xaxis("L1", "f", "lin", -f_mod*x_scaling, f_mod*x_scaling, 50000)
code.yaxis("abs")                 

code.save("error_signal.kat")	
kat.parse(code.get_lines())
out = kat.run()

wl = 1064e-9
actual_L = (0.26 // wl) * wl
f0 = c / wl

frequencies = f0 + out.x                # in Hz or offset units
error_signal = out["PDinphase"]    # assuming complex, just use real part


mask = (frequencies >= (f0-linewidth/2)) & (frequencies <= (f0+linewidth/2))
x_range = frequencies[mask]
y_range = error_signal[mask]
dy_dx = np.gradient(y_range, x_range)
# error_interp = interp1d(frequencies, error_signal, kind='cubic', bounds_error=False, fill_value="extrapolate")

fig, ax1 = plt.subplots()
ax1.plot(frequencies, error_signal.real, label="Error Signal")
ax2 = ax1.twinx()
ax2.plot(x_range, dy_dx, color='red', linestyle='--', label='Derivative')
ax1.axvspan(f0-linewidth/2, f0+linewidth/2, color='gray', alpha=0.3, label='shaded area')
plt.grid()
plt.show()

"""
plt.loglog(f, np.sqrt(Pxx))
plt.xlabel("Frequency [Hz]")
plt.ylabel("ASD [Hz/√Hz]")
plt.title("Laser Frequency Noise (1/f)")
plt.grid(True, which="both")
plt.show()
"""