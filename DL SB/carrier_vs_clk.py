import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend, welch
from scipy.optimize import minimize_scalar
from pytdi.dsp import timeshift

# ── CONFIG ────────────────────────────────────────────────────────────────
FILE_CARRIER = 'data/Carrier_20260526_160851.npy'
FILE_CLK     = 'data/CLK_20260526_160854.npy'

# Arm delay search (Carrier A vs Carrier B — same file, no offset problem)
DELAY_NOMINAL_S = 4.1   # programmed delay (s)
DELAY_SEARCH_S  = 0.5   # ± around nominal (s)

# Start-time offset search (Carrier file vs CLK file)
# Carrier started ~3 s BEFORE CLK → negative value shifts carrier forward
OFFSET_NOMINAL_S = -3.0  # rough prior (s)
OFFSET_SEARCH_S  =  1.0  # ± around nominal (s)

# PSD integration band for both optimisation stages
FMIN_OBJ = 1e-3  # Hz
FMAX_OBJ = 1.0   # Hz

# ASD plot floor
FMIN_ASD = 9e-4  # Hz

# Segment length for coarse searches (None = all data)
COARSE_SEGMENT_S = 5 * 60   # 5 min

# ── ─────────────────────────────────────────────────────────────────────────
# 1. LOAD
# ──────────────────────────────────────────────────────────────────────────
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

if abs(fs - fs_clk) / fs > 1e-3:
    print(f"  WARNING: sample rates differ by more than 0.1% "
          f"({fs:.6f} vs {fs_clk:.6f} Hz)")

# Timing jitter from CLK channel A [seconds]
t_jitter_clk = clk['phase_A'] / clk['freq_A']

# ── ─────────────────────────────────────────────────────────────────────────
# 2. STAGE 1 — ARM DELAY  from Carrier A vs Carrier B
#    Both channels live in the same file on the same time axis,
#    so there is NO inter-file offset to worry about here.
# ──────────────────────────────────────────────────────────────────────────
def carrier_ab_psd(delay_s, segment_s=None):
    """
    Integrated PSD of (pA_detrended - pB_delayed_detrended).
    Uses only the Carrier file — no CLK involved.
    """
    t     = carrier['t']
    pA    = detrend(carrier['phase_A'])
    pB    = detrend(carrier['phase_B'])

    if segment_s is not None:
        mask = t <= t[0] + segment_s
        t, pA, pB = t[mask], pA[mask], pB[mask]

    delay_samp = delay_s * fs
    n_crop     = int(np.ceil(abs(delay_samp))) + 5

    if len(t) < 2 * n_crop + 20:
        return np.inf

    pB_dly = timeshift(pB, -delay_samp)

    sl    = slice(n_crop, -n_crop)
    pA_d  = detrend(pA[sl])
    pBd_d = detrend(pB_dly[sl])

    residual = pA_d - pBd_d

    nperseg = min(int(fs / FMIN_OBJ), len(residual))
    f, psd  = welch(residual, fs=fs, nperseg=nperseg, detrend='constant')
    band    = (f >= FMIN_OBJ) & (f <= FMAX_OBJ)
    if band.sum() < 2:
        return np.inf
    return float(np.trapz(psd[band], f[band]))


# Coarse sweep
print(f"\n── Stage 1: arm delay (Carrier A vs B), "
      f"coarse sweep on first {COARSE_SEGMENT_S/60:.0f} min ──")
n_coarse  = 50
delays_c  = np.linspace(DELAY_NOMINAL_S - DELAY_SEARCH_S,
                         DELAY_NOMINAL_S + DELAY_SEARCH_S, n_coarse)
psds_delay = np.array([carrier_ab_psd(d, segment_s=COARSE_SEGMENT_S)
                        for d in delays_c])

best_i  = np.nanargmin(psds_delay)
delay0  = delays_c[best_i]
print(f"  Coarse minimum: delay = {delay0:.6f} s  "
      f"(integrated PSD = {psds_delay[best_i]:.4e})")

# Fine optimisation on all data
print(f"  Fine optimisation on all data...")
res_delay = minimize_scalar(
    lambda d: carrier_ab_psd(d, segment_s=None),
    bounds=(delay0 - 0.05, delay0 + 0.05),
    method='bounded',
    options={'xatol': 1e-8, 'maxiter': 300},
)
delay_s_opt = float(res_delay.x)
print(f"  Fine result: delay = {delay_s_opt:.9f} s")
"""
# Coarse delay curve plot
fig, ax = plt.subplots(figsize=(8, 4))
ax.semilogy(delays_c, psds_delay, 'o-', ms=4)
ax.axvline(delay_s_opt, color='r', ls='--',
           label=f'opt = {delay_s_opt:.6f} s')
ax.set_xlabel('Delay (s)')
ax.set_ylabel('Integrated PSD (Carrier A − B)')
ax.set_title('Stage 1 — arm delay coarse sweep (Carrier A vs B)')
ax.legend(); ax.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig('plots/stage1_delay_sweep.png', dpi=150)
print("  Saved: plots/stage1_delay_sweep.png")
"""


