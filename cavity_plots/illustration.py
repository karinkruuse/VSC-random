"""
Static slide figure: resonance combs of two cavities near 281 THz.
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

matplotlib.rcParams['font.family'] = 'Helvetica'
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype']  = 42

c         = 299792458.0
LA_r      = 0.25 + 0.2e-6
LB_r      = 0.30 + 10.0e-6
nu0       = 281e12
half_span = 5e9

fsrA = c / (2.0 * LA_r)
fsrB = c / (2.0 * LB_r)

m_min = int(np.ceil((nu0 - half_span) / fsrA))
m_max = int(np.floor((nu0 + half_span) / fsrA))
n_min = int(np.ceil((nu0 - half_span) / fsrB))
n_max = int(np.floor((nu0 + half_span) / fsrB))

offA = np.array([m * fsrA - nu0 for m in range(m_min, m_max + 1)])
offB = np.array([n * fsrB - nu0 for n in range(n_min, n_max + 1)])

close_pairs = []
for a in offA:
    diffs = np.abs(offB - a)
    idx   = np.argmin(diffs)
    beat  = diffs[idx]
    if beat < 60e6:
        close_pairs.append((beat, a, offB[idx]))
close_pairs.sort()

C1   = (215/255,  27/255,  47/255)
C2   = ( 45/255,  19/255, 180/255)
C_HL = (130/255,  23/255, 112/255)

# GridSpec: narrow top strip for beat labels, main plot below
fig = plt.figure(figsize=(13, 4.0))
fig.patch.set_facecolor('white')
gs  = fig.add_gridspec(2, 1, height_ratios=[1, 4], hspace=0)
ax_ann = fig.add_subplot(gs[0])
ax     = fig.add_subplot(gs[1])
for a in [ax_ann, ax]:
    a.set_facecolor('white')

# ── Beat labels in top strip ──────────────────────────────────────────────────
ax_ann.set_xlim(-half_span/1e9, half_span/1e9)
ax_ann.set_ylim(0, 1)
ax_ann.axis('off')

for beat, a, b in close_pairs:
    mid = (a + b) / 2.0 / 1e9
    ax_ann.text(mid, 0.45, f"{beat/1e6:.1f} MHz",
                ha='center', va='center', fontsize=8,
                color=C_HL, fontweight='bold')

# ── Main plot ─────────────────────────────────────────────────────────────────
# Highlighted bands
for beat, a, b in close_pairs:
    cx = (a + b) / 2.0 / 1e9
    w  = max(abs(a - b), 80e6) / 1e9
    ax.axvspan(cx - w/2, cx + w/2,
               color=C_HL, alpha=0.20, zorder=0, lw=0)

# Cavity A lines — upper half
for x in offA:
    ax.plot([x/1e9, x/1e9], [0.55, 0.97],
            color=C1, lw=1.1, solid_capstyle='butt', zorder=2)

# Cavity B lines — lower half
for x in offB:
    ax.plot([x/1e9, x/1e9], [0.03, 0.45],
            color=C2, lw=1.1, solid_capstyle='butt', zorder=2)

ax.axhline(0.50, color='#dddddd', lw=0.7, zorder=1)

ax.set_xlim(-half_span/1e9, half_span/1e9)
ax.set_ylim(0, 1)
ax.set_xlabel("Frequency offset from 281 THz (GHz)", fontsize=12)
ax.set_yticks([])
for spine in ['left', 'right', 'top']:
    ax.spines[spine].set_visible(False)
ax.spines['bottom'].set_linewidth(0.8)
ax.tick_params(axis='x', labelsize=10)
ax.grid(axis='x', linestyle=':', lw=0.4, alpha=0.35, color='gray', zorder=0)

plt.savefig("cavity_resonances_slide.pdf",
            bbox_inches='tight', dpi=300)
plt.savefig("cavity_resonances_slide.png",
            bbox_inches='tight', dpi=300)
print("Saved.")