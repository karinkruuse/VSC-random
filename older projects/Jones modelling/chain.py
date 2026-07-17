"""
jones/chain.py
==============
Chain and Result — fully implemented, no need to modify.

The chain is a simple ordered list of elements. evaluate() multiplies
their matrices left-to-right onto the input Jones vector. That's it.
"""

import sympy as sp
from elements import Element


class Result:
    """
    Output of Chain.evaluate(E0).
    Holds the output Jones vector and provides power, Stokes, LaTeX, lambdify.
    """

    def __init__(self, E: sp.Matrix):
        self._E = E

    # ── Access ────────────────────────────────────────────────────────

    def jones(self) -> sp.Matrix:
        """The output Jones vector [Ex, Ey]."""
        return self._E

    # ── Power ─────────────────────────────────────────────────────────

    def power(self) -> sp.Expr:
        """
        Total optical power:  P = |Ex|² + |Ey|²  =  E† · E
        Returns a sympy expression.
        """
        Ex, Ey = self._E
        return sp.simplify(sp.expand(
            sp.conjugate(Ex)*Ex + sp.conjugate(Ey)*Ey
        ))

    # ── Stokes ────────────────────────────────────────────────────────

    def stokes(self) -> sp.Matrix:
        """
        Stokes vector [S0, S1, S2, S3].

            S0 = |Ex|² + |Ey|²       total power
            S1 = |Ex|² - |Ey|²       H vs V  (linear)
            S2 = 2 Re(Ex Ey*)        +45 vs -45  (linear, diagonal)
            S3 = 2 Im(Ex Ey*)        RCP vs LCP  (circular)

        S2 and S3 carry the phase information. A plain power meter
        only sees S0. You need a polarization analyzer for S1, S2, S3.

        For fully polarized light:  S0² = S1² + S2² + S3²
        """
        Ex, Ey = self._E
        S0 = sp.conjugate(Ex)*Ex + sp.conjugate(Ey)*Ey
        S1 = sp.conjugate(Ex)*Ex - sp.conjugate(Ey)*Ey
        S2 = 2 * sp.re(Ex * sp.conjugate(Ey))
        S3 = 2 * sp.im(Ex * sp.conjugate(Ey))
        return sp.Matrix([sp.simplify(sp.expand(s)) for s in [S0, S1, S2, S3]])

    # ── LaTeX ─────────────────────────────────────────────────────────

    def latex(self) -> str:
        """LaTeX string for the Jones vector."""
        return sp.latex(self._E)

    def latex_power(self) -> str:
        """LaTeX string for the power expression."""
        return sp.latex(self.power())

    def latex_stokes(self) -> str:
        """LaTeX string for the Stokes vector."""
        return sp.latex(self.stokes())

    # ── Numerical ─────────────────────────────────────────────────────

    def lambdify(self, symbols):
        """
        Convert the Jones vector to a fast numpy function.

            f = result.lambdify([theta])
            Ex, Ey = f(np.linspace(0, np.pi, 200))
        """
        f0 = sp.lambdify(symbols, self._E[0], modules='numpy')
        f1 = sp.lambdify(symbols, self._E[1], modules='numpy')
        return lambda *args: (f0(*args), f1(*args))

    def lambdify_power(self, symbols):
        """
        Convert the power expression to a fast numpy function.

            f = result.lambdify_power([theta])
            P = f(np.linspace(0, np.pi, 200))
        """
        return sp.lambdify(symbols, self.power(), modules='numpy')

    def lambdify_stokes(self, symbols):
        """
        Convert all four Stokes parameters to fast numpy functions.

            f = result.lambdify_stokes([theta])
            S0, S1, S2, S3 = f(np.linspace(0, np.pi, 200))
        """
        S = self.stokes()
        fns = [sp.lambdify(symbols, S[i], modules='numpy') for i in range(4)]
        return lambda *args: tuple(f(*args) for f in fns)

    # ── Dunder ────────────────────────────────────────────────────────

    def __repr__(self):
        return f"Result(E={self._E.T})"


class Chain:
    """
    Ordered sequence of optical elements applied to an input Jones vector.

    Elements are applied left-to-right (first in list = first element hit).
    The chain multiplies all element matrices together, then applies to E0.

    Example
    -------
        theta, Gamma = sp.symbols('theta Gamma', real=True)
        Cs, Cf = sp.symbols('C_s C_f', positive=True)

        chain = Chain([
            Isolator(),
            HWP(theta),
            Rotation(sp.Symbol('alpha_0')),
            PMFiber(Gamma),
            PMCoupler(Cs, Cf, port='signal'),
        ])

        result = chain.evaluate(sp.Matrix([1, 0]))
        print(result.power())
        print(result.stokes())

        # Plot it:
        import numpy as np
        f = result.lambdify_power([theta])
        P = f(np.linspace(0, np.pi, 200))
    """

    def __init__(self, elements: list):
        for e in elements:
            if not isinstance(e, Element):
                raise TypeError(
                    f"{e} is not an Element. Make sure your class inherits from Element."
                )
        self.elements = elements

    def system_matrix(self) -> sp.Matrix:
        """
        Combined Jones matrix for the full chain:  M = M_N @ ... @ M_2 @ M_1

        Raises NotImplementedError if any element is not yet implemented.
        """
        M = sp.eye(2)
        for element in self.elements:
            M = element.matrix() * M
        return M

    def evaluate(self, E0) -> Result:
        """
        Propagate input Jones vector E0 through the chain.

        Parameters
        ----------
        E0 : 2-element sympy Matrix (or list/tuple)

        Returns
        -------
        Result object with output Jones vector, power, Stokes, etc.
        """
        if not isinstance(E0, sp.Matrix):
            E0 = sp.Matrix(E0)
        M = self.system_matrix()
        return Result(sp.simplify(M * E0))

    def __repr__(self):
        body = ",\n".join(f"  {e}" for e in self.elements)
        return f"Chain([\n{body}\n])"
