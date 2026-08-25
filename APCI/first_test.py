#!/usr/bin/env python3
"""
apci_michelson.py
=================
Automatic Principal Component Interferometry (APCI) for laser-frequency-noise
cancellation, adapted to a miniLISA Michelson-X phasemeter dataset.

Reference
---------
Q. Baghi, J. Baker, J. Slutsky, J. I. Thorpe, "Model-independent time-delay
interferometry based on principal component analysis", PRD 104, 122001 (2021).

Idea
----
Stack integer-shifted copies of every single-link beat-note phase readout into
one tall data matrix X, take its SVD, and project the data onto the
*lowest-variance* right-singular vectors. Laser frequency noise is by far the
loudest thing in the data, so it collects in the high-variance components; the
low-variance components are the (approximately) laser-noise-free combinations --
the data-driven analogue of TDI-X / A,E,T, found without ever being told the
delays.

Scope
-----
This targets *laser* noise. Clock/timer noise (your REF pilot tones) is a
smaller secondary term and is left to your two-phasemeter correction, applied to
the beat notes before this stage. Phase is used directly (cyc); the shift+PCA
structure is identical in phase or fractional frequency because laser noise
enters as p(t-tau)-p(t) in both.
"""

import argparse
import re
import numpy as np
from scipy.linalg import svd as _svd
from scipy.signal import detrend as _detrend, welch, correlate

# ----------------------------------------------------------------------------
# 1. Loading the Moku:Delta / Moku:Pro phasemeter export
# ----------------------------------------------------------------------------
# The .txt is a metadata sidecar; the samples live in a same-stem .npy holding
# the columns the metadata describes: [Time, then per active input:
# Set Frequency, Frequency, Phase(cyc), I, Q]. We map input->channel from the
# "# % c12,c13,c21,c31,REF1,REF2,REF3" line and locate the Phase(cyc) columns by
# parsing the column-name line -- nothing about the layout is hard-coded.

import os


def _header_lines(path):
    hdr = []
    with open(path) as fh:
        for line in fh:
            if line.lstrip().startswith("#"):
                hdr.append(line)
            elif line.strip() == "":
                continue
            else:
                break
    return hdr


def _channel_order(hdr):
    """Return e.g. ['c12','c13','c21','c31','REF1','REF2','REF3']."""
    pat = re.compile(r"^(c\d+|REF\d+)$")
    for line in hdr:
        body = line.lstrip("#% ").strip()
        toks = [t.strip() for t in body.split(",")]
        if len(toks) >= 2 and all(pat.match(t) for t in toks):
            return toks
    return None


def _column_labels(hdr):
    """Return the ordered column labels from the 'Time (s), Input 1 ...' line."""
    for line in hdr:
        body = line.lstrip("#% ").strip()
        if body.startswith("Time"):
            return [t.strip() for t in body.split(",")]
    return None


def _acq_rate(hdr):
    """Sampling rate (Hz) from the 'Acquisition rate:' line, else None."""
    for line in hdr:
        m = re.search(r"Acquisition rate:\s*([0-9.eE+-]+)", line)
        if m:
            return float(m.group(1))
    return None


def _resolve_paths(path):
    """Given either the .txt metadata or the .npy data path, return (meta, data)."""
    stem, ext = os.path.splitext(path)
    meta = path if ext.lower() == ".txt" else stem + ".txt"
    data = path if ext.lower() == ".npy" else stem + ".npy"
    return meta, data


