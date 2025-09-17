import numpy as np
from pykat import finesse
from pykat.commands import * 
from simple_finesse_wrapper import FinesseGenerator

np.seterr(divide='ignore')

kat = finesse.kat()
code = """
####################################################
# misalignment_resonance_single.kat
####################################################

l L1 0.25 0 n0
s s0 1 1 n0 n1

mod EOM 10M 1.08 5 pm n1 n2
s s1 1 1 n2 n3

m M1 0.99972 0.00028 0 n3 n4
s s_cav 0.30 1 n4 n5
m M2 0.99972 0.00028 0 n5 n6
attr M2 Rc 0.5
attr M2 xbeta 40u    # <<--- set tilt angle here

cav cavity1 M1 n4 M2 n5

maxtem 5

pd trans_dc n6
pd refl_dc n3

xaxis L1 f lin -450M 450M 4000
yaxis abs


"""
kat.parse(code)
out = kat.run()
out.plot()
