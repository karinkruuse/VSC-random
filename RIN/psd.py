#!/usr/bin/env python3
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import welch

# ========== USER CONFIG ==========
file_path = r"data\Reflaser_20251215_140350.csv"  # single CSV with Input1=PD, Input2=ADC
gain_db = 0           # PDA100A2 setting (0,10,20,30,40,50,60,70)
load_is_50_ohm = True  # True if DAQ is 50 Ω (Moku etc.)
welch_nperseg = None   # None => auto
welch_noverlap = None  # None => 50%
welch_window  = "hann"
# =================================

Q_E = 1.602176634e-19  # C

# PDA100A2 transimpedance gains (V/A) — into 50 Ω and Hi-Z
GAIN_50 = {0:0.75e3,10:2.38e3,20:0.75e4,30:2.38e4,40:0.75e5,50:2.38e5,60:0.75e6,70:2.38e6}
GAIN_HZ = {0:1.51e3,10:4.75e3,20:1.5e4,30:4.75e4,40:1.51e5,50:4.75e5,60:1.5e6,70:4.75e6}

def parse_fs(path):
    fs = None
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.startswith("#"):
                break
            m = re.search(r"Acquisition rate:\s*([0-9eE+\-\.]+)\s*Hz", line)
            if m:
                fs = float(m.group(1)); break
    if fs is None:
        raise ValueError("Sampling rate not found in header.")
    return fs

def read_moku_csv(path):
    df = pd.read_csv(path, comment="#", header=None,
                     names=["Time_s","Input1_V","Input2_V"])
    return df.dropna(how="all")

def auto_welch(n):
    nper = min(max(256, n//8), 2**16)
    return nper, nper//2

def psd(series, fs, nperseg, noverlap, window):
    f, Pvv = welch(np.asarray(series,float), fs=fs, window=window,
                   nperseg=nperseg, noverlap=noverlap,
                   detrend="constant", return_onesided=True, scaling="density")
    return f, Pvv  # V^2/Hz

def asd(Pxx): return np.sqrt(np.maximum(Pxx, 0.0))  # V/√Hz

# ---- load & setup
fs = parse_fs(file_path)
df = read_moku_csv(file_path)
v1 = df["Input1_V"].to_numpy()  # photodiode (laser)
v2 = df["Input2_V"].to_numpy()  # ADC noise (terminated)
Vdc = float(np.mean(v1))
if Vdc == 0:
    raise RuntimeError("Input1 DC is zero; can’t normalize RIN.")

if welch_nperseg is None or welch_noverlap is None:
    welch_nperseg, welch_noverlap = auto_welch(len(v1))

G = (GAIN_50 if load_is_50_ohm else GAIN_HZ)[gain_db]  # V/A

# ---- PSD/ASD
f, Pvv1 = psd(v1, fs, welch_nperseg, welch_noverlap, welch_window)
_, Pvv2 = psd(v2, fs, welch_nperseg, welch_noverlap, welch_window)
ASD1 = asd(Pvv1)   # V/√Hz (laser)
ASD2 = asd(Pvv2)   # V/√Hz (ADC)

# ---- Instrument-space plot
plt.figure()
plt.loglog(f, ASD1, label="Input 1: PD (laser)")
plt.loglog(f, ASD2, label="Input 2: ADC")
plt.xlabel("Frequency (Hz)")
plt.ylabel("ASD (V/√Hz)")
plt.title("Instrument ASD")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()
plt.show()

# ---- Normalize to RIN ASD (1/√Hz) using laser DC (Input1 mean)
RIN_raw  = ASD1 / abs(Vdc)  # 1/√Hz
RIN_adc  = ASD2 / abs(Vdc)  # 1/√Hz (same normalization so subtraction is legit)

# ---- Shot-noise RIN (1/√Hz) and voltage ASD (for info)
RIN_shot = np.sqrt(2 * Q_E * G / abs(Vdc))      # 1/√Hz
Vshot    = np.sqrt(2 * Q_E * abs(Vdc) * G)      # V/√Hz
print(f"fs = {fs:.6g} Hz, gain G = {G:.3e} V/A, Vdc = {Vdc:.6g} V")
print(f"Shot noise: {Vshot*1e9:.2f} nV/√Hz (voltage),  {RIN_shot:.3e} 1/√Hz (RIN)")

"""# ---- Quadrature subtraction to estimate laser-only RIN
RIN_corr = np.sqrt(np.maximum(RIN_raw**2 - RIN_adc**2 - RIN_shot**2, 0.0))

# ---- RIN plot
plt.figure()
plt.semilogx(f[2:], RIN_raw[2:],  alpha=0.5, label="RIN (raw from PD)")
plt.semilogx(f[2:], RIN_adc[2:],  alpha=0.7, label="ADC (normalized)")
plt.axhline(RIN_shot, linestyle="--", label="Shot noise (RIN)")
plt.semilogx(f[2:], RIN_corr[2:], linewidth=2.0, label="RIN (corrected: raw ⊖ ADC ⊖ shot)")
plt.xlabel("Frequency (Hz)")
plt.ylabel("RIN ASD (1/√Hz)")
plt.title("Relative Intensity Noise")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()
plt.show()
"""
