"""Export article component figures from the audited notebook inputs.

Run: python artikel/make_component_figure.py
Component inputs are unsmoothed. The static corrected-X2 calculation retains shared detector inputs and four independent equivalent electronic link readouts.
"""
from pathlib import Path
import hashlib
import json
import ast

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullFormatter
import numpy as np
from scipy.special import jv
from scipy.constants import elementary_charge, Boltzmann

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
# Prospective detector operating point, with ideal matched three-way fanout.
# Preserve the raw measurements and the notebook's previous assumptions file.
config['nu_m_hz'] = {'1':35e6, '2':36e6, '3':34e6}
config['gamma_hz'] = {key: value + config['nu_m_hz'][str(ast.literal_eval(key)[1])]
                    - config['nu_m_hz'][str(ast.literal_eval(key)[0])]
                    for key, value in config['alpha_hz'].items()}
pd = config['newport']
par = pd['parameters']
pd['P_SC_W'] = pd['P_REF_W'] = power = 4e-3
fanout = 1/np.sqrt(3)
par['fanout_voltage_ratio'] = fanout
par['G_total'] = 50*fanout
pd['power_convention'] = '4 mW per beam incident at detector; ideal three-way RF split'
i_peak = {ch:2*par['Res']*np.sqrt(par['het_eff'])*power*abs(jv(n,par['m']))
          for ch,n in [('carrier',0),('sideband',1)]}
i_noise = {
    'shot (including dark)':np.sqrt(2*elementary_charge*(2*par['Res']*power+par['I_dark'])),
    'Johnson':np.sqrt(4*Boltzmann*par['T']/par['R_term']),
    'RIN':2*par['Res']*power*par['RIN'],
    'ADC':par['adc_FSR']/(2**par['adc_bits']*par['G_total']*np.sqrt(6*par['adc_fs']))
}
pd['components_cycles_per_sqrt_Hz'] = {
    ch:{name:np.sqrt(2)*value/(2*np.pi*peak) for name,value in i_noise.items()}
    for ch,peak in i_peak.items()}
pd['total_cycles_per_sqrt_Hz'] = {
    ch:np.sqrt(sum(v*v for v in terms.values()))
    for ch,terms in pd['components_cycles_per_sqrt_Hz'].items()}
carrier = pd['total_cycles_per_sqrt_Hz']['carrier']
sideband = pd['total_cycles_per_sqrt_Hz']['sideband']
config['article_budget'] = {
    'electronics':'same measured PSD per carrier/sideband link; independent equivalent link noises',
    'detector':'shared before fanout; independent detector channels; exclude ADC from this term',
    'modulation':'existing estimator assigned to independent source modulation phases; measurement to be repeated',
    'ADC':'shown in input readout prediction; not added again to measured electronic baseline',
    'primary_noises':'ideal cancellation; static delays',
}
assert np.isclose(sideband/carrier, abs(jv(0,par['m'])/jv(1,par['m'])))
peak_power = 2*power*(1+np.sqrt(par['het_eff']))
vpp = 2*2*par['Res']*np.sqrt(par['het_eff'])*power*par['G_total']
assert peak_power < 20e-3 and vpp < par['adc_FSR']
print('Detector model: mean/peak power mW:', 2*power*1e3, peak_power*1e3)
print('ADC beat Vpp:',vpp,'; input phase ASD carrier/SB:',carrier,sideband)

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
                  label='Sideband-difference estimator (measured)', zorder=4)
        ax.loglog(freq, np.full_like(freq, carrier), color=colors['carrier'], lw=1.3,
                  ls='-.', label='Carrier readout (linear model)')
        ax.loglog(freq, np.full_like(freq, sideband), color=colors['sideband'], lw=1.3,
                  ls=':', label='Sideband readout (linear model)')
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
                f'Linear model: {pd["P_SC_W"]*1e3:g} mW/beam, '
                + r'$\mu_{\mathrm{EOM}}=' + f'{pd["parameters"]["m"]:g}' + r'$' + '\nADC noise included',
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

# Static Michelson and clock correction, with the article's source placement.
links = [(1,2),(2,1),(1,3),(3,1)]
output_f = freq
nu_R = {int(i):v for i,v in config['nu_R_hz'].items()}
nu_m = {int(i):v for i,v in config['nu_m_hz'].items()}
alpha = {(i,j):nu_R[j]-nu_R[i] for i,j in links}
z = {l:np.exp(-2j*np.pi*freq*config['delays_seconds'][str(l)]) for l in links}
A, B = z[1,2]*z[2,1], z[1,3]*z[3,1]
P = {(1,2):-(1-B), (2,1):-(1-B)*z[1,2], (1,3):1-A, (3,1):(1-A)*z[1,3]}
K = {(1,2):-(alpha[1,3]+B*alpha[3,1]),
     (2,1):-z[1,2]*(alpha[1,3]+B*alpha[3,1])+(1-B)*z[1,2]*alpha[2,1],
     (1,3):alpha[1,2]+A*alpha[2,1],
     (3,1):z[1,3]*(alpha[1,2]+A*alpha[2,1])-(1-A)*z[1,3]*alpha[3,1]}
