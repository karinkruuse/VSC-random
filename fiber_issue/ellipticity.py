import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares

# -----------------------------
# Your data (as given)
# -----------------------------
bg_P1 = 0.24
bg_P2 = 0.38

deg = np.array([0,10,20,30,40,50,60,65,70,80,90,100,110,120,130,140,150,160,170,180], dtype=float)

P1 = np.array([501,403,356,388,483,558,676,688,679,603,486,374,333,370,475,591,674,683,618,509], dtype=float)
P2 = np.array([197,293,340,308,214,101.5,24.9,12.9,21.8,95.8,210,320,361,325,222,108.4,27,18,82,190], dtype=float)

# background subtraction (clip at 0 just in case)
P1 = np.clip(P1 - bg_P1, 0, None)
P2 = np.clip(P2 - bg_P2, 0, None)

# -----------------------------
# Build a robust "analyzed intensity" trace
# -----------------------------
Itot = P1 + P2
# Avoid divide-by-zero (shouldn't happen here, but don't be a hero)
Itot = np.clip(Itot, 1e-12, None)

# Use normalized power in one PBS port -> cancels power drift / detector gain to 1st order
I = P1 / Itot   # in [0,1] ideally

theta = np.deg2rad(deg)

# -----------------------------
# Model: rotating QWP => harmonics at 2θ and 4θ
# Include an unknown QWP angle offset theta0
# I(θ) = 0.5*(A + B sin(2(θ+θ0)) + C cos(4(θ+θ0)) + D sin(4(θ+θ0)))
# -----------------------------
def model(params, th):
    A, B, C, D, theta0 = params
    x = th + theta0
    return 0.5 * (A + B*np.sin(2*x) + C*np.cos(4*x) + D*np.sin(4*x))

def residuals(params, th, I_meas):
    return model(params, th) - I_meas

# Initial guess:
A0 = 2*np.mean(I)
B0 = 0.0
C0 = 0.0
D0 = 0.0
theta0_0 = 0.0  # rad

p0 = np.array([A0, B0, C0, D0, theta0_0], dtype=float)

# Optional bounds:
# A is ~2*mean(I) (so around 1), but keep wide.
# theta0: only defined modulo 90° for a QWP in this Fourier form; bound to ±90° to keep it sane.
lb = np.array([-10, -10, -10, -10, -np.deg2rad(90)], dtype=float)
ub = np.array([+10, +10, +10, +10, +np.deg2rad(90)], dtype=float)

res = least_squares(residuals, p0, bounds=(lb, ub), args=(theta, I))
A, B, C, D, theta0 = res.x

# Wrap theta0 to a nice degree value
theta0_deg = np.rad2deg(theta0)
# bring to [-90, 90)
theta0_deg = (theta0_deg + 90) % 180 - 90

# -----------------------------
# Map fit coeffs -> Stokes
# For this rotating-QWP + fixed analyzer model:
# S0 = A - C
# S1 = 2C
# S2 = 2D
# S3 = B
# (Overall scale cancels when you normalize, so using I=P1/(P1+P2) is fine.)
# -----------------------------
S0 = A - C
S1 = 2*C
S2 = 2*D
S3 = B

# Normalized Stokes
s1 = S1 / S0
s2 = S2 / S0
s3 = S3 / S0

DoP = np.sqrt(s1**2 + s2**2 + s3**2)

# Ellipse parameters
# ellipticity angle chi = 0.5 * asin(s3)
# axis ratio b/a = |tan(chi)|  (minor/major)
chi = 0.5 * np.arcsin(np.clip(s3, -1, 1))
chi_deg = np.rad2deg(chi)
minor_over_major = np.abs(np.tan(chi))

# Orientation (azimuth) psi = 0.5 * atan2(s2, s1)
psi = 0.5 * np.arctan2(s2, s1)
psi_deg = (np.rad2deg(psi) + 90) % 180 - 90  # wrap to [-90, 90)

# -----------------------------
# Print results
# -----------------------------
print("=== Fit coefficients (normalized-port model) ===")
print(f"A={A:+.6f}, B={B:+.6f}, C={C:+.6f}, D={D:+.6f}")
print(f"QWP angle offset theta0 = {theta0_deg:+.3f} deg")

print("\n=== Stokes (up to scale) ===")
print(f"S0={S0:+.6f}, S1={S1:+.6f}, S2={S2:+.6f}, S3={S3:+.6f}")

print("\n=== Normalized Stokes ===")
print(f"s1={s1:+.6f}, s2={s2:+.6f}, s3={s3:+.6f}")
print(f"DoP = {DoP:.6f}   (should be ≤ 1)")

print("\n=== Polarization ellipse ===")
print(f"psi (orientation) = {psi_deg:+.3f} deg")
print(f"chi (ellipticity angle) = {chi_deg:+.3f} deg")
print(f"ellipticity minor/major = {minor_over_major:.6f}")

# -----------------------------
# Plots (data vs fit, residuals)
# -----------------------------
th_fine = np.linspace(theta.min(), theta.max(), 1000)
I_fit = model(res.x, theta)
I_fine = model(res.x, th_fine)

plt.figure()
plt.plot(deg, I, "o", label="Measured: P1/(P1+P2)")
plt.plot(np.rad2deg(th_fine), I_fine, "-", label="Fit")
plt.xlabel("QWP angle (deg)")
plt.ylabel("Normalized port power")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

plt.figure()
plt.plot(deg, I_fit - I, "o-")
plt.axhline(0, linewidth=1)
plt.xlabel("QWP angle (deg)")
plt.ylabel("Residual (fit - data)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()