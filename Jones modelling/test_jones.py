"""
test_jones.py  —  run with:  python test_jones.py

SKIPs become PASSes as you implement each element.
Suggested order: Rotation -> LinearPolarizer ->
                 HWP -> Waveplate -> QWP -> 
                 PMFiber -> PMCoupler -> Beamsplitter -> Full chain
"""
import sympy as sp
from elements import (
    rotation_matrix, sandwiched,
    Rotation, LinearPolarizer,
    HWP, Waveplate, QWP,
    PMFiber, PMCoupler, Beamsplitter,
)
from chain import Chain

P = "  \u2713 PASS"
F = "  \u2717 FAIL"
S = "  - SKIP"

def check(name, fn, expected):
    try:
        got  = fn()
        diff = sp.simplify(sp.expand(got - expected))
        ok   = (diff == sp.zeros(*diff.shape)) if hasattr(diff,'shape') else (diff == 0)
        print(f"{P if ok else F}  {name}")
        if not ok:
            print(f"         got:      {got}")
            print(f"         expected: {expected}")
    except NotImplementedError:
        print(f"{S}  {name}")
    except Exception as e:
        print(f"  ? ERR  {name}: {e}")

def sec(t): print(f"\n{'='*52}\n  {t}\n{'='*52}")

# symbols
t  = sp.Symbol('theta',   real=True)
G  = sp.Symbol('Gamma',   real=True)
a  = sp.Symbol('alpha_0', real=True)
d  = sp.Symbol('delta',   real=True)
r  = sp.Symbol('rho',     real=True)
Cs = sp.Symbol('C_s', real=True, positive=True)
Cf = sp.Symbol('C_f', real=True, positive=True)
P0 = sp.Symbol('P_0', positive=True)

# ── Helpers ──────────────────────────────────────────────────────────
sec("HELPERS  (done for you)")
check("rotation_matrix(0) == I",
      lambda: rotation_matrix(0), sp.eye(2))
check("rotation_matrix(pi/2)",
      lambda: rotation_matrix(sp.pi/2), sp.Matrix([[0,1],[-1,0]]))

# ── Rotation ─────────────────────────────────────────────────────────
sec("Rotation  —  return rotation_matrix(self.alpha)")
check("Rotation(0) == I",
      lambda: Rotation(0).matrix(), sp.eye(2))
check("Rotation(pi/2)",
      lambda: Rotation(sp.pi/2).matrix(), sp.Matrix([[0,1],[-1,0]]))

# ── LinearPolarizer ───────────────────────────────────────────────────
sec("LinearPolarizer  —  projection matrix with offset alpha")

# basic known values (alpha=0)
check("LP(0) == [[1,0],[0,0]]",
      lambda: LinearPolarizer(0).matrix(), sp.Matrix([[1,0],[0,0]]))
check("LP(pi/2) == [[0,0],[0,1]]",
      lambda: LinearPolarizer(sp.pi/2).matrix(), sp.Matrix([[0,0],[0,1]]))
check("LP(pi/4) == 0.5*[[1,1],[1,1]]",
      lambda: LinearPolarizer(sp.pi/4).matrix(),
      sp.Matrix([[sp.Rational(1,2),sp.Rational(1,2)],
                 [sp.Rational(1,2),sp.Rational(1,2)]]))

# alpha offset shifts theta
alpha = sp.Symbol('alpha', real=True)
check("LP(0, alpha) == LP(alpha)",
      lambda: sp.simplify(LinearPolarizer(0, alpha).matrix()
                        - LinearPolarizer(alpha).matrix()),
      sp.zeros(2,2))
check("LP(t, alpha) == LP(t+alpha, 0)",
      lambda: sp.simplify(LinearPolarizer(t, alpha).matrix()
                        - LinearPolarizer(t+alpha).matrix()),
      sp.zeros(2,2))

