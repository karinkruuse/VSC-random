"""
Sideband readout noise budget
Plots all noise contributions:
  (i)  in natural units (V/sqrt(Hz) for additive noises, s/sqrt(Hz) for timing noises)
  (ii) once converted to phase noise (rad/sqrt(Hz))

Based on the signal chain model in miniLISA_Transferfunctions.pdf.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import j0, j1
from pathlib import Path
from config_loader import load_config
cfg = load_config(Path(__file__).parent / "lisa_config.toml")

# ─────────────────────────────────────────────
# Parameters  (from lisa_config.toml)
# ─────────────────────────────────────────────
# Optical / interferometer
E_ij   = np.sqrt(cfg.instrument.P_local)   # local E-field amplitude  [sqrt(W)]
E_ji   = np.sqrt(cfg.instrument.P_remote)  # remote E-field amplitude [sqrt(W)]

m      = cfg.instrument.m    # EOM modulation depth
R      = cfg.instrument.R    # photodiode responsivity [A/W]
eta    = cfg.instrument.eta  # heterodyne efficiency

# Frequencies
f_het  = cfg.beatnote.f_het    # heterodyne beatnote freq [Hz]
nu_m   = cfg.modulation.nu_m   # EOM modulation frequency [Hz]

# Photodetector transimpedance amplifier
C_pd = cfg.instrument.C_pd
Z = 1/(2*np.pi*C_pd*f_het)  # [V/A]

# Noise floors
I_dark    = 1e-12     # dark current ASD             [A/sqrt(Hz)]
S_amp     = 2e-9      # amplifier voltage noise ASD  [V/sqrt(Hz)]
RIN_level = 1e-8      # laser RIN ASD                [1/sqrt(Hz)]

# Modulation noise: sqrt(S_M(f)) = S_M0 * sqrt(1 + (f_corner/f)^2)
# (Hartwig thesis appendix)
S_M0       = 1e-14    # floor                        [s/sqrt(Hz)]
f_corner_M = 1.5e-2   # corner frequency             [Hz]

# USO clock noise: sqrt(S_q(f)) = S_q0 * f^{-3/2}
S_q0 = 1e-14          # USO timing noise coefficient [s/sqrt(Hz) at 1 Hz]

# Frequency axis (science band)
f = np.logspace(np.log10(cfg.science_band.f_science_min),
                np.log10(cfg.science_band.f_science_max), 2000)

# ─────────────────────────────────────────────
# Bessel function amplitudes
# ─────────────────────────────────────────────
J0m = j0(m)
J1m = j1(m)

# Sideband beatnote signal amplitude [V]
A_sb = 2 * R * Z * eta * E_ij * E_ji * J1m**2

# DC photocurrent for shot noise
I_DC = R * (E_ij**2 + E_ji**2)

print("Signal amplitudes:")
print(f"  A_carrier = {2*R*Z*eta*E_ij*E_ji*J0m**2:.3e} V")
print(f"  A_SB      = {A_sb:.3e} V  (J1^2/J0^2 = {J1m**2/J0m**2:.4f})")

# ─────────────────────────────────────────────
# Noise ASDs in natural (pre-PM) units
# ─────────────────────────────────────────────
e = 1.602e-19  # electron charge [C]

# Shot noise [V/sqrt(Hz)]
sqrt_S_shot = np.sqrt(2 * e * I_DC) * Z * np.ones_like(f)

# Dark noise [V/sqrt(Hz)]
sqrt_S_dark = I_dark * Z * np.ones_like(f)

# Amplifier noise [V/sqrt(Hz)]
sqrt_S_amp_v = S_amp * np.ones_like(f)

# 1f-RIN: additive voltage noise around f_het [V/sqrt(Hz)]
sqrt_S_RIN1f = np.ones_like(f) * R * Z *RIN_level * np.sqrt(E_ij**4 + E_ji**4)

# 2f-RIN: AM of sideband beatnote, couples at 2*f_het [V/sqrt(Hz)]
sqrt_S_RIN2f = RIN_level * np.sqrt(2) / 4 * np.ones_like(f)

# Modulation noise [s/sqrt(Hz)]
sqrt_S_M = S_M0 * np.sqrt(1 + (f_corner_M / f)**2)
sqrt_S_ro = 600/2/np.pi*1e-6 * np.sqrt(1+(0.7e-3/f)**4)

# USO clock noise [s/sqrt(Hz)]
sqrt_S_USO = S_q0 * f**(-3/2)

# ─────────────────────────────────────────────
# Convert to phase noise [rad/sqrt(Hz)]
#
# Additive voltage noises: phi_tilde = sqrt(2) * sqrt(S_n) / A_sb
#   (sqrt(2) from folding noise at +/- f_het, eq.3 in signal chain doc)
# Timing noises: phi = 2*pi*nu_m * timing_ASD
# ─────────────────────────────────────────────
def additive_to_phase(sqrt_S_V, A):
    return np.sqrt(2) * sqrt_S_V / A

freq_scaling = f_het / nu_m

sp_shot  = additive_to_phase(sqrt_S_shot,  A_sb) * freq_scaling
sp_dark  = additive_to_phase(sqrt_S_dark,  A_sb) * freq_scaling
sp_amp   = additive_to_phase(sqrt_S_amp_v, A_sb) * freq_scaling
sp_RIN1f = additive_to_phase(sqrt_S_RIN1f, A_sb) * freq_scaling
sp_RIN2f = sqrt_S_RIN2f * freq_scaling
sp_mod   = 2 * np.pi * nu_m * sqrt_S_M
sp_USO   = 2 * np.pi * f_het * sqrt_S_USO

# Total RSS
sp_tot = np.sqrt(sp_shot**2 + sp_dark**2 + sp_amp**2 +
                 sp_RIN1f**2 + sp_RIN2f**2 + sp_mod**2 ) #+ sp_USO**2

sp_tot_ro = np.sqrt(sp_shot**2 + sp_dark**2 + sp_amp**2 +
                 sp_RIN1f**2 + sp_RIN2f**2)

# ─────────────────────────────────────────────
# Print summary at 1 mHz
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
# Convert phase noise to displacement noise
# x = phi * lambda / (2*pi)   [m/sqrt(Hz)]
# ─────────────────────────────────────────────
lam = 1064e-9  # wavelength [m]
phase_to_disp = lam / (2 * np.pi)

sd_shot  = sp_shot  * phase_to_disp
sd_dark  = sp_dark  * phase_to_disp
sd_amp   = sp_amp   * phase_to_disp
sd_RIN1f = sp_RIN1f * phase_to_disp
sd_RIN2f = sp_RIN2f * phase_to_disp
sd_mod   = sp_mod   * phase_to_disp
sd_USO   = sp_USO   * phase_to_disp
sd_tot   = sp_tot   * phase_to_disp
sd_tot_ro   = sp_tot_ro   * phase_to_disp
sd_ro =  sqrt_S_ro * phase_to_disp

# ─────────────────────────────────────────────
# Plotting
# ─────────────────────────────────────────────
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
fig, ax = plt.subplots(figsize=(10, 6))
fig.suptitle('Sideband Readout Noise Budget', fontsize=14, fontweight='bold')

ax.loglog(f, sp_shot,  label='Shot noise',       color=colors[0])
ax.loglog(f, sp_dark,  label='Dark noise',       color=colors[1])
ax.loglog(f, sp_amp,   label='Amp noise',        color=colors[2])
ax.loglog(f, sp_RIN1f, label='1f-RIN',           color=colors[3])
ax.loglog(f, sp_RIN2f, label='2f-RIN',           color=colors[4])
ax.loglog(f, sp_mod,   label='Modulation noise', color=colors[5])
ax.loglog(f, sp_USO,   label='USO noise',        color=colors[6])
ax.loglog(f, sp_tot_ro,label='Total readout noise', color='grey', lw=2, alpha=0.7)
ax.loglog(f, sqrt_S_ro,   'k--', lw=2, label='readout limit')
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
plt.savefig('outputs/sideband_noise_budget.png', dpi=150, bbox_inches='tight')
print("Plot saved to outputs/sideband_noise_budget.png")
