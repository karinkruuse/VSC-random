import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.constants import Stefan_Boltzmann as sigma

def cylinder_material_volume(radius, height, thickness):
    """Return volume of material of a cylindrical shell [m^3]."""
    r_outer = radius
    r_inner = r_outer - thickness
    h_inner = height
    h_outer = height + 2*thickness  # include top/bottom plates
    vol_outer = np.pi * r_outer**2 * h_outer
    vol_inner = np.pi * r_inner**2 * h_inner
    return vol_outer - vol_inner

def cylinder_mass(radius, height, thickness, density=2700):
    """Return mass of cylindrical shell [kg]."""
    volume_shell = cylinder_material_volume(radius, height, thickness)
    return density * volume_shell

def cylinder_outer_surface_area(radius, height, thickness):
    """Return total outer surface area [m^2] including cylindrical wall and plates."""
    h_outer = height + 2*thickness
    return 2*np.pi*radius*h_outer + 2*np.pi*radius**2

# -------------------------------------------------
# Tank parameters: (inner_diameter, height, thickness, density)
# -------------------------------------------------
tank_params = [
    (0.50, 0.50, 0.005, 8000),
    (0.45, 0.40, 0.003, 2700),
    (0.40, 0.35, 0.003, 2700),
    (0.35, 0.30, 0.003, 2700)
]

# Lists to store masses and areas
masses = []
areas = []
radii = []

# Compute properties for each tank
for i, (d, h, t, density) in enumerate(tank_params, start=1):
    outer_radius = d / 2 + t  # outer radius
    vol = cylinder_material_volume(outer_radius, h, t)
    mass = cylinder_mass(outer_radius, h, t, density)
    area = cylinder_outer_surface_area(outer_radius, h, t)
    
    masses.append(mass)
    areas.append(area)
    radii.append(outer_radius)
    
    print(f"Tank {i}:")
    print(f"  Material volume = {vol:.6f} m^3 ({vol*1000:.2f} liters)")
    print(f"  Mass = {mass:.2f} kg")
    print(f"  Outer surface area = {area:.4f} m^2\n")



# Shield parameters
epsilon = 0.1
T = 294**3  # K^3, since later used in Stefan-Boltzmann approx
c = 900     # J/(kg K) for Al


temp2 = (1 - epsilon)/epsilon
temp1 = 1/epsilon

beta_01 = temp1 + ((1-0.5)/0.5)*(radii[0]/radii[1])
beta_12 = temp1 + temp2*(radii[1]/radii[2])
beta_23 = temp1 + temp2*(radii[2]/radii[3])

C_1 = c * masses[1]
C_2 = c * masses[2]
C_3 = c * masses[3]

theta_01 = beta_01 / (4 * areas[1] * T * sigma)
theta_12 = beta_12 / (4 * areas[2] * T * sigma)
theta_23 = beta_23 / (4 * areas[3] * T * sigma)

tau_01 = C_1 * theta_01
tau_12 = C_2 * theta_12
tau_23 = C_3 * theta_23


f = np.logspace(-4, 0, 1000)  # 0.1 mHz to 1 Hz

# Thermal requirement
T_rms = 10e-6
f_c = 2e-3

req_asd = T_rms * np.sqrt(1 + (f_c/f)**4)


T_ambient_rms = 0.5  # 100 mK
ambient_asd = np.ones_like(f) * T_ambient_rms


H = np.abs(1/(1+1j*f*tau_01) / (1+1j*f*tau_12) / (1+1j*f*tau_23))
#H_skip_inner = np.abs(1/(1+1j*f*tau_01) / (1+1j*f*tau_12))

plt.figure(figsize=(7,5))
plt.loglog(f, ambient_asd, label="Ambient T", linewidth=2)
plt.loglog(f, H*ambient_asd, label="Shielded T")
#plt.loglog(f, H_skip_inner*ambient_asd, label="Shielded T ASD (skip innermost)")
plt.loglog(f, req_asd, color='gray', linestyle='--', label="10 µK")
ymin, ymax = plt.ylim()
plt.vlines(0.001, ymin, ymax, color='black', linestyle='--', label='1 mHz limit')

plt.xlabel("Frequency [Hz]")
plt.ylabel("ASD [K/√Hz]")
plt.grid(True, ls="--")
plt.legend()

fc_01 = 1 / (2 * np.pi * tau_01)
fc_12 = 1 / (2 * np.pi * tau_12)
fc_23 = 1 / (2 * np.pi * tau_23)
param_text = (
    f"Aluminium ε = {epsilon}\n"
    f"Masses = {[f'{m:.2f}' for m in masses[1:4]]} kg\n"
    f"Cutoff f (01) = {fc_01*1e3:.2f} mHz\n"
    f"Cutoff f (12) = {fc_12*1e3:.2f} mHz\n"
    f"Cutoff f (23) = {fc_23*1e3:.2f} mHz"
)

plt.text(0.02, 0.2, param_text, transform=plt.gca().transAxes,
         fontsize=8, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray"))

plt.tight_layout()
plt.savefig("shielding.png", dpi=400)
plt.show()
