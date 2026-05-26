import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend, welch, decimate, correlate
from pytdi.dsp import timeshift

# ── CONFIG ────────────────────────────────────────────────────────────────
FILE_CARRIER = 'data/Carrier_20260526_134721.npy'
FILE_USB     = 'data/USB_20260526_134721.npy'
FILE_LSB     = 'data/LSB_20260526_134722.npy'
FILE_CLK     = 'data/CLK_20260526_134723.npy'

delay_s      = 4.1   # UPDATE: actual delay for this dataset
t_crop_start = 0.0            # seconds to remove from start (after sync)
t_crop_end   = 0.0            # seconds to remove from end   (after sync)
FMIN         = 9e-4           # lowest ASD frequency → sets nperseg

# Max lag to search when cross-correlating for time offset (~1 s is plenty)
SYNC_MAX_LAG_S = 2.0

# ── 1. LOAD .NPY FILES ────────────────────────────────────────────────────
def load_npy(path):
    data = np.load(path)
    def col(n): return data[n].copy()
    return {
        't':       col('Time (s)'),
        'freq_A':  col('Input A Frequency (Hz)'),
        'phase_A': col('Input A Phase (cyc)'),
        'freq_B':  col('Input B Frequency (Hz)'),
        'phase_B': col('Input B Phase (cyc)'),
    }

print("Loading files...")
carrier = load_npy(FILE_CARRIER)
usb     = load_npy(FILE_USB)
lsb     = load_npy(FILE_LSB)
clk     = load_npy(FILE_CLK)

fs     = 1.0 / np.median(np.diff(carrier['t']))
fs_clk = 1.0 / np.median(np.diff(clk['t']))
print(f"Carrier: {len(carrier['t'])} samples | fs ≈ {fs:.4f} Hz | "
      f"duration ≈ {carrier['t'][-1]-carrier['t'][0]:.1f} s")
print(f"CLK:     {len(clk['t'])} samples | fs_clk ≈ {fs_clk:.4f} Hz | "
      f"duration ≈ {clk['t'][-1]-clk['t'][0]:.1f} s")

# ── 2. DECIMATE CLK TO CARRIER SAMPLE RATE ───────────────────────────────
decimate_factor = int(round(fs_clk / fs))
print(f"Decimating CLK by factor {decimate_factor} "
      f"({fs_clk:.2f} → {fs_clk/decimate_factor:.2f} Hz, target {fs:.2f} Hz)")

# Pilot tone = CLK Input A (~41.666 MHz);  t_jitter = phase/freq [seconds]
t_jitter_clk     = clk['phase_A'] / clk['freq_A']
t_jitter_clk_dec = decimate(t_jitter_clk,  decimate_factor, zero_phase=True)
clk_freq_A_dec   = decimate(clk['freq_A'], decimate_factor, zero_phase=True)
t_clk_dec        = clk['t'][::decimate_factor]

n_dec          = min(len(t_clk_dec), len(t_jitter_clk_dec))
t_clk_dec      = t_clk_dec[:n_dec]
t_jitter_clk_dec = t_jitter_clk_dec[:n_dec]
clk_freq_A_dec   = clk_freq_A_dec[:n_dec]

# ── 3. CROSS-CORRELATION SYNC OF EACH FILE TO CLK ────────────────────────
# Strategy: detrend the frequency stream of each file and cross-correlate
# against the decimated CLK freq_A (pilot tone).  All four oscillators share
# the same 10 MHz external reference, so their frequency drifts are identical
# up to a time offset — that offset shows up as the lag of the xcorr peak.
#
# We search only within ±SYNC_MAX_LAG_S (nominally 2 s) to avoid false peaks.
# Sub-sample precision comes from fitting a parabola to the peak neighbourhood.
# After finding the offset we resample each file onto a common time grid
# anchored to CLK, which simultaneously handles the length mismatch.

max_lag_samples = int(np.ceil(SYNC_MAX_LAG_S * fs))

