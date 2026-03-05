# HWP + PBS Jones calculus — symbolic derivation with LaTeX output
#
# Run in Jupyter for inline rendered math.
# Run as plain script for pretty-printed terminal output.
#
# Automatically detects environment and uses:
#   Jupyter  -> display(Math(latex(...)))   [rendered LaTeX]
#   Terminal -> pprint(...)                 [unicode pretty print]

import sympy as sp

# ── Detect environment ────────────────────────────────────────────────────────
try:
    from IPython.display import display, Math
    from IPython import get_ipython
    IN_JUPYTER = get_ipython() is not None
except ImportError:
    IN_JUPYTER = False

def show(expr, label=None):
    """Print label then render expression — LaTeX in Jupyter, pprint elsewhere."""
    if label:
        print(f"\n{'='*55}")
        print(f"  {label}")
        print(f"{'='*55}")
    if IN_JUPYTER:
        display(Math(sp.latex(expr)))
    else:
        sp.pprint(expr, use_unicode=True)
        print()

# ── Symbols ───────────────────────────────────────────────────────────────────
phi, delta, alpha, eps = sp.symbols(r'\phi \delta \alpha \varepsilon', real=True)

# ── Helper functions ──────────────────────────────────────────────────────────

def RotMat(a):
    """2D rotation matrix."""
    return sp.Matrix([[sp.cos(a),  sp.sin(a)],
                      [-sp.sin(a), sp.cos(a)]])

def WavePlate(phi_, delta_):
    """Jones matrix: waveplate with retardance delta, fast axis at phi."""
    phase = sp.diag(sp.exp(sp.I*delta_/2), sp.exp(-sp.I*delta_/2))
    return RotMat(-phi_) * phase * RotMat(phi_)

def TIntensity(phi_, delta_, alpha_):
    """Transmitted intensity through PBS with transmission axis at alpha."""
    E_in  = sp.Matrix([1, 0])
    p_PBS = sp.Matrix([sp.cos(alpha_), sp.sin(alpha_)])
    E_out = WavePlate(phi_, delta_) * E_in
    amplitude = p_PBS.dot(E_out)
    return sp.trigsimp(sp.Abs(amplitude)**2)

# ── Symbolic derivations ──────────────────────────────────────────────────────

# Full general expression
T_sym = sp.trigsimp(sp.simplify(TIntensity(phi, delta, alpha)))
show(T_sym, r"Full T(\phi, \delta, \alpha)")

# Perfect HWP, aligned PBS
T_perfect = sp.trigsimp(T_sym.subs([(delta, sp.pi), (alpha, 0)]))
show(T_perfect, r"Perfect HWP (\delta=\pi), aligned PBS (\alpha=0)")
# Expect: cos^2(2*phi) = (1 + cos(4*phi)) / 2

# Perfect HWP, PBS misaligned by alpha
T_misaligned = sp.trigsimp(T_sym.subs(delta, sp.pi))
show(T_misaligned, r"Perfect HWP, PBS misaligned by \alpha")
# Expect: cos^2(2*phi - alpha) — phase shift only, T_min still 0

# Retardance error: delta = pi - eps, expand to order eps^2
T_perturbed = T_sym.subs([(alpha, 0), (delta, sp.pi - eps)])
T_series = sp.series(T_perturbed, eps, 0, 3).removeO()
T_series = sp.trigsimp(sp.expand_trig(T_series))
show(T_series, r"Retardance error \delta=\pi-\varepsilon, expanded to O(\varepsilon^2)")
# Expect: (1/2 + eps^2/8) + (1/2 - eps^2/8) * cos(4*phi)

# T_min and extinction ratio from the series
T_min_expr = T_series.subs(sp.cos(4*phi), -1)
T_max_expr = T_series.subs(sp.cos(4*phi),  1)
ER_expr     = sp.simplify(T_max_expr / T_min_expr)
eps_from_ER = sp.solve(sp.Eq(4/eps**2, sp.Symbol('ER')), eps)[0]

show(sp.Eq(sp.Symbol('T_min'), sp.simplify(T_min_expr)),
     r"T_{min} (raised floor due to \varepsilon)")
show(sp.Eq(sp.Symbol('ER'), ER_expr),
     r"Extinction ratio ER = T_{max}/T_{min}")
show(sp.Eq(eps, sp.sqrt(4/sp.Symbol('ER'))),
     r"\varepsilon = 2/\sqrt{ER}  (retardance error from measurement)")