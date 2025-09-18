import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.constants import Stefan_Boltzmann as sigma

# -------------------------------------------------
# Functions for geometry and mass
# -------------------------------------------------
def cylinder_surface_area(radius, height, thickness):
    """Return the *outer* surface area of a cylindrical shell [m^2]."""
    r_outer = radius
    h = height
    return 2*np.pi*r_outer*h + 2*np.pi*r_outer**2

def cylinder_mass(radius, height, thickness, density=2700):
    """Return mass of cylindrical shell [kg]."""
    r_outer = radius
    r_inner = r_outer - thickness
    h = height
    vol_outer = np.pi*r_outer**2*h
    vol_inner = np.pi*r_inner**2*h
    volume_shell = vol_outer - vol_inner
    return density * volume_shell

# -------------------------------------------------
# Simulation parameters
# -------------------------------------------------
fs = 1          # Sampling frequency [Hz]
T = 5_000_000   # Duration [s] (reduced for practicality)
N = int(fs * T)

amp = 1       # 100 mK fluctuation amplitude
noise = amp * np.random.randn(N)

# Welch ASD
nperseg = int(np.sqrt(N)) - 1
print(f"Using {nperseg} points per segment for Welch PSD.")
f_welch, psd_welch = welch(noise, fs=fs, nperseg=nperseg, noverlap=int(0.1*nperseg))
asd_welch = np.sqrt(psd_welch)

# -------------------------------------------------
# Shield parameters
# -------------------------------------------------
epsilon = 0.1
T = 294**3  # K^3, since later used in Stefan-Boltzmann approx
c = 900     # J/(kg K) for Al

height = 0.50  # m
thickness = 0.003  # m
density_al = 2700  # kg/m^3

# Radii of nested shields
radii = [0.25, 0.20, 0.185, 0.17]  # m (outer -> inner)

# Compute properties
masses = []
areas = []
for r in radii[1:]:
    m = cylinder_mass(r, height, thickness, density=density_al)
    a = cylinder_surface_area(r, height, thickness)
    masses.append(m)
    areas.append(a)

# Print results
for i, (m, a) in enumerate(zip(masses, areas), start=1):
    print(f"Shield {i}: mass = {m:.2f} kg, area = {a:.2f} m^2")

# -------------------------------------------------
# Thermal transfer function
# -------------------------------------------------
beta = (1-epsilon)/epsilon
beta_01 = 1/epsilon + beta*(radii[0]/radii[1])
beta_12 = 1/epsilon + beta*(radii[1]/radii[2])
beta_23 = 1/epsilon + beta*(radii[2]/radii[3])

C_1 = c*masses[0]
C_2 = c*masses[1]

theta_01 = beta_01 / (4*areas[0]*T*sigma)
theta_12 = beta_12 / (4*areas[1]*T*sigma)

tau_01 = C_1 * theta_01
tau_12 = C_2 * theta_12

print(f"tau_01 = {tau_01/60:.2f} min")
print(f"tau_12 = {tau_12/60:.2f} min")

H = np.abs(1/(1+1j*f_welch*tau_01)/(1+1j*f_welch*tau_12)/(1+1j*f_welch*tau_12))

# -------------------------------------------------
# Requirement line (white noise assumption)
# -------------------------------------------------
T_rms = 10e-6        # 10 µK RMS
req = T_rms / np.sqrt(fs/2)    # ASD [K/√Hz]

# -------------------------------------------------
# Plot
# -------------------------------------------------
plt.figure(figsize=(7,5))
plt.loglog(f_welch, asd_welch, label="Ambient T ASD", linewidth=2)
plt.loglog(f_welch, H*asd_welch, label="Shielded T ASD")
plt.hlines(req, f_welch[0], f_welch[-1], color='gray', linestyle='--', label="10 µK RMS → ASD")

plt.xlabel("Frequency [Hz]")
plt.ylabel("ASD [K/√Hz]")
plt.grid(True, ls="--")
plt.legend()

# Annotate parameters
param_text = (
    f"ε = {epsilon}\n"
    f"Height = {height:.2f} m\n"
    f"Thickness = {thickness*1e3:.1f} mm\n"
    f"Masses = {[f'{m:.2f}' for m in masses]} kg\n"
    f"τ₀₁ = {tau_01/60:.2f} min\n"
    f"τ₁₂ = {tau_12/60:.2f} min"
)
plt.text(0.02, 0.2, param_text, transform=plt.gca().transAxes,
         fontsize=8, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray"))

plt.tight_layout()
plt.savefig("thermal_shielding_epsilon005.png", dpi=400)
plt.show()
