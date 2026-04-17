import numpy as np
from scipy.signal import detrend
import matplotlib.pyplot as plt

# ── 1. Load ───────────────────────────────────────────────────────────────────

npy_file = 'data/Delayline_11MHz_mix_UNDEL_DDS_20260416_162317.npy'

data = np.load(npy_file)
print(f"Shape: {data.shape}  |  dtype: {data.dtype}")

# Access fields by name directly from structured array
def col(name):
    return data[name]

t  = col('Time (s)')
fs = 1.0 / np.median(np.diff(t))
print(f"Samples: {len(t)}  |  fs ≈ {fs:.4f} Hz  |  duration ≈ {t[-1]-t[0]:.1f} s")

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
    #channels[ch]['freq_detrended']  = detrend(channels[ch]['freq'],  type='linear')

# ── 4. Quick sanity plot ──────────────────────────────────────────────────────

fig, axes = plt.subplots(4, 2, figsize=(14, 10), sharex=True)
fig.suptitle('Moku:Pro Phasemeter — raw vs detrended', fontsize=12)

for i, ch in enumerate(range(1, 5)):
    ax_p = axes[i, 0]
    ax_p.plot(t, channels[ch]['phase'],           lw=0.6, label='raw')
    ax_p.plot(t, channels[ch]['phase_detrended'], lw=0.6, label='detrended', alpha=0.8)
    ax_p.set_ylabel(f'Ch{ch} phase (cyc)')
    ax_p.legend(fontsize=7)

    ax_f = axes[i, 1]
    ax_f.plot(t, channels[ch]['freq'],           lw=0.6, label='raw')
    #ax_f.plot(t, channels[ch]['freq_detrended'], lw=0.6, label='detrended', alpha=0.8)
    ax_f.set_ylabel(f'Ch{ch} freq (Hz)')
    ax_f.legend(fontsize=7)

for ax in axes[-1]:
    ax.set_xlabel('Time (s)')

plt.tight_layout()
plt.savefig('moku_overview.pdf', dpi=150)
plt.show()