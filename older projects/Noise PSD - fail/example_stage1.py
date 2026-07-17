"""
example_stage1.py
-----------------
Demonstration of the Stage 1 noise budget framework.

This script builds a simple noise budget for a single phasemeter readout
in the testbed, using analytic placeholder noise models.

Replace the analytic models with MeasuredNoise instances as you acquire
lab data (Stage 4).

Run from the lisa_noise_budget/ directory:
    python example_stage1.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from config import FREQ_CONFIG, FREQ_PLAN, ARM_CONFIG, CONSTANTS
from helpers import (
    make_freq_array_from_config,
    compute_coupling_coefficients,
)
from noise_sources import (
    LisaLaserNoise,
    ClockNoise,
    PowerLawNoise,
    SumNoise,
    AnalyticNoise,
)
from transfer_functions import (
    Unity,
    Gain,
    TDILaserSuppression,
    ClockCouplingTF,
    ChainedTF,
    FreqToPhase,
)
from budget import NoiseBudget


def main():
    # ------------------------------------------------------------------
    # 1. Frequency array
    # ------------------------------------------------------------------
    f = make_freq_array_from_config(FREQ_CONFIG)

    # ------------------------------------------------------------------
    # 2. Compute coupling coefficients from frequency plan
    # ------------------------------------------------------------------
    coeffs = compute_coupling_coefficients(FREQ_PLAN)
    print("Clock coupling coefficients (alpha_ji):")
    for k, v in coeffs["alpha"].items():
        print(f"  {k}: alpha = {v:.4e}")

    # ------------------------------------------------------------------
    # 3. Define noise sources
    #    (all analytic placeholders — replace with MeasuredNoise later)
    # ------------------------------------------------------------------

    # --- Laser frequency noise (pre-stabilised, LISA-like) ---
    laser_noise = LisaLaserNoise(
        name="Laser frequency noise (cavity)",
        asd_white=30.0,     # Hz/sqrt(Hz) — target level
        f_knee=2e-3,        # Hz — 1/f knee
    )

    # --- Free-running laser (for comparison, before cavity lock) ---
    laser_free_running = PowerLawNoise(
        name="Laser frequency noise (free-running)",
        amplitude=1e5,      # Hz/sqrt(Hz) at 1 Hz — rough placeholder
        exponent=-1,        # 1/f frequency noise
        f_ref=1.0,
    )

    # --- Clock (USO/Rb) noise ---
    # Rb clock: typical Allan dev ~1e-12 at 1 s
    clock_noise = ClockNoise(
        name="USO clock noise (Rb)",
        nu_carrier=FREQ_PLAN["f_uso"],
        sigma_y_1s=1e-12,
        f_flicker=1e-3,
    )

    # --- Delay line noise floor ---
    # Placeholder: white phase noise floor from ADC/DAC jitter
    # ADC jitter ~100 fs/sqrt(Hz) at 10 MHz input:
    #   phi_noise = 2*pi * f_beat * tau_jitter
    #             = 2*pi * 10e6 * 100e-15 ~ 6.3e-6 rad/sqrt(Hz)
    # Convert to frequency noise: nu_noise = phi_noise * f (at frequency f)
    # This is frequency-dependent (white phase -> rising frequency noise)
    f_beat_sc1 = FREQ_PLAN["f_beat"]["SC1"]
    adc_jitter = 100e-15  # s/sqrt(Hz) — placeholder, replace with measurement
    phi_noise_floor = 2.0 * np.pi * f_beat_sc1 * adc_jitter  # rad/sqrt(Hz)

    # Delay line adds white phase noise -> frequency noise ASD ~ phi_noise * f
    delay_line_noise = AnalyticNoise(
        name="Delay line floor (ADC/DAC jitter)",
        func=lambda f: (phi_noise_floor * f) ** 2,  # PSD in Hz^2/Hz
    )

    # --- Phasemeter (Moku:Pro) readout noise ---
    # Placeholder: ~1e-6 rad/sqrt(Hz) white phase noise floor
    # (measure this directly by feeding a clean signal)
    moku_phase_floor = 1e-6   # rad/sqrt(Hz) — PLACEHOLDER
    moku_noise = AnalyticNoise(
        name="Phasemeter readout noise (Moku:Pro)",
        func=lambda f: (moku_phase_floor * f) ** 2,  # Hz^2/Hz
    )

    # --- EOM modulation noise ---
    # Couples into sideband readout but not directly into carrier phase.
    # Here shown as its contribution to the clock correction residual.
    # Placeholder: white phase noise from modulation chain.
    eom_noise = PowerLawNoise(
        name="EOM modulation noise",
        amplitude=1e-4,     # Hz/sqrt(Hz) — PLACEHOLDER
        exponent=0,
    )

    # ------------------------------------------------------------------
    # 4. Build Budget A: Raw single phasemeter output (no TDI)
    # ------------------------------------------------------------------
    budget_raw = NoiseBudget(
        name="Raw phasemeter output (no TDI)",
        f=f,
        output_unit="freq",
        nu_laser=CONSTANTS["nu_laser"],
    )

    # Laser noise enters directly with unity TF at the phasemeter
    budget_raw.add(laser_noise, Unity(), label="Laser noise (cavity-locked)")
    budget_raw.add(laser_free_running, Unity(),
                   label="Laser noise (free-running)", linestyle="--")

    # Clock noise enters with coupling coefficient alpha
    alpha_12 = coeffs["alpha"]["SC2<-SC1"]
    budget_raw.add(
        clock_noise,
        Gain("clock_coupling", gain=alpha_12),
        label=f"Clock noise (alpha={alpha_12:.2e})",
    )

    # Delay line noise
    budget_raw.add(delay_line_noise, Unity(), label="Delay line floor")

    # Phasemeter noise
    budget_raw.add(moku_noise, Unity(), label="Phasemeter readout")

    # Disable free-running laser from total (it's just for reference)
    budget_raw.disable("Laser noise (free-running)")

    budget_raw.summary(f_eval=1e-3)

    # ------------------------------------------------------------------
    # 5. Build Budget B: After TDI X combination (laser noise suppressed)
    # ------------------------------------------------------------------
    tau = ARM_CONFIG["tau"]["12"]

    budget_tdi = NoiseBudget(
        name="After first-generation TDI X (laser noise suppressed)",
        f=f,
        output_unit="freq",
        nu_laser=CONSTANTS["nu_laser"],
    )

    # Laser noise after TDI
    tdi_tf = TDILaserSuppression(tau1=tau, tau2=tau)
    budget_tdi.add(laser_noise, tdi_tf, label="Laser noise (after TDI)")

    # Clock noise: not suppressed by TDI (enters differently)
    budget_tdi.add(
        clock_noise,
        Gain("clock_coupling", gain=alpha_12),
        label=f"Clock noise (after TDI, uncorrected)",
    )

    # Delay line and phasemeter noise: roughly pass through TDI
    # (conservative: treated as entering at each one-way link,
    #  full treatment in Stage 3)
    budget_tdi.add(delay_line_noise, Unity(), label="Delay line floor")
    budget_tdi.add(moku_noise, Unity(), label="Phasemeter readout")

    budget_tdi.summary(f_eval=1e-3)

    # ------------------------------------------------------------------
    # 6. Plot both budgets side by side
    # ------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    budget_raw.plot(
        ax=axes[0],
        show_total=True,
        show_lisa_req=True,
        show_laser_req=True,
        title="Raw phasemeter output",
    )

    budget_tdi.plot(
        ax=axes[1],
        show_total=True,
        show_lisa_req=True,
        title="After first-generation TDI X",
    )

    fig.suptitle("miniLISA Testbed — Stage 1 Noise Budget (analytic placeholders)",
                 fontsize=14, y=1.01)
    fig.tight_layout()
    fig.savefig("noise_budget_stage1.png", dpi=150, bbox_inches="tight")
    print("\nPlot saved to noise_budget_stage1.png")
    plt.show()

    return budget_raw, budget_tdi


if __name__ == "__main__":
    budget_raw, budget_tdi = main()
