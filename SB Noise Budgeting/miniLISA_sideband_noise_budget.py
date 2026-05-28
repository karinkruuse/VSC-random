import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import j0, j1
from scipy.constants import Boltzmann as kB, elementary_charge as e
from config_loader import cfg
import os

os.makedirs('outputs', exist_ok=True)

try:
    from noise_formulas import print_formula_summary, save_formula_page
except ImportError:
    def print_formula_summary(): pass
    def save_formula_page(path): pass


# ─────────────────────────────────────────────────────────────
# Parameters
# ─────────────────────────────────────────────────────────────

P_i    = cfg.instrument.P_i        # [W]
P_REF  = cfg.instrument.P_REF      # [W]
m      = cfg.instrument.m          # [rad]  EOM modulation depth
R      = cfg.instrument.R          # [A/W]  responsivity
eta    = cfg.instrument.eta        # [−]    heterodyne efficiency
C_pd   = cfg.instrument.C_pd       # [F]
I_dark_val = getattr(cfg.instrument, 'I_dark', 0.0)  # [A]     optional; 0 if NEP is set
S_amp      = getattr(cfg.instrument, 'S_amp',  0.0)  # [V/√Hz] optional; 0 if NEP is set

f_het  = cfg.beatnote.f_het        # [Hz]
nu_m   = cfg.modulation.nu_m       # [Hz]

lam    = cfg.laser.wavelength      # [m]
RIN    = cfg.laser.RIN_level       # [1/√Hz]

S_M0       = cfg.noise.S_M0        # [s/√Hz]
f_corner_M = cfg.noise.f_corner_M  # [Hz]
S_q0       = cfg.noise.S_q0        # [s/√Hz @ 1 Hz]

T = cfg.environment.T              # [K]


# ─────────────────────────────────────────────────────────────
# Derived quantities
# ─────────────────────────────────────────────────────────────

Z   = 1.0 / (2.0 * np.pi * C_pd * f_het)  # [Ω]  transimpedance at f_het
J1m = j1(m)                                # [−]
J0m = j0(m)                                # [−]

I_DC    = R * (P_i + P_REF)                # [A]   DC photocurrent
P_sb    = P_i * J1m**2                     # [W]   sideband power

A_sb_peak = 2 * R * Z * eta * np.sqrt(P_sb * P_REF)  # [V]  signal peak, single PD
A_sb_rms  = A_sb_peak / np.sqrt(2)                    # [V]  signal rms

freq_scaling   = f_het / nu_m              # [−]   beatnote → ranging observable
phase_to_disp  = lam / (2 * np.pi)        # [m/rad]


# ─────────────────────────────────────────────────────────────
# Frequency axis
# ─────────────────────────────────────────────────────────────

f = np.logspace(
    np.log10(cfg.science_band.f_science_min),
    np.log10(cfg.science_band.f_science_max),
    2000,
)   # [Hz]


# ─────────────────────────────────────────────────────────────
# BASELINE NOISE  (measured, from CSV)
# ─────────────────────────────────────────────────────────────
# Units in CSV: cyc/√Hz  →  rad/√Hz  (× 2π)
# Interpolated onto the script's frequency axis.
# Outside the CSV's frequency range the baseline is set to NaN
# and excluded from the total (no extrapolation).
# ─────────────────────────────────────────────────────────────

_baseline_path = 'baseline.csv'
sp_baseline = np.full_like(f, np.nan)   # [rad/√Hz]  NaN outside data range

if os.path.exists(_baseline_path):
    _bl = np.loadtxt(_baseline_path, delimiter=',', skiprows=1)
    _bl_f   = _bl[:, 0]
    _bl_asd = _bl[:, 1] * 2 * np.pi     # [rad/√Hz]

    # drop f=0 row and any non-positive frequencies
    _mask   = _bl_f > 0
    _bl_f   = _bl_f[_mask]
    _bl_asd = _bl_asd[_mask]

    # interpolate in log-log space onto script frequency axis
    _in_range = (f >= _bl_f[0]) & (f <= _bl_f[-1])
    if _in_range.any():
        sp_baseline[_in_range] = np.exp(
            np.interp(
                np.log(f[_in_range]),
                np.log(_bl_f),
                np.log(_bl_asd),
            )
        )
    print(f"  Baseline loaded: {_baseline_path}")
    print(f"  Coverage: {_bl_f[0]:.3e} – {_bl_f[-1]:.3e} Hz  ({_in_range.sum()} of {len(f)} freq bins)")
