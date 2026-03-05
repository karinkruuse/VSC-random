import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ── Raw data ──────────────────────────────────────────────────────────────────
deg   = np.array([149,150,155,160,165,170,180,190,194,
                   200,210,220,230,239,245,260,270,284], dtype=float)
trans = np.array([536,534,512,466,392,308,129,12.7,0.67,
                   18.15,149,333,481,539,513,302,121,0.03])
ref   = np.array([3.5,3.8,33,93.3,189,300,533,686,702,
                   679,511,267,72.5,3.85,30,304,543,703])

T = trans - 0.0
R = ref   - 0.2

# ── Physics model ─────────────────────────────────────────────────────────────
# HWP at angle phi rotates linear polarisation by 2*phi.
# After PBS:
#   T(phi) = (P_T/2)[1 + cos(4*phi + phi0)]
#   R(phi) = (P_R/2)[1 - cos(4*phi + phi0)]
# P_T != P_R because PBS has different efficiencies on each port.
# Both share the SAME phi0 — this is the key HWP test.
# Best figure of merit: T/(T+R) = 0.5*[1 + cos(4*phi + phi0)]
# which cancels PBS efficiency entirely.

def model_T(phi_deg, P_T, phi0_deg):
    return (P_T/2)*(1 + np.cos(4*np.radians(phi_deg) + np.radians(phi0_deg)))

def model_R(phi_deg, P_R, phi0_deg):
    return (P_R/2)*(1 - np.cos(4*np.radians(phi_deg) + np.radians(phi0_deg)))

def model_ratio(phi_deg, phi0_deg):
    return 0.5*(1 + np.cos(4*np.radians(phi_deg) + np.radians(phi0_deg)))

ratio = T / (T + R); ratio_f = T / (T + R)

p0 = [540, -600]
popt_T,     pcov_T     = curve_fit(model_T,     deg, T,     p0=p0,    maxfev=20000)
popt_R,     pcov_R     = curve_fit(model_R,     deg, R,     p0=p0,    maxfev=20000)
popt_ratio, pcov_ratio = curve_fit(model_ratio, deg, ratio, p0=[-600], maxfev=20000)

perr_T     = np.sqrt(np.diag(pcov_T))
perr_R     = np.sqrt(np.diag(pcov_R))
perr_ratio = np.sqrt(np.diag(pcov_ratio))

P0_T, phi0_T   = popt_T
P0_R, phi0_R   = popt_R
phi0_ratio     = popt_ratio[0]

print("="*55)
print("  HWP CHARACTERISATION RESULTS")
print("="*55)
print(f"\n  T fit:     P_T  = {P0_T:.1f} +/- {perr_T[0]:.1f} uW")
print(f"             phi0 = {phi0_T%360:.2f} +/- {perr_T[1]:.2f} deg (mod 360)")
print(f"\n  R fit:     P_R  = {P0_R:.1f} +/- {perr_R[0]:.1f} uW")
print(f"             phi0 = {phi0_R%360:.2f} +/- {perr_R[1]:.2f} deg (mod 360)")
print(f"\n  Ratio fit: phi0 = {phi0_ratio%360:.2f} +/- {perr_ratio[0]:.2f} deg (mod 360)")
print(f"\n  Phase agreement T vs R: Delta_phi0 = {abs((phi0_T-phi0_R)%360):.2f} deg")
print(f"  (Should be ~0 deg for a true HWP)")
print(f"\n  PBS efficiency ratio P_T/P_R = {P0_T/P0_R:.3f}")

T180_pred = model_T(180, *popt_T)
R180_pred = model_R(180, *popt_R)
print(f"\n  180 deg point:")
print(f"    T: measured={T[deg==180][0]:.1f}, predicted={T180_pred:.1f}, residual={T[deg==180][0]-T180_pred:.1f} uW")
print(f"    R: measured={R[deg==180][0]:.1f}, predicted={R180_pred:.1f}, residual={R[deg==180][0]-R180_pred:.1f} uW")

# ── Smooth curves ─────────────────────────────────────────────────────────────
phi_s = np.linspace(145, 290, 2000)
T_curve     = model_T(phi_s, *popt_T)
R_curve     = model_R(phi_s, *popt_R)
ratio_curve = model_ratio(phi_s, *popt_ratio)

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(11, 13))
fig.suptitle("HWP Characterisation  |  Linear input  →  HWP(φ)  →  PBS",
             fontsize=13, fontweight='bold', y=0.99)

cT='#1565C0'; cR='#B71C1C'; cFit='#1B1B1B'; cOut='#E65100'

ax = axes[0]
ax.plot(phi_s, T_curve, '-', color=cFit, lw=1.8,
        label=rf'Fit: $(P_T/2)[1+\cos(4\phi+\phi_0)]$   $P_T$={P0_T:.0f} µW, $\phi_0$={phi0_T%360:.1f}°')
ax.plot(deg, T, 'o', color=cT, ms=7, zorder=4, label='T data (used in fit)')
ax.set_ylabel('Transmitted power (µW)', fontsize=11)
ax.set_title('PBS Transmitted port')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3); ax.set_xlim(145, 290)

ax = axes[1]
ax.plot(phi_s, R_curve, '-', color=cFit, lw=1.8,
        label=rf'Fit: $(P_R/2)[1-\cos(4\phi+\phi_0)]$   $P_R$={P0_R:.0f} µW, $\phi_0$={phi0_R%360:.1f}°')
ax.plot(deg, R, 'o', color=cR, ms=7, zorder=4, label='R data (used in fit)')
ax.set_ylabel('Reflected power (µW)', fontsize=11)
ax.set_title('PBS Reflected port')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3); ax.set_xlim(145, 290)

ax = axes[2]
ax.plot(phi_s, ratio_curve, '-', color=cFit, lw=1.8,
        label=rf'Fit: $\frac{{1}}{{2}}[1+\cos(4\phi+\phi_0)]$   $\phi_0$={phi0_ratio%360:.1f}°')
ax.plot(deg, ratio, 'o', color='purple', ms=7, zorder=4, label='T/(T+R) data (fit)')
ax.axhline(0.5, color='gray', ls=':', lw=1, label='50%')
ax.set_xlabel('HWP rotation angle φ (°)', fontsize=11)
ax.set_ylabel('T / (T + R)', fontsize=11)
ax.set_title('Normalised ratio T/(T+R)  —  PBS-efficiency-free  [most reliable]')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3); ax.set_xlim(145, 290); ax.set_ylim(-0.05, 1.05)

plt.tight_layout(rect=[0,0,1,0.98])
plt.savefig('hwp_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print("\nPlot saved.")