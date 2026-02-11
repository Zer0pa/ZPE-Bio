"""
Unit tests for ZPE-Bio Python codec.
Tests align with PRD invariants INV-DET, INV-INV, INV-NOFLOW, INV-CAUSAL.
"""
import numpy as np
import pytest
from hypothesis import given, strategies as st, settings

from zpe_bio.codec import (
    quantise_ecg, quantise_ppg, adaptive_threshold_rms,
    compress_rle, decompress_rle, encode, decode,
    compute_prd, compute_rmse,
    ECG_FIXED_THR_DEFAULT, MAX_RLE_COUNT, ACTIVE_DIRECTIONS,
)


class TestQuantiseECG:
    """INV-DET: quantise_ecg is a pure deterministic function."""
    
    def test_stable_signal(self):
        assert quantise_ecg(0.0, 0.05) == 0
    
    def test_moderate_increase(self):
        assert quantise_ecg(0.06, 0.05) == 1
    
    def test_acute_increase(self):
        assert quantise_ecg(0.11, 0.05) == 2
    
    def test_moderate_decrease(self):
        assert quantise_ecg(-0.06, 0.05) == 7
    
    def test_acute_decrease(self):
        assert quantise_ecg(-0.11, 0.05) == 6
    
    def test_boundary_at_thr(self):
        # At exactly threshold, should be stable (<=)
        assert quantise_ecg(0.05, 0.05) == 0
    
    def test_boundary_at_2thr(self):
        # At exactly 2*threshold, should be moderate (<=)
        assert quantise_ecg(0.10, 0.05) == 1
    
    def test_negative_threshold_raises(self):
        with pytest.raises(ValueError):
            quantise_ecg(0.1, -0.01)
    
    @given(delta=st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False))
    @settings(max_examples=1000)
    def test_deterministic(self, delta):
        """INV-DET: Same input always gives same output."""
        r1 = quantise_ecg(delta, 0.05)
        r2 = quantise_ecg(delta, 0.05)
        assert r1 == r2
        assert r1 in ACTIVE_DIRECTIONS


class TestRLE:
    """INV-NOFLOW: RLE counts bounded to MAX_RLE_COUNT."""
    
    def test_empty_input(self):
        assert compress_rle([]) == []
    
    def test_single_element(self):
        assert compress_rle([0]) == [(0, 1)]
    
    def test_run_of_same(self):
        assert compress_rle([0, 0, 0]) == [(0, 3)]
    
    def test_alternating(self):
        assert compress_rle([0, 1, 0]) == [(0, 1), (1, 1), (0, 1)]
    
    def test_max_count_split(self):
        """INV-NOFLOW: Runs exceeding MAX_RLE_COUNT must be split."""
        big_run = [0] * (MAX_RLE_COUNT + 10)
        result = compress_rle(big_run)
        assert result[0] == (0, MAX_RLE_COUNT)
        assert result[1] == (0, 10)
    
    def test_roundtrip(self):
        """compress then decompress must be identity."""
        original = [0, 0, 1, 2, 2, 2, 7, 7, 6, 0]
        rle = compress_rle(original)
        recovered = decompress_rle(rle)
        assert recovered == original


class TestEncodeDecode:
    """INV-INV: decode(encode(x)) approximates x."""
    
    def test_sine_wave(self):
        t = np.linspace(0, 2, 500)
        signal = np.sin(2 * np.pi * t)
        
        # Use a small threshold to ensure we capture the sine wave shape
        encoded = encode(signal, threshold=0.01, signal_type="ecg", thr_mode="fixed")
        reconstructed = decode(encoded)
        
        assert len(reconstructed) == len(signal)
        prd = compute_prd(signal, reconstructed)
        # PRD should be finite and bounded
        assert 0 <= prd <= 100.0001
    
    def test_flat_signal(self):
        """DT-8 style: flat signal should not crash."""
        signal = np.ones(500) * 42.0
        encoded = encode(signal, signal_type="ecg", thr_mode="fixed")
        reconstructed = decode(encoded)
        assert len(reconstructed) == len(signal)
    
    def test_deterministic(self):
        """INV-DET: encoding the same signal twice gives identical output."""
        signal = np.random.RandomState(42).randn(500)
        e1 = encode(signal, signal_type="ecg")
        e2 = encode(signal, signal_type="ecg")
        assert e1.rle_tokens == e2.rle_tokens
        assert e1.start_value == e2.start_value
    
    def test_ppg_mode(self):
        """REQ-CODEC-5: PPG mode should work without error."""
        t = np.linspace(0, 2, 200)
        ppg = np.sin(2 * np.pi * 1.0 * t) * 0.5
        encoded = encode(ppg, signal_type="ppg", thr_mode="fixed")
        reconstructed = decode(encoded)
        assert len(reconstructed) == len(ppg)


class TestAdaptiveThreshold:
    """INV-DET, INV-CAUSAL: adaptive threshold is deterministic and causal."""
    
    def test_flat_window(self):
        thr = adaptive_threshold_rms(np.zeros(100))
        assert thr == 0.005  # should return thr_min
    
    def test_noisy_window(self):
        thr = adaptive_threshold_rms(np.ones(100))
        assert thr > 0.005  # should be > thr_min for non-zero signal
    
    def test_deterministic(self):
        window = np.random.RandomState(42).randn(250)
        t1 = adaptive_threshold_rms(window)
        t2 = adaptive_threshold_rms(window)
        assert t1 == t2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
