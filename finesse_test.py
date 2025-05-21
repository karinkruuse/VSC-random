import numpy as np

from pykat import finesse
from pykat.commands import * 

kat = finesse.kat()
code = """
l laser 1 0 n1
s space 1 n1 n2
pd pout n2
xaxis laser P lin 1 10 100
"""
kat.parse(code)
out = kat.run()
out.plot()