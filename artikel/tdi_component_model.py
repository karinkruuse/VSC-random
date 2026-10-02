"""Ordered, varying-delay phase-domain Michelson X2 component model.

The path order follows miniLISA timining jitters/miniLISA_TDI2.ipynb.
Paths below are stored OUTERMOST FIRST, unlike that notebook's Dn arguments.
Spectra are local (adiabatic) estimates, averaged over specified epochs.
They are not an exact stationary PSD of a time-varying system.
"""
from collections import defaultdict
import numpy as np

LINKS = ((1, 2), (2, 1), (1, 3), (3, 1))
A = ((1, 2), (2, 1))
B = ((1, 3), (3, 1))
P12 = {(): -1, B: 1, B + A: 1, A + B + B: -1}
P13 = {(): 1, A: -1, A + B: -1, B + A + A: 1}


def combine(*weighted_signals):
    out = defaultdict(float)
    for scale, signal in weighted_signals:
        for term, coefficient in signal.items():
            out[term] += scale * coefficient
    return {term: c for term, c in out.items() if c != 0}


def source(name):
    return {(name, ()): 1.0}


def delay(signal, path):
    return {(name, tuple(path) + old): c for (name, old), c in signal.items()}


def polynomial(signal, terms):
    return combine(*[(c, delay(signal, path)) for path, c in terms.items()])


def readouts(nu, modulation):
    """Return eta, r with phase in cycles and r in seconds.

    q and eps are timing sources (seconds); all others are phase sources.
    A detector channel is one source shared before the three-way split.
    Electronic readouts are independent equivalent link/channel sources.
    """
    eta, r = {}, {}
    for i, j in LINKS:
        path = ((i, j),)
        alpha = nu[j] - nu[i]
        e_c, e_sb = source(f'ec{i}{j}'), source(f'es{i}{j}')
        board = combine((1, source(f'eps{i}')), (-1, delay(source(f'eps{i}'), path)))
        detector_c = combine((1, delay(source(f'pc{j}'), path)), (-1, source(f'pc{i}')))
        detector_sb = combine((1, delay(source(f'ps{j}'), path)), (-1, source(f'ps{i}')))
        eta[i, j] = combine(
            (1, delay(source(f'laser{j}'), path)), (-1, source(f'laser{i}')),
            (-alpha, source(f'q{i}')), (nu[j], board), (1, detector_c), (1, e_c))
        r[i, j] = combine(
            (1, delay(source(f'q{j}'), path)), (-1, source(f'q{i}')), (1, board),
            (1/modulation[j], delay(source(f'm{j}'), path)),
            (-1/modulation[j], source(f'm{i}')),
            (1/modulation[j], detector_sb), (-1/modulation[j], detector_c),
            (1/modulation[j], e_sb), (-1/modulation[j], e_c))
    return eta, r


def michelson(eta, r, nu, corrected=True, generation=2):
    # With constant antisymmetric beat frequencies alpha_ji=-alpha_ij,
    # R^c_1j=eta_1j+D_1j eta_j1-alpha_1j r_1j cancels q_j exactly.
    # This is the reduced three-laser case, not the full LISA clock model.
    roundtrips = {}
    for j in (2, 3):
        roundtrips[j] = combine((1, eta[1, j]), (1, delay(eta[j, 1], ((1, j),))))
        if corrected:
            roundtrips[j] = combine((1, roundtrips[j]), (-(nu[j]-nu[1]), r[1, j]))
    if generation == 1:
        return combine((1, polynomial(roundtrips[2], {(): -1, B: 1})),
                       (1, polynomial(roundtrips[3], {(): 1, A: -1})))
    return combine((1, polynomial(roundtrips[2], P12)),
                   (1, polynomial(roundtrips[3], P13)))


def split_board_timing(signal):
    """Use eps_i = eps_common + deps_i, before squaring source responses.

    deps_i are differential timing errors in seconds. Their spectra must come
    from differential timing information, not from the shared oscillator PSD.
    """
    terms = []
    for (name, path), coefficient in signal.items():
        if name.startswith('eps'):
            terms.append((coefficient, {('eps_common', path): 1.0}))
            terms.append((coefficient, {('deps'+name[3:], path): 1.0}))
        else:
            terms.append((coefficient, {(name, path): 1.0}))
    return combine(*terms)


def path_lag(path, epoch, lengths, rates):
    """Exact nested affine delays d_ij(t)=lengths[ij]+rates[ij]*t."""
    lag = np.longdouble(0)
    for link in path:
        lag += np.longdouble(lengths[link]) + np.longdouble(rates[link])*(epoch-lag)
    return lag


def transfer(signal, frequencies, epoch, lengths, rates):
    # This is the instantaneous response to a monochromatic source.
    # Keeping retarded arguments before forming a local spectrum preserves
    # noncommutation; it does not include long-term frequency redistribution.
    out = {}
    for (name, path), c in signal.items():
        lag = path_lag(path, epoch, lengths, rates)
        term = c * np.exp(-2j*np.pi*frequencies*float(lag))
        out[name] = out.get(name, 0) + term
    return out


