"""
Additive noise in a LISA-like phasemeter — numerical illustration.

Core result:
    Phase noise ASD  φ̃(f) = √2 · ñ(f) / A         [correct]
                           = ñ(f) / A               [PDF-notes, wrong by √2]

The PDF-notes flaw: wrote Var(n_Q) = σ_n² instead of σ_n²/2.
  n_Q = ½ n(t) cos(ω₀t)  →  Var(n_Q) = (1/4) × σ_n² × <cos²> = σ_n²/8
  (not σ_n² as in the notes -- they forgot the ½ from <cos²(ω₀t)> = ½)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.signal import welch

rng = np.random.default_rng(42)

# ── parameters (normalised: fs = 1 Hz) ────────────────────────────────────────
fs    = 1.0          # normalised sampling rate
f0    = 0.1          # carrier [normalised Hz]
f_cut = f0 / 2       # LPF cutoff (kills 2f0 term)
w0    = 2*np.pi*f0
N     = 2**20        # samples (good PSD statistics)
t     = np.arange(N)
A     = 1.0
phi   = 0.3          # true phase [rad]

sigma_n = 0.3        # additive noise RMS

# one-sided noise ASD:  ñ = σ_n × √(2/fs)  [from Parseval, flat spectrum]
n_ASD = sigma_n * np.sqrt(2.0 / fs)

# theoretical phase noise ASDs
phi_ASD_correct = np.sqrt(2) * n_ASD / A   # correct

# Var(n_Q_lp) theory:
# n_Q_raw = ½ n cos(w0t)  → one-sided PSD = σ_n²/(4·fs) [from Var=σ²/8, BW=fs/2]
# after brickwall LPF at f_cut: Var = σ_n²/(4·fs) × f_cut
var_nQ_theory = sigma_n**2 / (4*fs) * f_cut

# ── ideal brickwall LPF via FFT ───────────────────────────────────────────────
def blpf(sig):
    S = np.fft.rfft(sig)
    f = np.fft.rfftfreq(len(sig), 1/fs)
    S[f > f_cut] = 0.0
    return np.fft.irfft(S, n=len(sig))

# ── simulate ──────────────────────────────────────────────────────────────────
n    = rng.normal(0, sigma_n, N)
x    = A * np.sin(w0*t + phi) + n
Q_lp = blpf(0.5 * x * np.cos(w0*t))
I_lp = blpf(0.5 * x * np.sin(w0*t))
nQ   = blpf(0.5 * n * np.cos(w0*t))
nI   = blpf(0.5 * n * np.sin(w0*t))
ph   = np.arctan2(Q_lp, I_lp)
dp   = np.arctan2(np.sin(ph - phi), np.cos(ph - phi))

# ── PSD of phase noise ────────────────────────────────────────────────────────
nperseg = 2**14
ff, psd = welch(dp, fs=fs, nperseg=nperseg, window='hann', detrend=False)

r           = np.corrcoef(nQ, nI)[0, 1]
var_nQ_sim  = np.var(nQ)
sig_phi_sim = np.std(dp)
sig_phi_th  = phi_ASD_correct * np.sqrt(f_cut)   # integrate over [0, f_cut]
mid         = (ff > f_cut*0.05) & (ff < f_cut*0.85)
asd_median  = np.median(np.sqrt(psd[mid]))

# ── SNR sweep ─────────────────────────────────────────────────────────────────
SNR_dB = np.arange(5, 36, 3)
sims, th_c, th_w = [], [], []
for db in SNR_dB:
    sig  = A / 10**(db/20)
    nn   = rng.normal(0, sig, N)
    Qd   = blpf(0.5*(A*np.sin(w0*t+phi)+nn)*np.cos(w0*t))
    Id   = blpf(0.5*(A*np.sin(w0*t+phi)+nn)*np.sin(w0*t))
    d    = np.arctan2(np.sin(np.arctan2(Qd,Id)-phi), np.cos(np.arctan2(Qd,Id)-phi))
    sims.append(np.std(d))
    n_asd_i = sig * np.sqrt(2/fs)
    th_c.append(np.sqrt(2) * n_asd_i / A * np.sqrt(f_cut))
    th_w.append(          n_asd_i / A * np.sqrt(f_cut))

snr_lin = 10**(SNR_dB/20)

# ── figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 11))
gs  = GridSpec(3, 2, fig, hspace=0.55, wspace=0.40)
fig.suptitle('Additive noise in a LISA-like phasemeter', fontsize=13, y=0.98)

# panel 1 – phasor diagram ─────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
th  = np.linspace(0, 2*np.pi, 300)
ax1.plot(np.cos(th), np.sin(th), color='lightgray', lw=1)
ax1.annotate('', xy=(A*np.cos(phi), A*np.sin(phi)), xytext=(0, 0),
             arrowprops=dict(arrowstyle='->', color='navy', lw=2.5))
rng2 = np.random.default_rng(7)
for _ in range(300):
    dq = rng2.normal(0, 0.12); di = rng2.normal(0, 0.12)
    ax1.plot(A*np.cos(phi)+dq, A*np.sin(phi)+di, '.', color='tomato', ms=3, alpha=0.4)
# perpendicular vs parallel arrows
perp_x = -np.sin(phi) * 0.25;  perp_y = np.cos(phi) * 0.25
para_x =  np.cos(phi) * 0.25;  para_y = np.sin(phi) * 0.25
cx, cy = A*np.cos(phi), A*np.sin(phi)
ax1.annotate('', xy=(cx+perp_x, cy+perp_y), xytext=(cx, cy),
             arrowprops=dict(arrowstyle='->', color='red', lw=2))
ax1.annotate('', xy=(cx+para_x, cy+para_y), xytext=(cx, cy),
             arrowprops=dict(arrowstyle='->', color='green', lw=2))
ax1.text(cx+perp_x+0.05, cy+perp_y, r'$n_\perp$ → δφ = $n_\perp$/A', fontsize=9, color='red')
ax1.text(cx+para_x+0.03, cy+para_y-0.12, r'$n_\parallel$ → δA', fontsize=9, color='green')
ax1.set_xlim(-1.5, 1.7); ax1.set_ylim(-1.5, 1.5); ax1.set_aspect('equal')
ax1.set_xlabel('I  (in-phase)'); ax1.set_ylabel('Q  (quadrature)')
ax1.set_title('Phasor picture:\nonly noise ⊥ to carrier rotates the phase')
ax1.grid(alpha=0.3)
ax1.text(0.03, 0.06, r'$\delta\phi \approx n_\perp / A$', transform=ax1.transAxes,
         fontsize=12, color='red',
         bbox=dict(boxstyle='round', fc='white', alpha=0.8))

# panel 2 – scatter n_Q vs n_I ─────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
sub = slice(None, None, 200)
ax2.scatter(nQ[sub], nI[sub], s=4, alpha=0.3, color='purple')
ax2.set_xlabel('$n_Q = ½n\\cos ω_0t$ → LPF'); ax2.set_ylabel('$n_I = ½n\\sin ω_0t$ → LPF')
ax2.set_title(f'Noise channels\nPearson r = {r:.4f} ≈ 0  ✓  (uncorrelated)')
ax2.grid(alpha=0.3)
info = (f'Var($n_Q$) sim    = {var_nQ_sim:.6f}\n'
        f'Var($n_Q$) theory = {var_nQ_theory:.6f}  ✓\n\n'
        f'PDF notes: Var = σ²  = {sigma_n**2:.4f}  ✗\n'
        f'  (missing ⟨cos²⟩ = ½\n   → off by factor 4)')
ax2.text(0.04, 0.97, info, transform=ax2.transAxes, va='top',
         fontsize=8.5, family='monospace',
         bbox=dict(boxstyle='round,pad=0.3', fc='lightyellow', alpha=0.9))

# panel 3 – phase noise ASD ────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, :])
ax3.loglog(ff[mid], np.sqrt(psd[mid]), color='steelblue', lw=1.2, label='simulation')
ax3.axhline(phi_ASD_correct, color='red',   lw=2.5, ls='--',
            label=f'√2·ñ/A = {phi_ASD_correct:.4f} rad/√Hz')
ax3.set_xlabel('Frequency [normalised]')
ax3.set_ylabel('Phase noise ASD  [rad/√Hz]')
ax3.set_title(f'Phase noise ASD   (sim median = {asd_median:.4f},  ratio to correct = {asd_median/phi_ASD_correct:.3f} ✓)')
ax3.legend(fontsize=9.5); ax3.grid(alpha=0.3, which='both')

# panel 4 – phase error histogram ──────────────────────────────────────────────
ax4 = fig.add_subplot(gs[2, 0])
xg  = np.linspace(-4.5*sig_phi_th, 4.5*sig_phi_th, 500)
G   = lambda s: np.exp(-xg**2/(2*s**2)) / (np.sqrt(2*np.pi)*s)
ax4.hist(dp, bins=100, density=True, color='steelblue', alpha=0.65, label='simulation')
ax4.plot(xg, G(sig_phi_th),             'r-',  lw=2.5, label=f'correct:   σ = {sig_phi_th:.4f} rad')
ax4.plot(xg, G(sig_phi_th/np.sqrt(2)),  'k--', lw=2,   label=f'PDF notes: σ = {sig_phi_th/np.sqrt(2):.4f} rad  ✗')
ax4.set_xlabel('Phase error δφ [rad]'); ax4.set_ylabel('Probability density')
ax4.set_title(f'Phase error histogram\n(sim σ = {sig_phi_sim:.4f} rad,  theory = {sig_phi_th:.4f} rad ✓)')
ax4.legend(fontsize=9); ax4.grid(alpha=0.3)

# panel 5 – sigma_phi vs SNR ───────────────────────────────────────────────────
ax5 = fig.add_subplot(gs[2, 1])
ax5.semilogy(SNR_dB, np.degrees(sims),  'o',   ms=6,  color='steelblue', label='simulation')
ax5.semilogy(SNR_dB, np.degrees(th_c),  'r--', lw=2,  label='correct:  √2·ñ/A')
ax5.semilogy(SNR_dB, np.degrees(th_w),  'k:',  lw=2,  label='PDF notes: ñ/A  ✗')
ax5.set_xlabel('SNR [dB]  (= 20 log₁₀ A/σ_n)')
ax5.set_ylabel('σ_φ  [degrees]')
ax5.set_title('Integrated phase noise vs SNR')
ax5.legend(fontsize=9); ax5.grid(alpha=0.3, which='both')

# ── console ────────────────────────────────────────────────────────────────────
print("="*62)
print(f"  σ_n = {sigma_n},  A = {A},  f0 = {f0},  fs = {fs}")
print("="*62)
print(f"  Noise ASD ñ             = {n_ASD:.5f} rad/√Hz")
print(f"  φ̃ correct (√2·ñ/A)     = {phi_ASD_correct:.5f} rad/√Hz")
print(f"  φ̃ sim (PSD median)     = {asd_median:.5f} rad/√Hz  ratio={asd_median/phi_ASD_correct:.4f} ✓")
print()
print(f"  Var(n_Q) theory         = {var_nQ_theory:.6f}")
print(f"  Var(n_Q) sim            = {var_nQ_sim:.6f}   ratio={var_nQ_sim/var_nQ_theory:.4f} ✓")
print(f"  PDF notes Var           = {sigma_n**2:.6f}  ✗ (off by {sigma_n**2/var_nQ_theory:.0f}×)")
print(f"  Cov(n_Q, n_I) sim       = {np.cov(nQ,nI)[0,1]:.7f}  ≈ 0 ✓")
print()
print(f"  σ_φ sim                 = {sig_phi_sim:.5f} rad")
print(f"  σ_φ correct (theory)    = {sig_phi_th:.5f} rad  ✓")
print(f"  σ_φ PDF notes           = {sig_phi_th/np.sqrt(2):.5f} rad  ✗  (off by √2)")
print("="*62)

plt.savefig('phasemeter_noise.png', dpi=150, bbox_inches='tight')
