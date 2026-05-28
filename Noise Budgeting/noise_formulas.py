"""
noise_formulas.py
─────────────────
Canonical definitions of every noise term in the miniLISA sideband
noise budget.  Each function is decorated with @latexify so the LaTeX
expression is generated directly from the Python source — no manual
transcription, no drift between code and documentation.

Usage (plain Python / terminal):
    python noise_formulas.py              # prints full LaTeX summary

Usage (Jupyter):
    from noise_formulas import shot_noise
    shot_noise                            # renders as LaTeX in cell

Usage from main script:
    from noise_formulas import print_formula_summary, save_formula_page
    print_formula_summary()               # LaTeX strings to stdout
    save_formula_page('outputs/formulas.png')   # rendered PNG
"""

import math, re
import latexify

pi = math.pi    # bare name so latexify renders it as \pi

_lx = dict(use_math_symbols=True, use_signature=False)

# ══════════════════════════════════════════════════════════════════════
# SIGNAL
# ══════════════════════════════════════════════════════════════════════

@latexify.function(**_lx)
def signal_sideband_peak(R, Z, eta, J_1, P_i, P_REF):
    """Peak voltage beatnote, single PD port [V].
    50:50 BS → 2ρτ=1.  SC beam EOM-modulated (J_1 factor); REF plain."""
    return 2 * R * Z * eta * J_1 * math.sqrt(P_i * P_REF)

@latexify.function(**_lx)
def signal_rms(A_sb):
    """RMS signal amplitude (peak / √2) [V]."""
    return A_sb / math.sqrt(2)

# ══════════════════════════════════════════════════════════════════════
# DC PHOTOCURRENT
# ══════════════════════════════════════════════════════════════════════

@latexify.function(**_lx)
def dc_photocurrent(R, P_i, P_REF):
    """DC photocurrent on one PD [A].  EOM conserves total beam power."""
    return R * (P_i + P_REF)

# ══════════════════════════════════════════════════════════════════════
# SINGLE-PD ELECTRONIC NOISE  [A/√Hz]
# ══════════════════════════════════════════════════════════════════════

@latexify.function(**_lx)
def shot_noise(e, I_DC):
    """Photon shot noise [A/√Hz]."""
    return math.sqrt(2 * e * I_DC)

@latexify.function(**_lx)
def dark_noise(e, I_dark):
    """Dark-current shot noise [A/√Hz]."""
    return math.sqrt(2 * e * I_dark)

@latexify.function(**_lx)
def johnson_noise(k, T, Z):
    """Johnson / thermal noise of transimpedance Z, input-referred [A/√Hz]."""
    return math.sqrt(4 * k * T / Z)

@latexify.function(**_lx)
def amp_noise_current(S_amp, Z):
    """TIA voltage noise referred to input [A/√Hz]."""
    return S_amp / Z

# ══════════════════════════════════════════════════════════════════════
# 1f-RIN   (Wissel 2022 eq. 35, with ρ²=τ²=0.5 substituted)
# ══════════════════════════════════════════════════════════════════════

@latexify.function(**_lx)
def rin_1f_voltage(R, Z, tilde_r, P_i, J_1, P_REF):
    """1f-RIN voltage noise at TIA output, single PD [V/√Hz].
    ρ²=τ²=0.5 substituted directly.  SC sideband power = P_i·J_1²."""
    return R * Z * tilde_r / 2 * math.sqrt(
        (P_i * J_1**2)**2 + P_REF**2
    )

@latexify.function(**_lx)
def rin_1f_phase(V_1f, A_rms):
    """1f-RIN phase noise, single PD [rad/√Hz]  (Wissel eq. 31).
    R·Z cancels; η and J_1 survive via A_rms."""
    return V_1f / A_rms

# ══════════════════════════════════════════════════════════════════════
# 2f-RIN   (Wissel 2022 eq. 40, ρ²=τ²=0.5 substituted)
# ══════════════════════════════════════════════════════════════════════

@latexify.function(**_lx)
def rin_2f_phase(tilde_r):
    """2f-RIN phase noise, single PD [rad/√Hz]  (Wissel 2022 eq. 40).
    Power- and Bessel-independent.  ρτ=0.5 and √(P_i J_1² P_REF)
    cancel between numerator and A_rms denominator."""
    return tilde_r / 2

# ══════════════════════════════════════════════════════════════════════
# TWO-PD COMBINATION
# ══════════════════════════════════════════════════════════════════════

@latexify.function(**_lx)
def two_pd_noise(noise_1pd):
    """Two independent PDs: noise powers add → amplitude ×√2."""
    return math.sqrt(2) * noise_1pd

