import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.signal import welch
from scipy.fft import fft, fftfreq

# Fixed laser parameters
gamma_c = 1 / 16e-9       # Cavity decay rate [1/s]
gamma_2 = 1 / 0.005       # Upper state decay rate [1/s]
K = 1                     # Gain coefficient
beta = 1e-5               # Spontaneous emission factor
N_th = gamma_c / K        # Threshold inversion
R_th = gamma_2 * N_th     # Threshold pump rate

pump_factors = [1.1, 100, 3000, 1e4]
pump_labels = ["Pumpnig rate R_p = " + str(pump_factors[i]) + " R_th" for i in range(len(pump_factors))]	
colors = ['navy', 'maroon', 'goldenrod', 'green']	


# Time setup
t_span = (0, 200e-6)  # 200 microseconds
t_eval = np.linspace(*t_span, 10000)

# Storage for the last (highest) simulation for RIN
last_t = None
last_n = None

n0 = 5
# PLAY WITH THIS ALSO
N0 =  1.05 * gamma_c
y0 = [n0, N0]

# Create a single figure with 3 subplots (one for each R_p case)
fig, axes = plt.subplots(len(pump_factors), 2, figsize=(14, 3 * len(pump_factors)))

color2 = 'gray'

# Can modify!
def rate_equations(t, y):
    n, N = y
    dn_dt = (-gamma_c + K * N) * n + beta * gamma_2 * N
    dN_dt = R_p - (gamma_2 + K * n) * N
    return [dn_dt, dN_dt]


for i, factor in enumerate(pump_factors):
    R_p = factor * R_th

    sol = solve_ivp(rate_equations, t_span, y0, t_eval=t_eval, method='RK45')

    # Plot n(t)/γ2 and N(t)/γc on the left axis
    ax1 = axes[i, 0]
    color1 = colors[i]
    ax1.set_title(pump_labels[i])
    ax1.set_xlabel("Time [µs]")
    ax1.set_ylabel(r"Photon number $n(t)/\gamma_2$", color=color1)
    ax1.plot(sol.t * 1e6, sol.y[0] / gamma_2, color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True)

    ax2 = ax1.twinx()
    color2 = 'gray'
    ax2.set_ylabel(r"Population $N(t)/\gamma_c$", color=color2)
    ax2.plot(sol.t * 1e6, sol.y[1] / gamma_c, color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.axhline(y=N_th / gamma_c, color='darkgray', linestyle='--', linewidth=1, label='N_th')

    # Right plot: phase-space style N vs n
    ax3 = axes[i, 1]
    ax3.plot(sol.y[0] / gamma_2, sol.y[1] / gamma_c, color=color1)
    ax3.set_xlabel(r"Photon number $n(t)/\gamma_2$")
    ax3.set_ylabel(r"Population $N(t)/\gamma_c$")
    ax3.grid(True)
    ax3.set_title(f"Phase Space: {pump_labels[i]}")
    
    if factor == 3000:
        last_t = sol.t
        last_n = sol.y[0]

fig.suptitle("Photon Number and Inversion Dynamics for Varying Pump Rates", fontsize=14)
fig.tight_layout()
plt.show()


show_RIN = False
if show_RIN:
    # RIN Spectrum (Welch + FFT) for highest pump case
    n_norm = last_n / np.mean(last_n)
    n_centered = n_norm - 1
    fs = 1 / (last_t[1] - last_t[0])
    f_welch, Pxx = welch(n_centered, fs=fs, nperseg=1024, scaling='density')
    RIN_dBc_Hz_welch = 10 * np.log10(Pxx)

    N = len(n_centered)
    fft_vals = fft(n_centered)
    fft_freqs = fftfreq(N, 1 / fs)
    pos_mask = fft_freqs > 0
    fft_freqs = fft_freqs[pos_mask]
    fft_power = (np.abs(fft_vals[pos_mask])**2) / (fs * N)
    RIN_dBc_Hz_fft = 10 * np.log10(fft_power)

    # Plot RIN
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.semilogx(f_welch, RIN_dBc_Hz_welch, label='Welch PSD', color='tab:blue')
    ax.semilogx(fft_freqs, RIN_dBc_Hz_fft, label='FFT Spectrum', color='tab:red', alpha=0.6)
    ax.set_title("RIN Spectrum for R_p = 3000 R_th")
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("RIN [dBc/Hz]")
    ax.grid(True, which='both', ls='--')
    ax.legend()
    plt.tight_layout()
    plt.show()
