import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares



# --- data (replace with yours) ---
degrees = np.array([0, 20, 40, 60, 80, 100, 120, 140, 160, 180], dtype=float)
P1_meas = np.array([208, 181,  80,  66, 172, 218, 124,  51, 109, 208], dtype=float)  # OUT1 meter1

# THIS Powermeter was accidentally set to 400 nm
# and the responsivity for that is 2, but for IR its 4.
P2_meas = 2*np.array([111, 119, 154, 161, 126, 108, 139, 164, 144, 110], dtype=float)  # OUT2 meter2

theta = np.deg2rad(degrees)

# ------------------------------------------------------------
# Physics model (lossless coupler, two axes):
#   P_s = P0 cos^2(alpha),  P_f = P0 sin^2(alpha),  alpha = 2*theta + alpha0
#   OUT2 = Cs*P_s + Cf*P_f
#   OUT1 = (1-Cs)*P_s + (1-Cf)*P_f
# Meter mismatch: x * P2_meas = OUT2(true) in meter1 units
#
# NEW: force 50:50 splitting for ONE axis:
#   either Cs = 0.5 (slow axis forced 50/50) OR Cf = 0.5 (fast axis forced 50/50)
# ------------------------------------------------------------

FORCE_AXIS = "slow"   # "slow" or "fast"

def predict(theta, P0, Cs, Cf, alpha0):
    alpha = 2.0*theta + alpha0
    c2 = np.cos(alpha)**2
    s2 = 1.0 - c2
    Ps = P0 * c2
    Pf = P0 * s2
    out2 = Cs*Ps + Cf*Pf
    out1 = (1.0 - Cs)*Ps + (1.0 - Cf)*Pf
    return out1, out2

def residuals(p, theta, P1, P2, force_axis):
    # p = [P0, Cfree, alpha0, x]
    P0, Cfree, alpha0, x = p

    if force_axis == "slow":
        Cs, Cf = 0.5, Cfree
    elif force_axis == "fast":
        Cs, Cf = Cfree, 0.5
    else:
        raise ValueError("FORCE_AXIS must be 'slow' or 'fast'")

    out1_pred, out2_pred = predict(theta, P0, Cs, Cf, alpha0)

    r1 = P1 - out1_pred
    r2 = x*P2 - out2_pred
    return np.concatenate([r1, r2])

# --- initial guesses ---
P0_0 = np.mean(P1_meas) + np.mean(P2_meas)          # rough total-ish (arb)
Cfree_0 = 0.5                                       # start near 50/50
alpha0_0 = 0.0
x_0 = np.mean(P1_meas) / np.mean(P2_meas)           # rough meter gain ratio

p0 = np.array([P0_0, Cfree_0, alpha0_0, x_0], dtype=float)

# bounds: P0>0, Cfree in [0,1], alpha0 free-ish, x>0
lb = np.array([0.0, 0.0, -10*np.pi, 0.0])
ub = np.array([np.inf, 1.0,  10*np.pi, np.inf])

res = least_squares(residuals, p0, bounds=(lb, ub), args=(theta, P1_meas, P2_meas, FORCE_AXIS))
P0, Cfree, alpha0, x = res.x

if FORCE_AXIS == "slow":
    Cs, Cf = 0.5, Cfree
else:
    Cs, Cf = Cfree, 0.5

print("Fit (meter1 defines the arb units):")
print(f"  FORCE_AXIS = {FORCE_AXIS}  ->  {'Cs=0.5' if FORCE_AXIS=='slow' else 'Cf=0.5'}")
print(f"  P0     = {P0:.6g}")
print(f"  Cs     = {Cs:.6g}")
print(f"  Cf     = {Cf:.6g}")
print(f"  alpha0 = {alpha0:.6g} rad  ({np.rad2deg(alpha0):.3f} deg)")
print(f"  x      = {x:.6g}   (multiply meter2 OUT2 readings by x to compare to meter1 units)")

# --- plot ---
th_f = np.linspace(theta.min(), theta.max(), 1000)
out1_fit, out2_fit = predict(th_f, P0, Cs, Cf, alpha0)



plt.figure()
plt.plot(degrees, P1_meas, "o", label="OUT1 meas (meter1)")
plt.plot(degrees, P2_meas, "o", label="OUT2 meas (meter2)")
plt.plot(np.rad2deg(th_f), out1_fit, "-", label="OUT1 fit")
plt.plot(np.rad2deg(th_f), out2_fit/x, "-", label="OUT2 fit (in meter2 units)")
plt.plot(np.rad2deg(th_f), out2_fit, "--", label="x·OUT2 fit (scaled to meter1 units)")
plt.plot(np.rad2deg(th_f), out1_fit+out2_fit, ":", label="sum of fits")
plt.xlabel("HWP angle θ (deg)")
plt.ylabel("Power (arb.)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()