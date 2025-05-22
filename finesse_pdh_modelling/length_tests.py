import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import c
from scipy.signal import find_peaks



p = 2 * np.pi

wl = 1064e-9
f0 = c / wl

R = 0.9995 
r = np.sqrt(R)

def reflection_coef(f, L):
    ex = np.exp(-1j * 2 * L * p / c * f)
    return -r * (ex - 1) / (1 - R * ex)

def g(L, R):
    return 1- L/R

def fsr(L):
    return c / (2 * L)  # FSR in Hz

therm_tuning_range = 6e9
fmin = f0 - therm_tuning_range
fmax = f0 + therm_tuning_range
f_range = np.linspace(fmin, fmax, 1000000)
scaling = 1
L1 = 0.23114 * scaling
LR = 0.25908 * scaling

print("L1", L1, "LR", LR)

R1 = np.abs(reflection_coef(f_range, L1))
R2 = np.abs(reflection_coef(f_range, LR))

FSR1 = fsr(L1)
FSRR = fsr(LR)


m1 = int(np.round(f0 / FSR1))
mr = int(np.round(f0 / FSRR))
print("mode nr L1", m1, "gives us wavelength",  c/(FSR1 * m1))
print("mode nr LR", mr, "gives us wavelength",  c/(FSRR * mr))


off1 = therm_tuning_range // FSR1
offR = therm_tuning_range // FSRR

f1_peaks = FSR1 * np.arange(m1 - off1, (m1+1) + off1)
fr_peaks = FSRR * np.arange(mr - offR, (mr+1) + offR)

# For each f in f1_peaks, find the two closest fr_peaks and store the diffs
peak_diffs = []
count = 0
for f in f1_peaks:
    idx = np.searchsorted(fr_peaks, f)
    
    idxs = []
    if idx > 0:
        idxs.append(idx - 1)
    if idx < len(fr_peaks):
        idxs.append(idx)
    
    for i in idxs:
        diff = abs(f - fr_peaks[i])/ 1e6
        peak_diffs.append(diff)  # Convert to MHz

        if diff > 25 and diff < 60:
            print("L1 peak", (f-f0)/1e6, "is close to LR peak", (fr_peaks[i]-f0)/1e6, "with diff", diff, "MHz")
            count += 1

plt.figure(figsize=(14, 8))
# Plot reflection spectra
plt.plot((f_range - f0) * 1e-6, R1, label=r"Laser1 cavity $L_1$ = " + str(np.round(L1*1000, 2)) + " mm", color="maroon")
plt.plot((f_range - f0) * 1e-6, R2, label=r"Reference laser cavity $L_R$ = " + str(LR*1000) + " mm", color="grey", alpha=0.8)

# Overlay analytical peak positions
for f in f1_peaks:
    #plt.axvline((f - f0) * 1e-6, color='maroon', linestyle='--', alpha=0.3)
    f_offset = (f - f0) * 1e-6 
    plt.axvspan(f_offset + 25, f_offset + 60, color='maroon', alpha=0.1)
    plt.axvspan(f_offset - 60, f_offset - 25, color='maroon', alpha=0.1)

for f in fr_peaks:
    plt.axvline((f - f0) * 1e-6, color='grey', linestyle='--', alpha=0.3)

plt.xlabel("Frequency offset from 1064 nm (MHz)")
plt.ylabel("Cavity Reflection Coefficient")
plt.legend()
plt.ylim(0, 1.005)
plt.grid()
plt.savefig("UF cavity lengths.png", dpi=350)

"""
# Histogram
plt.hist(peak_diffs, bins=200, edgecolor='black')
plt.xlabel("Possible Beatnote (MHz)")
plt.ylabel("Count in the tuning range: ±" + str(therm_tuning_range/1e9) + " GHz")
plt.axvspan(25, 60, color='grey', alpha=0.5, label="Target range")
plt.title("Closest Peak Distances between L1 and LR")
plt.grid()
plt.show()
"""