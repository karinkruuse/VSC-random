import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend, welch, csd, coherence

# ── CONFIG ────────────────────────────────────────────────────────────────
filename           = 'Delayline_11MHz_mix_UNDEL_DDS_400mVpp_ADC_on_inputs_1_2_and4_20260419_222428'

fmin               = 1e-4
fmax               = 1

segment_duration_s = 0.5 * 60 * 60   # segment length in seconds
PT_channel         = 4
start_time         = 15 * 60 * 60
end_time           = 0  * 60 * 60

# ── 1. LOAD ───────────────────────────────────────────────────────────────
data = np.load(f'data/{filename}.npy')

def col(name):
    return data[name].copy()

t  = col('Time (s)')
fs = 1.0 / np.median(np.diff(t))

print(f"Samples: {len(t)} | fs ≈ {fs:.4f} Hz | duration ≈ {t[-1]-t[0]:.1f} s or {(t[-1]-t[0])/3600:.2f} hours")

def load_channel(ch):
    pfx = f'Input {ch} '
    return {
        'freq':  col(pfx + 'Frequency (Hz)'),
        'phase': col(pfx + 'Phase (cyc)'),
    }

channels_full = {ch: load_channel(ch) for ch in range(1, 5)}

# ── 2. INITIAL CROPPING ───────────────────────────────────────────────────
def crop_time(t, data_dict, t_start=0, t_end=0):
    print(f"Cropping: removing {t_start} s from start and {t_end} s from end")
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

t_full, channels_full = crop_time(t, channels_full, start_time, end_time)
print(f"After cropping: {len(t_full)} samples | duration ≈ {(t_full[-1]-t_full[0])/3600:.2f} hours")

# ── 3. SEGMENT DEFINITIONS ────────────────────────────────────────────────
seg_samples = int(segment_duration_s * fs)
n_segs      = len(t_full) // seg_samples
nperseg     = int(fs / fmin)

print(f"Segment length: {segment_duration_s/3600:.2f} h ({seg_samples} samples) | Segments: {n_segs}")

# ── 4. SEGMENT LOOP ───────────────────────────────────────────────────────
cmap   = plt.get_cmap('viridis')
colors = [cmap(i / max(n_segs - 1, 1)) for i in range(n_segs)]

# Storage for per-segment scalars (integrated coherence)
t_mids          = []
mean_coh_13     = []   # ch1 vs ch3 phase
mean_coh_1j     = []   # ch1 vs jitter

# We'll accumulate lines into the axes as we go
fig1, axes1 = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
fig1.suptitle('ch1 phase vs ch3 phase — coherence analysis per segment')

fig2, axes2 = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
fig2.suptitle('ch1 phase vs timing jitter — coherence analysis per segment')



for seg_idx in range(n_segs):
    if seg_idx != 35:
        continue

    i0 = seg_idx * seg_samples
    i1 = i0 + seg_samples
    sl = slice(i0, i1)

    channels_seg = {
        ch: {k: v[sl] for k, v in channels_full[ch].items()}
        for ch in channels_full
    }

    t_mid_h = (t_full[i0] + t_full[i1 - 1]) / 2 / 3600
    t_mids.append(t_mid_h)

    # ── signals (detrended) ───────────────────────────────────────────────
    ch1_phase = detrend(channels_seg[1]['phase'], type='linear')
    ch3_phase = detrend(channels_seg[3]['phase'], type='linear')
    t_jitter  = channels_seg[PT_channel]['phase'] / channels_seg[PT_channel]['freq']
    jitter    = detrend(t_jitter, type='linear')

    nperseg_use = min(nperseg, len(ch1_phase))
    label       = f"t={t_mid_h:.1f}h"
    c           = colors[seg_idx]

    # ══════════════════════════════════════════════════════════════════════
    # ANALYSIS A: ch1 phase  vs  ch3 phase
    # ══════════════════════════════════════════════════════════════════════
    f,  S_11   = welch(ch1_phase, fs=fs, nperseg=nperseg_use)
    _,  S_33   = welch(ch3_phase, fs=fs, nperseg=nperseg_use)
    _,  S_13   = csd(ch1_phase, ch3_phase, fs=fs, nperseg=nperseg_use)
    #_,  gam2   = coherence(ch1_phase, ch3_phase, fs=fs, nperseg=nperseg_use)

    # uncorrelated noise floor estimates
    S_uncorr_1 = np.abs(S_11 - np.abs(S_13))
    S_uncorr_3 = np.abs(S_33 - np.abs(S_13))

    fmask = (f >= fmin) & (f <= fmax)

    axes1[0].loglog(f[fmask], np.sqrt(S_11[fmask]), color="black", lw=0.8, alpha=0.5, label=label)
    axes1[0].loglog(f[fmask], np.sqrt(S_uncorr_1[fmask]), color=c, lw=0.8, alpha=0.8, label=label)
    axes1[1].loglog(f[fmask], np.sqrt(S_33[fmask]), color="black", lw=0.8, alpha=0.5, label=label)
    axes1[1].loglog(f[fmask], np.sqrt(S_uncorr_3[fmask]), color=c, lw=0.8, alpha=0.8, label=label)
    #axes1[2].semilogx(f[fmask], gam2[fmask],              color=c, lw=0.8, alpha=0.8, label=label)

    #mean_coh_13.append(np.mean(gam2[fmask]))

    # ══════════════════════════════════════════════════════════════════════
    # ANALYSIS B: ch1 phase  vs  timing jitter
    # ══════════════════════════════════════════════════════════════════════
    _,  S_jj   = welch(jitter,    fs=fs, nperseg=nperseg_use)
    _,  S_1j   = csd(ch1_phase, jitter, fs=fs, nperseg=nperseg_use)
    _,  gam2_j = coherence(ch1_phase, jitter, fs=fs, nperseg=nperseg_use)

    S_uncorr_j = np.abs(S_jj - np.abs(S_1j))
    S_uncorr_1j = np.abs(S_11 - np.abs(S_1j))

    axes2[0].loglog(f[fmask], np.sqrt(S_11[fmask]),       color="black", lw=0.8, alpha=0.5, label=label)
    axes2[0].loglog(f[fmask], np.sqrt(S_uncorr_1j[fmask]), color=c, lw=0.8, alpha=0.8, label=label)
    axes2[1].loglog(f[fmask], np.sqrt(S_uncorr_j[fmask]), color=c, lw=0.8, alpha=0.8, label=label)
    axes2[1].loglog(f[fmask], np.sqrt(S_33[fmask]), color="black", lw=0.8, alpha=0.5, label=label)
    #axes2[2].semilogx(f[fmask], gam2_j[fmask],            color=c, lw=0.8, alpha=0.8, label=label)

    mean_coh_1j.append(np.mean(gam2_j[fmask]))

    print(f"Seg {seg_idx+1}/{n_segs}  t={t_mid_h:.2f}h  " )

