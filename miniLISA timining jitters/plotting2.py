"""
noise_budget.py
---------------
Computes and plots TDI noise budgets directly from SymPy transfer functions.

Change the settings at the top to switch noise type, TDI combination,
and whether to show the clock-corrected residual alongside the uncorrected.
"""

# ══════════════════════════════════════════════════════════════════════════════
# USER SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
# One noise type, or a list for combined plot:
#   'clock' | 'board' | 'modulation' | 'optical' | 'optical_sb' | 'board_baseline'
NOISE_TO_PLOT  = ['board']   # string or list of strings
TDI_NAME       = 'X2'       # 'X1' | 'alpha1' | 'X2'
SHOW_CORRECTED = True       # also compute and overlay clock-corrected version

# Data files (set to None to use filler models)
MODULATOR_PSD_FILE = 'modulator_psd.csv'
BASELINE_ASD_FILE  = 'baseline.csv'

# ── Physical parameters ───────────────────────────────────────────────────────
c            = 299792458.0
lambda_laser = 1064e-9
L            = 2.5e9 / c

# ── Armlength rates of change [s/s] — set to 0 for static arms ───────────────
# In the static case these are all zero and X2 reduces to X1 exactly.
# Set to realistic LISA values (e.g. ~1e-8 s/s) to see the τ̇-dependent residual.
dL = 5e-8   # common value used for all six links when arms are symmetric

# ── Heterodyne & modulation frequencies [Hz] ─────────────────────────────────
nu1  = 15.0e6;  nu2  =  6.9e6;  nu3  = 13.6e6
mod_order = 7
num1 =  2.4*10**mod_order;  num2 =  2.4*10**mod_order;  num3 =  2.4*10**mod_order

# ══════════════════════════════════════════════════════════════════════════════
# IMPORTS
# ══════════════════════════════════════════════════════════════════════════════
from sympy import (Function, Symbol, symbols, simplify, expand, collect,
                   exp, I, lambdify, latex)
from sympy import Function as SympyFunction
from sympy.core.function import AppliedUndef
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# ══════════════════════════════════════════════════════════════════════════════
# FREQUENCY GRID & ALLOCATION
# ══════════════════════════════════════════════════════════════════════════════
freqs  = np.logspace(-4, 0, 2000)
omegas = 2*np.pi*freqs

Sx_alloc        = (64*omegas**2 * np.sin(omegas*L)**2 * np.sin(2*omegas*L)**2
                   * (1e-12/lambda_laser)**2 * (1+(2e-3/freqs)**4))
asd_alloc_freq  = np.sqrt(Sx_alloc)
asd_alloc_phase = asd_alloc_freq / freqs

# ══════════════════════════════════════════════════════════════════════════════
# INPUT NOISE PSDs
# ══════════════════════════════════════════════════════════════════════════════
def S_clock(freqs):
    return 4e-27 / freqs

def S_board(freqs):
    return 4e-27 / freqs

def S_modulation(freqs):
    data = np.loadtxt(MODULATOR_PSD_FILE, delimiter=',', comments='#')
    data = data[data[:,0] > 0]
    interp = interp1d(data[:,0], data[:,1], bounds_error=False,
                      fill_value=(data[0,1], data[-1,1]))
    return interp(freqs) / freqs**2   # Hz^2/Hz -> cyc^2/Hz

def S_optical(freqs):
    return (600 * 1e-6 * np.sqrt(1 + (0.7e-3/freqs)**4) / 2.4e9 * 24e6)**2

def S_board_baseline(freqs):
    data = np.loadtxt(BASELINE_ASD_FILE, delimiter=',', skiprows=1)
    data = data[data[:,0] > 0]
    interp = interp1d(data[:,0], data[:,1]**2, bounds_error=False,
                      fill_value=(data[0,1]**2, data[-1,1]**2))
    return interp(freqs)

# ══════════════════════════════════════════════════════════════════════════════
# SYMPY DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════
t = Symbol('t')

tau12,tau21,tau13,tau31,tau23,tau32 = symbols(
    r'\tau_{12} \tau_{21} \tau_{13} \tau_{31} \tau_{23} \tau_{32}',
    real=True, positive=True)

