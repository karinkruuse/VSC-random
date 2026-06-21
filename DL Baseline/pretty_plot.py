"""
TDI combination + publication-quality ASD plot.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.signal import detrend, welch
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
    "xtick.labelsize"    : 13,
    "ytick.labelsize"    : 13,
    "axes.labelsize"     : 13,
    "legend.fontsize"    : 10,
    "legend.framealpha"  : 0.92,
    "legend.edgecolor"   : "#cccccc",
    "legend.handlelength": 2.0,
    "figure.dpi"         : 150,
})


# ── CONFIG ─────────────────────────────────────────────────────────────────
filename      = 'DownstairsTest_20260423_170536'
delay_s       = 3.999041
DDS_signal_nr = 2
nr_of_channels = 4
start_time    = 0 * 60 * 60   # seconds to crop from start
end_time      = 0 * 60 * 60   # seconds to crop from end

# ── 1. LOAD ────────────────────────────────────────────────────────────────
data = np.load(f'data/{filename}.npy')

def col(name):
    return data[name].copy()

t  = col('Time (s)')
fs = 1.0 / np.median(np.diff(t))
print(f"Samples: {len(t)} | fs ≈ {fs:.4f} Hz | duration ≈ {t[-1]-t[0]:.1f} s")

def load_channel(ch):
    pfx = f'Input {ch} '
    return {
        'freq':  col(pfx + 'Frequency (Hz)'),
        'phase': col(pfx + 'Phase (cyc)'),
    }

channels = {ch: load_channel(ch) for ch in range(1, nr_of_channels + 1)}

# ── 2. CROP ────────────────────────────────────────────────────────────────
duration = t[-1] - t[0]
print(f"Duration: {duration:.1f} s = {duration/3600:.2f} h")
print(t)
i0 = np.searchsorted(t, t[0]  + start_time)
i1 = np.searchsorted(t, t[-1] - end_time)
sl = slice(i0, i1)
t  = t[sl]
channels = {ch: {k: v[sl] for k, v in channels[ch].items()} for ch in channels}

# ── 3. DERIVED SIGNALS ─────────────────────────────────────────────────────
print(f"Measuring timing jitter from channel {DDS_signal_nr}")
t_jitter = channels[DDS_signal_nr]['phase'] / channels[DDS_signal_nr]['freq']

delay_samples = delay_s * fs
print(f"Delay: {delay_s:.6f} s = {delay_samples:.2f} samples")

# ── 4. APPLY DELAYS ────────────────────────────────────────────────────────
ch3_phase_dly = timeshift(channels[3]['phase'], -delay_samples)
ch3_freq_dly  = timeshift(channels[3]['freq'],  -delay_samples)
tj_dly        = timeshift(t_jitter,             -delay_samples)

# ── 5. CROP EDGES AFTER TIMESHIFT ──────────────────────────────────────────
n_crop = int(np.ceil(abs(delay_samples))) + 5
sl2    = slice(n_crop, -n_crop)

t            = t[sl2]
ch1_phase    = channels[1]['phase'][sl2]
ch1_freq     = channels[1]['freq'][sl2]
ch3_phase    = channels[3]['phase'][sl2]
ch3_phase_dly = ch3_phase_dly[sl2]
ch3_freq_dly  = ch3_freq_dly[sl2]
tj            = t_jitter[sl2]
tj_dly        = tj_dly[sl2]

print(f"Post-shift length: {len(t)} samples")

# ── 6. DETREND ─────────────────────────────────────────────────────────────
ch1_phase_d = detrend(ch1_phase)
ch3_phase_d = detrend(ch3_phase_dly)
tj_d        = detrend(tj)
tj_dly_d    = detrend(tj_dly)

# ── 7. TDI COMBINATION ─────────────────────────────────────────────────────
tdi = (
    ch1_phase_d
    - ch3_phase_d
    - ch3_freq_dly * (tj_d - tj_dly_d)
)

# ── 8. ASD ─────────────────────────────────────────────────────────────────
def compute_asd(x, fs, fmin=1e-4):
    nperseg = min(int(fs / fmin), len(x))
    print(f"nperseg = {nperseg}  (len = {len(x)})")
    f, psd = welch(x, fs=fs, nperseg=nperseg, detrend='constant')
    return f[1:], np.sqrt(psd[1:])

f1, asd_ch1 = compute_asd(ch1_phase_d,       fs)
f2, asd_ch3 = compute_asd(detrend(ch3_phase), fs)
f3, asd_tdi = compute_asd(detrend(tdi),       fs)

np.savetxt(
    "baseline.csv",
    np.column_stack((f3, asd_tdi)),
    header='Frequency (Hz),ASD (cyc/sqrt(Hz))',
    delimiter=',', comments=''
)
print("Saved: baseline.csv")

# ── 9. PLOT ────────────────────────────────────────────────────────────────
used_hours = (duration - start_time - end_time) / 3600

fig, ax = plt.subplots(figsize=(7, 4.8))

ax.loglog(f2, asd_ch3, color=(215/255, 27/255,  47/255, 0.5), lw=1.4, label="Input Signal")
ax.loglog(f1, asd_ch1, color=(215/255, 27/255,  47/255), lw=1.4, label="Delayed Signal")
ax.loglog(f3, asd_tdi, color=(130/255, 23/255, 112/255), lw=1.4, label="Residual noise")


import numpy as np
import matplotlib.pyplot as plt

c = 3e8        # speed of light [m/s]
lam = 1064e-9  # LISA laser wavelength [m]

f = np.logspace(-4, 2, 1000)  # frequency array [Hz]

# --- individual noise ASDs in phase [cycles/sqrt(Hz)] ---
asd_oms = (15e-12 / lam) * np.sqrt(1.0 + (2e-3 / f)**4)

asd_acc = (3e-15 / ((2 * np.pi * f)**2 * lam)) \
          * np.sqrt(1.0 + (0.4e-3 / f)**2) \
          * np.sqrt(1.0 + (f / 8e-3)**4)

# --- total single-link phase noise ASD [cycles/sqrt(Hz)] ---
asd_total = np.sqrt(asd_oms**2 + asd_acc**2)



ax.set_xlabel("Fourier frequency (Hz)")
ax.set_ylabel("ASD (cyc / $\\sqrt{\\mathrm{Hz}}$)")
ax.set_xlim(1e-4, fs / 2)

ax.xaxis.set_minor_locator(ticker.LogLocator(subs="all", numticks=10))
ax.yaxis.set_minor_locator(ticker.LogLocator(subs="all", numticks=10))
ax.tick_params(which="minor", length=2.5, width=0.6)

ax.grid(True,  which="major", color="#e0e0e0", linewidth=0.6, linestyle="--")
ax.grid(False, which="minor")

ax.legend(loc="upper right", frameon=True, fancybox=False)

ax.set_title(
    f"delay = {delay_s:.8f} s",
    fontsize=9, pad=6
)

fig.subplots_adjust(left=0.13, bottom=0.13, right=0.97, top=0.93)

out = f"plots/{filename}_TDI1_asd_pub.svg"
fig.savefig(out, dpi=300, bbox_inches="tight")
print(f"Saved: {out}")

plt.show()