import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ------------------------------------------------------------
# Setup: linear polarization rotating from 0° -> 90°
# Waveplate: HWP with theta_deg = 0 (fast axis along +x)
# Effect (for linear pol): alpha_out = -alpha_in  (mirror about x-axis)
# ------------------------------------------------------------

theta_deg = 0.0  # fast axis angle (deg) from +x (fixed as you asked)
alpha_start_deg = 0.0
alpha_end_deg = 90.0*3

# animation controls
FPS = 60
DURATION_S = 4.0
NFRAMES = int(FPS * DURATION_S)

# optical-phase sampling for the Ex-Ey locus (Lissajous)
NPTS = 1200
t = np.linspace(0, 2*np.pi, NPTS)

def ex_ey_locus_linear(alpha_rad):
    # Jones vector for linear pol at angle alpha: [cos a, sin a]
    Ex0 = np.cos(alpha_rad)
    Ey0 = np.sin(alpha_rad)
    # real field vs optical phase (exp(-i wt) convention)
    Ex = Ex0 * np.cos(t)
    Ey = Ey0 * np.cos(t)
    return Ex, Ey

# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.2, 6.2), dpi=140)

# loci
line_before, = ax.plot([], [], lw=2, label="before (linear)")
line_after,  = ax.plot([], [], lw=2, ls="--", label="after HWP (θ=0°)")

# orientation indicators (just to make it obvious as hell)
vec_before, = ax.plot([], [], lw=4)      # from origin to unit direction
vec_after,  = ax.plot([], [], lw=4, ls="--")

# formatting
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
    vec_after.set_data([], [])
    title.set_text("")
    return line_before, line_after, vec_before, vec_after, title

def update(frame):
    # alpha_in rotates 0 -> 90 deg
    frac = frame / (NFRAMES - 1)
    alpha_in = np.deg2rad(alpha_start_deg + frac * (alpha_end_deg - alpha_start_deg))

    # HWP with fast axis along x: reflect Ey -> -Ey => alpha_out = -alpha_in
    alpha_out = -alpha_in

    # loci (linear => straight line, but plotting locus makes it explicit)
    Exb, Eyb = ex_ey_locus_linear(alpha_in)
    Exa, Eya = ex_ey_locus_linear(alpha_out)

    line_before.set_data(Exb, Eyb)
    line_after.set_data(Exa, Eya)

    # direction vectors
    vb = np.array([np.cos(alpha_in),  np.sin(alpha_in)])
    va = np.array([np.cos(alpha_out), np.sin(alpha_out)])
    vec_before.set_data([0, vb[0]], [0, vb[1]])
    vec_after.set_data([0, va[0]], [0, va[1]])

    title.set_text(
        f"Linear input rotates {alpha_start_deg:.0f}° → {alpha_end_deg:.0f}°\n"
        f"Before angle = {np.rad2deg(alpha_in):5.1f}° | After HWP(θ=0°) = {np.rad2deg(alpha_out):5.1f}°"
    )

    return line_before, line_after, vec_before, vec_after, title

ani = FuncAnimation(fig, update, frames=NFRAMES, init_func=init, blit=True, interval=1000/FPS)

plt.show()
