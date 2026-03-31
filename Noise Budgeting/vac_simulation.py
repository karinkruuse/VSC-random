import numpy as np
from scipy.signal import welch
import matplotlib.pyplot as plt

# ── simulation parameters ─────────────────────────────────────────────────────
# 80 MHz for 1s = 80M samples → too much RAM. Use a shorter segment.
# We only need f resolution down to ~0.1 Hz, so T=10s is plenty.
# But at 80MHz that's still 800M samples. Trick: simulate at a lower rate
# that still captures f_het. Nyquist needs > 2*f_het = 14 MHz → use 40 MHz.
# T = 0.1 s → 4M samples, manageable.

fs    = 20e6      # sampling frequency [Hz]
T     = 5       # total duration [s]
N     = int(fs * T)
t     = np.arange(N) / fs

# ── physical parameters ───────────────────────────────────────────────────────
R     = 0.8
Z     = 5e3
Power1 = 10e-3
E      = np.sqrt(Power1)      
f_het = 5e6
omega = 2*np.pi*f_het

rng   = np.random.default_rng(42)

# ── noise helpers ─────────────────────────────────────────────────────────────

def colored_noise(f_knee, asd_floor, N, fs):
    """1/f + white noise via shaped FFT."""
    freqs      = np.fft.rfftfreq(N, d=1/fs)
    freqs[0]   = 1e-10
    asd        = asd_floor * np.sqrt((f_knee / freqs)**2 + 1.0)
    wn         = (rng.standard_normal(len(freqs)) +
                  1j*rng.standard_normal(len(freqs))) / np.sqrt(2)
    shaped     = wn * asd * np.sqrt(fs / 2)
    shaped[0]  = 0
    return np.fft.irfft(shaped, n=N)

def white_noise(asd, N, fs):
    return rng.standard_normal(N) * asd * np.sqrt(fs / 2)

def psd(x, fs):
    nperseg = min(N, int(fs * 0.01))   # 10 ms segments
    f, P    = welch(x, fs=fs, nperseg=nperseg, window='hann', scaling='density')
    return f[1:], np.sqrt(P[1:])

# ── assemble V_AC ─────────────────────────────────────────────────────────────

def build_vac(laser=False, shot=False, amp=False, rin=False):
    dphi_ij = colored_noise(0.2, 30, N, fs) if laser else np.zeros(N)
    dphi_ji = colored_noise(0.2, 30, N, fs) if laser else np.zeros(N)
    rin_ij  = colored_noise(1e3, 1e-8, N, fs) if rin   else np.zeros(N)
    rin_ji  = colored_noise(1e3, 1e-8, N, fs) if rin   else np.zeros(N)

    n_shot  = white_noise(R*Z*np.sqrt(2*1.6e-19*R*E**2), N, fs) if shot else np.zeros(N)
    n_amp   = white_noise(5e-9, N, fs)                           if amp  else np.zeros(N)

    carrier   = np.cos(omega*t + dphi_ij - dphi_ji)
    signal    = 2*R*Z*E*E * carrier
    additive  = n_shot + n_amp
    rin_1f    = R*Z*E**2*(rin_ij + rin_ji)
    rin_2f    = 2*R*Z*E*E * 0.5*(rin_ij + rin_ji) * carrier

    return signal + additive + rin_1f + rin_2f

print("Case 1: no noise...")
v1 = build_vac()
print("Case 2: laser phase noise...")
v2 = build_vac(laser=True)
print("Case 3: all noises...")
v3 = build_vac(laser=True, shot=True, amp=True, rin=True)

print("Computing PSDs...")
f1,a1 = psd(v1, fs)
f2,a2 = psd(v2, fs)
f3,a3 = psd(v3, fs)

# ── plot ──────────────────────────────────────────────────────────────────────
BG  = "#0f0f1a"
BG2 = "#161625"
CG  = "#2a2a3a"

