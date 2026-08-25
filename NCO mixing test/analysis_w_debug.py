import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend
from pytdi.dsp import timeshift
from scipy.signal import welch

# ── CONFIG ────────────────────────────────────────────────────────────────
filename      = 'BaselineW250MHz_20260811_141659'
delay_s       = 4.29999
start_time    = 0 * 60 * 60   # seconds to crop from start
end_time      = 0 * 60 * 60   # seconds to crop from end

# Set to False if the input file only has channels 1-3 (no delayed sideband
# data), in which case the sideband-based alternative TDI combo can't be
# computed and everything related to it is skipped.
ENABLE_SIDEBAND = False

# channel roles within data/MokuPhasemeterData_20260808_135900.npy -- per the
# txt header's "% delayed carrier, PT, carrier, delayes SB" line, which lists
# Inputs 1-4 in that order
UNDELAYED_INPUT  = 3   # carrier -- direct/undelayed
DELAYED_INPUT    = 1   # delayed carrier -- gets time-shifted
PT_INPUT         = 2   # pilot tone, co-located with the delayed channel
DELAYED_SB_INPUT = 4   # delayed sideband -- for the alt residual combo

min_f = 5e-4

# ── 0. DOWNLOAD FROM MOKU PRO (optional) ────────────────────────────────────
# Requires mokucli on PATH (installer at
# https://liquidinstruments.com/products/utilities/, not a pip package) and
# the Moku Pro reachable over the Ethernet link -- find its IP in the Moku
# app under Settings > Network, or run `mokucli list` to discover it.
MOKU_IP = '10.117.24.124'   # <-- set this to your Moku Pro's IP

if (False):
    import subprocess
    try:
        os.makedirs('data', exist_ok=True)
        li_path = f'data/{filename}.li'

        if os.path.exists(li_path):
            os.remove(li_path)  # force a fresh pull even if a stale copy is sitting here

        print(f"Downloading {filename}.li from Moku Pro at {MOKU_IP} ...")
        subprocess.run(
            ['mokucli', 'files', 'download', MOKU_IP, '--name', f'{filename}.li'],
            cwd='data', check=True,
        )

        print(f"Converting {filename}.li -> {filename}.npy (+ .txt header) ...")
        subprocess.run(
            ['mokucli', 'convert', li_path, '--format', 'npy'],
            check=True,
        )

        os.remove(li_path)  # only the .npy and .txt are kept
    except subprocess.CalledProcessError as e:
        print(f"Error during Moku Pro download/convert: {e}")


# ── 1. LOAD ───────────────────────────────────────────────────────────────
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

# channel 1 = undelayed/direct carrier, channel 3 = delayed carrier, channel
# 'pt' = pilot tone for jitter (kept as 1/3/pt to match the rest of the
# pipeline below, which was written for a 4-channel Moku layout)
channels = {
    1:    load_input(UNDELAYED_INPUT),
    3:    load_input(DELAYED_INPUT),
    'pt': load_input(PT_INPUT),
}
if ENABLE_SIDEBAND:
    channels['sb'] = load_input(DELAYED_SB_INPUT)

# ── 2. OPTIONAL INITIAL CROPPING ──────────────────────────────────────────
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

duration = t[-1] - t[0]
print(f"Duration: {duration:.1f} s or {duration/3600:.2f} hours")
start_time = 0 * 60 * 60
end_time = 0 * 60 * 60
t, channels = crop_time(t, channels, start_time, end_time)

# ── 3. DERIVED SIGNALS ────────────────────────────────────────────────────

print(f"Measuring timing jitters from pilot tone (Input {PT_INPUT})")
t_jitter = channels['pt']['phase'] / channels['pt']['freq']

#f0 = channels[4]['freq'].mean()
#print(f"Reference frequency (ch4 mean): {f0:.6f} Hz")

delay_samples = delay_s * fs
print(f"Delay: {delay_s:.3f} s = {delay_samples:.2f} samples")

# ── 4. APPLY DELAYS ───────────────────────────────────────────────────────
def apply_delay(x, tau):
    # the delayed carrier (channel 3) lags the direct carrier (channel 1) by
    # delay_s, so it needs to be *advanced* (positive shift) to land back on
    # channel 1's timebase -- NOT delayed further.
    return timeshift(x, tau)