def xcorr_offset(sig_ref, sig_other, max_lag):
    """
    Return the lag (in samples) of sig_other relative to sig_ref.
    Positive lag  →  sig_other starts LATER than sig_ref
                     (i.e. we need to shift sig_other to the left).
    """
    x = detrend(sig_ref)
    y = detrend(sig_other)
    # Normalise so amplitude doesn't matter
    x = x / np.std(x)
    y = y / np.std(y)
    cc = correlate(x, y, mode='full')
    lags = np.arange(-(len(x)-1), len(y))
    # Restrict to search window
    win = np.abs(lags) <= max_lag
    cc_win  = cc[win]
    lags_win = lags[win]
    peak_idx = np.argmax(cc_win)
    # Sub-sample parabola fit around peak
    if 0 < peak_idx < len(cc_win) - 1:
        y0, y1, y2 = cc_win[peak_idx-1], cc_win[peak_idx], cc_win[peak_idx+1]
        delta = 0.5 * (y0 - y2) / (y0 - 2*y1 + y2)
    else:
        delta = 0.0
    lag_samples = lags_win[peak_idx] + delta
    return lag_samples

# Use the reference signal for cross-correlation.
# CLK freq_A (pilot tone, decimated) is the reference.
# Each other file contributes its freq_A (the delayed-arm signal).
# Both share the same external 10 MHz clock → their frequency envelopes track.
clk_ref_for_xcorr = detrend(clk_freq_A_dec)

def find_offset_s(other_freq_arr):
    """Find time offset of other_freq_arr relative to CLK, in seconds."""
    lag_samp = xcorr_offset(clk_ref_for_xcorr, other_freq_arr, max_lag_samples)
    return lag_samp / fs

print("\nCross-correlating files against CLK to find time offsets...")
offset_carrier_s = find_offset_s(carrier['freq_A'])
offset_usb_s     = find_offset_s(usb['freq_A'])
offset_lsb_s     = find_offset_s(lsb['freq_A'])
print(f"  Carrier offset vs CLK: {offset_carrier_s*1000:+.3f} ms")
print(f"  USB     offset vs CLK: {offset_usb_s*1000:+.3f} ms")
print(f"  LSB     offset vs CLK: {offset_lsb_s*1000:+.3f} ms")

# ── 4. RESAMPLE ALL FILES ONTO CLK TIME GRID ─────────────────────────────
# After finding each file's time offset relative to CLK, we shift its time
# axis by that offset and then interpolate onto a common grid.
# The common grid = CLK decimated time axis, restricted to the overlap of all.

def shifted_time(d, offset_s):
    """Return d['t'] shifted so it is aligned to CLK time."""
    return d['t'] + offset_s   # offset_s > 0 means file started later → shift forward

t_car_shifted = shifted_time(carrier, offset_carrier_s)
t_usb_shifted = shifted_time(usb,     offset_usb_s)
t_lsb_shifted = shifted_time(lsb,     offset_lsb_s)
# CLK reference needs no shift

# Common grid: overlap of all five time axes
t_start = max(t_clk_dec[0],   t_car_shifted[0],
              t_usb_shifted[0], t_lsb_shifted[0])
t_end   = min(t_clk_dec[-1],  t_car_shifted[-1],
              t_usb_shifted[-1], t_lsb_shifted[-1])

common_grid = t_clk_dec[(t_clk_dec >= t_start) & (t_clk_dec <= t_end)]
print(f"\nCommon time grid: {len(common_grid)} samples "
      f"| {(common_grid[-1]-common_grid[0])/3600:.2f} h")

def onto_grid(t_shifted, arr):
    """Interpolate arr (on t_shifted) onto common_grid."""
    return np.interp(common_grid, t_shifted, arr)

# Interpolate every channel onto the common grid
car_pA = onto_grid(t_car_shifted, carrier['phase_A'])
car_fA = onto_grid(t_car_shifted, carrier['freq_A'])
car_pB = onto_grid(t_car_shifted, carrier['phase_B'])
car_fB = onto_grid(t_car_shifted, carrier['freq_B'])

usb_pA = onto_grid(t_usb_shifted, usb['phase_A'])
usb_fA = onto_grid(t_usb_shifted, usb['freq_A'])
usb_pB = onto_grid(t_usb_shifted, usb['phase_B'])
usb_fB = onto_grid(t_usb_shifted, usb['freq_B'])

lsb_pA = onto_grid(t_lsb_shifted, lsb['phase_A'])
lsb_fA = onto_grid(t_lsb_shifted, lsb['freq_A'])
lsb_pB = onto_grid(t_lsb_shifted, lsb['phase_B'])
lsb_fB = onto_grid(t_lsb_shifted, lsb['freq_B'])

