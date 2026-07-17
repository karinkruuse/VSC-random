"""
Board noise in X2 — publication-quality ASD plot.
Two panels: frequency ASD and phase ASD.
Lines: 1 pm allocation (red), X2 uncorrected (purple, alpha=0.5),
       X2 clock-corrected (purple, alpha=1.0).
"""

# ══════════════════════════════════════════════════════════════════════════════
# IMPORTS
# ══════════════════════════════════════════════════════════════════════════════
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from sympy import (Function, Symbol, symbols, simplify, expand,
                   exp, I, lambdify)
from sympy.core.function import AppliedUndef

# ══════════════════════════════════════════════════════════════════════════════
# MATPLOTLIB STYLE
# ══════════════════════════════════════════════════════════════════════════════
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
    "xtick.major.size"   : 4,  "ytick.major.size"   : 4,
    "xtick.minor.size"   : 2.5,"ytick.minor.size"   : 2.5,
    "xtick.major.width"  : 0.8,"ytick.major.width"  : 0.8,
    "xtick.labelsize"    : 10, "ytick.labelsize"    : 10,
    "axes.labelsize"     : 11,
    "legend.fontsize"    : 9,
    "legend.framealpha"  : 0.92,
    "legend.edgecolor"   : "#cccccc",
    "legend.handlelength": 2.0,
    "figure.dpi"         : 150,
})

# ══════════════════════════════════════════════════════════════════════════════
# PHYSICAL PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════
c            = 299792458.0
lambda_laser = 1064e-9
L            = 2.5e9 / c
dL           = 5e-8   # arm rate of change [s/s]

nu1  = 15.0e6;  nu2  =  6.9e6;  nu3  = 13.6e6
mod_order = 7
num1 = 2.4*10**mod_order;  num2 = 2.4*10**mod_order;  num3 = 2.4*10**mod_order

# ══════════════════════════════════════════════════════════════════════════════
# FREQUENCY GRID & 1 PM ALLOCATION
# ══════════════════════════════════════════════════════════════════════════════
freqs  = np.logspace(-4, 0, 2000)
omegas = 2 * np.pi * freqs

Sx_alloc       = (64 * omegas**2 * np.sin(omegas*L)**2 * np.sin(2*omegas*L)**2
                  * (1e-12/lambda_laser)**2 * (1 + (2e-3/freqs)**4))
asd_alloc_freq  = np.sqrt(Sx_alloc)
asd_alloc_phase = asd_alloc_freq / freqs

# ══════════════════════════════════════════════════════════════════════════════
# BOARD NOISE PSD
# ══════════════════════════════════════════════════════════════════════════════
def S_board(f):
    return 4e-27 / f

# ══════════════════════════════════════════════════════════════════════════════
# SYMPY SETUP  (copied verbatim from plotting2.py)
# ══════════════════════════════════════════════════════════════════════════════
t = Symbol('t')

tau12,tau21,tau13,tau31,tau23,tau32 = symbols(
    r'\tau_{12} \tau_{21} \tau_{13} \tau_{31} \tau_{23} \tau_{32}',
    real=True, positive=True)
dtau12,dtau21,dtau13,dtau31,dtau23,dtau32 = symbols(
    r'\dot\tau_{12} \dot\tau_{21} \dot\tau_{13} \dot\tau_{31} \dot\tau_{23} \dot\tau_{32}',
    real=True)

omega1,omega2,omega3     = symbols(r'\omega_1 \omega_2 \omega_3', real=True)
omega1m,omega2m,omega3m  = symbols(r'\omega_1^m \omega_2^m \omega_3^m', real=True)
omegaREFA,omegaREFB,omegaREFC = symbols(
    r'\omega^{REF}_A \omega^{REF}_B \omega^{REF}_C', real=True)

phi1=Function(r'\phi_1'); phi2=Function(r'\phi_2'); phi3=Function(r'\phi_3')
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

tau_d  = {(1,2):tau12,(2,1):tau21,(1,3):tau13,(3,1):tau31,(2,3):tau23,(3,2):tau32}
dtau_d = {(1,2):dtau12,(2,1):dtau21,(1,3):dtau13,(3,1):dtau31,(2,3):dtau23,(3,2):dtau32}