P = {l:(1-A*B)*v for l,v in P.items()}
K = {l:(1-A*B)*v for l,v in K.items()}

# Cancel each physical laser and common clock source, before forming PSDs.
for sc in [1,2,3]:
    hp=sum(P[i,j]*(z[i,j]*(j==sc)-(i==sc)) for i,j in links)
    hq=sum(-P[i,j]*alpha[i,j]*(i==sc)+K[i,j]*(z[i,j]*(j==sc)-(i==sc)) for i,j in links)
    assert np.max(abs(hp)) < 1e-12
    assert np.max(abs(hq)) < 1e-6
# Four equal unit-weight independent channels yield sqrt(4) in ASD.
assert np.isclose(np.sqrt(sum(1.0 for l in links)), 2.0)
# Equal-arm raw X2 weights have the known extra differencing factors.
tau=config['delays_seconds'][str(links[0])]
raw_gain=np.sqrt(sum(abs(v)**2 for v in P.values()))
assert np.allclose(raw_gain,8*abs(np.sin(2*np.pi*freq*tau)*np.sin(4*np.pi*freq*tau)),atol=1e-12)

def interp_psd(data, is_asd):
    good=(data[:,0]>0)&np.isfinite(data[:,1])&(data[:,1]>0)
    grid,values=data[good,0],data[good,1]
    assert freq[0]>=grid[0] and freq[-1]<=grid[-1]
    return np.exp(np.interp(np.log(freq),np.log(grid),np.log(values**2 if is_asd else values)))
# Interpolate full measured support, rather than dropping neighboring end bins.
baseline_full=np.loadtxt(ROOT/config['input_paths']['baseline.csv'],delimiter=',',skiprows=1)
modulation_full=np.loadtxt(ROOT/config['input_paths']['modulator_psd.csv'],delimiter=',',comments='#')
Sb=interp_psd(baseline_full,True)
Sm=interp_psd(modulation_full,False)
hc={l:P[l]-K[l]/nu_m[l[1]] for l in links}
hs={l:K[l]/nu_m[l[1]] for l in links}
electronic=np.sqrt(Sb*sum(abs(hc[l])**2+abs(hs[l])**2 for l in links))
# chi_i = p_i^SB - p_i^c and source modulation have the same delayed-source map.
H={sc:sum(K[i,j]/nu_m[j]*(z[i,j]*(j==sc)-(i==sc)) for i,j in links) for sc in [1,2,3]}
source_gain=sum(abs(v)**2 for v in H.values())
detector_difference_psd=sum(value**2 for terms in pd['components_cycles_per_sqrt_Hz'].values()
                            for name,value in terms.items() if name!='ADC')
readout=np.sqrt(source_gain*detector_difference_psd)
mod=np.sqrt(source_gain*Sm)
total=np.sqrt(electronic**2+readout**2+mod**2)
budget={'single_link_reference_in_TDI_ASD':raw_gain*reference}
config['article_budget']['detector_difference_psd']=detector_difference_psd
(OUT/'figure_parameters.json').write_text(json.dumps(config,indent=2))
print('Source and four-link transfer checks passed; total uses shared detector inputs.')

for show_components, name in [(False, 'total_noise_tdi2_corrected'),
                              (True, 'total_noise_tdi2_corrected_budget')]:
    with plt.rc_context({'font.size': 10, 'axes.labelsize': 11, 'legend.fontsize': 8.5}):
        fig, ax = plt.subplots(figsize=(7, 4.8))
        if show_components:
            ax.loglog(output_f, electronic, color=colors['baseline'], lw=0.9,
                      label='Electronic baseline contribution')
            ax.loglog(output_f, mod, color=colors['modulation'], lw=0.9,
                      label='Modulation estimate')
            ax.loglog(output_f, readout, color=colors['carrier'], lw=0.9,
                      label='Shared detector contribution')
        ax.loglog(output_f, budget['single_link_reference_in_TDI_ASD'],
                  color='#777777', ls='--', lw=1.2,
                  label='Single-link reference propagated through TDI 2')
        ax.loglog(output_f, total, color='black', lw=1.6, zorder=6,
                  label=r'Estimated $X_{2\mathrm{c}}$ noise')
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
                 f'Linear model: {pd["P_SC_W"]*1e3:g} mW/beam, '
                 + r'$\mu_{\mathrm{EOM}}=' + f'{pd["parameters"]["m"]:g}' + r'$' + '; ADC covered by electronic baseline',
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
