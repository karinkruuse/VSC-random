import numpy as np
import matplotlib.pyplot as plt

# Parameters
sigma_a = 8  # noise strength (1/s)
dt = 1e-6    # time step (s)
T = 200e-6   # total time (s)
N = int(T / dt)
t = np.linspace(0, T, N)

# Wiener process for phase (real part of W(t))
dW = np.sqrt(dt) * np.random.randn(N)
W = np.cumsum(dW)  # real-valued Wiener process

# Phase evolution
phi = np.sqrt(sigma_a / 2) * W  # factor sqrt(σ/2)

# Deterministic oscillation (no noise)
A_det = np.exp(1j * 2 * np.pi * 1e5 * t)  # 100 kHz signal

# Stochastic oscillation
A_noise = np.exp(1j * phi)

# Plot phase evolution
plt.figure()
plt.plot(t * 1e6, phi)
plt.xlabel('Time (μs)')
plt.ylabel('Phase φ(t) [rad]')
plt.title('Phase Diffusion over Time')
plt.grid()

# Plot real part of field
plt.figure()
plt.plot(t * 1e6, np.real(A_det), label='Deterministic')
plt.plot(t * 1e6, np.real(A_noise), label='With Noise', alpha=0.7)
plt.xlabel('Time (μs)')
plt.ylabel('Re[A(t)]')
plt.title('Field Evolution')
plt.legend()
plt.grid()

plt.show()
