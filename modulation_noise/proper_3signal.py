"""Frequency-only, three-signal ASD analysis; no phase data are used."""
from pathlib import Path
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend, windows


def amplitude_spectra(x, fs, starts, size):
    """One-sided amplitude density per Hann-windowed, linearly detrended segment.

    RMS-average these amplitudes for a Welch-equivalent ASD. No PSD arrays
    or PSD products are calculated. DC is excluded from all output.
    """
    window = windows.hann(size, sym=False)
    scale = np.full(size // 2 + 1, np.sqrt(2 / (fs * np.dot(window, window))))
    scale[0] /= np.sqrt(2)
    if size % 2 == 0:
        scale[-1] /= np.sqrt(2)
    return np.array([np.abs(np.fft.rfft(detrend(x[s:s + size], type="linear") * window)) * scale
                     for s in starts])


def rms_amplitude(amplitudes):
    # Vector norm gives the RMS of segment amplitude densities directly.
    return np.linalg.norm(amplitudes, axis=0) / np.sqrt(len(amplitudes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", nargs="?", type=Path,
                        default=Path(__file__).resolve().parent / "data" / "mod_nois_20260930_124152.npy")
    parser.add_argument("--channels", nargs=3, type=int, metavar=("CARRIER", "LSB", "USB"))
    parser.add_argument("--cut-start", type=float, default=0)
    parser.add_argument("--cut-end", type=float, default=0, help="Seconds discarded at end (default: 0, full recording)")
    parser.add_argument("--segment-seconds", type=float, default=256)
    parser.add_argument("--fmin", type=float, default=0.01)
    parser.add_argument("--transient-threshold", type=float, default=5,
                        help="Hz from median in either sideband-carrier difference; diagnostic only")
    args = parser.parse_args()
    if min(args.cut_start, args.cut_end) < 0 or min(args.segment_seconds, args.fmin, args.transient_threshold) <= 0:
        parser.error("Cuts must be nonnegative; segment length, fmin and threshold must be positive")
    data = args.data.resolve()
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
    size = int(round(args.segment_seconds * fs))
    if size < 8 or len(t) < 2 * size:
        raise ValueError("Need at least two full segments; reduce --segment-seconds or cuts")
    starts = np.arange(0, len(t) - size + 1, size // 2)
    frequency = np.fft.rfftfreq(size, 1 / fs)
    band = frequency >= max(args.fmin, 2 * fs / size)
    if not np.any(band):
        raise ValueError("fmin exceeds the available frequency range")
    uc, cl = u - c, c - l
    signals = {"Carrier": c, "LSB": l, "USB": u,
               "USB - Carrier": uc, "Carrier - LSB": cl,
               "(USB - LSB) / 2": (u - l) / 2,
               "USB + LSB - 2 Carrier": uc - cl}
    bad = (np.abs(uc - np.median(uc)) > args.transient_threshold) | (np.abs(cl - np.median(cl)) > args.transient_threshold)
    quiet = np.array([not np.any(bad[s:s + size]) for s in starts])
    spectra = {name: amplitude_spectra(x - np.median(x), fs, starts, size)[:, band]
               for name, x in signals.items()}
    full = {name: rms_amplitude(x) for name, x in spectra.items()}
    clean = {name: rms_amplitude(x[quiet]) for name, x in spectra.items()} if np.any(quiet) else {}
    f = frequency[band]
    prefix = data.with_suffix("")
    colors = {"Carrier": "black", "LSB": "#295f24", "USB": "#821770",
              "USB - Carrier": "#821770", "Carrier - LSB": "#295f24",
              "(USB - LSB) / 2": "tab:blue", "USB + LSB - 2 Carrier": "tab:orange"}

    # Show every sample so narrow transients are not lost by downsampling.
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
                ax.plot(hours, residual, color=colors[name], linewidth=.4, rasterized=True)
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
        for ext in ("png", "pdf"):
            fig.savefig(f"{prefix}_freq_differences_timeseries.{ext}", dpi=200)
        plt.close(fig)

    def plot(values, names, suffix, title):
        fig, ax = plt.subplots(figsize=(9, 5))
        for name in names:
            ax.loglog(f, values[name], label=name, color=colors[name], linewidth=1)
        ax.set(xlabel="Fourier frequency (Hz)", ylabel=r"Frequency ASD (Hz/$\sqrt{Hz}$)",
               title=title, xlim=(f[0], f[-1]))
        ax.grid(True, which="both", alpha=.25)
        ax.legend(fontsize=9)
        fig.tight_layout()
        for ext in ("png", "pdf"):
            fig.savefig(f"{prefix}_{suffix}.{ext}", dpi=200)
        plt.close(fig)

    plot(full, list(signals)[:3] + ["(USB - LSB) / 2"], "asd_freq", "All segments: measured frequency noise")
    plot(full, list(signals)[3:], "asd_freq_differences", "All segments: modulation estimates and closure residual")
    if clean:
        fig, ax = plt.subplots(figsize=(9, 5))
        for name in list(signals)[3:]:
            ax.loglog(f, full[name], color=colors[name], alpha=.25, linewidth=.7)
            ax.loglog(f, clean[name], label=name, color=colors[name], linewidth=1)
        ax.set(xlabel="Fourier frequency (Hz)", ylabel=r"Frequency ASD (Hz/$\sqrt{Hz}$)",
               title=f"Transient diagnostic: {quiet.sum()}/{len(starts)} segments retained (faint: all)", xlim=(f[0], f[-1]))
        ax.grid(True, which="both", alpha=.25)
        ax.legend(fontsize=9)
        fig.tight_layout()
        for ext in ("png", "pdf"):
            fig.savefig(f"{prefix}_asd_freq_transient_comparison.{ext}", dpi=200)
        plt.close(fig)
    lines = [f"Source: {data.name}", f"Channels: carrier={carrier}, LSB={lower}, USB={upper}",
             f"fs={fs:.12g} Hz; samples={len(t)}; duration={t[-1]-t[0]:.6f} s",
             f"Cuts: start={args.cut_start:g} s, end={args.cut_end:g} s",
             f"Hann segments: {size/fs:.6f} s; 50% overlap; linear detrend per segment",
             f"Frequency spacing: {fs/size:.8g} Hz; plotted minimum: {f[0]:.8g} Hz",
             f"Segments: {len(starts)} total, {quiet.sum()} without detected transients (overlapping, not independent)",
             f"Transient rule: either sideband-carrier difference > {args.transient_threshold:g} Hz from its median",
             f"Flagged samples: {bad.sum()} ({100*bad.mean():.6f}%)",
             "Full-data spectra retain every segment; diagnostic rejects whole affected segments, without interpolation.",
             "Selected quiet segments are conditional diagnostics, not an unbiased full-record noise estimate.",
             "Closure = USB + LSB - 2 Carrier: ideal common carrier and opposite modulation terms both cancel.",
             "Residual spectra include source noise, readout noise and differential path effects.", ""]
    for name, x in signals.items():
        residual = x - np.median(x)
        lines.append(f"{name}: median={np.median(x):.12g} Hz; std={np.std(x):.8g} Hz; residual 1/50/99 percentiles={np.quantile(residual,[.01,.5,.99])} Hz; max absolute residual={np.max(abs(residual)):.8g} Hz")
    lines.append("\nMedian ASD in bands (Hz/sqrt(Hz)); these are band summaries, not integrated RMS:")
    for lo, hi in ((.01,.1),(.1,1),(1,10)):
        pick = (f >= lo) & (f < hi)
        if np.any(pick):
            for name in list(signals)[3:]:
                lines.append(f"{lo:g}-{hi:g} Hz, {name}: all={np.median(full[name][pick]):.6g}" +
                             (f", quiet={np.median(clean[name][pick]):.6g}" if clean else ""))
    Path(f"{prefix}_frequency_summary.txt").write_text("\n".join(lines)+"\n", encoding="utf-8")
    np.savetxt(f"{prefix}_frequency_transients.csv", np.column_stack((t[bad], (uc-np.median(uc))[bad], (cl-np.median(cl))[bad])),
               delimiter=",", header="time_s,USB_minus_carrier_residual_Hz,carrier_minus_LSB_residual_Hz", comments="")
    np.savez(f"{prefix}_frequency_asd.npz", frequency_Hz=f,
             **{f"all_{name}": x for name, x in full.items()}, **{f"quiet_{name}": x for name, x in clean.items()})
    print("\n".join(lines))
    print(f"Saved frequency ASD plots, arrays, summary and transient list beside {data.name}")


if __name__ == "__main__":
    main()
