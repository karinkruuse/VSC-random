import sympy as sp


# ---------------------------------------------------------------------------
# Helpers — done for you
# ---------------------------------------------------------------------------

def rotation_matrix(angle):
    """
    2x2 rotation matrix (counterclockwise by `angle`).

        R(a) = [ cos(a)   sin(a) ]
               [-sin(a)   cos(a) ]

    Rotates a vector INTO a frame tilted by `angle`, i.e. it expresses
    the same vector in a rotated coordinate system.
    """
    a = angle
    return sp.Matrix([
        [ sp.cos(a), sp.sin(a)],
        [-sp.sin(a), sp.cos(a)],
    ])


def sandwiched(M_eigen, psi):
    """
    Transform element matrix M_eigen (in its own eigenframe) to the
    lab frame, where its principal axis is at angle psi:

        M_lab = R(-psi) @ M_eigen @ R(psi)

    This is used for any element whose axes are tilted in the lab:
    first rotate INTO the element frame (R(psi)), apply the element,
    then rotate BACK (R(-psi) = R(psi).T).
    """
    R = rotation_matrix(psi)
    return R.T * M_eigen * R


# ---------------------------------------------------------------------------
# Base class — do not modify
# ---------------------------------------------------------------------------

class Element:
    """
    Base class for all optical elements.
    Every element must implement .matrix() -> 2x2 sympy Matrix.
    """
    def matrix(self) -> sp.Matrix:
        raise NotImplementedError(
            f"{self.__class__.__name__}.matrix() is not implemented yet."
        )

    def __repr__(self):
        return f"{self.__class__.__name__}()"


# ---------------------------------------------------------------------------
# Elements — YOUR JOB: implement .matrix() for each one
# ---------------------------------------------------------------------------

class Rotation(Element):
    """
    Pure coordinate rotation by angle alpha.

    This is NOT a physical optical element — just a frame transform.

        M = rotation_matrix(alpha)

    Parameters
    ----------
    alpha : rotation angle in radians
    """
    def __init__(self, alpha):
        self.alpha = alpha

    def matrix(self):
        return rotation_matrix(self.alpha)

    def __repr__(self):
        return f"Rotation(alpha={self.alpha})"


class LinearPolarizer(Element):
    """
    The Jones matrix is a projection operator:

        M = [ cos²θ        sin θ cos θ ]
            [ sin θ cos θ  sin²θ       ]

    Note: this matrix is NOT unitary (det = 0), it loses power.

    Parameters
    ----------
    theta : transmission axis angle w.r.t. lab x-axis (radians)
    alpha is like an unknown tuning angle for offsets in theta. 0 by default.
    """
    def __init__(self, theta, alpha=0):
        self.t = theta
        self.a = alpha

    def matrix(self):
        return sp.Matrix([
        [ sp.cos(self.t+self.a)**2, sp.sin(self.t+self.a)*sp.cos(self.t+self.a) ],
        [ sp.sin(self.t+self.a)*sp.cos(self.t+self.a), sp.sin(self.t+self.a)**2 ],
    ])

    def __repr__(self):
        return f"LinearPolarizer(theta={self.t}, alpha={self.a})"


class HWP(Element):
    """
    Half-wave plate with fast axis at mechanical angle theta.

    Rotates linear polarization by 2*theta. The real-valued Jones matrix:

        M = [ cos 2θ   sin 2θ ]
            [ sin 2θ  -cos 2θ ]

    Parameters
    ----------
    theta : fast axis angle w.r.t. lab x-axis (radians)
    """
    def __init__(self, theta):
        self.theta = theta

    def matrix(self):
        c2 = sp.cos(2 * self.theta)
        s2 = sp.sin(2 * self.theta)
        return sp.Matrix([
            [c2,  s2],
            [s2, -c2],
        ])

    def __repr__(self):
        return f"HWP(theta={self.theta})"


class Waveplate(Element):
    """
    General waveplate with retardation delta and fast axis at angle psi.

    In the waveplate's own frame (fast axis = x), the matrix is diagonal:

        M_eigen = [ exp(+i δ/2)    0           ]
                  [ 0              exp(-i δ/2) ]

    The fast axis component advances by δ/2, the slow axis retards by δ/2.
    In the lab frame (fast axis at angle psi), use sandwiched().

    Special cases:
        HWP : delta = pi      ->  exp(±i π/2) = ±i
        QWP : delta = pi/2    ->  exp(±i π/4) = (1±i)/√2

    Parameters
    ----------
    delta : phase retardation in radians (fast leads slow by delta)
    psi   : fast axis angle w.r.t. lab x-axis (radians)
    """
    def __init__(self, delta, psi):
        self.delta = delta
        self.psi   = psi

    def matrix(self):
        retarder = sp.Matrix([
        [ sp.exp(sp.I*self.delta/2), 0],
        [ 0, sp.exp(-sp.I*self.delta/2) ],
        ])
        return sandwiched(retarder, self.psi)

    def __repr__(self):
        return f"Waveplate(delta={self.delta}, psi={self.psi})"


class QWP(Element):
    """
    Quarter-wave plate with fast axis at angle theta.

    delta = pi/2. Converts between linear and elliptical/circular polarization.

    Examples:
        QWP at 45°, input horizontal  -> right circular (or left, by convention)
        QWP at 0°,  input circular    -> linear

    Parameters
    ----------
    theta : fast axis angle w.r.t. lab x-axis (radians)
    alpha : tiny unknown offset in theta, default 0
    """
    def __init__(self, theta, alpha=0):
        self.theta = theta
        self.alpha = alpha

    def matrix(self):
        return Waveplate(sp.pi/2, self.theta + self.alpha).matrix()

    def __repr__(self):
        return f"QWP(theta={self.theta}, alpha={self.alpha})"


