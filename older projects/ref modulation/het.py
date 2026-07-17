"""
Heterodyne interferometer signal from electric fields.

A photodiode cannot follow optical frequencies (~100 THz); it time-averages
over many optical cycles. We implement this correctly by working with the
slowly-varying envelope, which is exact and avoids sampling the optical carrier.

Starting point:
    E_k(t) = Re[ a_k * exp(i*omega_k*t) ]

The time-averaged power (over one optical period) is:
    <E_k^2> = a_k^2 / 2  =: P_k

For a 50:50 beamsplitter:
    E_A = (1/sqrt2)*E_m + (1/sqrt2)*E_r
    E_B = -(1/sqrt2)*E_m + (1/sqrt2)*E_r

Detected (time-averaged) powers:
    P_A = <E_A^2> = (1/2)<(E_m + E_r)^2>
                  = (1/2)[<E_m^2> + <E_r^2> + 2<E_m*E_r>]

The cross term <E_m*E_r> = (a_m*a_r/2)*cos(omega_het*t - phi)
because the product of two cosines at different frequencies only has a
slowly-varying (surviving) component at the difference frequency.
"""

import numpy as np
import matplotlib.pyplot as plt

# ── Parameters ────────────────────────────────────────────────────────────────
P0      = 1.0           # equal beam power [W]
f_het   = 1e6           # heterodyne frequency [Hz]
phi     = np.pi / 4     # relative optical phase [rad]

# Amplitudes: P = a^2/2  =>  a = sqrt(2*P)
a_m = np.sqrt(2 * P0)
a_r = np.sqrt(2 * P0)

# Time axis: 3 heterodyne cycles
T_het = 1 / f_het
t = np.linspace(0, 3 * T_het, 10_000)
omega_het = 2 * np.pi * f_het

# ── Time-averaged cross term ───────────────────────────────────────────────────
# <E_m * E_r> = (a_m * a_r / 2) * cos(omega_het*t - phi)
cross = (a_m * a_r / 2) * np.cos(omega_het * t - phi)

# ── Individual beam powers (DC, from time-averaging cos^2) ────────────────────
P_m = a_m**2 / 2   # = P0
P_r = a_r**2 / 2   # = P0

# ── Detected powers at each port ──────────────────────────────────────────────
# P_A = (1/2)(P_m + P_r + cross_term)  -- the 1/2 comes from BS coefficients
# More explicitly, with rho=tau=1/sqrt(2):
#   P_A = rho^2*P_m + tau^2*P_r + 2*rho*tau*(a_m*a_r/2)*cos(...)
#        =  P_m/2   +  P_r/2   +       cross
P_A = P_m/2 + P_r/2 + cross     # = P0 + P0*cos(...)
P_B = P_m/2 + P_r/2 - cross     # = P0 - P0*cos(...)

# ── Analytical formula (equal beams) ──────────────────────────────────────────
P_A_theory = P0 * (1 + np.cos(omega_het * t - phi))
P_B_theory = P0 * (1 - np.cos(omega_het * t - phi))

# ── Energy conservation ────────────────────────────────────────────────────────
P_total_in  = P_m + P_r
P_total_out = P_A + P_B     # should be P0+P0 = 2 W at every instant

max_err = np.max(np.abs(P_total_out - P_total_in))

print("=" * 55)
print("  Heterodyne interferometer — power budget")
print("=" * 55)
print(f"  Beam power P0                 : {P0:.4f} W")
print(f"  Total input  P_m + P_r        : {P_total_in:.4f} W")
print()
print(f"  DC of P_A                     : {P0:.4f} W  (= P0)")
print(f"  DC of P_B                     : {P0:.4f} W  (= P0)")
print(f"  AC amplitude (both ports)     : {P0:.4f} W  (= P0)")
print()
print(f"  P_A max  (constructive)       : {2*P0:.4f} W  (= 2*P0)")
print(f"  P_A min  (destructive)        : {0.:.4f} W  (= 0)")
print()
print(f"  Max |P_A + P_B - P_in|        : {max_err:.2e} W  ✓")
print("=" * 55)
print()
print("  P_A = P0*(1 + cos(w_het*t - phi))")
print("  P_B = P0*(1 - cos(w_het*t - phi))")
print("  P_A + P_B = 2*P0  at every instant  =>  energy conserved")
print("=" * 55)

# ── Plot ───────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(9, 8), sharex=True)
t_us = t * 1e6

# Port A
axes[0].plot(t_us, P_A,        lw=2,   label=r'$P_A$ (numerical)',   color='steelblue')
axes[0].plot(t_us, P_A_theory, lw=1.5, label=r'$P_A$ (analytical)',  color='navy', ls='--')
axes[0].axhline(P0,  color='grey', lw=0.8, ls=':', label='$P_0$ (DC level)')
axes[0].axhline(2*P0,color='grey', lw=0.8, ls=':')
axes[0].set_ylabel('Power (W)')
axes[0].set_title('Port A  —  constructive interference at $t=0$')
axes[0].legend(loc='upper right')
axes[0].set_ylim(-0.15, 2.3)

