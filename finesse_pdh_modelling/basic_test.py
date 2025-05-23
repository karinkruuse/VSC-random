import numpy as np
from pykat import finesse
from pykat.commands import * 
from simple_finesse_wrapper import FinesseGenerator

np.seterr(divide='ignore')

kat = finesse.kat()
code = """
l i1 1 0 n0                 # laser P=1W f_offset=0Hz
s s0 1 n0 n1
mod eo1 40k 0.3 3 pm n1 n2  # phase modulator f_mod=40kHz
                            # midx=0.3 order=3 
s s1 1 n2 n3
                            # a Fabry-Perot cavity
m m1 0.9 0.0001 0 n3 n4     # mirror R=0.9 T=0.0001 phi=0
s s_cav 1200 n4 n5          # space L=1200
m m2 0.9 0.1 0 n5 n6        # mirror R=0.8 T=0.1 phi=0
attr m2 Rc 1400             # ROC for m2 = 1400m

cav cavity1 m1 n4 m2 n5     # compute cavity eigenmodes
maxtem 3                    # TEM modes up to n+m=3
time                        # print computation time


pd1 pdh 40k 0 n3                # diode for PDH signal
xaxis i1 f lin -100000.0 100000.0 50000     # tune the angle of m2 

yaxis abs    
"""
kat.parse(code)
out = kat.run()
out.plot()
