import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend, welch
from scipy.optimize import minimize_scalar
from pytdi.dsp import timeshift


# ── CONFIG ────────────────────────────────────────────────────────────────
FILE_CARRIER     = 'data/Carrier_20260526_160851.npy'

DELAY_NOMINAL_S  = 4.1    # programmed delay between carrier A and B (s)
DELAY_SEARCH_S   = 0.1    # coarse sweep: ± this around nominal

FMIN_OBJ         = 1e-3   # Hz — lower edge of band used for PSD minimisation
FMAX_OBJ         = 1.0    # Hz — upper edge

FMIN_ASD         = 9e-4   # Hz — lowest frequency shown on ASD plot


# ── 1. LOAD ───────────────────────────────────────────────────────────────
data = np.load(FILE_CARRIER)

t        = data['Time (s)'].copy()
phase_A  = data['Input A Phase (cyc)'].copy()
freq_A   = data['Input A Frequency (Hz)'].copy()
phase_B  = data['Input B Phase (cyc)'].copy()
freq_B   = data['Input B Frequency (Hz)'].copy()

fs = 1.0 / np.median(np.diff(t))
print(f"Loaded: {len(t)} samples | fs = {fs:.4f} Hz | "
      f"duration = {(t[-1]-t[0])/3600:.3f} h")


# ── 2. COARSE DELAY SWEEP ─────────────────────────────────────────────────
# For each candidate delay we:
#   - shift phase_B forward by delay_samples
#   - crop the edges that timeshift leaves invalid
#   - detrend both signals
#   - compute integrated Welch PSD of the residual (A - B_delayed)
# The delay that minimises this is our starting point for the fine search.

print(f"\nCoarse sweep: {DELAY_NOMINAL_S} ± {DELAY_SEARCH_S} s")

delays      = np.linspace(DELAY_NOMINAL_S - DELAY_SEARCH_S,
                           DELAY_NOMINAL_S + DELAY_SEARCH_S, 60)
psd_values  = np.full(len(delays), np.inf)

for k, delay_s in enumerate(delays):
    delay_samples = delay_s * fs
    n_crop        = int(np.ceil(abs(delay_samples))) + 5

    phase_B_dly = timeshift(phase_B, -delay_samples)

    sl = slice(n_crop, -n_crop)
    residual = detrend(phase_A[sl]) - detrend(phase_B_dly[sl])

    nperseg      = min(int(fs / FMIN_OBJ), len(residual))
    f, psd       = welch(residual, fs=fs, nperseg=nperseg, detrend='constant')
    band         = (f >= FMIN_OBJ) & (f <= FMAX_OBJ)
    psd_values[k] = np.trapezoid(psd[band], f[band])

best_k   = np.argmin(psd_values)
delay0   = delays[best_k]
print(f"Coarse minimum: delay = {delay0:.6f} s  "
      f"(integrated PSD = {psd_values[best_k]:.4e})")


# ── 3. FINE DELAY OPTIMISATION ────────────────────────────────────────────
# Brent's method in a tight window around the coarse minimum.

print(f"\nFine optimisation (Brent) around {delay0:.6f} s ...")

def residual_psd(delay_s):
    delay_samples = delay_s * fs
    n_crop        = int(np.ceil(abs(delay_samples))) + 5
    phase_B_dly   = timeshift(phase_B, -delay_samples)
    sl            = slice(n_crop, -n_crop)
    residual      = detrend(phase_A[sl]) - detrend(phase_B_dly[sl])
    nperseg       = min(int(fs / FMIN_OBJ), len(residual))
    f, psd        = welch(residual, fs=fs, nperseg=nperseg, detrend='constant')
    band          = (f >= FMIN_OBJ) & (f <= FMAX_OBJ)
    return float(np.trapezoid(psd[band], f[band]))

result   = minimize_scalar(residual_psd,
                            bounds=(delay0 - 0.05, delay0 + 0.05),
                            method='bounded',
                            options={'xatol': 1e-8, 'maxiter': 200})
delay_s  = float(result.x)
print(f"Fine result: delay = {delay_s:.9f} s")


