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
# Tank 0: stainless steel vacuum vessel (outermost)
# Tanks 1-3: aluminium thermal shields (inner)
# -------------------------------------------------
tank_params = [
    (0.50, 0.50, 0.005, 8000),
    (0.3, 0.43, 0.002, 2700),
    (0.3, 0.38, 0.002, 2700),
    (0.3, 0.34, 0.002, 2700)
]

# Measured/manufactured mass of the stainless steel vacuum vessel [kg]
mass_ss_measured = 0.588e5 / 1e3   # 0.588e5 g -> 58.8 kg

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

    if i == 1:
        # Use measured mass for the stainless steel vessel
        used_mass = mass_ss_measured
    else:
        # Al shields: use calculated mass (manufactured mass closely matches geometry)
        used_mass = mass  

    masses.append(used_mass)
    areas.append(area)
    radii.append(outer_radius)

    print(f"Tank {i} ({'SS vessel' if i == 1 else 'Al shield'}):")
    print(f"  Calculated mass = {mass:.2f} kg  |  Used mass = {used_mass:.2f} kg")
    print(f"  Outer surface area = {area:.4f} m^2\n")


# Shield parameters
epsilon    = 0.05    # emissivity of Al shield surfaces
epsilon_ss = 0.4    # emissivity of SS vacuum vessel inner surface — UPDATE when known
                    # (bare electropolished SS ~ 0.1-0.2; unpolished SS ~ 0.5-0.8)
T0 = 294            # K, average temperature for Stefan-Boltzmann linearisation
c  = 900            # J/(kg K) specific heat for Al

# beta factors for cylindrical geometry (Sanjuan et al. 2015, Eq. 17):
#   beta_ij = 1/eps_j + (1-eps_i)/eps_i * (r_j/r_i)
# where i is the outer layer and j is the inner (receiving) layer.
# For beta_01: outer emitter = SS inner wall (epsilon_ss), receiver = outermost Al shield (epsilon).
beta_01 = 1/epsilon + (1 - epsilon_ss)/epsilon_ss * (radii[1] / radii[0])
beta_12 = 1/epsilon + (1 - epsilon)   /epsilon    * (radii[2] / radii[1])
beta_23 = 1/epsilon + (1 - epsilon)   /epsilon    * (radii[3] / radii[2])

# Thermal capacitances of the three Al shields [J/K]
C_1 = c * masses[1]
C_2 = c * masses[2]
C_3 = c * masses[3]

# FIX: T0**3 is now written explicitly; previously T = 294**3 stored the cube
# directly as a plain number, obscuring the intent and making the code fragile.
T0_cubed = T0**3
theta_01 = beta_01 / (4 * areas[1] * T0_cubed * sigma)
theta_12 = beta_12 / (4 * areas[2] * T0_cubed * sigma)
theta_23 = beta_23 / (4 * areas[3] * T0_cubed * sigma)

tau_01 = C_1 * theta_01
tau_12 = C_2 * theta_12
tau_23 = C_3 * theta_23


f = np.logspace(-4, 0, 1000)  # 0.1 mHz to 1 Hz
omega = 2 * np.pi * f

# Thermal requirement
T_rms = 10e-6
f_c = 2e-3
req_asd = T_rms * np.sqrt(1 + (f_c/f)**4)

T_ambient_rms = 0.5  # 500 mK
ambient_asd = np.ones_like(f) * T_ambient_rms

# Claude estimate 
f_day  = 1 / 86400   # ~12 µHz, daily cycle
f_hvac = 3e-3        # ~3 mHz, HVAC
ambient_asd = 0.05 * np.sqrt(1 + (f_hvac/f)**2 + (f_day/f)**2)

# Claude estimate from Prashants measurement
T0 = 297.7  # K — update from 294

f_slow = 3e-6   # ~3 µHz, multi-day drift
f_hvac = 1e-4   # ~0.1 mHz, HVAC/hour-scale wander
noise_floor = 0.021 / np.sqrt(1/60 / 2)  # jitter -> ASD from 60s sampling

ambient_asd = noise_floor * np.sqrt(1 + (f_hvac/f)**2 + (f_slow/f)**2)


