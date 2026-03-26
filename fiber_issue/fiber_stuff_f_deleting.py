import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares

# =============================================================================
# DATA
# =============================================================================
degrees = np.array([
    244, 245, 250, 255, 260, 270, 280, 290, 300, 310,
    320, 330, 340, 350, 360, 370, 380, 390, 400, 410
], dtype=float)
# --- without kapton (label on fiber, NOT in optical path) ---
P1_meas = np.array([
     236, 238, 252, 259, 249, 199, 122, 48, 14.9, 37.6,
     108.9, 189, 244, 245, 198, 119, 45, 12, 31, 95
 ], dtype=float)
P2_meas = np.array([
     261, 260, 249, 247, 254, 286, 339, 388, 409, 389,
     339, 284, 246, 240, 271, 325, 370, 388, 369, 326], dtype=float)
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

# =============================================================================
# PHYSICS MODEL
# =============================================================================
# Jones vector of elliptically polarized input:  E_in = [cos(eps), i*sin(eps)]
# HWP at mechanical angle phi rotates it. Power per fiber axis after HWP:
#
#   Ps = P0/2 * (1 + cos(4*phi) * cos(2*eps))   <- slow axis
#   Pf = P0/2 * (1 - cos(4*phi) * cos(2*eps))   <- fast axis
#
# eps=0: linear input, full modulation
# eps=pi/4: circular input, zero modulation (flat outputs)
#
# PDL: fast axis transmission Tf = 1 - pdl  (slow axis = 1)
# Coupler: fraction to Tap = Cs (slow), Cf (fast)
#
#   P_signal = (1-Cs)*Ps + (1-Cf)*Tf*Pf
#   P_tap    =    Cs *Ps +    Cf *Tf*Pf

def predict(theta, P0, Cs, Cf, alpha0, pdl, eps):
    phi     = theta + alpha0 / 2
    cos2eps = np.cos(2 * 0)
    Ps = P0 * (1 + np.cos(4 * phi) * cos2eps) / 2
    Pf = P0 * (1 - np.cos(4 * phi) * cos2eps) / 2
    Tf = 1- 0.17#1.0 - pdl
    P_signal = (1 - Cs) * Ps + (1 - Cf) * Tf * Pf
    P_tap    =       Cs  * Ps +       Cf  * Tf * Pf
    return P_signal, P_tap

# =============================================================================
# FIT CONFIGURATION
# Set to 0.0 to FIX a parameter at its default value (see `defaults` dict).
# =============================================================================
Cs0  = 0.5    # slow axis coupling -> Tap   (0.0 = fix at 0.5)
Cf0  = 0.8    # fast axis coupling -> Tap   (0.0 = fix at 0.5)
pdl0 = 0.1    # PDL                         (0.0 = fix, no PDL)
eps0 = 0.05   # ellipticity angle (rad)     (0.0 = fix, linear input)

# =============================================================================
# BUILD PARAMETER VECTOR DYNAMICALLY
# =============================================================================
defaults = {"Cs": 0.5, "Cf": 0.5, "pdl": 0.0, "eps": 0.0}
config   = {"Cs": Cs0,  "Cf": Cf0,  "pdl": pdl0, "eps": eps0}

names  = ["P0", "alpha0"]
p0_vec = [np.mean(P1_meas + P2_meas), 0.0]
lb_vec = [0.0,  -10*np.pi]
ub_vec = [np.inf, 10*np.pi]

for name in ["Cs", "Cf", "pdl", "eps"]:
    if config[name] != 0.0:
        names.append(name)
        p0_vec.append(config[name])
        if name == "eps":
            lb_vec.append(-np.pi/4);  ub_vec.append(np.pi/4)
        else:
            lb_vec.append(0.0);       ub_vec.append(1.0)

p0_vec = np.array(p0_vec, float)
lb_vec = np.array(lb_vec, float)
ub_vec = np.array(ub_vec, float)

def unpack(p):
    d = {**defaults, **dict(zip(names, p))}
    return d["P0"], d["Cs"], d["Cf"], d["alpha0"], d["pdl"], d["eps"]

def resid(p):
    P0, Cs, Cf, alpha0, pdl, eps = unpack(p)
    s, t = predict(theta, P0, Cs, Cf, alpha0, pdl, eps)
    return np.r_[P1_meas - s, P2_meas - t]

res = least_squares(resid, p0_vec, bounds=(lb_vec, ub_vec))
P0, Cs, Cf, alpha0, pdl, eps = unpack(res.x)
Tf = 1.0 - pdl
fit_flags = {n: (config.get(n, 0.0) != 0.0) for n in ["Cs","Cf","pdl","eps"]}

