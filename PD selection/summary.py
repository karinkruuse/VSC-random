import numpy as np
import matplotlib.pyplot as plt
import scipy.special as sp
from scipy.constants import elementary_charge as e, Boltzmann as kB

# ── Common ────────────────────────────────────────────────────────────────────
het_eff = 0.9
m       = 0.53
bw_eff  = (np.pi / 2) * 100e3
RIN     = 1e-8

def compute(P_m, Res, NEP=None, CMRR=None, R_johnson=None):
    """Compute phase noise ASDs.
    NEP      : use NEP-based electronic noise (pW/√Hz)
    R_johnson: use Johnson noise from resistor R [Ω] instead
    CMRR     : balanced detection factor (linear). None = single-ended.
    """
    P_r   = P_m
    i_sig = Res * sp.j1(m) * np.sqrt(het_eff * P_m * P_r)

    # shot
    shot_asd = np.sqrt(2 * e * Res * (P_m + P_r))

    # electronic noise
    if NEP is not None:
        elec_asd = NEP * Res
    else:
        elec_asd = np.sqrt(4 * kB * 300 / R_johnson) * np.ones_like(P_m)

    # RIN
    rin_asd = Res * (P_m + P_r) * RIN

    if CMRR is None:   # single-ended
        ph_shot = shot_asd / i_sig
        ph_elec = elec_asd / i_sig
        ph_rin  = rin_asd  / i_sig
    else:              # balanced
        ph_shot = shot_asd / i_sig / np.sqrt(2)
        ph_elec = elec_asd / i_sig / np.sqrt(2)
        ph_rin  = rin_asd  / i_sig / CMRR

    ph_total = np.sqrt(ph_shot**2 + ph_elec**2 + ph_rin**2)
    return ph_shot, ph_elec, ph_rin, ph_total

# ── Detector definitions ──────────────────────────────────────────────────────
# Newport: single-ended, Johnson noise, no stated sat limit → show up to 20 mW
newport_P   = np.linspace(10e-6, 10e-3, 500)
newport     = compute(newport_P, Res=0.6, R_johnson=50)
newport_sat = None   # no saturation limit in datasheet
newport_elec_label = 'Johnson (50Ω)'
newport_unit = 1e3   # plot in mW

# FEMTO HBPR-100M-60K-IN-FC: balanced, ×4 gain
femto_P_sat = 53e-6 / (2 * np.sqrt(het_eff))
femto_P     = np.linspace(1e-6, femto_P_sat, 500)
femto       = compute(femto_P, Res=0.65, NEP=6e-12, CMRR=10**(55/20))
femto_elec_label = 'NEP (6 pW/√Hz)'
femto_unit  = 1e6   # plot in µW

# Thorlabs PDB425C: balanced
thor_P_sat  = 15e-6 / (2 * np.sqrt(het_eff))
thor_P      = np.linspace(1e-6, thor_P_sat, 500)
thor        = compute(thor_P, Res=0.65, NEP=5.2e-12, CMRR=10**(35/20))
thor_elec_label = 'NEP (5.2 pW/√Hz)'
thor_unit   = 1e6

# Menlo FPD510-FC-NIR: single-ended
menlo_P_sat = 50e-6
menlo_P     = np.linspace(1e-6, menlo_P_sat, 500)
menlo       = compute(menlo_P, Res=0.65, NEP=3.0e-12)
menlo_elec_label = 'NEP (3 pW/√Hz)'
menlo_unit  = 1e6

detectors = [
    dict(name='Newport\n(single-ended)',           P=newport_P, data=newport,
         color='tab:purple', P_sat=newport_sat,   unit=newport_unit, xunit='mW',
         elec_label=newport_elec_label,
         balanced=False),
    dict(name='FEMTO HBPR-100M\n(bal., CMRR=55dB)', P=femto_P,   data=femto,
         color='tab:blue',   P_sat=femto_P_sat,   unit=femto_unit,   xunit='µW',
         elec_label=femto_elec_label,
         balanced=True),
    dict(name='Thorlabs PDB425C\n(bal., CMRR≥35dB)', P=thor_P,  data=thor,
         color='tab:orange', P_sat=thor_P_sat,    unit=thor_unit,    xunit='µW',
         elec_label=thor_elec_label,
         balanced=True),
    dict(name='Menlo FPD510-FC-NIR\n(single-ended)', P=menlo_P, data=menlo,
         color='tab:green',  P_sat=menlo_P_sat,   unit=menlo_unit,   xunit='µW',
         elec_label=menlo_elec_label,
         balanced=False),
]