# ── 4. APPLY OPTIMAL DELAY AND CROP ──────────────────────────────────────
delay_samples = delay_s * fs
n_crop        = int(np.ceil(abs(delay_samples))) + 5

phase_B_dly = timeshift(phase_B, -delay_samples)
freq_B_dly  = timeshift(freq_B,  -delay_samples)

sl = slice(n_crop, -n_crop)
t         = t[sl]
phase_A   = phase_A[sl]
phase_B_dly = phase_B_dly[sl]
freq_B_dly  = freq_B_dly[sl]

print(f"\nPost-crop: {len(t)} samples | {(t[-1]-t[0])/3600:.3f} h")


# ── 5. DETREND AND FORM RESIDUAL ──────────────────────────────────────────
phase_A_d   = detrend(phase_A)
phase_B_d   = detrend(phase_B_dly)

residual = phase_A_d - phase_B_d


# ── 6. ASD ────────────────────────────────────────────────────────────────
def compute_asd(x):
    nperseg = min(int(fs / FMIN_ASD), len(x))
    print(f"  nperseg = {nperseg}  (len = {len(x)})")
    f, psd = welch(x, fs=fs, nperseg=nperseg, detrend='constant')
    return f, np.sqrt(psd)

print("\nComputing ASDs...")
f_res, asd_res = compute_asd(detrend(residual))
f_A,   asd_A   = compute_asd(phase_A_d)
f_B,   asd_B   = compute_asd(phase_B_d)


# ── 7. PLOTS ──────────────────────────────────────────────────────────────
# — coarse sweep curve
fig, ax = plt.subplots(figsize=(8, 4))
ax.semilogy(delays, psd_values, 'o-', ms=3)
ax.axvline(delay_s, color='r', ls='--', label=f'opt = {delay_s:.6f} s')
ax.set_xlabel('Delay (s)')
ax.set_ylabel('Integrated PSD  [cyc²]')
ax.set_title('Coarse delay sweep — Carrier A vs B')
ax.legend()
ax.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig('plots/carrier_delay_sweep.png', dpi=150)
print("Saved: plots/carrier_delay_sweep.png")

# — time series
t_h = (t - t[0]) / 3600   # relative time in hours

fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

axes[0].plot(t_h, phase_A_d,   lw=0.6, color='steelblue',  label='Phase A (detrended)')
axes[0].set_ylabel('Phase (cyc)')
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)

axes[1].plot(t_h, phase_B_d,   lw=0.6, color='darkorange', label='Phase B delayed (detrended)')
axes[1].set_ylabel('Phase (cyc)')
axes[1].legend(loc='upper right')
axes[1].grid(True, alpha=0.3)

axes[2].plot(t_h, residual,    lw=0.6, color='firebrick',  label='A − B delayed')
axes[2].set_ylabel('Phase (cyc)')
axes[2].set_xlabel('Elapsed time (h)')
axes[2].legend(loc='upper right')
axes[2].grid(True, alpha=0.3)

fig.suptitle(f'Carrier A vs B delayed  |  delay = {delay_s:.9f} s', fontsize=11)
plt.tight_layout()
plt.savefig('plots/carrier_delay_timeseries.png', dpi=150)
print("Saved: plots/carrier_delay_timeseries.png")

# — ASD
fig, ax = plt.subplots(figsize=(9, 5))
ax.loglog(f_res, asd_res, lw=1.5, label='Residual  (A − B delayed)')
ax.loglog(f_A,   asd_A,   lw=1.0, label='Carrier A',  alpha=0.7)
ax.loglog(f_B,   asd_B,   lw=1.0, label='Carrier B (delayed)', alpha=0.7)
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('ASD  (cyc / √Hz)')
ax.set_title(f'Carrier A vs B  |  delay = {delay_s:.9f} s  |  '
             f'duration = {(t[-1]-t[0])/3600:.3f} h')
ax.grid(True, which='both', ls='--', alpha=0.5)
ax.legend()
plt.tight_layout()
plt.savefig('plots/carrier_delay_asd.png', dpi=150)
print("Saved: plots/carrier_delay_asd.png")

plt.show()