sc = {
    1: (phi1, q1, omega1, omega1m, epsilonA, omegaREFA, N1_m),
    2: (phi2, q2, omega2, omega2m, epsilonB, omegaREFB, N2_m),
    3: (phi3, q3, omega3, omega3m, epsilonC, omegaREFC, N3_m),
}
N_d = {
    (1,2):(N1_2,n1_2),(1,3):(N1_3,n1_3),
    (2,1):(N2_1,n2_1),(2,3):(N2_3,n2_3),
    (3,1):(N3_1,n3_1),(3,2):(N3_3,n3_3),
}
B_d = {
    (1,2):(B_12,B_12S),(1,3):(B_13,B_13S),
    (2,1):(B_21,B_21S),(2,3):(B_23,B_23S),
    (3,1):(B_31,B_31S),(3,2):(B_32,B_32S),
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

# ── Delay helpers ─────────────────────────────────────────────────────────────
def D(expr, tau_key):
    if expr == 0: return 0
    if isinstance(tau_key, tuple):
        tau_val = tau_d[tau_key] + dtau_d[tau_key] * t
    else:
        tau_val = tau_key
    return expr.subs(t, t - tau_val)

def Dn(expr, *tau_keys):
    for tk in tau_keys:
        expr = D(expr, tk)
    return expr

def drop_dtau_squared(expr):
    dtau_set = {dtau12,dtau21,dtau13,dtau31,dtau23,dtau32}
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

# ── Transfer function extractor ───────────────────────────────────────────────
def get_transfer_function(tdi_expr, noise_func):
    zero_subs = {}
    for fn in master_noise_funcs:
        if fn == noise_func: continue
        for inst in tdi_expr.atoms(type(noise_func(t)).__mro__[1]):
            if inst.func == fn: zero_subs[inst] = 0
    for fn in master_noise_funcs:
        if fn == noise_func: continue
        for inst in list(tdi_expr.atoms(AppliedUndef)):
            if inst.func == fn: zero_subs[inst] = 0
    expr2 = tdi_expr.subs(zero_subs)
    phase_subs = {inst: exp(-I*omega_sym*(t - inst.args[0]))
                  for inst in expr2.atoms(AppliedUndef) if inst.func == noise_func}
    return expand(expr2.subs(phase_subs))

# ══════════════════════════════════════════════════════════════════════════════
# BUILD X2 — BOARD NOISE (UNCORRECTED)
# ══════════════════════════════════════════════════════════════════════════════
board_funcs = [epsilonA, epsilonB, epsilonC]

def build_board_eta():
    eta = {}
    for (i,j) in tau_d:
        _,_,_,_,eps_i,_,_ = sc[i]
        _,_,om_j,_,_,_,_  = sc[j]
        eta[(i,j)] = expand(om_j * (eps_i(t) - D(eps_i(t), (i,j))))
    return eta

def build_board_eta_sb():
    eta = {}; etaSB = {}
    for (i,j) in tau_d:
        _,_,_,_,eps_i,_,_ = sc[i]
        _,_,om_j,omm_j,_,_,_ = sc[j]
        eta[(i,j)]   = expand(om_j         * (eps_i(t) - D(eps_i(t), (i,j))))
        etaSB[(i,j)] = expand((om_j+omm_j) * (eps_i(t) - D(eps_i(t), (i,j))))
    return eta, etaSB

def build_X2(eta):
    def P12(e): return -(  e
                         - Dn(e,(3,1),(1,3))
                         - Dn(e,(2,1),(1,2),(3,1),(1,3))
                         + Dn(e,(3,1),(1,3),(3,1),(1,3),(2,1),(1,2)))
    def P13(e): return  (  e
                         - Dn(e,(2,1),(1,2))
                         - Dn(e,(3,1),(1,3),(2,1),(1,2))
                         + Dn(e,(2,1),(1,2),(2,1),(1,2),(3,1),(1,3)))
    def P21(e): return P12(Dn(e,(1,2)))
    def P31(e): return P13(Dn(e,(1,3)))
    X2 = expand(P12(eta[(1,2)])+P21(eta[(2,1)])+P13(eta[(1,3)])+P31(eta[(3,1)]))
    return drop_dtau_squared(X2)

def build_X2_corrected(eta, etaSB):
    X2_base = build_X2(eta)
    r = {}
    for (i,j) in tau_d:
        _,_,_,omm_j,_,_,_ = sc[j]
        r[(i,j)] = simplify((eta[(i,j)] - etaSB[(i,j)]) / omm_j)

    RT12 = r[(1,2)] + Dn(r[(2,1)],(1,2))
    RT13 = r[(1,3)] + Dn(r[(3,1)],(1,3))

    R = {}
    R[(1,2)] = (-(RT12 - Dn(RT12,(3,1),(1,3)))
                +(2*RT13 - Dn(RT13,(2,1),(1,2)) - Dn(RT13,(3,1),(1,3),(2,1),(1,2))))
    R[(2,3)] = 0
    R[(3,1)] = (-(2*RT12 - Dn(RT12,(3,1),(1,3)) - Dn(RT12,(2,1),(1,2),(3,1),(1,3)))
                +(RT13 - Dn(RT13,(2,1),(1,2)))
                +(r[(1,3)] - Dn(r[(1,3)],(2,1),(1,2))
                  - Dn(r[(1,3)],(3,1),(1,3),(2,1),(1,2))
                  + Dn(r[(1,3)],(2,1),(1,2),(2,1),(1,2),(3,1),(1,3))))
    R[(2,1)] = (-(RT12 - Dn(RT12,(3,1),(1,3)))
                -(r[(1,2)] - Dn(r[(1,2)],(3,1),(1,3))
                  - Dn(r[(1,2)],(2,1),(1,2),(3,1),(1,3))
                  + Dn(r[(1,2)],(3,1),(1,3),(3,1),(1,3),(2,1),(1,2)))
                +(2*RT13 - Dn(RT13,(2,1),(1,2)) - Dn(RT13,(3,1),(1,3),(2,1),(1,2))))
    R[(3,2)] = 0
    R[(1,3)] = (-(2*RT12 - Dn(RT12,(3,1),(1,3)) - Dn(RT12,(2,1),(1,2),(3,1),(1,3)))
                +(RT13 - Dn(RT13,(2,1),(1,2))))

    a = {(i,j): sc[i][2]-sc[j][2] for (i,j) in tau_d}
    correction = 0
    for (i,j,k) in [(1,2,3),(2,3,1),(3,1,2)]:
        correction -= (-a[(i,j)]*R[(i,j)] - a[(i,k)]*R[(i,k)])

    return drop_dtau_squared(expand(X2_base + correction))

# ══════════════════════════════════════════════════════════════════════════════
# NUMERICAL EVALUATION
# ══════════════════════════════════════════════════════════════════════════════
num_subs = {
    omega1:2*np.pi*nu1,  omega2:2*np.pi*nu2,  omega3:2*np.pi*nu3,
    omega1m:2*np.pi*num1, omega2m:2*np.pi*num2, omega3m:2*np.pi*num3,
    tau12:L, tau21:L, tau13:L, tau31:L, tau23:L, tau32:L,
    dtau12:dL, dtau21:dL, dtau13:dL, dtau31:dL, dtau23:dL, dtau32:dL,
}

def eval_total_asd(tdi_sym):
    S_input = S_board(freqs)
    psd_total = np.zeros(len(freqs))
    for fn in board_funcs:
        H_sym  = get_transfer_function(tdi_sym, fn)
        if H_sym == 0: continue
        H_eq   = H_sym.subs(num_subs).subs(t, 0)
        H_num  = lambdify(omega_sym, H_eq, modules='numpy')
        H_vals = np.ones(len(freqs), dtype=complex) * H_num(omegas)
        H_vals /= (2 * np.pi)   # board: divide_2pi = True
        psd_total += np.abs(H_vals)**2 * S_input
    asd_freq  = np.sqrt(psd_total)
    asd_phase = asd_freq / freqs
    return asd_freq, asd_phase

print("Building X2 (uncorrected)…")
eta_unc = build_board_eta()
X2_unc  = build_X2(eta_unc)
asd_unc_freq, asd_unc_phase = eval_total_asd(X2_unc)

print("Building X2 (clock-corrected) — may take ~60 s…")
eta_cor, etaSB_cor = build_board_eta_sb()
X2_cor  = build_X2_corrected(eta_cor, etaSB_cor)
asd_cor_freq, asd_cor_phase = eval_total_asd(X2_cor)

# ══════════════════════════════════════════════════════════════════════════════
# PLOT
# ══════════════════════════════════════════════════════════════════════════════
purple = (130/255, 23/255, 112/255)
red    = (215/255, 27/255,  47/255)

fig, (ax_f, ax_p) = plt.subplots(1, 2, figsize=(12, 5))

for ax, (asd_unc, asd_cor, asd_alloc, ylabel) in zip(
    [ax_f, ax_p],
    [
        (asd_unc_freq,  asd_cor_freq,  asd_alloc_freq,
         r"ASD [Hz / $\sqrt{\mathrm{Hz}}$]"),
        (asd_unc_phase, asd_cor_phase, asd_alloc_phase,
         r"ASD [cycles / $\sqrt{\mathrm{Hz}}$]"),
    ]
):
    ax.loglog(freqs, asd_alloc,
              color="#333333", lw=1.4, ls="--", label="1 pm allocation")
    ax.loglog(freqs, asd_unc,
              color=purple, alpha=0.9, lw=1.4, label="Board clock noise")
    #ax.loglog(freqs, asd_cor,
    #          color=purple, alpha=1.0, lw=1.4, label="X2 board noise (corrected)")

    ax.set_xlim(freqs[0], freqs[-1])
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel(ylabel)
    ax.xaxis.set_minor_locator(ticker.LogLocator(subs="all", numticks=10))
    ax.yaxis.set_minor_locator(ticker.LogLocator(subs="all", numticks=10))
    ax.tick_params(which="minor", length=2.5, width=0.6)
    ax.grid(True,  which="major", color="#e0e0e0", linewidth=0.6, linestyle="--")
    ax.grid(False, which="minor")
    ax.legend(loc="lower left", frameon=True, fancybox=False)

ax_f.set_title("Frequency ASD", fontsize=11)
ax_p.set_title("Phase ASD", fontsize=11)

fig.suptitle(
    f"X2 board noise  |  $\\dot{{L}} = {dL:.1e}$ s/s  |  $L = {L:.3f}$ s",
    fontsize=10
)
fig.subplots_adjust(wspace=0.32)
fig.tight_layout()

out = "X2_board_noise_asd.png"
fig.savefig(out, dpi=300, bbox_inches="tight")
print(f"Saved: {out}")
plt.show()