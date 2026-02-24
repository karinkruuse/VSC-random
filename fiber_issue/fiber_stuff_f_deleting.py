import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares



# --- data (replace with yours) ---
degrees = np.array([0, 20, 40, 60, 80, 100, 120, 140, 160, 180], dtype=float)
P1_meas = np.array([208, 181,  80,  66, 172, 218, 124,  51, 109, 208], dtype=float)  # OUT1 meter1

# THIS Powermeter was accidentally set to 400 nm
# and the responsivity for that is 2, but for IR its 4.
P2_meas = 2*np.array([111, 119, 154, 161, 126, 108, 139, 164, 144, 110], dtype=float)  # OUT2 meter2





# --- data (replace with yours) ---
degrees = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 110, 130, 150, 170, 180], dtype=float)
P1_meas = np.array([778, 864, 871, 796, 681, 570, 517, 546, 641, 750, 836, 660, 511, 634, 748], dtype=float)  # OUT1 meter1

# THIS Powermeter was accidentally set to 400 nm
# and the responsivity for that is 2, but for IR its 4.
P2_meas = np.array([169, 41, 26, 135, 306, 467, 535, 481, 329, 157, 29, 303, 528, 331, 161], dtype=float)  # OUT2 meter2

theta = np.deg2rad(degrees)

# --------------------------------------------------------------------
# Convention:
#   Cs0 == 0  -> FIX Cs = 0.5 (50:50 on slow axis)
#   Cf0 == 0  -> FIX Cf = 0.5 (50:50 on fast axis)
#   otherwise -> FIT that parameter starting from Cs0/Cf0
# --------------------------------------------------------------------
Cs0 = 0.5   # set to 0 to FIX at 0.5, else e.g. 0.6 to fit starting near 0.6
Cf0 = 0.6   # example: fit Cf; set to 0.0 to FIX at 0.5

def predict(theta, P0, Cs, Cf, alpha0):
    alpha = 2*theta + alpha0
    c2 = np.cos(alpha)**2
    Ps = P0*c2
    Pf = P0*(1 - c2)
    out2 = Cs*Ps + Cf*Pf
    out1 = (1-Cs)*Ps + (1-Cf)*Pf
    return out1, out2

# build parameter vector depending on what we fit
names = ["P0", "alpha0", "x"]
p0 = [np.mean(P1_meas) + np.mean(P2_meas), 0.0, np.mean(P1_meas)/np.mean(P2_meas)]
lb = [0.0, -10*np.pi, 0.0]
ub = [np.inf, 10*np.pi, np.inf]

fit_Cs = (Cs0 != 0.0)
fit_Cf = (Cf0 != 0.0)

if fit_Cs:
    names.append("Cs")
    p0.append(Cs0)
    lb.append(0.0)
    ub.append(1.0)
if fit_Cf:
    names.append("Cf")
    p0.append(Cf0)
    lb.append(0.0)
    ub.append(1.0)

p0 = np.array(p0, float)
lb = np.array(lb, float)
ub = np.array(ub, float)

def unpack(p):
    d = dict(zip(names, p))
    P0 = d["P0"]
    alpha0 = d["alpha0"]
    x = d["x"]
    Cs = d["Cs"] if "Cs" in d else 0.5
    Cf = d["Cf"] if "Cf" in d else 0.5
    return P0, Cs, Cf, alpha0, x

def resid(p):
    P0, Cs, Cf, alpha0, x = unpack(p)
    out1, out2 = predict(theta, P0, Cs, Cf, alpha0)
    return np.r_[P1_meas - out1, x*P2_meas - out2]

res = least_squares(resid, p0, bounds=(lb, ub))
P0, Cs, Cf, alpha0, x = unpack(res.x)

print("Fit:")
print(f"  P0     = {P0:.6g}")
print(f"  Cs     = {Cs:.6g} {'(fixed 0.5)' if not fit_Cs else ''}")
print(f"  Cf     = {Cf:.6g} {'(fixed 0.5)' if not fit_Cf else ''}")
print(f"  alpha0 = {alpha0:.6g} rad ({np.rad2deg(alpha0):.3f} deg)")
print(f"  x      = {x:.6g}  (multiply meter2 readings by x to compare to meter1 units)")

# --- plot ---
th_f = np.linspace(theta.min(), theta.max(), 2000)
out1_fit, out2_fit = predict(th_f, P0, Cs, Cf, alpha0)

plt.figure()
plt.plot(degrees, P1_meas, "o", label="OUT1 meas (meter1)")
plt.plot(degrees, P2_meas, "o", label="OUT2 meas (meter2)")
plt.plot(np.rad2deg(th_f), out1_fit, "-", label="OUT1 fit")
plt.plot(np.rad2deg(th_f), out2_fit/x, "-", label="OUT2 fit (in meter2 units)")
plt.plot(np.rad2deg(th_f), out2_fit, "--", label="x·OUT2 fit (scaled to meter1 units)")
plt.plot(np.rad2deg(th_f), out1_fit + out2_fit, ":", label="OUT1+OUT2 (fit, meter1 units)")
plt.xlabel("HWP angle θ (deg)")
plt.ylabel("Power (arb.)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()