else:
    print(f"  Baseline file not found ({_baseline_path}) — omitted from total")

sqrt_S_ro_LISA = 600 / (2*np.pi) * 1e-6 * np.sqrt(1 + (0.7e-3/f)**4) / 2.4e9 * nu_m
# [rad/√Hz]


# ─────────────────────────────────────────────────────────────
# SHOT NOISE
# ─────────────────────────────────────────────────────────────

I_shot  = np.sqrt(2 * e * I_DC)           # [A/√Hz]  single PD
V_shot  = Z * I_shot                       # [V/√Hz]
sp_shot = np.sqrt(2) * V_shot / A_sb_rms * freq_scaling * np.ones_like(f)
# [rad/√Hz]  √2 for two independent PDs, freq_scaling for ranging observable


# ─────────────────────────────────────────────────────────────
# DETECTOR INTERNAL NOISE  (dark + thermal + amp)
#
# Two modes depending on what the toml provides:
#
#   NEP mode  — toml has instrument.NEP  [W/√Hz]
#       NEP is the datasheet-measured combined noise floor.
#       I_NEP = NEP × R  replaces dark + thermal + amp entirely.
#       sp_dark and sp_thermal are set to zero; sp_amp carries the NEP.
#
#   Estimated mode  — no NEP in toml
#       Individual terms computed from I_dark, S_amp, T, Z.
# ─────────────────────────────────────────────────────────────

NEP = getattr(cfg.instrument, 'NEP', None)   # [W/√Hz]  optional

if NEP is not None:
    # ── NEP mode ─────────────────────────────────────────────
    I_NEP      = NEP * R                     # [A/√Hz]  input-referred
    V_NEP      = Z * I_NEP                   # [V/√Hz]
    sp_NEP     = np.sqrt(2) * V_NEP / A_sb_rms * freq_scaling * np.ones_like(f)
    # [rad/√Hz]

    # Zero out the individual terms so total is unaffected
    sp_dark    = np.zeros_like(f)            # [rad/√Hz]  absorbed into NEP
    sp_thermal = np.zeros_like(f)            # [rad/√Hz]  absorbed into NEP
    sp_amp     = sp_NEP                      # [rad/√Hz]  NEP carried on amp line

else:
    # ── Estimated mode ───────────────────────────────────────
    sp_NEP     = None

    I_dark_noise = np.sqrt(2 * e * I_dark_val)   # [A/√Hz]
    V_dark       = Z * I_dark_noise               # [V/√Hz]
    sp_dark      = np.sqrt(2) * V_dark / A_sb_rms * freq_scaling * np.ones_like(f)
    # [rad/√Hz]

    I_thermal  = np.sqrt(4 * kB * T / Z)         # [A/√Hz]  input-referred
    V_thermal  = Z * I_thermal                    # [V/√Hz]
    sp_thermal = np.sqrt(2) * V_thermal / A_sb_rms * freq_scaling * np.ones_like(f)
    # [rad/√Hz]

    I_amp  = S_amp / Z                            # [A/√Hz]  input-referred
    V_amp  = Z * I_amp                            # [V/√Hz]
    sp_amp = np.sqrt(2) * V_amp / A_sb_rms * freq_scaling * np.ones_like(f)
    # [rad/√Hz]


# ─────────────────────────────────────────────────────────────
# 1f-RIN NOISE
# 50:50 BS: ρ² = τ² = 0.5
# SC beam carries sideband power P_i·J1²; REF is unmodulated
#
# Two modes depending on whether CMRR_dB is in the toml:
#
#   Unbalanced (no CMRR_dB):
#       √2 × single-PD, two independent SC lasers
#
#   Balanced (CMRR_dB present):
#       1f-RIN is common-mode and suppressed by the CMRR.
#       The residual after subtraction is divided by CMRR_linear.
#       Note: CMRR only suppresses the common-mode (REF-dominated)
#       part; the differential SC sideband term is not cancelled.
#       Conservative estimate: apply CMRR to the full 1f-RIN floor.
# ─────────────────────────────────────────────────────────────

CMRR_dB = getattr(cfg.instrument, 'CMRR_dB', None)  # [dB]  optional

