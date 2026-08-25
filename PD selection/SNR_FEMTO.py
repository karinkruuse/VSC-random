import numpy as np
import matplotlib.pyplot as plt
import scipy.special as sp
from scipy.constants import elementary_charge as e

# ── HBPR-100M-60K-IN-FC parameters (from datasheet) ──────────────────────────
Res      = 0.65                  # responsivity [A/W] @ 1064 nm
NEP      = 6e-12               # NEP [W/√Hz] @ 100 MHz (worst case in band)
CMRR_dB  = 55                    # common mode rejection ratio [dB]
CMRR     = 10**(CMRR_dB / 20)   # linear CMRR (~562)

het_eff  = 0.9                   # heterodyne efficiency η_het
m        = 0.53                  # modulation depth


# ── Saturation limit from TIA differential power (datasheet p.3) ──────────────
# Max differential CW power for linear operation: 53 µW (×4 gain)
# The heterodyne beatnote IS a differential signal with peak amplitude:
#   P_diff_peak = 2 * sqrt(η_het * P_m * P_r)
# For equal beams: P_diff_peak = 2 * sqrt(η_het) * P_m
# Saturation when P_diff_peak = P_diff_max:
#   P_m_max = P_diff_max / (2 * sqrt(η_het))
P_diff_max_x4  = 53e-6           # [W] max differential power, ×4 gain
P_diff_max_x12 = 18e-6           # [W] max differential power, ×12 gain

P_sat_x4  = P_diff_max_x4  / (2 * np.sqrt(het_eff))   # ~28 µW per beam
P_sat_x12 = P_diff_max_x12 / (2 * np.sqrt(het_eff))   # ~9.5 µW per beam

# Use ×4 gain (higher power, less restrictive)
P_max = P_sat_x4

# ── Power sweep up to saturation ──────────────────────────────────────────────
P_m = np.linspace(1e-6, P_max, 500)
P_r = P_m

i_sig_peak = Res * sp.j1(m) * np.sqrt(het_eff * P_m * P_r)

# ── RIN ───────────────────────────────────────────────────────────────────────
RIN = 1e-8

rin_asd          = Res * (P_m + P_r) * RIN
phase_rin_unbal  = rin_asd / i_sig_peak
phase_rin_bal    = phase_rin_unbal / CMRR

# ── Shot noise ────────────────────────────────────────────────────────────────
shot_asd         = np.sqrt(2 * e * Res * (P_m + P_r))
phase_shot_unbal = shot_asd / i_sig_peak
phase_shot_bal   = phase_shot_unbal / np.sqrt(2)

# ── NEP ───────────────────────────────────────────────────────────────────────
nep_asd          = NEP * Res
phase_nep_unbal  = nep_asd / i_sig_peak
phase_nep_bal    = phase_nep_unbal / np.sqrt(2)

# ── Total ─────────────────────────────────────────────────────────────────────
phase_total_unbal = np.sqrt(phase_shot_unbal**2 + phase_nep_unbal**2 + phase_rin_unbal**2)
phase_total_bal   = np.sqrt(phase_shot_bal**2   + phase_nep_bal**2   + phase_rin_bal**2)

# ── Plotting ──────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('HBPR-100M-60K-IN-FC  |  Phase noise ASD  |  PLL BW = 100 kHz', fontsize=12)

colors = {'shot': 'tab:blue', 'nep': 'tab:orange', 'rin': 'tab:green', 'total': 'black'}

for ax, (phase_shot, phase_nep, phase_rin, phase_total, label) in zip(axes, [
    (phase_shot_unbal, phase_nep_unbal, phase_rin_unbal, phase_total_unbal, 'Unbalanced'),
    (phase_shot_bal,   phase_nep_bal,   phase_rin_bal,   phase_total_bal,
     f'Balanced (CMRR = {CMRR_dB} dB)'),
]):
    ax.plot(P_m * 1e6, phase_shot  * 1e6, color=colors['shot'],  label='Shot noise')
    ax.plot(P_m * 1e6, phase_nep   * 1e6, color=colors['nep'],   label=f'NEP ({NEP*1e12:.1f} pW/√Hz)')
    ax.plot(P_m * 1e6, phase_rin   * 1e6, color=colors['rin'],   label=f'RIN ({RIN:.0e} /√Hz)')
    ax.plot(P_m * 1e6, phase_total * 1e6, color=colors['total'], label='Total', linestyle='--', linewidth=1.5)
    ax.axvline(P_sat_x4  * 1e6, color='red',    linestyle=':', linewidth=1.2,
               label=f'Sat. ×4 gain ({P_sat_x4*1e6:.1f} µW/beam)')
    ax.axvline(P_sat_x12 * 1e6, color='darkred', linestyle=':', linewidth=1.2,
               label=f'Sat. ×12 gain ({P_sat_x12*1e6:.1f} µW/beam)')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Power per beam $P_m$ (µW)')
    ax.set_ylabel('Phase noise ASD (μrad/√Hz)')
    ax.set_title(label)
    ax.legend(fontsize=8)
    ax.grid(True, which='both', alpha=0.3)

plt.tight_layout()
#plt.savefig('SNR_FEMTO.png', dpi=150)
plt.show()