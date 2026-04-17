import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend
from pytdi.dsp import timeshift
from scipy.signal import welch

# ── CONFIG ────────────────────────────────────────────────────────────────
filename = 'DL_baseline_20260417_154937'
delay_s  = 3.9993

# ── 1. LOAD ───────────────────────────────────────────────────────────────
data = np.load(f'data/second/{filename}.npy')

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

channels = {ch: load_channel(ch) for ch in range(1, 5)}

# ── 2. OPTIONAL INITIAL CROPPING ──────────────────────────────────────────
def crop_time(t, data_dict, t_start=0, t_end=0):
    i0 = np.searchsorted(t, t[0] + t_start)
    i1 = np.searchsorted(t, t[-1] - t_end)

    if i0 >= i1:
        raise ValueError("Cropping removed entire dataset")

    sl = slice(i0, i1)
    t_new = t[sl]

    out = {}
    for ch in data_dict:
        out[ch] = {k: v[sl] for k, v in data_dict[ch].items()}

    return t_new, out

t, channels = crop_time(t, channels)

# ── 3. DERIVED SIGNALS ────────────────────────────────────────────────────
t_jitter = channels[4]['phase'] / channels[4]['freq']

delay_samples = delay_s * fs
print(f"Delay: {delay_s:.3f} s = {delay_samples:.2f} samples")

# ── 4. APPLY DELAYS ───────────────────────────────────────────────────────
def apply_delay(x, tau):
    return timeshift(x, -tau)

ch3_phase_dly = apply_delay(channels[3]['phase'], delay_samples)
ch3_freq_dly  = apply_delay(channels[3]['freq'],  delay_samples)
tj_dly        = apply_delay(t_jitter,             delay_samples)

# ── 5. CROP AFTER TIMESHIFT (IMPORTANT) ───────────────────────────────────
def crop_edges(t, arrays, n_crop):
    sl = slice(n_crop, -n_crop)
    t_new = t[sl]
    arrays_new = [a[sl] for a in arrays]
    return t_new, arrays_new

n_crop = int(np.ceil(abs(delay_samples))) + 2  # +2 for safety

t, (
    ch1_phase,
    ch3_phase_dly,
    ch3_freq_dly,
    tj,
    tj_dly
) = crop_edges(
    t,
    [
        channels[1]['phase'],
        ch3_phase_dly,
        ch3_freq_dly,
        t_jitter,
        tj_dly
    ],
    n_crop
)

print(f"Post-shift length: {len(t)} samples")

# ── 6. DETREND ────────────────────────────────────────────────────────────
ch1_phase_d = detrend(ch1_phase)
ch3_phase_d = detrend(ch3_phase_dly)
tj_d        = detrend(tj)
tj_dly_d    = detrend(tj_dly)

# ── 7. TDI COMBINATION ────────────────────────────────────────────────────
tdi = (
    ch1_phase_d
    - ch3_phase_d
    - ch3_freq_dly * (tj_d - tj_dly_d)
)

# ── 8. PLOT ───────────────────────────────────────────────────────────────

"""
fig, ax = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

ax[0].plot(t, ch1_phase_d, lw=0.5, label='ch1 phase')
ax[0].plot(t, ch3_phase_d, lw=0.5, label='ch3 delayed')
ax[0].legend()

ax[1].plot(t, ch3_freq_dly * (tj_d - tj_dly_d), lw=0.5)
ax[1].set_ylabel('Correction term')

ax[2].plot(t, detrend(tdi), lw=0.5)
ax[2].plot(t, ch3_phase_d, lw=0.5)
ax[2].set_ylabel('TDI')
ax[2].set_xlabel('Time (s)')

plt.tight_layout()
plt.show()

"""
# ── 9. ASD COMPUTATION ────────────────────────────────────────────────────
def compute_asd(x, fs, nperseg=None):
    if nperseg is None:
        nperseg = min(len(x)//4, 2**14)
    f, psd = welch(x, fs=fs, nperseg=nperseg, detrend='constant')
    asd = np.sqrt(psd)
    return f, asd

# Use detrended signals
f1, asd_ch1 = compute_asd(ch1_phase_d, fs)
f2, asd_ch3 = compute_asd(ch3_phase_d, fs)
f3, asd_tdi = compute_asd(detrend(tdi), fs)

# ── 10. ASD PLOT ──────────────────────────────────────────────────────────
plt.figure(figsize=(8, 5))

plt.loglog(f1, asd_ch1, lw=1, label='ch1 phase')
plt.loglog(f2, asd_ch3, lw=1, label='ch3 delayed phase')
plt.loglog(f3, asd_tdi, lw=1.5, label='TDI combo')

plt.xlabel('Frequency (Hz)')
plt.ylabel('ASD (cyc / √Hz)')
plt.title('Amplitude Spectral Density')

plt.grid(True, which='both', ls='--', alpha=0.5)
plt.legend()

plt.tight_layout()
plt.show()