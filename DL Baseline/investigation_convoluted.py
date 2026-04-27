import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.signal import detrend, welch, csd
from pytdi.dsp import timeshift

# ── CONFIG ────────────────────────────────────────────────────────────────
filename           = 'Delayline_opticalbaseline_100hr_measurement_2_20260424_173355'

fmin               = 1e-4
fmax               = 1

segment_duration_s = 0.5 * 60 * 60
PT_channel         = 2
start_time         = 0  * 60 * 60
end_time           = 2  * 60 * 60
nr_of_channels     = 3

delay_s            = 3.9989879870   # best-known delay for TDI

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

channels_full = {ch: load_channel(ch) for ch in range(1, nr_of_channels + 1)}

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
seg_samples  = int(segment_duration_s * fs)
n_segs       = len(t_full) // seg_samples
nperseg      = int(fs / fmin)
n_crop_fixed = int(np.ceil(abs(delay_s * fs))) + 3

print(f"Segment length: {segment_duration_s/3600:.2f} h ({seg_samples} samples) | Segments: {n_segs}")

# ── 4. FIGURES ────────────────────────────────────────────────────────────
cmap   = plt.get_cmap('viridis')
colors = [cmap(i / max(n_segs - 1, 1)) for i in range(n_segs)]
t_mids = []

# fig1: uncorrelated floor — ch1 vs ch3
fig1, axes1 = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
fig1.suptitle('Uncorrelated noise floor: ch1 vs ch3 phase')

# fig2: uncorrelated floor — ch1 vs jitter
fig2, axes2 = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
fig2.suptitle('Uncorrelated noise floor: ch1 phase vs timing jitter')

# fig3: TDI ASD vs uncorrelated floor — the key comparison
fig3, ax3 = plt.subplots(figsize=(10, 5))
ax3.set_title('TDI residual ASD vs uncorrelated noise floor (ch1–ch3)')

# fig4: transfer function ch1 → ch3 (magnitude + phase)
fig4, axes4 = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
fig4.suptitle('Transfer function ch1 → ch3  (H = S₁₃ / S₁₁)')

# fig5: suppression ratios
fig5, axes5 = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
fig5.suptitle('Noise suppression ratios')

# ── 5. SEGMENT LOOP ───────────────────────────────────────────────────────
print(f"Timing jitter from channel {PT_channel}")

