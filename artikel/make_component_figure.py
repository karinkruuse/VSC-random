"""Export article component figures from the audited notebook inputs.

Run: python artikel/make_component_figure.py
No fitting, smoothing, extrapolation, or TDI filtering is applied.
"""
from pathlib import Path
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullFormatter
import numpy as np

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent / 'miniLISA timining jitters'
ROOT = HERE.parent
OUT = HERE / 'images' / 'performance'
OUT.mkdir(parents=True, exist_ok=True)
config = json.loads((MODEL / 'article_model_outputs' / 'assumptions.json').read_text())
assert config['modulation_psd_kind'] == 'phase_cycles'
for name, expected in config['input_sha256'].items():
    source = ROOT / config['input_paths'][name]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == expected, (
        f'{name} changed: rerun the modelling notebook before exporting.')

baseline = np.loadtxt(ROOT / config['input_paths']['baseline.csv'], delimiter=',', skiprows=1)
modulation = np.loadtxt(ROOT / config['input_paths']['modulator_psd.csv'], delimiter=',', comments='#')
fmin, fmax = config['fourier_band_hz']
baseline = baseline[(baseline[:, 0] >= fmin) & (baseline[:, 0] <= fmax)]
modulation = modulation[(modulation[:, 0] >= fmin) & (modulation[:, 0] <= fmax)]
assert np.all(baseline[:, 1] >= 0) and np.all(modulation[:, 1] >= 0)
freq = np.geomspace(fmin, fmax, 1500)
lam = 1064e-9
oms = 15e-12 / lam * np.sqrt(1 + (2e-3 / freq)**4)
acc = 3e-15 / ((2*np.pi*freq)**2 * lam) * np.sqrt(1 + (0.4e-3/freq)**2) * np.sqrt(1 + (freq/8e-3)**4)
reference = np.hypot(oms, acc)
pd = config['newport']
carrier = pd['total_cycles_per_sqrt_Hz']['carrier']
sideband = pd['total_cycles_per_sqrt_Hz']['sideband']
for ch, total in [('carrier', carrier), ('sideband', sideband)]:
    assert np.isclose(total**2, sum(v*v for name, v in pd['components_cycles_per_sqrt_Hz'][ch].items()
                                  if name != 'ADC' or pd['include_ADC']), rtol=1e-12)

# Palette, inward ticks, square legend and restrained grid from pretty_plot.py.
colors = {'baseline': '#d71b2f', 'modulation': '#821770',
          'carrier': '#295f24', 'sideband': '#29658a', 'reference': '#444444'}
plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
    'mathtext.fontset': 'dejavusans', 'pdf.fonttype': 42, 'ps.fonttype': 42,
    'svg.fonttype': 'none', 'axes.linewidth': 0.7,
    'xtick.direction': 'in', 'ytick.direction': 'in',
    'xtick.top': True, 'ytick.right': True,
    'xtick.major.size': 4, 'ytick.major.size': 4,
    'xtick.minor.size': 2.3, 'ytick.minor.size': 2.3,
    'xtick.major.width': 0.7, 'ytick.major.width': 0.7,
    'xtick.minor.width': 0.5, 'ytick.minor.width': 0.5,
    'legend.fancybox': False, 'legend.framealpha': 0.96,
    'legend.edgecolor': '#cccccc', 'savefig.facecolor': 'white',
})

