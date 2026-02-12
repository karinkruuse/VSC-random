import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ------------------------------------------------------------
# Linear polarization rotating from 0° -> 90°
# Waveplate: QWP with theta_deg = 0 (fast axis along +x)
# Effect: adds +pi/2 relative phase between y and x components:
#   Ein = [cos a, sin a]
#   Eout = [cos a, i sin a]
# which becomes elliptical in general (circular at a=45°).
# ------------------------------------------------------------

theta_deg = 0.0  # fast axis angle (deg) from +x (fixed)
alpha_start_deg = 0.0
alpha_end_deg = 90.0

# animation controls
FPS = 60
DURATION_S = 4.0
NFRAMES = int(FPS * DURATION_S)

# optical phase samples for Ex-Ey locus
NPTS = 1600
t = np.linspace(0, 2*np.pi, NPTS)

def locus_from_jones(E):
    """
    E is a complex Jones vector [Ex0, Ey0] with exp(-i wt) convention.
    Return real Ex(t), Ey(t).
    """
    ph = np.exp(-1j * t)
    Ex = np.real(E[0] * ph)
    Ey = np.real(E[1] * ph)
    return Ex, Ey

def jones_linear(alpha_rad):
    return np.array([np.cos(alpha_rad), np.sin(alpha_rad)], dtype=complex)

def apply_qwp_theta0(Ein):
    # QWP fast axis along x: J = diag(1, i)
    J = np.array([[1, 0],
                  [0, 1j]], dtype=complex)
    return J @ Ein

# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.2, 6.2), dpi=140)

line_before, = ax.plot([], [], lw=2, label="before (linear)")
line_after,  = ax.plot([], [], lw=2, ls="--", label="after QWP (θ=0°)")

# direction indicator for the *linear* input only (output isn't a single direction)
vec_before, = ax.plot([], [], lw=4)

ax.set_aspect("equal", adjustable="box")
ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-1.1, 1.1)
ax.set_xlabel(r"$E_x$")
ax.set_ylabel(r"$E_y$")
ax.grid(True, alpha=0.3)
ax.legend(loc="upper right")
title = ax.set_title("")

def init():
    line_before.set_data([], [])
    line_after.set_data([], [])
    vec_before.set_data([], [])
    title.set_text("")
    return line_before, line_after, vec_before, title

def update(frame):
    frac = frame / (NFRAMES - 1)
    alpha = np.deg2rad(alpha_start_deg + frac * (alpha_end_deg - alpha_start_deg))

    Ein = jones_linear(alpha)
    Eout = apply_qwp_theta0(Ein)

    Exb, Eyb = locus_from_jones(Ein)
    Exa, Eya = locus_from_jones(Eout)

    line_before.set_data(Exb, Eyb)
    line_after.set_data(Exa, Eya)

    vb = np.array([np.cos(alpha), np.sin(alpha)])
    vec_before.set_data([0, vb[0]], [0, vb[1]])

    # Useful scalar: ellipticity angle chi, where tan(chi)=b/a, |chi|<=45°
    # For Ein=[A, iB] with A,B real >=0, the ellipse axes are A and B => tan|chi| = min(A,B)/max(A,B)
    A = abs(np.cos(alpha))
    B = abs(np.sin(alpha))
    if max(A, B) < 1e-12:
        chi_deg = 0.0
    else:
        chi_deg = np.rad2deg(np.arctan(min(A, B) / max(A, B)))

    title.set_text(
        f"Linear input rotates {alpha_start_deg:.0f}° → {alpha_end_deg:.0f}°\n"
        f"QWP(θ=0°): Eout = [cos α, i sin α]  |  α={np.rad2deg(alpha):5.1f}°  |  |ellipticity angle|≈{chi_deg:4.1f}°"
    )

    return line_before, line_after, vec_before, title

ani = FuncAnimation(fig, update, frames=NFRAMES, init_func=init, blit=True, interval=1000/FPS)

plt.show()

# Optional save:
# ani.save("pol_qwp_theta0.mp4", fps=FPS, dpi=160)  # needs ffmpeg
# ani.save("pol_qwp_theta0.gif", fps=FPS)