V_RIN1f_1pd  = R * Z * RIN * np.sqrt((0.5 * P_sb)**2 + (0.5 * P_REF)**2)
# [V/√Hz]
sp_RIN1f_1pd = V_RIN1f_1pd / A_sb_rms               # [rad/√Hz]  single PD

if CMRR_dB is not None:
    CMRR_linear = 10 ** (CMRR_dB / 20)              # [−]  voltage ratio
    sp_RIN1f    = np.sqrt(2) * sp_RIN1f_1pd / CMRR_linear * freq_scaling * np.ones_like(f)
    # [rad/√Hz]  balanced: CMRR suppression applied
else:
    sp_RIN1f    = np.sqrt(2) * sp_RIN1f_1pd * freq_scaling * np.ones_like(f)
    # [rad/√Hz]  unbalanced: no suppression


# ─────────────────────────────────────────────────────────────
# 2f-RIN NOISE
# Power- and Bessel-independent (Wissel et al. 2022, eq. 40)
# Cannot be suppressed by balanced detection
# ─────────────────────────────────────────────────────────────

sp_RIN2f_1pd = RIN / 2.0                    # [rad/√Hz]  single PD
sp_RIN2f     = np.sqrt(2) * sp_RIN2f_1pd * freq_scaling * np.ones_like(f)
# [rad/√Hz]


# ─────────────────────────────────────────────────────────────
# MODULATION (EOM CLOCK) NOISE
# ─────────────────────────────────────────────────────────────

sqrt_S_M = S_M0 * np.sqrt(1 + (f_corner_M / f)**2)   # [s/√Hz]
sp_mod   = 2 * np.pi * (f_het + nu_m) * sqrt_S_M      # [rad/√Hz]


# ─────────────────────────────────────────────────────────────
# USO CLOCK NOISE
# ─────────────────────────────────────────────────────────────

sqrt_S_USO = S_q0 * f**(-3/2)              # [s/√Hz]
sp_USO     = 2 * np.pi * f_het * sqrt_S_USO  # [rad/√Hz]


# ─────────────────────────────────────────────────────────────
# TOTALS
# ─────────────────────────────────────────────────────────────

sp_tot_ro = np.sqrt(sp_shot**2 + sp_dark**2 + sp_thermal**2
                    + sp_amp**2 + sp_RIN1f**2 + sp_RIN2f**2)
# [rad/√Hz]  readout noise only

sp_tot = np.sqrt(sp_tot_ro**2 + sp_mod**2)
# [rad/√Hz]  + modulation clock (USO omitted by default)

# Add baseline in quadrature only where data exists (NaN elsewhere)
_bl_sq = np.where(np.isfinite(sp_baseline), sp_baseline**2, 0.0)
sp_tot_with_baseline = np.sqrt(sp_tot**2 + _bl_sq)
# NaN outside baseline coverage so the line only appears where data exists
sp_tot_with_baseline[~np.isfinite(sp_baseline)] = np.nan


# ─────────────────────────────────────────────────────────────
# CONSOLE SUMMARY
# ─────────────────────────────────────────────────────────────

print_formula_summary()
save_formula_page('outputs/miniLISA_formula_reference.png')

pd_model = getattr(cfg.instrument, 'PD_model', 'unknown PD')
f_ref    = 1e-3
idx      = np.argmin(np.abs(f - f_ref))

noise_rows = [
    ('Shot',        sp_shot),
]
rin1f_label = (f'1f-RIN (balanced, {CMRR_dB:.0f} dB CMRR)' if CMRR_dB is not None
               else '1f-RIN (unbalanced)')
noise_rows.append((rin1f_label, sp_RIN1f))
noise_rows.append(('2f-RIN', sp_RIN2f))

if NEP is not None:
    noise_rows.append((f'NEP ({NEP:.1e} W/√Hz)', sp_amp))
else:
    noise_rows += [
        ('Dark',    sp_dark),
        ('Thermal', sp_thermal),
        ('Amp',     sp_amp),
    ]
noise_rows += [
    ('Mod noise',  sp_mod),
    ('USO',        sp_USO),
    ('Total (RO)', sp_tot_ro),
    ('Total',      sp_tot),
]
if np.isfinite(sp_baseline[idx]):
    noise_rows.append(('Baseline (measured)', sp_baseline))
    noise_rows.append(('Total + baseline',    sp_tot_with_baseline))

