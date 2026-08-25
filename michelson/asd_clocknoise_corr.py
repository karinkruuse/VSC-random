"""
ASD plots of the carrier-minus-sideband ("carrier - sb") clock observable
for both corr1 and corr2 (eta = carrier, zeta = sideband; see
sync_clocknoise_corr.py's module docstring for the channel maps and the
corr1-external/corr2-internal clock distinction), from the synced
data/no sb/synced_clocknoise_corr.npz.


"""
import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import welch
from scipy.optimize import minimize
from pytdi.dsp import timeshift


plt.rcParams.update({
    "font.family"        : "sans-serif",
    "font.sans-serif"    : ["Helvetica", "Arial", "DejaVu Sans"],
    "mathtext.fontset"   : "custom",
    "mathtext.rm"        : "Helvetica",
    "mathtext.it"        : "Helvetica:italic",
    "mathtext.bf"        : "Helvetica:bold",
    "axes.spines.top"    : True,
    "axes.spines.right"  : True,
    "axes.linewidth"     : 0.8,
    "xtick.direction"    : "in",
    "ytick.direction"    : "in",
    "xtick.major.size"   : 4,
    "ytick.major.size"   : 4,
    "xtick.minor.size"   : 2.5,
    "ytick.minor.size"   : 2.5,
    "xtick.major.width"  : 0.8,
    "ytick.major.width"  : 0.8,
    "xtick.labelsize"    : 15,
    "ytick.labelsize"    : 15,
    "axes.labelsize"     : 13,
    "legend.fontsize"    : 14,
    "legend.framealpha"  : 0.92,
    "legend.edgecolor"   : "#cccccc",
    "legend.handlelength": 2.0,
    "figure.dpi"         : 600,
})


DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "no sb")
NPZ_FILE = os.path.join(DATA_DIR, "synced_clocknoise_corr.npz")
OUT_DIR = os.path.join(os.path.dirname(__file__), "plots", "asd")

REF_FREQ_HZ = 10e6  # SYSREF1/SYSREF2's own demodulation frequency
TARGET_FREQ_HZ = 15e6  # eta12/eta21's demodulation frequency -- what the
# correction is rescaled onto before being subtracted from them

FMIN_PLOT = 1e-3 # Hz -- lowest frequency shown/used for nperseg sizing
BAND_LO, BAND_HI = 1e-3, 1.0  # Hz -- band used for the printed RMS/suppression numbers

delay1 = 8.14895613  # seed / fallback -- refined below by minimizing the "board
delay2 = 8.21742184  
FIT_DELAY = False
DELAY_SEARCH_HALFWIDTH = 0.5  # s, search window around the seed above

def welch_asd(x, fs, fmin=FMIN_PLOT):
    nperseg = min(int(fs / fmin), len(x))
    f, psd = welch(x, fs=fs, nperseg=nperseg)
    return f, np.sqrt(psd)


def band_rms(f, asd, lo=BAND_LO, hi=BAND_HI):
    m = (f >= lo) & (f <= hi)
    return np.sqrt(np.trapezoid(asd[m] ** 2, f[m]))


data = np.load(NPZ_FILE)

t = data["time_s"]
fs = 1.0 / np.median(np.diff(t))
print(f"{os.path.basename(NPZ_FILE)}: N = {len(t)}, fs = {fs:.4f} Hz, "
      f"duration = {(t[-1] - t[0]) / 3600:.2f} h")



color_extrapolated = "#d71b2f"   # (215, 27, 47)  red
color_measured     = "#295f24"   # (41, 95, 36)   green
color_modulator    = "#821770"   # (130, 23, 112) magenta
color_delayline    = "#2d13b4"   # (45, 19, 180)  blue

colors = [color_extrapolated, color_measured, color_modulator]

# reference-channel clock-noise corrections, from corr1's SYSREF1/SYSREF2
corrections = {
    "SYSREF1": data["corr1_SYSREF1"] / REF_FREQ_HZ * TARGET_FREQ_HZ,
    "SYSREF2": data["corr1_SYSREF2"] / REF_FREQ_HZ * TARGET_FREQ_HZ,
}

#- timeshift(data["corr1_SYSREF2"] *1.5, -fs*delay)
#- timeshift(data["corr1_SYSREF1"] *1.5, -fs*delay)