# ══════════════════════════════════════════════════════════════════════
# FREQUENCY SCALING
# ══════════════════════════════════════════════════════════════════════

@latexify.function(**_lx)
def freq_scaling(f_het, nu_m):
    """Beatnote phase → sideband ranging observable r_ij.
    (Barke PhD / LISA metrology chain)"""
    return f_het / nu_m

# ══════════════════════════════════════════════════════════════════════
# CLOCK / MODULATION NOISE
# ══════════════════════════════════════════════════════════════════════

@latexify.function(**_lx)
def mod_noise_phase(f_het, nu_m, S_M, f, f_c):
    """Modulation (EOM clock) noise [rad/√Hz]."""
    return 2 * pi * (f_het + nu_m) * S_M * math.sqrt(1 + (f_c / f)**2)

@latexify.function(**_lx)
def uso_noise_phase(f_het, S_q, f):
    """USO clock noise [rad/√Hz]."""
    return 2 * pi * f_het * S_q * f**(-3 / 2)

# ══════════════════════════════════════════════════════════════════════
# DISPLACEMENT CONVERSION
# ══════════════════════════════════════════════════════════════════════

@latexify.function(**_lx)
def phase_to_displacement(phi, lam):
    """One-way displacement from phase [m/√Hz]."""
    return phi * lam / (2 * pi)


# ══════════════════════════════════════════════════════════════════════
# LaTeX cleaning: make latexify output compatible with matplotlib
# ══════════════════════════════════════════════════════════════════════

def clean_for_mpl(latex: str) -> str:
    """Strip/replace latexify constructs that matplotlib mathtext can't parse."""
    s = latex
    # Remove \mathopen{} and \mathclose{} wrappers
    s = re.sub(r'\\mathopen\{\}', '', s)
    s = re.sub(r'\\mathclose\{\}', '', s)
    # Unwrap \mathrm{...} — matplotlib handles plain names fine
    s = re.sub(r'\\mathrm\{([^}]+)\}', r'\1', s)
    # Unescape underscores (\_ → _)
    s = s.replace('\\_', '_')
    # Wrap multi-character subscripts in braces (P_REF → P_{REF})
    s = re.sub(r'_([A-Za-z][A-Za-z0-9]+)(?!\})', r'_{\1}', s)
    # Friendly substitutions for common variable names
    s = re.sub(r'\blam\b', r'\\lambda', s)
    s = re.sub(r'\btilde_r\b', r'\\tilde{r}', s)
    s = re.sub(r'\bnu_m\b', r'\\nu_m', s)
    return s


# ══════════════════════════════════════════════════════════════════════
# Summary table definition
# ══════════════════════════════════════════════════════════════════════

_SECTIONS = [
    ("Signal & DC photocurrent", [
        ("Signal peak $A_{sb}$ [V peak]",     signal_sideband_peak,
         "50:50 BS, SC sideband × unmod. REF"),
        ("Signal rms [V]",                    signal_rms,
         "sinusoid: peak / $\\sqrt{2}$"),
        ("DC photocurrent $I_{DC}$ [A]",      dc_photocurrent,
         "EOM conserves total beam power"),
    ]),
    ("Single-PD electronic noise [A/$\\sqrt{\\mathrm{Hz}}$]", [
        ("Shot noise",    shot_noise,         ""),
        ("Dark noise",    dark_noise,         ""),
        ("Johnson noise", johnson_noise,      "TIA transimpedance $Z$, input-referred"),
        ("Amp noise",     amp_noise_current,  "TIA voltage noise $S_{amp}$ [V/$\\sqrt{Hz}$]"),
    ]),
    ("RIN-to-phase [$\\mathrm{rad}/\\sqrt{\\mathrm{Hz}}$]  —  $\\rho^2{=}\\tau^2{=}0.5$, uncorrelated lasers", [
        ("1f-RIN voltage [V/$\\sqrt{Hz}$]",   rin_1f_voltage,
         "SC sideband power $P_i J_1^2$; REF plain"),
        ("1f-RIN phase (÷ $A_{rms}$)",        rin_1f_phase,
         "$R\\cdot Z$ cancels; $\\eta$, $J_1$ via $A_{rms}$"),
        ("2f-RIN phase",                      rin_2f_phase,
         "power/Bessel-independent (Wissel 2022 eq. 40)"),
    ]),
    ("Two-PD combination & frequency scaling", [
        ("Two-PD noise (×$\\sqrt{2}$)",       two_pd_noise,
         "independent PDs add in quadrature"),
        ("Freq. scaling $f_{het}/\\nu_m$",    freq_scaling,
         "beatnote phase → ranging obs. $r_{ij}$ (Barke PhD)"),
    ]),
    ("Clock noise [$\\mathrm{rad}/\\sqrt{\\mathrm{Hz}}$]", [
        ("Modulation (EOM clock)",            mod_noise_phase,
         "with $1/f$ corner at $f_c$"),
        ("USO",                               uso_noise_phase, ""),
    ]),
    ("Displacement conversion", [
        ("Phase → displacement [m/$\\sqrt{Hz}$]", phase_to_displacement,
         "one-way, $\\lambda/(2\\pi)$"),
    ]),
]


