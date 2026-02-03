import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(4)

# Primary time axis τ_m
T = 20000.0
fs = 2.0
t = np.arange(0, T, 1/fs)
dt = 1/fs
N = t.size

# Fractional frequency error y(t) = qdot(t)
y0 = 0#3e-7
white = 0# 3e-10 * rng.standard_normal(N)
wander = np.cumsum(2e-12 * rng.standard_normal(N)) * dt
slow = 1.5e-7 * np.sin(2*np.pi*t/7000.0+0.5*np.pi)
y = y0 + slow + wander + white

# Time deviation q(t) = ∫ y dt
q = np.cumsum(y) * dt

# Timer deviation δτ_i(τ_m) = δτ_i0 + q(t)
delta0 = 2.3
delta = delta0 + q

# Clock-i time axis τ_i(τ_m)
tau_i = t + delta

# Inverse mapping τ_m(τ_i) by interpolation
tau_samples = np.linspace(tau_i[0], tau_i[-1], 2000)
t_true = np.interp(tau_samples, tau_i, t)

# Inverse Jacobian evaluated at the true event time
inv_slope_at_tau = 1.0 / (1.0 + np.interp(t_true, t, y))

# Finite-difference derivative check
y_fd = np.gradient(q, dt)

# ---- Plot everything in one figure ----
fig, axs = plt.subplots(3, 2, figsize=(12, 10))
axs = axs.ravel()

axs[0].plot(t, y)
axs[0].set_xlabel(r"Primary time $\tau_m$ [s]")
axs[0].set_ylabel(r"Fractional frequency error $\dot q_i(\tau_m)$")
axs[0].set_title(r"$\dot q_i$: instantaneous rate error")

axs[1].plot(t, q)
axs[1].set_xlabel(r"Primary time $\tau_m$ [s]")
axs[1].set_ylabel(r"Time deviation $q_i(\tau_m)$ [s]")
axs[1].set_title(r"$q_i=\int \dot q_i\,d\tau$ (accumulated time error)")

axs[2].plot(t, tau_i)
axs[2].set_xlabel(r"Primary time $\tau_m$ [s]")
axs[2].set_ylabel(r"Clock-i time $\tau_i$ [s]")
axs[2].set_title(r"Forward time-warp $\tau_i(\tau_m)$")

axs[3].plot(tau_samples, inv_slope_at_tau)
axs[3].set_xlabel(r"Recorded time $\tau$ (clock $i$) [s]")
axs[3].set_ylabel(r"$d\tau_m^{\tau_i}(\tau)/d\tau$")
axs[3].set_title(r"Inverse Jacobian $d\tau_m/d\tau_i=1/(1+\dot q_i)$")

axs[4].plot(t, y, label=r"$\dot q_i$ (model)")
axs[4].plot(t, y_fd, label=r"$dq_i/d\tau_m$ (finite diff)")
axs[4].set_xlabel(r"Primary time $\tau_m$ [s]")
axs[4].set_ylabel(r"Fractional frequency error")
axs[4].set_title(r"Check: $\dot q_i = dq_i/d\tau_m$")
axs[4].legend()

axs[5].plot(t, delta)
axs[5].set_xlabel(r"Primary time $\tau_m$ [s]")
axs[5].set_ylabel(r"Timer deviation $\delta\tau_i(\tau_m)$ [s]")
axs[5].set_title(r"Timer deviation $\delta\tau_i=\delta\tau_{i,0}+q_i$")

fig.suptitle(r"Clock model: $\dot q$ (rate error) $\rightarrow$ $q$ (time error) $\rightarrow$ time-warp and Jacobian", y=0.98)
fig.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()

{
    "mean(dot q)": float(np.mean(y)),
    "std(dot q)": float(np.std(y)),
    "q range [s]": (float(np.min(q)), float(np.max(q))),
    "delta range [s]": (float(np.min(delta)), float(np.max(delta)))
}