# ── ─────────────────────────────────────────────────────────────────────────
# 3. STAGE 2 — INTER-FILE OFFSET  via full TDI minimisation
#    Now we fix delay_s_opt and vary offset_s.
#    TDI =  pA_d  -  pB_dly_d  -  fB_dly * (tj_d - tj_dly_d)
#    same combination as analysis_w_debug.py
# ──────────────────────────────────────────────────────────────────────────
def full_tdi_psd(offset_s, delay_s, segment_s=None):
    """
    Integrated PSD of the full TDI combination including CLK jitter correction.

    offset_s : time to ADD to carrier['t'] to align it onto the CLK time axis
    delay_s  : arm delay (fixed from Stage 1)
    """
    t_car = carrier['t'] + offset_s

    t0 = max(clk['t'][0],  t_car[0])
    t1 = min(clk['t'][-1], t_car[-1])
    if segment_s is not None:
        t1 = min(t1, t0 + segment_s)

    delay_samp = delay_s * fs
    n_crop     = int(np.ceil(abs(delay_samp))) + 5

    mask = (clk['t'] >= t0) & (clk['t'] <= t1)
    grid = clk['t'][mask]

    if len(grid) < 2 * n_crop + 20:
        return np.inf

    def og_car(arr): return np.interp(grid, t_car,    arr)
    def og_clk(arr): return np.interp(grid, clk['t'], arr)

    pA  = og_car(carrier['phase_A'])
    pB  = og_car(carrier['phase_B'])
    fB  = og_car(carrier['freq_B'])
    tj  = og_clk(t_jitter_clk)

    pB_dly = timeshift(pB,  -delay_samp)
    fB_dly = timeshift(fB,  -delay_samp)
    tj_dly = timeshift(tj,  -delay_samp)

    sl = slice(n_crop, -n_crop)
    pA, pB_dly, fB_dly, tj, tj_dly = (
        x[sl] for x in [pA, pB_dly, fB_dly, tj, tj_dly])

    pA_d     = detrend(pA)
    pB_dly_d = detrend(pB_dly)
    tj_d     = detrend(tj)
    tj_dly_d = detrend(tj_dly)

    tdi = pA_d - pB_dly_d - fB_dly * (tj_d - tj_dly_d)

    nperseg = min(int(fs / FMIN_OBJ), len(tdi))
    f, psd  = welch(tdi, fs=fs, nperseg=nperseg, detrend='constant')
    band    = (f >= FMIN_OBJ) & (f <= FMAX_OBJ)
    if band.sum() < 2:
        return np.inf
    return float(np.trapz(psd[band], f[band]))


# Coarse sweep
print(f"\n── Stage 2: inter-file offset (full TDI), "
      f"coarse sweep on first {COARSE_SEGMENT_S/60:.0f} min ──")
print(f"  (delay fixed at {delay_s_opt:.9f} s)")
n_coarse   = 50
offsets_c  = np.linspace(OFFSET_NOMINAL_S - OFFSET_SEARCH_S,
                          OFFSET_NOMINAL_S + OFFSET_SEARCH_S, n_coarse)
psds_offset = np.array([full_tdi_psd(o, delay_s_opt, segment_s=COARSE_SEGMENT_S)
                         for o in offsets_c])

best_i   = np.nanargmin(psds_offset)
offset0  = offsets_c[best_i]
print(f"  Coarse minimum: offset = {offset0:.6f} s  "
      f"(integrated PSD = {psds_offset[best_i]:.4e})")

# Fine optimisation on all data
print(f"  Fine optimisation on all data...")
res_offset = minimize_scalar(
    lambda o: full_tdi_psd(o, delay_s_opt, segment_s=None),
    bounds=(offset0 - 0.5, offset0 + 0.5),
    method='bounded',
    options={'xatol': 1e-6, 'maxiter': 300},
)
offset_s_opt = float(res_offset.x)
print(f"  Fine result: offset = {offset_s_opt:.6f} s")

# Coarse offset curve plot
fig, ax = plt.subplots(figsize=(8, 4))
ax.semilogy(offsets_c, psds_offset, 'o-', ms=4)
ax.axvline(offset_s_opt, color='r', ls='--',
           label=f'opt = {offset_s_opt:.6f} s')
