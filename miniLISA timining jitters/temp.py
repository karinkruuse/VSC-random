import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch, detrend
from scipy.interpolate import interp1d
from pytdi.dsp import timeshift

# =====================================
# Settings
# =====================================
file_path = r"C:\Users\Avishkar\OneDrive\Desktop\Mini-LISA\Data Delay line\DownstairsTest_20260423_170536.npy"
tau = 4.0  # exact delay in seconds

# =====================================
# Load data
# =====================================
data = np.load(file_path, allow_pickle=True)

time = data['Time (s)']

# Channel mapping
ch1_phase = data['Input 1 Phase (cyc)']   # delayed signal
ch2_phase  = data['Input 2 Phase (cyc)']   # pilot tone / DDS
ch3_phase = data['Input 3 Phase (cyc)']   # undelayed signal

w_s = 2 * np.pi * data['Input 1 Frequency (Hz)']   # angular frequency of input 1
w_d = 2 * np.pi * data['Input 2 Frequency (Hz)']   # angular frequency of input 2

# =====================================
# Unwrap phase and Detrend
# =====================================
ch1_phase = np.unwrap(ch1_phase, period=1.0)
ch2_phase = np.unwrap(ch2_phase, period=1.0)
ch3_phase = np.unwrap(ch3_phase, period=1.0)

ch1_phase = detrend(ch1_phase, type='linear')
ch2_phase = detrend(ch2_phase, type='linear')
ch3_phase = detrend(ch3_phase, type='linear')

# Sampling frequency from time array
fs = 37.252902985

# Delay in samples
shift_samples = -tau * fs   # negative for delay

ratio = w_s / w_d

delayed_ch3 = timeshift(ch3_phase, shift_samples, order=31)
delayed_ratio_ch2 = timeshift(ratio * ch2_phase, shift_samples, order=31)
delayed_ch2 = timeshift(ch2_phase, shift_samples, order=31)

Corrected_data = ch1_phase - delayed_ch3 - delayed_ratio_ch2 - ratio * ch2_phase

Corrected_data2 = ch1_phase - delayed_ch3 - (ratio* ch2_phase - delayed_ratio_ch2)


# Compute PSD for each channel
f, PSD_ch1 = welch(ch1_phase, fs, nperseg=2**16)
f, PSD_ch2 = welch(ch2_phase, fs, nperseg=2**16)
f, PSD_corrected = welch(Corrected_data, fs, nperseg=2**16)
f, PSD_corrected2 = welch(Corrected_data2, fs, nperseg=2**16)

# Compute ASD by taking square root of PSD
ASD_ch1 = np.sqrt(PSD_ch1)
ASD_ch2 = np.sqrt(PSD_ch2)
ASD_corrected = np.sqrt(PSD_corrected)
ASD_corrected2 = np.sqrt(PSD_corrected2)

# Plotting
plt.figure(figsize=(10, 6))
plt.loglog(f, ASD_ch1, label='Input 1 Phase (Delayed)')
plt.loglog(f, ASD_ch2, label='Input 2 Phase (DDS / Pilot Tone)')
plt.loglog(f, ASD_corrected, label='Corrected Data')
plt.loglog(f, ASD_corrected2, label='Corrected Data Original')
plt.xlabel('Frequency [Hz]')
plt.ylabel('ASD [cycles/√Hz]')
plt.legend()
plt.grid(True, which="both", ls="--")
plt.show()