def board_jitter_residual(delay_val1, delay_val2):
    """cc3c - r3c (the "board jitter correction" trace) for a trial delay."""
    eta12c = data["corr1_eta12"] - timeshift(corrections["SYSREF1"], -fs*delay_val1)
    eta21c = data["corr2_eta21"] - timeshift(corrections["SYSREF2"], -fs*delay_val2)
    r2 = (data["corr2_zeta_U_21"]-data["corr2_eta21"])/2e6*data["corr2_eta21_freq"]
    r3c = r2 + timeshift(corrections["SYSREF2"], -fs*delay_val2) - corrections["SYSREF2"]
    return (eta21c - eta12c) - r3c


def delay_cost(delays):
    delay_val1, delay_val2 = delays
    f, asd = welch_asd(board_jitter_residual(delay_val1, delay_val2), fs)
    return band_rms(f, asd)


if FIT_DELAY:
    _result = minimize(delay_cost, x0=[delay1, delay2], method="Nelder-Mead",
                        options={"xatol": 1e-9, "fatol": 1e-12})
    print(_result.x)
    delay1, delay2 = _result.x

cc2 = (data["corr2_eta21"] ) - timeshift(data["corr1_eta12"], -fs*delay2)
r2 = (data["corr2_zeta_U_21"]-data["corr2_eta21"])/2e6*data["corr2_eta21_freq"]

cc = (data["corr1_eta12"] ) - timeshift(data["corr2_eta21"], -fs*delay1)
r1 = -(data["corr1_zeta_U_12"]-data["corr1_zeta_L_12"])/1e6*data["corr1_eta12_freq"]


r2c = r2 + timeshift(corrections["SYSREF2"], -fs*delay2) - corrections["SYSREF2"]
r1c = r1 - timeshift(corrections["SYSREF1"], -fs*delay1) + corrections["SYSREF1"]


eta12c = data["corr1_eta12"] + timeshift(corrections["SYSREF1"], -fs*delay1)
eta21c = data["corr2_eta21"] + timeshift(corrections["SYSREF2"], -fs*delay2)

cc2c = (eta21c) - timeshift(eta12c, -fs*delay1)
cc1c = (eta12c) - timeshift(eta21c, -fs*delay1)

cc3 = (data["corr2_eta21"] ) - data["corr1_eta12"]
r3 = (data["corr2_zeta_U_21"]-data["corr2_eta21"])/2e6*15e6

cc3_swap = (data["corr1_eta12"] ) - data["corr2_eta21"]
r3_swap = (data["corr1_zeta_U_12"]-data["corr1_eta12"])/1e6*15e6

# assume q_1 = 0
cc3c = eta21c - eta12c
r3c = r3 + timeshift(corrections["SYSREF2"], -fs*delay2) - corrections["SYSREF2"]

carrier_minus_carrier = {
   # "cc1 - r1": cc - r1,
   # "r1 - r2": [eta12c + timeshift(eta21c, -fs*delay1), "black"]  ,
   # "r1-r2": r1 +timeshift(r2, -fs*delay)  ,
    "$\eta_{12} - \eta_{21}$" : [cc3, color_extrapolated],
    "sideband correction" : [cc3 -r2, color_measured] ,
    "board jitter correction" : [cc3c -r3c, color_modulator],
    "cc1- r14": [(cc1c - r1c), "black" ], #-(cc1c - r1c) limits
}



baseline_ref = np.loadtxt(os.path.join('..', 'measured noises', 'baseline.csv'), delimiter=',', skiprows=1)

os.makedirs(OUT_DIR, exist_ok=True)

fig1, ax1 = plt.subplots(figsize=(9, 6))
for label, x in carrier_minus_carrier.items():
    f, asd = welch_asd(x[0], fs)
    ax1.loglog(f[1:], asd[1:], lw=0.9, label=label, color=x[1])
    print(f"{label}: band RMS [{BAND_LO}, {BAND_HI}] Hz = {band_rms(f, asd):.3e} cyc")

ax1.loglog(baseline_ref[:, 0], np.sqrt(3)*baseline_ref[:, 1], lw=1.5, label='2-board baseline', color='k', alpha=0.3)
ax1.set_xlabel("Frequency (Hz)")
ax1.set_ylabel("ASD (cyc/√Hz)")
#ax1.set_title("carrier_minus_carrier (uncorrected)")
ax1.grid(True, which="both", ls="--", alpha=0.4)
plt.legend( fontsize=12, frameon=True, fancybox=False)
ax1.set_xlim(FMIN_PLOT, 10)
fig1.tight_layout()
out1 = os.path.join(OUT_DIR, "asd_carrier_minus_sb_raw.png")
fig1.savefig(out1)
print(f"saved {out1}")
