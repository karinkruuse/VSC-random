"""
Runs the Troebs & Heinzel LPSD algorithm (pip install lpsd -- the `lpsd`
package, not scipy) on the sideband-based residual instead of scipy.welch's
fixed-nperseg ASD. LPSD uses logarithmically spaced frequency bins, which
gives much better resolution at low frequencies for the same compute
budget -- useful for telling apart closely-spaced peaks near the low end of
the [2e-2, 3e-1] Hz band that analysis_w_debug.py's peak finder looks at.

Recomputes the residual directly from the raw .npy rather than importing
analysis_w_debug.py, since that script is a top-to-bottom driver (Moku
download + every plot) and not meant to be imported. Keep the CONFIG block
below in sync with analysis_w_debug.py if its channel roles or delay_s change.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import detrend, find_peaks
from lpsd import lpsd

# ── CONFIG -- keep in sync with analysis_w_debug.py ────────────────────────
filename = 'BaselineW119MHz_20260812_175544'
delay_s  = 4.29999

PT_INPUT         = 2   # pilot tone, co-located with the delayed channel
DELAYED_INPUT    = 1   # delayed carrier
DELAYED_SB_INPUT = 4   # delayed sideband

peak_fmin, peak_fmax = 2e-2, 3e-1
peak_prominence = 0.3  # in log10(ASD) -- ~2x above the surrounding floor

color_delayline = "#295f24"  # same green used for the sideband residual elsewhere

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

ch3 = load_input(DELAYED_INPUT)
pt  = load_input(PT_INPUT)
sb  = load_input(DELAYED_SB_INPUT)

# ── SIDEBAND RESIDUAL (same combo as analysis_w_debug.py's tdi_alt) ───────
# crop the same n_crop from both ends as the main script so results stay
# comparable -- ch3/pt/sb aren't software-delayed for this combo, so it's
# not strictly required here, just kept for parity.
delay_samples = delay_s * fs
n_crop = int(np.ceil(abs(delay_samples))) + 5
sl = slice(n_crop, -n_crop)

t = t[sl]
ch3_phase, ch3_freq = ch3['phase'][sl], ch3['freq'][sl]
pt_phase,  pt_freq  = pt['phase'][sl],  pt['freq'][sl]
sb_phase,  sb_freq  = sb['phase'][sl],  sb['freq'][sl]

t_jitter = pt_phase / pt_freq

tj_d             = detrend(t_jitter)
dcarrier_phase_d = detrend(ch3_phase)
sb_phase_d       = detrend(sb_phase)

tdi_alt = (
    sb_phase_d
    - dcarrier_phase_d
    - (np.mean(sb_freq - ch3_freq)) * tj_d
)
print(f"Residual length: {len(tdi_alt)} samples")

# ── LPSD ────────────────────────────────────────────────────────────────
residual = pd.Series(tdi_alt, index=t)
spectrum = lpsd(residual, sample_rate=fs, n_frequencies=2000)

f_lpsd   = spectrum.index.to_numpy()
asd_lpsd = spectrum['asd'].to_numpy()

# ── PLOT: LPSD ASD ──────────────────────────────────────────────────────
plt.figure(figsize=(8, 5))
plt.loglog(f_lpsd, asd_lpsd, lw=1.5, color=color_delayline, label='Residual with sideband (LPSD)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('ASD (cyc / √Hz)')
plt.title(f'LPSD of sideband residual, delay = {delay_s:.8f} s')
plt.grid(True, which='both', ls='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(f'plots/{filename}_residual_sideband_lpsd.png', dpi=300)

# ── PEAKS + SPACING (same band/prominence as analysis_w_debug.py) ─────────
band = (f_lpsd >= peak_fmin) & (f_lpsd <= peak_fmax)
f_band, asd_band = f_lpsd[band], asd_lpsd[band]

peak_idx, _ = find_peaks(np.log10(asd_band), prominence=peak_prominence)
peak_freqs = f_band[peak_idx]
peak_amps  = asd_band[peak_idx]

print(f"\nLPSD peaks, {peak_fmin:g}-{peak_fmax:g} Hz (prominence >= {peak_prominence} dex):")
if len(peak_freqs) == 0:
    print("  none found")
for pf, pa in zip(peak_freqs, peak_amps):
    print(f"  f = {pf:.5f} Hz   ASD = {pa:.3e} cyc/sqrt(Hz)")

if len(peak_freqs) >= 2:
    peak_spacing = np.diff(peak_freqs)
    print(f"\nSpacing between the {len(peak_freqs)} peaks ({len(peak_spacing)} intervals):")
    for f_lo, f_hi, df in zip(peak_freqs[:-1], peak_freqs[1:], peak_spacing):
        print(f"  {f_lo:.5f} -> {f_hi:.5f} Hz : Δf = {df:.5f} Hz")
    print(f"  mean Δf   = {peak_spacing.mean():.5f} Hz")
    print(f"  median Δf = {np.median(peak_spacing):.5f} Hz")
    print(f"  std Δf    = {peak_spacing.std():.5f} Hz")
    print(f"  min/max Δf = {peak_spacing.min():.5f} / {peak_spacing.max():.5f} Hz")
else:
    print("\nFewer than 2 peaks found -- no spacing stats")

plt.figure(figsize=(8, 5))
plt.loglog(f_band, asd_band, lw=1.5, color=color_delayline, label='Residual with sideband (LPSD)')
plt.loglog(peak_freqs, peak_amps, 'x', color='k', ms=8, mew=2, label='Detected peaks')
for pf in peak_freqs:
    plt.axvline(pf, color='k', ls=':', lw=0.7, alpha=0.6)

plt.xlabel('Frequency (Hz)')
plt.ylabel('ASD (cyc / √Hz)')
plt.title(f'LPSD peaks in residual with sideband, {peak_fmin:g}-{peak_fmax:g} Hz')
plt.grid(True, which='both', ls='--', alpha=0.5)
plt.legend()
plt.xlim(peak_fmin, peak_fmax)
plt.tight_layout()
plt.savefig(f'plots/{filename}_residual_sideband_lpsd_peaks.png', dpi=300)
