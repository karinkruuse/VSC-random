import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import j0, j1
from config_loader import cfg
from scipy.constants import Boltzmann as kB, elementary_charge as e
import os

os.makedirs('outputs', exist_ok=True)

# ─────────────────────────────────────────────
# Formula printer (latexify — generates LaTeX from Python AST)
# noise_formulas.py must be in the same directory.
# ─────────────────────────────────────────────
try:
    from noise_formulas import print_formula_summary, save_formula_page
except ImportError:
    def print_formula_summary():
        print('(noise_formulas.py not found — skipping formula summary)')
    def save_formula_page(path):
        print(f'(noise_formulas.py not found — skipping formula page: {path})')

    print(f"{'='*W}")

    section("SIGNAL AMPLITUDE  [V peak, single PD port]")
    row("Sideband signal (peak)",
        "2 * R * Z * eta * J1m * sqrt(P_i * P_REF)",
        "[V]",
        "50:50 BS (2rho*tau=1), one sideband x unmodulated REF")
    row("Signal rms",
        "A_sb_1pd / sqrt(2)",
        "[V]",
        "sinusoid peak to rms")

    section("DC PHOTOCURRENT  [A]")
    row("I_DC",
        "R * (P_i + P_REF)",
        "[A]",
        "full beam power on PD (EOM does not change total power)")

    section("SINGLE-PD ELECTRONIC NOISE  [A/sqrt(Hz)]")
    row("Shot noise",
        "sqrt(2 * e * I_DC)",
        "[A/sqrt(Hz)]")
    row("Dark-current shot noise",
        "sqrt(2 * e * I_dark_datasheet)",
        "[A/sqrt(Hz)]")
    row("Thermal / Johnson noise (TIA input-referred)",
        "sqrt(4 * kB * T / Z)",
        "[A/sqrt(Hz)]",
        "Johnson noise of transimpedance Z")
    row("TIA voltage noise (input-referred)",
        "S_amp / Z",
        "[A/sqrt(Hz)]",
        "S_amp is voltage ASD of amplifier [V/sqrt(Hz)]")

    section("1f-RIN PHASE NOISE  [rad/sqrt(Hz), single PD]")
    row("Voltage noise from 1f-RIN",
        "R * Z * RIN_level * sqrt((0.5 * P_i * J1m**2)**2 + (0.5 * P_REF)**2)",
        "[V/sqrt(Hz)]",
        "50:50 BS: rho2=tau2=0.5; SC sideband power P_i*J1^2; REF unmodulated")
    row("Phase noise (divided by signal rms)",
        "V_RIN1f_1pd / A_sb_rms",
        "[rad/sqrt(Hz)]",
        "R*Z cancels; eta and J1 remain via A_sb_rms denominator")

    section("2f-RIN PHASE NOISE  [rad/sqrt(Hz), single PD]")
    row("2f-RIN (power/Bessel independent — Wissel 2022 eq.40)",
        "RIN_level / 2",
        "[rad/sqrt(Hz)]",
        "coupling via beat amplitude cancels with A_sb_rms; uncorrelated lasers")

    section("TWO-PD COMBINATION  (sqrt(2) for independent additive noise)")
    row("Electronic noise (two independent PDs)",
        "sqrt(2) * sqrt_S_elec_1pd",
        "[V/sqrt(Hz)]")
    row("1f-RIN (unbalanced, worst case)",
        "sqrt(2) * sp_RIN1f_1pd",
        "[rad/sqrt(Hz)]",
        "1f-RIN same sign both ports; sqrt(2) for two independent SC lasers")
    row("2f-RIN (cannot cancel with balanced detection)",
        "sqrt(2) * sp_RIN2f_1pd",
        "[rad/sqrt(Hz)]")

    section("FREQ SCALING  (beatnote phase to sideband ranging observable)")
    row("Scale factor",
        "f_het / nu_m",
        "[dimensionless]",
        "additive noise at f_het propagates to r_ij scaled by f_het/nu_m (Barke PhD)")

    section("TIMING / CLOCK NOISE  [rad/sqrt(Hz)]")
    row("Modulation (EOM clock) noise",
        "2 * pi * (f_het + nu_m) * S_M0 * sqrt(1 + (f_corner_M / f)**2)",
        "[rad/sqrt(Hz)]")
    row("USO clock noise",
        "2 * pi * f_het * S_q0 * f**(-3/2)",
        "[rad/sqrt(Hz)]")

    section("DISPLACEMENT CONVERSION")
    row("Phase to displacement (one-way)",
        "phi * lam / (2 * pi)",
        "[m/sqrt(Hz)]")

    print(f"\n{'='*W}\n")