def load_dataset(path):
    """Load ALL channels' Phase(cyc) from the .npy, using the .txt metadata for
    the channel map and sampling rate. Returns (t, cols, fs) where cols maps
    each channel name (c12..REF3) to its phase array.

    Handles both a Moku structured/record array (1-D with named fields -- the
    normal export) and a plain 2-D float matrix."""
    meta, data_path = _resolve_paths(path)
    hdr = _header_lines(meta)
    order = _channel_order(hdr)
    if order is None:
        raise ValueError("Metadata missing the channel-order line.")
    D = np.load(data_path)
    fs = _acq_rate(hdr)

    if D.dtype.names is not None:                 # structured / record array
        names = D.dtype.names
        def get_phase(inp):
            key = f"Input {inp} Phase (cyc)"
            if key not in names:
                raise ValueError(f"Field '{key}' not in .npy. Have: {names}")
            return np.asarray(D[key], float)
        def get_fset(inp):
            key = f"Input {inp} Set Frequency (Hz)"
            return float(np.median(D[key])) if key in names else np.nan
        t = np.asarray(D["Time (s)"], float) if "Time (s)" in names \
            else np.arange(len(D), dtype=float)
    else:                                         # plain 2-D matrix
        labels = _column_labels(hdr)
        if D.ndim == 1:
            D = D[None, :]
        if labels is None or D.shape[1] != len(labels):
            raise ValueError(f"{os.path.basename(data_path)} has {D.shape[1]} "
                             f"columns but metadata lists "
                             f"{len(labels) if labels else '?'}.")
        pcol = {int(m.group(1)): j for j, lab in enumerate(labels)
                if (m := re.search(r"Input\s+(\d+)\s+Phase", lab))}
        scol = {int(m.group(1)): j for j, lab in enumerate(labels)
                if (m := re.search(r"Input\s+(\d+)\s+Set Frequency", lab))}
        get_phase = lambda inp: D[:, pcol[inp]].astype(float)
        get_fset = lambda inp: (float(np.median(D[:, scol[inp]]))
                                if inp in scol else np.nan)
        tc = next((j for j, l in enumerate(labels)
                   if l.lower().startswith("time")), None)
        t = D[:, tc].astype(float) if tc is not None else np.arange(D.shape[0])

    cols = {name: get_phase(idx + 1) for idx, name in enumerate(order)}
    fset = {name: get_fset(idx + 1) for idx, name in enumerate(order)}
    if fs is None:
        fs = 1.0 / np.median(np.diff(t))
    return t, cols, fset, fs


def form_eta(cols, fset, delays, omegas=(17e6, 38e6, 47e6)):
    """Clock-noise-corrected single-link variables from the raw phasemeter
    columns, via the two-pilot-tone correction:

        eta_12 =  detrend(c12) - w2 (REF1 - D_{d12} REF1)
        eta_13 =  detrend(c13) - w3 (REF1 - D_{d13} REF1)
        eta_21 = -detrend(c21) - w1 (REF2 - D_{d21} REF2)
        eta_31 = -detrend(c31) - w1 (REF3 - D_{d31} REF3)

    The pilot tones enter as TIMING in seconds (delta_t = phi_cyc / f_REF, i.e.
    phi = f * delta_t), so that w * (REF - D REF) has units of cycles and is
    commensurate with the beat-note phase. Column order out is (c12,c13,c21,c31).
    delays: dict with integer sample delays 'd12','d13','d21','d31'."""
    w1, w2, w3 = omegas
    dt = lambda x: _detrend(x, type="linear")
    S = integer_shift
    rt1 = cols["REF1"] / fset["REF1"]             # pilot tone -> seconds
    rt2 = cols["REF2"] / fset["REF2"]
    rt3 = cols["REF3"] / fset["REF3"]
    eta12 = dt(cols["c12"]) - w2 * (rt1 - S(rt1, delays["d12"]))
    eta13 = dt(cols["c13"]) - w3 * (rt1 - S(rt1, delays["d13"]))
    eta21 = -dt(cols["c21"]) - w1 * (rt2 - S(rt2, delays["d21"]))
    eta31 = -dt(cols["c31"]) - w1 * (rt3 - S(rt3, delays["d31"]))
    return np.column_stack([eta12, eta13, eta21, eta31])


def decimate_cols(Y, q):
    """Zero-phase FIR decimation by q along time (per channel)."""
    from scipy.signal import decimate
    if q <= 1:
        return Y
    return decimate(Y, q, axis=0, ftype="fir", zero_phase=True)


# ----------------------------------------------------------------------------
# 2. Pre-processing
# ----------------------------------------------------------------------------

