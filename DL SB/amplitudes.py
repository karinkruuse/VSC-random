import numpy as np
import matplotlib.pyplot as plt

# ── CONFIG ────────────────────────────────────────────────────────────────
FILES = {
    'Carrier': 'data/Carrier_20260526_160851.npy',
    'USB':     'data/USB_20260526_160852.npy',
    'LSB':     'data/LSB_20260526_160853.npy',
    'CLK':     'data/CLK_20260526_160854.npy',
}

# ── LOAD ──────────────────────────────────────────────────────────────────
def load_npy(path):
    data = np.load(path)
    def col(n): return data[n].copy()
    return {
        't':   col('Time (s)'),
        'I_A': col('Input A I (V)'),
        'Q_A': col('Input A Q (V)'),
        'I_B': col('Input B I (V)'),
        'Q_B': col('Input B Q (V)'),
    }

print("Loading files...")
datasets = {name: load_npy(path) for name, path in FILES.items()}

# ── COMPUTE AMPLITUDES ────────────────────────────────────────────────────
# Amplitude = sqrt(I^2 + Q^2)
for name, d in datasets.items():
    d['amp_A'] = np.sqrt(d['I_A']**2 + d['Q_A']**2)
    d['amp_B'] = np.sqrt(d['I_B']**2 + d['Q_B']**2)

# ── PLOT: one row per file, two columns (A and B channels) ────────────────
fig, axes = plt.subplots(4, 2, figsize=(14, 12), sharex=False)
fig.suptitle('Phasemeter Signal Amplitudes — All 8 Channels\n√(I² + Q²)',
             fontsize=13)

for row, (name, d) in enumerate(datasets.items()):
    t_h = (d['t'] - d['t'][0]) / 3600   # time in hours from start

    for col_idx, (ch, amp) in enumerate([('A', d['amp_A']), ('B', d['amp_B'])]):
        ax = axes[row, col_idx]
        ax.plot(t_h, amp, lw=0.5, color=f'C{row*2 + col_idx}')
        ax.set_ylabel('Amplitude (V)')
        ax.set_title(f'{name} — Input {ch}')
        ax.grid(True, ls='--', alpha=0.4)
        # Annotate mean
        ax.axhline(np.median(amp), color='k', ls='--', lw=0.8, alpha=0.6,
                   label=f'median={np.median(amp):.4f} V')
        ax.legend(fontsize=8, loc='upper right')

for ax in axes[-1, :]:
    ax.set_xlabel('Time from start (h)')

plt.tight_layout()
plt.savefig('plots/all_amplitudes.png', dpi=150)
print("Saved: plots/all_amplitudes.png")
plt.show()