# ─────────────────────────────────────────────
# Fundamental constants
# ─────────────────────────────────────────────
# (Physical constants from scipy; experiment parameters from toml)

# ─────────────────────────────────────────────
# Parameters  (from minilisa_config.toml)
# ─────────────────────────────────────────────
# Optical powers  [W]
P_i   = cfg.instrument.P_i       # SC laser power
P_REF = cfg.instrument.P_REF     # reference laser power

# Derived E-field amplitudes [sqrt(W)]  (kept for legacy signal formula)
E_i   = np.sqrt(P_i)
E_REF = np.sqrt(P_REF)

m      = cfg.instrument.m    # EOM modulation depth  [rad]
R      = cfg.instrument.R    # photodiode responsivity [A/W]
eta    = cfg.instrument.eta  # heterodyne efficiency (overlap integral)

# Frequencies
f_het  = cfg.beatnote.f_het    # heterodyne beatnote freq [Hz]
nu_m   = cfg.modulation.nu_m   # EOM modulation frequency [Hz]

# Transimpedance: single-pole RC model
# Z = 1 / (2π C_pd f_het)  [Ω]
# For a bare 50 Ω PD (no TIA), set C_pd = 1/(2π × f_het × 50) in the toml
# so this formula evaluates to exactly 50 Ω — no script changes needed.
C_pd = cfg.instrument.C_pd
Z = 1.0 / (2.0 * np.pi * C_pd * f_het)   # [V/A]

# ─────────────────────────────────────────────
# Noise parameters  (from toml)
# ─────────────────────────────────────────────
I_dark_datasheet = cfg.instrument.I_dark   # dark current [A]
S_amp            = cfg.instrument.S_amp    # TIA voltage noise ASD [V/sqrt(Hz)]; 0 for bare PD
RIN_level        = cfg.laser.RIN_level     # laser RIN ASD [1/sqrt(Hz)]

# Modulation (clock) noise
S_M0       = cfg.noise.S_M0        # white timing floor  [s/sqrt(Hz)]
f_corner_M = cfg.noise.f_corner_M  # 1/f corner          [Hz]

# USO clock noise
S_q0 = cfg.noise.S_q0              # [s/sqrt(Hz)] at 1 Hz

# Laser wavelength and temperature
lam = cfg.laser.wavelength          # [m]
T   = cfg.environment.T             # [K]

# ─────────────────────────────────────────────
# Frequency axis
# ─────────────────────────────────────────────
f = np.logspace(np.log10(cfg.science_band.f_science_min),
                np.log10(cfg.science_band.f_science_max), 2000)

print(f"miniLISA vs LISA modulation freq ratio: {nu_m/2.4e9:.5f}")

# LISA readout requirement (scaled to miniLISA nu_m)
sqrt_S_ro = 600/(2*np.pi) * 1e-6 * np.sqrt(1 + (0.7e-3/f)**4) / 2.4e9 * nu_m

# ─────────────────────────────────────────────
# Bessel factors
# Only the SC beam is EOM-modulated; REF is unmodulated.
# The sideband signal beatnote is:
#   SC sideband  (J1(m) * E_i)  ×  REF carrier  (J0=1 * E_REF)
# ─────────────────────────────────────────────
J0m = j0(m)
J1m = j1(m)

# ─────────────────────────────────────────────
# Signal amplitude — voltage at TIA output [V] (peak of the AC beatnote)
#
# Optical power at one PD port (50:50 BS, ρ=τ=1/√2):
#   P_beat = 2 ρτ η_het √(P_sb · P_REF) = η_het √(P_i J1²(m) · P_REF)
#            [uses ρτ = 1/2 for 50:50]
# Current amplitude:  I_beat = R · P_beat
# Voltage amplitude:  A_sb  = I_beat · Z   (peak, not rms)
# The factor 2 below comes from 2ρτ = 1 for a 50:50 BS.
# ─────────────────────────────────────────────
P_sb = P_i * J1m**2          # power in one sideband  [W]
# Signal amplitude (peak voltage, single PD port) [V]
A_sb_1pd = 2 * R * Z * eta * np.sqrt(P_sb * P_REF)
# = 2 R Z eta sqrt(P_i) sqrt(P_REF) J1(m)   — identical to original formula
A_sb_rms = A_sb_1pd / np.sqrt(2)   # signal rms amplitude [V] (peak/√2 for a sinusoid)

