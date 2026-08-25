import numpy as np
import matplotlib.pyplot as plt
import scipy.special as sp
from scipy.constants import elementary_charge as e, Boltzmann as kB

# ── Common ────────────────────────────────────────────────────────────────────
het_eff = 0.9
m       = 0.53
bw_eff  = (np.pi / 2) * 100e3
RIN     = 0.9e-8


def compute(P_m, P_r, Res, *, het_eff=0.9, m=0.53, T=300, RIN=0.9e-8,
                 NEP=None, R_term=None, e_LNA=0.0,          # electronic: NEP xor (R_term[+e_LNA])
                 I_dark=0.0,                                # bare diode only; 0 when NEP given
                 G_total=None, adc_FSR=1, adc_bits=14, adc_fs=2e9,  # ADC (optional)
                 balanced=False, CMRR=1.0):
    P_m, P_r = map(np.asarray, (P_m, P_r))
    i_sig = Res*sp.j1(m)*np.sqrt(het_eff*P_m*P_r)          # per-port sideband beat
    shot  = np.sqrt(2*e*(Res*(P_m+P_r) + I_dark))          # dark folded in
    elec  = (NEP*Res if NEP is not None
             else np.sqrt(4*kB*T/R_term + (e_LNA/R_term)**2)) * np.ones_like(P_m)
    rin   = Res*(P_m+P_r)*RIN

    adc   = (((adc_FSR/2**adc_bits)/np.sqrt(12)/np.sqrt(adc_fs/2))/G_total
             if G_total is not None else 0.0) * np.ones_like(P_m)

    f = np.sqrt(2) if balanced else 1.0                    # uncorrelated: √2 improvement
    ph_shot   = shot / i_sig / f / (2*np.pi)
    ph_elec   = elec / i_sig / f / (2*np.pi)
    ph_adc    = adc  / i_sig / f / (2*np.pi)
    ph_rin    = rin  / i_sig / (CMRR if balanced else 1.0) / (2*np.pi)
    ph_total  = np.sqrt(ph_shot**2 + ph_elec**2 + ph_rin**2 + ph_adc**2)
    return ph_shot, ph_elec, ph_rin, ph_adc,  ph_total

# ── Detector definitions ──────────────────────────────────────────────────────

# I_dark = 100 nA (datasheet max) — bare diode, dark shot noise is a real,
# separate term here. Do NOT add I_dark for FEMTO/Menlo/Thorlabs: their NEP is
# the total input-referred electronic floor (dark + thermal + amplifier)

newport_P   = np.linspace(10e-6, 10e-3, 500)  
newport     = compute(newport_P, newport_P, Res=0.6, R_term=50,
                       I_dark=100e-9, G_total=50)

newport_elec_label = 'Johnson (50Ω)'
newport_unit = 1e3 

# FEMTO HBPR-100M-60K-IN-FC: balanced, ×4 gain.
# P_sat_dc (28 µW/beam) is the DC/differential-power TIA limit and only applies
# if DC-coupled. AC-coupling removes that constraint, letting the FEMTO run up
# to ~450 µW/beam — the "optimal" budget must use that ceiling, not 28 µW,
# or the FEMTO is handicapped to its worst (DC-coupled) operating mode.
femto_P_sat_dc = 53e-6 / (2 * np.sqrt(het_eff))       # ~28 µW/beam, DC-coupled ref. only
femto_P_sat_ac = 16 * femto_P_sat_dc                  # ~450 µW/beam, AC-coupled ceiling (used below)
femto_P     = np.linspace(1e-6, femto_P_sat_ac, 500)
femto       = compute(femto_P, femto_P, Res=0.65, NEP=6e-12, CMRR=10**(55/20), balanced=True,
                       G_total=60e3)
femto_elec_label = 'NEP (6 pW/√Hz)'
femto_unit  = 1e6   # plot in µW

# Thorlabs: balanced.
# trusting the NEP/CMRR/sat numbers below.
thor_P_sat  = 15e-6 / (2 * np.sqrt(het_eff))
thor_P      = np.linspace(1e-6, thor_P_sat, 500)
thor        = compute(thor_P, thor_P, Res=0.65, NEP=5.2e-12, CMRR=10**(35/20), balanced=True,
                       G_total=50e3)
