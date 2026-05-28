import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from lisaorbits import KeplerianOrbits
from lisainstrument import Instrument


def welch_psd(x, fs, nperseg=1024, overlap=0.5):
    """Simple Welch PSD estimate for a 1D real-valued series."""
    x = np.asarray(x)
    if x.ndim != 1:
        raise ValueError("welch_psd expects a 1D array")

    nperseg = min(int(nperseg), len(x))
    if nperseg < 8:
        raise ValueError("nperseg too small")

    noverlap = int(overlap * nperseg)
    if noverlap >= nperseg:
        raise ValueError("overlap must be smaller than 1")

    step = nperseg - noverlap
    starts = np.arange(0, len(x) - nperseg + 1, step)
    if len(starts) == 0:
        starts = np.array([0])
        nperseg = len(x)

    window = np.hanning(nperseg)
    win_norm = fs * np.sum(window**2)

    psd_accum = None
    for start in starts:
        seg = x[start:start + nperseg]
        seg = seg - np.mean(seg)
        X = np.fft.rfft(seg * window)
        Pxx = (np.abs(X) ** 2) / win_norm
        if nperseg % 2 == 0:
            Pxx[1:-1] *= 2.0
        else:
            Pxx[1:] *= 2.0

        if psd_accum is None:
            psd_accum = Pxx
        else:
            psd_accum += Pxx

    psd = psd_accum / len(starts)
    freqs = np.fft.rfftfreq(nperseg, d=1.0 / fs)
    return freqs, psd


def plot_science_psds(t, sci_array, links, outfile):
    dt = t[1] - t[0]
    fs = 1.0 / dt

    plt.figure(figsize=(8, 5))
    for i, link in enumerate(links):
        f, psd = welch_psd(sci_array[i], fs=fs, nperseg=min(1024, len(t)))
        positive = f > 0.0
        plt.loglog(f[positive], psd[positive], label=f"link {link}")

    plt.xlabel("Frequency [Hz]")
    plt.ylabel(r"PSD [Hz$^2$/Hz]")
    plt.title("Science-carrier laser-noise PSDs")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend(ncol=2)
    plt.tight_layout()
    plt.savefig(outfile, dpi=200)
    plt.close()


def main():
    # ----------------------------
    # User settings
    # ----------------------------
    outdir = Path("/mnt/data/lisainstrument_demo")
    outdir.mkdir(parents=True, exist_ok=True)

    orbit_file = outdir / "keplerian_orbits.h5"
    npz_file = outdir / "laser_only_streams.npz"
    psd_plot_file = outdir / "laser_only_science_psd.png"

    # Measurement stream settings
    dt = 1.0               # science-output sample spacing [s]
    size = 4096            # number of samples
    t0 = 0.0               # start time in TCB seconds relative to LISA epoch
    seed = 12345           # reproducible random seed

    # Orbit file settings
    # We use a dynamic Keplerian constellation so the delays vary in time.
    orbit_t0 = -3.0 * 86400.0   # start orbit file 3 days earlier than t0
    orbit_dt = 300.0            # orbit sampling [s]
    orbit_size = 3000           # ~10.4 days of orbit data

    # ----------------------------
    # 1) Make a time-varying-delay orbit file
    # ----------------------------
    if orbit_file.exists():
        orbit_file.unlink()

    orbits = KeplerianOrbits(L=2.5e9)
    orbits.write(str(orbit_file), t0=orbit_t0, dt=orbit_dt, size=orbit_size, mode="w")

    # ----------------------------
    # 2) Build a laser-noise-only instrument model
    # ----------------------------
    instrument = Instrument(
        size=size,
        dt=dt,
        t0=t0,
        seed=seed,
        aafilter=None,          # simplest for this first playground script
        orbits=str(orbit_file),
        orbit_dataset="tcb/ltt",   # this worked robustly here for dynamic delays
    )

    # Keep only laser noise. Turn off deterministic Doppler terms too,
    # so the output is just laser noise propagated through time-varying delays.
    instrument.disable_all_noises(excluding="laser")
    instrument.disable_dopplers()

    # keep_all=True gives access to the time-varying link delays (pprs)
    results = instrument.export_numpy(keep_all=True)

    # ----------------------------
    # 3) Pull out the useful streams
    # ----------------------------
    t = results.t

    # One-way science interferometer outputs for each link
    sci = results.mosa_data.sci_carrier_fluctuations

    # Proper pseudo-ranges [s] for each link, evaluated on the physics grid
    pprs = results.mosa_data.pprs

    # Convert to plain arrays stacked in a fixed link order
    links = ["12", "13", "21", "23", "31", "32"]
    sci_array = np.vstack([sci[link] for link in links])
    ppr_array = np.vstack([pprs[link] for link in links])

    # Physics time grid for the pprs
    physics_dt = instrument.physics_dt
    t_ppr = instrument.t0 + np.arange(ppr_array.shape[1]) * physics_dt

    # ----------------------------
    # 4) Save a compact file for later analysis
    # ----------------------------
    np.savez(
        npz_file,
        t=t,
        t_ppr=t_ppr,
        links=np.array(links),
        sci_carrier_fluctuations_hz=sci_array,
        pprs_s=ppr_array,
    )

    # ----------------------------
    # 5) Plot PSDs of the science-carrier streams
    # ----------------------------
    plot_science_psds(t, sci_array, links, psd_plot_file)

    # -----------------------------
    # Plot time series
    # -----------------------------
    plt.figure(figsize=(10, 5))

    for i, link in enumerate(links):
        plt.plot(t, sci[i], label=link, alpha=0.7)

    plt.xlabel("Time [s]")
    plt.ylabel("Frequency fluctuations [Hz]")
    plt.title("Laser-noise-only science carrier time series")
    plt.legend(ncol=3)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    print(f"Saved orbit file: {orbit_file}")
    print(f"Saved data file : {npz_file}")
    print(f"Saved PSD plot  : {psd_plot_file}")
    print()
    print("Stored arrays:")
    print(f"  t                           shape = {t.shape}")
    print(f"  t_ppr                       shape = {t_ppr.shape}")
    print(f"  sci_carrier_fluctuations_hz shape = {sci_array.shape}")
    print(f"  pprs_s                      shape = {ppr_array.shape}")
    print()
    print("Link order:", links)
    print("Example: mean PPR for link 12 [s] =", np.mean(pprs["12"]))
    print("Example: std  PPR for link 12 [s] =", np.std(pprs["12"]))
    print("Example: std of science stream 12 [Hz] =", np.std(sci["12"]))


if __name__ == "__main__":
    main()
