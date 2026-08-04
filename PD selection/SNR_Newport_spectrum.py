import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.special as sp
from scipy.constants import elementary_charge as e, Boltzmann as kB

# ── Newport PD parameters (same values as SNR_Newport.py / summary.py) ────────
Res   = 0.6                             # responsivity [A/W]
R     = 50                              # termination resistance [Ω]
T     = 300                             # temperature [K]

het_eff = 0.9                           # heterodyne efficiency
m       = 0.53                          # modulation depth
RIN     = 1e-8                          # relative intensity noise [1/√Hz]

# ── Fixed operating point: 1 mW per beam, 2 mW combined on the PD ─────────────
P_m = 1e-3                              # power per beam [W]
P_r = 1e-3

# Signal: peak current at the heterodyne beat frequency
i_sig_peak = Res * sp.j1(m) * np.sqrt(het_eff * P_m * P_r)

# ── Noise terms (shot/Johnson/RIN are white -> flat spectra in this model) ────
shot_current    = np.sqrt(2 * e * Res * (P_m + P_r))       # A/√Hz
johnson_current = np.sqrt(4 * kB * T / R)                  # A/√Hz
rin_current     = Res * (P_m + P_r) * RIN                  # A/√Hz

phase_shot    = shot_current    / i_sig_peak                # rad/√Hz
phase_johnson = johnson_current / i_sig_peak
phase_rin     = rin_current     / i_sig_peak
phase_total   = np.sqrt(phase_shot**2 + phase_johnson**2 + phase_rin**2)

print(f"Signal current (peak): {i_sig_peak*1e6:.3f} uA")
print(f"Shot noise:            {phase_shot*1e6:.4f} urad/sqrt(Hz)")
print(f"Johnson noise:         {phase_johnson*1e6:.4f} urad/sqrt(Hz)")
print(f"RIN:                   {phase_rin*1e6:.4f} urad/sqrt(Hz)")
print(f"Total:                 {phase_total*1e6:.4f} urad/sqrt(Hz)")

# ── Save the noise floor (total, flat/white) for use in other plots ───────────
noise_floor_path = os.path.join(os.path.dirname(__file__), '..', 'clock_noise', 'newport_pd_noise_floor.csv')
with open(noise_floor_path, 'w') as fh:
    fh.write('Phase ASD (rad/sqrt(Hz))\n')
    fh.write(f'{phase_total}\n')

# ── Plot as spectra vs Fourier frequency (flat, since all terms are white) ────
f = np.logspace(-4, 6, 500)   # Hz

plt.figure(figsize=(9, 5.5))
plt.plot(f, np.full_like(f, phase_shot    * 1e6), label='Shot noise')
plt.plot(f, np.full_like(f, phase_johnson * 1e6), label='Johnson noise')
plt.plot(f, np.full_like(f, phase_rin     * 1e6), label='RIN')
plt.plot(f, np.full_like(f, phase_total   * 1e6), 'k--', label='Total')

plt.xscale('log')
plt.yscale('log')
plt.xlabel('Fourier frequency (Hz)')
plt.ylabel('Phase noise ASD (μrad/√Hz)')
plt.title('Newport PD noise spectra\n(1 mW/beam, 2 mW combined on PD)')
plt.legend()
plt.grid(True, which='both', alpha=0.3)

plt.tight_layout()
plt.savefig('newport_noise_spectrum.png', dpi=150)
plt.show()
