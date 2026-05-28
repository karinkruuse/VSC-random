"""
config_loader.py
----------------
Load and access the miniLISA testbed configuration.

Usage
-----
    from config_loader import load_config, cfg

    # Option A: module-level singleton — picks up the MINILISA_CONFIG
    #           environment variable, or prompts interactively if not set.
    print(cfg.beatnote.f_het_min)

    # Option B: explicit path passed by the caller
    cfg2 = load_config("path/to/my_config.toml")

    # Option C: interactive selection from a config folder
    cfg3 = load_config(interactive=True, config_dir="conf")

Interactive selection
---------------------
    When interactive=True (or when no path / env-var is set), the loader
    scans `config_dir` for *.toml files, prints a numbered menu, and waits
    for the user to press a key.  No Enter needed — single keypress only.

    Set MINILISA_CONFIG=/path/to/file.toml in the environment to skip the
    prompt entirely (useful for automated runs / CI).

Config directory
----------------
    Default config_dir is a folder named  conf/  that sits next to this
    script.  Drop any *.toml file there and it will appear in the menu.

Requires Python >= 3.11 for tomllib (stdlib).
For Python 3.9 / 3.10:  pip install tomli
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

# ---------------------------------------------------------------------------
# TOML loading  (stdlib in 3.11+, tomli on older versions)
# ---------------------------------------------------------------------------
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError as exc:
        raise ImportError(
            "Python < 3.11 requires the 'tomli' package: pip install tomli"
        ) from exc

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent
_DEFAULT_CONF_DIR = _HERE / "conf"
_ENV_VAR = "MINILISA_CONFIG"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dict_to_namespace(d: dict[str, Any]) -> SimpleNamespace:
    """Recursively convert a nested dict into SimpleNamespace objects."""
    ns = SimpleNamespace()
    for key, value in d.items():
        setattr(ns, key, _dict_to_namespace(value) if isinstance(value, dict) else value)
    return ns


def _getkey() -> str:
    """Read a single keypress without requiring Enter (cross-platform)."""
    if sys.platform == "win32":
        import msvcrt
        return msvcrt.getwch()
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _select_config(config_dir: str | Path) -> Path:
    """
    Scan config_dir for *.toml files, print a numbered menu, and return
    the path chosen by the user via a single keypress.
    """
    config_dir = Path(config_dir)
    if not config_dir.is_dir():
        raise FileNotFoundError(
            f"Config directory not found: {config_dir}\n"
            f"Create it and place *.toml files inside, or pass an explicit path."
        )

    tomls = sorted(config_dir.glob("*.toml"))
    if not tomls:
        raise FileNotFoundError(f"No *.toml files found in {config_dir}")

    # Build menu — support up to 9 entries with digit keys, then a–z
    keys = list("123456789abcdefghijklmnopqrstuvwxyz")
    if len(tomls) > len(keys):
        tomls = tomls[: len(keys)]          # silently cap at 35 entries

    print("\n┌─ miniLISA config selector " + "─" * 40)
    for k, p in zip(keys, tomls):
        print(f"│  [{k}]  {p.name}")
    print("└" + "─" * 67)
    print("    Press a key to select: ", end="", flush=True)

    while True:
        ch = _getkey().lower()
        if ch in keys[: len(tomls)]:
            chosen = tomls[keys.index(ch)]
            print(ch)   # echo the pressed key
            print(f"    → {chosen.name}\n")
            return chosen
        # ignore any other key


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_config(
    path: str | Path | None = None,
    *,
    interactive: bool = False,
    config_dir: str | Path = _DEFAULT_CONF_DIR,
) -> SimpleNamespace:
    """
    Parse a TOML config file and return a SimpleNamespace tree.

    Resolution order
    ----------------
    1. `path` argument, if given explicitly.
    2. MINILISA_CONFIG environment variable (full path to .toml).
    3. Interactive menu (if interactive=True or no other source found).

    Parameters
    ----------
    path : str, Path, or None
        Explicit path to a .toml file.  Overrides everything else.
    interactive : bool
        Force the interactive menu even if `path` is not given but
        MINILISA_CONFIG is set (useful for one-off overrides).
    config_dir : str or Path
        Directory scanned for *.toml files shown in the interactive menu.
        Defaults to  <script_dir>/conf/.

    Returns
    -------
    SimpleNamespace
        Nested namespace; TOML table sections become attributes.
        Example: cfg.clocks.f_USO, cfg.beatnote.f_het_min
    """
    # 1. Explicit path
    if path is not None:
        resolved = Path(path)

    # 2. Environment variable (skip if interactive override requested)
    elif not interactive and (env := os.environ.get(_ENV_VAR)):
        resolved = Path(env)
        print(f"[config_loader] Using MINILISA_CONFIG={resolved}")

    # 3. Interactive menu
    else:
        resolved = _select_config(config_dir)

    if not resolved.exists():
        raise FileNotFoundError(f"Config file not found: {resolved}")

    with resolved.open("rb") as fh:
        raw = tomllib.load(fh)
    return _dict_to_namespace(raw)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
# Loaded once on import.  Uses env-var if set, otherwise prompts.
# Scripts that want to pass a specific path should call load_config()
# directly and not use this singleton.
cfg = load_config()


# ---------------------------------------------------------------------------
# Quick sanity check / demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
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