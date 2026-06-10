import numpy as np
import matplotlib.pyplot as plt
import scipy.special as sp
from scipy.constants import elementary_charge as e

# ── Menlo FPD510-FC-NIR parameters (from datasheet) ──────────────────────────
# WARNING: Responsivity at 1064 nm not stated in datasheet — using ~0.8 A/W
# from typical InGaAs curve. Verify this value for your wavelength!
Res  = 0.65                       # responsivity [A/W] @ 1064 nm (estimate!)
NEP  = 3.0e-12                   # NEP [W/√Hz] (calculated, from datasheet)

het_eff = 0.9                    # heterodyne efficiency
m       = 0.53                   # modulation depth

bw      = 100e3                  # PLL 3dB bandwidth [Hz]
bw_eff  = (np.pi / 2) * bw      # noise-equivalent BW, 1st order PLL [Hz]

# ── Saturation: <100 µW optical input power (single-ended detector) ───────────
# This is total power on the photodiode, not a differential limit.
# For a heterodyne setup using this as single port:
#   P_tot = P_m + P_r on the detector
# Saturation when P_tot = P_sat_total
# Equal beams: P_m = P_r = P_sat_total / 2
P_sat_total   = 100e-6           # [W] saturation limit (total power on PD)
P_sat_per_beam = P_sat_total / 2 # [W] per beam for equal powers

# ── Power sweep ───────────────────────────────────────────────────────────────
P_m = np.linspace(1e-6, P_sat_per_beam, 500)
P_r = P_m

i_sig_peak = Res * sp.j1(m) * np.sqrt(het_eff * P_m * P_r)

# ── Shot noise ────────────────────────────────────────────────────────────────
# Single-ended: no balanced detection, no RIN cancellation
shot_asd   = np.sqrt(2 * e * Res * (P_m + P_r))
phase_shot = shot_asd / i_sig_peak
rms_shot   = phase_shot * np.sqrt(bw_eff)

# ── NEP ───────────────────────────────────────────────────────────────────────
nep_asd    = NEP * Res
phase_nep  = nep_asd / i_sig_peak
rms_nep    = phase_nep * np.sqrt(bw_eff)

# ── RIN ───────────────────────────────────────────────────────────────────────
RIN        = 1e-8
rin_asd    = Res * (P_m + P_r) * RIN
phase_rin  = rin_asd / i_sig_peak
rms_rin    = phase_rin * np.sqrt(bw_eff)

# ── Total ─────────────────────────────────────────────────────────────────────
phase_total = np.sqrt(phase_shot**2 + phase_nep**2 + phase_rin**2)
rms_total   = phase_total * np.sqrt(bw_eff)

# ── Plotting ──────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
fig.suptitle('Menlo FPD510-FC-NIR  |  Phase noise ASD  |  PLL BW = 100 kHz', fontsize=10)

ax.plot(P_m * 1e6, phase_shot  * 1e6, color='tab:blue',   label='Shot noise')
ax.plot(P_m * 1e6, phase_nep   * 1e6, color='tab:orange', label=f'NEP ({NEP*1e12:.1f} pW/√Hz)')
ax.plot(P_m * 1e6, phase_rin   * 1e6, color='tab:green',  label=f'RIN ({RIN:.0e} /√Hz)')
ax.plot(P_m * 1e6, phase_total * 1e6, color='black',      label='Total', linestyle='--', linewidth=1.5)
ax.axvline(P_sat_per_beam * 1e6, color='red', linestyle=':', linewidth=1.2,
           label=f'Sat. limit ({P_sat_per_beam*1e6:.0f} µW/beam, 100 µW total)')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Power per beam $P_m$ (µW)')
ax.set_ylabel('Phase noise ASD (μrad/√Hz)')
ax.set_title('Single-ended (unbalanced)')
ax.legend(fontsize=9)
ax.grid(True, which='both', alpha=0.3)

plt.tight_layout()
#plt.savefig('SNR_Menlo.png', dpi=150)
plt.show()