ax.set_xlabel('Offset (s)')
ax.set_ylabel('Integrated PSD (full TDI)')
ax.set_title(f'Stage 2 — inter-file offset coarse sweep\n'
             f'(delay fixed: {delay_s_opt:.6f} s)')
ax.legend(); ax.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig('plots/stage2_offset_sweep.png', dpi=150)
print("  Saved: plots/stage2_offset_sweep.png")
"""
# ── ─────────────────────────────────────────────────────────────────────────
# 4. FINAL DATASET
# ──────────────────────────────────────────────────────────────────────────
print(f"\n── Building final dataset ──")
print(f"  delay  = {delay_s_opt:.9f} s")
print(f"  offset = {offset_s_opt:.6f} s")

t_car = carrier['t'] + offset_s_opt
t0    = max(clk['t'][0],  t_car[0])
t1    = min(clk['t'][-1], t_car[-1])

delay_samp = delay_s_opt * fs
n_crop     = int(np.ceil(abs(delay_samp))) + 5

mask = (clk['t'] >= t0) & (clk['t'] <= t1)
grid = clk['t'][mask]

def og_car(arr): return np.interp(grid, t_car,    arr)
def og_clk(arr): return np.interp(grid, clk['t'], arr)

pA  = og_car(carrier['phase_A'])
pB  = og_car(carrier['phase_B'])
fB  = og_car(carrier['freq_B'])
tj  = og_clk(t_jitter_clk)

pB_dly = timeshift(pB,  -delay_samp)
fB_dly = timeshift(fB,  -delay_samp)
tj_dly = timeshift(tj,  -delay_samp)

sl = slice(n_crop, -n_crop)
t_final, pA, pB_dly, fB_dly, tj, tj_dly = (
    x[sl] for x in [grid, pA, pB_dly, fB_dly, tj, tj_dly])

pA_d     = detrend(pA)
pB_dly_d = detrend(pB_dly)
tj_d     = detrend(tj)
tj_dly_d = detrend(tj_dly)

tdi_final = pA_d - pB_dly_d - fB_dly * (tj_d - tj_dly_d)
tdi_final = detrend(tdi_final)

# also keep A-B without jitter correction for comparison
tdi_no_clk = detrend(pA_d - pB_dly_d)

duration = t_final[-1] - t_final[0]
print(f"  {len(t_final)} samples | {duration/3600:.3f} h")


plt.plot(pA_d, label='pA_d')
plt.plot(pB_dly_d, label='pB_dly_d')
plt.show()

"""
def compute_asd(x, fmin=FMIN_ASD):
    nperseg = min(int(fs / fmin), len(x))
    print(f"  nperseg = {nperseg}  (signal length = {len(x)})")
    f, psd = welch(x, fs=fs, nperseg=nperseg, detrend='constant')
    return f, np.sqrt(psd)

print("\nComputing ASDs...")
f_tdi,    a_tdi    = compute_asd(tdi_final)
f_noclk,  a_noclk  = compute_asd(tdi_no_clk)
f_pA,     a_pA     = compute_asd(pA_d)
f_pB,     a_pB     = compute_asd(detrend(og_car(carrier['phase_B'])[sl]))

# ── ─────────────────────────────────────────────────────────────────────────
# 6. ASD PLOT
# ──────────────────────────────────────────────────────────────────────────
title = (f'Carrier TDI  |  delay = {delay_s_opt:.9f} s  |  offset = {offset_s_opt:.6f} s\n'
         f'duration = {duration/3600:.3f} h')

plt.figure(figsize=(10, 5))
plt.loglog(f_tdi,   a_tdi,   lw=1.5, label='TDI + CLK jitter correction')
plt.loglog(f_noclk, a_noclk, lw=1.5, label='TDI (A−B, no CLK correction)',
           ls='--', alpha=0.8)
plt.loglog(f_pA,    a_pA,    lw=1.0, label='Carrier A (delayed arm)', alpha=0.6)
plt.loglog(f_pB,    a_pB,    lw=1.0, label='Carrier B (direct arm)',  alpha=0.6)
plt.xlabel('Frequency (Hz)')
plt.ylabel('ASD (cyc / √Hz)')
plt.title(f'Carrier TDI | optimal delay = {delay_opt:.9f} s')
plt.grid(True, which='both', ls='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig('plots/carrier_clk_tdi_asd.png', dpi=150)
print("Saved: plots/carrier_clk_tdi_asd.png")
plt.show()
"""
