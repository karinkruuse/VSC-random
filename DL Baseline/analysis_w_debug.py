import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend
from pytdi.dsp import timeshift
from scipy.signal import welch

# ── CONFIG ────────────────────────────────────────────────────────────────
filename = 'DownstairsTest_20260423_170536'
delay_s  = 3.9990392852
DDS_signal_nr = 2
# ── 1. LOAD ───────────────────────────────────────────────────────────────
data = np.load(f'data/{filename}.npy')

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

print(f"Measuring timing jitters from channel {DDS_signal_nr}")
t_jitter = channels[DDS_signal_nr]['phase'] / channels[DDS_signal_nr]['freq']

f0 = channels[4]['freq'].mean()
print(f"Reference frequency (ch4 mean): {f0:.6f} Hz")

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

n_crop = int(np.ceil(abs(delay_samples))) + 5  # +2 for safety

t, (
    ch1_phase,
    ch1_freq,          # <-- add this
    ch3_phase,
    ch3_phase_dly,
    ch3_freq_dly,
    tj,
    tj_dly
) = crop_edges(
    t,
    [
        channels[1]['phase'],
        channels[1]['freq'],   # <-- add this
        channels[3]['phase'],
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
    - ch3_freq_dly * (tj_d - tj_dly_d) # it looks like Dch3_freq and ch1_freq are equivalent here (theory also says so)
)

if (False):
    # ── 8. PLOT ───────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(3, 1, figsize=(10, 12), sharex=True)


    ax[0].plot(t, ch3_freq_dly * (tj_d - tj_dly_d), lw=0.5, label='ch3 freq * jitter')
    ax[0].plot(t, ch1_freq * (tj_d - tj_dly_d), lw=0.5, label='ch1 freq * jitter')
    ax[0].plot(t, ch1_phase_d, lw=0.5, label='ch1 phase')
    ax[0].set_ylabel('Comparison of clock jitter cancelling')
    ax[0].legend(loc='upper right')

    ax[1].plot(t, detrend(tdi), lw=0.5, label='TDI combo')
    ax[1].plot(t, ch3_phase_d, lw=0.5, label='ch3 phase')
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
def compute_asd(x, fs, fmin=9e-4, nperseg=None):
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
f1, asd_ch1 = compute_asd(ch1_phase_d, fs)
f2, asd_ch3 = compute_asd(detrend(ch3_phase), fs) # detrending gets rid of a lot of low-f noise
f3, asd_tdi = compute_asd(detrend(tdi), fs)

# ── 10. ASD PLOT ──────────────────────────────────────────────────────────
plt.figure(figsize=(8, 5))

plt.loglog(f1, asd_ch1, lw=1, label='ch1 phase')
plt.loglog(f3, asd_tdi, lw=1.5, label='TDI combo')
plt.loglog(f2, asd_ch3, lw=1, label='ch3 phase')

plt.xlabel('Frequency (Hz)')
plt.ylabel('ASD (cyc / √Hz)')
plt.title('Amplitude Spectral Density, delay = {:.8f} s\nDuration used: {:.1f} h\ncut: {} s from start, {} s from end'.format(delay_s, (duration - end_time - start_time)/3600, start_time, end_time))

plt.grid(True, which='both', ls='--', alpha=0.5)
plt.legend()

plt.tight_layout()
plt.savefig(f'plots/{filename}_TDI1_asd.png', dpi=300)
