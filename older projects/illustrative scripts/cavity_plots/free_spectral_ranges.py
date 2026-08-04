"""
Cavity resonance comb plotter — two Fabry-Pérot cavities near 281 THz

c = 299792458 m/s  (exact SI definition)
FSR = c / (2*L),  computed with exact c.

IMPORTANT: With LA=0.25 and LB=0.30 m exactly, LB/LA = 6/5 as an exact
rational, so FSR_A/FSR_B = 6/5 and beat notes are always exactly 0 for
certain mode pairs — a pure number-theory artefact of using round lengths.
Real cavities deviate from nominal by micrometres, giving nonzero beats.
Use the dLA / dLB sliders below to explore realistic length offsets.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Slider

c   = 299792458.0      # [m/s] exact
LA0 = 0.25             # [m] nominal
LB0 = 0.30             # [m] nominal
nu0 = 281e12           # [Hz] centre frequency

half_span = 15e9       # [Hz] plot window ±15 GHz

def compute(dLA_um, dLB_um):
    LA = LA0 + dLA_um * 1e-6
    LB = LB0 + dLB_um * 1e-6
    fsrA = c / (2.0 * LA)
    fsrB = c / (2.0 * LB)

    m_min = int(np.ceil((nu0 - half_span) / fsrA))
    m_max = int(np.floor((nu0 + half_span) / fsrA))
    n_min = int(np.ceil((nu0 - half_span) / fsrB))
    n_max = int(np.floor((nu0 + half_span) / fsrB))

    # Absolute frequencies, then subtract nu0 for plotting
    nuA = np.array([m * fsrA for m in range(m_min, m_max + 1)])
    nuB = np.array([n * fsrB for n in range(n_min, n_max + 1)])
    offA = nuA - nu0   # [Hz] offsets from 281 THz
    offB = nuB - nu0

    # All beats
    beats = []
    for i, a in enumerate(offA):
        diffs = np.abs(offB - a)
        idx = np.argmin(diffs)
        beat = diffs[idx]
        beats.append((beat, a, offB[idx]))

    beats.sort()
    return offA, offB, beats, fsrA, fsrB

def draw(dLA_um, dLB_um):
    ax.cla()
    offA, offB, beats, fsrA, fsrB = compute(dLA_um, dLB_um)

    COLOR_A = '#3266ad'
    COLOR_B = '#c94f3b'
    COLOR_OK = '#50b450'
    COLOR_NO = '#cc3333'

    for x in offA:
        ax.axvline(x / 1e9, ymin=0.52, ymax=1.00, color=COLOR_A, lw=1.2, alpha=0.85)
    for x in offB:
        ax.axvline(x / 1e9, ymin=0.00, ymax=0.48, color=COLOR_B, lw=1.2, alpha=0.85)
    ax.axhline(0.5, color='gray', lw=0.5, linestyle='--', alpha=0.4)

    # Nearest beat
    best_beat, ba, bb = beats[0]
    beat_mhz = best_beat / 1e6
    under_60  = beat_mhz < 60.0
    col = COLOR_OK if under_60 else COLOR_NO
    sign = '✓' if under_60 else '✗'

    if under_60:
        xlo = min(ba, bb) / 1e9 - 0.05
        xhi = max(ba, bb) / 1e9 + 0.05
        ax.axvspan(xlo, xhi, color=COLOR_OK, alpha=0.15)

    ax.set_title(
        f"Nearest pair:  A @ {ba/1e9:+.6f} GHz,  B @ {bb/1e9:+.6f} GHz  "
        f"→  beat = {beat_mhz:.4f} MHz  {sign}\n"
        f"FSR_A = {fsrA/1e6:.6f} MHz   FSR_B = {fsrB/1e6:.6f} MHz",
        fontsize=10, color=col
    )

    ax.set_xlim(-half_span / 1e9, half_span / 1e9)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Frequency offset from 281 THz (GHz)", fontsize=11)
    ax.set_yticks([0.25, 0.75])
    ax.set_yticklabels(['Cavity B  (30 cm + δ)', 'Cavity A  (25 cm + δ)'], fontsize=10)
    ax.tick_params(axis='y', length=0)
    ax.grid(axis='x', linestyle=':', lw=0.5, alpha=0.4)

    LA_mm = (LA0 + dLA_um*1e-6)*1e3
    LB_mm = (LB0 + dLB_um*1e-6)*1e3
    pa = mpatches.Patch(color=COLOR_A,
        label=f'Cavity A — {LA_mm:.4f} mm   FSR = {fsrA/1e6:.6f} MHz')
    pb = mpatches.Patch(color=COLOR_B,
        label=f'Cavity B — {LB_mm:.4f} mm   FSR = {fsrB/1e6:.6f} MHz')
    ax.legend(handles=[pa, pb], loc='upper right', fontsize=9, framealpha=0.85)

    fig.canvas.draw_idle()

# ── Figure layout ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 5))
plt.subplots_adjust(bottom=0.28)

fig.suptitle(
    f"Fabry-Pérot resonance combs near 281 THz  |  c = {int(c)} m/s (exact)",
    fontsize=11
)

draw(0.0, 0.0)

# ── Sliders for length offsets ────────────────────────────────────────────────
ax_dLA = plt.axes([0.15, 0.12, 0.70, 0.03])
ax_dLB = plt.axes([0.15, 0.06, 0.70, 0.03])

s_dLA = Slider(ax_dLA, 'δL_A (µm)', -500, 500, valinit=0, valstep=1, color='#aac4e8')
s_dLB = Slider(ax_dLB, 'δL_B (µm)', -500, 500, valinit=0, valstep=1, color='#f0b8b0')

def on_change(_):
    draw(s_dLA.val, s_dLB.val)

s_dLA.on_changed(on_change)
s_dLB.on_changed(on_change)

plt.savefig("cavity_resonances.png", dpi=150, bbox_inches='tight')
plt.show()