# physical properties (should hold for any theta+alpha)
check("LP is a projector: M^2 == M  (idempotent)",
      lambda: sp.simplify(LinearPolarizer(t, alpha).matrix()**2
                        - LinearPolarizer(t, alpha).matrix()),
      sp.zeros(2,2))
check("LP det == 0  (lossy)",
      lambda: sp.simplify(LinearPolarizer(t, alpha).matrix().det()),
      sp.Integer(0))
check("LP passes its own axis: LP(t)*[cos t, sin t] == [cos t, sin t]",
      lambda: sp.simplify(
          LinearPolarizer(t).matrix()*sp.Matrix([sp.cos(t), sp.sin(t)])
          - sp.Matrix([sp.cos(t), sp.sin(t)])),
      sp.zeros(2,1))
check("LP blocks orthogonal: LP(t)*[-sin t, cos t] == [0,0]",
      lambda: sp.simplify(
          LinearPolarizer(t).matrix()*sp.Matrix([-sp.sin(t), sp.cos(t)])),
      sp.zeros(2,1))

# ── HWP ───────────────────────────────────────────────────────────────
sec("HWP  —  [[cos2t, sin2t],[sin2t, -cos2t]]")
check("HWP(0) == diag(1,-1)",
      lambda: HWP(0).matrix(), sp.Matrix([[1,0],[0,-1]]))
check("HWP(pi/4) == [[0,1],[1,0]]",
      lambda: HWP(sp.pi/4).matrix(), sp.Matrix([[0,1],[1,0]]))
check("HWP(t)^2 == I",
      lambda: sp.simplify(HWP(t).matrix()**2), sp.eye(2))
check("HWP(t)*[1,0] == [cos2t, sin2t]",
      lambda: HWP(t).matrix()*sp.Matrix([1,0]),
      sp.Matrix([sp.cos(2*t), sp.sin(2*t)]))

# ── Waveplate ─────────────────────────────────────────────────────────
sec("Waveplate  —  diag(exp(+id/2), exp(-id/2))  then sandwiched()")
check("Waveplate(d,0) is diagonal",
      lambda: Waveplate(d,0).matrix(),
      sp.Matrix([[sp.exp(sp.I*d/2),0],[0,sp.exp(-sp.I*d/2)]]))
check("Waveplate(0,t) == I  (no retardation)",
      lambda: sp.simplify(Waveplate(0,t).matrix()), sp.eye(2))
check("Waveplate(pi,t) == i*HWP(t)  (same up to global phase)",
      lambda: sp.simplify(Waveplate(sp.pi,t).matrix() - sp.I*HWP(t).matrix()),
      sp.zeros(2,2))

# ── QWP ───────────────────────────────────────────────────────────────
sec("QWP  —  delegate to Waveplate(pi/2, theta)")
check("QWP(0) diagonal = [exp(i*pi/4), exp(-i*pi/4)]",
      lambda: QWP(0).matrix(),
      sp.Matrix([[sp.exp(sp.I*sp.pi/4),0],[0,sp.exp(-sp.I*sp.pi/4)]]))
# QWP at 45deg on H input should give equal power in Ex and Ey (circular)
def _qwp_circular():
    E = sp.simplify(QWP(sp.pi/4).matrix()*sp.Matrix([1,0]))
    Px = sp.Abs(E[0])**2
    Py = sp.Abs(E[1])**2
    return sp.simplify(Px - Py)
check("QWP(pi/4)*[1,0] has |Ex|==|Ey|  (circular)", _qwp_circular, sp.Integer(0))


# ── PMFiber ───────────────────────────────────────────────────────────
sec("PMFiber  —  same structure as Waveplate")
check("PMFiber(G,0) diagonal",
      lambda: PMFiber(G,0).matrix(),
      sp.Matrix([[sp.exp(sp.I*G/2),0],[0,sp.exp(-sp.I*G/2)]]))

def _pmf_power():
    E = PMFiber(G).matrix() * sp.Matrix([sp.cos(t), sp.sin(t)])
    P = sp.conjugate(E[0])*E[0] + sp.conjugate(E[1])*E[1]
    return sp.simplify(P - 1)
