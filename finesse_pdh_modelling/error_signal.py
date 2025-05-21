import numpy as np
from scipy.constants import c


from pykat import finesse
from pykat.commands import * 
from simple_finesse_wrapper import FinesseGenerator


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

code.mirror("M1", R, T, 0, "n3", "n4")
code.space("s_cav", L, "n4", "n5")
code.mirror("M2", R, T, 0, "n5", "n6")

phase_shifts = np.arange(0, 90, 10)
for p in phase_shifts:
    code.photodiode("deg" + str(p), freqs=[f_mod], phases=[p], nodes=["n3"])                                  

#code.photodiode("quadrature", freqs=[f_mod], phases=[pha+180], nodes=["n3"])                           
#code.photodiode("though",nodes=["n6"])         

x_scaling = 0.05
code.xaxis("L1", "f", "lin", -f_mod*x_scaling, f_mod*x_scaling, 50000)
code.yaxis("abs")                 

code.save("error_signal.kat")	
kat.parse(code.get_lines())
out = kat.run()

out.plot()