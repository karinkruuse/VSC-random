"""
budget/budget.py
----------------
The NoiseBudget class: the central object that assembles noise sources,
transfer functions, and produces output PSDs and plots.

Usage
-----
    from budget.budget import NoiseBudget
    from noise_sources.base import LisaLaserNoise, ClockNoise
    from transfer_functions.base import Unity, TDILaserSuppression

    budget = NoiseBudget(name="Single phasemeter output", f=freq_array)

    # Add a noise contribution: (noise_source, transfer_function)
    budget.add(LisaLaserNoise(), Unity(), label="Laser noise (raw)")
    budget.add(ClockNoise(), Unity(), label="Clock noise")

    budget.plot()
    summary = budget.summary()
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from dataclasses import dataclass, field
from typing import Optional, List

from noise_sources import NoiseSource
from transfer_functions import TransferFunction
from helpers import (
    psd_to_asd,
    freq_noise_asd_to_displacement_asd,
    lisa_secondary_noise_freq,
    lisa_laser_noise_requirement,
)


@dataclass
class NoiseTerm:
    """A single (noise source, transfer function) pair with a label."""
    noise: NoiseSource
    tf: TransferFunction
    label: str
    color: Optional[str] = None
    linestyle: str = "-"
    enabled: bool = True


class NoiseBudget:
    """
    Assembles noise sources and transfer functions to compute a total
    output noise PSD, broken down by contributing term.

    Parameters
    ----------
    name : str
        Name of this budget (used in plot titles).
    f : np.ndarray
        Frequency array  [Hz].
    output_unit : str
        'freq'  -> Hz/sqrt(Hz)   (default)
        'phase' -> rad/sqrt(Hz)
        'disp'  -> m/sqrt(Hz)
    nu_laser : float
        Laser carrier frequency for displacement conversion  [Hz].
    """

    UNIT_LABELS = {
        "freq":  r"Frequency noise ASD  [Hz/$\sqrt{\mathrm{Hz}}$]",
        "phase": r"Phase noise ASD  [rad/$\sqrt{\mathrm{Hz}}$]",
        "disp":  r"Displacement ASD  [m/$\sqrt{\mathrm{Hz}}$]",
    }

    def __init__(
        self,
        name: str,
        f: np.ndarray,
        output_unit: str = "freq",
        nu_laser: float = 281e12,
    ):
        if output_unit not in self.UNIT_LABELS:
            raise ValueError(
                f"output_unit must be one of {list(self.UNIT_LABELS)}, "
                f"got '{output_unit}'"
            )
        self.name = name
        self.f = np.asarray(f, dtype=float)
        self.output_unit = output_unit
        self.nu_laser = nu_laser
        self._terms: List[NoiseTerm] = []

    # ------------------------------------------------------------------
    # Building the budget
    # ------------------------------------------------------------------

    def add(
        self,
        noise: NoiseSource,
        tf: TransferFunction,
        label: Optional[str] = None,
        color: Optional[str] = None,
        linestyle: str = "-",
        enabled: bool = True,
    ) -> "NoiseBudget":
        """
        Add a noise term to the budget.

        Parameters
        ----------
        noise : NoiseSource
        tf : TransferFunction
        label : str, optional
            Display label.  Defaults to noise.name.
        color : str, optional
            Matplotlib color string.
        linestyle : str
            Matplotlib linestyle.
        enabled : bool
            If False, the term is stored but excluded from totals and plots.

        Returns
        -------
        self  (for chaining)
        """
        if label is None:
            label = noise.name
        self._terms.append(
            NoiseTerm(
                noise=noise,
                tf=tf,
                label=label,
                color=color,
                linestyle=linestyle,
                enabled=enabled,
            )
        )
        return self

    def remove(self, label: str) -> "NoiseBudget":
        """Remove a term by label."""
        self._terms = [t for t in self._terms if t.label != label]
        return self

    def enable(self, label: str) -> "NoiseBudget":
        for t in self._terms:
            if t.label == label:
                t.enabled = True
        return self

    def disable(self, label: str) -> "NoiseBudget":
        for t in self._terms:
            if t.label == label:
                t.enabled = False
        return self

    # ------------------------------------------------------------------
    # Computing PSDs
    # ------------------------------------------------------------------

    def _output_psd(self, term: NoiseTerm) -> np.ndarray:
        """
        Compute the output PSD for a single term, in the budget's output units.
        Internal: always works in freq noise PSD [Hz^2/Hz], converts at end.
        """
        # PSD after transfer function, in Hz^2/Hz
        psd_freq = term.tf.apply(term.noise, self.f)

        if self.output_unit == "freq":
            return psd_freq
        elif self.output_unit == "phase":
            # S_phase = S_freq / (2*pi*f)^2
            return psd_freq / (2.0 * np.pi * self.f) ** 2
        elif self.output_unit == "disp":
            asd_freq = psd_to_asd(psd_freq)
            asd_disp = freq_noise_asd_to_displacement_asd(
                asd_freq, self.f, nu_laser=self.nu_laser
            )
            return asd_disp**2

    def term_asds(self) -> dict[str, np.ndarray]:
        """
        Compute the output ASD for each enabled term.

        Returns
        -------
        dict  label -> ASD array
        """
        return {
            t.label: psd_to_asd(self._output_psd(t))
            for t in self._terms
            if t.enabled
        }

    def total_asd(self) -> np.ndarray:
        """
        Quadrature sum of all enabled terms.

        Returns
        -------
        np.ndarray  [output unit / sqrt(Hz)]
        """
        total_psd = sum(
            self._output_psd(t) for t in self._terms if t.enabled
        )
        return psd_to_asd(total_psd)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self, f_eval: Optional[float] = None) -> str:
        """
        Print a summary table of noise contributions.

        Parameters
        ----------
        f_eval : float, optional
            Frequency at which to evaluate and rank contributions  [Hz].
            Defaults to the geometric mean of the frequency array.
        """
        if f_eval is None:
            f_eval = np.sqrt(self.f[0] * self.f[-1])

        # Find nearest frequency index
        idx = np.argmin(np.abs(self.f - f_eval))
        f_actual = self.f[idx]

        unit = self.output_unit
        lines = [
            f"\n{'='*60}",
            f"  Noise Budget: {self.name}",
            f"  Evaluated at f = {f_actual:.4g} Hz",
            f"  Output unit: {unit}",
            f"{'='*60}",
            f"  {'Label':<35} {'ASD':>15}",
            f"  {'-'*50}",
        ]

        asds = self.term_asds()
        # Sort by contribution at f_eval
        sorted_items = sorted(
            asds.items(),
            key=lambda kv: kv[1][idx],
            reverse=True,
        )

        for label, asd in sorted_items:
            lines.append(f"  {label:<35} {asd[idx]:>15.3e}")

        total = self.total_asd()[idx]
        lines += [
            f"  {'-'*50}",
            f"  {'TOTAL (quadrature)':<35} {total:>15.3e}",
            f"{'='*60}\n",
        ]

        result = "\n".join(lines)
        print(result)
        return result

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------

    def plot(
        self,
        ax: Optional[plt.Axes] = None,
        show_total: bool = True,
        show_lisa_req: bool = True,
        show_laser_req: bool = False,
        figsize: tuple = (10, 6),
        title: Optional[str] = None,
        ylim: Optional[tuple] = None,
        xlim: Optional[tuple] = None,
        save_path: Optional[str] = None,
    ) -> plt.Figure:
        """
        Plot the noise budget.

        Parameters
        ----------
        ax : matplotlib Axes, optional
            Plot into an existing axes if provided.
        show_total : bool
            Whether to plot the quadrature total.
        show_lisa_req : bool
            Whether to overlay the LISA secondary noise requirement.
        show_laser_req : bool
            Whether to overlay the LISA pre-stabilised laser noise level.
        figsize : tuple
        title : str, optional
        ylim : tuple, optional
        xlim : tuple, optional
        save_path : str, optional
            If given, save the figure to this path.

        Returns
        -------
        matplotlib Figure
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.get_figure()

        # Assign colors automatically if not set
        cmap = cm.get_cmap("tab10")
        enabled_terms = [t for t in self._terms if t.enabled]
        for i, term in enumerate(enabled_terms):
            if term.color is None:
                term.color = cmap(i % 10)

        # Plot individual terms
        asds = self.term_asds()
        for term in enabled_terms:
            ax.loglog(
                self.f,
                asds[term.label],
                color=term.color,
                linestyle=term.linestyle,
                linewidth=1.5,
                alpha=0.85,
                label=term.label,
            )

        # Total
        if show_total:
            ax.loglog(
                self.f,
                self.total_asd(),
                color="black",
                linewidth=2.0,
                linestyle="--",
                label="Total (quadrature sum)",
                zorder=5,
            )

        # LISA secondary noise requirement
        if show_lisa_req and self.output_unit in ("freq", "disp"):
            if self.output_unit == "freq":
                req = lisa_secondary_noise_freq(self.f, nu_laser=self.nu_laser)
            else:
                from helpers import lisa_secondary_noise_displacement
                req = lisa_secondary_noise_displacement(self.f)
            ax.loglog(
                self.f,
                req,
                color="gray",
                linewidth=1.5,
                linestyle="--",
                label="LISA secondary noise req.",
                zorder=4,
            )

        # LISA laser noise requirement
        if show_laser_req and self.output_unit == "freq":
            req = lisa_laser_noise_requirement(self.f)
            ax.loglog(
                self.f,
                req,
                color="lightgray",
                linewidth=1.5,
                linestyle=":",
                label="LISA laser noise req. (pre-stab)",
                zorder=3,
            )

        # Labels and formatting
        ax.set_xlabel("Frequency  [Hz]", fontsize=12)
        ax.set_ylabel(self.UNIT_LABELS[self.output_unit], fontsize=12)
        ax.set_title(title or self.name, fontsize=13)
        ax.legend(fontsize=9, loc="upper right")
        ax.grid(True, which="both", alpha=0.3)

        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)

        fig.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")

        return fig