def preprocess(Y, remove_ramp=True):
    """Strip the per-channel linear phase ramp (constant beat-note offset). The
    ramp is deterministic and would dominate the variance; removing it keeps the
    SVD focused on the (laser-noise) fluctuations."""
    Y = np.asarray(Y, float)
    Y = Y - Y[0]
    if remove_ramp:
        Y = _detrend(Y, axis=0, type="linear")
    return Y


# ----------------------------------------------------------------------------
# 3. Delay diagnostic (guide for choosing nh -- not needed by APCI itself)
# ----------------------------------------------------------------------------

def estimate_delays(Y, channels, max_lag=None):
    """One-way arm delays (samples) from beat-note cross-correlation. We
    differentiate first (phase -> frequency): the huge common slow drift that
    otherwise pins the correlation peak at lag 0 is flat in frequency, exposing
    the delayed-copy structure. c12 carries -p1 (undelayed), c21 carries +D_a p1,
    so their cross-correlation peaks at the one-way delay a. Returns {(ca,cb): lag}."""
    N = Y.shape[0]
    max_lag = N // 4 if max_lag is None else max_lag
    idx = {c: i for i, c in enumerate(channels)}
    lags = np.arange(-(N - 1) + 1, N - 1)          # diff shortens by 1
    sel = np.abs(lags) <= max_lag
    out = {}
    for ca, cb in (("c12", "c21"), ("c13", "c31")):
        if ca in idx and cb in idx:
            a = _detrend(np.diff(Y[:, idx[ca]]))
            b = _detrend(np.diff(Y[:, idx[cb]]))
            corr = correlate(a, b, mode="full", method="fft")
            k = np.argmax(np.abs(corr[sel]))
            out[(ca, cb)] = int(abs(lags[sel][k]))
    return out


def suggest_nh(delays, margin=1.2):
    """A Michelson-X-equivalent combination spans both round trips: 2*(a+b)."""
    if not delays:
        return None
    return int(np.ceil(margin * 2 * sum(delays.values())))


# ----------------------------------------------------------------------------
# 4. APCI core
# ----------------------------------------------------------------------------

def integer_shift(Y, m):
    """D^m: out[n] = Y[n-m], zero-filled edges. Works on (N,) or (N,ell)."""
    out = np.zeros_like(Y)
    N = Y.shape[0]
    if m == 0:
        out[:] = Y
    elif 0 < m < N:
        out[m:] = Y[: N - m]
    elif -N < m < 0:
        out[: N + m] = Y[-m:]
    return out


def build_data_matrix(Y, nh):
    """X = (D^{-nh}Y, ..., D^{+nh}Y), shape (N, ell*(2*nh+1))."""
    N, ell = Y.shape
    p = 2 * nh + 1
    X = np.empty((N, ell * p), dtype=float)
    for k, m in enumerate(range(-nh, nh + 1)):
        X[:, k * ell:(k + 1) * ell] = integer_shift(Y, m)
    return X


def apci_decompose(X, method="svd"):
    """Right-singular vectors V (columns = PCs) and singular values, ordered
    ASCENDING so that column 0 is the lowest-variance (most laser-suppressed)
    combination.

    method='svd' works on X directly and preserves the smallest singular values
    across the ~15-order dynamic range. method='cov' eigendecomposes X^T X
    (cheaper for very long records but squares the condition number)."""
    if method == "svd":
        _, s, Vt = _svd(X, full_matrices=False, lapack_driver="gesdd")
        V = Vt.T[:, ::-1]
        s = s[::-1]
    elif method == "cov":
        w, V = np.linalg.eigh(X.T @ X)          # ascending
        s = np.sqrt(np.clip(w, 0.0, None))
    else:
        raise ValueError(method)
    return V, s


def apci_project(X, V, q):
    """Project onto the q lowest-variance PCs -> (N, q) combination series."""
    return X @ V[:, :q]


def run_apci(Y, nh, q=6, method="svd", trim=True):
    """Full pipeline on a preprocessed (N,ell) array.
    Returns dict with combinations T (N',q), singular values, and variances."""
    X = build_data_matrix(Y, nh)
    V, s = apci_decompose(X, method=method)
    T = apci_project(X, V, q)
    if trim:                                    # drop shift-contaminated edges
        T = T[nh:-nh]
    var = s ** 2 / (X.shape[0] - 1)
    return dict(T=T, sing=s, var=var, V=V, nh=nh)


