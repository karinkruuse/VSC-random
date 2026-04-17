import numpy as np
from scipy.signal import detrend
import matplotlib.pyplot as plt

# ── 1. Load ───────────────────────────────────────────────────────────────────
filename = 'DL_baseline_20260417_154937'
npy_file = f'data/second/{filename}.npy'
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
        'set_f':  col(pfx + 'Set Frequency (Hz)'),
        'freq':   col(pfx + 'Frequency (Hz)'),
        'phase':  col(pfx + 'Phase (cyc)'),
        'I':      col(pfx + 'I (V)'),
        'Q':      col(pfx + 'Q (V)'),
    }

# ── 2. Throw away first 10000 s ───────────────────────────────────────────────
to_burn = 0
burn_idx = np.searchsorted(t, t[0] + to_burn)
print(f"Discarding first {burn_idx} samples (≈ {to_burn} s)")

t = t[burn_idx:]
for ch in range(1, 5):
    for key in channels[ch]:
        channels[ch][key] = channels[ch][key][burn_idx:]

# ── 3. Compute t_jitter (ch4_phase / ch4_freq) BEFORE any trimming ────────────

t_jitter = channels[4]['phase'] / channels[4]['freq']   # undelayed, full length

delay_s       = 1.337
delay_samples = int(round(delay_s * fs))
print(f"Delay: {delay_s*1e3:.1f} ms = {delay_samples} samples at fs={fs:.4f} Hz")
print("Synthetic delay length in seconds (includes rounding error):", delay_samples / fs)

N_trim = len(t) - delay_samples

# ── 4. Delayed streams (drop first delay_samples) ─────────────────────────────

ch1_freq_delayed     = channels[1]['freq'] [delay_samples : delay_samples + N_trim]
ch3_phase_delayed    = channels[3]['phase'][delay_samples : delay_samples + N_trim]
t_jitter_delayed     = t_jitter            [delay_samples : delay_samples + N_trim]

# ── 5. Undelayed streams (trim from end) ──────────────────────────────────────

t_trim               = t                   [:N_trim]
ch1_phase            = channels[1]['phase'][:N_trim]
ch2_phase            = channels[2]['phase'][:N_trim]
ch1_freq             = channels[1]['freq'] [:N_trim]
ch2_freq             = channels[2]['freq'] [:N_trim]
ch3_freq             = channels[3]['freq'] [:N_trim]
t_jitter_undelayed   = t_jitter            [:N_trim]

print(f"Final array length: {N_trim} samples  |  duration ≈ {t_trim[-1]-t_trim[0]:.1f} s")

# ── 6. Detrend all phases and jitters ─────────────────────────────────────────

ch1_phase_d         = detrend(ch1_phase,          type='linear')
ch2_phase_d         = detrend(ch2_phase,          type='linear')
ch3_phase_delayed_d = detrend(ch3_phase_delayed,  type='linear')
t_jitter_ud         = detrend(t_jitter_undelayed, type='linear')
t_jitter_d          = detrend(t_jitter_delayed,   type='linear')

# ── 7. TDI-like combination ───────────────────────────────────────────────────
# ch1_phase - delayed_ch3_phase - delayed_ch1_freq * (t_jitter_undelayed - t_jitter_delayed)
# units: phase [cyc], freq [Hz], t_jitter [s] → freq * t_jitter [cyc] ✓

tdi_combo = (
      ch1_phase_d
    - ch3_phase_delayed_d
    + ch1_freq_delayed * (t_jitter_ud - t_jitter_d)
)

# ── 8. Plot ───────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(5, 1, figsize=(12, 14), sharex=True)
fig.suptitle('Aligned streams and TDI combination', fontsize=12)

axes[0].plot(t_trim, ch1_phase_d,         lw=0.5, label='ch1 phase (undelayed)')
axes[0].plot(t_trim, ch3_phase_delayed_d, lw=0.5, label='ch3 phase (delayed)',  alpha=0.8)
axes[0].set_ylabel('Phase (cyc)')
axes[0].legend(fontsize=8)

axes[1].plot(t_trim, ch1_freq,         lw=0.5, label='ch1 freq (undelayed)')
axes[1].plot(t_trim, ch1_freq_delayed, lw=0.5, label='ch1 freq (delayed)',  alpha=0.8)
axes[1].set_ylabel('Freq (Hz)')
axes[1].legend(fontsize=8)

axes[2].plot(t_trim, t_jitter_ud, lw=0.5, label='t_jitter (undelayed)')
axes[2].plot(t_trim, t_jitter_d,  lw=0.5, label='t_jitter (delayed)',  alpha=0.8)
axes[2].set_ylabel('t_jitter (s)')
axes[2].legend(fontsize=8)

axes[3].plot(t_trim, t_jitter_ud - t_jitter_d, lw=0.5)
axes[3].set_ylabel('Δt_jitter (s)')

axes[4].plot(t_trim, tdi_combo, lw=0.5)
axes[4].set_ylabel('TDI combo (cyc)')
axes[4].set_xlabel('Time (s)')

plt.tight_layout()
plt.savefig('moku_tdi.pdf', dpi=150)
plt.show()