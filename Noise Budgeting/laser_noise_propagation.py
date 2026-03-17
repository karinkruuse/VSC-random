import numpy as np
import matplotlib.pyplot as plt
from config_loader import cfg



#  LISA parameters
L_arm     = 2.5e9          # nominal arm length [m]  (2.5 million km)
c         = 3e8            # speed of light [m/s]
nu0       = 281.6e12       # laser carrier frequency [Hz]  (λ ≈ 1064 nm)
tau       = L_arm / c      # one-way light travel time [s]  ≈ 8.3 s

delta_L   = 25e6           # arm-length mismatch between two arms [m]  (~1%)
delta_tau = delta_L / c    # mismatch in travel time [s]

f = np.logspace(-4, 0, 5000)   # 0.1 mHz → 1 Hz


S_laser = 30**2 * (1 + (f / 2e-3)**(-4))    # laser frequency noise [Hz²/Hz]

# USO noise (Eq. 45)
S_q = 4*10e-27 / f                 # fractional frequency PSD

 

S_input = S_laser

alpha = cfg.beatnote.f_het_max / cfg.clocks.f_s

S_clock = alpha**2 * S_q
S_isi = 2 * S_laser + S_clock




fig, ax = plt.subplots(figsize=(10, 6))

ax.loglog(f, np.sqrt(S_input), lw=2,
          label='Laser noise (input)')
ax.loglog(f, np.sqrt(S_clock), lw=2,
          label='Clock noise (input)')
ax.loglog(f, np.sqrt(S_isi),   lw=2, ls='--',
          label='ISI output')

ax.set_xlabel('Frequency  [Hz]')
ax.set_ylabel('Frequency noise ASD  [Hz / √Hz]')
ax.set_title('Laser noise through the LISA measurement chain')
ax.legend(fontsize=11)
ax.grid(True, which='both', alpha=0.3)
ax.set_xlim(f[0], f[-1])

plt.tight_layout()
plt.show()
