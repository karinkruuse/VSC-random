import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend, welch
from scipy.optimize import minimize
from pytdi.dsp import timeshift

# ── CONFIG ────────────────────────────────────────────────────────────────
filename = 'DownstairsTest_20260423_150448'
print(f"Processing file: {filename}")


tau0_init   = 3.9986
taudot_init = 0.0

fmin = 5e-4
fmax = 0.1

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

# ── 2. INITIAL CROPPING ───────────────────────────────────────────────────
def crop_time(t, data_dict, t_start=0, t_end=0):
    print(f"Cropping data: start_time={t[0] + t_start:.1f} s, end_time={ t[-1] - t_end:.1f} s")
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

t, channels = crop_time(t, channels, t_start=7.4 * 60 * 60, t_end=7 * 60 * 60)

# ── 3. DERIVED SIGNAL ─────────────────────────────────────────────────────
PT_channel = 2
print("Computing jitter from channel {}".format(PT_channel))
t_jitter = channels[PT_channel]['phase'] / channels[PT_channel]['freq']

# ── 4. HELPERS ────────────────────────────────────────────────────────────
def crop_edges(t, arrays, n_crop):
    if 2 * n_crop >= len(t):
        raise ValueError("Crop too large")

    sl = slice(n_crop, -n_crop)
    t_new = t[sl]
    arrays_new = [a[sl] for a in arrays]
    return t_new, arrays_new

def compute_asd(x, fs, fmin):
    nperseg = min(int(fs / fmin), len(x))
    f, psd = welch(x, fs=fs, nperseg=nperseg, detrend='constant')
    return f, np.sqrt(psd), psd

# ── 5. CORE PIPELINE (TIME-VARYING DELAY) ──────────────────────────────────
def compute_tdi(params):
    tau0, tau_dot = params

    f0 = 10000001.91833843 # np.mean(channels[4]['freq'])
    board_clk_fluctuations = channels[4]['freq'] - f0

    tau_t       = tau0 + tau_dot * np.cumsum(board_clk_fluctuations * tau0 / f0)
    tau_samples = tau_t * fs               # samples

    # --- TDI-consistent delay
    ch3_phase_dly = timeshift(channels[3]['phase'], -tau_samples)
    ch3_freq_dly  = timeshift(channels[3]['freq'],  -tau_samples)
    tj_dly        = timeshift(t_jitter,             -tau_samples)

    # --- crop based on worst delay
    tau_max = np.max(np.abs(tau_t))
    n_crop = int(np.ceil(tau_max * fs)) + 2

    t_loc, (
        ch1_phase,
        ch1_freq,
        ch3_phase_dly,
        ch3_freq_dly,
        tj,
        tj_dly
    ) = crop_edges(
        t,
        [
            channels[1]['phase'],
            channels[1]['freq'],
            ch3_phase_dly,
            ch3_freq_dly,
            t_jitter,
            tj_dly
        ],
        n_crop
    )

    # --- detrend
    ch1_phase_d = detrend(ch1_phase)
    ch3_phase_d = detrend(ch3_phase_dly)
    tj_d        = detrend(tj)
    tj_dly_d    = detrend(tj_dly)

    # --- TDI combination
    tdi = (
        ch1_phase_d
        - ch3_phase_d
        - ch3_freq_dly * (tj_d - tj_dly_d)
    )

    return tdi

# ── 6. COST FUNCTION ──────────────────────────────────────────────────────
def tdi_cost(params):
    tdi = compute_tdi(params)

    nperseg = min(int(fs / fmin), len(tdi))
    f, psd = welch(tdi, fs=fs, nperseg=nperseg, detrend='constant')

    mask = (f >= fmin) & (f <= fmax)
    return np.trapezoid(psd[mask], f[mask])

# ── 7. OPTIMIZATION ───────────────────────────────────────────────────────
x0 = [tau0_init, taudot_init]

result = minimize(
    tdi_cost, x0,
    method='Nelder-Mead',
    options={
        'initial_simplex': np.array([[tau0_init, 0.0],
                                     [tau0_init + 1e-4, 0.0],
                                     [tau0_init, 0.5]]),
        'xatol': 1e-9, 'fatol': 1e-12, 'maxiter': 500
    }
)

tau0_opt, tau_dot_opt = result.x

print(f"\nInitial tau0:   {tau0_init:.10f} s")
print(f"Optimal tau0:   {tau0_opt:.10f} s")
print(f"Optimal taudot: {tau_dot_opt:.3e} s/s")

if (False):
    # ── 8. COST LANDSCAPE (optional sanity check) ──────────────────────────────
    taus = np.linspace(tau0_init - 5e-4, tau0_init + 5e-4, 30)
    costs = [tdi_cost([tau, tau_dot_opt]) for tau in taus]

    plt.figure()
    plt.plot(taus, costs, '-o', ms=3)
    plt.axvline(tau0_opt, color='r')
    plt.xlabel('tau0 (s)')
    plt.ylabel('Cost')
    plt.tight_layout()
    plt.savefig(f'plots/{filename}_delay_scan_drift.png', dpi=200)

# ── 9. FINAL ASD ──────────────────────────────────────────────────────────
tdi_init = compute_tdi([tau0_init, taudot_init])
tdi_opt  = compute_tdi([tau0_opt, tau_dot_opt])

f, asd_init, _ = compute_asd(detrend(tdi_init), fs, fmin)
_, asd_opt, _  = compute_asd(detrend(tdi_opt),  fs, fmin)

plt.figure(figsize=(8,5))
plt.loglog(f, asd_init, label='Initial delay', alpha=0.7)
plt.loglog(f, asd_opt,  label='Optimized (τ0 + drift)', lw=1.5)

plt.xlabel('Frequency (Hz)')
plt.ylabel('ASD (cyc / √Hz)')
plt.title('TDI with Time-Varying Delay Optimization')
plt.grid(True, which='both', ls='--', alpha=0.5)
plt.legend()

plt.tight_layout()
plt.savefig(f'plots/{filename}_tdi_drift_optimized_asd.png', dpi=300)