plt.rcParams.update({
    "font.family": "monospace",
    "text.color": "white", "axes.labelcolor": "white",
    "xtick.color": "white", "ytick.color": "white",
})

fig, (ax_t, ax_f) = plt.subplots(1, 2, figsize=(14, 7), facecolor=BG)
fig.patch.set_facecolor(BG)

for ax in (ax_t, ax_f):
    ax.set_facecolor(BG2)
    for sp in ax.spines.values(): sp.set_color("#444466")
    ax.tick_params(colors="white", which="both", labelsize=9)
    ax.grid(True, which="major", color=CG, lw=0.5, alpha=0.6)

# ── time domain: show 3 beatnote cycles ──────────────────────────────────────
n_show = int(fs * 3/f_het)
t_ns   = t[:n_show] * 1e9

ax_t.plot(t_ns, v1[:n_show]*1e3, color="#555577", lw=1.5,
          label="No noise", zorder=3)
ax_t.plot(t_ns, v2[:n_show]*1e3, color="#4FC3F7", lw=1.5,
          label="Laser $\\delta\\phi$", alpha=0.85, zorder=4)
ax_t.plot(t_ns, v3[:n_show]*1e3, color="#FF8A65", lw=1.2,
          label="All noises", alpha=0.75, zorder=2)

ax_t.set_xlabel("Time  [ns]", fontsize=10)
ax_t.set_ylabel("$V_\\mathrm{AC}$  [mV]", fontsize=10)
ax_t.set_title("Time domain  (3 beatnote cycles)", fontsize=11, color="white", pad=10)
ax_t.legend(fontsize=9, framealpha=0.2, labelcolor="white",
            facecolor=BG2, edgecolor="#444466")

# ── frequency domain ─────────────────────────────────────────────────────────
ax_f.loglog(f1, a1, color="#555577", lw=1.5, label="No noise (numerical floor)")
ax_f.loglog(f2, a2, color="#4FC3F7", lw=2.0, label="Laser $\\delta\\phi$ only")
ax_f.loglog(f3, a3, color="#FF8A65", lw=2.0, label="All noises")

ax_f.axvline(f_het,   color="white", lw=0.8, ls=":", alpha=0.5)
ax_f.axvline(2*f_het, color="white", lw=0.8, ls=":", alpha=0.3)
ax_f.text(f_het*1.05,   1e-11, r"$f_\mathrm{het}$",   color="white", fontsize=9, alpha=0.7)
ax_f.text(2*f_het*1.05, 1e-11, r"$2f_\mathrm{het}$",  color="white", fontsize=9, alpha=0.5)

ax_f.set_xlim(f1[1], fs/2)
ax_f.set_xlabel("Frequency  [Hz]", fontsize=10)
ax_f.set_ylabel(r"$V_\mathrm{AC}$ ASD  [V/$\sqrt{\mathrm{Hz}}$]", fontsize=10)
ax_f.set_title("Voltage ASD  (Welch)", fontsize=11, color="white", pad=10)
ax_f.legend(fontsize=9, framealpha=0.2, labelcolor="white",
            facecolor=BG2, edgecolor="#444466")

fig.text(0.5, 0.97, r"$V_\mathrm{AC}(t)$ — time domain simulation & PSD",
         ha="center", va="top", fontsize=13, color="white", fontweight="bold")
fig.text(0.5, 0.935,
         r"$f_s=40\,\mathrm{MHz}$  |  $T=0.1\,\mathrm{s}$  |  "
         r"$f_\mathrm{het}=7\,\mathrm{MHz}$  |  $\mathcal{R}=0.8$  |  "
         r"$Z=1\,\mathrm{k}\Omega$  |  $E=1\,\mathrm{mW}^{1/2}$",
         ha="center", va="top", fontsize=9, color="#aaaacc")

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig("vac_simulation.png",
            dpi=150, bbox_inches="tight", facecolor=BG)
print("Done.")
