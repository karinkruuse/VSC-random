import numpy as np
import matplotlib.pyplot as plt
import scipy.special as sp
from scipy.constants import elementary_charge as e

# ── Thorlabs PDB425C parameters (from datasheet) ──────────────────────────────
# TODO: part number mismatch — this uses PDB425C, but PDB415C was referenced
# elsewhere; the two differ in bandwidth/NEP. Confirm the correct part before
# trusting the NEP/CMRR/sat numbers below.
Res      = 0.65                   # responsivity [A/W] @ peak (InGaAs)
NEP      = 5.2e-12               # NEP [W/√Hz], DC to 75 MHz
CMRR_dB  = 35                    # CMRR minimum [dB]
CMRR     = 10**(CMRR_dB / 20)   # linear (~56)

het_eff  = 0.9                   # heterodyne efficiency
m        = 0.53                  # modulation depth

bw       = 100e3                 # PLL 3dB bandwidth [Hz]
bw_eff   = (np.pi / 2) * bw     # noise-equivalent BW, 1st order PLL [Hz]

# ── Saturation: CW saturation power = 15 µW (power *difference* into TIA) ────
# Beatnote peak differential power: P_diff = 2 * sqrt(η_het * P_m * P_r)
# Equal beams: P_diff = 2 * sqrt(η_het) * P_m
# Saturation when P_diff = P_diff_max:
#   P_m_max = P_diff_max / (2 * sqrt(η_het))
P_diff_max = 15e-6               # [W] CW saturation power @ 1550 nm
P_sat      = P_diff_max / (2 * np.sqrt(het_eff))   # ~7.9 µW per beam

# ── Power sweep ───────────────────────────────────────────────────────────────
P_m = np.linspace(1e-6, P_sat, 500)
P_r = P_m

i_sig_peak = Res * sp.j1(m) * np.sqrt(het_eff * P_m * P_r)

# ── Shot noise ────────────────────────────────────────────────────────────────
shot_asd         = np.sqrt(2 * e * Res * (P_m + P_r))
phase_shot_unbal = shot_asd / i_sig_peak
phase_shot_bal   = phase_shot_unbal / np.sqrt(2)
rms_shot_unbal   = phase_shot_unbal * np.sqrt(bw_eff)
rms_shot_bal     = phase_shot_bal   * np.sqrt(bw_eff)

# ── NEP ───────────────────────────────────────────────────────────────────────
nep_asd          = NEP * Res
phase_nep_unbal  = nep_asd / i_sig_peak
phase_nep_bal    = phase_nep_unbal / np.sqrt(2)
rms_nep_unbal    = phase_nep_unbal * np.sqrt(bw_eff)
rms_nep_bal      = phase_nep_bal   * np.sqrt(bw_eff)

# ── RIN ───────────────────────────────────────────────────────────────────────
RIN              = 1e-8
rin_asd          = Res * (P_m + P_r) * RIN
phase_rin_unbal  = rin_asd / i_sig_peak
phase_rin_bal    = phase_rin_unbal / CMRR
rms_rin_unbal    = phase_rin_unbal * np.sqrt(bw_eff)
rms_rin_bal      = phase_rin_bal   * np.sqrt(bw_eff)

# ── Total ─────────────────────────────────────────────────────────────────────
phase_total_unbal = np.sqrt(phase_shot_unbal**2 + phase_nep_unbal**2 + phase_rin_unbal**2)
phase_total_bal   = np.sqrt(phase_shot_bal**2   + phase_nep_bal**2   + phase_rin_bal**2)
rms_total_unbal   = phase_total_unbal * np.sqrt(bw_eff)
rms_total_bal     = phase_total_bal   * np.sqrt(bw_eff)

# ── Plotting ──────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Thorlabs PDB425C  |  Phase noise ASD  |  PLL BW = 100 kHz', fontsize=12)

colors = {'shot': 'tab:blue', 'nep': 'tab:orange', 'rin': 'tab:green', 'total': 'black'}

for ax, (phase_shot, phase_nep, phase_rin, phase_total, label) in zip(axes, [
    (phase_shot_unbal, phase_nep_unbal, phase_rin_unbal, phase_total_unbal, 'Unbalanced'),
    (phase_shot_bal,   phase_nep_bal,   phase_rin_bal,   phase_total_bal,
     f'Balanced (CMRR ≥ {CMRR_dB} dB)'),
]):
    ax.plot(P_m * 1e6, phase_shot  * 1e6, color=colors['shot'],  label='Shot noise')
    ax.plot(P_m * 1e6, phase_nep   * 1e6, color=colors['nep'],   label=f'NEP ({NEP*1e12:.1f} pW/√Hz)')
    ax.plot(P_m * 1e6, phase_rin   * 1e6, color=colors['rin'],   label=f'RIN ({RIN:.0e} /√Hz)')
    ax.plot(P_m * 1e6, phase_total * 1e6, color=colors['total'], label='Total', linestyle='--', linewidth=1.5)
    ax.axvline(P_sat * 1e6, color='red', linestyle=':', linewidth=1.2,
               label=f'TIA sat. ({P_sat*1e6:.1f} µW/beam)')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Power per beam $P_m$ (µW)')
    ax.set_ylabel('Phase noise ASD (μrad/√Hz)')
    ax.set_title(label)
    ax.legend(fontsize=8)
    ax.grid(True, which='both', alpha=0.3)

plt.tight_layout()
#plt.savefig('SNR_Thorlabs.png', dpi=150)
plt.show()