ch3_phase_dly = apply_delay(channels[3]['phase'], delay_samples)
ch3_freq_dly  = apply_delay(channels[3]['freq'],  delay_samples)
tj_dly        = apply_delay(t_jitter,             delay_samples)

# main TDI combo:
#   ch1_phase - apply_delay(ch3_phase - (ch3_freq/pt_freq)*pt_phase) - (ch1_freq/pt_freq)*pt_phase
# ch3 (dict key 3) is the channel that needs the software delay applied to
# align it onto ch1's (dict key 1) timebase; ch1 stays as the leading,
# undelayed term.
freq_ratio_u         = channels[1]['freq'] / channels['pt']['freq']
freq_ratio_d         = channels[3]['freq'] / channels['pt']['freq']
correction_term      = channels[3]['phase'] - freq_ratio_d * channels['pt']['phase']
correction_term_dly  = apply_delay(correction_term, delay_samples)

if ENABLE_SIDEBAND:
    # the delayed sideband is already physically delayed (recorded after the
    # signal passed through the delay line) -- do NOT shift it again in software.
    sb_phase      = channels['sb']['phase']

# ── 5. CROP AFTER TIMESHIFT (IMPORTANT) ───────────────────────────────────
def crop_edges(t, arrays, n_crop):
    sl = slice(n_crop, -n_crop)
    t_new = t[sl]
    arrays_new = [a[sl] for a in arrays]
    return t_new, arrays_new

n_crop = int(np.ceil(abs(delay_samples))) + 5  # +5 for safety

crop_arrays = [
    channels[1]['phase'],
    channels[1]['freq'],   # <-- add this
    channels[3]['phase'],
    ch3_phase_dly,
    ch3_freq_dly,
    channels[3]['freq'],
    t_jitter,
    tj_dly,
    channels['pt']['phase'],
    channels['pt']['freq'],
    freq_ratio_u,
    correction_term_dly,
]
if ENABLE_SIDEBAND:
    crop_arrays += [sb_phase, channels['sb']['freq']]

t, (
    ch1_phase,
    ch1_freq,          # <-- add this
    ch3_phase,
    ch3_phase_dly,
    ch3_freq_dly,
    ch3_freq,
    t_jitter,
    tj_dly,
    pt_phase,
    pt_freq,
    freq_ratio_u,
    correction_term_dly,
    *sb_cropped,
) = crop_edges(t, crop_arrays, n_crop)

if ENABLE_SIDEBAND:
    sb_phase, sb_freq = sb_cropped

print(f"Post-shift length: {len(t)} samples")

# ── 6. DETREND ────────────────────────────────────────────────────────────
#ch4_phase_d = detrend(ch4_phase)
ch1_phase_d      = detrend(ch1_phase)
dcarrier_phase_d = detrend(ch3_phase)  # raw (unshifted) delayed-carrier phase
if ENABLE_SIDEBAND:
    sb_phase_d   = detrend(sb_phase)

# ── 7. TDI COMBINATION ────────────────────────────────────────────────────
# ch1_phase - apply_delay(ch3_phase - (ch3_freq/pt_freq)*pt_phase) - (ch1_freq/pt_freq)*pt_phase
tdi = (
    ch1_phase
    - correction_term_dly
    - freq_ratio_u * pt_phase
)

# ── 7b. ALTERNATIVE COMBINATION -- delayed SB vs delayed carrier, both raw
# (unshifted), since they're recorded simultaneously by the same delayer unit
# and so carry no relative delay between them. Jitter correction uses the
# frequency *difference* between the two delayed-side channels, still
# referenced to the delayer's own pilot tone (Input 2). ─────────────────────
if ENABLE_SIDEBAND:
    tj_d = detrend(t_jitter)
    tdi_alt = (
        sb_phase_d
        - dcarrier_phase_d
        - (sb_freq - ch3_freq) * (tj_d)
    )
    # raw sideband-minus-carrier, with no jitter correction applied -- shows
    # how much of tdi_alt's noise reduction actually comes from that term
    sb_minus_carrier = detrend(sb_phase - ch3_phase)
    print(np.mean(sb_freq - ch1_freq))