# DC photocurrent for shot noise: total optical power on PD
# SC beam power with EOM modulation: carrier J0² + sideband J1² (×2 for ±1)
# In practice the full beam power P_i lands on the PD.
I_DC = R * (P_i + P_REF)    # [A]

print("\nminiLISA signal amplitudes:")
print(f"  A_carrier = {2*R*Z*eta*E_i*E_REF*J0m:.3e} V   [single J0 sideband × REF carrier]")
print(f"  A_sb      = {A_sb_1pd:.3e} V   [single J1, J1/J0 = {J1m/J0m:.4f}]")
print(f"  Z         = {Z:.1f} Ohm")
print(f"  I_DC      = {I_DC*1e3:.3f} mA")
print(f"  P_sb/P_i  = {P_sb/P_i:.4f}  (J1²(m))")

# ─────────────────────────────────────────────
# SINGLE-PD NOISE ASDs  [A/sqrt(Hz)] in current domain
#
# All noise sources are computed as equivalent current ASDs
# so they can be combined before converting to phase.
# ─────────────────────────────────────────────

# 1) Shot noise  [A/sqrt(Hz)]
I_shot = np.sqrt(2 * e * I_DC)

# 2) Dark-current shot noise  [A/sqrt(Hz)]
I_dark = np.sqrt(2 * e * I_dark_datasheet)

# 3) Johnson / thermal noise of the transimpedance  [A/sqrt(Hz)]
#    Referred to the input of the TIA.
I_thermal = np.sqrt(4 * kB * T / Z)

# 4) TIA voltage noise, referred to input  [A/sqrt(Hz)]
I_amp = S_amp / Z

# Combined single-PD voltage noise at TIA output  [V/sqrt(Hz)]
# (quadrature sum, then × Z to get volts)
sqrt_S_elec_1pd = Z * np.sqrt(I_shot**2 + I_dark**2 + I_thermal**2 + I_amp**2)

# ─────────────────────────────────────────────
# RIN-TO-PHASE COUPLING
#
# Starting from Wissel et al. (2022) eq. (19a) but with the EOM included:
# only the SC beam is modulated, so the power that beats against P_REF
# to form the sideband signal is  P_i * J1²(m).  The REF is unmodulated.
#
# 50:50 BS: ρ² = τ² = 1/2,  ρτ = 1/2.
# SC and REF lasers: uncorrelated RIN  r̃_i = r̃_REF = r̃ = RIN_level.
#
# ── 1f-RIN ──────────────────────────────────
# The 1f-RIN power fluctuation at port A is (Wissel eq. 19a):
#   δP_A^1f = ρ² · (P_i J1²) · r̃_i  +  τ² · P_REF · r̃_REF
# (J1² because only the sideband field participates in the beat)
#
# As a voltage noise at the TIA output [V/sqrt(Hz)]:
#   Ṽ_1f,A = R·Z · sqrt( (ρ² P_i J1²)² + (τ² P_REF)² ) · r̃
#           = (R·Z·r̃/2) · sqrt( (P_i J1²)² + P_REF² )
#
# Signal rms at the same port:
#   A_rms = A_sb / √2  =  R·Z·η·J1·√(P_i·P_REF) · √2
#   (A_sb = 2RZη J1 √(P_i P_REF) is the peak amplitude)
#
# Phase noise (Wissel eq. 31,  α̃ = Ṽ_noise / A_rms):
#
#   α̃_1f = (R·Z·r̃/2) · sqrt((P_i J1²)² + P_REF²)
#           ─────────────────────────────────────────
#                R·Z·η·J1·√(P_i·P_REF)·√2
#
#         = r̃ · sqrt((P_i J1²)² + P_REF²)
#           ─────────────────────────────────
#              2√2 · η · J1 · √(P_i · P_REF)
#
# Note: R·Z cancels, leaving a pure optical expression.
#
# ── 2f-RIN ──────────────────────────────────
# The 2f coupling is via the beat term itself (Wissel eq. 19a, 2f part):
#   δP_A^2f ∝ (r̃_i + r̃_REF)/2 · ρτ · η · √(P_i J1² · P_REF)
# Normalised by A_rms ∝ ρτ · η · √(P_i J1² · P_REF), these cancel.
# The 2f phase coupling coefficient is therefore power/Bessel independent:
#   α̃_2f = r̃ / 2    (single port, uncorrelated, 50:50 BS)
# This is Wissel eq. (40) — unchanged by the EOM.
# ─────────────────────────────────────────────

