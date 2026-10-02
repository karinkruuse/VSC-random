"""Synchronize two equal-rate phasemeter recordings using their common input B."""
from pathlib import Path
import json
import numpy as np
from scipy.signal import correlate, correlation_lags
from scipy.interpolate import CubicSpline
from scipy.optimize import minimize_scalar


def estimate_offset(x, y, max_lag):
    """Return lag in samples: y[j] corresponds to x[j + lag]."""
    x = x - np.mean(x)
    y = y - np.mean(y)
    if min(np.std(x), np.std(y)) == 0:
        raise ValueError("Input B has no variation to determine synchronization")
    lags = correlation_lags(len(x), len(y))
    correlation = correlate(x, y, method="fft")
    valid = np.abs(lags) <= max_lag
    lag = int(lags[valid][np.argmax(correlation[valid])])
    if abs(lag) == max_lag:
        raise ValueError("Synchronization peak is at the search boundary")
    idx = np.arange(max(0, lag + 2), min(len(x), len(y) + lag - 2))
    spline = CubicSpline(np.arange(len(y)), y, extrapolate=False)

    def fit(indices):
        result = minimize_scalar(lambda shift: np.var(x[indices] - spline(indices - shift)),
                                 bounds=(lag - .5, lag + .5), method="bounded")
        return float(result.x)

    shift = fit(idx)
    aligned = spline(idx - shift)
    quality = float(np.corrcoef(x[idx], aligned)[0, 1])
    if quality < .8:
        raise ValueError(f"Ambiguous input B alignment (correlation={quality:.3f})")
    return shift, quality, [fit(block) for block in np.array_split(idx, 3)]


def synchronize(first, second):
    first, second = Path(first).resolve(), Path(second).resolve()
    a, b = [np.load(p, allow_pickle=False) for p in (first, second)]
    dt = np.median(np.diff(a['Time (s)']))
    for data in (a, b):
        if not np.allclose(np.diff(data['Time (s)']), dt, rtol=1e-6, atol=1e-9):
            raise ValueError("Synchronization requires equal, uniform sampling rates")
        for field in ('Input A Frequency (Hz)', 'Input B Frequency (Hz)'):
            if not np.all(np.isfinite(data[field])):
                raise ValueError(f"Non-finite samples in {field}")
    # B is the common USB; the lower A beat is LSB and the other A is carrier.
    if abs(np.median(a['Input A Frequency (Hz)']) - np.median(b['Input A Frequency (Hz)'])) < 1e3:
        raise ValueError('Cannot distinguish carrier and LSB from input A frequencies')
    if np.median(a['Input A Frequency (Hz)']) > np.median(b['Input A Frequency (Hz)']):
        return synchronize(second, first)
    x, y = a['Input B Frequency (Hz)'], b['Input B Frequency (Hz)']
    if abs(np.median(x) - np.median(y)) > 1e3:
        raise ValueError("Input B frequencies do not identify the same reference signal")
    max_lag = min(int(round(10 / dt)), min(len(a), len(b)) // 4)
    lag, quality, block_lags = estimate_offset(x, y, max_lag)
    indices = np.arange(len(a))
    keep = (indices - lag >= 0) & (indices - lag <= len(b) - 1)
    indices = indices[keep]
    if len(indices) < 256:
        raise ValueError("Insufficient overlap after synchronization")
    mapped = indices - lag
    quantities = ['Frequency (Hz)', 'Phase (cyc)', 'Set Frequency (Hz)', 'I (V)', 'Q (V)']
    quantities = [q for q in quantities if all(f'Input {ch} {q}' in data.dtype.names
                  for data in (a, b) for ch in ('A', 'B'))]
    dtype = [('Time (s)', 'f8')] + [(f'Input {ch} {q}', 'f8') for ch in (1, 2, 3) for q in quantities]
    merged = np.empty(len(indices), dtype=dtype)
    merged['Time (s)'] = (indices - indices[0]) * dt
    for q in quantities:
        values = b[f'Input A {q}']
        if not np.all(np.isfinite(values)):
            raise ValueError(f"Non-finite carrier {q}")
        # Centre before interpolation to retain precision for MHz beat frequencies.
        offset = np.median(values)
        merged[f'Input 1 {q}'] = CubicSpline(np.arange(len(b)), values-offset)(mapped) + offset
        merged[f'Input 2 {q}'] = a[f'Input A {q}'][indices]
        merged[f'Input 3 {q}'] = a[f'Input B {q}'][indices]
    centered_y = y - np.median(y)
    residual = (x[indices] - np.median(y)) - CubicSpline(np.arange(len(b)), centered_y)(mapped)
    report = {
        'reference_file': str(first), 'shifted_file': str(second),
        'offset_definition': 'shifted file sample j occurs at reference sample j + offset_samples',
        'offset_samples': lag, 'offset_seconds': lag * dt,
        'thirds_offset_seconds': [v*dt for v in block_lags],
        'aligned_B_correlation': quality, 'aligned_B_difference_std_Hz': float(np.std(residual)),
        'sample_rate_Hz': 1/dt, 'overlap_samples': len(indices),
        'overlap_duration_seconds': float(merged['Time (s)'][-1]),
        'channel_mapping': {'1': 'shifted file A: carrier', '2': 'reference file A: LSB', '3': 'reference file B: USB'},
        'method': 'constant offset from B frequency correlation and cubic interpolation refinement; no clock-drift correction',
        'interpolation': 'carrier only; cubic interpolation can change noise near Nyquist; both sidebands remain unresampled',
    }
    output = first.with_name(first.stem + '_synced.npy')
    np.save(output, merged)
    output.with_suffix('.txt').write_text(f"# Acquisition rate: {1/dt:.12g} Hz\n# Carrier, LSB, USB; see synchronization JSON for provenance.\n", encoding='utf-8')
    output.with_name(output.stem + '_synchronization.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return output
