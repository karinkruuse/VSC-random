import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend, welch
from scipy.optimize import minimize_scalar
from pytdi.dsp import timeshift

# ── CONFIG ────────────────────────────────────────────────────────────────
filename = 'Delayline_11MHz_mix_UNDEL_DDS_400mVpp_ADC_on_inputs_1_2_and4_20260419_222428'
delay_s_init = 3.9990

fmin = 1e-4
fmax = 1

search_width = 1e-3

segment_duration_s = 1 * 60 * 60   # segment length in seconds (1 hour)
PT_channel = 4
start_time = 15 * 60 * 60
end_time   = 0 * 60 * 60

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
seg_samples   = int(segment_duration_s * fs)
n_segs        = len(t_full) // seg_samples

print(f"Segment length: {segment_duration_s/3600:.1f} h ({seg_samples} samples) | Number of segments: {n_segs}")

# ── 4. GLOBAL FIXES (CRITICAL) ────────────────────────────────────────────
max_delay        = delay_s_init + search_width
n_crop_fixed     = int(np.ceil(abs(max_delay * fs))) + 3
nperseg_fixed    = int(fs / fmin)

# ── 5. CORE PIPELINE (operates on externally supplied arrays) ─────────────
def compute_tdi_arrays(channels_seg, t_jitter_seg, delay_s):
    """
    channels_seg  : dict {1: {'freq': ..., 'phase': ...}, 3: ...}
    t_jitter_seg  : 1-D array
    delay_s       : scalar delay to apply
    """
    delay_samples = delay_s * fs

    ch3_phase_dly = timeshift(channels_seg[3]['phase'], -delay_samples)
    ch3_freq_dly  = timeshift(channels_seg[3]['freq'],  -delay_samples)
    tj_dly        = timeshift(t_jitter_seg,             -delay_samples)

    sl = slice(n_crop_fixed, -n_crop_fixed)

    ch1_phase_d = detrend(channels_seg[1]['phase'][sl], type='linear')
    ch3_phase_d = detrend(ch3_phase_dly[sl],            type='linear')
    # Fix 4: detrend the difference as a whole, not each signal independently
    tj_diff_d   = detrend(t_jitter_seg[sl] - tj_dly[sl], type='linear')

    tdi = (
        ch1_phase_d
        - ch3_phase_d
        - ch3_freq_dly[sl] * tj_diff_d
    )
    return tdi


def tdi_cost_arrays(channels_seg, t_jitter_seg, delay_s):
    tdi = compute_tdi_arrays(channels_seg, t_jitter_seg, delay_s)

    f, psd  = welch(tdi, fs=fs, nperseg=min(nperseg_fixed, len(tdi)), detrend='constant')

    #plt.loglog(f, psd, label=f'delay={delay_s:.6f} s')
    #plt.xlim(fmin/10, fmax*10)
    #plt.show()

    mask = (f >= fmin)
    if fmax is not None:
        mask &= (f <= fmax)

    return np.trapezoid(psd[mask], f[mask])


# ── 6. LOOP OVER SEGMENTS ─────────────────────────────────────────────────
print(f"Measuring timing jitters from channel {PT_channel}")

seg_results = []   # list of dicts, one per segment

for seg_idx in range(n_segs):
    i0 = seg_idx * seg_samples
    i1 = i0 + seg_samples
    sl = slice(i0, i1)

    # slice channels for this segment
    channels_seg = {
        ch: {k: v[sl] for k, v in channels_full[ch].items()}
        for ch in channels_full
    }

    t_jitter_seg = channels_seg[PT_channel]['phase'] / channels_seg[PT_channel]['freq']

    t_mid_h = (t_full[i0] + t_full[i1 - 1]) / 2 / 3600   # midpoint in hours

    print(f"\n── Segment {seg_idx + 1}/{n_segs}  (t_mid = {t_mid_h:.2f} h) ──")

    prev_delay = delay_s_init # seg_results[-1]['delay_opt'] if seg_results else delay_s_init
    # optimise
    result = minimize_scalar(
        lambda d: tdi_cost_arrays(channels_seg, t_jitter_seg, d),
        bounds=(prev_delay - search_width, prev_delay + search_width),
        method='bounded',
        options={'xatol': 1e-9, 'maxiter': 500}
    )

    delay_opt = result.x
    cost_init = tdi_cost_arrays(channels_seg, t_jitter_seg, prev_delay)
    cost_opt  = result.fun

    #print(f"  init delay : {delay_s_init:.10f} s  (cost {cost_init:.4e})")
    print(f"  opt  delay : {delay_opt:.10f} s  (cost {cost_opt:.4e})")

    # compute and store ASD for this segment at optimal delay
    tdi_opt      = compute_tdi_arrays(channels_seg, t_jitter_seg, delay_opt)
    nperseg_seg  = min(nperseg_fixed, len(tdi_opt))
    f_asd, psd   = welch(tdi_opt, fs=fs, nperseg=nperseg_seg, detrend='constant')
    asd_opt      = np.sqrt(psd)

    seg_results.append({
        't_mid_h':   t_mid_h,
        'delay_opt': delay_opt,
        'cost_init': cost_init,
        'cost_opt':  cost_opt,
        'f_asd':     f_asd,
        'asd_opt':   asd_opt,
    })

