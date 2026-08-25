"""
build_modulation_tf.py
-----------------------
SLOW step, run once (or whenever L, dL, nu1/nu2/nu3, or the TDI
combination change). Derives the clock-corrected modulation-noise
transfer function symbolically and pickles it to disk.

The modulation frequencies omega1m, omega2m, omega3m (i.e. nu^m — the
things called num1/num2/num3 in plottingX2.py) are deliberately left as
free symbols in the saved expression. Everything else (arm length,
dtau, heterodyne beatnote frequencies nu1/nu2/nu3) is substituted
numerically here.

After running this once, use run_modulation_tf.py to plug in different
nu^m values and re-plot in seconds, without repeating any SymPy work.
"""
import pickle
from pathlib import Path

import numpy as np

from tdi_core import (
    t, tau12, tau21, tau13, tau31, tau23, tau32,
    dtau12, dtau21, dtau13, dtau31, dtau23, dtau32,
    omega1, omega2, omega3,
    omega1m, omega2m, omega3m, omega_sym,
    N1_m, N2_m, N3_m,
    build_corrected_tdi, get_transfer_function,
)

HERE = Path(__file__).parent


def build_modulation_transfer_functions(
    tdi_name='X2',
    L=2.5e9 / 299792458.0,
    dL=5e-8,
    nu1=15.0e6, nu2=10.9e6, nu3=21.6e6,
    save_path=None,
):
    """
    Derive H(omega; omega1m, omega2m, omega3m) for modulation noise in
    the clock-corrected TDI combination `tdi_name`.

    omega1m/omega2m/omega3m (nu^m) are left as free symbols so the
    numeric-evaluation step can scan over different modulation
    frequencies later. L, dL, and the heterodyne frequencies nu1/nu2/nu3
    are baked in numerically now -- rerun this function if those change.

    Returns (and pickles to `save_path`) a dict:
        {'tdi_name', 'H': {'N1_m':expr, 'N2_m':expr, 'N3_m':expr},
         'omega_sym', 'omega1m', 'omega2m', 'omega3m', 'params'}
    """
    print(f"Building clock-corrected {tdi_name} for modulation noise "
          f"(omega1m/2m/3m kept symbolic)... this can take ~1 min for X2.")
    tdi_cor = build_corrected_tdi('modulation', tdi_name)

    numeric_subs = {
        omega1: 2*np.pi*nu1, omega2: 2*np.pi*nu2, omega3: 2*np.pi*nu3,
        tau12: L, tau21: L, tau13: L, tau31: L, tau23: L, tau32: L,
        dtau12: dL, dtau21: dL, dtau13: dL, dtau31: dL, dtau23: dL, dtau32: dL,
    }

    H = {}
    for fn, key in [(N1_m, 'N1_m'), (N2_m, 'N2_m'), (N3_m, 'N3_m')]:
        H_sym = get_transfer_function(tdi_cor, fn)
        H_sym = H_sym.subs(numeric_subs).subs(t, 0)
        H[key] = H_sym
        print(f"  H[{key}] = {H_sym}")

    result = {
        'tdi_name': tdi_name,
        'H': H,
        'omega_sym': omega_sym,
        'omega1m': omega1m, 'omega2m': omega2m, 'omega3m': omega3m,
        'params': {'L': L, 'dL': dL, 'nu1': nu1, 'nu2': nu2, 'nu3': nu3},
    }

    if save_path is None:
        save_path = HERE / f'modulation_tf_{tdi_name}.pkl'
    with open(save_path, 'wb') as f:
        pickle.dump(result, f)
    print(f"Saved to {save_path}")
    return result


if __name__ == '__main__':
    build_modulation_transfer_functions(tdi_name='X2')
