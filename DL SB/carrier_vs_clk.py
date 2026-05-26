import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend, welch, decimate
from scipy.optimize import minimize
from pytdi.dsp import timeshift

# ── CONFIG ────────────────────────────────────────────────────────────────
FILE_CARRIER = 'data/Carrier_20260526_134721.npy'
FILE_CLK     = 'data/CLK_20260526_134723.npy'

# Search bounds
# Carrier started ~2 s BEFORE CLK, so to align carrier onto CLK's time axis
# we subtract ~2 s from carrier's timestamps: offset_s ≈ -2.0 s
OFFSET_NOMINAL_S = -2.0   # carrier started before CLK → negative offset
OFFSET_SEARCH_S  =  1.0   # ± around nominal
DELAY_NOMINAL_S  =  4.1   # programmed delay
DELAY_SEARCH_S   =  0.5   # ± around nominal

# Coarse grid resolution
OFFSET_GRID_N    = 30
DELAY_GRID_N     = 30

# Data segments
SYNC_SEGMENT_S   = 5 * 60   # 5 min for coarse search
# Set to None to use all available data for fine search
FINE_SEGMENT_S   = None

FMIN = 9e-4   # lowest ASD frequency

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

t_jitter_clk_dec = decimate(clk['phase_A'] / clk['freq_A'],
                             decimate_factor, zero_phase=True)
clk_freq_A_dec   = decimate(clk['freq_A'], decimate_factor, zero_phase=True)
t_clk_dec        = clk['t'][::decimate_factor]

n_dec            = min(len(t_clk_dec), len(t_jitter_clk_dec))
t_clk_dec        = t_clk_dec[:n_dec]
t_jitter_clk_dec = t_jitter_clk_dec[:n_dec]
clk_freq_A_dec   = clk_freq_A_dec[:n_dec]

# ── 3. INTEGRATED PSD OBJECTIVE ──────────────────────────────────────────
# Frequency band to integrate over — target the band where laser noise
# dominates and TDI suppression is expected. Adjust to your signal band.
FMIN_OBJ = 1e-3    # Hz  — lower bound of integration band
FMAX_OBJ = 1.0     # Hz  — upper bound of integration band

def tdi_integrated_psd(offset_s, delay_s, segment_s=None):
    """
    Compute the integrated PSD of the TDI residual over [FMIN_OBJ, FMAX_OBJ].
    Minimising this finds the (offset, delay) that best suppresses noise
    across the band of interest, ignoring slow drifts outside it.

    offset_s : time offset of carrier relative to CLK [s]
    delay_s  : arm delay [s]
    segment_s: if not None, only use first segment_s seconds of overlap
    """
    t_car      = carrier['t'] + offset_s
    delay_samp = delay_s * fs
    n_crop     = int(np.ceil(abs(delay_samp))) + 5

    # Build common grid
    t0 = max(t_clk_dec[0],  t_car[0])
    t1 = min(t_clk_dec[-1], t_car[-1])
    if segment_s is not None:
        t1 = min(t1, t0 + segment_s)

    grid = t_clk_dec[(t_clk_dec >= t0) & (t_clk_dec <= t1)]
    if len(grid) < 2 * n_crop + 10:
        return np.inf

    def og(t_src, arr): return np.interp(grid, t_src, arr)

    pA = og(t_car,     carrier['phase_A'])
    pB = og(t_car,     carrier['phase_B'])
    fB = og(t_car,     carrier['freq_B'])
    tj = og(t_clk_dec, t_jitter_clk_dec)

    pB_dly = timeshift(pB, -delay_samp)
    fB_dly = timeshift(fB, -delay_samp)
    tj_dly = timeshift(tj, -delay_samp)

    sl = slice(n_crop, -n_crop)
    pA, pB_dly, fB_dly, tj, tj_dly = (
        x[sl] for x in [pA, pB_dly, fB_dly, tj, tj_dly])

    delta_tj = detrend(tj) - detrend(tj_dly)
    tdi      = detrend(pA) - detrend(pB_dly) - fB_dly * delta_tj

    # Welch PSD — nperseg chosen to resolve FMIN_OBJ
    nperseg = min(int(fs / FMIN_OBJ), len(tdi))
    f, psd  = welch(tdi, fs=fs, nperseg=nperseg, detrend='constant')

    # Integrate PSD over the target band (trapezoidal)
    band    = (f >= FMIN_OBJ) & (f <= FMAX_OBJ)
    if band.sum() < 2:
        return np.inf
    return np.trapz(psd[band], f[band])