# τ̇ symbols — rate of change of each one-way light travel time [s/s]
dtau12,dtau21,dtau13,dtau31,dtau23,dtau32 = symbols(
    r'\dot\tau_{12} \dot\tau_{21} \dot\tau_{13} \dot\tau_{31} \dot\tau_{23} \dot\tau_{32}',
    real=True)

omega1,omega2,omega3     = symbols(r'\omega_1 \omega_2 \omega_3', real=True)
omega1m,omega2m,omega3m  = symbols(r'\omega_1^m \omega_2^m \omega_3^m', real=True)
omegaREFA,omegaREFB,omegaREFC = symbols(
    r'\omega^{REF}_A \omega^{REF}_B \omega^{REF}_C', real=True)

phi1=Function(r'\phi_1'); phi2=Function(r'\phi_2'); phi3=Function(r'\phi_3')
phiREF=Function(r'\phi_{REF}')
epsilonA=Function(r'\epsilon_A'); epsilonB=Function(r'\epsilon_B')
epsilonC=Function(r'\epsilon_C')
q1=Function('q_1'); q2=Function('q_2'); q3=Function('q_3')
N1_1=Function('N_{1_1}'); N2_2=Function('N_{2_2}'); N3_3=Function('N_{3_3}')
N1_2=Function('N_{1_2}'); N1_3=Function('N_{1_3}')
N2_1=Function('N_{2_1}'); N2_3=Function('N_{2_3}')
N3_1=Function('N_{3_1}'); N3_2=Function('N_{3_2}')
n1_1=Function('n_{1_1}'); n2_2=Function('n_{2_2}'); n3_3=Function('n_{3_3}')
n1_2=Function('n_{1_2}'); n1_3=Function('n_{1_3}')
n2_1=Function('n_{2_1}'); n2_3=Function('n_{2_3}')
n3_1=Function('n_{3_1}'); n3_2=Function('n_{3_2}')
N1_m=Function('P_{1}^{m}'); N2_m=Function('P_{2}^{m}'); N3_m=Function('P_{3}^{m}')
B_12=Function('B_{12}'); B_21=Function('B_{21}')
B_13=Function('B_{13}'); B_31=Function('B_{31}')
B_23=Function('B_{23}'); B_32=Function('B_{32}')
B_12S=Function('B12S'); B_21S=Function('B21S')
B_13S=Function('B13S'); B_31S=Function('B31S')
B_23S=Function('B23S'); B_32S=Function('B32S')

# ── Delay operator dictionaries ───────────────────────────────────────────────
tau  = {(1,2):tau12, (2,1):tau21, (1,3):tau13, (3,1):tau31, (2,3):tau23, (3,2):tau32}
dtau = {(1,2):dtau12,(2,1):dtau21,(1,3):dtau13,(3,1):dtau31,(2,3):dtau23,(3,2):dtau32}

def D(expr, tau_key):
    """
    Apply a single delay.
    - tau_key as tuple (i,j): time-varying delay tau_ij(t) = tau_ij^0 + dtau_ij * t
      This is the non-commutative Doppler-delay operator needed for 2nd gen TDI.
    - tau_key as sympy symbol: constant delay (used for X1/alpha1).
    """
    if expr == 0:
        return 0
    if isinstance(tau_key, tuple):
        tau_val = tau[tau_key] + dtau[tau_key] * t
    else:
        tau_val = tau_key
    return expr.subs(t, t - tau_val)

def Dn(expr, *tau_keys):
    """
    Apply a sequence of delays left-to-right, each evaluated at the
    already-shifted time from previous delays. This encodes non-commutativity:
      Dn(f, (1,2), (2,1))  !=  Dn(f, (2,1), (1,2))  when dtau != 0.
    Pass tuples for time-varying links, or symbols for constant delays.
    """
    for tau_key in tau_keys:
        expr = D(expr, tau_key)
    return expr

def drop_dtau_squared(expr):
    """
    Drop all terms of order τ̇² or higher in the time-arguments of noise
    functions. This linearises the delay composition, matching the 2nd gen
    TDI approximation used in Hartwig & Bayle (2021).
    """
    dtau_set = {dtau12, dtau21, dtau13, dtau31, dtau23, dtau32}
    def clean_arg(arg):
        result = 0
        for term in expand(arg).as_ordered_terms():
            deg = sum(term.as_powers_dict().get(dv, 0) for dv in dtau_set)
            if deg <= 1:
                result += term
        return result
    return expr.replace(
        lambda f: isinstance(f, AppliedUndef),
        lambda f: f.func(clean_arg(f.args[0]))
    )

