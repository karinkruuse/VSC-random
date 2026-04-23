import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend, welch
from pytdi.dsp import timeshift

# ── CONFIG ────────────────────────────────────────────────────────────────
filename = 'Delay_line_clock_ref_in_input_4_pilot_in_input_2_20260421_132555'
print(f"Processing file: {filename}")

tau0   = 3.9988968047
print(f"Initial guess: tau0={tau0:.6f} s, taudot={9999999:.1e} s/s")

fmin = 5e-4
fmax = 0.1

# ── 1. LOAD ───────────────────────────────────────────────────────────────
data = np.load(f'data/second/{filename}.npy')

def col(name):
    return data[name].copy()

t  = col('Time (s)')
fs = 1.0 / np.median(np.diff(t))
duration = t[-1] - t[0]
print(f"Samples: {len(t)} | fs ≈ {fs:.4f} Hz | duration ≈ {duration:.1f} s or {duration/3600:.2f} hours")

def load_channel(ch):
    pfx = f'Input {ch} '
    return {
        'freq':  col(pfx + 'Frequency (Hz)'),
        'phase': col(pfx + 'Phase (cyc)'),
    }

channels = {ch: load_channel(ch) for ch in range(1, 5)}

# ── 2. INITIAL CROPPING ───────────────────────────────────────────────────
def crop_time(t, data_dict, t_start=0, t_end=0):
    i0 = np.searchsorted(t, t[0] + t_start)
    i1 = np.searchsorted(t, t[-1] - t_end)
    if i0 >= i1:
        raise ValueError("Cropping removed entire dataset")
    sl = slice(i0, i1)
    return t[sl], {ch: {k: v[sl] for k, v in data_dict[ch].items()} for ch in data_dict}

start_time = 7.4 * 60 * 60
end_time = 7 * 60 * 60
print(f"Cropping data: start_time={start_time:.1f} s, end_time={ t[-1] - end_time:.1f} s")
t, channels = crop_time(t, channels, start_time, end_time)

data_check = False
if data_check:
    plt.plot(t, channels[1]['phase'], label='Ch1 phase')
    plt.plot(t, channels[3]['phase'], label='Ch3 phase')    
    plt.legend()
    plt.show()

# ── 3. DERIVED SIGNAL ─────────────────────────────────────────────────────
PT_channel = 2
print("Computing jitter from channel {}".format(PT_channel))
t_jitter = channels[PT_channel]['phase'] / channels[PT_channel]['freq']

# ── 4. HELPERS ────────────────────────────────────────────────────────────
def crop_edges(t, arrays, n_crop):
    if 2 * n_crop >= len(t):
        raise ValueError("Crop too large")
    sl = slice(n_crop, -n_crop)
    return t[sl], [a[sl] for a in arrays]

def compute_asd(x, fs, fmin):
    nperseg = min(int(fs / fmin), len(x))
    f, psd = welch(x, fs=fs, nperseg=nperseg, detrend='constant')
    return f, np.sqrt(psd)



# ── 5. COMPUTE TDI1 ────────────────────────────────────────────────────────
tau_t1       = tau0
tau_samples1 = tau_t1 * fs                   # samples

ch3_phase_dly1 = timeshift(channels[3]['phase'], -tau_samples1)
ch3_freq_dly1  = timeshift(channels[3]['freq'],  -tau_samples1)
tj_dly1        = timeshift(t_jitter,             -tau_samples1)

tau_max1 = np.max(np.abs(tau_t1))
n_crop1  = int(np.ceil(tau_max1 * fs)) + 2

t_loc1, (ch1_phase, ch1_freq, ch3_phase_dly1, ch3_freq_dly1, tj, tj_dly1) = crop_edges(
    t,
    [channels[1]['phase'], channels[1]['freq'],
     ch3_phase_dly1, ch3_freq_dly1,
     t_jitter, tj_dly1],
    n_crop1
)

tdi1 = (
    detrend(ch1_phase)
    - detrend(ch3_phase_dly1)
    - ch3_freq_dly1 * (detrend(tj) - detrend(tj_dly1))
)

# ── 5. COMPUTE TDI2 ────────────────────────────────────────────────────────

f0 = 10000001.91833843 # np.mean(channels[4]['freq'])
board_clk_fluctuations = f0 -channels[4]['freq']
tau_correction = np.cumsum(board_clk_fluctuations * tau0 / f0)
if False:
    plt.plot(t, board_clk_fluctuations)
    plt.plot(t, tau_correction)
    plt.show()
fit = 4.143e-03
tau_t       = tau0 + fit * tau_correction
tau_samples = tau_t * fs                   # samples, NOT INTEGER

ch3_phase_dly = timeshift(channels[3]['phase'], -tau_samples)
ch3_freq_dly  = timeshift(channels[3]['freq'],  -tau_samples)
tj_dly        = timeshift(t_jitter,             -tau_samples)

tau_max = np.max(np.abs(tau_t))
n_crop  = int(np.ceil(tau_max * fs)) + 2

t_loc, (ch1_phase, ch1_freq, ch3_phase_dly, ch3_freq_dly, tj, tj_dly) = crop_edges(
    t,
    [channels[1]['phase'], channels[1]['freq'],
     ch3_phase_dly, ch3_freq_dly,
     t_jitter, tj_dly],
    n_crop
)

tdi = (
    detrend(ch1_phase)
    - detrend(ch3_phase_dly)
    - ch3_freq_dly * (detrend(tj) - detrend(tj_dly))
)


# ── 6. ASD ────────────────────────────────────────────────────────────────
f,     asd     = compute_asd(detrend(tdi),        fs, fmin)
f1,     asd1     = compute_asd(detrend(tdi1),        fs, fmin)
f_ch1, asd_ch1 = compute_asd(detrend(ch1_phase),  fs, fmin)
f_ch3, asd_ch3 = compute_asd(detrend(ch3_phase_dly), fs, fmin)

print(f"\ntau0   = {tau0:.10f} s")
#print(f"taudot = {taudot:.3e} s/s")

plt.figure(figsize=(8, 5))
#plt.loglog(f_ch1, asd_ch1, lw=1.0, alpha=0.7, label='Ch1 phase')
plt.loglog(f_ch3, asd_ch3, lw=1.0, alpha=0.7, label='Ch3 phase (delayed)')
plt.loglog(f,     asd,     lw=1.5, c='green', label=f'TDI  τ₀={tau0:.6f} s, τ̇=crazy s/s')
plt.loglog(f1,     asd1,     lw=1.0, c='red', label=f'TDI1 τ={tau0:.6f} s', alpha=0.4)
plt.xlabel('Frequency (Hz)')
plt.ylabel('ASD (cyc / √Hz)')
plt.title(f'TDI ASD\noverall duration: {duration:.1f} s\nseconds cut from start/end: {start_time:.1f}s, {end_time:.1f}s')
plt.grid(True, which='both', ls='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(f'plots/{filename}_tdi_asd.png', dpi=300)
print(f"Plot saved to plots/{filename}_tdi_asd.png")