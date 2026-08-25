"""
Detrends both channels of a Moku:Lab timing-jitters log (Input 1, Input 2 --
see the .txt header for what's physically connected to each) and plots:
  - phase time series (both channels)
  - frequency time series (both channels)
  - phase noise ASD (both channels)
  - frequency noise ASD (both channels)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend, welch, find_peaks

# ── CONFIG ──────────────────────────────────────────────────────────────
filename = 'PTvsSysref_20260813_180721'
min_f = 1e-3  # Hz; None -> auto-size nperseg from the data length instead

peak_fmin, peak_fmax = 0.9e-2, 5e-1
peak_prominence = 1.1  # in log10(ASD) -- ~2x above the surrounding floor

color_ch1 = "#d71b2f"  # red   -- Input 1
color_ch2 = "#295f24"  # green -- Input 2


MOKU_IP = '169.254.170.210'   # <-- set this to your Moku Pro's IP
import os
if (False):
    import subprocess
    try:
        os.makedirs('data', exist_ok=True)
        li_path = f'data/{filename}.li'

        if os.path.exists(li_path):
            os.remove(li_path)  # force a fresh pull even if a stale copy is sitting here

        print(f"Downloading {filename}.li from Moku Pro at {MOKU_IP} ...")
        subprocess.run(
            ['mokucli', 'files', 'download', MOKU_IP, '--name', f'{filename}.li'],
            cwd='data', check=True,
        )

        print(f"Converting {filename}.li -> {filename}.npy (+ .txt header) ...")
        subprocess.run(
            ['mokucli', 'convert', li_path, '--format', 'npy'],
            check=True,
        )

        os.remove(li_path)  # only the .npy and .txt are kept
    except subprocess.CalledProcessError as e:
        print(f"Error during Moku Pro download/convert: {e}")


# ── LOAD ────────────────────────────────────────────────────────────────
data = np.load(f'data/{filename}.npy')

def col(name):
    return data[name].copy()

t  = col('Time (s)')
fs = 1.0 / np.median(np.diff(t))
print(f"Samples: {len(t)} | fs ≈ {fs:.4f} Hz | duration ≈ {t[-1]-t[0]:.1f} s")

def load_input(n):
    pfx = f'Input {n} '
    return {
        'freq':  col(pfx + 'Frequency (Hz)'),
        'phase': col(pfx + 'Phase (cyc)'),
    }

channels = {1: load_input(1), 2: load_input(2)}

# ── DETREND ─────────────────────────────────────────────────────────────
for ch in channels.values():
    ch['phase_d'] = detrend(ch['phase'])
    ch['freq_d']  = detrend(ch['freq'])

# ── ASD ─────────────────────────────────────────────────────────────────
def compute_asd(x, fs, fmin=min_f, nperseg=None):
    if nperseg is None:
        nperseg = min(len(x) // 4, 2**14)
    if fmin is not None:
        nperseg = int(fs / fmin)
    nperseg = min(nperseg, len(x))  # safety clamp
    f, psd = welch(x, fs=fs, nperseg=nperseg, detrend='constant')
    return f, np.sqrt(psd)

for ch in channels.values():
    ch['f_phase'], ch['asd_phase'] = compute_asd(ch['phase_d'], fs)
    ch['f_freq'],  ch['asd_freq']  = compute_asd(ch['freq_d'], fs)

colors = {1: color_ch1, 2: color_ch2}
color_diff = "#821770"  # purple -- ch1-ch2 diff, referred to 10 MHz

# ── PHASE DIFFERENCE, REFERRED TO THE 10 MHz REFERENCE CLOCK ──────────────
# each channel's phase (cyc) is N_i times the shared reference oscillator's
# phase, where N_i = f_i / f_ref is the (fixed) frequency-multiplication
# factor -- dividing by each channel's own carrier frequency removes that
# factor and leaves a common "phase time" (cyc/Hz = s), so differencing the
# two channels isolates the noise that *isn't* common between them. Scaling
# that difference back up by the internal 10 MHz reference clock expresses
# it as an equivalent phase noise as if measured directly on a 10 MHz carrier.
f_ref = 15e6  # Moku's internal reference clock (see the .txt header)

f1_mean = channels[1]['freq'].mean()
f2_mean = channels[2]['freq'].mean()

phase1_time = channels[1]['phase'] / f1_mean
phase2_time = channels[2]['phase'] / f2_mean

phase_diff_10MHz = detrend((phase1_time - phase2_time) * f_ref)
f_diff, asd_diff_10MHz = compute_asd(phase_diff_10MHz, fs)

# fixed filename (not timestamped) so analysis_w_debug.py can pick it up
# without needing to know which timingjitters run produced it -- overwritten
# each time this script runs, same pattern as measured_clock_asd.csv
diff_asd_path = os.path.join('..', 'measured noises', f'pt_diff_{f_ref/1e6:.0f}MHz_asd.csv')
np.savetxt(
    diff_asd_path,
    np.column_stack((f_diff, asd_diff_10MHz)),
    header=f'freq_Hz,asd_diff_{f_ref/1e6:.0f}MHz_cyc_per_rtHz',
    delimiter=',',
    comments=''
)
print(f"Saved PT diff ASD (referred to {f_ref/1e6:.0f} MHz) -> {diff_asd_path}")

# ── PEAKS IN THE DIFF ───────────────────────────────────────────────────
# find_peaks' prominence measures height above the higher of the two
# neighboring troughs, so it holds up reasonably well against a sloped
# 1/f-ish background instead of just flagging the low-f end of the band.
diff_band = (f_diff >= peak_fmin) & (f_diff <= peak_fmax)
diff_f_band   = f_diff[diff_band]
diff_asd_band = asd_diff_10MHz[diff_band]

diff_peak_idx, _ = find_peaks(np.log10(diff_asd_band), prominence=peak_prominence)
diff_peak_freqs = diff_f_band[diff_peak_idx]
diff_peak_amps  = diff_asd_band[diff_peak_idx]

print(f"\nPeaks in the diff ASD, {peak_fmin:g}-{peak_fmax:g} Hz "
      f"(prominence >= {peak_prominence} dex):")
if len(diff_peak_freqs) == 0:
    print("  none found")
for pf, pa in zip(diff_peak_freqs, diff_peak_amps):
    print(f"  f = {pf:.5f} Hz   ASD = {pa:.3e} cyc/sqrt(Hz)")

if len(diff_peak_freqs) >= 2:
    diff_peak_spacing = np.diff(diff_peak_freqs)
    print(f"\nSpacing between the {len(diff_peak_freqs)} peaks ({len(diff_peak_spacing)} intervals):")
    for f_lo, f_hi, df in zip(diff_peak_freqs[:-1], diff_peak_freqs[1:], diff_peak_spacing):
        print(f"  {f_lo:.5f} -> {f_hi:.5f} Hz : Δf = {df:.5f} Hz")
    print(f"  mean Δf   = {diff_peak_spacing.mean():.5f} Hz")
    print(f"  median Δf = {np.median(diff_peak_spacing):.5f} Hz")
    print(f"  std Δf    = {diff_peak_spacing.std():.5f} Hz")
    print(f"  min/max Δf = {diff_peak_spacing.min():.5f} / {diff_peak_spacing.max():.5f} Hz")
else:
    print("\nFewer than 2 peaks found -- no spacing stats")

"""
# ── PLOT: PHASE TIME SERIES ────────────────────────────────────────────
plt.figure(figsize=(10, 5))
for n, ch in channels.items():
    plt.plot(t, ch['phase_d'], lw=0.5, color=colors[n], label=f'Input {n}')