class PMFiber(Element):
    """
    Polarization-maintaining fiber segment.

    Acts as a waveplate: introduces differential phase Gamma between
    the slow (x) and fast (y) fiber axes. The fiber axes may be
    rotated by psi relative to the lab frame.

    Physical meaning of Gamma:
        Gamma = 2*pi * B * L / lambda
        B = n_slow - n_fast  ~ 4e-4  (Panda fiber birefringence)
        L = fiber length
        lambda = wavelength

    IMPORTANT: Gamma does NOT change the power in each axis —
    it only changes the relative phase, i.e. the ellipticity.
    A power meter cannot see Gamma.

    Parameters
    ----------
    Gamma : differential phase retardation (slow leads fast), radians, use random?
    psi   : rotation of fiber slow axis w.r.t. lab x-axis (default 0)
    """
    def __init__(self, Gamma, psi=0):
        self.Gamma = Gamma
        self.psi   = psi

    def matrix(self):
        M_eigen = sp.Matrix([
            [sp.exp(sp.I*self.Gamma/2), 0],
            [0, sp.exp(-sp.I*self.Gamma/2)]
        ])
        return sandwiched(M_eigen, self.psi)
        

    def __repr__(self):
        return f"PMFiber(Gamma={self.Gamma}, psi={self.psi})"



class PMCoupler(Element):
    """
    Polarization-maintaining fiber coupler.

    Splits each fiber axis independently with power coupling ratios
    Cs (slow) and Cf (fast). The fast axis may have extra loss: Tf = 1-pdl.

    Since this is a 2-output device, you select which port to follow
    at construction time. The matrix for the chosen port is diagonal
    with amplitude coefficients (square roots of power fractions):

        port='signal':  M = diag( sqrt(1-Cs),  sqrt((1-Cf)*Tf) )
        port='tap':     M = diag( sqrt(Cs),    sqrt(Cf*Tf)     )

    where Tf = 1 - pdl.

    Why sqrt? Jones matrices act on AMPLITUDES. If power fraction Cs
    goes to tap, then amplitude fraction sqrt(Cs) goes to tap, because
    power = |amplitude|².

    Parameters
    ----------
    Cs   : power coupling ratio, slow axis -> tap port. 0.5 = 50:50.
    Cf   : power coupling ratio, fast axis -> tap port.
    pdl  : polarization-dependent loss. Tf = 1 - pdl (fast axis only).
    port : which output to follow. 'signal' or 'tap'.
    """
    PORTS = ('signal', 'tap')

    def __init__(self, Cs, Cf, pdl=0, port='signal'):
        if port not in self.PORTS:
            raise ValueError(f"port must be one of {self.PORTS}, got '{port}'")
        self.Cs   = Cs
        self.Cf   = Cf
        self.pdl  = pdl
        self.port = port

    def matrix(self):
        Cs, Cf, Tf = self.Cs, self.Cf, 1 - self.pdl
        if self.port == 'signal':
            return sp.Matrix([[sp.sqrt(1-Cs), 0],
                              [0, sp.sqrt((1-Cf)*Tf)]])
            
        else:  
            return sp.Matrix([[sp.sqrt(Cs), 0],
                              [0, sp.sqrt((Cf)*Tf)]])

    def __repr__(self):
        return f"PMCoupler(Cs={self.Cs}, Cf={self.Cf}, pdl={self.pdl}, port='{self.port}')"


class Beamsplitter(Element):
    """
    Ideal polarization-independent beamsplitter.

    Splits both polarization components equally. Power reflectance R,
    transmittance T = 1 - R. The matrix is a scalar times identity:

        port='transmitted':  M = sqrt(1-R) * I
        port='reflected':    M = sqrt(R)   * I

    Parameters
    ----------
    R    : power reflectance (e.g. 0.5 for 50:50) 
    port : 'transmitted' or 'reflected'
    """
    PORTS = ('transmitted', 'reflected')

    def __init__(self, R=0.5, port='transmitted'):
        if port not in self.PORTS:
            raise ValueError(f"port must be one of {self.PORTS}, got '{port}'")
        self.R    = R
        self.port = port

    def matrix(self):
        if self.port == 'reflected':
            return sp.sqrt(self.R) * sp.eye(2)
        else:
            return sp.sqrt(1 - self.R) * sp.eye(2)

    def __repr__(self):
        return f"Beamsplitter(R={self.R}, port='{self.port}')"


class PBS(Element):
    """

    

    Parameters
    ----------
    R    : Power ratio.  
    port : 'transmitted' or 'reflected'
    """
    PORTS = ('transmitted', 'reflected')

    def __init__(self, R=0.5, port='transmitted'):
        if port not in self.PORTS:
            raise ValueError(f"port must be one of {self.PORTS}, got '{port}'")
        self.R    = R
        self.port = port

    def matrix(self):
        if self.port == 'reflected':
            return sp.sqrt(self.R) * sp.eye(2)
        else:
            return sp.sqrt(1 - self.R) * sp.eye(2)

    def __repr__(self):
        return f"Beamsplitter(R={self.R}, port='{self.port}')"