sc = {
    1: (phi1, q1, omega1, omega1m, epsilonA, omegaREFA, N1_m),
    2: (phi2, q2, omega2, omega2m, epsilonB, omegaREFB, N2_m),
    3: (phi3, q3, omega3, omega3m, epsilonC, omegaREFC, N3_m),
}
N = {
    (1,2):(N1_2,n1_2),(1,3):(N1_3,n1_3),
    (2,1):(N2_1,n2_1),(2,3):(N2_3,n2_3),
    (3,1):(N3_1,n3_1),(3,2):(N3_3,n3_3),
}
B = {
    (1,2):(B_12, B_12S), (1,3):(B_13, B_13S),
    (2,1):(B_21, B_21S), (2,3):(B_23, B_23S),
    (3,1):(B_31, B_31S), (3,2):(B_32, B_32S),
}

master_noise_funcs = [
    phi1,phi2,phi3, q1,q2,q3, epsilonA,epsilonB,epsilonC,
    N1_m,N2_m,N3_m,
    N1_1,N1_2,N1_3,N2_1,N2_2,N2_3,N3_1,N3_2,N3_3,
    n1_1,n1_2,n1_3,n2_1,n2_2,n2_3,n3_1,n3_2,n3_3,
    B_12,B_21,B_13,B_31,B_23,B_32,
    B_12S,B_21S,B_13S,B_31S,B_23S,B_32S,
]
omega_sym = Symbol('omega', real=True, positive=True)

# ══════════════════════════════════════════════════════════════════════════════
# ETA BUILDERS
# ══════════════════════════════════════════════════════════════════════════════
def build_eta_for_noise(noise_type):
    """Single isolated noise type — for uncorrected TDI.
    Uses tuple-keyed D() so delays are time-varying for X2."""
    eta = {}
    for (i,j) in tau:
        phi_i,q_i,om_i,omm_i,eps_i,_,N_i_m = sc[i]
        phi_j,q_j,om_j,omm_j,eps_j,_,N_j_m = sc[j]
        Nij,nij = N[(i,j)]; Bij,BijSB = B[(i,j)]
        if   noise_type == 'phi':            eta[(i,j)] = expand(D(phi_j(t),(i,j)) - phi_i(t))
        elif noise_type == 'clock':          eta[(i,j)] = expand(-(om_j-om_i)*q_i(t))
        elif noise_type == 'board':          eta[(i,j)] = expand(om_j*(eps_i(t)-D(eps_i(t),(i,j))))
        elif noise_type == 'optical':        eta[(i,j)] = Nij(t)
        elif noise_type == 'optical_sb':     eta[(i,j)] = 0
        elif noise_type == 'modulation':     eta[(i,j)] = 0
        elif noise_type == 'board_baseline': eta[(i,j)] = Bij(t)
        else:                                eta[(i,j)] = 0
    return eta

def build_eta_and_sb_for_noise(noise_type):
    """Build carrier eta and sideband etaSB for a single noise type.
    Uses tuple-keyed D() so delays are time-varying for X2."""
    eta = {}; etaSB = {}
    for (i,j) in tau:
        phi_i,q_i,om_i,omm_i,eps_i,_,N_i_m = sc[i]
        phi_j,q_j,om_j,omm_j,eps_j,_,N_j_m = sc[j]
        Nij,nij = N[(i,j)]; Bij,BijSB = B[(i,j)]

        # carrier
        if   noise_type == 'phi':            c = expand(D(phi_j(t),(i,j)) - phi_i(t))
        elif noise_type == 'clock':          c = expand(-(om_j-om_i)*q_i(t))
        elif noise_type == 'board':          c = expand(om_j*(eps_i(t)-D(eps_i(t),(i,j))))
        elif noise_type == 'optical':        c = Nij(t)
        elif noise_type == 'optical_sb':     c = 0
        elif noise_type == 'modulation':     c = 0
        else:                                c = Bij(t)

        # sideband
        if   noise_type == 'phi':        sb = expand(D(phi_j(t),(i,j)) - phi_i(t))
        elif noise_type == 'clock':      sb = expand(-(om_j-om_i+omm_j-omm_i)*q_i(t)
                                                     - omm_i*q_i(t)
                                                     + omm_j*D(q_j(t),(i,j)))
        elif noise_type == 'board':      sb = expand((om_j+omm_j)*(eps_i(t)-D(eps_i(t),(i,j))))
        elif noise_type == 'optical':    sb = 0
        elif noise_type == 'optical_sb': sb = nij(t)
        elif noise_type == 'modulation': sb = expand(N_i_m(t)-D(N_j_m(t),(i,j)))
        else:                            sb = BijSB(t)

        eta[(i,j)] = c; etaSB[(i,j)] = sb
    return eta, etaSB

