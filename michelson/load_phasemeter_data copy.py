"""
Single-phasemeter TDI: 4 carriers (c12, c13, c21, c31) on ONE Moku, so one
clock, no sync, no sidebands.  TDI's only job is to null the common laser.

This fits the four Michelson delays INDEPENDENTLY (non-reciprocal) by
minimising the Welch-band RMS of X1, with a train/test split so we know the
delays are real physical legs and not four knobs fitting noise.

Channel map (from the Moku header "% c12, c13, c21, c31, REF1..3"):
    Input 1 -> c12    Input 2 -> c13    Input 3 -> c21    Input 4 -> c31
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch, detrend
from scipy.signal import welch, csd
from scipy.optimize import minimize

from pytdi.dsp import timeshift
from pytdi.michelson import X1_ETA



# ---------------------------------------------------------------- config
FILENAME     = "NOISY_NO_RANGING_20260821_132220"
DATA_DIR     = os.path.join(os.path.dirname(__file__), "data/no sb")

FMIN, FMAX   = 1e-4, 2                # band for the fit AND the metric
FIT_DELAYS   = True                      # False -> use DELAYS_START directly
DELAYS_START = [8, 8, 8, 8]      # optimiser seed (d12, d21, d13, d31) [s]
EDGE_CROP    = 1500                      # samples dropped each end
CROP_FRACTION = 0.15

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
    "legend.fontsize"    : 10,
    "legend.framealpha"  : 0.92,
    "legend.edgecolor"   : "#cccccc",
    "legend.handlelength": 2.0,
    "figure.dpi"         : 600,
})


# ---------------------------------------------------------------- load
data = np.load(os.path.join(DATA_DIR, f"{FILENAME}.npy"))

M = 0
def crop_data(data, fraction):
    """Keep only the first `fraction` of the record (0-1], from the start."""
    n_keep = int(round(len(data) * fraction))
    return data[M:n_keep]

if CROP_FRACTION < 1.0:
    data = crop_data(data, CROP_FRACTION)

t  = data["Time (s)"].astype(float)
fs = 1.0 / np.median(np.diff(t))
N  = len(t)
duration_hr = (t[-1] - t[0]) / 3600.0
print(f"{FILENAME}: N = {N}, fs = {fs:.4f} Hz, duration = {t[-1]-t[0]:.1f} s "
      f"({duration_hr:.2f} h, {CROP_FRACTION*100:.0f}% of record used)")

def phase(input_n):
    return data[f"Input {input_n} Phase (cyc)"].astype(float)

def freq(input_n):
    return data[f"Input {input_n} Frequency (Hz)"].astype(float)

def D(data, delay):
    return timeshift(data, -delay*fs)


ref1 = detrend(phase(5))/2e6
ref2 = detrend(phase(6))/2e6
ref3 = detrend(phase(7))/2e6

ref_AB = ref1 - ref2

omega1 = 17e6
omega2 = 38e6
omega3 = 47e6

# detrend removes each beatnote's carrier ramp (constant frequency offset);
# eta_21 / eta_31 carry the testbed's minus-sign polarity.


# ---------------------------------------------------------------- metric
def band_rms(x, sl, lo=FMIN, hi=FMAX):
    nps = (sl.stop - sl.start) // 8
    f, p = welch(x[sl], fs=fs, nperseg=nps)
    m = (f >= lo) & (f <= hi)
    return np.sqrt(np.trapezoid(p[m], f[m]))

# ---------------------------------------------------------------- TDI (X1)
def build_x1(delays):
    """First-gen Michelson X1 with 4 independent delays (d12, d21, d13, d31) [s]."""
    d12, d21, d13, d31 = delays

    
    etas = {
        "eta_12":  (freq(1) - np.mean(freq(1))),
        "eta_13":  (freq(2)- np.mean(freq(2))),
        "eta_21": -(freq(3)- np.mean(freq(3))),
        "eta_31": -(freq(4)- np.mean(freq(4))),
    }

    etas = {
        "eta_12":  detrend(phase(1)),
        "eta_13":  detrend(phase(2)),
        "eta_21": -detrend(phase(3)),
        "eta_31": -detrend(phase(4)),
    }

    return X1_ETA.build(
        {"d_12": d12, "d_21": d21, "d_13": d13, "d_31": d31}, fs
    )(etas, unit="phase")
    
        
    eta_12 = (freq(1) - np.mean(freq(1)))
    eta_13 = (freq(2)- np.mean(freq(2)))
    eta_21 = -(freq(3)- np.mean(freq(3)))
    eta_31 = -(freq(4)- np.mean(freq(4)))


    phi_12 = eta_12 + D(eta_21, d12)
    phi_13 = eta_13 + D(eta_31, d13)

    P12 = phi_12 - D(phi_12, d31+d13)
    P13 = -(phi_13 - D(phi_13, d21+d12))

    return P12 + P13 


def build_x1c(delays):
    """First-gen Michelson X1 with 4 independent delays (d12, d21, d13, d31) [s]."""
    d12, d21, d13, d31 = delays
    eta_12 = detrend(phase(1))- omega2*(ref1 - D(ref1, d12))
    eta_13 = detrend(phase(2))- omega3*(ref1 - D(ref1, d13))
    eta_21 = -detrend(phase(3))- omega1*(ref2 - D(ref2, d21))
    eta_31 = -detrend(phase(4))- omega1*(ref3 - D(ref3, d31))


    phi_12 = eta_12 + D(eta_21, d12)
    phi_13 = eta_13 + D(eta_31, d13)

    P12 = phi_12 - D(phi_12, d31+d13)
    P13 = -(phi_13 - D(phi_13, d21+d12))

    return P12 + P13 
# ---------------------------------------------------------------- fit delays
full = slice(EDGE_CROP, N - EDGE_CROP)

if FIT_DELAYS:
    half  = N // 2
    train = slice(EDGE_CROP, half)
    test  = slice(half, N - EDGE_CROP)

    cost = lambda p, sl: band_rms(build_x1(p), sl)
    BOUNDS = [(DELAYS_START[0]-0.5, DELAYS_START[0]+0.5)]*4
    res    = minimize(cost, DELAYS_START, args=(full,),  method="Nelder-Mead",
                       options={"xatol": 1e-12, "fatol": 1e-10, "maxiter": 4000})
    
    delays = tuple(res.x)

    print("\ndelay fit (d12, d21, d13, d31) [s]:")
    print(f"  full-record fit : {np.round(delays, 4)}")
else:
    delays = DELAYS_START




# ---------------------------------------------------------------- final + plot
TDI = build_x1(delays)
TDI22 = build_x1c(delays)

print(f"\nfinal (full record, delays {np.round(delays,4)}):")
print(f"  raw η₁₂ band-RMS : {band_rms(detrend(phase(1)), full):.3e}")
print(f"  X1  band-RMS     : {band_rms(TDI, full):.3e}"
      f"   ({band_rms(detrend(phase(1)), full)/band_rms(TDI, full):.0f}x)")


if (FIT_DELAYS): print(res)

nps = (full.stop - full.start) // 10
nps = int(fs / FMIN)
f, p_raw = welch(detrend(phase(1))[full],   fs=fs, nperseg=nps)
f, p_fit = welch(TDI[full],                 fs=fs, nperseg=nps)

f, p_ref = welch(ref1[full], fs=fs, nperseg=nps)
f, p_TDI22  = welch(TDI22[full], fs=fs, nperseg=nps)

baseline_ref = np.loadtxt(os.path.join('..', 'measured noises', 'baselineX1.csv'), delimiter=',', skiprows=1)



color_extrapolated = "#d71b2f"   # (215, 27, 47)  red
color_measured     = "#295f24"   # (41, 95, 36)   green
color_anchor       = color_extrapolated
color_modulator    = "#821770"   # (130, 23, 112) magenta
color_delayline    = "#2d13b4"   # (45, 19, 180)  blue


plt.figure(figsize=(8, 5))
plt.loglog(f, np.sqrt(p_raw), lw=1.0, color=color_extrapolated, label=r"raw $\eta_{12}$")
#plt.loglog(f, 14e6*np.sqrt(p_ref), lw=1.0, color="green", label="p_ref")
plt.loglog(f, np.sqrt(p_fit), lw=1.4, color=color_modulator, label=f"TDI X1")
#plt.loglog(f, np.sqrt(p_TDIc), lw=0.5, color="0.6", label="TDIc")
#plt.loglog(f, np.sqrt(p_TDI22), lw=0.5, alpha=0.6, color="blue", label="TDI + board jitter correction")

plt.loglog(baseline_ref[:, 0], baseline_ref[:, 1], lw=1.5, label='3-board baseline', color='k', alpha=0.3)

#plt.axvspan(FMIN, FMAX, color="tab:blue", alpha=0.06, label="fit band")
plt.xlim(10e-4, 10)
plt.xlabel("Fourier Frequency [Hz]"); plt.ylabel("ASD [cyc/√Hz]")
#plt.title(f"Measurement time {(t[-1]-t[0])/60:.1f} min")
plt.grid(True, which="major", color="#e0e0e0", linewidth=0.6, linestyle="--")
plt.grid(False, which="minor")

plt.legend(loc="center left", bbox_to_anchor=(0.8, 0.95), fontsize=12, frameon=True, fancybox=False)
plt.tight_layout()
plt.savefig(f"{FILENAME}_X1_delayfit.png", transparent=True)
print(f"\nsaved {FILENAME}_X1_delayfit.png")



# ---------------------------------------------------------------- timeseries plot
if (False):
    uga = freq(2)[full] - np.mean(freq(2)[full])
    buga = freq(4)[full]- np.mean(freq(4)[full])
    mix = (uga + timeshift(buga, -fs*8.2))


    uga12 = freq(1)[full] - np.mean(freq(1)[full])
    buga21 = freq(3)[full]- np.mean(freq(3)[full])
    mix2 = (uga12 + timeshift(buga21, -fs*8.1))
    plt.figure(figsize=(10, 6))
    #plt.plot(t[full], uga12, lw=0.6, label="c12")
    plt.plot(t[full], (uga), lw=0.6, label="c13")
    #plt.plot(t[full], (freq(3)[full]), lw=0.6, label="c21")
    plt.plot(t[full], buga, lw=0.6, label=" timeshift(c31, -fs*8.2)")
    #plt.plot(t[full], mix-mix2, lw=0.6, label="uga buga")
    plt.xlabel("Time (s)"); plt.ylabel("Frequency (Hz)")
    plt.title("Carrier beatnote frequencies (cropped)")
    plt.grid(True, ls="--", alpha=0.4)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{FILENAME}_freq_timeseries.png", dpi=200)
    print(f"saved {FILENAME}_freq_timeseries.png")

# ---------------------------------------------------------------- export detrended data
def save_detrended(filename=None):
    """Write cropped, detrended t, c12, c13, c21, c31, REF1-3 data to a CSV file."""
    if filename is None:
        filename = f"{FILENAME}_detrended.csv"
    out = np.column_stack([
        t[full],
        detrend(freq(1)[full]),
        detrend(freq(2)[full]),
        detrend(freq(3)[full]),
        detrend(freq(4)[full]),
        ref1[full],
        ref2[full],
        ref3[full],
    ])
    header = "Time (s),c12 (Hz),c13 (Hz),c21 (Hz),c31 (Hz),REF1,REF2,REF3"
    np.savetxt(filename, out, delimiter=",", header=header, comments="")
    print(f"saved {filename}")
    return filename

#save_detrended()