# =============================================================================
# PRINT RESULTS
# =============================================================================
print("=" * 52)
print("FIT RESULTS")
print("=" * 52)
print(f"  P0     = {P0:.4g} uW")
print(f"  alpha0 = {alpha0:.4g} rad  ({np.rad2deg(alpha0):.2f} deg)")
print(f"  Cs     = {Cs:.5f}  {'(fitted)' if fit_flags['Cs']  else '(fixed 0.5)'}")
print(f"  Cf     = {Cf:.5f}  {'(fitted)' if fit_flags['Cf']  else '(fixed 0.5)'}")
print(f"  pdl    = {pdl:.5f}  Tf={Tf:.5f}  {'(fitted)' if fit_flags['pdl'] else '(fixed: no PDL)'}")
print(f"  eps    = {eps:.5f} rad  ({np.rad2deg(eps):.3f} deg)  {'(fitted)' if fit_flags['eps'] else '(fixed: linear)'}")
print()
print("DERIVED")
print(f"  cos(2*eps) = {np.cos(2*eps):.5f}  (modulation depth scaling)")
print(f"  Slow: {(1-Cs)*100:.1f}% Signal / {Cs*100:.1f}% Tap  |  {10*np.log10(Cs/(1-Cs)):+.2f} dB")
print(f"  Fast: {(1-Cf)*100:.1f}% Signal / {Cf*100:.1f}% Tap  |  {10*np.log10(Cf/(1-Cf)):+.2f} dB")
print(f"  PDL (fast vs slow): {-10*np.log10(Tf):.3f} dB")
s_pred, t_pred = predict(theta, P0, Cs, Cf, alpha0, pdl, eps)
rms_s = np.sqrt(np.mean((P1_meas - s_pred)**2))
rms_t = np.sqrt(np.mean((P2_meas - t_pred)**2))
print(f"  RMS residuals: Signal={rms_s:.2f} uW,  Tap={rms_t:.2f} uW")

# =============================================================================
# PLOT
# =============================================================================
c_purple = (130/255, 23/255, 112/255)
c_green  = (41/255, 95/255, 36/255)
c_blue   = (0.3, 0.4, 0.7)

th_f = np.linspace(theta.min(), theta.max(), 2000)
s_fit, t_fit = predict(th_f, P0, Cs, Cf, alpha0, pdl, eps)

fig, ax = plt.subplots(1, 1, figsize=(6, 4), sharex=True)
\
ax.plot(degrees, P1_meas,                "o",  color=c_green,  label="Signal out (data)")
ax.plot(degrees, P2_meas,                "o",  color=c_purple, label="Tap out (data)")
ax.plot(np.rad2deg(th_f), s_fit,         "-",  color=c_green,  label="Signal fit")
ax.plot(np.rad2deg(th_f), t_fit,         "-",  color=c_purple, label="Tap fit")
ax.plot(degrees, P1_meas + P2_meas,      "o",  color=c_blue,   label="Signal+Tap (data)", alpha=0.6)
ax.plot(np.rad2deg(th_f), s_fit + t_fit, "--", color=c_blue,   label="Signal+Tap (fit)",  alpha=0.8)
ax.set_ylabel("Power (µW)")
ax.grid(True)
ax.legend(fontsize=8)


txt = (f"$C_s={Cs:.3f}$,  $C_f={Cf:.3f}$\n"
       f"PDL $= {-10*np.log10(Tf):.2f}$ dB")
ax.text(0.7, 0.9, txt, transform=ax.transAxes, fontsize=9,
        verticalalignment='bottom',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
"""

txt = (f"$C_s={Cs:.3f}$,  $C_f={Cf:.3f}$\n"
       f"PDL $= {-10*np.log10(Tf):.2f}$ dB\n"
       f"$\\epsilon = {np.rad2deg(eps):.2f}°$  "
       f"[$\\cos 2\\epsilon={np.cos(2*eps):.4f}$]")
ax.text(0.02, 0.05, txt, transform=ax.transAxes, fontsize=9,
        verticalalignment='bottom',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
"""
"""
ax2 = axes[1]
ax2.axhline(0, color="k", lw=0.8)
ax2.plot(degrees, P1_meas - s_pred, "o", color=c_green,  label="Signal residual")
ax2.plot(degrees, P2_meas - t_pred, "o", color=c_purple, label="Tap residual")
ax2.set_ylabel("Residual (µW)")
ax2.set_xlabel("HWP angle θ (deg)")
ax2.grid(True)
ax2.legend(fontsize=8)
"""
plt.tight_layout()
plt.savefig("fiber_w_kapton.png", dpi=400)
print("Plot saved.")