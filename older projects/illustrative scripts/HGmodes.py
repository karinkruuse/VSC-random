import numpy as np
import matplotlib.pyplot as plt
from scipy.special import hermite, factorial

# Parameters
w0 = 1e-3  # beam waist in meters
λ = 1064e-9  # wavelength in meters
z = 10*λ  # distance along beam axis (z = 0 at waist)
k = 2 * np.pi / λ
zR = np.pi * w0**2 / λ  # Rayleigh range

# Generate transverse grid
x = np.linspace(-3*w0, 3*w0, 500)
y = np.linspace(-3*w0, 3*w0, 500)
X, Y = np.meshgrid(x, y)
r2 = X**2 + Y**2

# Define Hermite-Gauss mode intensity function
def HG_mode_intensity(n, m, X, Y, w0, z):
    w_z = w0 * np.sqrt(1 + (z / zR)**2)
    R_z = z if z != 0 else np.inf
    Gouy_phase = (n + m + 1) * np.arctan(z / zR)
    
    ξ = np.sqrt(2) * X / w_z
    η = np.sqrt(2) * Y / w_z

    Hn = hermite(n)(ξ)
    Hm = hermite(m)(η)
    norm = 1 / (2**(n + m) * factorial(n) * factorial(m))**0.5
    envelope = np.exp(-2 * r2 / w_z**2)
    
    # The Gouy phse exp is missing, however, does that matter for the intensity??

    intensity = norm**2 * (Hn**2) * (Hm**2) * envelope
    return intensity

# Choose mode numbers (n, m)
modes = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0)]

# Add more rows for different z values (propagation distances)
z_values = [0, 0.2 * zR, 0.5 * zR, zR, 4 * zR]  # From waist to 1 Rayleigh range

# Create figure with one row per z, one column per mode
fig, axes = plt.subplots(len(z_values), len(modes), figsize=(15, 9))

for i, z in enumerate(z_values):
    for j, (n, m) in enumerate(modes):
        I = HG_mode_intensity(n, m, X, Y, w0, z)
        ax = axes[i, j]
        ax.imshow(I, extent=(-3*w0*1e3, 3*w0*1e3, -3*w0*1e3, 3*w0*1e3), cmap='inferno')
        if i == 0:
            ax.set_title(f'HG$_{{{n}{m}}}$')
        if j == 0:
            ax.set_ylabel(f'z = {z:.2f} m')
        ax.set_xticks([])
        ax.set_yticks([])

plt.suptitle('Hermite-Gaussian Beam Intensities at Multiple z Positions')
plt.tight_layout()
plt.show()

