"""
Phasemeter phase noise for coloured (power-law) input noise.

General formula (derived from mixer + LPF + linearised atan2):

    φ̃(f)² = [S_n(f₀+f) + S_n(f₀−f)] / A²

i.e. the phase noise PSD at baseband frequency f is set by the input
noise PSD at the two sidebands f₀ ± f, added in quadrature.

For flat (white) noise S_n = const:
    φ̃(f) = √2 · ñ / A = ñ / A_rms

For coloured noise (S_n ∝ f^α), the phase noise inherits the same slope
evaluated at the carrier band — the √2/A factor still holds locally,
at each frequency.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.signal import welch

# ── parameters ────────────────────────────────────────────────────────────────
fs      = 1.0
f0      = 0.1          # carrier
f_cut   = f0 / 2       # LPF cutoff
w0      = 2*np.pi*f0
N       = 2**20
t       = np.arange(N)
A       = 1.0
phi     = 0.3
sigma_n = 0.3

# ── coloured noise generator ──────────────────────────────────────────────────
def coloured_noise(alpha, seed=42):
    """Noise with one-sided PSD ∝ f^alpha, normalised to RMS = sigma_n."""
    rng   = np.random.default_rng(seed)
    S     = np.fft.rfft(rng.standard_normal(N))
    f     = np.fft.rfftfreq(N, 1/fs);  f[0] = f[1]
    S    *= f ** (alpha / 2.0);        S[0]  = 0.0
    out   = np.fft.irfft(S, n=N)
    return out / out.std() * sigma_n

# ── brickwall LPF ─────────────────────────────────────────────────────────────
def blpf(sig):
    S = np.fft.rfft(sig)
    S[np.fft.rfftfreq(N, 1/fs) > f_cut] = 0.0
    return np.fft.irfft(S, n=N)

# ── phasemeter ────────────────────────────────────────────────────────────────
def phasemeter(noise):
    x  = A * np.sin(w0*t + phi) + noise
    Q  = blpf(0.5 * x * np.cos(w0*t))
    I  = blpf(0.5 * x * np.sin(w0*t))
    ph = np.arctan2(Q, I)
    return np.arctan2(np.sin(ph - phi), np.cos(ph - phi))

# ── theoretical prediction for coloured noise ─────────────────────────────────
def predict_phi_asd(ff, psd_n):
    """φ̃(f) = (1/A) √[S_n(f₀+f) + S_n(f₀−f)]"""
    Sn_plus  = np.interp(f0 + ff, ff, psd_n)
    Sn_minus = np.interp(np.abs(f0 - ff), ff, psd_n)
    return (1/A) * np.sqrt(Sn_plus + Sn_minus)

# ── cases ─────────────────────────────────────────────────────────────────────
cases = [
    ('white  (α= 0)',  0,  'steelblue',  42),
    ('pink   (α=−1)', -1,  'darkorange', 43),
    ('red    (α=−2)', -2,  'crimson',    44),
]

nperseg = 2**14
band    = None

fig = plt.figure(figsize=(14, 10))
gs  = GridSpec(2, 2, fig, hspace=0.45, wspace=0.38)
fig.suptitle(
    r'Phasemeter phase noise:  $\tilde{\varphi}(f)^2 = [S_n(f_0{+}f) + S_n(f_0{-}f)]\,/\,A^2$',
    fontsize=12, y=0.99)

ax_in  = fig.add_subplot(gs[0, 0])
ax_out = fig.add_subplot(gs[0, 1])
ax_rat = fig.add_subplot(gs[1, 0])
ax_his = fig.add_subplot(gs[1, 1])

print(f"  {'Case':<18}  ratio φ̃/predicted  (expect 1.00)")
print("  " + "-"*48)

for label, alpha, col, seed in cases:
    noise = coloured_noise(alpha, seed)
    dp    = phasemeter(noise)

    ff, psd_n   = welch(noise, fs=fs, nperseg=nperseg, window='hann', detrend=False)
    ff, psd_phi = welch(dp,    fs=fs, nperseg=nperseg, window='hann', detrend=False)

    if band is None:
        band = (ff > f_cut * 0.03) & (ff < f_cut * 0.85)

    phi_pred = predict_phi_asd(ff, psd_n)
    ratio    = np.sqrt(psd_phi[band]) / phi_pred[band]
    print(f"  {label:<18}  {np.median(ratio):.4f}")

    ax_in.loglog( ff[band], np.sqrt(psd_n[band]),   color=col, lw=1.5, label=label)
    ax_out.loglog(ff[band], np.sqrt(psd_phi[band]),  color=col, lw=1.5, label=label)
    ax_out.loglog(ff[band], phi_pred[band], color=col, lw=2, ls='--', alpha=0.6)
    ax_rat.semilogx(ff[band], ratio, color=col, lw=1.5, label=label)
    ax_his.hist(dp, bins=150, density=True, alpha=0.5, color=col, label=label)

# formatting
ax_in.set_xlabel('Frequency [normalised Hz]')
ax_in.set_ylabel('Input noise ASD  ñ(f)  [/√Hz]')
ax_in.set_title('Input noise spectra')
ax_in.legend(fontsize=9); ax_in.grid(alpha=0.3, which='both')

ax_out.set_xlabel('Frequency [normalised Hz]')
ax_out.set_ylabel('Phase noise ASD  φ̃(f)  [rad/√Hz]')
ax_out.set_title('Output phase noise ASD\n(solid = sim, dashed = theory)')
ax_out.legend(fontsize=9); ax_out.grid(alpha=0.3, which='both')

ax_rat.axhline(1.0, color='k', lw=2, ls='--', label='expected = 1')
ax_rat.set_ylim(0, 2)
ax_rat.set_xlabel('Frequency [normalised Hz]')
ax_rat.set_ylabel('φ̃_sim / φ̃_theory')
ax_rat.set_title('Ratio: simulation / prediction\n(flat at 1.0 for all spectra ✓)')
ax_rat.legend(fontsize=9); ax_rat.grid(alpha=0.3, which='both')

ax_his.set_xlabel('Phase error δφ [rad]')
ax_his.set_ylabel('Probability density')
ax_his.set_title('Phase error distributions\n(steeper noise → broader, non-Gaussian tails)')
ax_his.legend(fontsize=9); ax_his.grid(alpha=0.3)

plt.savefig('phasemeter_noise_coloured.png', dpi=150, bbox_inches='tight')
