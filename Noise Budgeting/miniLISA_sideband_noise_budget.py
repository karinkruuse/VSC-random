"""
miniLISA Sideband Readout Noise Budget
Plots all noise contributions:
  (i)   in natural units (V/sqrt(Hz) for additive noises, s/sqrt(Hz) for timing noises)
  (ii)  converted to phase noise (rad/sqrt(Hz))
  (iii) converted to displacement noise (m/sqrt(Hz))

Key differences from LISA:
  - Local laser beats against unmodulated reference oscillator beam
    => A_sb = 2*R*Z*eta * E_i * E_REF * J1(m)   [single J1, not J1^2]
  - Lower modulation frequency (~11 MHz vs 2.4 GHz)
    => freq_scaling = f_het / nu_m is much less favourable
  - No balanced detection => 1f-RIN not suppressed
  - Each readout noise appears twice (once per spacecraft PD), uncorrelated
    => multiply single-PD phase noise by sqrt(2)
  - RIN: contributions from laser_i, laser_j, and 2x ref laser
    => laser_i and laser_j: independent, RSS normally
    => ref laser: appears in both readouts, adds coherently (factor 2 in amplitude)
  - Independent USOs on each spacecraft => USO noise enters as in LISA

Based on miniLISA_Transferfunctions.pdf, section 2.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import j0, j1

# ─────────────────────────────────────────────
# Parameters  (edit here)
# ─────────────────────────────────────────────
# Optical powers
P_i   = 4e-3     # SC laser power at PD         [W]
P_REF = 4e-3     # reference laser power at PD  [W]  (placeholder, set as needed)

E_i   = np.sqrt(P_i)
E_REF = np.sqrt(P_REF)

m      = 0.53        # EOM modulation depth
R      = 0.69        # photodiode responsivity       [A/W]
eta    = 0.8         # heterodyne efficiency

# Frequencies
f_het  = 10e6        # heterodyne beatnote freq      [Hz]  (SC laser - REF)
nu_m   = 11e6        # EOM modulation frequency      [Hz]

# Photodetector transimpedance
C_pd = 10e-12
Z = 1 / (2 * np.pi * C_pd * f_het)   # [V/A]

# Noise floors
I_dark    = 1e-12    # dark current ASD              [A/sqrt(Hz)]
S_amp     = 2e-9     # amplifier voltage noise ASD   [V/sqrt(Hz)]
RIN_level = 1e-8     # laser RIN ASD (all lasers)    [1/sqrt(Hz)]

# Modulation noise: sqrt(S_M(f)) = S_M0 * sqrt(1 + (f_corner/f)^2)
S_M0       = 1e-14   # floor                         [s/sqrt(Hz)]
f_corner_M = 1.5e-2  # corner frequency              [Hz]

# USO clock noise: sqrt(S_q(f)) = S_q0 * f^{-3/2}
S_q0 = 1e-14         # USO timing noise coefficient  [s/sqrt(Hz) at 1 Hz]

# Wavelength
lam = 1064e-9        # [m]

# Frequency axis
f = np.logspace(-4, 1, 2000)   # 0.1 mHz to 10 Hz

# ─────────────────────────────────────────────
# Bessel factors
# ─────────────────────────────────────────────
J0m = j0(m)
J1m = j1(m)

# ─────────────────────────────────────────────
# Signal amplitude
# REF beam is unmodulated => only one J1 factor
# A_sb = 2 * R * Z * eta * E_i * E_REF * J1(m)
# ─────────────────────────────────────────────
A_sb = 2 * R * Z * eta * E_i * E_REF * J1m

# DC photocurrent (total power on PD, for shot noise)
I_DC = R * (E_i**2 + E_REF**2)

print("miniLISA signal amplitudes:")
print(f"  A_carrier = {2*R*Z*eta*E_i*E_REF*J0m:.3e} V   [single J0]")
print(f"  A_SB      = {A_sb:.3e} V   [single J1, J1/J0 = {J1m/J0m:.4f}]")
print(f"  Z         = {Z:.1f} Ohm")
print(f"  I_DC      = {I_DC*1e3:.3f} mA")

# ─────────────────────────────────────────────
# Single-PD noise ASDs in natural units
# ─────────────────────────────────────────────
e = 1.602e-19

# Shot noise [V/sqrt(Hz)]
sqrt_S_shot = np.sqrt(2 * e * I_DC) * Z * np.ones_like(f)

# Dark noise [V/sqrt(Hz)]
sqrt_S_dark = I_dark * Z * np.ones_like(f)

# Amplifier noise [V/sqrt(Hz)]
sqrt_S_amp_v = S_amp * np.ones_like(f)

# 1f-RIN: from SC laser and REF laser, uncorrelated [V/sqrt(Hz)]
# Single PD sees RIN_i and RIN_REF
sqrt_S_RIN1f_single = R * Z * RIN_level * np.sqrt(E_i**4 + E_REF**4) * np.ones_like(f)

# 2f-RIN: already a phase noise [rad/sqrt(Hz)] (single PD, two uncorrelated beams)
sqrt_S_RIN2f_single = RIN_level * np.sqrt(2) / 4 * np.ones_like(f)

# Modulation noise [s/sqrt(Hz)]
sqrt_S_M = S_M0 * np.sqrt(1 + (f_corner_M / f)**2)

# USO clock noise [s/sqrt(Hz)]
sqrt_S_USO = S_q0 * f**(-3/2)

# ─────────────────────────────────────────────
# Doubling factors for two-PD readout
#
# Shot, dark, amp: each PD independent => sqrt(2) in amplitude
#
# 1f-RIN: SC laser i appears only in PD i (factor sqrt(2) from two independent SC lasers
#         already in sqrt_S_RIN1f_single if E_i == E_j).
#         REF laser appears in BOTH PDs => adds coherently => factor 2 in amplitude.
#         Here we treat the two SC lasers as independent and the ref as correlated:
#         total = sqrt( (RZ*RIN*E_i^2)^2 + (RZ*RIN*E_j^2)^2 + (2*RZ*RIN*E_REF^2)^2 ) / A_sb
#         For simplicity with E_i = E_j = E_REF we keep the explicit expression below.
#
# 2f-RIN: same logic, ref laser correlated => handled via factor below
#
# Mod noise: two independent EOMs => sqrt(2)
# USO: two independent USOs => sqrt(2)  (differential, as in LISA)
# ─────────────────────────────────────────────

# 1f-RIN total across both readouts [V/sqrt(Hz)]
# SC laser i, SC laser j independent; REF coherent (factor 2)
sqrt_S_RIN1f = R * Z * RIN_level * np.sqrt(E_i**4 + E_i**4 + (2*E_REF**2)**2) * np.ones_like(f)
# = R*Z*RIN * sqrt(2*E_i^4 + 4*E_REF^4)

# 2f-RIN total [rad/sqrt(Hz)]: two SC lasers independent, REF coherent
# single-PD 2f-RIN ~ RIN/2sqrt(2) per beam pair; REF appears twice coherently
sqrt_S_RIN2f = RIN_level / (2 * np.sqrt(2)) * np.sqrt(2 + 4) * np.ones_like(f)
# = RIN * sqrt(6) / (2*sqrt(2))

# ─────────────────────────────────────────────
# Convert to phase noise [rad/sqrt(Hz)]
# Additive: phi = sqrt(2) * sqrt(S_n) / A_sb  then * freq_scaling
# Timing:   phi = 2*pi*nu_m * timing_ASD      (nu_m cancels with 1/nu_m in r_ij)
# ─────────────────────────────────────────────
def additive_to_phase(sqrt_S_V, A):
    return np.sqrt(2) * sqrt_S_V / A

freq_scaling = f_het / nu_m

# Additive noises: sqrt(2) doubling for two independent PDs
sp_shot  = additive_to_phase(sqrt_S_shot,   A_sb) * freq_scaling * np.sqrt(2)
sp_dark  = additive_to_phase(sqrt_S_dark,   A_sb) * freq_scaling * np.sqrt(2)
sp_amp   = additive_to_phase(sqrt_S_amp_v,  A_sb) * freq_scaling * np.sqrt(2)
sp_RIN1f = additive_to_phase(sqrt_S_RIN1f,  A_sb) * freq_scaling   # doubling already in sqrt_S_RIN1f
sp_RIN2f = sqrt_S_RIN2f * freq_scaling                              # doubling already in sqrt_S_RIN2f
sp_mod   = 2 * np.pi * nu_m * sqrt_S_M * np.sqrt(2)   # two independent EOMs
sp_USO   = 2 * np.pi * nu_m * sqrt_S_USO * np.sqrt(2) # two independent USOs

# Totals
sp_tot = np.sqrt(sp_shot**2 + sp_dark**2 + sp_amp**2 +
                 sp_RIN1f**2 + sp_RIN2f**2 + sp_mod**2) #  + sp_USO**2

sp_tot_ro = np.sqrt(sp_shot**2 + sp_dark**2 + sp_amp**2 +
                    sp_RIN1f**2 + sp_RIN2f**2)

# ─────────────────────────────────────────────
# Print summary
# ─────────────────────────────────────────────
f_ref = 1e-3
idx = np.argmin(np.abs(f - f_ref))
print(f"\nPhase noise ASDs at f = {f_ref*1e3:.0f} mHz [rad/sqrt(Hz)]:")
for name, arr in [
    ('Shot',      sp_shot),
    ('Dark',      sp_dark),
    ('Amp',       sp_amp),
    ('1f-RIN',    sp_RIN1f),
    ('2f-RIN',    sp_RIN2f),
    ('Mod noise', sp_mod),
    ('USO',       sp_USO),
    ('Total',     sp_tot),
    ('Readout',   sp_tot_ro),
]:
    print(f"  {name:<12} {arr[idx]:.2e}")

# ─────────────────────────────────────────────
# Displacement noise
# x = phi * lambda / (2*pi)   one-way measurement
# ─────────────────────────────────────────────
phase_to_disp = lam / (2 * np.pi)

sd_shot   = sp_shot   * phase_to_disp
sd_dark   = sp_dark   * phase_to_disp
sd_amp    = sp_amp    * phase_to_disp
sd_RIN1f  = sp_RIN1f  * phase_to_disp
sd_RIN2f  = sp_RIN2f  * phase_to_disp
sd_mod    = sp_mod    * phase_to_disp
sd_USO    = sp_USO    * phase_to_disp
sd_tot    = sp_tot    * phase_to_disp
sd_tot_ro = sp_tot_ro * phase_to_disp

# ─────────────────────────────────────────────
# Plotting
# ─────────────────────────────────────────────
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('miniLISA Sideband Readout Noise Budget', fontsize=14, fontweight='bold')

# ── Left: natural units ──────────────────────
ax = axes[0]
ax.loglog(f, sqrt_S_shot,    label='Shot noise', color=colors[0])
ax.loglog(f, sqrt_S_dark,    label='Dark noise', color=colors[1])
ax.loglog(f, sqrt_S_amp_v,   label='Amp noise',  color=colors[2])
ax.loglog(f, sqrt_S_RIN1f,   label='1f-RIN',     color=colors[3])
ax.loglog(f, sqrt_S_RIN2f,   label='2f-RIN',     color=colors[4])
ax2 = ax.twinx()
ax2.loglog(f, sqrt_S_M,   '--', label='Mod noise [s/√Hz]', color=colors[5])
ax2.loglog(f, sqrt_S_USO, '--', label='USO [s/√Hz]',       color=colors[6])
ax2.set_ylabel('Timing noise ASD [s/√Hz]', color='grey')
ax2.tick_params(axis='y', labelcolor='grey')
ax2.legend(loc='lower left', fontsize=9)
ax.set_xlabel('Fourier frequency [Hz]')
ax.set_ylabel('Voltage noise ASD [V/√Hz]')
ax.set_title('Natural units (single PD)')
ax.legend(loc='upper right', fontsize=9)
ax.grid(True, which='both', alpha=0.3)
ax.set_xlim(f[0], f[-1])

# ── Right: phase noise ───────────────────────
ax = axes[1]
ax.loglog(f, sp_shot,    label='Shot noise',        color=colors[0])
ax.loglog(f, sp_dark,    label='Dark noise',        color=colors[1])
ax.loglog(f, sp_amp,     label='Amp noise',         color=colors[2])
ax.loglog(f, sp_RIN1f,   label='1f-RIN',            color=colors[3])
ax.loglog(f, sp_RIN2f,   label='2f-RIN',            color=colors[4])
ax.loglog(f, sp_mod,     label='Modulation noise',  color=colors[5])
ax.loglog(f, sp_USO,     label='USO noise',         color=colors[6])
ax.loglog(f, sp_tot_ro,  color='grey', lw=2, alpha=0.7, label='Total readout noise')
ax.loglog(f, sp_tot,     'k--', lw=2, label='Total (RSS)')
ax.set_xlabel('Fourier frequency [Hz]')
ax.set_ylabel('Phase noise ASD [rad/√Hz]')
ax.set_title('Converted to phase noise (both PDs)')
ax.legend(fontsize=9)
ax.grid(True, which='both', alpha=0.3)
ax.set_xlim(f[0], f[-1])

plt.tight_layout()
plt.savefig('outputs/miniLISA_sideband_noise_budget.png', dpi=150, bbox_inches='tight')

# ── Displacement noise ───────────────────────
fig2, ax = plt.subplots(figsize=(8, 6))
ax.loglog(f, sd_shot,    label='Shot noise',        color=colors[0])
ax.loglog(f, sd_dark,    label='Dark noise',        color=colors[1])
ax.loglog(f, sd_amp,     label='Amp noise',         color=colors[2])
ax.loglog(f, sd_RIN1f,   label='1f-RIN',            color=colors[3])
ax.loglog(f, sd_RIN2f,   label='2f-RIN',            color=colors[4])
ax.loglog(f, sd_mod,     label='Modulation noise',  color=colors[5])
ax.loglog(f, sd_USO,     label='USO noise',         color=colors[6])
ax.loglog(f, sd_tot_ro,  color='grey', lw=3, alpha=0.7, label='Total readout noise')
ax.loglog(f, sd_tot,     'k--', lw=2, label='Total (RSS)')
ax.set_xlabel('Fourier frequency [Hz]')
ax.set_ylabel('Displacement noise ASD [m/√Hz]')
ax.set_title(f'Displacement noise  (λ = {lam*1e9:.0f} nm,  x = φ·λ/2π)')
ax.legend(fontsize=9)
ax.grid(True, which='both', alpha=0.3)
ax.set_xlim(f[0], f[-1])
fig2.tight_layout()
fig2.savefig('outputs/miniLISA_sideband_noise_budget_displacement.png', dpi=150, bbox_inches='tight')
print("Plots saved.")
