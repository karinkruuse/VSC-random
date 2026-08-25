

import numpy as np


def rin_to_phase(
    rin_1f,          # RIN ASD at f_het          [1/sqrt(Hz)]  (scalar or array)
    rin_2f,          # RIN ASD at 2*f_het        [1/sqrt(Hz)]  (scalar or array)
    P_m=1.0,         # measurement-beam power on the PD  [arb, only ratio matters]
    P_r=1.0,         # reference-beam power on the PD    [arb]
    contrast=1.0,    # heterodyne efficiency eta_het in [0, 1]
    split=0.5,       # recombination beamsplitter power reflectivity rho^2 (tau^2 = 1-split)
    correlated=True, # True: one laser (rm = rr, add linearly). False: two lasers (add in quad.)
    balanced=False,  # True: ideal balanced detection removes the 1f term
):

    rho2 = split
    tau2 = 1.0 - split
    rho = np.sqrt(rho2)
    tau = np.sqrt(tau2)

    # ---- 1f coupling coefficient (DC power / beat amplitude) ----
    I_dc   = rho2 * P_m + tau2 * P_r
    I_beat = 2.0 * rho * tau * np.sqrt(contrast * P_m * P_r)
    C_1f = 0.0 if balanced else I_dc / I_beat

    # correlated vs uncorrelated only rescales how the two beams' RIN combine.
    # For a single laser (correlated) the coefficient above already assumes
    # coherent addition; for two lasers the effective RIN is ~sqrt(2) smaller
    # per-beam contribution -> fold a 1/sqrt(2) into the 1f term.
    if not correlated:
        C_1f = C_1f / np.sqrt(2.0)

    # ---- 2f coupling coefficient ----
    C_2f = (1.0 / np.sqrt(2.0)) if correlated else 0.5

    phase_1f = C_1f * np.asarray(rin_1f, dtype=float)/2/np.pi
    phase_2f = C_2f * np.asarray(rin_2f, dtype=float)/2/np.pi
    phase_total = np.sqrt(phase_1f**2 + phase_2f**2)
    return phase_1f, phase_2f, phase_total


def phase_to_displacement(phase_rad, wavelength=1064e-9):
    """rad/sqrt(Hz) -> m/sqrt(Hz), single-pass:  dL = phi * lambda / (2 pi)."""
    return np.asarray(phase_rad) * wavelength / (2.0 * np.pi)


if __name__ == "__main__":
    # ---------------------------------------------------------------
    # Example: the miniLISA EOM measurement.
    # Carrier beats at 30 MHz, sidebands at 19 and 41 MHz, so the three
    # tones sample RIN at DIFFERENT frequencies:
    #     tone   f_het   2*f_het
    #     LSB    19 MHz   38 MHz
    #     Car    30 MHz   60 MHz
    #     USB    41 MHz   82 MHz
    # Supply the measured laser RIN at each of these. Placeholders below.
    # ---------------------------------------------------------------
    tones = {
        "LSB (19 MHz)": dict(rin_1f=1e-7, rin_2f=1e-8),
        "Carrier (30 MHz)": dict(rin_1f=1e-7, rin_2f=1e-8),
        "USB (41 MHz)": dict(rin_1f=1e-7, rin_2f=1e-8),
    }

    # setup: single InGaAs PD (no balanced detection), one laser (correlated),
    # sidebands ~10x weaker than carrier -> unmatched powers for the SB tones.
    common = dict(contrast=0.9, split=0.5, correlated=True, balanced=False)

    print("RIN-to-phase coupling (Wissel 2022), single unbalanced PD")
    print(f"{'tone':<18}{'1f (rad/rtHz)':>16}{'2f (rad/rtHz)':>16}"
          f"{'total (cyc/rtHz)':>18}{'disp (pm/rtHz)':>16}")
    for name, rin in tones.items():
        # crude power model: reference (LO) = 1, sideband = 0.01, carrier = 1
        Pm = 0.01 if name.startswith(("LSB", "USB")) else 1.0
        p1, p2, ptot = rin_to_phase(P_m=Pm, P_r=1.0, **rin, **common)
        cyc = ptot / (2 * np.pi)
        pm = phase_to_displacement(ptot) * 1e12
        print(f"{name:<18}{p1:>16.2e}{p2:>16.2e}{cyc:>18.2e}{pm:>16.3f}")

    print()
    print("measured per-channel floor ~1.3e-6 cyc/rtHz (~1.4 pm/rtHz) for comparison.")
    print("If the tabulated 1f/2f columns land well below that, RIN-to-phase is")
    print("not your floor. Swap in RIN values MEASURED at 19-82 MHz to decide.")

    # ---------------------------------------------------------------
    # If you have a measured RIN spectrum vs frequency (array), you can
    # evaluate the coupling across a band instead of at single points:
    #
    #   f, rin = load_your_rin_asd()          # f in Hz, rin in 1/sqrt(Hz)
    #   fhet = 30e6
    #   r1 = np.interp(fhet,   f, rin)
    #   r2 = np.interp(2*fhet, f, rin)
    #   _, _, ptot = rin_to_phase(r1, r2, ...)
    # ---------------------------------------------------------------