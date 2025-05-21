import numpy as np
from pykat import finesse
from pykat.commands import * 
from simple_finesse_wrapper import FinesseGenerator

np.seterr(divide='ignore')

kat = finesse.kat()
code = """
l i1 1 0 n0                 
s s0 1 n0 n1
mod eo1 20M 0.3 3 pm n1 n2  
                            
s s1 1 n2 n3
                            
m m1 0.99986 0.00014 0 n3 n4     
s s_cav 0.26 n4 n5          
m m2 0.99986 0.00014 0 n5 dump         

pd1 inphase 20M 0 n3       
                            
pd1 quadrature 20M 90 n3    
xaxis m2 phi lin -20 20 400 
                           
yaxis abs    
"""
kat.parse(code)
out = kat.run()
out.plot()
