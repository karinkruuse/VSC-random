import numpy as np
from scipy.fft import fft, ifft, fftfreq
from scipy.constants import c
import matplotlib.pyplot as plt

from elements.cavity import OpticalCavity

np.seterr(divide='ignore')


#cavity1 = OpticalCavity("Reference cavity", L=0.24, radius2=1)
#cavityR = OpticalCavity("Laser1 cavity", linewidth=60e3, L=0.21, radius2=3)



from pykat import finesse
from pykat.commands import * 

kat = finesse.kat()

with open("finesse_txt/pdh-signal.kat", "r") as f:
    code = f.read()

kat.parse(code)
out = kat.run()

out.plot()
