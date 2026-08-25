"""
LISA laser-frequency-noise budget: pre-stabilised laser noise, where it lands
after TDI-1 / TDI-2 with a 1 m ranging error, and the single-link secondary
noise floor (acceleration + OMS).

All curves are expressed as an equivalent laser FREQUENCY noise ASD [Hz/sqrt(Hz)].

  - laser + TDI residuals are already a frequency noise (factor * sqrt(S_nu)),
    so they need no nu0.
  - OMS / acceleration are displacement / acceleration noises; converting each
    to an equivalent laser frequency noise multiplies by nu0:
        sqrt(S_nu^equiv) = nu0 * (2 pi f / c) * sqrt(S_dL)

Sources
-------
- Pre-stab laser, acc, OMS shapes: LISA-LCST-SGS-TN-001 (Eqs 9-13),
  Hartwig 2021 (Eq D.1).
- TDI ranging-bias residual: Staab et al. 2024, PRD 109, 043040, Eq. (41),
  S_dX2 = |C~|^2 [ 4 Bbar^2 (2 pi f)^2 |S~|^2 |F~|^2 S_p ], with C~ the
  second-gen Michelson factor (1 - D_12131) = (1 - e^{-4ix}), |C~| = 2|sin(2x)|.
  X2 = (1 - D_12131) * X1 (equal arms) -> TDI-1 lacks the |C~| factor.
"""
import numpy as np
import matplotlib.pyplot as plt


plt.rcParams.update({
    "font.family"        : "sans-serif",
    "font.sans-serif"    : ["Helvetica", "Arial", "DejaVu Sans"],
    "mathtext.fontset"   : "custom",
    "mathtext.rm"        : "Helvetica",
    "mathtext.it"        : "Helvetica:italic",
    "mathtext.bf"        : "Helvetica:bold",
    "axes.spines.top"    : True,
    "axes.spines.right"  : True,
    "axes.linewidth"     : 0.8,
    "xtick.direction"    : "in",
    "ytick.direction"    : "in",
    "xtick.major.size"   : 4,
    "ytick.major.size"   : 4,
    "xtick.minor.size"   : 2.5,
    "ytick.minor.size"   : 2.5,
    "xtick.major.width"  : 0.8,
    "ytick.major.width"  : 0.8,
    "xtick.labelsize"    : 15,
    "ytick.labelsize"    : 15,
    "axes.labelsize"     : 13,
    "legend.fontsize"    : 10,
    "legend.framealpha"  : 0.92,
    "legend.edgecolor"   : "#cccccc",
    "legend.handlelength": 2.0,
    "figure.dpi"         : 150,
})



# ---------------------------------------------------------------- constants
c     = 299792458.0          # m/s
lam   = 1064e-9              # m  (Nd:YAG)
nu0   = c / lam              # ~2.82e14 Hz  optical carrier
L     = 2.5e9               # m  LISA arm length
tau   = L / c              # one-way light time ~8.33 s

# ranging error
dL    = 1.0                 # m
B     = dL / c            # ranging bias in seconds (3.34 ns)

# representative differential arm-length rate for the TDI-1 flexing term
dv    = 10.0                 # m/s  (arm "breathing" rate; ~5-10 m/s over orbit)
dd_X1 = (dv / c) * (2 * L / c)   # first-order path mismatch [s] ~2.8e-7 s

# ---------------------------------------------------------------- frequency
f = np.logspace(-4, 0, 4000)   # 0.1 mHz .. 1 Hz
w = 2 * np.pi * f

# ---------------------------------------------------------------- shapes
# laser frequency-noise requirement [Hz/sqrt(Hz)]
Snu_half = 30.0 * np.sqrt(1 + (2e-3 / f) ** 4)
laser_hz = Snu_half                        # already a frequency noise [Hz/sqrt(Hz)]

# single-link secondary noises as equivalent laser frequency noise [Hz/sqrt(Hz)]
oms_hz = nu0 * 15e-12 * (w / c) * np.sqrt(1 + (2e-3 / f) ** 4)
acc_hz = nu0 * (3e-15 / (w * c)) * np.sqrt(1 + (0.4e-3 / f) ** 2) \
                                 * np.sqrt(1 + (f / 8e-3) ** 4)
floor_hz = np.sqrt(oms_hz ** 2 + acc_hz ** 2)

# ---------------------------------------------------------------- TDI residuals
Ctilde = 2 * np.abs(np.sin(4 * np.pi * f * L / c))   # |1 - e^{-4ix}|, x=2pi f L/c

# ranging-bias residual [Hz/sqrt(Hz)]
tdi1_rang = (2 * B) * w * laser_hz
tdi2_rang = Ctilde * (2 * B) * w * laser_hz

# TDI-1 flexing (uncancelled arm motion) -- the real TDI-1 limit
tdi1_flex = dd_X1 * w * laser_hz

color_extrapolated = "#d71b2f"   # (215, 27, 47)  red
color_measured     = "#295f24"   # (41, 95, 36)   green
color_anchor       = color_extrapolated
color_modulator    = "#821770"   # (130, 23, 112) magenta
color_delayline    = "#2d13b4"   # (45, 19, 180)  blue

# ---------------------------------------------------------------- plot

fig, ax = plt.subplots(figsize=(12, 6.4))

ax.loglog(f, laser_hz, color=color_extrapolated, lw=2.4,
          label=r"Pre-stabilised laser noise (30 Hz/$\sqrt{\rm Hz}$)")

ax.loglog(f, tdi1_flex, color="gray", lw=1.6, ls=":",
          label=r"TDI-1 residual, flexing limit ($\dot L\!\sim\!10\,$m/s)")
ax.loglog(f, tdi1_rang, color="gray", lw=1.8, ls="--",
          label="TDI-1 residual, 1 m ranging")
ax.loglog(f, tdi2_rang, color=color_measured, lw=2.0,
          label="TDI-2 residual, 1 m ranging")

# ax.loglog(f, acc_hz, color="#2ca02c", lw=1.3, alpha=0.9,
#           label=r"Acceleration noise (1 link)")
# ax.loglog(f, oms_hz, color="#17becf", lw=1.3, alpha=0.9,
#           label=r"OMS noise (1 link)")

ax.loglog(f, floor_hz, color=color_modulator, lw=2.4,
          label="Single-link noise floor (acc + OMS)")

ax.set_xlabel("Fourier frequency  [Hz]")
ax.set_ylabel(r"Frequency Noise ASD [Hz/$\sqrt{\rm Hz}$]")
#ax.set_title("Expected TDI performance")
ax.set_xlim(1e-4, 1e0)
ax.set_ylim(1e-10, 1e5)
ax.grid(True, which="major", color="#e0e0e0", linewidth=0.6, linestyle="--")
ax.grid(False, which="minor")

ax.legend(loc="center left", bbox_to_anchor=(0.8, 0.95), fontsize=12, frameon=True, fancybox=False)

fig.tight_layout()
fig.savefig("lisa_laser_tdi_budget_hz.png", dpi=300, transparent=True)
print("saved figure")

# ---------------------------------------------------------------- quick numbers
for ftest in (1e-3, 4e-3, 1e-2):
    i = np.argmin(np.abs(f - ftest))
    print(f"f={ftest*1e3:5.1f} mHz | laser={laser_hz[i]:.2e} "
          f"TDI1_rang={tdi1_rang[i]:.2e} TDI2_rang={tdi2_rang[i]:.2e} "
          f"TDI1_flex={tdi1_flex[i]:.2e} floor={floor_hz[i]:.2e} "
          f"| TDI2/floor={tdi2_rang[i]/floor_hz[i]:.1e}")