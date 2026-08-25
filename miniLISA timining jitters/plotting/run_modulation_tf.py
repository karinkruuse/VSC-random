"""
run_modulation_tf.py
---------------------
FAST step. Loads the SymPy transfer functions pickled by
build_modulation_tf.py and numerically evaluates/plots the
modulation-noise ASD for whatever modulation frequencies (nu^m) you
want -- no SymPy re-derivation needed.

Run build_modulation_tf.py once first (or whenever L, dL, nu1/nu2/nu3,
or the TDI combination change).
"""
import pickle
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from sympy import lambdify

HERE = Path(__file__).parent
MODULATOR_PSD_FILE = HERE / '../../measured noises/modulator_psd.csv'


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
    "xtick.labelsize"    : 15,
    "ytick.labelsize"    : 15,
    "axes.labelsize"     : 13,
    "legend.fontsize"    : 14,
    "legend.framealpha"  : 0.92,
    "legend.edgecolor"   : "#cccccc",
    "legend.handlelength": 2.0,
    "figure.dpi"         : 600,
})

def load_modulation_transfer_functions(tdi_name='X2', path=None):
    if path is None:
        path = HERE / f'modulation_tf_{tdi_name}.pkl'
    with open(path, 'rb') as f:
        return pickle.load(f)


def S_modulation(freqs, psd_file=MODULATOR_PSD_FILE):
    data = np.loadtxt(psd_file, delimiter=',', comments='#')
    data = data[data[:, 0] > 0]
    interp = interp1d(data[:, 0], data[:, 1], bounds_error=False,
                       fill_value=(data[0, 1], data[-1, 1]))
    return interp(freqs) / freqs**2   # Hz^2/Hz -> cyc^2/Hz


def evaluate_modulation_asd(tf_data, freqs, nu_m1, nu_m2, nu_m3):
    """
    Numerically evaluate the already-derived modulation-noise transfer
    functions at modulation frequencies nu_m1/nu_m2/nu_m3 [Hz], over
    `freqs` [Hz]. Cheap -- just lambdify + array eval, no SymPy
    simplification.
    """
    omega_sym = tf_data['omega_sym']
    omega1m, omega2m, omega3m = tf_data['omega1m'], tf_data['omega2m'], tf_data['omega3m']
    omegas = 2*np.pi*freqs
    om1m, om2m, om3m = 2*np.pi*nu_m1, 2*np.pi*nu_m2, 2*np.pi*nu_m3

    S_input = S_modulation(freqs)

    asd_srcs_phase = []
    for key, H_sym in tf_data['H'].items():
        if H_sym == 0:
            asd_srcs_phase.append(np.zeros(len(freqs)))
            continue
        H_num = lambdify((omega_sym, omega1m, omega2m, omega3m), H_sym, modules='numpy')
        H_vals = np.ones(len(freqs), dtype=complex) * H_num(omegas, om1m, om2m, om3m)
        psd = np.abs(H_vals)**2 * S_input
        asd_srcs_phase.append(np.sqrt(psd))

    asd_total_phase = np.sqrt(sum(a**2 for a in asd_srcs_phase))
    asd_srcs_freq = [a*freqs for a in asd_srcs_phase]
    asd_total_freq = asd_total_phase*freqs

    return {
        'srcs_freq': asd_srcs_freq, 'total_freq': asd_total_freq,
        'srcs_phase': asd_srcs_phase, 'total_phase': asd_total_phase,
    }


def plot_modulation_asd(freqs, curves, tdi_name='X2', L=2.5e9/299792458.0,
                          lambda_laser=1064e-9, save_path=None):
    """
    curves: list of (label, res, color) tuples, each `res` from
    evaluate_modulation_asd(), overlaid on the same axes.
    """
    omegas = 2*np.pi*freqs
    Sx_alloc = (64*omegas**2 * np.sin(omegas*L)**2 * np.sin(2*omegas*L)**2
                * (1e-12/lambda_laser)**2 * (1+(2e-3/freqs)**4))
    asd_alloc_freq  = np.sqrt(Sx_alloc)
    asd_alloc_phase = asd_alloc_freq / freqs

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, (key_tot, alloc, ylabel) in zip(axes, [
        ('total_freq',  asd_alloc_freq,  r'ASD [cycles / $\sqrt{\mathrm{Hz}}$]'),
        ('total_phase', asd_alloc_phase, r'ASD [cycles / $\sqrt{\mathrm{Hz}}$]'),
    ]):
        for label, res, color in curves:
            ax.loglog(freqs, res[key_tot], lw=1.5, color=color,
                      label=f'{tdi_name}$^c$ modulation noise ({label})', zorder=10)
        ax.loglog(freqs, alloc, lw=1, color='gray', label='1 pm alloc.')
        ax.loglog(freqs, 15*alloc, lw=1, color='black', label='15 pm alloc.')
        ax.set_xlabel('Fourier Frequency [Hz]')
        ax.set_ylabel(ylabel)
        ax.set_xlim([freqs[0], freqs[-1]])
        ax.legend(fontsize=8)
        ax.grid(True, which='both', alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', transparent=True)
    return fig


if __name__ == '__main__':
    tf_data = load_modulation_transfer_functions(tdi_name='X2')

    freqs = np.logspace(-4, 0, 2000)

    res_350M = evaluate_modulation_asd(tf_data, freqs, nu_m1=350e6, nu_m2=350e6, nu_m3=350e6)
    res_2G   = evaluate_modulation_asd(tf_data, freqs, nu_m1=2e9,   nu_m2=2e9,   nu_m3=2e9)



    color_extrapolated = "#d71b2f"   # (215, 27, 47)  red
    color_measured     = "#295f24"   # (41, 95, 36)   green
    color_modulator    = "#821770"   # (130, 23, 112) magenta
    color_delayline    = "#2d13b4"   # (45, 19, 180)  blue

    plot_modulation_asd(
        freqs,
        [('350 MHz', res_350M, color_modulator), ('2 GHz', res_2G, color_measured)],
        tdi_name=tf_data['tdi_name'],
        save_path=HERE / f"{tf_data['tdi_name']}_modulation_split.png",
    )
    #plt.show()