def export(name, size, fontsize):
    with plt.rc_context({'font.size': fontsize, 'axes.labelsize': fontsize,
                         'xtick.labelsize': fontsize-0.5, 'ytick.labelsize': fontsize-0.5}):
        fig, ax = plt.subplots(figsize=size)
        # Plot measured bins directly. Thin line, no smoothing or resampling.
        ax.loglog(baseline[:, 0], baseline[:, 1], color=colors['baseline'], lw=0.65,
                  label='Delay-line residual (measured)', zorder=3)
        ax.loglog(modulation[:, 0], np.sqrt(modulation[:, 1]), color=colors['modulation'], lw=0.65,
                  label='Modulation noise (measured)', zorder=4)
        ax.loglog(freq, np.full_like(freq, carrier), color=colors['carrier'], lw=1.3,
                  ls='-.', label='Carrier readout (predicted)')
        ax.loglog(freq, np.full_like(freq, sideband), color=colors['sideband'], lw=1.3,
                  ls=':', label='Sideband readout (predicted)')
        ax.loglog(freq, reference, color=colors['reference'], lw=1.35,
                  ls='--', label='Single-link reference (OMS + acc.)', zorder=2)
        ax.set(xlim=(fmin, fmax), ylim=(1.5e-9, 5e-3), xlabel='Fourier frequency (Hz)',
               ylabel=r'Phase ASD (cycles/$\sqrt{\mathrm{Hz}}$)')
        for axis in (ax.xaxis, ax.yaxis):
            axis.set_major_locator(LogLocator(base=10, numticks=12))
            axis.set_minor_locator(LogLocator(base=10, subs=np.arange(2,10), numticks=100))
            axis.set_minor_formatter(NullFormatter())
        ax.grid(which='major', color='#dedede', lw=0.5, ls='--')
        ax.set_axisbelow(True)
        ax.legend(loc='lower left', bbox_to_anchor=(0.025, 0.24),
                  fontsize=fontsize-1, handlelength=2.8, borderpad=0.65, labelspacing=0.5)
        # Compact operating point; full electronics and frequency plan in caption.
        ax.text(0.98, 0.97,
                f'Newport: {pd["P_SC_W"]*1e3:g} mW/beam, '
                + r'$\beta=' + f'{pd["parameters"]["m"]:g}' + r'$' + '\nADC noise included',
                ha='right', va='top', transform=ax.transAxes, fontsize=fontsize-1,
                bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': 0.85, 'pad': 2})
        fig.subplots_adjust(left=0.19 if size[0]<4 else 0.12, bottom=0.145, right=0.98, top=0.97)
        for suffix in ['pdf', 'svg', 'png']:
            fig.savefig(OUT / f'{name}.{suffix}', dpi=600)
        plt.close(fig)

export('component_inputs_single_link', (7.0, 4.8), 10)
export('component_inputs_single_link_column', (3.4, 3.7), 8)

# Companion figure: separate predicted noise components for the two beat types.
with plt.rc_context({'font.size': 9, 'axes.labelsize': 10, 'legend.fontsize': 8}):
    fig, axes = plt.subplots(1, 2, figsize=(7, 3.3), sharex=True, sharey=True)
    component_colors = ['#821770', '#d71b2f', '#295f24', '#29658a']
    for ax, ch in zip(axes, ['carrier', 'sideband']):
        for (label, value), color in zip(pd['components_cycles_per_sqrt_Hz'][ch].items(), component_colors):
            ax.loglog(freq, np.full_like(freq, value), lw=1.0, color=color,
                      label={'shot (including dark)': 'Shot + dark current'}.get(label, label))
        ax.loglog(freq, np.full_like(freq, pd['total_cycles_per_sqrt_Hz'][ch]),
                  'k--', lw=1.4, label='Total')
        ax.set(xlim=(fmin, fmax), ylim=(1.5e-10, 2e-8), xlabel='Fourier frequency (Hz)')
        ax.set_title('Carrier' if ch == 'carrier' else 'First-order sideband', fontsize=10)
        ax.grid(which='major', color='#dedede', lw=0.5, ls='--')
        ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2,10), numticks=100))
        ax.yaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2,10), numticks=100))
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.yaxis.set_minor_formatter(NullFormatter())
    axes[0].set_ylabel(r'Phase ASD (cycles/$\sqrt{\mathrm{Hz}}$)')
    axes[1].legend(loc='lower left', fontsize=7, frameon=True)
    fig.subplots_adjust(left=0.105, right=0.98, bottom=0.18, top=0.91, wspace=0.10)
    for suffix in ['pdf', 'svg', 'png']:
        fig.savefig(OUT / f'newport_readout_breakdown.{suffix}', dpi=600)
    plt.close(fig)
