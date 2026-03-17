"""
config_loader.py
----------------
Load and access the miniLISA testbed configuration.

Usage
-----
    from config_loader import load_config, cfg

    # Option A: use the module-level singleton (loads once on import)
    print(cfg.beatnote.f_het_min)

    # Option B: load explicitly (e.g. different file or reload)
    cfg2 = load_config("path/to/other_config.toml")
    print(cfg2.clocks.f_USO)

Requires Python >= 3.11 for tomllib (stdlib).
For Python 3.9 / 3.10 install tomli:  pip install tomli
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

# ---------------------------------------------------------------------------
# TOML loading (stdlib in 3.11+, tomli on older versions)
# ---------------------------------------------------------------------------
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib          # pip install tomli
    except ImportError as exc:
        raise ImportError(
            "Python < 3.11 requires the 'tomli' package: pip install tomli"
        ) from exc

# Default config path sits next to this script
_DEFAULT_CONFIG = Path(__file__).parent / "minilisa_config.toml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dict_to_namespace(d: dict[str, Any]) -> SimpleNamespace:
    """Recursively convert a nested dict into SimpleNamespace objects."""
    ns = SimpleNamespace()
    for key, value in d.items():
        setattr(ns, key, _dict_to_namespace(value) if isinstance(value, dict) else value)
    return ns


def load_config(path: str | Path = _DEFAULT_CONFIG) -> SimpleNamespace:
    """
    Parse a TOML config file and return a SimpleNamespace tree.

    Parameters
    ----------
    path : str or Path
        Path to the .toml config file.

    Returns
    -------
    SimpleNamespace
        Nested namespace; TOML sections become attributes.
        Example: cfg.clocks.f_USO, cfg.beatnote.f_het_min
    """
    path = Path(path)
    with path.open("rb") as fh:
        raw = tomllib.load(fh)
    return _dict_to_namespace(raw)


# Module-level singleton — loaded once from the default path
cfg = load_config()


# ---------------------------------------------------------------------------
# Quick sanity check / demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import math

    print("=== miniLISA config ===\n")

    print(f"  USO frequency       : {cfg.clocks.f_USO / 1e6:.1f} MHz")
    print(f"  Beatnote range      : {cfg.beatnote.f_het_min/1e6:.0f} – "
          f"{cfg.beatnote.f_het_max/1e6:.0f} MHz")
    print(f"  SB offset           : {cfg.modulation.delta_f_SB/1e6:.1f} MHz")
    print(f"  Light travel time   : {cfg.geometry.tau:.2f} s")
    print(f"  TDI null (computed) : {1/(2*cfg.geometry.tau)*1e3:.1f} mHz")
    print(f"  TDI null (config)   : {cfg.science_band.f_TDI_null*1e3:.1f} mHz")
    print(f"  Science band        : {cfg.science_band.f_science_min*1e3:.1f} mHz – "
          f"{cfg.science_band.f_science_max:.1f} Hz")
    print(f"  TDIR ranging tone   : {cfg.ranging.f_tone_TDIR:.4f} Hz  "
          f"(= 1/{1/cfg.ranging.f_tone_TDIR:.0f} Hz)")