for seg_idx in range(n_segs):
    i0 = seg_idx * seg_samples
    i1 = i0 + seg_samples
    sl = slice(i0, i1)

    channels_seg = {
        ch: {k: v[sl] for k, v in channels_full[ch].items()}
        for ch in channels_full
    }

    t_mid_h = (t_full[i0] + t_full[i1 - 1]) / 2 / 3600
    t_mids.append(t_mid_h)

    label       = f"t={t_mid_h:.1f}h"
    c           = colors[seg_idx]
    nperseg_use = min(nperseg, len(channels_seg[1]['phase']))

    def fmask(f):
        return (f >= fmin) & (f <= fmax)

    # ── detrended signals (no delay — for floor estimation) ───────────────
    ch1_phase = detrend(channels_seg[1]['phase'], type='linear')
    ch3_phase = detrend(channels_seg[3]['phase'], type='linear')
    t_jitter  = channels_seg[PT_channel]['phase'] / channels_seg[PT_channel]['freq']
    jitter    = detrend(t_jitter, type='linear')

    # ══════════════════════════════════════════════════════════════════════
    # FLOOR A: ch1 vs ch3
    # ══════════════════════════════════════════════════════════════════════
    f,  S_11 = welch(ch1_phase, fs=fs, nperseg=nperseg_use)
    _,  S_33 = welch(ch3_phase, fs=fs, nperseg=nperseg_use)
    _,  S_13 = csd(ch1_phase, ch3_phase, fs=fs, nperseg=nperseg_use)

    S_uncorr_1 = np.abs(S_11 - np.abs(S_13))
    S_uncorr_3 = np.abs(S_33 - np.abs(S_13))

    fm = fmask(f)
    axes1[0].loglog(f[fm], np.sqrt(S_11[fm]),       color='k', lw=0.7, alpha=0.3)
    axes1[0].loglog(f[fm], np.sqrt(S_uncorr_1[fm]), color=c,   lw=0.8, alpha=0.85, label=label)
    axes1[1].loglog(f[fm], np.sqrt(S_33[fm]),       color='k', lw=0.7, alpha=0.3)
    axes1[1].loglog(f[fm], np.sqrt(S_uncorr_3[fm]), color=c,   lw=0.8, alpha=0.85, label=label)

    # ══════════════════════════════════════════════════════════════════════
    # FLOOR B: ch1 vs jitter
    # ══════════════════════════════════════════════════════════════════════
    _,  S_jj = welch(jitter,    fs=fs, nperseg=nperseg_use)
    _,  S_1j = csd(ch1_phase, jitter, fs=fs, nperseg=nperseg_use)

    S_uncorr_j  = np.abs(S_jj  - np.abs(S_1j))
    S_uncorr_1j = np.abs(S_11  - np.abs(S_1j))

    axes2[0].loglog(f[fm], np.sqrt(S_11[fm]),        color='k', lw=0.7, alpha=0.3)
    axes2[0].loglog(f[fm], np.sqrt(S_uncorr_1j[fm]), color=c,   lw=0.8, alpha=0.85, label=label)
    axes2[1].loglog(f[fm], np.sqrt(S_jj[fm]),        color='k', lw=0.7, alpha=0.3)
    axes2[1].loglog(f[fm], np.sqrt(S_uncorr_j[fm]),  color=c,   lw=0.8, alpha=0.85, label=label)

    # ══════════════════════════════════════════════════════════════════════
    # TDI COMBO (delay applied to ch3)
    # ══════════════════════════════════════════════════════════════════════
    delay_samples = delay_s * fs

    ch3_phase_dly = timeshift(channels_seg[3]['phase'], -delay_samples)
    ch3_freq_dly  = timeshift(channels_seg[3]['freq'],  -delay_samples)
    tj_dly        = timeshift(t_jitter,                 -delay_samples)

    sl_crop = slice(n_crop_fixed, -n_crop_fixed)

    ch1_phase_d = detrend(channels_seg[1]['phase'][sl_crop], type='linear')
    ch3_phase_d = detrend(ch3_phase_dly[sl_crop],            type='linear')
    tj_diff_d   = detrend(t_jitter[sl_crop] - tj_dly[sl_crop], type='linear')

    tdi = ch1_phase_d - ch3_phase_d - ch3_freq_dly[sl_crop] * tj_diff_d

    nperseg_tdi    = min(nperseg_use, len(tdi))
    f_tdi, psd_tdi = welch(tdi, fs=fs, nperseg=nperseg_tdi, detrend='constant')
    fm_tdi         = fmask(f_tdi)

    # solid = TDI residual, dashed = uncorrelated floor, same colour = same segment
    ax3.loglog(f_tdi[fm_tdi], np.sqrt(psd_tdi[fm_tdi]), color=c, lw=1.0, alpha=0.85)
    ax3.loglog(f[fm],         np.sqrt(S_uncorr_1[fm]),  color=c, lw=1.0, alpha=0.85, ls='--')

    # ══════════════════════════════════════════════════════════════════════
    # TRANSFER FUNCTION ch1 → ch3:  H = S₁₃ / S₁₁
    # ══════════════════════════════════════════════════════════════════════
    H_13     = S_13 / S_11                      # complex transfer function
    H_mag    = np.abs(H_13)                     # magnitude (should be ~1 if signals match)
    H_phase  = np.unwrap(np.angle(H_13))        # phase in radians — slope = -2π·delay

    # delay estimate from phase slope (linear fit weighted by |S_13|)
    f_fit   = f[fm]
    ph_fit  = H_phase[fm]
    w_fit   = np.abs(S_13[fm])
    coeffs  = np.polyfit(f_fit, ph_fit, 1, w=w_fit)
    delay_from_phase = -coeffs[0] / (2 * np.pi)
    phase_fit_line   = np.polyval(coeffs, f_fit)

    axes4[0].semilogx(f[fm], H_mag[fm],   color=c, lw=0.8, alpha=0.85, label=label)
    axes4[1].semilogx(f[fm], H_phase[fm], color=c, lw=0.8, alpha=0.85,
                      label=f"{label}  τ={delay_from_phase:.8f}s")
    axes4[1].semilogx(f_fit, phase_fit_line, color=c, lw=0.5, alpha=0.5, ls='--')

    # ══════════════════════════════════════════════════════════════════════
    # SUPPRESSION RATIOS
    # ══════════════════════════════════════════════════════════════════════
    # Ratio 1: TDI / ch1  — how much laser noise is suppressed
    # interpolate psd_tdi onto f grid (they may differ slightly due to cropping)
    psd_tdi_interp = np.interp(f, f_tdi, psd_tdi)
    ratio_suppression = np.sqrt(psd_tdi_interp / S_11)

    # Ratio 2: TDI / uncorrelated floor  — how close to the fundamental limit
    ratio_to_floor = np.sqrt(psd_tdi_interp / (S_uncorr_1 + 1e-300))  # guard /0

    axes5[0].semilogx(f[fm], ratio_suppression[fm], color=c, lw=0.8, alpha=0.85, label=label)
    axes5[1].semilogx(f[fm], ratio_to_floor[fm],    color=c, lw=0.8, alpha=0.85, label=label)

    print(f"Seg {seg_idx+1}/{n_segs}  t={t_mid_h:.2f}h  delay_from_phase={delay_from_phase:.8f}s")

