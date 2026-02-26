# simple_asd_scipy.py

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

FNAME = "RefLaserandryanlaserLFN_20260211_184102.npy"
FS = 37.252902985
Y_FIELD = "Input 1 Frequency (Hz)"   # change if needed

# --- load structured array ---
d = np.load(FNAME, allow_pickle=True)
y = d[Y_FIELD].astype(float)

# --- Welch: long segments, small overlap (low averaging) ---
nperseg = min(len(y), 16384*2)     # increase for lower f_min
noverlap = nperseg // 8          # small overlap → less averaging

f, Pxx = welch(
    y,
    fs=FS,
    window="hann",
    nperseg=nperseg,
    noverlap=noverlap,
    detrend="constant",
    return_onesided=True,
    scaling="density",
)

asd = np.sqrt(Pxx)

print(f"N = {len(y)}")
print(f"Segments averaged ≈ {(len(y)-noverlap)//(nperseg-noverlap)}")
print(f"Lowest nonzero frequency ≈ {f[1]:.6g} Hz")

plt.loglog(f[1:], asd[1:])   # skip DC
plt.grid(True, which="both")
plt.xlabel("Frequency [Hz]")
plt.ylabel("ASD [Hz/√Hz]")
plt.title("Frequency Noise ASD (Welch)")
plt.tight_layout()
plt.show()