print(f"\n{'─'*52}")
print(f"  miniLISA noise budget  —  {pd_model}")
print(f"{'─'*52}")
print(f"  Z             = {Z:.1f} Ω")
print(f"  A_sb (peak)   = {A_sb_peak:.3e} V")
print(f"  I_DC          = {I_DC*1e3:.3f} mA")
print(f"  freq_scaling  = f_het/nu_m = {freq_scaling:.3f}")
if NEP is not None:
    print(f"  NEP mode      = ON  ({NEP:.1e} W/√Hz)")
else:
    print(f"  NEP mode      = OFF  (estimating dark + thermal + amp)")
if CMRR_dB is not None:
    print(f"  RIN mode      = balanced  (CMRR = {CMRR_dB:.0f} dB)")
else:
    print(f"  RIN mode      = unbalanced")
print(f"\n  Phase noise ASDs at f = {f_ref*1e3:.0f} mHz  [rad/√Hz]:")
for name, arr in noise_rows:
    print(f"    {name:<36}  {arr[idx]:.2e}")
print(f"{'─'*56}\n")


# ─────────────────────────────────────────────────────────────
# PLOT
# ─────────────────────────────────────────────────────────────

colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
fig, ax = plt.subplots(figsize=(10, 6))
fig.suptitle('miniLISA Sideband Readout Noise Budget', fontsize=14, fontweight='bold')
ax.set_title(f'Photodetector: {pd_model}', fontsize=10, color='dimgrey')

ax.loglog(f, sp_shot,         label=f'Shot noise, laser power {P_i*1e3:.1f} mW',               color=colors[0])
rin1f_plot_label = (f'1f-RIN (balanced, {CMRR_dB:.0f} dB)' if CMRR_dB is not None
                    else '1f-RIN (unbalanced)')
ax.loglog(f, sp_RIN1f,        label=rin1f_plot_label,            color=colors[4])
ax.loglog(f, sp_RIN2f,        label='2f-RIN',                   color=colors[5])

if NEP is not None:
    ax.loglog(f, sp_amp,      label=f'NEP  ({NEP:.1e} W/√Hz)',  color=colors[3])
else:
    ax.loglog(f, sp_dark,     label='Dark noise',               color=colors[1])
    ax.loglog(f, sp_thermal,  label='Thermal noise',            color=colors[2], linestyle='--')
    ax.loglog(f, sp_amp,      label='Amp noise',                color=colors[3])

ax.loglog(f, sp_tot_ro,       label='Total readout noise',          color='grey',   lw=2, alpha=0.7)
ax.loglog(f, sqrt_S_ro_LISA,  label='LISA readout limit (scaled)',   color='k',      lw=2, linestyle='--')
ax.loglog(f, sqrt_S_ro_LISA*240,  label='LISA readout limit',   color='gray',      lw=2, linestyle='--')



S_req = 60e-6 * (1.0 + 0.07 / f)  # rad/√Hz, this modulation noise will be f_het/nu_m scaled in post processing

ax.loglog(f, S_req,
           linestyle="--",
           color="k",
           linewidth=1.2,
           label=r"Requirement: $60\left(1+\frac{70\,\mathrm{mHz}}{f}\right)\,\mu$rad/$\sqrt{\mathrm{Hz}}$")



if np.isfinite(sp_baseline).any():
    ax.loglog(f, sp_baseline,         label='Delay line intrinsic noise',          color='black',  lw=1, linestyle=':', alpha=0.8)
    ax.loglog(f, sp_tot_with_baseline, label='Readout + delay line noise',            color='crimson', lw=2)

ax.set_xlabel('Fourier frequency [Hz]')
ax.set_ylabel('Phase noise ASD [rad/√Hz]')
ax.legend(fontsize=9)
ax.grid(True, which='both', alpha=0.3)
ax.set_xlim(f[0], f[-1])

ax2 = ax.twinx()
ax2.set_yscale('log')
ax2.set_ylim(np.array(ax.get_ylim()) * phase_to_disp)
ax2.set_ylabel('Displacement noise ASD [m/√Hz]')

plt.tight_layout()

pd_slug = pd_model.replace(' ', '_').replace('/', '-')
outpath = f'outputs/miniLISA_sideband_noise_budget_{pd_slug}.png'
plt.savefig(outpath, dpi=300, bbox_inches='tight')
print(f"Plot saved to {outpath}")