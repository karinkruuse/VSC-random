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

L1 = 0.23114
LR = 0.25908

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
# Monte Carlo analysis of length sensitivity
np.random.seed(0)
N = 1000  # Number of random trials
scaling = 1.2

L1_center = 0.23114 * scaling
LR_center = 0.25908 * scaling
print("L1", L1_center, "LR", LR_center)
FSR1 = fsr(L1_center)
FSRR = fsr(LR_center)

print("FSR1: ", FSR1/1e6, "MHz")
print("FSRR: ", FSRR/1e6, "MHz")

L1_samples = np.random.normal(loc=L1_center, scale=0.00001, size=N)
LR_samples = np.random.normal(loc=LR_center, scale=0.00001, size=N)

print(np.std(L1_samples)*1000, "mm, L1 std")
print(np.std(LR_samples)*1000, "mm, LR std")

good_counts = []

for L1_test, LR_test in zip(L1_samples, LR_samples):
    FSR1 = fsr(L1_test)
    FSRR = fsr(LR_test)
    m1 = int(np.round(f0 / FSR1))
    mr = int(np.round(f0 / FSRR))
    off1 = np.ceil(therm_tuning_range // FSR1)
    offR = np.ceil(therm_tuning_range // FSRR)

    f1_peaks = FSR1 * np.arange(m1 - off1, m1 + off1 + 1)
    fr_peaks = FSRR * np.arange(mr - offR, mr + offR + 1)

    count = 0
    for f in f1_peaks:
        idx = np.searchsorted(fr_peaks, f)
        idxs = []
        if idx > 0: idxs.append(idx - 1)
        if idx < len(fr_peaks): idxs.append(idx)
        for i in idxs:
            diff = abs(f - fr_peaks[i]) / 1e6  # MHz
            if 25 <= diff <= 60:
                count += 1
    good_counts.append(count)

"""
fig, axs = plt.subplots(1, 2, figsize=(12, 4))

axs[0].hist(L1_samples * 1e3, bins=40, color='maroon', edgecolor='black')
axs[0].set_title("Distribution of L1 Samples")
axs[0].set_xlabel("L1 (mm)")
axs[0].set_ylabel("Count")
axs[0].grid()

axs[1].hist(LR_samples * 1e3, bins=40, color='gray', edgecolor='black')
axs[1].set_title("Distribution of LR Samples")
axs[1].set_xlabel("LR (mm)")
axs[1].set_ylabel("Count")
axs[1].grid()

plt.tight_layout()
plt.show()
"""
bb = max(good_counts)
plt.hist(good_counts, bins=np.arange(bb+1)-0.5, edgecolor='black')
plt.xticks(range(10))
plt.xlim([-1, 10])
plt.xlabel("Number of usable beatnotes (25–60 MHz) in laser tuning range")
plt.ylabel("Number of suitable peak pairs")
plt.title("Number of length pairs: " +  str(N) + ", length std: "+ str(np.round(np.std(L1_samples)*1000, 4)) + "mm")
plt.savefig("Histogram 1-3x UF lengths.png", dpi=350)