check("PMFiber preserves power", _pmf_power, sp.Integer(0))

# ── PMCoupler ─────────────────────────────────────────────────────────
sec("PMCoupler  —  diagonal sqrt amplitude matrices")
check("PMCoupler signal: slow amp = sqrt(1-Cs)",
      lambda: PMCoupler(Cs,Cf,port='signal').matrix()[0,0], sp.sqrt(1-Cs))
check("PMCoupler signal: fast amp = sqrt(1-Cf)  (pdl=0)",
      lambda: PMCoupler(Cs,Cf,pdl=0,port='signal').matrix()[1,1], sp.sqrt(1-Cf))
check("PMCoupler tap: slow amp = sqrt(Cs)",
      lambda: PMCoupler(Cs,Cf,port='tap').matrix()[0,0], sp.sqrt(Cs))
check("PMCoupler tap: fast amp = sqrt(Cf)  (pdl=0)",
      lambda: PMCoupler(Cs,Cf,pdl=0,port='tap').matrix()[1,1], sp.sqrt(Cf))

def _coupler_conservation():
    E = sp.Matrix([sp.cos(t), sp.sin(t)])
    # use numerical Cs, Cf so sympy doesn't choke on sqrt(1-Cs)
    cs, cf = sp.Rational(1,2), sp.Rational(3,4)
    E1 = PMCoupler(cs, cf, pdl=0, port='signal').matrix()*E
    E2 = PMCoupler(cs, cf, pdl=0, port='tap').matrix()*E
    P1 = sp.conjugate(E1[0])*E1[0] + sp.conjugate(E1[1])*E1[1]
    P2 = sp.conjugate(E2[0])*E2[0] + sp.conjugate(E2[1])*E2[1]
    return sp.simplify(sp.trigsimp(P1 + P2 - 1))
check("PMCoupler(pdl=0): P_signal + P_tap == 1", _coupler_conservation, sp.Integer(0))

# ── Beamsplitter ──────────────────────────────────────────────────────
sec("Beamsplitter  —  scalar * identity")
check("BS transmitted = sqrt(T)*I  (R=0.5)",
      lambda: Beamsplitter(sp.Rational(1,2),port='transmitted').matrix(),
      sp.sqrt(sp.Rational(1,2))*sp.eye(2))
check("BS reflected = sqrt(R)*I  (R=0.5)",
      lambda: Beamsplitter(sp.Rational(1,2),port='reflected').matrix(),
      sp.sqrt(sp.Rational(1,2))*sp.eye(2))

# ── Full chain ────────────────────────────────────────────────────────
sec("Full chain  —  your experimental setup")
try:
    cs_val = sp.Rational(1, 2)
    cf_val = sp.Rational(3, 4)

    chain = Chain([
        HWP(t),
        Rotation(a),
        PMFiber(G),
        PMCoupler(cs_val, cf_val, pdl=0, port='signal'),
    ])
    chain_tap = Chain([
        HWP(t),
        Rotation(a),
        PMFiber(G),
        PMCoupler(cs_val, cf_val, pdl=0, port='tap'),
    ])

    result     = chain.evaluate(sp.Matrix([sp.sqrt(P0), 0]))
    result_tap = chain_tap.evaluate(sp.Matrix([sp.sqrt(P0), 0]))

    print(f"{P}  Chain evaluates OK")

    diff_G = sp.simplify(result.power().subs(G, 0) - result.power().subs(G, sp.pi/3))
    print(f"{P if diff_G==0 else F}  Power independent of Gamma (fiber phase)")

    total = sp.simplify(sp.trigsimp(result.power() + result_tap.power() - P0))
    print(f"{P if total==0 else F}  P_signal + P_tap == P0")

except NotImplementedError:
    print(f"{S}  Full chain (implement elements above first)")
except Exception as e:
    print(f"  ? ERR  {e}")

print(f"\n{'='*52}\n  Done.\n{'='*52}\n")
