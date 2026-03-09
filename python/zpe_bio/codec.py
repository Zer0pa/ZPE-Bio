"""
ZPE-Bio Codec — Python Reference Implementation
=================================================
Ratified Phase 1.1 Dual-Mode Reference Implementation.
Supports TRANSPORT (Direction-only) and CLINICAL (Direction + Magnitude) modes.
PRD Reference: ZPE_BIOSIGNAL_CODEC_PRD_v1.0.md §6.5 §4.2
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Union
import numpy as np

# ── Constants ───────────────────────────────────────────────────────────────
ECG_SAMPLE_RATE = 250
PPG_SAMPLE_RATE = 100
MAX_RLE_COUNT = 65535

# Adaptive Threshold Constants (RUNBOOK_00 §6)
ADAPTIVE_K = 0.15
ADAPTIVE_THR_MIN = 0.001
ADAPTIVE_ALPHA = 0.95

# Weber-Fechner Log-Magnitude Table (64 entries, 6-bit)
# base = 255^(1/63) ≈ 1.091928
LOG_MAG_TABLE = np.array([round(1.091928**i) for i in range(64)], dtype=np.int32)
LOG_BASE = np.log(1.091928)

class CodecMode(Enum):
    TRANSPORT = "transport"  # High compression (CR >= 5x), direction-only
    CLINICAL = "clinical"  # High fidelity (PRD < 5%), direction + magnitude


# Mode-specific presets (normalised mV units)
MODE_CONFIGS = {
    CodecMode.TRANSPORT: {"threshold": 0.050, "step": 0.050},
    CodecMode.CLINICAL: {"threshold": 0.001, "step": 0.001},
}

DIRECTION_DELTAS = {
    0: 0.0,
    1: 1.0,    # +1x
    2: 8.0,    # +8x
    3: 32.0,   # +32x
    4: 128.0,  # +128x
    5: -32.0,  # -32x
    6: -8.0,   # -8x
    7: -1.0,   # -1x
}

@dataclass
class EncodedStream:
    # tokens are (direction, magnitude_idx, count)
    # in TRANSPORT, magnitude_idx is always 0 (val 1)
    # in CLINICAL, magnitude_idx is 0-63 (index into LOG_MAG_TABLE)
    tokens: List[Tuple[int, int, int]]
    start_value: float
    threshold: float
    step: float
    sample_rate: int
    signal_type: str
    thr_mode: str
    mode: CodecMode
    num_samples: int

    @property
    def num_tokens(self) -> int:
        return len(self.tokens)

    @property
    def compression_ratio(self) -> float:
        raw_bits = self.num_samples * 16  # Assuming 16-bit raw samples
        
        # Phase 2.3 Breakthrough VLB:
        # Each Token: 3b direction
        # + mag: 0b (Transport) or 6b (Clinical)
        # + RLE: 1b flag + (4b if short else 16b)
        total_bits = 0
        for d, m_idx, count in self.tokens:
            token_bits = 3 # direction
            if self.mode == CodecMode.CLINICAL:
                token_bits += 6 # mag_idx
            
            # RLE bit packing: 1 bit flag + 4 bits (short) or 16 bits (long)
            token_bits += 1
            if count < 16:
                token_bits += 4
            else:
                token_bits += 16
            total_bits += token_bits
            
        return raw_bits / total_bits if total_bits > 0 else 0.0


def quantise_ecg(delta: float, threshold: float) -> int:
    """Canonical Hyper-Gear selection."""
    abs_delta = abs(delta)
    if abs_delta < threshold:
        return 0

    if delta > 0:
        if abs_delta > 64 * threshold:
            return 4
        if abs_delta > 16 * threshold:
            return 3
        if abs_delta > 4 * threshold:
            return 2
        return 1

    if abs_delta > 16 * threshold:
        return 5
    if abs_delta > 4 * threshold:
        return 6
    return 7


def encode(
    samples: np.ndarray,
    mode: Union[CodecMode, str] = CodecMode.CLINICAL,
    threshold: Optional[float] = None,
    thr_mode: str = "fixed",
    signal_type: str = "ecg",
    step: Optional[float] = None,
) -> EncodedStream:
    if len(samples) < 2:
        raise ValueError("Signal too short")
    
    # Robust String-to-Enum conversion
    if isinstance(mode, str):
        mode = CodecMode(mode.lower())

    fs = ECG_SAMPLE_RATE if signal_type == "ecg" else PPG_SAMPLE_RATE
    mode_cfg = MODE_CONFIGS[mode]
    threshold = threshold if threshold is not None else mode_cfg["threshold"]
    step = step if step is not None else mode_cfg["step"]
    
    samples_f = samples.astype(np.float64)
    raw_tokens = []
    reconstructed_val = samples_f[0]
    
    # Adaptive envelope state
    env = 0.0
    
    for actual in samples_f[1:]:
        delta = actual - reconstructed_val
        
        # Update adaptive threshold if enabled
        if thr_mode == "adaptive_rms":
            # Simple envelope tracker: env = alpha * env + (1-alpha) * |delta|
            env = ADAPTIVE_ALPHA * env + (1.0 - ADAPTIVE_ALPHA) * abs(delta)
            current_thr = max(ADAPTIVE_THR_MIN, ADAPTIVE_K * env)
        else:
            current_thr = threshold
            
        d = quantise_ecg(delta, current_thr)
        
        if mode == CodecMode.TRANSPORT:
            mag_val = 1
            mag_idx = 0
        else:
            if d == 0:
                mag_idx = 0
                mag_val = 0
            else:
                d_delta = DIRECTION_DELTAS[d]
                target_m = abs(delta) / (abs(d_delta) * step)
                
                # Optimized find closest index via log math
                # Standardized Optimized Lookup (matches Rust Linear Search Parity)
                # np.argmin picks the FIRST occurrence of the minimum error.
                mag_idx = int(np.argmin(np.abs(LOG_MAG_TABLE - target_m)))
                mag_val = int(LOG_MAG_TABLE[mag_idx])
        
        raw_tokens.append((d, mag_idx))
        reconstructed_val += (DIRECTION_DELTAS[d] * mag_val) * step
    
    return EncodedStream(
        tokens=compress_rle_hybrid(raw_tokens),
        start_value=float(samples_f[0]),
        threshold=threshold,
        step=step,
        sample_rate=fs,
        signal_type=signal_type,
        thr_mode=thr_mode,
        mode=mode,
        num_samples=len(samples),
    )


def decode(encoded: EncodedStream) -> np.ndarray:
    raw_tokens = decompress_rle_hybrid(encoded.tokens)
    reconstructed = np.zeros(len(raw_tokens) + 1, dtype=np.float64)
    reconstructed[0] = encoded.start_value
    for i, (d, mag_idx) in enumerate(raw_tokens):
        if encoded.mode == CodecMode.TRANSPORT:
            mag_val = 1
        else:
            mag_val = LOG_MAG_TABLE[mag_idx] if d != 0 else 0
        reconstructed[i + 1] = reconstructed[i] + (DIRECTION_DELTAS[d] * mag_val * encoded.step)
    return reconstructed


def compress_rle_hybrid(raw_tokens: List[Tuple[int, int]]) -> List[Tuple[int, int, int]]:
    if not raw_tokens:
        return []
    result = []
    curr_d, curr_m = raw_tokens[0]
    curr_count = 1
    for d, m in raw_tokens[1:]:
        if d == curr_d and m == curr_m and curr_count < MAX_RLE_COUNT:
            curr_count += 1
        else:
            result.append((curr_d, curr_m, curr_count))
            curr_d, curr_m = d, m
            curr_count = 1
    result.append((curr_d, curr_m, curr_count))
    return result


def decompress_rle_hybrid(tokens: List[Tuple[int, int, int]]) -> List[Tuple[int, int]]:
    result = []
    for d, m, count in tokens:
        result.extend([(d, m)] * count)
    return result


def compute_prd(original: np.ndarray, reconstructed: np.ndarray) -> float:
    """PRD calculation with stability floor."""
    x = original.astype(np.float64)
    x_hat = reconstructed.astype(np.float64)
    length = min(len(x), len(x_hat))
    
    # Accuracy floor for very small signals (e.g. Asystole)
    if np.max(np.abs(x[:length])) < 1e-4:
        return 0.0 if np.max(np.abs(x_hat[:length])) < 1e-4 else 100.0
        
    numerator = np.sqrt(np.sum((x[:length] - x_hat[:length]) ** 2))
    denominator = np.sqrt(np.sum((x[:length] - np.mean(x[:length])) ** 2))
    return 100.0 * numerator / denominator if denominator > 1e-8 else 0.0


def compute_rmse(original: np.ndarray, reconstructed: np.ndarray) -> float:
    """Standardized RMSE / range."""
    x = original.astype(np.float64)
    x_hat = reconstructed.astype(np.float64)
    length = min(len(x), len(x_hat))
    err = np.sqrt(np.mean((x[:length] - x_hat[:length]) ** 2))
    s_range = x[:length].max() - x[:length].min()
    return err / s_range if s_range > 1e-8 else 0.0