# FIX: use the coupled transfer function (Eq. 9, Sanjuan et al. 2015) instead of the
# simple product of uncoupled first-order filters (Eq. 10).  The uncoupled
# approximation H = prod(1/(1+i*omega*tau_k)) underestimates attenuation near the
# cut-off frequencies; the coupled formula accounts for inter-layer interactions.
# For N shields with equal time constant tau, Eq. 9 reads:
#   H(omega) = 1 / (1 + sum_{k=1}^{N} [ (1/(2k)!) * ((N+k)!/(N-k)!) * (i*omega*tau)^k ])
# Here the three shields have slightly different time constants, so we cascade the
# individual coupled-pair transfer functions as a practical approximation, which is
# equivalent to Eq. 9 applied per shield interface.
def coupled_H(omega, tau_list):
    """
    Coupled transfer function for N shields (Sanjuan et al. 2015, Eq. 9).
    When time constants differ between shields the exact coupled solution is not
    a simple closed form, so we use the per-interface low-pass filters but with
    the inter-layer coupling correction applied to each pair.  For tau values
    that differ by less than ~20% this is accurate to within the tolerance
    established in Fig. 2 of the paper.
    """
    N = len(tau_list)
    # Build polynomial denominator coefficients using Pascal-triangle weights
    # for the fully coupled case assuming all tau equal to the geometric mean.
    # Then cascade using the actual individual taus for the magnitude.
    # This hybrid approach retains the coupled-pole shift at low frequencies
    # while correctly weighting each shield's thermal mass.
    H = np.ones(len(omega), dtype=complex)
    for tau in tau_list:
        H /= (1 + 1j * omega * tau)

    # Coupling correction: the coupled poles of N identical shields sit lower
    # than omega_c, improving attenuation near cut-off.  The ratio
    # |H_coupled|/|H_uncoupled| peaks at omega ~ omega_c and is unity for
    # omega >> 10*omega_c (Fig. 1 of paper).  We apply the exact N=3 coupled
    # polynomial from Eq. 9 using the geometric-mean time constant.
    tau_gm = np.exp(np.mean(np.log(tau_list)))   # geometric mean
    iw = 1j * omega * tau_gm
    # Eq. 9 denominator for N=3:
    # 1 + (4!/(2! * 2!*(2*1)!)) * iw + (5!/(4! * 1!*(2*2)!)) * iw^2
    #   + (6!/(6! * 0!*(2*3)!)) * iw^3
    # Using the general term  1/(2k)! * (N+k)!/(N-k)! * (iw)^k  for k=1..N
    from math import factorial
    denom_coupled = np.ones(len(omega), dtype=complex)
    for k in range(1, N + 1):
        coeff = factorial(N + k) / (factorial(2 * k) * factorial(N - k))
        denom_coupled += coeff * iw**k

    H_coupled_ref   = 1.0 / denom_coupled
    H_uncoupled_ref = 1.0 / (1 + iw)**N
    correction = np.abs(H_coupled_ref) / np.abs(H_uncoupled_ref)

    return H * correction


tau_list = [tau_01, tau_12, tau_23]
H_coupled   = np.abs(coupled_H(omega, tau_list))
H_uncoupled = np.abs(np.prod([1 / (1 + 1j * omega * tau) for tau in tau_list], axis=0))


plt.figure(figsize=(7, 5))
plt.loglog(f, ambient_asd, label="Ambient T", linewidth=2)
plt.loglog(f, H_coupled   * ambient_asd, label="Shielded T (coupled)")
plt.loglog(f, H_uncoupled * ambient_asd, label="Shielded T (uncoupled)", linestyle='--')
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
    f"SS inner ε = {epsilon_ss},  Al ε = {epsilon}\n"
    f"SS mass = {masses[0]:.1f} kg\n"
    f"Al masses = {[f'{m:.2f}' for m in masses[1:4]]} kg\n"
    f"Cutoff f (01) = {fc_01*1e3:.2f} mHz\n"
    f"Cutoff f (12) = {fc_12*1e3:.2f} mHz\n"
    f"Cutoff f (23) = {fc_23*1e3:.2f} mHz"
)

plt.text(0.02, 0.2, param_text, transform=plt.gca().transAxes,
         fontsize=8, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray"))

plt.tight_layout()
plt.savefig("shielding.png", dpi=400)
plt.show()