import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Constants
# -----------------------------
c = 299792458.0
lambda_laser = 1064e-9          # [m]
L = 2.5e9 / c                   # light travel time [s]

# -----------------------------
# Frequency grid
# -----------------------------
f = np.logspace(-4, 0, 4000)    # 0.1 mHz – 1 Hz
omega = 2 * np.pi * f

# -----------------------------
# USO noise (Eq. 45)
# -----------------------------
S_q = 4e-27 / f                 # fractional frequency PSD

# -----------------------------
# Programmed beatnote offsets (Eqs. 42–44)
# -----------------------------
O12 =  8.1e6
O21 = -9.5e6
O13 =  1.4e6
O31 = 10.3e6

a12 = O21 - O12
a13 = O31 - O13
a21 = O12 - O21
a31 = O13 - O31
b12 = O13 - O12

print("Beatnote frequencies used [MHz]:")
print(f"a12 = {a12/1e6:+.3f}")
print(f"a13 = {a13/1e6:+.3f}")
print(f"a21 = {a21/1e6:+.3f}")
print(f"a31 = {a31/1e6:+.3f}")
print(f"b12 = {b12/1e6:+.3f}")

# -----------------------------
# Eq. (30): full AX2
# -----------------------------
AX2_full = (
    (a12 - a13)**2
    + a21**2
    + a31**2
    - 4 * b12 * (a12 - a13 - b12) * np.sin(omega * L)**2
)

# -----------------------------
# Eq. (29): full X2 clock noise
# -----------------------------
S_Xq2_full = (
    16
    * np.sin(2 * omega * L)**2
    * np.sin(omega * L)**2
    * AX2_full
    * S_q
)

# -----------------------------
# Simplified X2^{dot q}
# -----------------------------
AX2_simple = (
    (a12 - a13)**2
    + a21**2
    + a31**2
)

S_Xq2_simple = (
    16
    * np.sin(2 * omega * L)**2
    * np.sin(omega * L)**2
    * AX2_simple
    * S_q
)

# -----------------------------
# X1^{dot q}  (your new expression)
# -----------------------------
AX1_simple = (
    (a12 - a13)**2
    + a12**2
    + a13**2
)

S_Xq1 = (
    4
    * np.sin(omega * L)**2
    * AX1_simple
    * S_q
)

# -----------------------------
# Eq. (31): 1 pm allocation
# -----------------------------
Sx_alloc = (
    64
    * omega**2
    * np.sin(omega * L)**2
    * np.sin(2 * omega * L)**2
    * (1e-12 / lambda_laser)**2
    * (1 + (2e-3 / f)**4)
)

# Convert to ASD
ASD_alloc = np.sqrt(Sx_alloc)
ASD_Xq2_full = np.sqrt(S_Xq2_full)
ASD_Xq2_simple = np.sqrt(S_Xq2_simple)
ASD_Xq1 = np.sqrt(S_Xq1)

# -----------------------------
# Plot
# -----------------------------
plt.figure(figsize=(7.5, 5.5))

plt.loglog(f, ASD_alloc, color='red',
           label='1 pm allocation (Eq. 31)')
plt.loglog(f, ASD_Xq2_full, color='C0',
           label=r'$X_2$ clock noise (Eq. 29)')
plt.loglog(f, ASD_Xq2_simple, color='black',
           label=r'miniLISA $X_2^{q}$')
plt.loglog(f, ASD_Xq1, color='gray',
           label=r'$miniLISA X_1^{q}$')

plt.xlabel('Frequency [Hz]')
plt.ylabel('ASD [m / √Hz]')
plt.grid(True, which='both', ls=':')
plt.legend()
plt.tight_layout()
plt.savefig('clock_residuals.pdf', dpi=600)
