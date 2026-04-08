"""
Clock jitter extraction: why f_mod >> f_het matters.

The simulation:
  1. Generate a true clock jitter signal q(t)
  2. Imprint it onto a sideband as phase: phi_SB = 2*pi*f_mod * q(t)
  3. Add readout noise phi_noise to the PM measurement
  4. Extract q_hat = phi_SB_measured / (2*pi*f_mod)
  5. Compare residual noise for different choices of f_mod
"""

import numpy as np
import matplotlib.pyplot as plt

# ── Setup ──────────────────────────────────────────────────────────────────────
rng   = np.random.default_rng(42)
fs    = 10.0          # sample rate [Hz]
T     = 1e5           # duration [s]
N     = int(T * fs)
t     = np.arange(N) / fs
f     = np.fft.rfftfreq(N, 1/fs)
f     = f[1:]         # drop DC

# True clock jitter: 1/f noise in fractional frequency -> integrate to timing
# S_qdot(f) = 4e-27 / f  (fractional freq) => S_q(f) = 4e-27 / f^3
# We just generate it directly in freq domain
def generate_pink_phase(f, fs, N, amplitude):
    """Generate 1/f timing jitter time series."""
    # Build one-sided PSD, then ifft
    psd    = amplitude / f**3          # S_q(f) ~ 1/f^3
    amp    = np.sqrt(psd * fs / 2)     # amplitude per bin
    phase  = rng.uniform(0, 2*np.pi, len(f))
    X      = amp * np.exp(1j * phase)
    # mirror to two-sided
    X_full = np.zeros(N // 2 + 1, dtype=complex)
    X_full[1:] = X
    return np.fft.irfft(X_full, n=N)

q_true = generate_pink_phase(f, fs, N, amplitude=4e-27)

# PM readout noise: flat phase noise floor [rad/sqrt(Hz)]
phi_noise_asd = 5e-4   # rad/sqrt(Hz)  -- shot-noise limited PM

# ── Simulate for different f_mod ───────────────────────────────────────────────
f_mods = {
    r'$f_\mathrm{mod}$ = 1 MHz'  : 1e6,
    r'$f_\mathrm{mod}$ = 75 MHz' : 75e6,
    r'$f_\mathrm{mod}$ = 2.4 GHz': 2.4e9,
}

results = {}
for label, f_mod in f_mods.items():
    # Imprint: phi_SB = 2*pi*f_mod * q(t)
    phi_SB = 2 * np.pi * f_mod * q_true

    # Add PM readout noise
    phi_noise = rng.normal(0, phi_noise_asd * np.sqrt(fs), N)
    phi_measured = phi_SB + phi_noise

    # Extract: divide by 2*pi*f_mod
    q_hat = phi_measured / (2 * np.pi * f_mod)

    results[label] = q_hat

# ── Compute PSDs ───────────────────────────────────────────────────────────────
def asd(x, fs):
    X   = np.fft.rfft(x)[1:]
    psd = (np.abs(X)**2) / (len(x) * fs)
    return np.fft.rfftfreq(len(x), 1/fs)[1:], np.sqrt(psd)

f_ax, asd_true = asd(q_true, fs)

# Readout noise floor in timing for each f_mod
noise_floors = {label: phi_noise_asd / (2*np.pi*f_mod)
                for label, f_mod in f_mods.items()}

# ── Plot ───────────────────────────────────────────────────────────────────────
plt.style.use('dark_background')
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.patch.set_facecolor('#0d0d14')
for ax in axes:
    ax.set_facecolor('#13131f')
    ax.grid(True, which='both', color='#2a2a3a', lw=0.5)
    for sp in ax.spines.values():
        sp.set_edgecolor('#2a2a3a')
    ax.tick_params(colors='#aaaacc')

COLORS = ['#ff6e40', '#b388ff', '#00d4ff']

# ── Left: time domain (zoom in on first 1000 s) ────────────────────────────────
ax = axes[0]
zoom = int(1000 * fs)
ax.plot(t[:zoom], q_true[:zoom] * 1e12, color='white', lw=1.5,
        label='True $q(t)$', zorder=0)
for (label, _), color in zip(f_mods.items(), COLORS):
    ax.plot(t[:zoom], results[label][:zoom] * 1e12,
            color=color, lw=1, alpha=0.8, label=f'Extracted: {label}')

ax.set_xlabel('Time [s]', color='#aaaacc', fontfamily='monospace')
ax.set_ylabel('Timing jitter [ps]', color='#aaaacc', fontfamily='monospace')
ax.set_title('Time domain', color='#ccccdd', fontfamily='monospace')
ax.legend(fontsize=8.5, facecolor='#1a1a2e', edgecolor='#3a3a5a',
          labelcolor='#ccccdd', prop={'family': 'monospace'})

# ── Right: ASD ─────────────────────────────────────────────────────────────────
ax = axes[1]
ax.loglog(f_ax, asd_true * 1e12, color='white', lw=1, linestyle='--',
          label='True $q(t)$', zorder=0)
for (label, f_mod), color in zip(f_mods.items(), COLORS):
    f_ex, asd_ex = asd(results[label], fs)
    ax.loglog(f_ex, asd_ex * 1e12, color=color, lw=1.2, alpha=0.9,
              label=f'Extracted: {label}')
    # noise floor
    floor = noise_floors[label] * 1e12
    ax.axhline(floor, color=color, lw=1, ls='--', alpha=0.5)

ax.set_xlabel('Frequency [Hz]', color='#aaaacc', fontfamily='monospace')
ax.set_ylabel('Timing jitter ASD [ps/√Hz]', color='#aaaacc', fontfamily='monospace')
ax.set_title('ASD  (dashed = readout noise floor)', color='#ccccdd',
             fontfamily='monospace')
ax.set_xlim(f_ax[0], f_ax[-1])
ax.legend(fontsize=8.5, facecolor='#1a1a2e', edgecolor='#3a3a5a',
          labelcolor='#ccccdd', prop={'family': 'monospace'})

fig.suptitle(
    f'Clock extraction: readout noise floor = $\\tilde{{\\phi}}_\\mathrm{{PM}}$ / $(2\\pi f_\\mathrm{{mod}})$'
    f'   |   PM noise = {phi_noise_asd:.0e} rad/√Hz',
    color='#eeeeff', fontfamily='monospace', fontsize=11)

plt.tight_layout()
plt.savefig('outputs/clock_scaling.png',
            dpi=150, facecolor=fig.get_facecolor())
print("Done.")
