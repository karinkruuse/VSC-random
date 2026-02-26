import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares

# -------------------------
# Paste your datasets here
# -------------------------
deg_A = np.array([0,10,20,30,40,45,48,50,55,60,65,70,80,90], dtype=float)
P1_A  = np.array([363,380,467,582,677,699,703,700,682,646,590,535,413,344], dtype=float)
P2_A  = np.array([367,350,266,156,64.4,43,38.6,40.4,57.7,91.7,145,188,315,381], dtype=float)

deg_B = np.array([0,10,20,30,40,45,50,55,60,66,70,75,80,90], dtype=float)
P1_B  = np.array([157,262,317,255,206,150,94.4,47.7,15.3,2.3,10.4,39.6,91,211], dtype=float)
P2_B  = np.array([548,439,385,407,494,548,602,648,680,693,685,656,604,486], dtype=float)


def model_I(theta, A, B, C, D, theta0, Ioff):
    # theta, theta0 in radians
    t = theta - theta0
    return Ioff + 0.5*(A + B*np.sin(2*t) + C*np.cos(4*t) + D*np.sin(4*t))

def fit_rotating_qwp(theta_deg, I_meas):
    theta = np.deg2rad(theta_deg)

    # initial guesses
    Ioff0 = np.min(I_meas) * 0.0
    A0 = 2*np.mean(I_meas)               # because mean(I) ~ Ioff + 0.5*A
    B0 = 0.0
    C0 = 0.0
    D0 = 0.0
    theta00 = 0.0

    x0 = np.array([A0, B0, C0, D0, theta00, Ioff0], dtype=float)

    def resid(x):
        A,B,C,D,theta0,Ioff = x
        return model_I(theta, A,B,C,D,theta0,Ioff) - I_meas

    # mild bounds to keep things sane (optional)
    # A roughly positive; theta0 anywhere
    lb = np.array([-np.inf, -np.inf, -np.inf, -np.inf, -np.pi, -np.inf])
    ub = np.array([ np.inf,  np.inf,  np.inf,  np.inf,  np.pi,  np.inf])

    res = least_squares(resid, x0, bounds=(lb,ub))
    A,B,C,D,theta0,Ioff = res.x

    # Paper mapping
    S0 = A - C
    S1 = 2*C
    S2 = 2*D
    S3 = B

    # Normalize
    s1 = S1/S0
    s2 = S2/S0
    s3 = S3/S0
    DoP = np.sqrt(s1*s1 + s2*s2 + s3*s3)

    # Ellipticity minor/major from chi = 0.5*asin(s3)
    s3c = np.clip(s3, -1.0, 1.0)
    chi = 0.5*np.arcsin(s3c)
    ell = abs(np.tan(chi))

    return dict(
        A=A,B=B,C=C,D=D,theta0=theta0,Ioff=Ioff,
        S0=S0,S1=S1,S2=S2,S3=S3,
        s1=s1,s2=s2,s3=s3,DoP=DoP,chi=chi,ell=ell,
        success=res.success, cost=res.cost
    )

def analyze(name, deg, P1, P2, port="P1"):
    I = P1 if port.upper()=="P1" else P2
    out = fit_rotating_qwp(deg, I)

    print(f"\n=== {name} | analyzer={port} (RAW µW) ===")
    print(f"theta0 = {np.rad2deg(out['theta0']):+.2f} deg, Ioff = {out['Ioff']:+.3g} µW")
    print(f"A={out['A']:+.6g}, B={out['B']:+.6g}, C={out['C']:+.6g}, D={out['D']:+.6g}")
    print(f"Normalized Stokes: s1={out['s1']:+.6f}, s2={out['s2']:+.6f}, s3={out['s3']:+.6f}")
    print(f"DoP = {out['DoP']:.6f}  (should be ≤ 1; lasers should be near 1)")
    print(f"Ellipticity minor/major = {out['ell']:.6f}")
    print(f"chi = {np.rad2deg(out['chi']):+.3f} deg")

    # plots
    theta = np.deg2rad(deg)
    I_fit = model_I(theta, out["A"],out["B"],out["C"],out["D"],out["theta0"],out["Ioff"])
    deg_dense = np.linspace(deg.min(), deg.max(), 1000)
    th_dense = np.deg2rad(deg_dense)
    I_dense = model_I(th_dense, out["A"],out["B"],out["C"],out["D"],out["theta0"],out["Ioff"])

    plt.figure(figsize=(7,4))
    plt.plot(deg, P1, "o-", label="P1")
    plt.plot(deg, P2, "o-", label="P2")
    plt.plot(deg, P1+P2, "o--", label="P1+P2")
    plt.xlabel("QWP dial angle (deg)")
    plt.ylabel("Power (µW)")
    plt.title(f"{name}: powers")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.figure(figsize=(7,4))
    plt.plot(deg, I, "o", label=f"measured {port}")
    plt.plot(deg_dense, I_dense, "-", label="fit")
    plt.xlabel("QWP dial angle (deg)")
    plt.ylabel(f"{port} (µW)")
    plt.title(f"{name}: analyzer signal + fit (with θ0)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.figure(figsize=(7,3.2))
    plt.axhline(0, linewidth=1)
    plt.plot(deg, I - I_fit, "o-")
    plt.xlabel("QWP dial angle (deg)")
    plt.ylabel("residual (µW)")
    plt.title(f"{name}: residuals")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    return out

# Run: choose analyzer port (try both if you want)
outA = analyze("Dataset A (no HWP)", deg_A, P1_A, P2_A, port="P1")
outB = analyze("Dataset B (HWP=17.7°)", deg_B, P1_B, P2_B, port="P1")

plt.show()