plt.xlabel('Time (s)')
plt.ylabel('Detrended phase (cyc)')
plt.title(f'Phase noise time series -- {filename}')
plt.grid(True, ls='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(f'plots/{filename}_phase_timeseries.png', dpi=300)

# ── PLOT: FREQUENCY TIME SERIES ────────────────────────────────────────
plt.figure(figsize=(10, 5))
for n, ch in channels.items():
    plt.plot(t, ch['freq_d'], lw=0.5, color=colors[n], label=f'Input {n}')
plt.xlabel('Time (s)')
plt.ylabel('Detrended frequency (Hz)')
plt.title(f'Frequency noise time series -- {filename}')
plt.grid(True, ls='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(f'plots/{filename}_freq_timeseries.png', dpi=300)
"""
# ── PLOT: PHASE NOISE ASD ──────────────────────────────────────────────
plt.figure(figsize=(8, 5))
labels = ["45 MHz PT", "100 MHz SYS REF"]
for n, ch in channels.items():
    plt.loglog(ch['f_phase'], ch['asd_phase'], lw=1.2, color=colors[n], label=labels[n-1])
plt.loglog(f_diff, asd_diff_10MHz, lw=0.5, color=color_diff, label='diff referred to 15 MHz')
#plt.loglog(diff_peak_freqs, diff_peak_amps, 'o', color='k', ms=5, label='Diff peaks')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Phase ASD (cyc / √Hz)')
plt.title(f'Phase noise ASD -- {filename}')
plt.grid(True, which='both', ls='--', alpha=0.5)
plt.legend()
plt.xlim(ch['f_phase'][1], fs / 2)  # skip the f=0 bin on a log axis
plt.tight_layout()
plt.savefig(f'plots/{filename}_phase_asd.png', dpi=300)