# ══════════════════════════════════════════════════════════════════════════════
# TDI COMBINATION BUILDERS
# ══════════════════════════════════════════════════════════════════════════════
def build_tdi_from_eta(eta, tdi_name='X1'):
    if tdi_name == 'X1':
        # X1 uses constant delays — pass symbols directly
        def P12(e): return e - D(e, tau13+tau31)
        def P13(e): return -(e - D(e, tau12+tau21))
        return expand(P13(eta[(1,3)]+D(eta[(3,1)],tau13)) + P12(eta[(1,2)]+D(eta[(2,1)],tau12)))

    elif tdi_name == 'alpha1':
        return expand(
              eta[(1,2)]+D(eta[(2,3)],tau12)+D(eta[(3,1)],tau12+tau23)
            - eta[(1,3)]-D(eta[(3,2)],tau13)-D(eta[(2,1)],tau13+tau32))

    elif tdi_name == 'X2':
        # 2nd gen Michelson — all delays via tuples for non-commutativity.
        # Delay notation: D_131 = Dn(·,(3,1),(1,3)), etc.
        def P12_X2(e):
            return -(  e
                     - Dn(e, (3,1),(1,3))
                     - Dn(e, (2,1),(1,2),(3,1),(1,3))
                     + Dn(e, (3,1),(1,3),(3,1),(1,3),(2,1),(1,2)))
        def P13_X2(e):
            return  (  e
                     - Dn(e, (2,1),(1,2))
                     - Dn(e, (3,1),(1,3),(2,1),(1,2))
                     + Dn(e, (2,1),(1,2),(2,1),(1,2),(3,1),(1,3)))
        def P21_X2(e): return P12_X2(Dn(e, (1,2)))
        def P31_X2(e): return P13_X2(Dn(e, (1,3)))

        X2 = expand(
              P12_X2(eta[(1,2)]) + P21_X2(eta[(2,1)])
            + P13_X2(eta[(1,3)]) + P31_X2(eta[(3,1)])
        )
        # Drop τ̇² terms to stay in the linear (2nd gen) approximation
        return drop_dtau_squared(X2)

    else:
        raise ValueError(f"Unknown TDI '{tdi_name}'")


