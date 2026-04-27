import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend, welch, csd
from pytdi.dsp import timeshift

# ── CONFIG ────────────────────────────────────────────────────────────────
filename   = 'Delayline_opticalbaseline_100hr_measurement_2_20260424_173355'
delay_s    = 3.9989879870
PT_channel = 2
fmin       = 1e-4
fmax       = 1
start_time = 0  * 60 * 60
end_time   = 2  * 60 * 60

# ── 1. LOAD ───────────────────────────────────────────────────────────────
data = np.load(f'data/{filename}.npy')

def col(name):
    return data[name].copy()

t  = col('Time (s)')
fs = 1.0 / np.median(np.diff(t))
print(f"Samples: {len(t)} | fs ≈ {fs:.4f} Hz | duration ≈ {(t[-1]-t[0])/3600:.2f} h")

channels = {}
for ch in [1, 2, 3]:
    pfx = f'Input {ch} '
    channels[ch] = {
        'freq':  col(pfx + 'Frequency (Hz)'),
        'phase': col(pfx + 'Phase (cyc)'),
    }

# ── 2. CROP ───────────────────────────────────────────────────────────────
i0 = np.searchsorted(t, t[0]  + start_time)
i1 = np.searchsorted(t, t[-1] - end_time)
sl = slice(i0, i1)

t = t[sl]
for ch in channels:
    channels[ch] = {k: v[sl] for k, v in channels[ch].items()}

print(f"After crop: {len(t)} samples | duration ≈ {(t[-1]-t[0])/3600:.2f} h")

# ── 3. SIGNALS ────────────────────────────────────────────────────────────
nperseg = int(fs / fmin)

t_jitter  = channels[PT_channel]['phase'] / channels[PT_channel]['freq']

# detrend for spectral analysis
ch1 = detrend(channels[1]['phase'], type='linear')
ch3 = detrend(channels[3]['phase'], type='linear')
tj  = detrend(t_jitter,             type='linear')

# ── 4. TDI COMBO ──────────────────────────────────────────────────────────
n_crop        = int(np.ceil(abs(delay_s * fs))) + 3
delay_samples = delay_s * fs

ch3_phase_dly = timeshift(channels[3]['phase'], -delay_samples)
ch3_freq_dly  = timeshift(channels[3]['freq'],  -delay_samples)
tj_dly        = timeshift(t_jitter,             -delay_samples)

sc = slice(n_crop, -n_crop)
ch1_d     = detrend(channels[1]['phase'][sc], type='linear')
ch3_d     = detrend(ch3_phase_dly[sc],        type='linear')
tj_diff_d = detrend(t_jitter[sc] - tj_dly[sc], type='linear')

tdi = ch1_d - ch3_d - ch3_freq_dly[sc] * tj_diff_d

# ── 5. SPECTRA ────────────────────────────────────────────────────────────
nperseg_tdi = min(nperseg, len(tdi))

# raw signals (no delay) — for reference ASDs only
f,   S_11 = welch(ch1, fs=fs, nperseg=nperseg)
_,   S_33 = welch(ch3, fs=fs, nperseg=nperseg)

f_t, S_tdi = welch(tdi, fs=fs, nperseg=nperseg_tdi, detrend='constant')

# ── informed spectral estimator ───────────────────────────────────────────
# Give the estimator the same signals TDI actually uses:
#   - ch3_delayed  : ch3 after the delay has been applied
#   - tj_diff      : (tj - tj_delayed), the jitter difference term
# These are already computed and cropped above (ch1_d, ch3_d, tj_diff_d).
# Using them means the cross-spectra see the delay-corrected signals,
# so the estimator doesn't have to learn the delay implicitly.

nperseg_sc = min(nperseg, len(ch1_d))

f_s, S_11s  = welch(ch1_d,    fs=fs, nperseg=nperseg_sc)
_,   S_33s  = welch(ch3_d,    fs=fs, nperseg=nperseg_sc)
_,   S_dds  = welch(tj_diff_d, fs=fs, nperseg=nperseg_sc)   # jitter difference

_,   S_13s  = csd(ch1_d, ch3_d,    fs=fs, nperseg=nperseg_sc)  # ch1 vs ch3_delayed
_,   S_1ds  = csd(ch1_d, tj_diff_d, fs=fs, nperseg=nperseg_sc) # ch1 vs jitter diff
_,   S_3ds  = csd(ch3_d, tj_diff_d, fs=fs, nperseg=nperseg_sc) # ch3_del vs jitter diff

# simple two-signal floor: ch1 vs ch3_delayed only
S_n1_simple = np.abs(S_11s - np.abs(S_13s))

# partial coherence: jointly remove ch3_delayed AND jitter_diff from ch1
# Residual = S_11 - v^H C^{-1} v
# where v = [S_13s, S_1ds]  and  C = [[S_33s, S_3ds], [S_3ds*, S_dds]]
det_C = S_33s * S_dds - np.abs(S_3ds)**2
det_C = np.maximum(det_C.real, 1e-300)

coherent_power = (
    np.abs(S_13s)**2 * S_dds.real
    - 2 * np.real(S_13s * S_3ds * np.conj(S_1ds))
    + np.abs(S_1ds)**2 * S_33s.real
) / det_C

S_n1_partial = np.abs(S_11s.real - coherent_power)

# ── jitter contribution to TDI ────────────────────────────────────────────
ch3_freq_mean    = np.mean(ch3_freq_dly[sc])
f_j, S_tj_diff   = welch(tj_diff_d, fs=fs, nperseg=nperseg_tdi, detrend='constant')
S_jitter_contrib = ch3_freq_mean**2 * S_tj_diff

fm  = (f   >= fmin) & (f   <= fmax)
fmt = (f_t >= fmin) & (f_t <= fmax)
fmj = (f_j >= fmin) & (f_j <= fmax)
fms = (f_s >= fmin) & (f_s <= fmax)

# ── 6. PLOT ──────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))

ax.loglog(f[fm],    np.sqrt(S_11[fm]),                color='C0', lw=1.2,          label='ch1 phase ASD (raw)')
ax.loglog(f[fm],    np.sqrt(S_33[fm]),                color='C1', lw=1.2,          label='ch3 phase ASD (raw)')
ax.loglog(f_t[fmt], np.sqrt(S_tdi[fmt]),              color='C3', lw=1.8,          label='TDI residual ASD')
ax.loglog(f_j[fmj], np.sqrt(S_jitter_contrib[fmj]),  color='C4', lw=1.2, ls=':',  label='jitter contrib to TDI  (f̅ch3² · S_Δtj)')
ax.loglog(f_s[fms], np.sqrt(S_n1_simple[fms]),        color='C6', lw=1.2, ls='--', label='floor: ch1 vs ch3_delayed only')
ax.loglog(f_s[fms], np.sqrt(S_n1_partial[fms]),       color='C5', lw=1.5, ls='--', label='floor: ch1 vs ch3_delayed + jitter_diff (partial coherence)')

ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('ASD (cyc / √Hz)')
ax.set_title(f'Noise analysis — {filename}')
ax.set_xlim(fmin, fmax)
ax.grid(True, which='both', ls='--', alpha=0.4)
ax.legend()

plt.tight_layout()
plt.savefig(f'plots/{filename}_noise_analysis.png', dpi=300)
print(f"Saved → plots/{filename}_noise_analysis.png")
plt.show()