# ----------------------------------------------------------------------------
# 5. Reference first-generation Michelson-X (validation only; needs delays)
# ----------------------------------------------------------------------------

def reference_michelson_X(Y, a, b):
    """Delay-informed first-gen X for INTEGER one-way delays a (arm 1-2) and
    b (arm 1-3), with column order (c12,c13,c21,c31). Cancels laser noise by
    construction; used to check that blind APCI reaches the same floor."""
    s12, s13, s21, s31 = (Y[:, i] for i in range(4))
    S = integer_shift
    beta12 = s12 + S(s21, a)                     # 1->2->1 round trip
    beta13 = s13 + S(s31, b)                     # 1->3->1 round trip
    X = (beta12 - S(beta12, 2 * b)) - (beta13 - S(beta13, 2 * a))
    return X


# ----------------------------------------------------------------------------
# 6. Spectra
# ----------------------------------------------------------------------------

def asd(x, fs, nperseg=None):
    """Amplitude spectral density sqrt(PSD) in [unit]/sqrt(Hz)."""
    nperseg = min(len(x), 8192) if nperseg is None else nperseg
    f, p = welch(x, fs=fs, nperseg=nperseg, detrend="constant")
    return f, np.sqrt(p)


# ----------------------------------------------------------------------------
# 7. Synthetic self-test (3 lasers, integer delays, X-cancelable topology)
# ----------------------------------------------------------------------------

def make_synthetic(N=20000, fs=37.2529, a=30, b=42, seed=0,
                   laser_level=1.0, sec_level=1e-4):
    rng = np.random.default_rng(seed)

    def red(level):                              # random-walk "laser" phase
        x = np.cumsum(rng.standard_normal(N))
        x -= np.linspace(x[0], x[-1], N)
        return level * x / np.std(x)

    def sh(x, m):
        out = np.zeros_like(x)
        if m > 0:
            out[m:] = x[:N - m]
        elif m < 0:
            out[:N + m] = x[-m:]
        else:
            out[:] = x
        return out

    def n():
        return sec_level * rng.standard_normal(N)

    p1, p2, p3 = red(laser_level), red(laser_level), red(laser_level)
    s12 = sh(p2, a) - p1 + n()
    s21 = sh(p1, a) - p2 + n()
    s13 = sh(p3, b) - p1 + n()
    s31 = sh(p1, b) - p3 + n()
    Y = np.column_stack([s12, s13, s21, s31])    # (c12,c13,c21,c31)
    return Y, fs, a, b


