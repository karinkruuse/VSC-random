import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
from scipy.constants import Stefan_Boltzmann as sigma


matplotlib.rcParams['font.family'] = 'Helvetica'
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype']  = 42

# ── Palette ───────────────────────────────────────────────────────────────────
C1   = (215/255,  27/255,  47/255)   # red    — ambient
C2   = ( 45/255,  19/255, 180/255)   # blue   — shielded
C_HL = (130/255,  23/255, 112/255)   # purple — requirement
GRAY = (0.45, 0.45, 0.45)

# ── Geometry helpers ──────────────────────────────────────────────────────────
def cylinder_material_volume(radius, height, thickness):
    r_i = radius - thickness
    return np.pi * radius**2 * (height + 2*thickness) - np.pi * r_i**2 * height

def cylinder_mass(radius, height, thickness, density=2700):
    return density * cylinder_material_volume(radius, height, thickness)

def cylinder_outer_surface_area(radius, height, thickness):
    h_out = height + 2*thickness
    return 2*np.pi*radius*h_out + 2*np.pi*radius**2

# ── Tank parameters ───────────────────────────────────────────────────────────
tank_params = [
    (0.50, 0.50, 0.005, 8000),
    (0.3,  0.43, 0.002, 2700),
    (0.3,  0.38, 0.002, 2700),
    (0.3,  0.34, 0.002, 2700),
]
mass_ss_measured = 58.8  # kg

masses, areas, radii = [], [], []
for i, (d, h, t, rho) in enumerate(tank_params):
    r = d/2 + t
    mass = cylinder_mass(r, h, t, rho)
    area = cylinder_outer_surface_area(r, h, t)
    masses.append(mass_ss_measured if i == 0 else mass)
    areas.append(area)
    radii.append(r)

# ── Thermal parameters ────────────────────────────────────────────────────────
epsilon    = 0.05
epsilon_ss = 0.4
T0         = 297.7
c          = 900

beta_01 = 1/epsilon + (1 - epsilon_ss)/epsilon_ss * (radii[1]/radii[0])
beta_12 = 1/epsilon + (1 - epsilon)   /epsilon    * (radii[2]/radii[1])
beta_23 = 1/epsilon + (1 - epsilon)   /epsilon    * (radii[3]/radii[2])

C1m = c * masses[1]; C2m = c * masses[2]; C3m = c * masses[3]

T0c = T0**3
theta_01 = beta_01 / (4 * areas[1] * T0c * sigma)
theta_12 = beta_12 / (4 * areas[2] * T0c * sigma)
theta_23 = beta_23 / (4 * areas[3] * T0c * sigma)

tau_01 = C1m * theta_01
tau_12 = C2m * theta_12
tau_23 = C3m * theta_23

fc_01 = 1 / (2*np.pi*tau_01)
fc_12 = 1 / (2*np.pi*tau_12)
fc_23 = 1 / (2*np.pi*tau_23)

# ── Frequency axis ────────────────────────────────────────────────────────────
f     = np.logspace(-4, 0, 2000)
omega = 2*np.pi*f

# ── Ambient ASD (model from measurements) ────────────────────────────────────
f_slow = 3e-6
f_hvac = 1e-4
noise_floor = 0.021 / np.sqrt(1/60 / 2)
ambient_asd = noise_floor * np.sqrt(1 + (f_hvac/f)**2 + (f_slow/f)**2)

# ── Transfer function (uncoupled cascade) ─────────────────────────────────────
tau_list = [tau_01, tau_12, tau_23]
H = np.ones(len(omega), dtype=complex)
for tau in tau_list:
    H /= (1 + 1j*omega*tau)
H_mag = np.abs(H)

shielded_asd = H_mag * ambient_asd

# ── Requirement (50 µK flat) ──────────────────────────────────────────────────
req_asd = np.full_like(f, 50e-6)

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

ax.loglog(f, ambient_asd,  color=C1,   lw=2,   label="Ambient")
ax.loglog(f, shielded_asd, color=C_HL,   lw=2,   label="Shielded (3 layers)")
ax.loglog(f, req_asd,      color=(50/255, 50/255, 50/255), lw=1.8, ls='--', label="50 µK requirement")

# Cutoff frequency markers
#for fc, label in [(fc_01, r"$f_{c,01}$"), (fc_12, r"$f_{c,12}$"), (fc_23, r"$f_{c,23}$")]:
#    ax.axvline(fc, color=GRAY, lw=0.8, ls=':')
#    ax.text(fc*1.08, ax.get_ylim()[0]*3 if ax.get_ylim()[0] > 0 else 1e-12,
#            label, color=GRAY, fontsize=8, va='bottom')

# 1 mHz marker
#ax.axvline(1e-3, color='black', lw=1.0, ls='--', alpha=0.4)
#ax.text(1e-3*1.08, 1e-2, "1 mHz", color='black', fontsize=8, alpha=0.6, va='top')

ax.set_xlabel("Frequency  [Hz]", fontsize=11)
ax.set_ylabel(r"ASD  $[\mathrm{K}\,/\!\sqrt{\mathrm{Hz}}]$", fontsize=11)
ax.set_xlim(f[0], f[-1])

ax.grid(True, which='major', ls='--', lw=0.5, color='#cccccc')
ax.grid(True, which='minor', ls=':', lw=0.3, color='#e0e0e0')

# Re-draw cutoff labels now that ylim is settled
#ybot = ax.get_ylim()[0]
#for fc, label in [(fc_01, r"$f_{c,01}$"), (fc_12, r"$f_{c,12}$"), (fc_23, r"$f_{c,23}$")]:
#    ax.text(fc*1.08, ybot*1.5, label, color=GRAY, fontsize=8, va='bottom')

leg = ax.legend(frameon=True, framealpha=0.92, edgecolor='#cccccc',
                fontsize=10, loc='lower left')

# Parameter box (top right)
param_text = (
    f"SS  ε = {epsilon_ss},   Al  ε = {epsilon}\n"
    f"Al masses:  {masses[1]:.2f} / {masses[2]:.2f} / {masses[3]:.2f}  kg\n"
    f"$f_c$:  {fc_01*1e3:.2f} / {fc_12*1e3:.2f} / {fc_23*1e3:.2f}  mHz"
)
#ax.text(0.98, 0.97, param_text, transform=ax.transAxes,
#        fontsize=8, va='top', ha='right',
#        bbox=dict(boxstyle='round,pad=0.4', fc='white', ec='#cccccc', alpha=0.9))

ax.set_title("Thermal shielding performance", fontsize=12, fontweight='bold', pad=10)

plt.tight_layout()
plt.savefig("shielding.png", dpi=300, bbox_inches='tight')
print("Saved.")