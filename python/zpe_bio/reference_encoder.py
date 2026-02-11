"""
encoder.py
==============

This module implements a simple encoder/decoder for one‑dimensional biosignals,
such as ECG or PPG waveforms, using an 8‑directional stroke alphabet.  The
encoder transforms the continuous signal into a sequence of discrete tokens
representing directional changes between consecutive samples.  A basic run
length encoding (RLE) compressor is included to reduce the size of the token
stream.  While the algorithm implemented here is intentionally simple, it
demonstrates the core ideas behind the 8 primitives described in the research
artefact: invertible directional encoding, compact representation and
deterministic decoding.  Production‑grade implementations should integrate
error handling, adaptive quantisation and entropy coding.

Usage Example
-------------

```
import numpy as np
from encoder import encode_signal, decode_signal

# Simulate a short ECG waveform (sine wave + noise)
t = np.linspace(0, 2*np.pi, num=100)
ecg = np.sin(t) + 0.05*np.random.randn(len(t))

# Encode and compress
tokens = encode_signal(ecg, threshold=0.02)

# Decode to approximate the original waveform
reconstructed = decode_signal(tokens)
```

Functions
---------
encode_signal(signal: Sequence[float], threshold: float) -> List[Tuple[int,int]]
    Convert a sequence of samples into a list of (direction, length) tokens.  The
    direction is an integer in [0..7] corresponding to the 8 compass points.

compress_tokens(tokens: List[int]) -> List[Tuple[int,int]]
    Apply run‑length encoding to a list of direction codes.  Each output tuple
    contains (direction, count).

decompress_tokens(rle: List[Tuple[int,int]]) -> List[int]
    Expand a run‑length encoded token stream back into a list of direction codes.

decode_signal(rle: List[Tuple[int,int]], start_value: float = 0.0,
              step: float = 0.005) -> List[float]
    Reconstruct an approximate signal from a run‑length encoded token stream.
    The `step` parameter controls the amplitude change per directional step.
"""

from typing import List, Tuple, Sequence
import numpy as np

# Mapping from direction index to unit vector (dx, dy) in 2D.  For a 1D
# waveform (time vs amplitude) the x component is fixed (time always
# increases by one unit), so we only use the y component to update the
# reconstructed amplitude.  Directions follow the conventional Freeman chain
# code ordering: 0=E,1=NE,2=N,3=NW,4=W,5=SW,6=S,7=SE.
_DIRECTION_VECTORS = {
    0: (1, 0),   # East: no change in amplitude
    1: (1, 1),   # North‑East: moderate increase
    2: (0, 1),   # North: strong increase
    3: (-1, 1),  # North‑West: unused in 1D but reserved
    4: (-1, 0),  # West: unused in 1D but reserved
    5: (-1, -1), # South‑West: unused in 1D but reserved
    6: (0, -1),  # South: strong decrease
    7: (1, -1),  # South‑East: moderate decrease
}

def _quantise_difference(dy: float, threshold: float) -> int:
    """Map a sample difference to one of the 8 directional indices.

    The input `dy` represents the change in amplitude between two samples.  The
    threshold controls sensitivity: values with absolute magnitude below the
    threshold are treated as flat (direction 0/East).  Positive values above
    threshold map to direction 2 (North) or 1 (North‑East) depending on
    magnitude; negative values below ‑threshold map to direction 6 (South) or 7
    (South‑East).  The unused diagonal directions (3,4,5) remain reserved.
    """
    if dy > threshold * 2:
        # steep increase
        return 2
    elif dy > threshold:
        # gentle increase
        return 1
    elif dy < -2 * threshold:
        # steep decrease
        return 6
    elif dy < -threshold:
        # gentle decrease
        return 7
    else:
        # flat / no significant change
        return 0

def encode_signal(signal: Sequence[float], threshold: float = 0.01) -> List[Tuple[int,int]]:
    """Encode a waveform into an RLE‑compressed sequence of directional tokens.

    Parameters
    ----------
    signal : Sequence[float]
        Input one‑dimensional waveform samples (e.g. ECG, PPG).
    threshold : float
        Sensitivity threshold for quantising amplitude changes.  Smaller values
        produce more directional changes; larger values increase sparsity.

    Returns
    -------
    List[Tuple[int,int]]
        A list of (direction, run‑length) tuples encoding the signal.
    """
    if len(signal) < 2:
        return []
    directions: List[int] = []
    prev = signal[0]
    for sample in signal[1:]:
        dy = sample - prev
        directions.append(_quantise_difference(dy, threshold))
        prev = sample
    return compress_tokens(directions)

def compress_tokens(tokens: List[int]) -> List[Tuple[int,int]]:
    """Simple run‑length encoding for a list of direction codes."""
    if not tokens:
        return []
    rle: List[Tuple[int,int]] = []
    current_dir = tokens[0]
    count = 1
    for direction in tokens[1:]:
        if direction == current_dir:
            count += 1
        else:
            rle.append((current_dir, count))
            current_dir = direction
            count = 1
    rle.append((current_dir, count))
    return rle

def decompress_tokens(rle: List[Tuple[int,int]]) -> List[int]:
    """Expand a run‑length encoded token stream back into individual codes."""
    tokens: List[int] = []
    for direction, count in rle:
        tokens.extend([direction] * count)
    return tokens

def decode_signal(rle: List[Tuple[int,int]], start_value: float = 0.0,
                  step: float = 0.01) -> List[float]:
    """Reconstruct an approximate waveform from RLE‑encoded directional tokens.

    Parameters
    ----------
    rle : List[Tuple[int,int]]
        Run‑length encoded directional tokens produced by `encode_signal`.
    start_value : float
        Initial amplitude value for reconstruction.  This should match the
        starting point of the original signal for accurate recovery.
    step : float
        Increment in amplitude per directional step.  Increasing `step`
        exaggerates changes; decreasing it smooths the reconstructed waveform.

    Returns
    -------
    List[float]
        Approximate reconstructed waveform samples.
    """
    amplitude = start_value
    reconstructed: List[float] = [amplitude]
    tokens = decompress_tokens(rle)
    for direction in tokens:
        # Only use the vertical component for amplitude update
        dy = _DIRECTION_VECTORS[direction][1] * step
        amplitude += dy
        reconstructed.append(amplitude)
    return reconstructed

if __name__ == "__main__":
    import argparse
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser(description="Encode and decode a biosignal using 8‑direction chain coding.")
    parser.add_argument("--length", type=int, default=1000,
                        help="Number of samples to simulate in the test signal")
    parser.add_argument("--threshold", type=float, default=0.05,
                        help="Quantisation threshold for directional encoding")
    args = parser.parse_args()

    # Generate a synthetic ECG‑like waveform (sine wave + noise + baseline wander)
    t = np.linspace(0, 4 * np.pi, num=args.length)
    signal = 0.6 * np.sin(t) + 0.2 * np.sin(3 * t) + 0.05 * np.random.randn(len(t))

    rle_tokens = encode_signal(signal, threshold=args.threshold)
    reconstructed = decode_signal(rle_tokens, start_value=signal[0], step=args.threshold)

    print(f"Original samples: {len(signal)}")
    print(f"Number of RLE tokens: {len(rle_tokens)}")

    # Plot original and reconstructed signals for visual inspection
    plt.figure(figsize=(10, 4))
    plt.plot(signal, label="Original")
    plt.plot(reconstructed, label="Reconstructed", linestyle="--")
    plt.legend()
    plt.title("8‑directional encoding and reconstruction")
    plt.xlabel("Sample index")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.show()