# ── 7. SUMMARY TABLE ──────────────────────────────────────────────────────
print("\n══ SUMMARY ══════════════════════════════════════════════════════════")
print(f"{'Seg':>4}  {'t_mid (h)':>10}  {'delay_opt (s)':>18}  {'cost_init':>12}  {'cost_opt':>12}")
for i, r in enumerate(seg_results):
    print(f"{i+1:>4}  {r['t_mid_h']:>10.3f}  {r['delay_opt']:>18.10f}  {r['cost_init']:>12.4e}  {r['cost_opt']:>12.4e}")

# ── 8. PLOT: DELAY VS TIME ────────────────────────────────────────────────
t_mids      = np.array([r['t_mid_h']   for r in seg_results])
delays_opt  = np.array([r['delay_opt'] for r in seg_results])
costs_init  = np.array([r['cost_init'] for r in seg_results])
costs_opt   = np.array([r['cost_opt']  for r in seg_results])

fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

# -- top panel: estimated delay
ax = axes[0]
ax.yaxis.set_major_formatter(plt.matplotlib.ticker.ScalarFormatter(useOffset=False))
ax.ticklabel_format(style='plain', axis='y')
ax.plot(t_mids, delays_opt, 'o-', color='C0', ms=6, lw=1.5, label='minimized delay')
#ax.axhline(delay_s_init, color='k', ls='--', lw=1, label=f'init = {delay_s_init} s')
#ax.axhline(np.mean(delays_opt), color='C1', ls=':', lw=1.2, label=f'mean opt = {np.mean(delays_opt):.10f} s')
ax.set_ylabel('Delay (s)')
ax.set_title(f'Segmented delay optimisation — {segment_duration_s/3600:.1f} h segments')
ax.legend(fontsize=8)
ax.grid(True, ls='--', alpha=0.5)

# -- bottom panel: cost improvement
ax = axes[1]
ax.plot(t_mids, costs_init, 's--', color='C2', ms=5, lw=1, alpha=0.8, label='cost (init delay)')
ax.plot(t_mids, costs_opt,  'o-',  color='C3', ms=6, lw=1.5,          label='cost (opt delay)')
ax.set_xlabel('Time (h)')
ax.set_ylabel('Integrated PSD (cost)')
ax.legend(fontsize=8)
ax.grid(True, ls='--', alpha=0.5)
ax.set_yscale('log')

plt.tight_layout()
plt.savefig(f'plots/{filename}_segmented_delay.png', dpi=300)
print(f"\nPlot saved → plots/{filename}_segmented_delay.png")
plt.show()
# ── 9. PLOT: ASD PER SEGMENT ──────────────────────────────────────────────
cmap   = plt.get_cmap('viridis')
colors = [cmap(i / max(n_segs - 1, 1)) for i in range(n_segs)]

fig, ax = plt.subplots(figsize=(9, 5))

for i, r in enumerate(seg_results):
    ax.loglog(
        r['f_asd'], r['asd_opt'],
        color=colors[i], lw=1.0, alpha=0.85,
        label=f"seg {i+1}  t={r['t_mid_h']:.1f}h  τ={r['delay_opt']:.8f}s",
    )

ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('ASD (cyc / √Hz)')
ax.set_title(f'ASD per segment — {segment_duration_s/3600:.1f} h segments')
ax.set_xlim(fmin, fmax)
ax.grid(True, which='both', ls='--', alpha=0.4)
#ax.legend(fontsize=7, loc='upper right')

# colour bar to show time progression
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=t_mids[0], vmax=t_mids[-1]))
sm.set_array([])
fig.colorbar(sm, ax=ax, label='Segment midpoint in the full data (h)')

plt.tight_layout()
plt.savefig(f'plots/{filename}_segmented_asd.png', dpi=300)
print(f"Plot saved → plots/{filename}_segmented_asd.png")