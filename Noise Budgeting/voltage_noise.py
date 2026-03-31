import numpy as np
import matplotlib.pyplot as plt

# ── physical parameters (normalised / representative) ────────────────────────
f_het  = 7e6       # heterodyne frequency [Hz]
R      = 0.6       # photodiode responsivity [A/W]
Z      = 5e3       # transimpedance gain [V/A]
Power1 = 10e-3
E      = np.sqrt(Power1)      
I_dc   = R * E**2  # mean photocurrent [A]
V_beat = 2*R*Z*E*E # beatnote voltage amplitude [V]

# frequency axis
f = np.logspace(-4, 8, 10000)

# ── INPUT noise ASDs ──────────────────────────────────────────────────────────
# Laser phase noise [rad/√Hz]: 1/f^0.5 slope
S_phi   = 30* (1 + (0.002/f)**4)/f

# RIN [1/√Hz]: 1/f + white floor
S_rin   = np.sqrt((5e-8 / np.maximum(f, 1e-3))**2 + (1e-8)**2)

# Shot noise current ASD [A/√Hz]
S_shot_A = np.sqrt(2 * 1.6e-19 * I_dc) * np.ones_like(f)

# PD dark current
S_dark_A = 2e-12 * np.ones_like(f)

# Amplifier voltage noise [V/√Hz]
S_amp_V  = 5e-9 * np.ones_like(f)

# ── NOISE IN V_AC ─────────────────────────────────────────────────────────────
# Laser phase: PM sidebands on beatnote → V_beat * S_phi
S_phi_V     = V_beat * S_phi

# RIN term (ii): E^2 * RIN, additive at low f (1f mechanism)
S_rin_ii_V  = V_beat * S_rin

# RIN term (iii): (V_beat/2) * RIN, AM sidebands on beatnote (2f mechanism)
S_rin_iii_V = (V_beat / 2) * S_rin

# Shot → voltage via transimpedance
S_shot_V    = R * Z * S_shot_A

# Dark Current as voltage
S_dark_V    = R * Z * S_dark_A

# Amp noise already in V
# S_amp_V as above

# total in V_AC
S_total_V = np.sqrt(S_phi_V**2 + S_rin_ii_V**2 +
                    S_rin_iii_V**2 + S_shot_V**2 + S_dark_V**2 + S_amp_V**2)

# ── colours ───────────────────────────────────────────────────────────────────
C_phi  = "#4FC3F7"   # blue
C_rin  = "#FF8A65"   # orange
C_shot = "#A5D6A7"   # teal
C_dark = "#A5D6D5"   # teal
C_amp  = "#CE93D8"   # violet
C_tot  = "#FFD54F"   # amber
BG     = "#0f0f1a"
BG2    = "#161625"
CG     = "#2a2a3a"

plt.rcParams.update({
    "font.family":     "monospace",
    "text.color":      "white",
    "axes.labelcolor": "white",
    "xtick.color":     "white",
    "ytick.color":     "white",
})

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), facecolor=BG)
fig.patch.set_facecolor(BG)

for ax in (ax1, ax2):
    ax.set_facecolor(BG2)
    for sp in ax.spines.values():
        sp.set_color("#444466")
    ax.tick_params(colors="white", which="both", labelsize=9)
    ax.grid(True, which="major", color=CG, lw=0.6, alpha=0.6)
    ax.grid(True, which="minor", color=CG, lw=0.3, alpha=0.3)

# ── LEFT: input noise ASDs ────────────────────────────────────────────────────
ax1.loglog(f, S_phi,    color=C_phi,  lw=2.0, label=r"Laser phase noise  $\tilde{\delta\phi}$  [rad/$\sqrt{\rm Hz}$]")
ax1.loglog(f, S_rin,    color=C_rin,  lw=2.0, label=r"RIN  $\tilde{r}$  [$1/\sqrt{\rm Hz}$]")
ax1.loglog(f, S_shot_A, color=C_shot, lw=2.0, label=r"Shot noise  $\sqrt{2eI_{\rm dc}}$  [A/$\sqrt{\rm Hz}$]")
ax1.loglog(f, S_dark_A, color=C_dark, lw=2.0, label=r"Dark current [A/$\sqrt{\rm Hz}$]")
ax1.loglog(f, S_amp_V,  color=C_amp,  lw=2.0, label=r"Amp noise  $\tilde{n}_{\rm amp}$  [V/$\sqrt{\rm Hz}$]")

