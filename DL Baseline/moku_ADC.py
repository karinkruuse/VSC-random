"""
Moku Pro phasemeter phase noise floor.

The phasemeter demodulates at carrier f0. ADC noise at the two sidebands
(f0 - f) and (f0 + f) both fold into the phase estimate, giving:

    S_phi(f) = 2 * e_n(f0)^2 / A_peak^2     [rad^2/Hz]

Since f0 >> f (11 MHz carrier, mHz-Hz offsets), e_n is evaluated at f0,
which from the measured Moku Pro ASD is flat at ~1e-7 V/sqrt(Hz).

L(f) = S_phi(f) / 2     [dBc/Hz]   (standard SSB convention)
"""

import numpy as np
import matplotlib.pyplot as plt

# ── Parameters ────────────────────────────────────────────────────────────────

e_n_at_f0  = 1e-7      # ADC noise at carrier frequency [V/sqrt(Hz)] — flat floor
signal_dBm = 18      # signal power into 50 ohm [dBm]
f0         = 11e6      # carrier frequency [Hz]
impedance  = 50.0      # input impedance [ohm]

# Offset frequency axis
f = np.logspace(-3, 1.1, 500)   # 1 mHz to ~12 Hz

# ── Signal amplitude ──────────────────────────────────────────────────────────

signal_W = 10 ** ((signal_dBm - 30) / 10)   # [W]
V_rms    = np.sqrt(signal_W * impedance)      # [V rms]
print(signal_W, V_rms)
A_peak   = V_rms * np.sqrt(2)                 # [V peak]

# ── Phase noise floor (flat in offset frequency) ──────────────────────────────

S_phi   = 2 * e_n_at_f0**2 / A_peak**2       # [rad^2/Hz]
L_f     = S_phi / 2                           # [1/Hz]  SSB phase noise
L_f_dBc = 10 * np.log10(L_f)                 # [dBc/Hz]  — single number, flat

# Frequency noise ASD
S_f_sqrt = f0 * np.sqrt(S_phi)               # [Hz/sqrt(Hz)]

# ── Print ─────────────────────────────────────────────────────────────────────

print("=" * 52)
print("  Moku Pro phasemeter noise floor")
print("=" * 52)
print(f"  e_n at f0        : {e_n_at_f0:.1e} V/sqrt(Hz)")
print(f"  Signal           : {signal_dBm} dBm  ->  Vrms = {V_rms*1e3:.2f} mV")
print(f"  A_peak           : {A_peak*1e3:.2f} mV")
print(f"  Carrier f0       : {f0/1e6:.1f} MHz")
print("-" * 52)
print(f"  S_phi            : {10*np.log10(S_phi):.1f} dBrad^2/Hz")
print(f"  L(f)             : {L_f_dBc:.1f} dBc/Hz  (flat, white)")
print(f"  Sf               : {S_f_sqrt:.3f} Hz/sqrt(Hz)")
print("=" * 52)

# ── Plot ──────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots()
fig.suptitle(
    f"Moku Pro phasemeter noise floor  |  "
    f"signal = {signal_dBm} dBm,  f0 = {f0/1e6:.1f} MHz,  "
    f"e_n = {e_n_at_f0:.0e} V/sqrt(Hz)",
    fontsize=12
)

axes.loglog(f, np.full_like(f, np.sqrt(S_phi/2/np.pi)), color="#185FA5", linewidth=2)
axes.set_xlabel("Fourier offset frequency (Hz)")
axes.set_ylabel("Sqrt(S_phi)  [cyc/sqrt(Hz)]")
axes.set_title("Phase noise floor")
axes.grid(True, which="both", linestyle="--", alpha=0.4)
axes.set_xlim(f[0], f[-1])



plt.tight_layout()
plt.savefig("phasemeter_noise_floor.png", dpi=150)
plt.show()
print("\nPlot saved.")