# ══════════════════════════════════════════════════════════════════════
# Terminal printer
# ══════════════════════════════════════════════════════════════════════

def print_formula_summary():
    W = 72
    print("\n" + "=" * W)
    print("  miniLISA SIDEBAND NOISE BUDGET — formula summary")
    print("  LaTeX from latexify (directly from Python source).")
    print("=" * W)
    for title, entries in _SECTIONS:
        # strip any $ from section title for terminal
        clean_title = re.sub(r'\$[^$]*\$', lambda m: m.group().strip('$'), title)
        print(f"\n{'─'*W}\n  {clean_title}\n{'─'*W}")
        for label, fn, note in entries:
            clean_label = re.sub(r'\$[^$]*\$', lambda m: m.group().strip('$'), label)
            print(f"  {clean_label}")
            print(f"    ${str(fn)}$")
            if note:
                print(f"    [{note}]")
    print("\n" + "=" * W + "\n")


# ══════════════════════════════════════════════════════════════════════
# PNG renderer — saves a formula reference page alongside the plot
# ══════════════════════════════════════════════════════════════════════

def save_formula_page(path: str = 'outputs/miniLISA_formula_reference.png'):
    """Render all formulas to a PNG using matplotlib mathtext."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    # Count total rows for figure height
    n_rows = sum(len(entries) for _, entries in _SECTIONS) + len(_SECTIONS) + 2
    fig_h = n_rows * 0.52 + 1.0
    fig, ax = plt.subplots(figsize=(13, fig_h), facecolor='white')
    ax.set_facecolor('white')
    ax.axis('off')

    # coordinate system: y goes 0 (bottom) → 1 (top), we'll work top-down
    dy = 1.0 / (n_rows + 2)
    y = 1.0 - dy * 0.6

    def put(text, yy, x=0.02, size=10, color='black', weight='normal',
            ha='left', math=False):
        kw = dict(fontsize=size, color=color, fontweight=weight,
                  transform=ax.transAxes, va='top', ha=ha)
        if math:
            text = f'${text}$'
        try:
            ax.text(x, yy, text, **kw)
        except Exception:
            # fallback: strip maths markup
            ax.text(x, yy, re.sub(r'\$[^$]*\$', '?', text), **kw)

    # Title
    put('miniLISA Sideband Noise Budget — Formula Reference',
        y, x=0.5, size=13, weight='bold', color='#1a1a2e', ha='center')
    y -= dy * 1.6

    for sec_title, entries in _SECTIONS:
        # Section divider line
        ax.axhline(y + dy * 0.55, color='#4a4a8a', linewidth=0.9,
                   xmin=0.01, xmax=0.99)
        put(sec_title, y + dy * 0.4, x=0.01, size=9.5,
            weight='bold', color='#4a4a8a')
        y -= dy * 1.05

        for label, fn, note in entries:
            latex_clean = clean_for_mpl(str(fn))
            # left column: label
            put(label, y, x=0.02, size=8.5, color='#333333')
            # right column: rendered formula
            try:
                ax.text(0.38, y, f'${latex_clean}$',
                        fontsize=9.5, color='#1a1a2e',
                        transform=ax.transAxes, va='top', ha='left')
            except Exception as err:
                ax.text(0.38, y, f'[{err}]',
                        fontsize=7, color='red',
                        transform=ax.transAxes, va='top')
            # note in grey
            if note:
                put(note, y, x=0.72, size=7.5, color='#777777')
            y -= dy

    y -= dy * 0.4
    ax.axhline(y + dy * 0.3, color='#cccccc', linewidth=0.5,
               xmin=0.01, xmax=0.99)
    put('Wissel et al. 2022 (RIN coupling)  |  Barke PhD (freq. scaling)  |  '
        'ρ²=τ²=0.5 (50:50 BS)  |  LaTeX via latexify',
        y, x=0.5, size=7, color='#999999', ha='center')

    plt.savefig(path, dpi=180, bbox_inches='tight', facecolor='white')
    print(f"Formula reference page saved → {path}")


if __name__ == "__main__":
    print_formula_summary()
    save_formula_page('outputs/miniLISA_formula_reference.png')