# ── 4. COARSE 2D GRID SEARCH (5 min) ─────────────────────────────────────
print(f"\n── Coarse grid search on first {SYNC_SEGMENT_S/60:.0f} min ──")
offsets = np.linspace(OFFSET_NOMINAL_S - OFFSET_SEARCH_S,
                       OFFSET_NOMINAL_S + OFFSET_SEARCH_S, OFFSET_GRID_N)
delays  = np.linspace(DELAY_NOMINAL_S  - DELAY_SEARCH_S,
                       DELAY_NOMINAL_S  + DELAY_SEARCH_S,  DELAY_GRID_N)

rms_grid = np.zeros((len(delays), len(offsets)))
for i, d in enumerate(delays):
    for j, o in enumerate(offsets):
        rms_grid[i, j] = tdi_integrated_psd(o, d, segment_s=SYNC_SEGMENT_S)
    print(f"  delay row {i+1}/{len(delays)}: min integrated PSD so far = {rms_grid[:i+1].min():.4e}")

ij_min  = np.unravel_index(np.argmin(rms_grid), rms_grid.shape)
off0    = offsets[ij_min[1]]
dly0    = delays[ij_min[0]]
print(f"\nCoarse minimum: offset={off0:.4f} s, delay={dly0:.4f} s, "
      f"integrated PSD={rms_grid[ij_min]:.4e}")

# Plot coarse grid
fig_grid, ax_grid = plt.subplots(figsize=(8, 6))
im = ax_grid.pcolormesh(offsets, delays, np.log10(rms_grid), shading='auto', cmap='viridis_r')
ax_grid.plot(off0, dly0, 'r*', ms=12, label=f'min: off={off0:.4f}s, dly={dly0:.4f}s')
plt.colorbar(im, ax=ax_grid, label='log₁₀(TDI RMS)')
ax_grid.set_xlabel('Offset (s)')
ax_grid.set_ylabel('Delay (s)')
ax_grid.set_title(f'Coarse search — first {SYNC_SEGMENT_S/60:.0f} min')
ax_grid.legend()
plt.tight_layout()
plt.savefig('plots/coarse_grid.png', dpi=150)
print("Saved: plots/coarse_grid.png")

# ── 5. FINE 2D MINIMISATION (all data) ───────────────────────────────────
seg_label = f"all data" if FINE_SEGMENT_S is None else f"{FINE_SEGMENT_S/60:.0f} min"
print(f"\n── Fine minimisation on {seg_label} ──")
print(f"  Starting from coarse: offset={off0:.4f} s, delay={dly0:.4f} s")

def objective(params):
    return tdi_integrated_psd(params[0], params[1], segment_s=FINE_SEGMENT_S)

result = minimize(
    objective,
    x0=[off0, dly0],
    method='L-BFGS-B',
    bounds=[
        (OFFSET_NOMINAL_S - OFFSET_SEARCH_S, OFFSET_NOMINAL_S + OFFSET_SEARCH_S),
        (DELAY_NOMINAL_S  - DELAY_SEARCH_S,  DELAY_NOMINAL_S  + DELAY_SEARCH_S),
    ],
    options={
        'ftol':    1e-15,
        'gtol':    1e-10,
        'eps':     1e-5,   # finite-difference step ~0.01 ms
        'maxiter': 200,
        'disp':    True,
    }
)