# ── Layout: 2 rows × 3 cols
# [0,0] total comparison  [0,1] Newport breakdown  [0,2] FEMTO breakdown
# [1,0] empty/legend      [1,1] Thorlabs breakdown [1,2] Menlo breakdown
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle(
    'Photodetector phase noise comparison  |  PLL BW = 100 kHz  |  RIN = 1×10⁻⁸ /√Hz  |  Responsivity = 0.65 A/W',
    fontsize=11)

# ── Top-left: total noise all detectors ───────────────────────────────────────
ax_total = axes[0, 0]
for d in detectors:
    ph_total = d['data'][3]
    # normalise x-axis to µW for the total plot (Newport in mW → convert)
    P_uw = d['P'] * 1e6
    ax_total.plot(P_uw, ph_total * 1e6, color=d['color'], linewidth=2,
                  label=d['name'].replace('\n', ' '))
    if d['P_sat'] is not None:
        ax_total.axvline(d['P_sat'] * 1e6, color=d['color'],
                         linestyle=':', linewidth=1, alpha=0.7)

ax_total.set_xscale('log'); ax_total.set_yscale('log')
ax_total.set_xlabel('Power per beam (µW)')
ax_total.set_ylabel('Phase noise ASD (μrad/√Hz)')
ax_total.set_title('Total phase noise — all detectors')
ax_total.legend(fontsize=8); ax_total.grid(True, which='both', alpha=0.3)

# ── Breakdown plots ───────────────────────────────────────────────────────────
breakdown_axes = [axes[0,1], axes[0,2], axes[1,1], axes[1,2]]

for ax, d in zip(breakdown_axes, detectors):
    P_x       = d['P'] * d['unit']   # scaled x axis
    ph_shot, ph_elec, ph_rin, ph_total = d['data']
    col = d['color']

    ax.plot(P_x, ph_shot  * 1e6, color=col, linestyle='-',  label='Shot noise')
    ax.plot(P_x, ph_elec  * 1e6, color=col, linestyle='--', label=d['elec_label'])
    ax.plot(P_x, ph_rin   * 1e6, color=col, linestyle=':',  label='RIN')
    ax.plot(P_x, ph_total * 1e6, color='black', linestyle='-.', linewidth=1.5, label='Total')

    if d['P_sat'] is not None:
        ax.axvline(d['P_sat'] * d['unit'], color='red', linestyle=':', linewidth=1,
                   label=f"Sat. ({d['P_sat']*1e6:.1f} µW/beam)")

    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel(f"Power per beam ({d['xunit']})")
    ax.set_ylabel('Phase noise ASD (μrad/√Hz)')
    ax.set_title(d['name'])
    ax.legend(fontsize=8); ax.grid(True, which='both', alpha=0.3)

# ── Bottom-left: hide empty axis, use for notes ───────────────────────────────
axes[1, 0].axis('off')
notes = (
    "Notes\n"
    "─────────────────────────────────\n"
    "All detectors: responsivity = 0.65 A/W\n"
    "  (estimate for 1064 nm InGaAs/Si)\n\n"
    "Newport: single-ended, no sat. limit\n"
    "  stated — shown up to 20 mW\n\n"
    "FEMTO: balanced (×4 gain), CMRR=55dB\n"
    "  sat. limited by TIA diff. power\n\n"
    "Thorlabs: balanced, CMRR≥35dB\n"
    "  sat. limited by CW sat. power\n\n"
    "Menlo: single-ended, no RIN cancellation\n"
    "  sat. = 100 µW total input\n\n"
    "Dashed vertical lines = sat. limits\n"
    "Balanced shot/NEP improvement = √2\n"
    "Balanced RIN suppression = CMRR"
)
axes[1, 0].text(0.05, 0.95, notes, transform=axes[1, 0].transAxes,
                fontsize=8.5, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.tight_layout()
plt.savefig('SNR_comparison.png', dpi=150, bbox_inches='tight')
plt.show()