if (False):
    # ── 8. PLOT ───────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(3, 1, figsize=(10, 12), sharex=True)


    ax[0].plot(t, ch3_freq_dly, lw=0.5, label='ch3 freq * jitter')
    ax[0].plot(t, ch1_freq, lw=0.5, label='ch1 freq * jitter')
    ax[0].plot(t, ch1_phase_d, lw=0.5, label='ch1 phase')
    ax[0].set_ylabel('Comparison of clock jitter cancelling')
    ax[0].legend(loc='upper right')

    ax[1].plot(t, detrend(tdi), lw=0.5, label='TDI combo')
    ax[1].plot(t, ch1_phase_d, lw=0.5, label='ch1 phase')
    ax[1].plot(t, dcarrier_phase_d, lw=0.5, label='ch3 phase')
    ax[1].set_ylabel('TDI vs ch3 phase to be subtracted')
    ax[1].set_xlabel('Time (s)')
    ax[1].legend(loc='upper right')

    ax[2].plot(t, ch1_freq, lw=0.5, label='ch1 freq')
    ax[2].plot(t, ch3_freq_dly, lw=0.5, label='ch3 freq (delayed)', alpha=0.8)
    ax[2].set_ylabel('Frequency (Hz)')
    ax[2].set_xlabel('Time (s)')
    ax[2].legend(loc='upper right')


    plt.tight_layout()
    plt.savefig(f'plots/{filename}_debug_tdi.png', dpi=300)
    plt.show()