(OUT / 'figure_parameters.json').write_text(json.dumps(config, indent=2))

# Total corrected static X2 budget, exported by the executed modelling notebook.
assert config['observable'] == 'static X2', 'Run the notebook with USE_STATIC_X2=True.'
budget_path = MODEL / 'article_model_outputs' / 'conditional_budget.csv'
budget_names = budget_path.read_text().splitlines()[0].lstrip('# ').split(',')
budget_data = np.loadtxt(budget_path, delimiter=',', comments='#')
budget = dict(zip(budget_names, budget_data.T))
output_f = budget['frequency_Hz']
electronic = np.hypot(budget['carrier b'], budget['sideband b'])
readout = np.hypot(budget['Newport carrier readout'], budget['Newport sideband readout'])
mod = budget['modulation m']
total = np.sqrt(electronic**2 + readout**2 + mod**2)
assert np.allclose(total, budget['total_included_ASD'], rtol=1e-12, atol=0)

for show_components, name in [(False, 'total_noise_tdi2_corrected'),
                              (True, 'total_noise_tdi2_corrected_budget')]:
    with plt.rc_context({'font.size': 10, 'axes.labelsize': 11, 'legend.fontsize': 8.5}):
        fig, ax = plt.subplots(figsize=(7, 4.8))
        if show_components:
            ax.loglog(output_f, electronic, color=colors['baseline'], lw=0.9,
                      label='Electronic baseline contribution')
            ax.loglog(output_f, mod, color=colors['modulation'], lw=0.9,
                      label='Modulation contribution')
            ax.loglog(output_f, readout, color=colors['carrier'], lw=0.9,
                      label='Newport readout + ADC')
        ax.loglog(output_f, budget['single_link_reference_in_TDI_ASD'],
                  color='#777777', ls='--', lw=1.2,
                  label='Single-link reference propagated through TDI 2')
        ax.loglog(output_f, total, color='black', lw=1.6, zorder=6,
                  label=r'Total predicted $X_{2\mathrm{c}}$ noise')
        ax.set(xlim=(fmin, fmax), xlabel='Fourier frequency (Hz)',
               ylabel=r'Phase ASD (cycles/$\sqrt{\mathrm{Hz}}$)')
        ax.grid(which='major', color='#dedede', lw=0.5, ls='--')
        for axis in (ax.xaxis, ax.yaxis):
            axis.set_minor_locator(LogLocator(base=10, subs=np.arange(2,10), numticks=100))
            axis.set_minor_formatter(NullFormatter())
        ax.legend(loc='lower left', frameon=True)
        modulation_values = ', '.join(f'{config["nu_m_hz"][str(i)]/1e6:g}' for i in [1,2,3])
        electrical_values = ', '.join(f'{config["nu_R_hz"][str(i)]/1e6:g}' for i in [1,2,3])
        ax.set_title('Static TDI 2 + clock correction; ideal primary-noise cancellation', fontsize=9)
        fig.text(0.54, 0.025,
                 f'Modulation (SC1,2,3): {modulation_values} MHz; electrical carriers: {electrical_values} MHz\n'
                 f'Newport: {pd["P_SC_W"]*1e3:g} mW/beam, '
                 + r'$\beta=' + f'{pd["parameters"]["m"]:g}' + r'$' + '; ADC included',
                 ha='center', fontsize=8)
        fig.subplots_adjust(left=0.12, right=0.98, bottom=0.20, top=0.94)
        for suffix in ['pdf', 'svg', 'png']:
            fig.savefig(OUT / f'{name}.{suffix}', dpi=600)
        plt.close(fig)
np.savetxt(OUT / 'total_noise_tdi2_corrected.csv',
           np.column_stack([output_f, total, electronic, mod, readout,
                            budget['single_link_reference_in_TDI_ASD']]),
           delimiter=',', header='Hz,total_ASD,electronic_ASD,modulation_ASD,readout_ASD,reference_ASD')
print(f'Saved PDF, SVG and 600-dpi PNG variants in {OUT}')