rho2 = 0.5    # ρ² for 50:50 BS
tau2 = 0.5    # τ²

# Effective SC sideband power seen by PD  [W]
P_sb_eff = P_i * J1m**2

# 1f-RIN voltage noise ASD at TIA output, single port  [V/sqrt(Hz)]
V_RIN1f_1pd = R * Z * RIN_level * np.sqrt((rho2 * P_sb_eff)**2 + (tau2 * P_REF)**2)

# Convert to phase: divide by A_sb_rms = A_sb_1pd / sqrt(2)
sp_RIN1f_1pd = V_RIN1f_1pd / A_sb_rms * np.ones_like(f)

# Equivalently (R·Z cancels):
# sp_RIN1f_1pd = RIN_level * sqrt((P_sb_eff/2)² + (P_REF/2)²)
#                / (eta * J1m * sqrt(P_i * P_REF))

# 2f-RIN phase noise [rad/sqrt(Hz)] — single PD, power/Bessel independent
sp_RIN2f_1pd = RIN_level / 2.0 * np.ones_like(f)

# ─────────────────────────────────────────────
# MODULATION AND CLOCK NOISE  [s/sqrt(Hz)]
# ─────────────────────────────────────────────
sqrt_S_M   = S_M0 * np.sqrt(1 + (f_corner_M / f)**2)
sqrt_S_USO = S_q0 * f**(-3/2)

# ─────────────────────────────────────────────
# TWO-PD (BALANCED) READOUT COMBINATION
#
# For additive (electronic) noise:
#   Both PDs independent  →  power adds  →  amplitude × √2
#
# For RIN:
#   1f-RIN: appears with SAME sign at both ports → DOES subtract
#           with balanced detection (Wissel §III). For worst-case
#           estimate (no cancellation / unbalanced) keep both.
#           Two independent SC lasers: add quadratically (×√2 in amplitude).
#           REF laser is CORRELATED between ports: adds coherently (×2).
#           We compute the combined two-port noise conservatively
#           (unbalanced / no cancellation).
#
#   2f-RIN: appears with SAME sign as signal, CANNOT be cancelled
#           by balanced detection. Two independent PD terms add in quadrature.
# ─────────────────────────────────────────────

# --- Additive (electronic) noise, two independent PDs ---
# Combined voltage ASD for the difference readout: sqrt(2) in amplitude
sqrt_S_elec_2pd = np.sqrt(2) * sqrt_S_elec_1pd   # [V/sqrt(Hz)]

# Convert additive voltage noise → phase noise [rad/sqrt(Hz)]
# Using Wissel eq. (31):  α̃ = noise_ASD / signal_rms
# (The √2 from eq.30 is already absorbed: noise_ASD here is the two-sided floor,
#  and we use the signal *peak* / √2 = rms, so α̃ = sqrt_S_V / A_rms)
sp_elec = sqrt_S_elec_2pd / A_sb_rms   # [rad/sqrt(Hz)]

# Breakdown for plotting
sp_shot    = np.sqrt(2) * Z * I_shot   / A_sb_rms * np.ones_like(f)
sp_dark    = np.sqrt(2) * Z * I_dark   / A_sb_rms * np.ones_like(f)
sp_thermal = np.sqrt(2) * Z * I_thermal / A_sb_rms * np.ones_like(f)
sp_amp     = np.sqrt(2) * Z * I_amp    / A_sb_rms * np.ones_like(f)

# --- RIN noise, two-PD combination ---
# Conservative (unbalanced) estimate: √2 × single-port for 1f (independent SC lasers),
# plus REF is common to both ports: treat as correlated → add linearly for worst case.
# We keep single-PD worst-case value × √2 for the SC-dominated term:
sp_RIN1f = np.sqrt(2) * sp_RIN1f_1pd   # two independent SC lasers, unbalanced

# 2f-RIN: cannot cancel, two PDs add in quadrature
sp_RIN2f = np.sqrt(2) * sp_RIN2f_1pd

