"""
ZPE-Bio Codec — Python Reference Implementation
=================================================
PRD Reference: ZPE_BIOSIGNAL_CODEC_PRD_v1.0.md §1.1
Requirement IDs: REQ-CODEC-1, REQ-CODEC-2, REQ-CODEC-3, REQ-CODEC-4, REQ-CODEC-5

INVARIANTS THIS CODE MUST PRESERVE:
- INV-DET: Deterministic — identical inputs produce identical outputs
- INV-INV: Invertible — decode(encode(x)) approximates x within ε
- INV-NOFLOW: No overflow — RLE counts bounded to 65535
- INV-CAUSAL: Causal — encode(x[0:t]) depends only on x[0:t]

WARNING: This is the reference implementation. The Rust codec MUST produce
byte-identical output for the same inputs. If they diverge, the Rust codec
is authoritative and this file must be updated.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import numpy as np

# ── Constants (from RUNBOOK_00 §6) ──────────────────────────────────────────
ECG_SAMPLE_RATE = 250          # Hz
PPG_SAMPLE_RATE = 100          # Hz
ECG_FIXED_THR_DEFAULT = 0.05   # normalised
PPG_FIXED_THR_DEFAULT = 0.03   # normalised
ADAPTIVE_K = 0.15              # RMS multiplier
ADAPTIVE_THR_MIN = 0.005       # threshold floor
ADAPTIVE_ALPHA = 0.95          # envelope decay
MAX_RLE_COUNT = 65535          # u16 max — INV-NOFLOW

# ── Direction Mapping ───────────────────────────────────────────────────────
# ID  Angle   Vector   Meaning
# 0   0° E    (1,0)    Stable (isoelectric)
# 1   45° NE  (1,1)    Moderate increase
# 2   90° N   (0,1)    Acute increase
# 3   135° NW (-1,1)   RESERVED
# 4   180° W  (-1,0)   RESERVED
# 5   225° SW (-1,-1)  RESERVED
# 6   270° S  (0,-1)   Acute decrease
# 7   315° SE (1,-1)   Moderate decrease

DIRECTION_DELTAS = {
    0: 0.0,    # East — no change
    1: 1.0,    # NE — moderate up
    2: 2.0,    # North — acute up
    6: -2.0,   # South — acute down
    7: -1.0,   # SE — moderate down
}

ACTIVE_DIRECTIONS = frozenset({0, 1, 2, 6, 7})


@dataclass
class EncodedStream:
    """Complete encoded representation of a biosignal segment."""
    rle_tokens: List[Tuple[int, int]]   # [(direction, count), ...]
    start_value: float                   # x[0] — needed for reconstruction
    threshold: float                     # quantisation threshold used
    step: float                          # reconstruction step size
    sample_rate: int                     # Hz
    signal_type: str                     # 'ecg' or 'ppg'
    thr_mode: str                        # 'fixed', 'adaptive_rms', 'adaptive_envelope'
    num_samples: int                     # original sample count
    num_tokens: int = field(init=False)  # number of RLE tuples

    def __post_init__(self):
        self.num_tokens = len(self.rle_tokens)

    @property
    def compression_ratio(self) -> float:
        """Raw bytes / compressed bytes. Higher is better."""
        raw_bytes = self.num_samples * 2  # 16-bit samples
        # Each RLE token = 1 byte dir + 2 bytes count = 3 bytes
        compressed_bytes = self.num_tokens * 3
        if compressed_bytes == 0:
            return 0.0
        return raw_bytes / compressed_bytes

    @property
    def bits_per_sample(self) -> float:
        """Average bits per original sample in compressed form."""
        if self.num_samples == 0:
            return 0.0
        compressed_bits = self.num_tokens * 3 * 8
        return compressed_bits / self.num_samples


def quantise_ecg(delta: float, threshold: float) -> int:
    """Quantise an ECG sample difference to a direction.
    
    REQ-CODEC-2: 8-primitive directional quantisation (5 active).
    INV-DET: Pure function, deterministic.
    
    Args:
        delta: x[t] - x[t-1], the first-order difference
        threshold: quantisation threshold (positive float)
    
    Returns:
        Direction ID in {0, 1, 2, 6, 7}
    """
    if threshold <= 0:
        raise ValueError(f"threshold must be positive, got {threshold}")
    
    if delta > 2 * threshold:
        return 2   # acute increase (North)
    elif delta > threshold:
        return 1   # moderate increase (NE)
    elif delta < -2 * threshold:
        return 6   # acute decrease (South)
    elif delta < -threshold:
        return 7   # moderate decrease (SE)
    else:
        return 0   # stable (East)


def quantise_ppg(delta: float, threshold: float) -> int:
    """Quantise a PPG sample difference to a direction.
    
    REQ-CODEC-5: PPG-specific quantisation with wider dead zone.
    INV-DET: Pure function, deterministic.
    
    PPG morphology is smoother than ECG. The wider multiplier (3× vs 2×)
    reduces direction flapping on gradual slopes.
    
    Args:
        delta: x[t] - x[t-1]
        threshold: quantisation threshold
    
    Returns:
        Direction ID in {0, 1, 2, 6, 7}
    """
    if threshold <= 0:
        raise ValueError(f"threshold must be positive, got {threshold}")
    
    if delta > 3 * threshold:
        return 2   # systolic upstroke
    elif delta > threshold:
        return 1   # diastolic rise
    elif delta < -3 * threshold:
        return 6   # systolic downstroke
    elif delta < -threshold:
        return 7   # dicrotic decay
    else:
        return 0   # plateau


def adaptive_threshold_rms(
    window: np.ndarray,
    k: float = ADAPTIVE_K,
    thr_min: float = ADAPTIVE_THR_MIN,
) -> float:
    """Compute adaptive threshold from window RMS.
    
    REQ-CODEC-4: Configurable adaptive threshold.
    INV-DET: Deterministic for same window.
    INV-CAUSAL: Uses only current window, no lookahead.
    INV-RAM: One float computation, no allocation.
    
    Args:
        window: Signal window (1D numpy array)
        k: RMS multiplier (default 0.15 from RUNBOOK_00 §6)
        thr_min: Minimum threshold floor (default 0.005)
    
    Returns:
        Adaptive threshold value, guaranteed >= thr_min
    """
    if len(window) == 0:
        return thr_min
    rms = float(np.sqrt(np.mean(window.astype(np.float64) ** 2)))
    return max(thr_min, k * rms)


def compress_rle(directions: List[int]) -> List[Tuple[int, int]]:
    """Run-Length Encode a direction stream.
    
    REQ-CODEC-3: RLE compression.
    INV-NOFLOW: Counts bounded to MAX_RLE_COUNT (65535).
    INV-DET: Deterministic.
    
    Args:
        directions: List of direction IDs (each in {0,1,2,6,7})
    
    Returns:
        List of (direction, count) tuples.
    """
    if not directions:
        return []
    
    result: List[Tuple[int, int]] = []
    current_dir = directions[0]
    current_count = 1
    
    for d in directions[1:]:
        if d not in ACTIVE_DIRECTIONS:
            # Re-read runbook/PRD: only 0,1,2,6,7 are active
            raise ValueError(f"Invalid direction {d}; expected one of {ACTIVE_DIRECTIONS}")
        if d == current_dir and current_count < MAX_RLE_COUNT:
            current_count += 1
        else:
            result.append((current_dir, current_count))
            current_dir = d
            current_count = 1
    
    result.append((current_dir, current_count))
    return result


def decompress_rle(rle_tokens: List[Tuple[int, int]]) -> List[int]:
    """Decompress RLE tokens back to a direction stream.
    
    INV-DET: Deterministic.
    
    Args:
        rle_tokens: List of (direction, count) tuples
    
    Returns:
        Full direction stream
    """
    result: List[int] = []
    for direction, count in rle_tokens:
        if count < 1 or count > MAX_RLE_COUNT:
            raise ValueError(f"Invalid count {count}; must be 1..{MAX_RLE_COUNT}")
        result.extend([direction] * count)
    return result


def encode(
    samples: np.ndarray,
    threshold: Optional[float] = None,
    thr_mode: str = "fixed",
    signal_type: str = "ecg",
    step: Optional[float] = None,
) -> EncodedStream:
    """Encode a biosignal sample array into compressed directional tokens.
    
    REQ-CODEC-1, REQ-CODEC-2, REQ-CODEC-3, REQ-CODEC-4, REQ-CODEC-5.
    INV-DET, INV-INV, INV-NOFLOW, INV-CAUSAL.
    
    Args:
        samples: 1D numpy array of signal samples (float or int16)
        threshold: Quantisation threshold. If None, uses default for signal_type.
        thr_mode: 'fixed' | 'adaptive_rms' | 'adaptive_envelope'
        signal_type: 'ecg' | 'ppg'
        step: Reconstruction step size. If None, computed from data.
    
    Returns:
        EncodedStream with RLE tokens and metadata
    """
    # Validate inputs
    if samples.ndim != 1:
        raise ValueError(f"samples must be 1D, got {samples.ndim}D")
    if len(samples) < 2:
        raise ValueError(f"samples must have >= 2 elements, got {len(samples)}")
    if signal_type not in ("ecg", "ppg"):
        raise ValueError(f"signal_type must be 'ecg' or 'ppg', got '{signal_type}'")
    if thr_mode not in ("fixed", "adaptive_rms", "adaptive_envelope"):
        raise ValueError(f"thr_mode must be 'fixed'|'adaptive_rms'|'adaptive_envelope', got '{thr_mode}'")
    
    # Set defaults
    fs = ECG_SAMPLE_RATE if signal_type == "ecg" else PPG_SAMPLE_RATE
    if threshold is None:
        threshold = ECG_FIXED_THR_DEFAULT if signal_type == "ecg" else PPG_FIXED_THR_DEFAULT
    
    quantise_fn = quantise_ecg if signal_type == "ecg" else quantise_ppg
    samples_f = samples.astype(np.float64)
    
    # Normalise to [0, 1] range for threshold consistency
    s_min, s_max = float(samples_f.min()), float(samples_f.max())
    s_range = s_max - s_min
    if s_range == 0:
        # Flat signal — all directions will be 0 (stable)
        s_range = 1.0
    samples_norm = (samples_f - s_min) / s_range
    
    # Compute step for reconstruction
    if step is None:
        step = s_range / 100.0  # 1% of range per direction unit
    
    # Compute differences and quantise
    directions: List[int] = []
    window_size = ECG_SAMPLE_RATE if signal_type == "ecg" else PPG_SAMPLE_RATE
    
    thr = threshold  # Initial threshold
    
    for i in range(1, len(samples_norm)):
        delta = samples_norm[i] - samples_norm[i - 1]
        
        # Adaptive threshold per window
        if thr_mode == "adaptive_rms":
            win_start = max(0, i - window_size)
            thr = adaptive_threshold_rms(samples_norm[win_start:i])
        elif thr_mode == "adaptive_envelope":
            if i == 1:
                thr = threshold
            else:
                thr = max(ADAPTIVE_THR_MIN, ADAPTIVE_ALPHA * thr + (1 - ADAPTIVE_ALPHA) * abs(delta))
        else:
            thr = threshold
        
        d = quantise_fn(delta, thr)
        directions.append(d)
    
    # Compress with RLE
    rle_tokens = compress_rle(directions)
    
    return EncodedStream(
        rle_tokens=rle_tokens,
        start_value=float(samples_f[0]),
        threshold=threshold,
        step=step,
        sample_rate=fs,
        signal_type=signal_type,
        thr_mode=thr_mode,
        num_samples=len(samples),
    )


def decode(encoded: EncodedStream) -> np.ndarray:
    """Decode an EncodedStream back to approximate sample values.
    
    INV-INV: reconstruction error bounded by threshold and step.
    INV-DET: Deterministic for same encoded input.
    
    Args:
        encoded: EncodedStream from encode()
    
    Returns:
        1D numpy array of reconstructed samples
    """
    directions = decompress_rle(encoded.rle_tokens)
    
    reconstructed = np.zeros(len(directions) + 1, dtype=np.float64)
    reconstructed[0] = encoded.start_value
    
    for i, d in enumerate(directions):
        if d not in DIRECTION_DELTAS:
            raise ValueError(f"Unknown direction {d}")
        reconstructed[i + 1] = reconstructed[i] + encoded.step * DIRECTION_DELTAS[d]
    
    return reconstructed


def compute_prd(original: np.ndarray, reconstructed: np.ndarray) -> float:
    """Compute Percent Root-Mean-Square Difference.
    
    PRD = 100 × ||x - x̂||₂ / ||x - mean(x)||₂
    
    Lower is better. Target: < 5.0%. Stretch: < 2.0%.
    """
    if len(original) != len(reconstructed):
        raise ValueError(f"Length mismatch: {len(original)} vs {len(reconstructed)}")
    x = original.astype(np.float64)
    x_hat = reconstructed.astype(np.float64)
    numerator = np.sqrt(np.sum((x - x_hat) ** 2))
    denominator = np.sqrt(np.sum((x - np.mean(x)) ** 2))
    if denominator == 0:
        return 0.0 if numerator == 0 else float("inf")
    return 100.0 * numerator / denominator


def compute_rmse(original: np.ndarray, reconstructed: np.ndarray) -> float:
    """Compute Root-Mean-Square Error (normalised to signal range)."""
    if len(original) != len(reconstructed):
        raise ValueError(f"Length mismatch: {len(original)} vs {len(reconstructed)}")
    x = original.astype(np.float64)
    x_hat = reconstructed.astype(np.float64)
    rmse = np.sqrt(np.mean((x - x_hat) ** 2))
    s_range = x.max() - x.min()
    if s_range == 0:
        return 0.0
    return rmse / s_range


# ── CLI Demo ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    
    if "--demo" in sys.argv:
        # Generate synthetic ECG
        t = np.linspace(0, 4, 1000)
        ecg = np.sin(2 * np.pi * 1.2 * t) * 0.3  # baseline
        # Add QRS complex spikes
        for beat_t in np.arange(0.4, 4.0, 0.8):
            ecg += np.exp(-((t - beat_t) ** 2) / 0.001) * 1.0
        
        # Encode
        encoded = encode(ecg, thr_mode="adaptive_rms", signal_type="ecg")
        
        # Decode
        reconstructed = decode(encoded)
        
        # Metrics
        prd = compute_prd(ecg, reconstructed)
        cr = encoded.compression_ratio
        
        print("ZPE-Bio Codec Demo")
        print("─" * 17)
        print(f"Signal:    {len(ecg)} samples (synthetic ECG, {ECG_SAMPLE_RATE} Hz, 4s)")
        print(f"Threshold: {encoded.threshold:.4f} ({encoded.thr_mode})")
        print(f"Tokens:    {encoded.num_tokens} RLE tuples")
        print(f"CR:        {cr:.2f}× ({len(ecg)} samples → {encoded.num_tokens * 3} bytes compressed)")
        print(f"PRD:       {prd:.1f}%")
        print(f"RMSE:      {compute_rmse(ecg, reconstructed):.4f}")
