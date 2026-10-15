"""Three-signal frequency ASD, derived phase ASD and optional recorded-phase ASD."""
from pathlib import Path
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.ndimage import median_filter


def frequency_asd(x, fs, nperseg):
    """Pass the full trace to Welch using SciPy's default segmentation.

    SciPy uses Hann windows, its default 50% overlap and mean averaging.
    Linear detrending is applied independently to each window.
    Only amplitude densities are returned.
    """
    frequency, density = welch(x, fs=fs, nperseg=nperseg,
                               detrend="linear")
    return frequency, np.sqrt(density)


def detect_spikes(series, sigma_threshold, absolute_threshold, window):
    """Detect isolated local outliers using a rolling median and robust scale."""
    local_residual = series - median_filter(series, size=window, mode="nearest")
    center = np.median(local_residual)
    robust_sigma = 1.4826 * np.median(np.abs(local_residual - center))
    if robust_sigma == 0:
        robust = np.zeros(len(series), dtype=bool)
    else:
        robust = np.abs(local_residual - center) > sigma_threshold * robust_sigma
    absolute = np.abs(local_residual - center) > absolute_threshold
    return robust | absolute, robust_sigma, local_residual


def interpolate_masked(series, bad):
    """Replace flagged samples by linear interpolation on the original grid."""
    if not np.any(bad):
        return series.copy()
    good = ~bad
    if np.count_nonzero(good) < 2:
        raise ValueError("Too few unflagged samples to interpolate spikes")
    sample = np.arange(len(series))
    return np.interp(sample, sample[good], series[good])