# ── 5. DRESS FIGURE 1 (ch1 vs ch3) ───────────────────────────────────────
axes1[0].set_ylabel('ASD uncorr ch1\n(cyc/√Hz)')
axes1[1].set_ylabel('ASD uncorr ch3\n(cyc/√Hz)')

for ax in axes1:
    ax.grid(True, which='both', ls='--', alpha=0.4)
    ax.set_xlim(fmin, fmax)

sm1 = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=t_mids[0], vmax=t_mids[-1]))
sm1.set_array([])
##fig1.colorbar(sm1, ax=axes1, label='Segment midpoint (h)')
fig1.tight_layout()
fig1.savefig(f'plots/{filename}_coherence_ch1_ch3.png', dpi=300)
print(f"Saved → plots/{filename}_coherence_ch1_ch3.png")

# ── 6. DRESS FIGURE 2 (ch1 vs jitter) ────────────────────────────────────
axes2[0].set_ylabel('ASD ch1 phase\n(cyc/√Hz)')
axes2[1].set_ylabel('ASD uncorr jitter\n(s/√Hz)')

for ax in axes2:
    ax.grid(True, which='both', ls='--', alpha=0.4)
    ax.set_xlim(fmin, fmax)

sm2 = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=t_mids[0], vmax=t_mids[-1]))
sm2.set_array([])
#fig2.colorbar(sm2, ax=axes2, label='Segment midpoint (h)')
fig2.tight_layout()
fig2.savefig(f'plots/{filename}_coherence_ch1_jitter.png', dpi=300)
print(f"Saved → plots/{filename}_coherence_ch1_jitter.png")
plt.show()
# ── 7. SUMMARY: MEAN COHERENCE OVER TIME ─────────────────────────────────
"""
t_mids       = np.array(t_mids)
mean_coh_13  = np.array(mean_coh_13)
mean_coh_1j  = np.array(mean_coh_1j)

fig3, ax3 = plt.subplots(figsize=(9, 4))
ax3.plot(t_mids, mean_coh_13, 'o-', label='ch1 vs ch3 phase',   lw=1.5)
ax3.plot(t_mids, mean_coh_1j, 's-', label='ch1 vs jitter',      lw=1.5)
ax3.set_xlabel('Time (h)')
ax3.set_ylabel('Mean coherence γ²')
ax3.set_title(f'Band-averaged coherence over time  [{fmin:.0e} – {fmax:.0e} Hz]')
ax3.set_ylim(0, 1.05)
ax3.axhline(1, color='k', lw=0.5, ls='--')
ax3.legend()
ax3.grid(True, ls='--', alpha=0.5)
fig3.tight_layout()
fig3.savefig(f'plots/{filename}_coherence_summary.png', dpi=300)
print(f"Saved → plots/{filename}_coherence_summary.png")

"
"""