thor_elec_label = 'NEP (5.2 pW/√Hz)'
thor_unit   = 1e6

# Menlo FPD510-FC-NIR: single-ended.
menlo_P_sat = 50e-6
menlo_P     = np.linspace(1e-6, menlo_P_sat, 500)
menlo       = compute(menlo_P, menlo_P, Res=0.65, NEP=3.0e-12, balanced=False,
                       G_total=15e4)
menlo_elec_label = 'NEP (3 pW/√Hz)'
menlo_unit  = 1e6

detectors = [
    dict(name='Newport\n(single-ended)',           P=newport_P, data=newport,
         color='tab:purple', P_sat=None,  unit=newport_unit, xunit='mW',
         elec_label=newport_elec_label,
         balanced=False),
    dict(name='FEMTO HBPR-100M\n(bal., CMRR=55dB)', P=femto_P,   data=femto,
         color='tab:blue',   P_sat=femto_P_sat_ac, P_sat_dc=femto_P_sat_dc,
         sat_label='AC-coupled ceiling',
         unit=femto_unit,   xunit='µW',
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
    'Photodetector phase noise comparison  |  PLL BW = 100 kHz  |  RIN = 0.9×10⁻⁸ /√Hz  |  Responsivity = 0.65 A/W',
    fontsize=11)


#vq      = (1.4 / 2**14) / np.sqrt(12) / np.sqrt(2*10e9/2)   # V/√Hz at ADC
#adc_asd = vq / G_total_VperA     # G_total = G_TI (amplified) OR R_term*G_LNA (Newport)


# ── Top-left: total noise all detectors ───────────────────────────────────────
ax_total = axes[0, 0]
for d in detectors:
    ph_total = d['data'][4]
    # normalise x-axis to µW for the total plot (Newport in mW → convert)
    P_uw = d['P'] * 1e6
    ax_total.plot(P_uw, ph_total * 1e6, color=d['color'], linewidth=2,
                  label=d['name'].replace('\n', ' '))
    if d['P_sat'] is not None:
        ax_total.axvline(d['P_sat'] * 1e6, color=d['color'],
                         linestyle=':', linewidth=1, alpha=0.7)

ax_total.set_xscale('log'); ax_total.set_yscale('log')
ax_total.set_xlabel('Power per beam (µW)')
ax_total.set_ylabel('Phase noise ASD (μcyc/√Hz)')
ax_total.set_title('Total phase noise — all detectors')
ax_total.legend(fontsize=8); ax_total.grid(True, which='both', alpha=0.3)

# ── Breakdown plots ───────────────────────────────────────────────────────────
breakdown_axes = [axes[0,1], axes[0,2], axes[1,1], axes[1,2]]

for ax, d in zip(breakdown_axes, detectors):
    P_x       = d['P'] * d['unit']   # scaled x axis
    ph_shot, ph_elec, ph_rin, ph_adc, ph_total = d['data']
    col = d['color']

    ax.plot(P_x, ph_shot   * 1e6, color=col, linestyle='-',  label='Shot noise')
    ax.plot(P_x, ph_elec   * 1e6, color=col, linestyle='--', label=d['elec_label'])
    ax.plot(P_x, ph_rin    * 1e6, color=col, linestyle=':',  label='RIN')
    ax.plot(P_x, ph_adc    * 1e6, color=col, linestyle='-.', label='ADC noise')
    ax.plot(P_x, ph_total  * 1e6, color='black', linestyle='-.', linewidth=1.5, label='Total')

    if d['P_sat'] is not None:
        sat_label = d.get('sat_label', 'Sat.')
        ax.axvline(d['P_sat'] * d['unit'], color='red', linestyle=':', linewidth=1,
                   label=f"{sat_label} ({d['P_sat']*1e6:.1f} µW/beam)")
    if d.get('P_sat_dc') is not None:
        ax.axvline(d['P_sat_dc'] * d['unit'], color='darkred', linestyle='--', linewidth=1,
                   label=f"DC-coupled ref. ({d['P_sat_dc']*1e6:.1f} µW/beam)")

    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel(f"Power per beam ({d['xunit']})")
    ax.set_ylabel('Phase noise ASD (μcyc/√Hz)')
    ax.set_title(d['name'])
    ax.legend(fontsize=8); ax.grid(True, which='both', alpha=0.3)

# ── Bottom-left: hide empty axis, use for notes ───────────────────────────────
axes[1, 0].axis('off')
notes = (
    "Notes\n"
    "─────────────────────────────────\n"
    "All detectors: responsivity = 0.65 A/W\n"
    "  (estimate for 1064 nm InGaAs/Si)\n\n"
    "Newport: single-ended, capped at 10 mW/\n"
    "  beam (30 mW abs-max). Dark current\n"
    "  (100 nA) folded into shot noise —\n"
    "  bare diode, not inside a NEP.\n"
    "  Elec. floor = Johnson (50Ω) only.\n"
    "  ADC term uses real digitizer spec\n"
    "  (1 Vpp, 14 bit, 122 MS/s).\n\n"
    "FEMTO: balanced (×4 gain), CMRR=55dB.\n"
    "  Red line = AC-coupled ceiling\n"
    "  (~450 µW/beam), the optimal operating\n"
    "  point. Dark red = DC-coupled TIA\n"
    "  diff.-power limit (28 µW/beam), shown\n"
    "  for reference only.\n\n"
    "Thorlabs: balanced, CMRR≥35dB. Part no.\n"
    "  needs reconciling (PDB425C vs PDB415C\n"
    "  — different BW/NEP, see TODO).\n\n"
    "Menlo: single-ended, no RIN cancellation.\n"
    "  Responsivity 0.65 A/W is an unverified\n"
    "  estimate — drives its shot term.\n\n"
    "FEMTO/Menlo/Thorlabs: I_dark = 0 always —\n"
    "  their NEP already includes dark-current\n"
    "  shot noise; adding it double-counts.\n\n"
    "Dashed/dotted vertical lines = sat./ceiling\n"
    "Balanced shot/NEP/ADC improvement = √2\n"
    "Balanced RIN suppression = CMRR"
)
axes[1, 0].text(0.05, 0.95, notes, transform=axes[1, 0].transAxes,
                fontsize=7.5, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.tight_layout()
plt.savefig('SNR_comparison.png', dpi=150, bbox_inches='tight')

# ── Optimal (at-ceiling) phase-noise budget, printed for hand-off/validation ──
# Radians (not the plot's cycles) to match the nrad/√Hz convention used when
# these numbers were reviewed: multiply the cycle-domain components by 2π.
print("\nOptimal (at-ceiling) phase noise budget  [nrad/sqrt(Hz)]")
header = f"{'Detector':<10} {'P/beam':>10} {'shot':>7} {'elec':>7} {'rin':>7} {'adc':>7}  {'total':>7}  limited by"
print(header)
print('-' * len(header))
for d in detectors:
    ph_shot, ph_elec, ph_rin, ph_adc, ph_total = d['data']
    i = -1   # ceiling point (end of sweep)
    comps = {'shot': ph_shot[i], 'elec': ph_elec[i], 'rin': ph_rin[i],
             'adc': ph_adc[i]}
    dominant = max(comps, key=comps.get)
    P_beam = d['P'][i]
    p_str = f"{P_beam*1e3:.2f} mW" if d['unit'] == 1e3 else f"{P_beam*1e6:.1f} uW"
    name1 = d['name'].split('\n')[0]
    rad = 2 * np.pi   # cycles -> radians
    print(f"{name1:<10} {p_str:>10} "
          f"{ph_shot[i]*rad*1e9:7.0f} {ph_elec[i]*rad*1e9:7.0f} {ph_rin[i]*rad*1e9:7.0f} "
          f"{ph_adc[i]*rad*1e9:7.0f} {ph_total[i]*rad*1e9:7.0f}  {dominant}")

plt.show()