import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares



# --- data (replace with yours) ---
degrees = np.array([0, 20, 40, 60, 80, 100, 120, 140, 160, 180], dtype=float)
# Need to check if white and read
red_out = np.array([208, 181,  80,  66, 172, 218, 124,  51, 109, 208], dtype=float)  # OUT1 meter1

# THIS Powermeter was accidentally set to 400 nm
# and the responsivity for that is 2, but for IR its 4.
white_out = 2*np.array([111, 119, 154, 161, 126, 108, 139, 164, 144, 110], dtype=float)  # OUT2 meter2





# --- data (replace with yours) ---
degrees = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 110, 130, 150, 170, 180], dtype=float)

# the one wo kapton, 24th of Feb, input on blue
white_out = np.array([778, 864, 871, 796, 681, 570, 517, 546, 641, 750, 836, 660, 511, 634, 748], dtype=float)  # OUT1 meter1
red_out = np.array([169, 41, 26, 135, 306, 467, 535, 481, 329, 157, 29, 303, 528, 331, 161], dtype=float)  # OUT2 meter2

# --- data (replace with yours) ---
degrees = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180], dtype=float)
# the one witout kapton, 25th of Feb, input on white
white_out = np.array([99,16,7,61,156,254,304,285,209,100,23,57,252,288,101], dtype=float)
red_out = np.array([426,480,488,455,392,328,294,303,353,425,476,458,331,304,425], dtype=float)
# the one with kapton, 25th of Feb, input on white
white_out = np.array([135, 75,64,109,190,267,301,278,211,131,73,109,259,282,136], dtype=float)
red_out = np.array([378,415,423,396,346,298,275,289,329,380,417,397,304,288,378], dtype=float)

theta = np.deg2rad(degrees)

# --------------------------------------------------------------------
# Manual ellipticity BEFORE the HWP: a single phase retardance (rad)
# delta=0 -> purely linear input (your old model)
# delta ~ few degrees can happen with mirror trains etc.
# --------------------------------------------------------------------
DELTA_PRE = np.deg2rad(140.0)   # <-- change this manually

# --------------------------------------------------------------------
# Convention:
#   Cs0 == 0  -> FIX Cs = 0.5
#   Cf0 == 0  -> FIX Cf = 0.5
#   otherwise -> FIT starting from Cs0/Cf0
# --------------------------------------------------------------------
Cs0 = 0.5
Cf0 = 0.6

def predict(theta, P0, Cs, Cf, alpha0, delta_pre=0.0):
    """
    Input field before HWP has a fixed ellipticity modeled as a relative phase
    between the coupler's (slow, fast) basis components.

    We take a simple fixed-amplitude input (equal components) with phase delta_pre:
        Ein = [1, exp(i*delta_pre)] / sqrt(2)
    Then apply the HWP rotated by (theta + alpha0) in the coupler basis.
    Then compute powers on slow/fast axes and apply coupler splitting.

    delta_pre=0 => linear at 45° in the coupler basis.
    If you want a different fixed amplitude ratio, tell me and I'll add one number.
    """
    th = theta + alpha0

    # HWP Jones matrix in (slow,fast) basis: J = R(th) diag(1,-1) R(-th)
    c = np.cos(th)
    s = np.sin(th)
    J11 =  c*c - s*s
    J12 = 2*c*s
    J21 = 2*c*s
    J22 =  s*s - c*c  # = -(c*c - s*s)

    # input Jones vector (fixed ellipticity before HWP)
    Ein_s = 1/np.sqrt(2)
    Ein_f = np.exp(1j*delta_pre)/np.sqrt(2)

    # field after HWP
    Es = J11*Ein_s + J12*Ein_f
    Ef = J21*Ein_s + J22*Ein_f

    Ps = P0 * (np.abs(Es)**2)
    Pf = P0 * (np.abs(Ef)**2)

    out2 = Cs*Ps + Cf*Pf
    out1 = (1-Cs)*Ps + (1-Cf)*Pf
    return out1, out2

# build parameter vector depending on what we fit
names = ["P0", "alpha0", "x"]
p0 = [np.mean(white_out) + np.mean(red_out), 0.0, np.mean(white_out)/np.mean(red_out)]
lb = [0.0, -10*np.pi, 0.0]
ub = [np.inf, 10*np.pi, np.inf]

fit_Cs = (Cs0 != 0.0)
fit_Cf = (Cf0 != 0.0)

if fit_Cs:
    names.append("Cs"); p0.append(Cs0); lb.append(0.0); ub.append(1.0)
if fit_Cf:
    names.append("Cf"); p0.append(Cf0); lb.append(0.0); ub.append(1.0)

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
    out1, out2 = predict(theta, P0, Cs, Cf, alpha0, delta_pre=DELTA_PRE)
    return np.r_[white_out - out1, x*red_out - out2]

res = least_squares(resid, p0, bounds=(lb, ub))
P0, Cs, Cf, alpha0, x = unpack(res.x)

print("Fit (manual ellipticity before HWP):")
print(f"  DELTA_PRE = {DELTA_PRE:.6g} rad ({np.rad2deg(DELTA_PRE):.3f} deg)")
print(f"  P0     = {P0:.6g}")
print(f"  Cs     = {Cs:.6g} {'(fixed 0.5)' if not fit_Cs else ''}")
print(f"  Cf     = {Cf:.6g} {'(fixed 0.5)' if not fit_Cf else ''}")
print(f"  alpha0 = {alpha0:.6g} rad ({np.rad2deg(alpha0):.3f} deg)")
print(f"  x      = {x:.6g}  (multiply meter2 readings by x to compare to meter1 units)")

# --- plot ---
th_f = np.linspace(theta.min(), theta.max(), 2000)
out1_fit, out2_fit = predict(th_f, P0, Cs, Cf, alpha0, delta_pre=DELTA_PRE)

plt.figure()
plt.plot(degrees, white_out, "o", label="OUT1 meas (meter1)")
plt.plot(degrees, red_out, "o", label="OUT2 meas (meter2)")
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