offset_s, delay_s_opt = result.x
print(f"\nFine result:")
print(f"  offset = {offset_s:.6f} s")
print(f"  delay  = {delay_s_opt:.9f} s")
print(f"  RMS    = {result.fun:.4e}")

# ── 6. BUILD FULL DATASET WITH OPTIMAL PARAMETERS ────────────────────────
t_car = carrier['t'] + offset_s
t_start = max(t_clk_dec[0],  t_car[0])
t_end   = min(t_clk_dec[-1], t_car[-1])
t = t_clk_dec[(t_clk_dec >= t_start) & (t_clk_dec <= t_end)]
print(f"\nCommon grid: {len(t)} samples | {(t[-1]-t[0])/3600:.3f} h")

def og(t_src, arr): return np.interp(t, t_src, arr)

car_pA   = og(t_car,     carrier['phase_A'])
car_fA   = og(t_car,     carrier['freq_A'])
car_pB   = og(t_car,     carrier['phase_B'])
car_fB   = og(t_car,     carrier['freq_B'])
t_jitter = og(t_clk_dec, t_jitter_clk_dec)

# ── 7. DELAY, CROP EDGES, DETREND, TDI ───────────────────────────────────
delay_samp = delay_s_opt * fs
n_crop     = int(np.ceil(abs(delay_samp))) + 5

car_pB_dly = timeshift(car_pB,   -delay_samp)
car_fB_dly = timeshift(car_fB,   -delay_samp)
tj_dly     = timeshift(t_jitter, -delay_samp)

sl = slice(n_crop, -n_crop)
t, car_pA, car_fA, car_pB, car_fB, car_pB_dly, car_fB_dly, t_jitter, tj_dly = (
    x[sl] for x in [t, car_pA, car_fA, car_pB, car_fB,
                     car_pB_dly, car_fB_dly, t_jitter, tj_dly])

duration = t[-1] - t[0]
print(f"Post-crop: {len(t)} samples | {duration/3600:.3f} h")

car_pA_d = detrend(car_pA)
car_pB_d = detrend(car_pB_dly)
tj_d     = detrend(t_jitter)
tj_dly_d = detrend(tj_dly)
delta_tj = tj_d - tj_dly_d

tdi = car_pA_d - car_pB_d #- car_fB_dly * delta_tj

# ── 8. ASD ────────────────────────────────────────────────────────────────
def asd(x):
    nperseg = min(int(fs / FMIN), len(x))
    print(f"  nperseg={nperseg}")
    f, p = welch(x, fs=fs, nperseg=nperseg, detrend='constant')
    return f, np.sqrt(p)

print("\nComputing ASDs...")
f_tdi,  a_tdi  = asd(detrend(tdi))
f_dly,  a_dly  = asd(car_pA_d)
f_pure, a_pure = asd(detrend(car_pB))

# ── 9. ASD PLOT ───────────────────────────────────────────────────────────
title = (f'Carrier TDI | delay={delay_s_opt:.6f} s | offset={offset_s:.4f} s\n'
         f'duration={duration/3600:.2f} h')

plt.figure(figsize=(9, 5))
plt.loglog(f_tdi,  a_tdi,  lw=1.5, label='TDI Residual')
plt.loglog(f_dly,  a_dly,  lw=2,   label='Delayed signal (A)', alpha=0.8)
plt.loglog(f_pure, a_pure, lw=1,   label='Undelayed signal (B)', alpha=0.7)
plt.xlabel('Frequency (Hz)')
plt.ylabel('ASD (cyc / √Hz)')
plt.title(title)
plt.grid(True, which='both', ls='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig('plots/carrier_clk_tdi_asd.png', dpi=150)
print("Saved: plots/carrier_clk_tdi_asd.png")
plt.show()