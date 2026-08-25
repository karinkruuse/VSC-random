import numpy as np
import matplotlib.pyplot as plt
import scipy.special as sp
from scipy.constants import elementary_charge as e, Boltzmann as kB

# ── Parameters ────────────────────────────────────────────────────────────────


# Turn off log plot and check that noises are lowers when the ratio is 50:50
P_tot = 1e-3                            # fixed total power
gamma = np.logspace(-2, 2, 200)   # NOT logspace(-2, 0, ...)
P_m = P_tot * gamma / (1 + gamma)
P_r = P_tot / (1 + gamma)


P_m   = np.arange(10e-6, 10e-3, 10e-6)  # power per beam [W], equal beams P_m = P_r; capped at 10 mW/beam (30 mW abs-max total)
P_r   = P_m




Res   = 0.6                             # responsivity [A/W]
R     = 50                              # termination resistance [Ω]
T     = 300                             # temperature [K]
bw    = 100e3                           # PLL 3dB bandwidth [Hz]
bw_eff = (np.pi / 2) * bw              # noise-equivalent BW, 1st order PLL [Hz]

het_eff = 0.9                           # heterodyne efficiency
m       = 0.53                          # modulation depth

# Signal: peak current at heterodyne frequency
i_sig_peak = Res * sp.j1(m) * np.sqrt(het_eff * P_m * P_r)


# ── Shot noise ────────────────────────────────────────────────────────────────
shot_asd   = np.sqrt(2 * e * Res * (P_m + P_r))        # current ASD [A/√Hz]
phase_shot = shot_asd / i_sig_peak        # phase ASD [rad/√Hz]
rms_shot   = phase_shot * np.sqrt(bw_eff)               # integrated RMS [rad]

# ── Johnson noise ─────────────────────────────────────────────────────────────
johnson_asd   = np.sqrt(4 * kB * T / R)                 # current ASD [A/√Hz]
phase_johnson = johnson_asd / i_sig_peak  # phase ASD [rad/√Hz]
rms_johnson   = phase_johnson * np.sqrt(bw_eff)         # integrated RMS [rad]

# ── RIN ───────────────────────────────────────────────────────────────────────
RIN       = 1e-8                                         # [1/√Hz]
rin_asd   = Res * (P_m + P_r) * RIN                     # current ASD [A/√Hz]
phase_rin = rin_asd / i_sig_peak          # phase ASD [rad/√Hz]
rms_rin   = phase_rin * np.sqrt(bw_eff)                 # integrated RMS [rad]

# ── Total ─────────────────────────────────────────────────────────────────────
phase_total = np.sqrt(phase_shot**2 + phase_johnson**2 + phase_rin**2)
rms_total   = phase_total * np.sqrt(bw_eff)

# ── Plotting ──────────────────────────────────────────────────────────────────

plt.plot(P_m * 1e3, phase_shot    * 1e6, label='Shot noise')
plt.plot(P_m * 1e3, phase_johnson * 1e6, label='Johnson noise')
plt.plot(P_m * 1e3, phase_rin     * 1e6, label='RIN')
plt.plot(P_m * 1e3, phase_total   * 1e6, 'k--', label='Total')
plt.xscale('log')
plt.yscale('log')
plt.xlabel('Power per beam $P_m$ (mW)')
plt.ylabel('Phase noise ASD (μrad/√Hz)')
plt.title('Phase noise spectral density')
plt.legend()
plt.grid(True, which='both', alpha=0.3)



plt.tight_layout()
#plt.savefig('SNR.png', dpi=150)
plt.show()