def mean_gains(signal, frequencies, epochs, lengths, rates):
    gains = defaultdict(lambda: np.zeros_like(frequencies))
    for epoch in epochs:
        for name, response in transfer(signal, frequencies, epoch, lengths, rates).items():
            gains[name] += abs(response)**2 / len(epochs)
    return dict(gains)


def validate(nu, modulation):
    """Check source cancellation, the static limit, and noncommuting paths."""
    import sympy as sp
    eta, r = readouts(nu, modulation)
    corrected = michelson(eta, r, nu)
    assert not any(name.startswith('q') for name, path in corrected)
    assert not any(name in ('laser2', 'laser3') for name, path in corrected)
    # For general unequal delays/rates, the surviving laser1 path difference
    # is BAAB-ABBA. Its constant and first-order rate terms vanish.
    laser = {(name, path): c for (name, path), c in corrected.items() if name == 'laser1'}
    assert laser == {('laser1', B+A+A+B): 1.0, ('laser1', A+B+B+A): -1.0}
    e, time = sp.symbols('e time')
    lengths_s = dict(zip(LINKS, sp.symbols('l12 l21 l13 l31')))
    rates_s = dict(zip(LINKS, sp.symbols('v12 v21 v13 v31')))
    def lag_series(path):
        l0, l1 = 0, 0
        for link in path:
            l1 += rates_s[link]*(time-l0)
            l0 += lengths_s[link]
        return sp.expand(l0+e*l1)
    assert sp.expand(lag_series(B+A+A+B)-lag_series(A+B+B+A)) == 0
    assert sp.expand(lag_series(A+B)-lag_series(B+A)) != 0
    # Numerical static limit, including the familiar four-link ASD gain.
    lengths = {link: 8.3391023799538 for link in LINKS}
    rates = {link: 0.0 for link in LINKS}
    f = np.geomspace(2.5e-4, 1, 401)
    link_signals = {link: source(f'link{link}') for link in LINKS}
    raw = michelson(link_signals, {}, nu, corrected=False)
    h = transfer(raw, f, 0, lengths, rates)
    gain = np.sqrt(sum(abs(v)**2 for v in h.values()))
    expected = 8*abs(np.sin(2*np.pi*f*lengths[1,2])*np.sin(4*np.pi*f*lengths[1,2]))
    assert np.allclose(gain, expected, atol=2e-12)
    static = transfer(corrected, f, 0, lengths, rates)
    assert np.max(abs(static['laser1'])) < 1e-12
    # Actual affine delays do not commute when one arm grows and one shrinks.
    rates = {link: (5e-8 if 2 in link else -5e-8) for link in LINKS}
    assert abs(path_lag(A+B, 0, lengths, rates)-path_lag(B+A, 0, lengths, rates)) > 1e-6
    # A shared board clock has the laser-like path residual (to first order).
    common = {}
    for (name, path), c in corrected.items():
        if name.startswith('eps'):
            common = combine((1, common), (c, {('eps', path): 1}))
    expected_common = {('eps', path): -nu[1]*c for (_, path), c in laser.items()}
    assert common == expected_common
    decomposed = split_board_timing(corrected)
    # The common source is collected at the amplitude level and is exactly
    # -nu_1 times the surviving local laser path polynomial.
    shared = {(name, path): c for (name, path), c in decomposed.items()
              if name == 'eps_common'}
    assert shared == {('eps_common', path): c for (_, path), c in expected_common.items()}
    # Differential coefficients are unchanged by the change of source basis.
    differential = {(name.replace('deps', 'eps', 1), path): c
                    for (name, path), c in decomposed.items() if name.startswith('deps')}
    assert differential == {(name, path): c for (name, path), c in corrected.items()
                            if name.startswith('eps')}

    # Independently evaluate the nested operators on a complex sinusoid.
    # This tests the stored-path orientation against direct function composition.
    f_test = 0.073
    for epoch in (-43200., 0., 43200.):
        for path in (A+B, B+A, A+B+B+A):
            waveform = lambda time: np.exp(2j*np.pi*f_test*time)
            for link in reversed(path):
                previous = waveform
                waveform = lambda time, link=link, previous=previous: previous(
                    time-lengths[link]-rates[link]*time)
            predicted = np.exp(2j*np.pi*f_test*(epoch-float(path_lag(path,epoch,lengths,rates))))
            assert abs(waveform(epoch)-predicted) < 1e-10
    # Verify convergence of the adiabatic power average, not a time-domain PSD.
    def epochs(n):
        return (np.arange(n)+0.5)/n*86400-43200
    coarse = mean_gains(corrected,f,epochs(25),lengths,rates)
    fine = mean_gains(corrected,f,epochs(101),lengths,rates)
    for name, reference in fine.items():
        if name.startswith('laser'):
            continue  # Tiny second-order residuals approach floating-point precision.
        mask = reference > np.max(reference)*1e-10
        assert np.max(abs(coarse[name][mask]/reference[mask]-1)) < 3e-3
    return {'clock_terms_cancel': True, 'laser_cancels_to_first_order_in_rates': True,
            'static_limit_checked': True, 'noncommuting_arms_checked': True,
            'shared_board_jitter_is_laser_like': True,
            'common_differential_decomposition_checked': True,
            'direct_tone_nested_delay_check': True,
            '25_vs_101_epoch_power_convergence_better_than_0.3_percent': True}
