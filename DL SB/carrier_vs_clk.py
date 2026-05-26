import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend, welch, decimate
from scipy.optimize import minimize_scalar
from pytdi.dsp import timeshift

# ── CONFIG ────────────────────────────────────────────────────────────────
FILE_CARRIER = 'data/Carrier_20260526_134721.npy'
FILE_CLK     = 'data/CLK_20260526_134723.npy'

DELAY_NOMINAL_S = 4.1
DELAY_SEARCH_S  = 0.1

FMIN_OBJ = 1e-3   # Hz — lower bound of PSD integration for minimisation
FMAX_OBJ = 1.0    # Hz — upper bound
FMIN_ASD = 9e-4   # Hz — for final ASD plot

# ── 1. LOAD ───────────────────────────────────────────────────────────────
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
clk     = load_npy(FILE_CLK)

fs     = 1.0 / np.median(np.diff(carrier['t']))
fs_clk = 1.0 / np.median(np.diff(clk['t']))
print(f"Carrier: {len(carrier['t'])} samples | fs={fs:.4f} Hz | "
      f"duration={carrier['t'][-1]-carrier['t'][0]:.1f} s")
print(f"CLK:     {len(clk['t'])} samples | fs={fs_clk:.4f} Hz | "
      f"duration={clk['t'][-1]-clk['t'][0]:.1f} s")

# ── 2. DECIMATE CLK ───────────────────────────────────────────────────────
decimate_factor  = int(round(fs_clk / fs))
print(f"Decimating CLK by {decimate_factor}x")

t_jitter_clk     = detrend(clk['phase_A']) / clk['freq_A']
t_jitter_clk_dec = decimate(t_jitter_clk, decimate_factor, ftype='iir', zero_phase=True)
clk_freq_A_dec   = clk['freq_A'][::decimate_factor]
t_clk_dec        = clk['t'][::decimate_factor]

n_dec            = min(len(t_clk_dec), len(t_jitter_clk_dec))
t_clk_dec        = t_clk_dec[:n_dec]
t_jitter_clk_dec = t_jitter_clk_dec[:n_dec]
clk_freq_A_dec   = clk_freq_A_dec[:n_dec]
print(f"Decimated CLK: {len(t_clk_dec)} samples | "
      f"fs={1.0/np.median(np.diff(t_clk_dec)):.4f} Hz | "
      f"duration={t_clk_dec[-1]-t_clk_dec[0]:.1f} s")

# ── 3. DELAY MINIMISATION ─────────────────────────────────────────────────
def integrated_psd(delay_s):
    delay_samp  = delay_s * fs
    n_crop      = int(np.ceil(abs(delay_samp))) + 5
    phase_dly   = timeshift(carrier['phase_B'], -delay_samp)

    pA  = carrier['phase_A'][n_crop:-n_crop]
    pB  = phase_dly[n_crop:-n_crop]
    tdi = detrend(pA - pB)

    nperseg = min(int(fs / FMIN_OBJ), len(tdi))
    f, psd  = welch(tdi, fs=fs, nperseg=nperseg, detrend='constant')
    band    = (f >= FMIN_OBJ) & (f <= FMAX_OBJ)
    return np.trapz(psd[band], f[band])

print(f"\nSearching delay in [{DELAY_NOMINAL_S-DELAY_SEARCH_S:.3f}, "
      f"{DELAY_NOMINAL_S+DELAY_SEARCH_S:.3f}] s ...")

result = minimize_scalar(
    integrated_psd,
    bounds=(DELAY_NOMINAL_S - DELAY_SEARCH_S,
            DELAY_NOMINAL_S + DELAY_SEARCH_S),
    method='bounded',
    options={'xatol': 1e-6}
)
delay_opt = result.x
print(f"Optimal delay: {delay_opt:.9f} s  (integrated PSD = {result.fun:.4e})")


# ── 4. FINAL TDI WITH OPTIMAL DELAY ──────────────────────────────────────
delay_samp  = delay_opt * fs
n_crop      = int(np.ceil(abs(delay_samp))) + 5
phase_dly   = timeshift(carrier['phase_B'], -delay_samp)

pA  = detrend(carrier['phase_A'][n_crop:-n_crop])
pB  = detrend(phase_dly[n_crop:-n_crop])
tdi = detrend(pA - pB)

# ── 5. TIMESERIES PLOT ───────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 4))
t_plot = np.arange(len(pA)) / fs / 3600   # hours
ax.plot(t_plot, pA, lw=0.5, label='phase_A (delayed arm)')
ax.plot(t_plot, pB, lw=0.5, label='phase_B (undelayed, time-shifted)', alpha=0.8)
ax.set_xlabel('Time (h)')
ax.set_ylabel('Phase (cyc)')
ax.set_title(f'Phase timeseries | delay = {delay_opt:.6f} s')
ax.legend()
ax.grid(True, ls='--', alpha=0.4)
plt.tight_layout()
plt.savefig('plots/carrier_timeseries.png', dpi=150)
print("Saved: plots/carrier_timeseries.png")

# ── 6. ASD ────────────────────────────────────────────────────────────────
def compute_asd(x, fmin=FMIN_ASD):
    nperseg = min(int(fs / fmin), len(x))
    print(f"  nperseg={nperseg}")
    f, psd = welch(x, fs=fs, nperseg=nperseg, detrend='constant')
    return f, np.sqrt(psd)

print("\nComputing ASDs...")
f_tdi, a_tdi = compute_asd(tdi)
f_A,   a_A   = compute_asd(detrend(pA))
f_B,   a_B   = compute_asd(detrend(pB))

# ── 6. ASD PLOT ───────────────────────────────────────────────────────────
plt.figure(figsize=(9, 5))
plt.loglog(f_tdi, a_tdi, lw=1.5, label='TDI residual')
plt.loglog(f_A,   a_A,   lw=2,   label='Delayed (A)',   alpha=0.8)
plt.loglog(f_B,   a_B,   lw=1,   label='Undelayed (B)', alpha=0.7)
plt.xlabel('Frequency (Hz)')
plt.ylabel('ASD (cyc / √Hz)')
plt.title(f'Carrier TDI | optimal delay = {delay_opt:.9f} s')
plt.grid(True, which='both', ls='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig('plots/carrier_tdi_asd.png', dpi=150)
print("Saved: plots/carrier_tdi_asd.png")
plt.show()