# ----------------------------------------------------------------------------
# 8. Driver
# ----------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file", nargs="?",
                    help="Moku phasemeter .txt metadata (or its .npy sibling)")
    ap.add_argument("--minutes", type=float, default=20.0,
                    help="length of data to use (minutes)")
    ap.add_argument("--start", type=float, default=60.0,
                    help="start offset into the record (seconds)")
    ap.add_argument("--decimate", type=int, default=4,
                    help="decimation factor for the eta -> APCI stage")
    ap.add_argument("--nh", type=int, default=None,
                    help="half-stencil (decimated samples). Default: auto")
    ap.add_argument("--q", type=int, default=6,
                    help="number of lowest-variance combinations to keep")
    ap.add_argument("--method", choices=("svd", "cov"), default="svd")
    ap.add_argument("--omegas", type=float, nargs=3, default=(17e6, 38e6, 47e6),
                    help="w1 w2 w3 pilot-tone scalings for the clock correction")
    ap.add_argument("--plot", default="apci_result.png")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    ref_X = None
    names = ["c12", "c13", "c21", "c31"]

    if args.file and not args.demo:
        t, cols, fset, fs = load_dataset(args.file)
        Ntot = len(next(iter(cols.values())))
        i0 = int(args.start * fs)
        i1 = min(Ntot, i0 + int(args.minutes * 60 * fs))
        cols = {k: v[i0:i1] for k, v in cols.items()}
        print(f"[data]  fs={fs:.4f} Hz  using {i1 - i0} samples "
              f"({(i1 - i0) / fs / 60:.1f} min, offset {args.start:.0f}s)")
        print(f"[data]  f_REF = "
              f"{fset['REF1']/1e6:.3f}/{fset['REF2']/1e6:.3f}/"
              f"{fset['REF3']/1e6:.3f} MHz")

        # arm delays (full rate) from the raw beat notes, via freq-domain xcorr
        Yc = np.column_stack([cols[c] for c in names])
        d = estimate_delays(Yc, names)
        a12 = d.get(("c12", "c21"), 0)
        a13 = d.get(("c13", "c31"), 0)
        delays = dict(d12=a12, d21=a12, d13=a13, d31=a13)
        print(f"[delay] one-way (full-rate samples): arm12={a12} arm13={a13} "
              f"= {a12 / fs:.2f}s / {a13 / fs:.2f}s")

        # clock-noise correction at full rate, then decimate the eta
        eta = form_eta(cols, fset, delays, omegas=tuple(args.omegas))
        q = max(1, args.decimate)
        Y = decimate_cols(eta, q)
        fs /= q
        span_dec = int(np.ceil(2 * (a12 + a13) / q))     # Michelson-X span
        nh = args.nh or int(np.ceil(1.2 * span_dec))
        Y = preprocess(Y)
        print(f"[eta]   omegas={tuple(args.omegas)}  decimate={q} "
              f"-> fs={fs:.3f} Hz, N={len(Y)}")
    else:
        Y, fs, a, b = make_synthetic()
        Y = preprocess(Y)
        nh = args.nh or int(np.ceil(1.3 * 2 * (a + b)))
        ref_X = reference_michelson_X(Y, a, b)[nh:-nh]
        print(f"[demo]  fs={fs:.4f} Hz  N={len(Y)}  a={a} b={b}")

    approx_bytes = len(Y) * Y.shape[1] * (2 * nh + 1) * 8
    print(f"[apci]  nh={nh}  q={args.q}  method={args.method}  "
          f"(X ~ {approx_bytes / 1e6:.0f} MB)")
    res = run_apci(Y, nh=nh, q=args.q, method=args.method)
    T, var = res["T"], res["var"]

    raw = Y[nh:-nh, 0]
    supp = np.std(raw) / np.std(T[:, 0])
    print(f"[apci]  RMS suppression (eta_12 -> APCI#1): {supp:.3e}x")
    if ref_X is not None:
        print(f"[check] APCI#1 vs first-gen X RMS ratio: "
              f"{np.std(T[:, 0]) / np.std(ref_X):.3f}")

    try:
        _plot(fs, raw, T, var, ref_X, names, args.plot)
        print(f"[plot]  wrote {args.plot}")
    except Exception as e:
        print(f"[plot]  skipped ({e})")


def _plot(fs, raw, T, var, ref_X, names, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (axv, axs) = plt.subplots(1, 2, figsize=(12, 4.6))

    axv.semilogy(np.arange(1, var.size + 1), var[::-1], ".", ms=3)
    axv.set(xlabel="PCA component (descending variance)",
            ylabel="variance  [cyc$^2$]",
            title="Variance spectrum")
    axv.grid(True, which="both", alpha=0.3)

    f, a_raw = asd(raw, fs)
    axs.loglog(f, a_raw, color="0.6", lw=1, label=f"raw {names[0]}")
    for m in range(min(3, T.shape[1])):
        f, a = asd(T[:, m], fs)
        axs.loglog(f, a, lw=1, label=f"APCI #{m + 1}")
    if ref_X is not None:
        f, a = asd(ref_X, fs)
        axs.loglog(f, a, "k--", lw=1.2, label="first-gen X (delay-informed)")
    axs.set(xlabel="Frequency [Hz]",
            ylabel=r"ASD [cyc/$\sqrt{\mathrm{Hz}}$]",
            title="Laser-noise suppression")
    axs.grid(True, which="both", alpha=0.3)
    axs.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(path, dpi=130)


if __name__ == "__main__":
    main()