# ── 9. ASD COMPUTATION ────────────────────────────────────────────────────
def compute_asd(x, fs, fmin=min_f, nperseg=None):
    if fmin is not None:
        nperseg = int(fs / fmin)

    if nperseg is None:
        nperseg = min(len(x)//4, 2**14)

    # safety clamp
    nperseg = min(nperseg, len(x))
    print(f"Using nperseg = {nperseg} for ASD computation, length of data = {len(x)}")

    f, psd = welch(x, fs=fs, nperseg=nperseg, detrend='constant')
    asd = np.sqrt(psd)
    return f, asd

# Use detrended signals
#f0, asd_ch4 = compute_asd(ch4_phase_d, fs)
f1, asd_ch1 = compute_asd(ch1_phase_d, fs)
f2, asd_ch3 = compute_asd(detrend(ch3_phase), fs) # detrending gets rid of a lot of low-f noise
f3, asd_tdi = compute_asd(detrend(tdi), fs)
if ENABLE_SIDEBAND:
    f4, asd_tdi_alt = compute_asd(detrend(tdi_alt), fs)
    f5, asd_sb = compute_asd(detrend(sb_phase), fs)
    f6, asd_sb_minus_carrier = compute_asd(sb_minus_carrier, fs)


# ── 9b. RECOVER CLOCK NOISE ASD ───────────────────────────────────────────
# tdi = clock(t) - clock(t - delay)  =>  |H(f)| = |1 - exp(-i2*pi*f*delay)| = 2|sin(pi*f*delay)|
transfer_fn = 2 * np.abs(np.sin(np.pi * f3 * delay_s))

# near its *interior* nulls (f = n/delay, n=1,2,3,...) this blows up to spikes
# that are a division artifact, not real signal, so mask those points out
# (purely cosmetic -- gaps instead of spikes). The n=0 null sits at f=0 itself,
# where the transfer function just rises smoothly from zero rather than dipping
# and recovering -- a global "< 0.15*max" threshold catches that whole low-f
# rise too and wipes out the low-frequency band, so restrict the mask to bins
# nearest an n>=1 null only, leaving the low-frequency data untouched
"""
with np.errstate(divide="ignore", invalid="ignore"):
    asd_clock = asd_tdi / transfer_fn
nearest_null_order = np.round(f3 * delay_s)
near_interior_null = (nearest_null_order >= 1) & (transfer_fn < 0.15 * transfer_fn.max())
asd_clock[near_interior_null] = np.nan

clock_asd_path = os.path.join(os.path.dirname(__file__), '..', 'clock_noise', 'measured_clock_asd.csv')
np.savetxt(
    clock_asd_path,
    np.column_stack((f3, asd_clock)),
    header='Frequency (Hz),ASD (cyc/sqrt(Hz))',
    delimiter=',',
    comments=''
)
"""
plt.rcParams.update({
    "font.family"        : "sans-serif",
    "font.sans-serif"    : ["Helvetica", "Arial", "DejaVu Sans"],
    "mathtext.fontset"   : "custom",
    "mathtext.rm"        : "Helvetica",
    "mathtext.it"        : "Helvetica:italic",
    "mathtext.bf"        : "Helvetica:bold",
    "axes.spines.top"    : True,
    "axes.spines.right"  : True,
    "axes.linewidth"     : 0.8,
    "xtick.direction"    : "in",
    "ytick.direction"    : "in",
    "xtick.major.size"   : 4,
    "ytick.major.size"   : 4,
    "xtick.minor.size"   : 2.5,
    "ytick.minor.size"   : 2.5,
    "xtick.major.width"  : 0.8,
    "ytick.major.width"  : 0.8,
    "xtick.labelsize"    : 15,
    "ytick.labelsize"    : 15,
    "axes.labelsize"     : 13,
    "legend.fontsize"    : 14,
    "legend.framealpha"  : 0.92,
    "legend.edgecolor"   : "#cccccc",
    "legend.handlelength": 2.0,
    "figure.dpi"         : 600,
})
# colors borrowed as-is from clock_noise/USO_phse_noise.py's validated palette
color_extrapolated = "#d71b2f"  # red    -- main TDI-derived residual
color_modulator     = "#821770"  # purple -- alt (sideband) residual
color_delayline     = "#295f24"  # blue   -- raw sideband signal
ink_secondary       = "#52514e"  # neutral gray -- pure/reference signal
color_sideband      = "#eb6834"  # orange -- raw sb-minus-carrier, no jitter corr.
color_ptdiff        = "#2d13b4"  # navy   -- PT diff referred to 10 MHz

plt.figure(figsize=(7, 5))


baseline_ref = np.loadtxt(os.path.join('..', 'measured noises', 'baseline.csv'), delimiter=',', skiprows=1)
plt.loglog(baseline_ref[:, 0], baseline_ref[:, 1], lw=1.5, label='Typical baseline', color='k', alpha=0.3)
plt.loglog(f3, asd_tdi, lw=1.5, label='Residual', color=color_modulator)
if ENABLE_SIDEBAND:
    plt.loglog(f4, asd_tdi_alt, lw=1.5, label='Residual with sideband', color=color_delayline, alpha=0.8)
plt.loglog(f1, asd_ch1, lw=1.2, label='Carrier ASD', color=color_extrapolated)
if ENABLE_SIDEBAND:
    plt.loglog(f5, asd_sb, lw=1.2, label='Sideband ASD', color=ink_secondary, alpha=0.8)
    #plt.loglog(f6, asd_sb_minus_carrier, lw=1.2, label='SB - Carrier (no jitter corr.)', color=color_sideband, alpha=0.8)
#plt.loglog(f3, asd_clock, lw=1.5, label='Clock Noise (recovered)', color='k')

#plt.loglog(f0, asd_ch4, lw=1, label='ch4 phase')
plt.xlabel('Frequency [Hz]')
plt.ylabel('ASD [cyc / √Hz]')
#lt.title('Amplitude Spectral Density, delay = {:.8f} s\nDuration used: {:.1f} h\ncut: {} s from start, {} s from end'.format(delay_s, (duration - end_time - start_time)/3600, start_time, end_time))

plt.grid(True, which='both', ls='--', alpha=0.5)
plt.legend()
plt.xlim(min_f, fs/2)

plt.tight_layout()
plt.savefig(f'plots/{filename}_TDI1_asd.png', dpi=300)

# ── 10. ASD PLOT ──────────────────────────────────────────────────────────
plt.figure(figsize=(8, 5))


# PT diff (referred to 10 MHz), from timingjitters_analysis.py -- run that
# script first to (re)generate this file for the latest timingjitters log
pt_diff_path = os.path.join('..', 'measured noises', 'pt_diff_15MHz_asd.csv')
if os.path.exists(pt_diff_path):
    pt_diff_ref = np.loadtxt(pt_diff_path, delimiter=',', skiprows=1)
    plt.loglog(pt_diff_ref[:, 0], pt_diff_ref[:, 1], lw=1.2, label='PT vs SYSREF (15 MHz)',
               color=color_ptdiff, ls='--', alpha=0.8)

plt.loglog(f3, asd_tdi, lw=1.5, label='Residual', color=color_extrapolated)
if ENABLE_SIDEBAND:
    plt.loglog(f4, asd_tdi_alt, lw=1.5, label='Residual with sideband', color=color_delayline, alpha=0.8)
plt.loglog(f1, asd_ch1, lw=1.2, label='Carrier ASD', color=color_modulator, alpha=0.8)
if ENABLE_SIDEBAND:
    plt.loglog(f5, asd_sb, lw=1.2, label='Sideband ASD', color=ink_secondary, alpha=0.8)
    #plt.loglog(f6, asd_sb_minus_carrier, lw=1.2, label='SB - Carrier (no jitter corr.)', color=color_sideband, alpha=0.8)
#plt.loglog(f3, asd_clock, lw=1.5, label='Clock Noise (recovered)', color='k')

#plt.loglog(f0, asd_ch4, lw=1, label='ch4 phase')
plt.xlabel('Frequency (Hz)')
plt.ylabel('ASD (cyc / √Hz)')
#plt.title('Amplitude Spectral Density, delay = {:.8f} s\nDuration used: {:.1f} h\ncut: {} s from start, {} s from end'.format(delay_s, (duration - end_time - start_time)/3600, start_time, end_time))

plt.grid(True, which='both', ls='--', alpha=0.5)
plt.legend()
plt.xlim(min_f, fs/2)

plt.tight_layout()
plt.savefig(f'plots/{filename}_TDI1_asd_wPT.png', dpi=300)

# ── 11. TDI TIME SERIES PLOT ──────────────────────────────────────────────
if (False):
    plt.figure(figsize=(10, 5))

    plt.plot(t, detrend(tdi), lw=0.5, color=color_extrapolated)

    plt.xlabel('Time (s)')
    plt.ylabel('TDI combo (cyc)')
    plt.title(f'TDI Combo Time Series, delay = {delay_s:.8f} s')

    plt.grid(True, ls='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(f'plots/{filename}_TDI1_timeseries.png', dpi=300)






"""
# ── 12. RESIDUAL / BASELINE RATIO ─────────────────────────────────────────
# how far the measured residual sits above (>1) or below (<1) the "typical
# baseline" reference curve, frequency-by-frequency. baseline_ref has its own
# frequency grid (and an f=0 row that log-interpolation can't use), so
# interpolate it in log-log space onto f3/f4 before dividing.
mask = f3 > 0
log_baseline_f = np.log10(baseline_ref[1:, 0])
log_baseline_asd = np.log10(baseline_ref[1:, 1])
baseline_on_f3 = 10 ** np.interp(np.log10(f3[mask]), log_baseline_f, log_baseline_asd)
ratio_tdi = asd_tdi[mask] / baseline_on_f3

plt.figure(figsize=(8, 5))
plt.loglog(f3[mask], ratio_tdi, lw=1.5, label='Residual / baseline', color=color_extrapolated)
if ENABLE_SIDEBAND:
    baseline_on_f4 = 10 ** np.interp(np.log10(f4[mask]), log_baseline_f, log_baseline_asd)
    ratio_tdi_alt = asd_tdi_alt[mask] / baseline_on_f4
    plt.loglog(f4[mask], ratio_tdi_alt, lw=1.5, label='Residual (sideband) / baseline', color=color_delayline, alpha=0.8)
plt.axhline(1.0, color='k', ls=':', lw=1, label='Residual = baseline')

plt.xlabel('Frequency (Hz)')
plt.ylabel('Residual ASD / Baseline ASD')
plt.title('Residual-to-baseline ratio')
plt.grid(True, which='both', ls='--', alpha=0.5)
plt.legend()
plt.xlim(min_f, fs/2)

plt.tight_layout()
plt.savefig(f'plots/{filename}_residual_baseline_ratio.png', dpi=300)


# ── 14. PT FREQUENCY NOISE PLOT ───────────────────────────────────────────
# frequency noise of the pilot tone (Input {PT_INPUT}) -- pt_freq is a direct
# frequency measurement from the Moku, not derived from phase, so no
# conversion is needed here.
pt_freq_d = detrend(pt_freq)
f_pt, asd_pt_freq = compute_asd(pt_freq_d, fs)

plt.figure(figsize=(8, 5))
plt.loglog(f_pt, asd_pt_freq, lw=1.5, color=color_modulator)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Frequency ASD (Hz / √Hz)')
plt.title(f'PT Frequency Noise (Input {PT_INPUT})')
plt.grid(True, which='both', ls='--', alpha=0.5)
plt.xlim(min_f, fs/2)

plt.tight_layout()
plt.savefig(f'plots/{filename}_PT_freq_noise.png', dpi=300)

"""