# ─────────────────────────────────────────────
# FREQ SCALING: sideband ranging observable
#
# The sideband phase readout r_ij is formed by dividing the
# heterodyne-frequency phase by nu_m.  Additive noise that
# enters at frequency f_het therefore appears in r_ij scaled
# by f_het / nu_m  (from the LISA metrology chain, Barke PhD thesis).
# RIN-to-phase coupling coefficients from Wissel are already
# expressed as phase noise of the beatnote and carry the same scaling.
# ─────────────────────────────────────────────
freq_scaling = f_het / nu_m

sp_shot    *= freq_scaling
sp_dark    *= freq_scaling
sp_thermal *= freq_scaling
sp_amp     *= freq_scaling
sp_RIN1f   *= freq_scaling
sp_RIN2f   *= freq_scaling

# Modulation/clock noise [rad/sqrt(Hz)]
sp_mod  = 2 * np.pi * (f_het + nu_m) * sqrt_S_M
sp_USO  = 2 * np.pi * f_het * sqrt_S_USO

# ─────────────────────────────────────────────
# TOTALS
# ─────────────────────────────────────────────
sp_tot_ro = np.sqrt(sp_shot**2 + sp_dark**2 + sp_thermal**2 +
                    sp_amp**2 + sp_RIN1f**2 + sp_RIN2f**2)

sp_tot = np.sqrt(sp_tot_ro**2 + sp_mod**2)   # + sp_USO**2 if desired

# ─────────────────────────────────────────────
# SUMMARY PRINT
print_formula_summary()
save_formula_page('outputs/miniLISA_formula_reference.png')
# ─────────────────────────────────────────────
f_ref = 1e-3
idx = np.argmin(np.abs(f - f_ref))
print(f"\nPhase noise ASDs at f = {f_ref*1e3:.0f} mHz  [rad/sqrt(Hz)]:")
print(f"  (freq_scaling = f_het/nu_m = {freq_scaling:.2e})")
for name, arr in [
    ('Shot',       sp_shot),
    ('Dark',       sp_dark),
    ('Thermal',    sp_thermal),
    ('Amp',        sp_amp),
    ('1f-RIN',     sp_RIN1f),
    ('2f-RIN',     sp_RIN2f),
    ('Mod noise',  sp_mod),
    ('USO',        sp_USO),
    ('Total (RO)', sp_tot_ro),
    ('Total',      sp_tot),
]:
    print(f"  {name:<14} {arr[idx]:.2e}")

# ─────────────────────────────────────────────
# DISPLACEMENT NOISE
# x = phi * lambda / (4*pi)   round-trip → one-way = lambda/(4pi) ? 
# Or for one-way: x = phi * lambda / (2*pi)
# We use one-way: x = phi * lam / (2*pi)
# ─────────────────────────────────────────────
phase_to_disp = lam / (2 * np.pi)

sd_shot    = sp_shot    * phase_to_disp
sd_dark    = sp_dark    * phase_to_disp
sd_thermal = sp_thermal * phase_to_disp
sd_amp     = sp_amp     * phase_to_disp
sd_RIN1f   = sp_RIN1f   * phase_to_disp
sd_RIN2f   = sp_RIN2f   * phase_to_disp
sd_mod     = sp_mod     * phase_to_disp
sd_tot_ro  = sp_tot_ro  * phase_to_disp
sd_tot     = sp_tot     * phase_to_disp
sd_ro      = sqrt_S_ro  * phase_to_disp

# ─────────────────────────────────────────────
# PLOT
# ─────────────────────────────────────────────
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
fig, ax = plt.subplots(figsize=(10, 6))

pd_model = getattr(cfg.instrument, 'PD_model', 'unknown PD')
fig.suptitle('miniLISA Sideband Readout Noise Budget', fontsize=14, fontweight='bold')
ax.set_title(f'Photodetector: {pd_model}', fontsize=10, color='dimgrey')

ax.loglog(f, sp_shot,    label='Shot noise',     color=colors[0])
ax.loglog(f, sp_dark,    label='Dark noise',     color=colors[1])
ax.loglog(f, sp_thermal, label='Thermal noise',  color=colors[2], linestyle='--')
ax.loglog(f, sp_amp,     label='Amp noise',      color=colors[3])
ax.loglog(f, sp_RIN1f,   label='1f-RIN', color=colors[4])
ax.loglog(f, sp_RIN2f,   label='2f-RIN', color=colors[5])
ax.loglog(f, sp_tot_ro,  color='grey', lw=2, alpha=0.7, label='Total readout noise')
ax.loglog(f, sqrt_S_ro,  'k--', lw=2, label='LISA readout limit (scaled)')

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
print(f"\nPlot saved to {outpath}")