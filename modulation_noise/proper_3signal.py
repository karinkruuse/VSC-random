"""Three-signal frequency ASD, derived phase ASD and optional recorded-phase ASD."""
from pathlib import Path
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch


def frequency_asd(x, fs):
    """Pass the full trace to Welch using SciPy's default segmentation.

    SciPy defaults to 256-sample Hann windows, 50% overlap, constant
    detrending and mean averaging. Only amplitude densities are returned.
    """
    frequency, density = welch(x, fs=fs)
    return frequency, np.sqrt(density)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", nargs="?", type=Path,
                        default=Path(__file__).resolve().parent / "data" / "mod35_20261002_161035.npy")
    parser.add_argument("--second-pm", type=Path, help="Second phasemeter file; synchronize using common input B")
    parser.add_argument("--channels", nargs=3, type=int, metavar=("CARRIER", "LSB", "USB"))
    parser.add_argument("--cut-start", type=float, default=0)
    parser.add_argument("--cut-end", type=float, default=0, help="Seconds discarded at end (default: 0, full recording)")
    parser.add_argument("--fmin", type=float, default=0.01)
    parser.add_argument("--transient-threshold", type=float, default=5,
                        help="Hz from median in either sideband-carrier difference; diagnostic only")
    parser.add_argument("--debug", action="store_true",
                        help="Save difference time series, and difference ASD plots")
    parser.add_argument("--direct-phase", action="store_true",
                        help="Also analyse recorded phase columns in cycles using Welch")
    args = parser.parse_args()
    if min(args.cut_start, args.cut_end) < 0 or min(args.fmin, args.transient_threshold) <= 0:
        parser.error("Cuts must be nonnegative; fmin and threshold must be positive")
    data = args.data.resolve()
    if data.is_dir() or args.second_pm:
        from sync_phasemeters import synchronize
        if data.is_dir():
            files = sorted(p for p in data.glob("*.npy") if not p.stem.endswith("_synced"))
            if len(files) != 2 or args.second_pm:
                parser.error("Supply a directory with exactly two raw NPY files, or a file plus --second-pm")
        else:
            files = [data, args.second_pm]
        data = synchronize(*files)
    arr = np.load(data, allow_pickle=False)
    t = arr["Time (s)"]
    fs = 1 / np.median(np.diff(t))
    header = data.with_suffix(".txt")
    if header.exists():
        for line in header.read_text(encoding="utf-8").splitlines():
            if "Acquisition rate:" in line:
                fs = float(line.split("Acquisition rate:")[1].split("Hz")[0])
                break
    if not np.all(np.isfinite(t)) or not np.allclose(np.diff(t), 1 / fs, rtol=1e-4, atol=1e-8):
        raise ValueError("Time samples must be finite and uniformly spaced")
    if args.channels:
        carrier, lower, upper = args.channels
    else:
        inputs = [int(n.split()[1]) for n in arr.dtype.names
                  if n.startswith("Input ") and n.endswith(" Frequency (Hz)") and "Set Frequency" not in n]
        if len(inputs) != 3:
            raise ValueError("Specify --channels CARRIER LSB USB for this file")
        lower, carrier, upper = sorted(inputs, key=lambda ch: np.median(arr[f"Input {ch} Frequency (Hz)"]))
    keep = (t >= t[0] + args.cut_start) & (t <= t[-1] - args.cut_end)
    t = t[keep]
    c, l, u = [arr[f"Input {ch} Frequency (Hz)"][keep] for ch in (carrier, lower, upper)]
    if not all(np.all(np.isfinite(x)) for x in (c, l, u)):
        raise ValueError("Non-finite frequency samples")
    if len(t) < 256:
        raise ValueError("Need at least 256 samples; reduce the cuts")
    uc, cl = u - c, c - l
    signals = {"Carrier": c, "LSB": l, "USB": u,
               "USB - Carrier": uc, "Carrier - LSB": cl,
               "(USB - LSB) / 2": (u - l) / 2,
               "USB + LSB - 2 Carrier": uc - cl}
    bad = (np.abs(uc - np.median(uc)) > args.transient_threshold) | (np.abs(cl - np.median(cl)) > args.transient_threshold)
    full = {}
    for name, x in signals.items():
        frequency, asd = frequency_asd(x, fs)
        band = (frequency > 0) & (frequency >= args.fmin)
        full[name] = asd[band]
    if not np.any(band):
        raise ValueError("fmin exceeds the available frequency range")
    f = frequency[band]
    prefix = data.with_suffix("")
    colors = {"Carrier": "black", "LSB": "#295f24", "USB": "#821770",
              "USB - Carrier": "#821770", "Carrier - LSB": "#295f24",
              "(USB - LSB) / 2": "tab:blue", "USB + LSB - 2 Carrier": "tab:orange"}

    if args.debug:
        # Draw bounded, overlapping paths to avoid Agg cell-block overflow.
        # Keep every sample and every connecting edge, including narrow transients.
        # Each row has its own full scale and a second view of the central 99.8%.
        with plt.rc_context({"path.simplify": False}):
            fig, axes = plt.subplots(4, 2, figsize=(13, 10), sharex=True)
            hours = (t - t[0]) / 3600
            for row, name in enumerate(list(signals)[3:]):
                offset = np.median(signals[name])
                residual = signals[name] - offset
                lo, hi = np.quantile(residual, [.001, .999])
                margin = max((hi - lo) * .15, 1e-6)
                for col in range(2):
                    ax = axes[row, col]
                    # Share one endpoint between chunks so the trace has no gaps.
                    for start in range(0, len(hours) - 1, 1000):
                        stop = min(start + 1001, len(hours))
                        ax.plot(hours[start:stop], residual[start:stop],
                                color=colors[name], linewidth=.4, rasterized=True)
                    ax.set_ylabel("Frequency residual (Hz)")
                    ax.set_title(f"{name}; median removed: {offset:.9g} Hz", fontsize=9)
                    ax.grid(True, alpha=.25)
                    ax.set_xlim(hours[0], hours[-1])
                axes[row, 1].set_ylim(lo - margin, hi + margin)
            for ax in axes[-1]:
                ax.set_xlabel("Time since analysed start (hours)")
            fig.suptitle("Frequency differences: full scale (left), vertical zoom (right)\n"
                         "All samples retained; zoom clips large transients; no detrending")
            fig.tight_layout(rect=(0, 0, 1, .95))
            fig.savefig(f"{prefix}_freq_differences_timeseries.png", dpi=200)
            plt.close(fig)

    def plot(values, names, suffix, title, ylabel=r"Frequency ASD (Hz/$\sqrt{Hz}$)"):
        fig, ax = plt.subplots(figsize=(9, 5))
        for name in names:
            ax.loglog(f, values[name], label=name, color=colors[name], linewidth=1)
        ax.set(xlabel="Fourier frequency (Hz)", ylabel=ylabel,
               title=title, xlim=(f[0], f[-1]))
        ax.grid(True, which="both", alpha=.25)
        ax.legend(fontsize=9)
        fig.tight_layout()
        fig.savefig(f"{prefix}_{suffix}.png", dpi=200)
        plt.close(fig)

    plot(full, list(signals)[:3] + ["(USB - LSB) / 2"], "asd_freq", "Welch: measured frequency noise")
    # d(phi_cycles)/dt = frequency_Hz, so the ASD transfer is 1/(2*pi*f).
    # This integrates the frequency spectrum, not the phasemeter phase columns.
    phase = {name: value / (2 * np.pi * f) for name, value in full.items()}
    plot(phase, list(signals)[:3] + ["(USB - LSB) / 2"], "asd_phase_from_frequency",
         "Welch: phase noise derived from frequency ASD", r"Phase ASD (cycles/$\sqrt{Hz}$)")
    if args.debug:
        plot(full, list(signals)[3:], "asd_freq_differences", "Welch: modulation estimates and closure residual")
        plot(phase, list(signals)[3:], "asd_phase_from_frequency_differences",
             "Phase differences derived from frequency ASD", r"Phase ASD (cycles/$\sqrt{Hz}$)")
    if args.direct_phase:
        phase_fields = [f"Input {ch} Phase (cyc)" for ch in (carrier, lower, upper)]
        missing = [field for field in phase_fields if field not in arr.dtype.names]
        if missing:
            raise ValueError(f"Direct phase analysis requires columns: {missing}")
        pc, pl, pu = [arr[field][keep] for field in phase_fields]
        if not all(np.all(np.isfinite(x)) for x in (pc, pl, pu)):
            raise ValueError("Non-finite recorded phase samples")
        phase_signals = {"Carrier": pc, "LSB": pl, "USB": pu,
                         "USB - Carrier": pu - pc, "Carrier - LSB": pc - pl,
                         "(USB - LSB) / 2": (pu - pl) / 2,
                         "USB + LSB - 2 Carrier": (pu - pc) - (pc - pl)}
        direct_phase = {}
        for name, x in phase_signals.items():
            _, asd = frequency_asd(x, fs)
            direct_phase[name] = asd[band]
        plot(direct_phase, list(signals)[:3] + ["(USB - LSB) / 2"], "asd_phase_direct",
             "Welch: recorded phase (no rollover correction)", r"Phase ASD (cycles/$\sqrt{Hz}$)")
        if args.debug:
            plot(direct_phase, list(signals)[3:], "asd_phase_direct_differences",
                 "Welch: recorded phase differences", r"Phase ASD (cycles/$\sqrt{Hz}$)")
        np.savez(f"{prefix}_phase_asd_direct.npz", frequency_Hz=f,
                 phase_unit="cycles/sqrt(Hz)",
                 **{f"all_{name}": x for name, x in direct_phase.items()})
        print("Saved direct recorded-phase ASD (PNG/NPZ); no unwrapping or rollover correction.")

    lines = [f"Source: {data.name}", f"Channels: carrier={carrier}, LSB={lower}, USB={upper}",
             f"fs={fs:.12g} Hz; samples={len(t)}; duration={t[-1]-t[0]:.6f} s",
             f"Cuts: start={args.cut_start:g} s, end={args.cut_end:g} s",
             f"Direct recorded-phase analysis: {args.direct_phase}; same Welch defaults, no rollover correction",
             "SciPy Welch defaults: 256-sample Hann windows; 50% overlap; constant detrend; mean averaging",
             f"Frequency spacing: {frequency[1]-frequency[0]:.8g} Hz; plotted minimum: {f[0]:.8g} Hz",
             f"Transient rule: either sideband-carrier difference > {args.transient_threshold:g} Hz from its median",
             f"Flagged samples: {bad.sum()} ({100*bad.mean():.6f}%)",
             "Full traces passed to Welch; transient flags are diagnostic only, with no sample rejection.",
             "Closure = USB + LSB - 2 Carrier: ideal common carrier and opposite modulation terms both cancel.",
             "Residual spectra include source noise, readout noise and differential path effects.",
             "Derived phase ASD (cycles/sqrt(Hz)) = frequency ASD / (2*pi*Fourier frequency).",
             "Multiply derived phase ASD by 2*pi for rad/sqrt(Hz); DC is excluded.", ""]
    for name, x in signals.items():
        residual = x - np.median(x)
        lines.append(f"{name}: median={np.median(x):.12g} Hz; std={np.std(x):.8g} Hz; residual 1/50/99 percentiles={np.quantile(residual,[.01,.5,.99])} Hz; max absolute residual={np.max(abs(residual)):.8g} Hz")
    lines.append("\nMedian ASD in bands (Hz/sqrt(Hz)); these are band summaries, not integrated RMS:")
    for lo, hi in ((.01,.1),(.1,1),(1,10)):
        pick = (f >= lo) & (f < hi)
        if np.any(pick):
            for name in list(signals)[3:]:
                lines.append(f"{lo:g}-{hi:g} Hz, {name}: all={np.median(full[name][pick]):.6g}")
    Path(f"{prefix}_frequency_summary.txt").write_text("\n".join(lines)+"\n", encoding="utf-8")
    np.savetxt(f"{prefix}_frequency_transients.csv", np.column_stack((t[bad], (uc-np.median(uc))[bad], (cl-np.median(cl))[bad])),
               delimiter=",", header="time_s,USB_minus_carrier_residual_Hz,carrier_minus_LSB_residual_Hz", comments="")
    np.savez(f"{prefix}_frequency_asd.npz", frequency_Hz=f,
             **{f"all_{name}": x for name, x in full.items()})
    np.savez(f"{prefix}_phase_asd_from_frequency.npz", frequency_Hz=f,
             phase_unit="cycles/sqrt(Hz)",
             **{f"all_{name}": x for name, x in phase.items()})
    print("\n".join(lines))
    print(f"Saved frequency and derived phase ASDs (PNG/NPZ), summary and transient list beside {data.name}")


if __name__ == "__main__":
    main()
