import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares

# --- data ---
degrees = np.array([
    244, 245, 250, 255, 260, 270, 280, 290, 300, 310,
    320, 330, 340, 350, 360, 370, 380, 390, 400, 410
], dtype=float)

# --- without kapton ---
P1_meas = np.array([
    236, 238, 252, 259, 249, 199, 122, 48, 14.9, 37.6,
    108.9, 189, 244, 245, 198, 119, 45, 12, 31, 95
], dtype=float)

P2_meas = np.array([
    261, 260, 249, 247, 254, 286, 339, 388, 409, 389,
    339, 284, 246, 240, 271, 325, 370, 388, 369, 326
], dtype=float)
# --- with kapton ---
P1_meas = np.array([
    214, 219, 238, 247, 243, 205, 142, 81.6, 54.9, 72.8,
    126, 187, 229, 232, 193, 131, 76, 52.6, 69, 121
], dtype=float)

P2_meas = np.array([
    253, 245, 236, 230, 233, 255, 296, 330, 341, 323,
    289, 248, 222, 222, 247, 286, 320, 333, 318, 286
], dtype=float)


theta = np.deg2rad(degrees)
c_purple = (130/255, 23/255, 112/255)
c_green  = (41/255, 95/255, 36/255)

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
plt.plot(degrees, P1_meas, "o", label="Signal out", color=c_green)
plt.plot(degrees, P2_meas, "o", label="Tap out", color=c_purple)
plt.plot(np.rad2deg(th_f), out1_fit, "-", label="fit", color=c_green)
plt.plot(np.rad2deg(th_f), out2_fit/x, "-", label="fit", color=c_purple)
plt.plot(degrees, P1_meas+P2_meas, "o", label="Signal + Tap")
#plt.plot(np.rad2deg(th_f), out2_fit, "--", label="x·OUT2 fit (scaled to meter1 units)")
#plt.plot(np.rad2deg(th_f), out1_fit + out2_fit, ":", label="OUT1+OUT2 (fit, meter1 units)")
plt.xlabel("HWP angle θ (deg)")
plt.ylabel("Power (uW)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("w_kapton.png", dpi=400)