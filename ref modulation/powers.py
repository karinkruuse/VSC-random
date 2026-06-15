import numpy as np
import matplotlib.pyplot as plt
import scipy.special as sc


P_0 = 10 #mW

heterodyne_eff = 1
modulation_depth_1 = 0.53
modulation_depth_2 = 0.3

BS_portA = P_0*2 + 2*P_0*heterodyne_eff

# Modulated beam
P_het = 9
P_carrier = sc.jv(0, modulation_depth_1)**2 * P_0
P_SB1 = sc.jv(1, modulation_depth_1)**2 * P_0