for fx, lbl in [(f_het, r"$f_{\rm het}$"), (2*f_het, r"$2f_{\rm het}$")]:
    ax1.axvline(fx, color="white", lw=0.8, ls=":", alpha=0.4)
    ax1.text(fx*1.08, 2e-11, lbl, color="white", fontsize=9, alpha=0.7)

ax1.set_xlim(f[0], f[-1])
ax1.set_ylim(1e-15, 1e6)
ax1.set_xlabel("Frequency  [Hz]", fontsize=10)
ax1.set_ylabel("Input noise ASD  (natural units)", fontsize=10)
ax1.set_title("Input noise spectra", fontsize=11, color="white", pad=10)
ax1.legend(fontsize=8.5, framealpha=0.2, loc="lower left",
           labelcolor="white", facecolor=BG2, edgecolor="#444466")

# ── RIGHT: noise in V_AC ──────────────────────────────────────────────────────
ax2.loglog(f, S_phi_V,     color=C_phi,  lw=2.0,
           label=r"Laser $\phi$ noise  $V_{\rm beat}\cdot\tilde{\delta\phi}$")
ax2.loglog(f, S_rin_ii_V,  color=C_rin,  lw=2.0, ls="-",
           label=r"1f-RIN  $\mathcal{R}Z E^2\tilde{r}$  (additive at low $f$)")
ax2.loglog(f, S_rin_iii_V, color=C_rin,  lw=2.0, ls="--",
           label=r"2f-RIN  $(V_{\rm beat}/2)\tilde{r}$  (AM sidebands)")
ax2.loglog(f, S_shot_V,    color=C_shot, lw=2.0,
           label=r"Shot  $\mathcal{R}Z\sqrt{2eI_{\rm dc}}$")
ax2.loglog(f, S_dark_V,    color=C_dark, lw=2.0,
           label=r"Dark current  $\mathcal{R}Z\sqrt{2eI_{\rm dark}}$")

ax2.loglog(f, S_amp_V,     color=C_amp,  lw=2.0,
           label=r"Amp noise  $\tilde{n}_{\rm amp}$")
ax2.loglog(f, S_total_V,   color=C_tot,  lw=2.5, ls="--",
           label="Total", zorder=5)

for fx, lbl in [(f_het, r"$f_{\rm het}$"), (2*f_het, r"$2f_{\rm het}$")]:
    ax2.axvline(fx, color="white", lw=0.8, ls=":", alpha=0.4)
    ax2.text(fx*1.08, 3e-14, lbl, color="white", fontsize=9, alpha=0.7)

# shade the region below f_het
ax2.axvspan(f[0], f_het, color="white", alpha=0.03)
ax2.text(3e3, 5e-8, "below\n$f_{\\rm het}$", color="white",
         fontsize=8, alpha=0.4, ha="center")

ax2.set_xlim(f[0], f[-1])
ax2.set_ylim(1e-14, 1e6)
ax2.set_xlabel("Frequency  [Hz]", fontsize=10)
ax2.set_ylabel(r"$V_{\rm AC}$ noise ASD  [V/$\sqrt{\rm Hz}$]", fontsize=10)
ax2.set_title(r"Noise contributions in $V_{\rm AC}(t)$", fontsize=11,
              color="white", pad=10)
ax2.legend(fontsize=8.5, framealpha=0.2, loc="lower left",
           labelcolor="white", facecolor=BG2, edgecolor="#444466")

# ── titles ────────────────────────────────────────────────────────────────────
fig.text(0.5, 0.97,
         r"Photodetector Noise Budget  —  $V_{\rm AC}(t)$",
         ha="center", va="top", fontsize=13, color="white",
         fontfamily="monospace", fontweight="bold")
fig.text(0.5, 0.935,
         r"$f_{\rm het}=7\,{\rm MHz}$  |  "
         r"$\mathcal{R}=0.8\,{\rm A/W}$  |  "
         r"$Z=1\,{\rm k}\Omega$  |  "
         r"$E_{ij}=E_{ji}=1\,{\rm mW}^{1/2}$",
         ha="center", va="top", fontsize=9, color="#aaaacc",
         fontfamily="monospace")

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig("rin_coupling.png",
            dpi=150, bbox_inches="tight", facecolor=BG)

