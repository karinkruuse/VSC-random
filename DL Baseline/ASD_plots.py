import numpy as np
from scipy.signal import detrend, welch
import matplotlib.pyplot as plt

# ── Config ────────────────────────────────────────────────────────────────────
filename = 'DL_baseline_20260417_154937'
npy_file   = 'data/second/' + filename +'.npy'
BURN_IN_S  = 0   # seconds to discard from the start

# ── 1. Load ───────────────────────────────────────────────────────────────────

data = np.load(npy_file)

def col(name):
    return data[name].copy()

t  = col('Time (s)')
fs = 1.0 / np.median(np.diff(t))
print(f"Samples: {len(t)}  |  fs ≈ {fs:.4f} Hz  |  duration ≈ {t[-1]-t[0]:.1f} s")

channels = {}
for ch in range(1, 5):
    pfx = f'Input {ch} '
    channels[ch] = {
        'freq':  col(pfx + 'Frequency (Hz)'),
        'phase': col(pfx + 'Phase (cyc)'),
    }

# ── 2. Throw away burn-in ─────────────────────────────────────────────────────

burn_idx = np.searchsorted(t, t[0] + BURN_IN_S)
print(f"Discarding first {burn_idx} samples (≈ {BURN_IN_S:.1f} s)")
t = t[burn_idx:]
for ch in range(1, 5):
    for key in channels[ch]:
        channels[ch][key] = channels[ch][key][burn_idx:]

print(f"After burn-in: {len(t)} samples  |  duration ≈ {t[-1]-t[0]:.1f} s")

# ── 3. Detrend ────────────────────────────────────────────────────────────────

for ch in range(1, 5):
    channels[ch]['phase_d'] = detrend(channels[ch]['phase'], type='linear')
    channels[ch]['freq_d']  = detrend(channels[ch]['freq'],  type='linear')

# ── 4. ASD via Welch ──────────────────────────────────────────────────────────

nperseg = min(len(t) // 8, 2**18)

def asd(x):
    f, psd = welch(x, fs=fs, window='hann', nperseg=nperseg, detrend='linear')
    return f, np.sqrt(psd)

ch_colors = ['C0', 'C1', 'C2', 'C3']

fig, axes = plt.subplots(2, 1, figsize=(10, 8))
fig.suptitle(f'Moku:Pro Phasemeter — ASD  (burn-in: {BURN_IN_S:.0f} s)', fontsize=12)

ax_phase, ax_freq = axes

for ch in range(1, 5):
    color = ch_colors[ch - 1]
    label = f'Ch{ch}'

    f, a_phase = asd(channels[ch]['phase_d'] * 2 * np.pi)
    ax_phase.loglog(f[1:], a_phase[1:], lw=0.8, color=color, label=label)

    f, a_freq = asd(channels[ch]['freq'])
    ax_freq.loglog(f[1:], a_freq[1:], lw=0.8, color=color, label=label)

ax_phase.set_ylabel('Phase ASD (rad/√Hz)')
ax_phase.set_xlabel('Frequency (Hz)')
ax_phase.legend(fontsize=9)
ax_phase.grid(True, which='both', alpha=0.3)
ax_phase.set_xlim(left=f[1])

ax_freq.set_ylabel('Frequency ASD (Hz/√Hz)')
ax_freq.set_xlabel('Frequency (Hz)')
ax_freq.legend(fontsize=9)
ax_freq.grid(True, which='both', alpha=0.3)
ax_freq.set_xlim(left=f[1])

plt.tight_layout()
plt.savefig(f'moku_asd_{filename}.pdf', dpi=150)
plt.show()