clk_jitter  = onto_grid(t_clk_dec, t_jitter_clk_dec)
clk_freq_pt = onto_grid(t_clk_dec, clk_freq_A_dec)

t = common_grid   # from here on, t is the shared time axis

# ── 5. CROP TIME (optional, e.g. remove modulation-change transient) ──────
def crop_time(t, arrays, t_start_cut, t_end_cut):
    i0 = np.searchsorted(t, t[0]  + t_start_cut)
    i1 = np.searchsorted(t, t[-1] - t_end_cut)
    if i0 >= i1:
        raise ValueError("Crop window removes all data.")
    sl = slice(i0, i1)
    return t[sl], [a[sl] for a in arrays]

t, (
    car_pA, car_fA, car_pB, car_fB,
    usb_pA, usb_fA, usb_pB, usb_fB,
    lsb_pA, lsb_fA, lsb_pB, lsb_fB,
    clk_jitter, clk_freq_pt,
) = crop_time(t, [
    car_pA, car_fA, car_pB, car_fB,
    usb_pA, usb_fA, usb_pB, usb_fB,
    lsb_pA, lsb_fA, lsb_pB, lsb_fB,
    clk_jitter, clk_freq_pt,
], t_crop_start, t_crop_end)

duration = t[-1] - t[0]
print(f"After crop: {len(t)} samples | duration = {duration/3600:.2f} h")

# ── 6. APPLY DELAY TO REFERENCE (B) SIGNALS AND JITTER ───────────────────
delay_samples = delay_s * fs
print(f"Delay: {delay_s:.6f} s = {delay_samples:.2f} samples")

def apply_delay(x, tau):
    return timeshift(x, -tau)

car_pB_dly  = apply_delay(car_pB,     delay_samples)
car_fB_dly  = apply_delay(car_fB,     delay_samples)
usb_pB_dly  = apply_delay(usb_pB,     delay_samples)
usb_fB_dly  = apply_delay(usb_fB,     delay_samples)
lsb_pB_dly  = apply_delay(lsb_pB,     delay_samples)
lsb_fB_dly  = apply_delay(lsb_fB,     delay_samples)
tj_dly       = apply_delay(clk_jitter, delay_samples)

# ── 7. CROP EDGES AFTER TIMESHIFT ─────────────────────────────────────────
n_crop = int(np.ceil(abs(delay_samples))) + 5

def crop_edges(t, arrays, n):
    sl = slice(n, -n)
    return t[sl], [a[sl] for a in arrays]

t, (
    car_pA, car_fA, car_pB, car_fB, car_pB_dly, car_fB_dly,
    usb_pA, usb_fA, usb_pB, usb_fB, usb_pB_dly, usb_fB_dly,
    lsb_pA, lsb_fA, lsb_pB, lsb_fB, lsb_pB_dly, lsb_fB_dly,
    clk_jitter, tj_dly,
) = crop_edges(t, [
    car_pA, car_fA, car_pB, car_fB, car_pB_dly, car_fB_dly,
    usb_pA, usb_fA, usb_pB, usb_fB, usb_pB_dly, usb_fB_dly,
    lsb_pA, lsb_fA, lsb_pB, lsb_fB, lsb_pB_dly, lsb_fB_dly,
    clk_jitter, tj_dly,
], n_crop)

print(f"Post-shift length: {len(t)} samples")

# ── 8. DETREND ────────────────────────────────────────────────────────────
car_pA_d   = detrend(car_pA)
car_pB_d   = detrend(car_pB_dly)
usb_pA_d   = detrend(usb_pA)
usb_pB_d   = detrend(usb_pB_dly)
lsb_pA_d   = detrend(lsb_pA)
lsb_pB_d   = detrend(lsb_pB_dly)
tj_d       = detrend(clk_jitter)
tj_dly_d   = detrend(tj_dly)

delta_tj = tj_d - tj_dly_d   # differential clock jitter [seconds]

# ── 9. TDI COMBINATIONS ───────────────────────────────────────────────────
tdi_carrier = car_pA_d - car_pB_d - car_fB_dly * delta_tj
tdi_usb     = usb_pA_d - usb_pB_d - usb_fB_dly * delta_tj
tdi_lsb     = lsb_pA_d - lsb_pB_d - lsb_fB_dly * delta_tj

