import numpy as np
from scipy.signal import detrend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import re


import glob
import os


"""USER INPUT FOR THE DATASET TO USE"""
# ── 0. Find all .npy/.txt pairs under data/*/ ────────────────────────────────
npy_files = sorted(glob.glob('data/**/*.npy', recursive=True))
# Only keep files that also have a matching .txt
pairs = [(f, f.replace('.npy', '.txt')) for f in npy_files if os.path.exists(f.replace('.npy', '.txt'))]

if not pairs:
    raise FileNotFoundError('No matching .npy/.txt pairs found under data/')

print('Available datasets:')
for i, (npy, _) in enumerate(pairs):
    print(f'  [{i}] {npy}')

idx = int(input(f'Select dataset [0-{len(pairs)-1}]: '))
npy_file, txt_file = pairs[idx]
filename = os.path.splitext(os.path.basename(npy_file))[0]
print(f'Loading: {npy_file}')


fmin = 1e-4

"""Actual data loading and initial processing starts here"""
data = np.load(npy_file)
print(f"Shape: {data.shape}  |  dtype: {data.dtype}")

# Access fields by name directly from structured array
def col(name):
    return data[name]

t  = col('Time (s)')
fs = 1.0 / np.median(np.diff(t))
print(f"Samples: {len(t)}  |  fs ≈ {fs:.4f} Hz  |  duration ≈ {t[-1]-t[0]:.1f} s")

# Parse acquisition start time from the .txt header (line 13: "# % Acquired YYYY-MM-DD T HH:MM:SS +HHMM")
with open(txt_file, 'r') as f:
    for line in f:
        m = re.search(r'Acquired\s+(\d{4}-\d{2}-\d{2})\s+T\s+(\d{2}:\d{2}:\d{2})', line)
        if m:
            t_start = datetime.strptime(f"{m.group(1)} {m.group(2)}", '%Y-%m-%d %H:%M:%S')
            break

# Convert relative timestamps to absolute datetime (no timezone, just wall-clock time from file)
t_abs = [t_start + timedelta(seconds=float(dt - t[0])) for dt in t]

# ── 2. Extract timestamps, frequencies, phases ────────────────────────────────

channels = {}
for ch in range(1, 5):
    pfx = f'Input {ch} '
    channels[ch] = {
        'set_f':  col(pfx + 'Set Frequency (Hz)'),
        'freq':   col(pfx + 'Frequency (Hz)'),
        'phase':  col(pfx + 'Phase (cyc)'),
        'I':      col(pfx + 'I (V)'),
        'Q':      col(pfx + 'Q (V)'),
    }

# ── 3. Detrend ────────────────────────────────────────────────────────────────

for ch in range(1, 5):
    channels[ch]['phase_detrended'] = detrend(channels[ch]['phase'], type='linear')

# ── 4. Quick sanity plot ──────────────────────────────────────────────────────

fig, axes = plt.subplots(4, 2, figsize=(15, 10))
fig.suptitle(f'{filename}', fontsize=12)

for i, ch in enumerate(range(1, 5)):
    ax_p = axes[i, 0]
    #ax_p.plot(t_abs, channels[ch]['phase'],           lw=0.6, label='raw')
    ax_p.plot(t_abs, channels[ch]['phase_detrended'], lw=0.6, label='detrended', alpha=0.8)
    ax_p.set_ylabel(f'Ch{ch} phase (cyc)')
    ax_p.grid(True, ls='--', alpha=0.5)
    #ax_p.legend(fontsize=7)

    ax_f = axes[i, 1]
    freq = channels[ch]['freq']
    freq_mean = np.mean(freq)
    ax_f.plot(t_abs, freq - freq_mean, lw=0.6, label=f'mean removed: {freq_mean/1e6:.6f} MHz')
    ax_f.set_ylabel(f'Ch{ch} freq (Hz)')
    ax_f.grid(True, ls='--', alpha=0.5)
    ax_f.legend(fontsize=7)

# Format x-axis as datetime on all subplots
duration_s = (t[-1] - t[0])
if duration_s < 120:
    fmt = mdates.DateFormatter('%H:%M:%S')
elif duration_s < 7200:
    fmt = mdates.DateFormatter('%H:%M:%S')
else:
    fmt = mdates.DateFormatter('%H:%M')

t_start_num = mdates.date2num(t_start)

def to_elapsed(x):
    return (x - t_start_num) * 24  # days -> hours

def to_absolute(x):
    return x / 24 + t_start_num

for i, ax in enumerate(axes.flat):
    ax.xaxis.set_major_formatter(fmt) # Depends on the duration
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=8, maxticks=14))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha='right', fontsize=7)
    secax = ax.secondary_xaxis('top', functions=(to_elapsed, to_absolute))
    #secax.tick_params(labelsize=7)
    if i == 0:
        secax.set_xlabel('Elapsed (h)') #, fontsize=7

for ax in axes[-1]:
    ax.set_xlabel('Time')

plt.tight_layout()
plt.savefig(f'plots/timeseries/first_look_{filename}.pdf', dpi=150)

from scipy.signal import welch
 
fig_asd, axes_asd = plt.subplots(2, 1, figsize=(9, 8))
fig_asd.suptitle(f'ASD:{filename}', fontsize=12)
 
for i, ch in enumerate(range(1, 5)):
    # Phase ASD
    ax_ph = axes_asd[0]
    f_ph, psd_ph = welch(channels[ch]['phase_detrended'], fs=fs, nperseg=min(int(fs / fmin), len(t)))
    asd_ph = np.sqrt(psd_ph)
    ax_ph.loglog(f_ph[1:], asd_ph[1:], lw=0.8, label=f'Ch{ch}')
    ax_ph.set_xlabel('Fourier Frequency (Hz)')
    ax_ph.set_ylabel('ASD (cyc/√Hz)')
    ax_ph.grid(True, which='both', ls='--', alpha=0.5)
    ax_ph.legend(fontsize=7)
 
    # Frequency ASD
    ax_fr = axes_asd[1]
    freq = channels[ch]['freq']
    freq_mean = np.mean(freq)
    f_fr, psd_fr = welch(freq - freq_mean, fs=fs, nperseg=min(int(fs / fmin), len(t)))
    asd_fr = np.sqrt(psd_fr)
    ax_fr.loglog(f_fr[1:], asd_fr[1:], lw=0.8, label=f'Ch{ch}')
    ax_fr.set_xlabel('Fourier Frequency (Hz)')
    ax_fr.set_ylabel('ASD (Hz/√Hz)')
    ax_fr.grid(True, which='both', ls='--', alpha=0.5)
    ax_fr.legend(fontsize=7)

plt.tight_layout()
plt.savefig(f'plots/asd/asd_{filename}.pdf', dpi=150)