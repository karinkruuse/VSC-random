import numpy as np
from scipy.constants import c
import matplotlib.pyplot as plt
"""
spot_size2 = 0.009 
L = 0.3
wl = 1064e-9 
temp = (np.pi*spot_size2**2/(L*wl))**-2
g1 = (1+np.sqrt(1-4*temp))/2
g2 = (1-np.sqrt(1-4*temp))/2

def R(g):
    return L/(1-g)

print("g1: ", g1, "R1: ", R(g1))
print("g2: ", g2, "R2: ", R(g2))

L = 0.26
R2 = 2
gUF = 1-L/R2
spot_size2 = np.sqrt(L*wl/np.pi*np.sqrt(1/(gUF*(1-gUF))))
print("gUF: ", gUF, "spot_size2: ", spot_size2)"""



L = 0.3
R = np.arange(L, 10*L, 0.1)
wl = 1064e-9
g = 1 - L/R

FSR = c / (2 * L) / 1e6

offset1 = 2/np.pi*np.arccos(np.sqrt(g)) * FSR
offset2 = 3/np.pi*np.arccos(np.sqrt(g)) * FSR
offset3 = 4/np.pi*np.arccos(np.sqrt(g)) * FSR
offset4 = 5/np.pi*np.arccos(np.sqrt(g)) * FSR
print(1 - L)
plt.plot(R, offset1, label="TEM01")
plt.plot(R, offset2, label="TEM02")
plt.plot(R, offset3, label="TEM03")
plt.plot(R, offset4, label="TEM04")

plt.vlines(1, 0, 5*FSR, color='gray', linestyle='--', label="L = 0.25 m")
plt.xlabel("Radius of curvature [m]")
plt.ylabel("Higher order mode offset [MHz]")
plt.title("L = 0.33 m")
plt.hlines(FSR, L, 10*L, color='gray', linestyle='--')
plt.hlines(FSR*2, L, 10*L, color='gray', linestyle='--')
plt.hlines(FSR*3, L, 10*L, color='gray', linestyle='--')
plt.legend()
plt.show()

