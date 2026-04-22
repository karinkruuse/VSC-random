import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend, welch
from scipy.optimize import minimize_scalar
from pytdi.dsp import timeshift

# ── CONFIG ────────────────────────────────────────────────────────────────
filename = 'Delay_line_clock_ref_in_input_4_pilot_in_input_2_20260421_132555'
delay_s_init = 3.9989

fmin = 1e-3
fmax = 1.0

search_width = 1e-2

# ── 1. LOAD ───────────────────────────────────────────────────────────────
data = np.load(f'data/second/{filename}.npy')

def col(name):
    return data[name].copy()

t  = col('Time (s)')
fs = 1.0 / np.median(np.diff(t))

start_time = 20 * 60 * 60
end_time   = 0.5 * 60 * 60

print(f"Samples: {len(t)} | fs ≈ {fs:.4f} Hz | duration ≈ {t[-1]-t[0]:.1f} s")

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
    t_new = t[sl]

    out = {}
    for ch in data_dict:
        out[ch] = {k: v[sl] for k, v in data_dict[ch].items()}

    return t_new, out

t, channels = crop_time(t, channels, start_time, end_time)

# ── 3. DERIVED SIGNAL ─────────────────────────────────────────────────────
t_jitter = channels[2]['phase'] / channels[2]['freq']

# ── 4. GLOBAL FIXES (CRITICAL) ────────────────────────────────────────────

# ---- FIXED PSD SETTINGS (no dependency on delay!)
nperseg_fixed = int(fs / fmin)

# ---- FIXED CROPPING (use worst-case delay)
max_delay = delay_s_init + search_width
max_delay_samples = max_delay * fs
n_crop_fixed = int(np.ceil(abs(max_delay_samples))) + 3

# ── 5. CORE PIPELINE ──────────────────────────────────────────────────────
def compute_tdi(delay_s):

    delay_samples = delay_s * fs

    # --- delay
    ch3_phase_dly = timeshift(channels[3]['phase'], -delay_samples)
    ch3_freq_dly  = timeshift(channels[3]['freq'],  -delay_samples)
    tj_dly        = timeshift(t_jitter,             -delay_samples)

    # --- FIXED cropping
    sl = slice(n_crop_fixed, -n_crop_fixed)

    ch1_phase = channels[1]['phase'][sl]
    ch1_freq  = channels[1]['freq'][sl]

    ch3_phase_dly = ch3_phase_dly[sl]
    ch3_freq_dly  = ch3_freq_dly[sl]

    tj     = t_jitter[sl]
    tj_dly = tj_dly[sl]

    # --- better detrending (important for low-f sanity)
    ch1_phase_d = detrend(ch1_phase, type='linear')
    ch3_phase_d = detrend(ch3_phase_dly, type='linear')
    tj_d        = detrend(tj, type='linear')
    tj_dly_d    = detrend(tj_dly, type='linear')

    # --- TDI
    tdi = (
        ch1_phase_d
        - ch3_phase_d
        - ch3_freq_dly * (tj_d - tj_dly_d)
    )

    return tdi

# ── 6. COST FUNCTION ──────────────────────────────────────────────────────
def tdi_cost(delay_s):

    tdi = compute_tdi(delay_s)

    f, psd = welch(
        tdi,
        fs=fs,
        nperseg=nperseg_fixed,
        detrend='constant'
    )

    mask = (f >= fmin)
    if fmax is not None:
        mask &= (f <= fmax)

    # ---- IMPORTANT: keep low frequencies, but stabilize slightly
    # very mild weighting (does NOT kill low-f, just avoids domination)
    weight = 1 + 0.0 * f[mask]

    cost = np.trapezoid(psd[mask] * weight, f[mask])

    return cost

# ── 7. OPTIMIZATION ───────────────────────────────────────────────────────
result = minimize_scalar(
    tdi_cost,
    bounds=(delay_s_init - search_width, delay_s_init + search_width),
    method='bounded',
    options={'xatol': 1e-9, 'maxiter': 400}
)

delay_opt = result.x

print(f"\nInitial delay:  {delay_s_init:.10f} s")
print(f"Optimal delay:  {delay_opt:.10f} s")

# ── 8. COST LANDSCAPE (TURN THIS ON IF CONFUSED) ───────────────────────────
if True:
    delays = np.linspace(delay_s_init - search_width, delay_s_init + search_width, 40)
    costs = [tdi_cost(d) for d in delays]

    plt.figure()
    plt.plot(delays, costs, '-o', ms=3)
    plt.axvline(delay_opt, color='r', label='optimum')
    plt.xlabel('Delay (s)')
    plt.ylabel('Integrated PSD')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'plots/{filename}_delay_scan.png', dpi=200)

# ── 9. FINAL ASD ──────────────────────────────────────────────────────────
def compute_asd(x):
    f, psd = welch(x, fs=fs, nperseg=nperseg_fixed, detrend='constant')
    return f, np.sqrt(psd)

tdi_opt  = compute_tdi(delay_opt)
tdi_init = compute_tdi(delay_s_init)

f, asd_opt  = compute_asd(tdi_opt)
_, asd_init = compute_asd(tdi_init)

plt.figure(figsize=(8,5))
plt.loglog(f, asd_init, label=f'init = {delay_s_init:.10f} s', alpha=0.7)
plt.loglog(f, asd_opt,  label=f'opt  = {delay_opt:.10f} s', lw=1.5)

plt.xlabel('Frequency (Hz)')
plt.ylabel('ASD (cyc / √Hz)')
plt.title('TDI delay optimization (stable)')
plt.grid(True, which='both', ls='--', alpha=0.5)
plt.legend()

plt.tight_layout()
plt.savefig(f'plots/{filename}_opt_const_delay.png', dpi=300)