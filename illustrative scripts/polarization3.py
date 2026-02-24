import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ------------------------------------------------------------
# Elliptical input -> QWP (theta=0°, fast axis along +x)
#
# Input Jones (phasors, exp(-i wt) convention):
#   Ein = [cos(alpha), sin(alpha) * exp(i delta)]
# alpha sets amplitude ratio, delta sets relative phase.
#
# QWP(theta=0): J = diag(1, i)
#   Eout = [cos(alpha), i * sin(alpha) * exp(i delta)]
# ------------------------------------------------------------

theta_deg = 0.0  # fixed as requested (fast axis along +x)

# Choose an "elliptical" input family to animate:
# We'll keep alpha fixed (amplitude ratio fixed) and sweep delta (relative phase),
# which cleanly shows how the ellipse changes and how the QWP shifts it.
alpha_deg = 30.0                 # amplitude angle (0..90). 45° gives equal amplitudes.
delta_start_deg = -180.0
delta_end_deg = 180.0

# animation controls
FPS = 60
DURATION_S = 5.0
NFRAMES = int(FPS * DURATION_S)

# optical phase samples for Ex-Ey locus
NPTS = 2000
t = np.linspace(0, 2*np.pi, NPTS)

def locus_from_jones(E):
    ph = np.exp(-1j * t)
    Ex = np.real(E[0] * ph)
    Ey = np.real(E[1] * ph)
    return Ex, Ey

def jones_elliptical(alpha_rad, delta_rad):
    return np.array([np.cos(alpha_rad),
                     np.sin(alpha_rad) * np.exp(1j * delta_rad)], dtype=complex)

def apply_qwp_theta0(Ein):
    J = np.array([[1, 0],
                  [0, 1j]], dtype=complex)
    return J @ Ein

# (Optional) quick-and-dirty ellipticity estimate from time samples:
# ratio b/a of minor/major axis from covariance eigenvalues.
def minor_over_major(Ex, Ey):
    X = np.vstack([Ex, Ey])
    C = np.cov(X)
    w = np.linalg.eigvalsh(C)     # sorted ascending
    if w[1] <= 0:
        return 0.0
    return float(np.sqrt(max(w[0], 0.0) / w[1]))

# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.2, 6.2), dpi=140)
line_before, = ax.plot([], [], lw=2, label="before (elliptical input)")
line_after,  = ax.plot([], [], lw=2, ls="--", label="after QWP (θ=0°)")

ax.set_aspect("equal", adjustable="box")
ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-1.1, 1.1)
ax.set_xlabel(r"$E_x$")
ax.set_ylabel(r"$E_y$")
ax.grid(True, alpha=0.3)
ax.legend(loc="upper right")
title = ax.set_title("")

alpha = np.deg2rad(alpha_deg)

def init():
    line_before.set_data([], [])
    line_after.set_data([], [])
    title.set_text("")
    return line_before, line_after, title

def update(frame):
    frac = frame / (NFRAMES - 1)
    delta = np.deg2rad(delta_start_deg + frac * (delta_end_deg - delta_start_deg))

    Ein = jones_elliptical(alpha, delta)
    Eout = apply_qwp_theta0(Ein)

    Exb, Eyb = locus_from_jones(Ein)
    Exa, Eya = locus_from_jones(Eout)

    line_before.set_data(Exb, Eyb)
    line_after.set_data(Exa, Eya)

    # compute minor/major axis ratio (numerical, robust enough)
    e_in = minor_over_major(Exb, Eyb)
    e_out = minor_over_major(Exa, Eya)

    title.set_text(
        f"Elliptical input into QWP(θ=0°)\n"
        f"alpha={alpha_deg:.1f}° (amplitude ratio), delta={np.rad2deg(delta):6.1f}° (relative phase)\n"
        f"minor/major: before≈{e_in:.3f} | after≈{e_out:.3f}"
    )

    return line_before, line_after, title

ani = FuncAnimation(fig, update, frames=NFRAMES, init_func=init, blit=True, interval=1000/FPS)

plt.show()

# Optional save:
# ani.save("elliptical_into_qwp_theta0.mp4", fps=FPS, dpi=160)  # needs ffmpeg
# ani.save("elliptical_into_qwp_theta0.gif", fps=FPS)