# ── 10. ASD COMPUTATION ───────────────────────────────────────────────────
def compute_asd(x, fs, fmin=FMIN):
    nperseg = min(int(fs / fmin), len(x))
    f, psd = welch(x, fs=fs, nperseg=nperseg, detrend='constant')
    return f, np.sqrt(psd)

print("\nComputing ASDs...")
f_car_res,  asd_car_res  = compute_asd(detrend(tdi_carrier), fs)
f_car_dly,  asd_car_dly  = compute_asd(car_pA_d, fs)
f_car_pure, asd_car_pure = compute_asd(detrend(car_pB), fs)

f_usb_res,  asd_usb_res  = compute_asd(detrend(tdi_usb), fs)
f_usb_dly,  asd_usb_dly  = compute_asd(usb_pA_d, fs)
f_usb_pure, asd_usb_pure = compute_asd(detrend(usb_pB), fs)

f_lsb_res,  asd_lsb_res  = compute_asd(detrend(tdi_lsb), fs)
f_lsb_dly,  asd_lsb_dly  = compute_asd(lsb_pA_d, fs)
f_lsb_pure, asd_lsb_pure = compute_asd(detrend(lsb_pB), fs)

# ── 11. PLOTS ─────────────────────────────────────────────────────────────
title_info = (f'delay={delay_s:.8f} s | {duration/3600:.1f} h | '
              f'offsets: carrier={offset_carrier_s*1e3:.1f} ms, '
              f'USB={offset_usb_s*1e3:.1f} ms, LSB={offset_lsb_s*1e3:.1f} ms')

fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
fig.suptitle('TDI Residuals — Carrier / USB / LSB\n' + title_info, fontsize=10)

for ax, label, f_res, a_res, f_dly, a_dly, f_pur, a_pur in [
    (axes[0], 'Carrier', f_car_res, asd_car_res, f_car_dly, asd_car_dly, f_car_pure, asd_car_pure),
    (axes[1], 'USB',     f_usb_res, asd_usb_res, f_usb_dly, asd_usb_dly, f_usb_pure, asd_usb_pure),
    (axes[2], 'LSB',     f_lsb_res, asd_lsb_res, f_lsb_dly, asd_lsb_dly, f_lsb_pure, asd_lsb_pure),
]:
    ax.loglog(f_res, a_res,  lw=1.5, label='TDI Residual')
    ax.loglog(f_dly, a_dly,  lw=2,   label='Delayed (A)', alpha=0.8)
    ax.loglog(f_pur, a_pur,  lw=1,   label='Undelayed (B)', alpha=0.7)
    ax.set_title(label)
    ax.set_xlabel('Frequency (Hz)')
    ax.grid(True, which='both', ls='--', alpha=0.5)
    ax.legend()

axes[0].set_ylabel('ASD (cyc / √Hz)')
plt.tight_layout()
plt.savefig('plots/tdi_asd_panels.png', dpi=150)
print("Saved: plots/tdi_asd_panels.png")

fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.loglog(f_car_res, asd_car_res, lw=1.5, label='Carrier TDI residual')
ax2.loglog(f_usb_res, asd_usb_res, lw=1.5, label='USB TDI residual')
ax2.loglog(f_lsb_res, asd_lsb_res, lw=1.5, label='LSB TDI residual')
ax2.loglog(f_car_dly, asd_car_dly, lw=1, ls='--', alpha=0.6, label='Carrier delayed (A)')
ax2.loglog(f_usb_dly, asd_usb_dly, lw=1, ls='--', alpha=0.6, label='USB delayed (A)')
ax2.loglog(f_lsb_dly, asd_lsb_dly, lw=1, ls='--', alpha=0.6, label='LSB delayed (A)')
ax2.set_xlabel('Frequency (Hz)')
ax2.set_ylabel('ASD (cyc / √Hz)')
ax2.set_title('TDI Residuals — All Channels\n' + title_info)
ax2.grid(True, which='both', ls='--', alpha=0.5)
ax2.legend()
plt.tight_layout()
plt.savefig('plots/tdi_asd_overlay.png', dpi=150)
print("Saved: plots/tdi_asd_overlay.png")
plt.show()