# ── 6. DRESS FIGURES ──────────────────────────────────────────────────────
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=t_mids[0], vmax=t_mids[-1]))
sm.set_array([])

# fig1
axes1[0].set_ylabel('ASD ch1 phase\n(cyc/√Hz)')
axes1[1].set_ylabel('ASD ch3 phase\n(cyc/√Hz)')
axes1[1].set_xlabel('Frequency (Hz)')
for ax in axes1:
    ax.grid(True, which='both', ls='--', alpha=0.4)
    ax.set_xlim(fmin, fmax)
fig1.colorbar(sm, ax=axes1, label='Segment midpoint (h)')
fig1.tight_layout()
fig1.savefig(f'plots/{filename}_floor_ch1_ch3.png', dpi=300)
print(f"Saved → plots/{filename}_floor_ch1_ch3.png")

# fig2
axes2[0].set_ylabel('ASD ch1 phase\n(cyc/√Hz)')
axes2[1].set_ylabel('ASD jitter\n(s/√Hz)')
axes2[1].set_xlabel('Frequency (Hz)')
for ax in axes2:
    ax.grid(True, which='both', ls='--', alpha=0.4)
    ax.set_xlim(fmin, fmax)
fig2.colorbar(sm, ax=axes2, label='Segment midpoint (h)')
fig2.tight_layout()
fig2.savefig(f'plots/{filename}_floor_ch1_jitter.png', dpi=300)
print(f"Saved → plots/{filename}_floor_ch1_jitter.png")

# fig3
legend_handles = [
    Line2D([0], [0], color='grey', lw=1.2,               label='TDI residual ASD'),
    Line2D([0], [0], color='grey', lw=1.2, ls='--',      label='Uncorrelated floor (ch1 − |S₁₃|)'),
]
ax3.legend(handles=legend_handles, fontsize=9)
ax3.set_xlabel('Frequency (Hz)')
ax3.set_ylabel('ASD (cyc/√Hz)')
ax3.grid(True, which='both', ls='--', alpha=0.4)
ax3.set_xlim(fmin, fmax)
fig3.colorbar(sm, ax=ax3, label='Segment midpoint (h)')
fig3.tight_layout()
fig3.savefig(f'plots/{filename}_tdi_vs_floor.png', dpi=300)
print(f"Saved → plots/{filename}_tdi_vs_floor.png")

# fig4
axes4[0].set_ylabel('|H₁₃| magnitude')
axes4[1].set_ylabel('∠H₁₃ phase (rad)')
axes4[1].set_xlabel('Frequency (Hz)')
axes4[0].axhline(1, color='k', lw=0.8, ls='--', alpha=0.5)
axes4[1].legend(fontsize=6, loc='upper right')
for ax in axes4:
    ax.grid(True, which='both', ls='--', alpha=0.4)
    ax.set_xlim(fmin, fmax)
fig4.colorbar(sm, ax=axes4, label='Segment midpoint (h)')
fig4.tight_layout()
fig4.savefig(f'plots/{filename}_transfer_fn.png', dpi=300)
print(f"Saved → plots/{filename}_transfer_fn.png")

# fig5
axes5[0].set_ylabel('TDI / ch1 ASD (suppression factor)')
axes5[1].set_ylabel('TDI / uncorr floor  (1 = at limit)')
axes5[1].set_xlabel('Frequency (Hz)')
axes5[1].axhline(1, color='k', lw=1.0, ls='--', alpha=0.7, label='floor limit')
axes5[1].legend(fontsize=8)
for ax in axes5:
    ax.grid(True, which='both', ls='--', alpha=0.4)
    ax.set_xlim(fmin, fmax)
fig5.colorbar(sm, ax=axes5, label='Segment midpoint (h)')
fig5.tight_layout()
fig5.savefig(f'plots/{filename}_suppression_ratios.png', dpi=300)
print(f"Saved → plots/{filename}_suppression_ratios.png")

plt.show()