import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullFormatter

import matplotlib.font_manager as fm
fm._load_fontmanager(try_read_cache=False)

plt.rcParams.update({
    "font.family"        : "sans-serif",
    "font.sans-serif"    : ["Helvetica", "Arial", "DejaVu Sans"],
    "mathtext.fontset"   : "custom",
    "mathtext.rm"        : "Helvetica",
    "mathtext.it"        : "Helvetica:italic",
    "mathtext.bf"        : "Helvetica:bold",
    "axes.spines.top"    : True,
    "axes.spines.right"  : True,
    "axes.linewidth"     : 0.8,
    "xtick.direction"    : "in",
    "ytick.direction"    : "in",
    "xtick.major.size"   : 4,
    "ytick.major.size"   : 4,
    "xtick.minor.size"   : 2.5,
    "ytick.minor.size"   : 2.5,
    "xtick.major.width"  : 0.8,
    "ytick.major.width"  : 0.8,
    "xtick.labelsize"    : 10,
    "ytick.labelsize"    : 10,
    "axes.labelsize"     : 11,
    "legend.fontsize"    : 9,
    "legend.framealpha"  : 0.92,
    "legend.edgecolor"   : "#cccccc",
    "legend.handlelength": 2.0,
    "figure.dpi"         : 150,
})

# ── load data ──────────────────────────────────────────────────────────────
baseline = pd.read_csv("baseline.csv",
                       names=["freq", "asd"], skiprows=1)
baseline = baseline[baseline["freq"] > 0]
freq_b = baseline["freq"].values
asd_b  = baseline["asd"].values   # cyc/√Hz

modulator = pd.read_csv("modulator_psd.csv",
                        comment="#", names=["freq", "psd"])
modulator = modulator[modulator["freq"] > 0]
freq_m = modulator["freq"].values
asd_m  = np.sqrt(modulator["psd"].values)   # cyc/√Hz

# ── requirement ────────────────────────────────────────────────────────────
f1   = np.logspace(np.log10(freq_b[1]), np.log10(freq_b[-1]), 2000)
S_req = (1 / 1064e-9) * 1e-12 * np.sqrt(1.0 + (2e-3 / f1)**4)

# ── colours ───────────────────────────────────────────────────────────────
gray = (50/255, 50/255, 50/255)
col1 = (130/255, 23/255, 112/255)
col2 = (215/255, 27/255,  47/255)

# ── plot ──────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4.5))

ax.plot(f1, S_req,         color=gray,    lw=1.5, ls="--", label="1 pm requirement", zorder=4)
ax.plot(f1, S_req / 200,   color="black", lw=1.2, ls="-",  label=r"1 pm requirement $\times 1/200$", zorder=4)

ax.plot(freq_b, asd_b, color=col1, lw=0.7, alpha=0.85, label="Baseline")
ax.plot(freq_m, asd_m, color=col2, lw=0.7, alpha=0.85, label="Modulator")

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel(r"Frequency noise ASD (cyc/$\sqrt{\mathrm{Hz}}$)")

ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2,10)*0.1, numticks=20))
ax.yaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2,10)*0.1, numticks=20))
ax.xaxis.set_minor_formatter(NullFormatter())
ax.yaxis.set_minor_formatter(NullFormatter())
ax.tick_params(which="both", top=True, right=True)


ax.grid(True,  which="major", color="#e0e0e0", linewidth=0.6, linestyle="--")
ax.grid(False, which="minor")

ax.set_xlim(freq_b[1], freq_b[-1])
ax.legend(loc="upper right")

fig.tight_layout()
fig.savefig("noise_asd.pdf", bbox_inches="tight")
fig.savefig("noise_asd.png", bbox_inches="tight", dpi=300)
print("Done")