def build_corrected_tdi(noise_type, tdi_name='X1'):
    """
    Build the clock-corrected TDI for a single noise type.
    r_{ij} = (eta_{ij} - etaSB_{ij}) / omega_j^m  (sign matches modelling_copy.ipynb)
    """
    eta, etaSB = build_eta_and_sb_for_noise(noise_type)

    r = {}
    for (i,j) in tau:
        _,_,_,omm_j,_,_,_ = sc[j]
        r[(i,j)] = simplify((eta[(i,j)] - etaSB[(i,j)]) / omm_j)

    if tdi_name == 'X1':
        X1_base = build_tdi_from_eta(eta, 'X1')
        R = {}
        R[(1,2)] = -(r[(1,3)] + D(r[(3,1)], tau13))
        R[(1,3)] =   r[(1,2)] + D(r[(2,1)], tau12)
        R[(2,1)] =  (r[(1,2)] - r[(1,3)]
                     - D(r[(3,1)], tau13) - D(r[(1,2)], tau13+tau31))
        R[(3,1)] = (-r[(1,3)] + r[(1,2)]
                     + D(r[(2,1)], tau12) + D(r[(1,3)], tau12+tau21))
        R[(2,3)] = 0; R[(3,2)] = 0
        a = {(i,j): sc[i][2]-sc[j][2] for (i,j) in tau}
        correction = 0
        for (i,j,k) in [(1,2,3),(2,3,1),(3,1,2)]:
            correction -= (-a[(i,j)]*R[(i,j)] - a[(i,k)]*R[(i,k)])
        return simplify(X1_base - correction)

    elif tdi_name == 'alpha1':
        alpha_base = build_tdi_from_eta(eta, 'alpha1')
        R_s = {}
        R_s[(1,2)]=0; R_s[(2,3)]=r[(1,2)]
        R_s[(3,1)]=r[(1,2)]+D(r[(2,3)],tau12)
        R_s[(1,3)]=0; R_s[(3,2)]=-r[(1,3)]
        R_s[(2,1)]=-(r[(1,3)]+D(r[(3,2)],tau13))
        a = {(i,j): sc[i][2]-sc[j][2] for (i,j) in tau}
        correction = 0
        for (i,j,k) in [(1,2,3),(2,3,1),(3,1,2)]:
            correction -= (-a[(i,j)]*R_s[(i,j)] - a[(i,k)]*R_s[(i,k)])
        return simplify(alpha_base - correction)

    elif tdi_name == 'X2':
        # R_X2 from Hartwig & Bayle (2021) eq. 13.29, all delays via tuples
        X2_base = build_tdi_from_eta(eta, 'X2')

        RT12 = r[(1,2)] + Dn(r[(2,1)], (1,2))
        RT13 = r[(1,3)] + Dn(r[(3,1)], (1,3))

        R_X2 = {}
        # (13.29a)
        R_X2[(1,2)] = (
            - (RT12 - Dn(RT12, (3,1),(1,3)))
            + (2*RT13 - Dn(RT13, (2,1),(1,2)) - Dn(RT13, (3,1),(1,3),(2,1),(1,2)))
        )
        # (13.29b)
        R_X2[(2,3)] = 0
        # (13.29c)
        R_X2[(3,1)] = (
            - (2*RT12 - Dn(RT12, (3,1),(1,3)) - Dn(RT12, (2,1),(1,2),(3,1),(1,3)))
            + (RT13 - Dn(RT13, (2,1),(1,2)))
            + (  r[(1,3)]
               - Dn(r[(1,3)], (2,1),(1,2))
               - Dn(r[(1,3)], (3,1),(1,3),(2,1),(1,2))
               + Dn(r[(1,3)], (2,1),(1,2),(2,1),(1,2),(3,1),(1,3)))
        )
        # (13.29d)
        R_X2[(2,1)] = (
            - (RT12 - Dn(RT12, (3,1),(1,3)))
            - (  r[(1,2)]
               - Dn(r[(1,2)], (3,1),(1,3))
               - Dn(r[(1,2)], (2,1),(1,2),(3,1),(1,3))
               + Dn(r[(1,2)], (3,1),(1,3),(3,1),(1,3),(2,1),(1,2)))
            + (2*RT13 - Dn(RT13, (2,1),(1,2)) - Dn(RT13, (3,1),(1,3),(2,1),(1,2)))
        )
        # (13.29e)
        R_X2[(3,2)] = 0
        # (13.29f)
        R_X2[(1,3)] = (
            - (2*RT12 - Dn(RT12, (3,1),(1,3)) - Dn(RT12, (2,1),(1,2),(3,1),(1,3)))
            + (RT13 - Dn(RT13, (2,1),(1,2)))
        )

        a = {(i,j): sc[i][2]-sc[j][2] for (i,j) in tau}
        correction_X2 = 0
        for (i,j,k) in [(1,2,3),(2,3,1),(3,1,2)]:
            correction_X2 -= (-a[(i,j)]*R_X2[(i,j)] - a[(i,k)]*R_X2[(i,k)])

        X2c = drop_dtau_squared(expand(X2_base + correction_X2))
        return X2c

    else:
        raise ValueError(f"Unknown TDI '{tdi_name}'")