def minmax_envelope(t, x, max_bins=6000):
    """Compact a dense trace for plotting while retaining every bin extreme."""
    if len(x) <= 2 * max_bins:
        return t, x
    edges = np.linspace(0, len(x), max_bins + 1, dtype=int)
    out_t = np.empty(2 * max_bins)
    out_x = np.empty(2 * max_bins)
    for i, (start, stop) in enumerate(zip(edges[:-1], edges[1:])):
        block = x[start:stop]
        out_t[2*i:2*i+2] = t[(start + stop - 1) // 2]
        out_x[2*i:2*i+2] = (np.min(block), np.max(block))
    return out_t, out_x


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", nargs="?", type=Path,
                        help="NPY file or directory containing a two-PM pair; omit for menu")
    parser.add_argument("--second-pm", type=Path,
                        help="Second phasemeter file; synchronize using common input B")
    parser.add_argument(
        "--search-dir", type=Path,
        default=Path(__file__).resolve().parent / "data",
        help="Directory searched recursively in interactive mode (default: modulation_noise/data)",
    )
    parser.add_argument("--channels", nargs=3, type=int, metavar=("CARRIER", "LSB", "USB"))
    parser.add_argument("--cut-start", type=float, default=0)
    parser.add_argument("--cut-end", type=float, default=0, help="Seconds discarded at end (default: 0, full recording)")
    parser.add_argument("--fmin", type=float, default=5e-5)
    parser.add_argument("--welch-seconds", type=float, default=4*3600,
                        help="Welch window duration in seconds (default: 4 hours)")
    parser.add_argument("--transient-threshold", type=float, default=5,
                        help="Absolute local spike threshold in Hz (default: 5)")
    parser.add_argument("--exclude-spikes", action="store_true",
                        help="Detect isolated spikes and interpolate them before Welch")
    parser.add_argument("--spike-sigma", type=float, default=7,
                        help="Robust local spike threshold (default: 7 sigma)")
    parser.add_argument("--spike-window", type=int, default=11,
                        help="Odd rolling-median window in samples (default: 11)")
    parser.add_argument("--debug", action="store_true",
                        help="Save difference time series, and difference ASD plots")
    parser.add_argument("--direct-phase", action="store_true",
                        help="Also analyse recorded phase columns in cycles using Welch")
    args = parser.parse_args()
    if min(args.cut_start, args.cut_end) < 0 or min(args.fmin, args.welch_seconds,
                                                    args.transient_threshold,
                                                    args.spike_sigma) <= 0:
        parser.error("Cuts must be nonnegative; fmin and threshold must be positive")
    if args.spike_window < 3 or args.spike_window % 2 == 0:
        parser.error("--spike-window must be an odd integer of at least 3")
    files = None
    if args.data is None:
        if args.second_pm is not None:
            parser.error("--second-pm requires the first NPY path, or omit both paths for the menu")
        from plot_two_pm_absolute_time import choose_pair
        files = choose_pair(args.search_dir)
    else:
        data = args.data.resolve()
    if files is not None or data.is_dir() or args.second_pm:
        from sync_phasemeters import synchronize
        if files is not None:
            pass
        elif data.is_dir():
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
    c_raw, l_raw, u_raw = [np.asarray(arr[f"Input {ch} Frequency (Hz)"][keep])
                           for ch in (carrier, lower, upper)]
    if not all(np.all(np.isfinite(x)) for x in (c_raw, l_raw, u_raw)):
        raise ValueError("Non-finite frequency samples")
    if len(t) < 256:
        raise ValueError("Need at least 256 samples; reduce the cuts")
    nperseg = min(len(t), int(round(args.welch_seconds * fs)))
    if nperseg < 256:
        raise ValueError("Welch window must contain at least 256 samples")
    noverlap = nperseg // 2
    welch_segments = 1 + (len(t) - nperseg) // (nperseg - noverlap)
    uc_raw, cl_raw = u_raw - c_raw, c_raw - l_raw
    modulation_raw = (u_raw - l_raw) / 2
    raw_signals = {"Carrier": c_raw, "LSB": l_raw, "USB": u_raw,
                   "USB - Carrier": uc_raw, "Carrier - LSB": cl_raw,
                   "(USB - LSB) / 2": modulation_raw,
                   "USB + LSB - 2 Carrier": uc_raw - cl_raw}
    spike_diagnostics = {}
    bad = np.zeros(len(t), dtype=bool)
    for name in ("USB - Carrier", "Carrier - LSB", "(USB - LSB) / 2"):
        found, robust_sigma, local_residual = detect_spikes(
            raw_signals[name], args.spike_sigma,
            args.transient_threshold, args.spike_window)
        bad |= found
        spike_diagnostics[name] = (robust_sigma, local_residual)
    if args.exclude_spikes:
        c, l, u = [interpolate_masked(x, bad) for x in (c_raw, l_raw, u_raw)]
    else:
        c, l, u = c_raw, l_raw, u_raw
    uc, cl = u - c, c - l
    signals = {"Carrier": c, "LSB": l, "USB": u,
               "USB - Carrier": uc, "Carrier - LSB": cl,
               "(USB - LSB) / 2": (u - l) / 2,
               "USB + LSB - 2 Carrier": uc - cl}
    full = {}
    for name, x in signals.items():
        frequency, asd = frequency_asd(x, fs, nperseg)
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
        hours = (t - t[0]) / 3600
        raw_names = ["Carrier", "LSB", "USB", "(USB - LSB) / 2"]
        fig, axes = plt.subplots(4, 1, figsize=(11, 9), sharex=True)
        for ax, name in zip(axes, raw_names):
            offset = np.median(raw_signals[name])
            residual = raw_signals[name] - offset
            plot_t, plot_x = minmax_envelope(hours, residual)
            ax.plot(plot_t, plot_x, color=colors[name], linewidth=.5)
            if np.any(bad):
                ax.scatter(hours[bad], residual[bad], s=10, color="red", zorder=3,
                           label="excluded sample (flagged in a difference)")
                ax.legend(fontsize=8, loc="upper right")
            ax.set_ylabel("Residual (Hz)")
            ax.set_title(f"{name}; median removed: {offset:.9g} Hz", fontsize=9)
            ax.grid(True, alpha=.25)
        axes[-1].set_xlabel("Time since synchronized start (hours)")
        fig.suptitle("Raw synchronized frequency data\n"
                     "Min/max envelope for display; no detrending or spike replacement")
        fig.tight_layout(rect=(0, 0, 1, .95))
        fig.savefig(f"{prefix}_raw_frequency_timeseries.png", dpi=200)
        plt.close(fig)

        # Difference views use raw samples. The right column clips only the
        # vertical plotting range, making slow changes and outliers visible.
        fig, axes = plt.subplots(4, 2, figsize=(13, 10), sharex=True)
        for row, name in enumerate(list(raw_signals)[3:]):
            offset = np.median(raw_signals[name])
            residual = raw_signals[name] - offset
            plot_t, plot_x = minmax_envelope(hours, residual)
            lo, hi = np.quantile(residual, [.001, .999])
            margin = max((hi - lo) * .15, 1e-6)
            for col in range(2):
                ax = axes[row, col]
                ax.plot(plot_t, plot_x, color=colors[name], linewidth=.5)
                if np.any(bad):
                    ax.scatter(hours[bad], residual[bad], s=8, color="red", zorder=3)
                ax.set_ylabel("Frequency residual (Hz)")
                ax.set_title(f"{name}; median removed: {offset:.9g} Hz", fontsize=9)
                ax.grid(True, alpha=.25)
                ax.set_xlim(hours[0], hours[-1])
            axes[row, 1].set_ylim(lo - margin, hi + margin)
        for ax in axes[-1]:
            ax.set_xlabel("Time since synchronized start (hours)")
        fig.suptitle("Raw frequency differences: full scale (left), vertical zoom (right)\n"
                     "Red points are detected outliers; no detrending or replacement")
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

    plot(full, list(signals)[:3] + ["(USB - LSB) / 2"], "asd_freq",
         "Welch: measured frequency noise (linear detrending)")
    # d(phi_cycles)/dt = frequency_Hz, so the ASD transfer is 1/(2*pi*f).
    # This integrates the frequency spectrum, not the phasemeter phase columns.
    phase = {name: value / (2 * np.pi * f) for name, value in full.items()}
    plot(phase, list(signals)[:3] + ["(USB - LSB) / 2"], "asd_phase_from_frequency",
         "Welch: phase noise derived from frequency ASD", r"Phase ASD (cycles/$\sqrt{Hz}$)")
    if args.debug:
        plot(full, list(signals)[3:], "asd_freq_differences", "Welch: modulation estimates and closure residual")
        plot(phase, list(signals)[3:], "asd_phase_from_frequency_differences",
             "Phase differences derived from frequency ASD", r"Phase ASD (cycles/$\sqrt{Hz}$)")
        if args.exclude_spikes and np.any(bad):
            raw_full = {}
            for name, x in raw_signals.items():
                _, raw_asd = frequency_asd(x, fs, nperseg)
                raw_full[name] = raw_asd[band]
            fig, ax = plt.subplots(figsize=(9, 5))
            for name in list(signals)[3:]:
                ax.loglog(f, raw_full[name], color=colors[name], alpha=.3,
                          linewidth=.7)
                ax.loglog(f, full[name], color=colors[name], linewidth=1,
                          label=f"{name} (cleaned)")
            ax.set(xlabel="Fourier frequency (Hz)",
                   ylabel=r"Frequency ASD (Hz/$\sqrt{Hz}$)",
                   title="Spike exclusion comparison (faint: raw)",
                   xlim=(f[0], f[-1]))
            ax.grid(True, which="both", alpha=.25)
            ax.legend(fontsize=8)
            fig.tight_layout()
            fig.savefig(f"{prefix}_asd_freq_spike_comparison.png", dpi=200)
            plt.close(fig)
    if args.direct_phase:
        phase_fields = [f"Input {ch} Phase (cyc)" for ch in (carrier, lower, upper)]
        missing = [field for field in phase_fields if field not in arr.dtype.names]
        if missing:
            raise ValueError(f"Direct phase analysis requires columns: {missing}")
        pc, pl, pu = [np.asarray(arr[field][keep]) for field in phase_fields]
        if not all(np.all(np.isfinite(x)) for x in (pc, pl, pu)):
            raise ValueError("Non-finite recorded phase samples")
        if args.exclude_spikes:
            pc, pl, pu = [interpolate_masked(x, bad) for x in (pc, pl, pu)]
        phase_signals = {"Carrier": pc, "LSB": pl, "USB": pu,
                         "USB - Carrier": pu - pc, "Carrier - LSB": pc - pl,
                         "(USB - LSB) / 2": (pu - pl) / 2,
                         "USB + LSB - 2 Carrier": (pu - pc) - (pc - pl)}
        direct_phase = {}
        for name, x in phase_signals.items():
            _, asd = frequency_asd(x, fs, nperseg)
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
             f"SciPy Welch: {nperseg} samples ({nperseg/fs:.6f} s) per Hann window; 50% overlap; {welch_segments} windows; linear detrend per window; mean averaging",
             f"Frequency spacing: {frequency[1]-frequency[0]:.8g} Hz; plotted minimum: {f[0]:.8g} Hz",
             f"Spike rule: local residual > {args.spike_sigma:g} robust sigma or > {args.transient_threshold:g} Hz; rolling median window={args.spike_window} samples",
             f"Detected spike samples: {bad.sum()} ({100*bad.mean():.9f}%)",
             f"Spike exclusion applied: {args.exclude_spikes}; flagged samples are linearly interpolated to preserve uniform sampling.",
             "Full selected traces are passed to scipy.signal.welch after optional spike replacement.",
             "Closure = USB + LSB - 2 Carrier: ideal common carrier and opposite modulation terms both cancel.",
             "Residual spectra include source noise, readout noise and differential path effects.",
             "Derived phase ASD (cycles/sqrt(Hz)) = frequency ASD / (2*pi*Fourier frequency).",
             "Multiply derived phase ASD by 2*pi for rad/sqrt(Hz); DC is excluded.", ""]
    for name, (robust_sigma, _) in spike_diagnostics.items():
        lines.append(f"Local residual robust sigma, {name}: {robust_sigma:.9g} Hz")
    lines.append("")
    for name, x in signals.items():
        residual = x - np.median(x)
        lines.append(f"{name}: median={np.median(x):.12g} Hz; std={np.std(x):.8g} Hz; residual 1/50/99 percentiles={np.quantile(residual,[.01,.5,.99])} Hz; max absolute residual={np.max(abs(residual)):.8g} Hz")
    lines.append("\nMedian ASD in bands (Hz/sqrt(Hz)); these are band summaries, not integrated RMS:")
    for lo, hi in ((5e-5, 1e-3), (1e-3, .01), (.01, .1), (.1, 1), (1, 10)):
        pick = (f >= lo) & (f < hi)
        if np.any(pick):
            for name in list(signals)[3:]:
                lines.append(f"{lo:g}-{hi:g} Hz, {name}: all={np.median(full[name][pick]):.6g}")
    Path(f"{prefix}_frequency_summary.txt").write_text("\n".join(lines)+"\n", encoding="utf-8")
    np.savetxt(f"{prefix}_frequency_transients.csv",
               np.column_stack((t[bad],
                                (uc_raw-np.median(uc_raw))[bad],
                                (cl_raw-np.median(cl_raw))[bad],
                                (modulation_raw-np.median(modulation_raw))[bad])),
               delimiter=",",
               header="time_s,USB_minus_carrier_residual_Hz,carrier_minus_LSB_residual_Hz,half_USB_minus_LSB_residual_Hz",
               comments="")
    np.savez(f"{prefix}_frequency_asd.npz", frequency_Hz=f,
             **{f"all_{name}": x for name, x in full.items()})
    np.savez(f"{prefix}_phase_asd_from_frequency.npz", frequency_Hz=f,
             phase_unit="cycles/sqrt(Hz)",
             **{f"all_{name}": x for name, x in phase.items()})
    print("\n".join(lines))
    print(f"Saved frequency and derived phase ASDs (PNG/NPZ), summary and transient list beside {data.name}")


if __name__ == "__main__":
    main()