# Port B
axes[1].plot(t_us, P_B,        lw=2,   label=r'$P_B$ (numerical)',  color='tomato')
axes[1].plot(t_us, P_B_theory, lw=1.5, label=r'$P_B$ (analytical)', color='darkred', ls='--')
axes[1].axhline(P0, color='grey', lw=0.8, ls=':')
axes[1].set_ylabel('Power (W)')
axes[1].set_title('Port B  —  destructive when A is constructive')
axes[1].legend(loc='upper right')
axes[1].set_ylim(-0.15, 2.3)

# Sum
axes[2].plot(t_us, P_A + P_B, lw=2, color='purple', label=r'$P_A + P_B$ (numerical)')
axes[2].axhline(P_total_in, color='k', lw=1.5, ls='--',
                label=f'Total input $P_m + P_r = {P_total_in:.1f}$ W')
axes[2].set_ylabel('Power (W)')
axes[2].set_title('Energy conservation: $P_A + P_B = P_m + P_r$ always')
axes[2].set_xlabel('Time (µs)')
axes[2].legend(loc='upper right')
axes[2].set_ylim(0, 3)

fig.suptitle(
    r'Heterodyne interferometer from $E$-fields  '
    r'($P_0=1\,\mathrm{W}$, 50:50 BS, $f_\mathrm{het}=1\,\mathrm{MHz}$)',
    fontsize=12
)
plt.tight_layout()
plt.savefig('heterodyne.png', dpi=150)
print("\n  Plot saved to heterodyne.png")

# ── Fourier transform of P_A and P_B ──────────────────────────────────────────
dt = t[1] - t[0]
N  = len(t)

# FFT (one-sided)
freqs = np.fft.rfftfreq(N, d=dt)           # [Hz]
FA    = np.fft.rfft(P_A) / N              # normalise by N → physical amplitude
FB    = np.fft.rfft(P_B) / N

# One-sided amplitude spectrum: double non-DC bins
amp_A = np.abs(FA) * 2
amp_B = np.abs(FB) * 2
amp_A[0] /= 2   # DC bin: don't double
amp_B[0] /= 2

# Power spectral density [W^2/Hz]  (one-sided)
PSD_A = (np.abs(FA)**2 * 2) / (N * dt)
PSD_B = (np.abs(FB)**2 * 2) / (N * dt)
PSD_A[0] /= 2
PSD_B[0] /= 2

print("\n" + "=" * 55)
print("  Fourier analysis")
print("=" * 55)
# Find DC and het peaks
i_dc  = 0
i_het = np.argmin(np.abs(freqs - f_het))
print(f"  P_A  DC amplitude   : {amp_A[i_dc]:.4f} W   (expect P0 = {P0:.4f} W)")
print(f"  P_A  f_het amplitude: {amp_A[i_het]:.4f} W   (expect P0 = {P0:.4f} W)")
print(f"  P_B  DC amplitude   : {amp_B[i_dc]:.4f} W   (expect P0 = {P0:.4f} W)")
print(f"  P_B  f_het amplitude: {amp_B[i_het]:.4f} W   (expect P0 = {P0:.4f} W)")
print("=" * 55)

# ── Plot spectra ───────────────────────────────────────────────────────────────
fig2, axes2 = plt.subplots(2, 1, figsize=(9, 6), sharex=True)

for ax, amp, label, color in zip(
        axes2,
        [amp_A, amp_B],
        ['Port A', 'Port B'],
        ['steelblue', 'tomato']):
    ax.stem(freqs / 1e6, amp, linefmt=color, markerfmt='o', basefmt='k-')
    ax.set_ylabel('Amplitude (W)')
    ax.set_title(f'{label} — amplitude spectrum')
    ax.set_xlim(-0.1, 3)
    ax.annotate(f'DC = {amp[i_dc]:.2f} W',
                xy=(0, amp[i_dc]), xytext=(0.3, amp[i_dc]*1.05),
                fontsize=9, color=color)
    ax.annotate(f'$f_{{\\rm het}}$ = {amp[i_het]:.2f} W',
                xy=(f_het/1e6, amp[i_het]), xytext=(f_het/1e6+0.15, amp[i_het]*1.05),
                fontsize=9, color=color)

axes2[1].set_xlabel('Frequency (MHz)')
fig2.suptitle(
    r'Amplitude spectrum of detected powers  '
    r'($P_0=1\,\mathrm{W}$, $f_\mathrm{het}=1\,\mathrm{MHz}$)',
    fontsize=12
)
plt.tight_layout()
plt.savefig('heterodyne_spectrum.png', dpi=150)
print("  Spectrum plot saved to heterodyne_spectrum.png")