# ══════════════════════════════════════════════════════════════════════════════
# TRANSFER FUNCTION EXTRACTOR
# ══════════════════════════════════════════════════════════════════════════════
def get_transfer_function(tdi_expr, noise_func):
    """Extract H(omega) for noise_func; zeros out all other noise functions."""
    zero_subs = {}
    for fn in master_noise_funcs:
        if fn == noise_func: continue
        for inst in tdi_expr.atoms(SympyFunction):
            if inst.func == fn: zero_subs[inst] = 0
    expr2 = tdi_expr.subs(zero_subs)
    phase_subs = {inst: exp(-I*omega_sym*(t-inst.args[0]))
                  for inst in expr2.atoms(SympyFunction) if inst.func == noise_func}
    return expand(expr2.subs(phase_subs))

# ══════════════════════════════════════════════════════════════════════════════
# NOISE TYPE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
noise_config = {
    'clock': {
        'funcs': [q1,q2,q3], 'labels': [r'$q_1$',r'$q_2$',r'$q_3$'],
        'S_func': S_clock, 'divide_2pi': True, 'units': 'freq',
        'ylabel_f': r'ASD [Hz / $\sqrt{\mathrm{Hz}}$]',
        'ylabel_p': r'ASD [cycles / $\sqrt{\mathrm{Hz}}$]',
        'title': r'Clock noise ($q$)',
    },
    'board': {
        'funcs': [epsilonA,epsilonB,epsilonC],
        'labels': [r'$\epsilon_A$',r'$\epsilon_B$',r'$\epsilon_C$'],
        'S_func': S_board, 'divide_2pi': True, 'units': 'freq',
        'ylabel_f': r'ASD [Hz / $\sqrt{\mathrm{Hz}}$]',
        'ylabel_p': r'ASD [cycles / $\sqrt{\mathrm{Hz}}$]',
        'title': r'Board jitter ($\epsilon$)',
    },
    'modulation': {
        'funcs': [N1_m,N2_m,N3_m], 'labels': [r'$N_1^m$',r'$N_2^m$',r'$N_3^m$'],
        'S_func': S_modulation, 'divide_2pi': False, 'units': 'cycles',
        'ylabel_f': r'ASD [cycles / $\sqrt{\mathrm{Hz}}$]',
        'ylabel_p': r'ASD [cycles / $\sqrt{\mathrm{Hz}}$]',
        'title': r'Modulation noise ($N^m$)',
    },
    'optical': {
        'funcs': [N1_1,N1_2,N1_3,N2_1,N2_2,N2_3,N3_1,N3_2,N3_3],
        'labels': [r'$N_{1_1}$',r'$N_{1_2}$',r'$N_{1_3}$',
                   r'$N_{2_1}$',r'$N_{2_2}$',r'$N_{2_3}$',
                   r'$N_{3_1}$',r'$N_{3_2}$',r'$N_{3_3}$'],
        'S_func': S_optical, 'divide_2pi': False, 'units': 'cycles',
        'ylabel_f': r'ASD [cycles / $\sqrt{\mathrm{Hz}}$]',
        'ylabel_p': r'ASD [cycles / $\sqrt{\mathrm{Hz}}$]',
        'title': r'Carrier readout noise ($N$)',
    },
    'optical_sb': {
        'funcs': [n1_1,n1_2,n1_3,n2_1,n2_2,n2_3,n3_1,n3_2,n3_3],
        'labels': [r'$n_{1_1}$',r'$n_{1_2}$',r'$n_{1_3}$',
                   r'$n_{2_1}$',r'$n_{2_2}$',r'$n_{2_3}$',
                   r'$n_{3_1}$',r'$n_{3_2}$',r'$n_{3_3}$'],
        'S_func': S_optical, 'divide_2pi': False, 'units': 'cycles',
        'ylabel_f': r'ASD [cycles / $\sqrt{\mathrm{Hz}}$]',
        'ylabel_p': r'ASD [cycles / $\sqrt{\mathrm{Hz}}$]',
        'title': r'Sideband readout noise ($n$)',
    },
    'board_baseline': {
        'funcs': [B_12,B_21,B_13,B_31,B_23,B_32],
        'labels': [r'$B_{12}$',r'$B_{21}$',r'$B_{13}$',
                   r'$B_{31}$',r'$B_{23}$',r'$B_{32}$'],
        'S_func': S_board_baseline, 'divide_2pi': False, 'units': 'cycles',
        'ylabel_f': r'ASD [cycles / $\sqrt{\mathrm{Hz}}$]',
        'ylabel_p': r'ASD [cycles / $\sqrt{\mathrm{Hz}}$]',
        'title': r'Board baseline ($B$)',
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# NUMERICAL SUBSTITUTION MAP
# ══════════════════════════════════════════════════════════════════════════════
# dtau values: set dL=0 for static arms (exact cancellation in X2 → same as X1).
# Use realistic LISA values (~1e-8 s/s) to model the τ̇-dependent residual.
num_subs = {
    omega1:2*np.pi*nu1,  omega2:2*np.pi*nu2,  omega3:2*np.pi*nu3,
    omega1m:2*np.pi*num1, omega2m:2*np.pi*num2, omega3m:2*np.pi*num3,
    tau12:L, tau21:L, tau13:L, tau31:L, tau23:L, tau32:L,
    dtau12:dL, dtau21:dL, dtau13:dL, dtau31:dL, dtau23:dL, dtau32:dL,
}

# ══════════════════════════════════════════════════════════════════════════════
# EVALUATE: symbolic TDI -> numerical ASD arrays
# ══════════════════════════════════════════════════════════════════════════════
def eval_tdi(tdi_sym, cfg, label=''):
    S_input = cfg['S_func'](freqs)
    print(f"\n── Symbolic H ({label}) ─────────────────────────────────────────────")
    H_list = []
    for fn in cfg['funcs']:
        H_sym = get_transfer_function(tdi_sym, fn)
        print(f"  H[{fn.name}] = {H_sym}")
        if H_sym == 0:
            H_list.append(np.zeros(len(freqs), dtype=complex)); continue

        H_eq  = H_sym.subs(num_subs).subs(t, 0)   # remove residual t after dtau subs
        H_num = lambdify(omega_sym, H_eq, modules='numpy')
        H_vals = np.ones(len(freqs), dtype=complex) * H_num(omegas)
        if cfg['divide_2pi']:
            H_vals /= (2*np.pi)
        H_list.append(H_vals)
    print("─────────────────────────────────────────────────────────────────────")

    psd_list  = [np.abs(H)**2 * S_input for H in H_list]
    psd_total = sum(psd_list)
    asd_srcs  = [np.sqrt(p) for p in psd_list]
    asd_total = np.sqrt(psd_total)

    if cfg['divide_2pi']:
        return {'srcs_freq': asd_srcs,           'total_freq': asd_total,
                'srcs_phase': [a/freqs for a in asd_srcs], 'total_phase': asd_total/freqs}
    else:
        return {'srcs_freq': [a*freqs for a in asd_srcs], 'total_freq': asd_total*freqs,
                'srcs_phase': asd_srcs,           'total_phase': asd_total}

# ══════════════════════════════════════════════════════════════════════════════
# BUILD & RUN
# ══════════════════════════════════════════════════════════════════════════════
noise_list = [NOISE_TO_PLOT] if isinstance(NOISE_TO_PLOT, str) else list(NOISE_TO_PLOT)
plot_title = ' + '.join(noise_list)

def combine_results(results_list):
    combined = {'srcs_freq': [], 'srcs_phase': [],
                'total_freq': np.zeros_like(freqs),
                'total_phase': np.zeros_like(freqs)}
    for res in results_list:
        combined['srcs_freq']  += res['srcs_freq']
        combined['srcs_phase'] += res['srcs_phase']
        combined['total_freq']  = np.sqrt(combined['total_freq']**2 + res['total_freq']**2)
        combined['total_phase'] = np.sqrt(combined['total_phase']**2 + res['total_phase']**2)
    return combined

# ── Uncorrected ───────────────────────────────────────────────────────────────
unc_results = []; all_labels = []
for noise in noise_list:
    cfg_n = noise_config[noise]
    print(f"\nBuilding {TDI_NAME} (uncorrected) for '{noise}'...")
    eta_k   = build_eta_for_noise(noise)
    tdi_unc = build_tdi_from_eta(eta_k, TDI_NAME)
    unc_results.append(eval_tdi(tdi_unc, cfg_n, label=f'unc/{noise}'))
    all_labels += cfg_n['labels']

res_unc = combine_results(unc_results)

# ── Corrected ─────────────────────────────────────────────────────────────────
res_cor = None; res_cor_mod = None
if SHOW_CORRECTED:
    cor_results = []
    for noise in noise_list:
        cfg_n = noise_config[noise]
        print(f"\nBuilding {TDI_NAME} (clock-corrected) for '{noise}'...")
        print("  (runs simplify() + drop_dtau_squared() — may take ~60 s for X2)")
        tdi_cor_n = build_corrected_tdi(noise, TDI_NAME)
        cor_results.append(eval_tdi(tdi_cor_n, cfg_n, label=f'cor/{noise}'))

        if noise == 'clock' and 'modulation' not in noise_list:
            print(f"\nExtracting modulation residual in corrected {TDI_NAME}...")
            res_cor_mod = eval_tdi(tdi_cor_n, noise_config['modulation'],
                                   label='corrected (mod residual)')

    res_cor = combine_results(cor_results)

# ── Plot config ───────────────────────────────────────────────────────────────
if len(noise_list) == 1:
    cfg = noise_config[noise_list[0]]
else:
    all_d2p = [noise_config[n]['divide_2pi'] for n in noise_list]
    same_unit = len(set(all_d2p)) == 1
    all_units = [noise_config[n]['units'] for n in noise_list]
    cfg = {
        'ylabel_f': noise_config[noise_list[0]]['ylabel_f'] if same_unit
                    else r'ASD [mixed units]',
        'ylabel_p': r'ASD [cycles / $\sqrt{\mathrm{Hz}}$]',
        'title': plot_title, 'labels': all_labels,
        'units': 'freq' if all(u == 'freq' for u in all_units) else 'cycles',
        'divide_2pi': noise_config[noise_list[0]]['divide_2pi'],
    }

# ══════════════════════════════════════════════════════════════════════════════
# PLOT
# ══════════════════════════════════════════════════════════════════════════════
freq_info = (f"$\\nu_1={nu1/1e6:.1f}$, $\\nu_2={nu2/1e6:.1f}$, "
             f"$\\nu_3={nu3/1e6:.1f}$ MHz  |  $\\nu^m={num1/1e6:.1f}$ MHz"
             f"  |  $\\dot{{L}}={dL:.1e}$ s/s")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

for ax, (key_src, key_tot, alloc, ylabel) in zip(axes, [
    ('srcs_freq',  'total_freq',  asd_alloc_freq,  cfg['ylabel_f']),
    ('srcs_phase', 'total_phase', asd_alloc_phase, cfg['ylabel_p']),
]):
    ax.loglog(freqs, res_unc[key_tot], lw=2.5, color='k',
              label=f'{TDI_NAME} total')
    if res_cor is not None:
        ax.loglog(freqs, res_cor[key_tot], lw=2.5, color='steelblue', ls='-.',
                  label=f'{TDI_NAME}$^c$ total (corrected)')
    if res_cor_mod is not None:
        ax.loglog(freqs, res_cor_mod[key_tot], lw=2, color='darkorange', ls='-.',
                  label=f'{TDI_NAME}$^c$ mod. residual')
    ax.loglog(freqs, alloc, lw=1.5, color='red', ls=':', label='1 pm alloc.')
    ax.set_xlabel('Frequency [Hz]')
    ax.set_ylabel(ylabel)
    ax.set_xlim([freqs[0], freqs[-1]])
    ax.legend(fontsize=8)
    ax.grid(True, which='both', alpha=0.3)

axes[0].set_title(f'{cfg["title"]} — frequency\n{freq_info}', fontsize=9)
axes[1].set_title(f'{cfg["title"]} — phase\n{freq_info}', fontsize=9)

corr_str = ' + corrected' if SHOW_CORRECTED else ''
plt.suptitle(f'{TDI_NAME}{corr_str}  |  {plot_title}  |  $L={L:.2f}$ s', fontsize=10)
plt.tight_layout()
plt.savefig(f'{TDI_NAME}_{plot_title}.png', dpi=300, bbox_inches='tight')