"""Wearable biosignal helpers for PRD_BIO_WEARABLE_BIOSIGNAL_AUGMENTATION_2026-02-20."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from zpe_bio.codec import CodecMode, EncodedStream, compute_prd, decode, encode


class WearableWaveError(Exception):
    """Base wearable error."""


class WearableDependencyError(WearableWaveError):
    """Raised when optional runtime dependencies are missing."""


class WearableSourceError(WearableWaveError):
    """Raised when datasets or source files are missing/unavailable."""


def _require_module(name: str) -> Any:
    try:
        return __import__(name)
    except ImportError as exc:  # pragma: no cover - exercised via CLI/runtime paths
        raise WearableDependencyError(f"Missing dependency: {name}") from exc


def _gzip_size(payload: bytes) -> int:
    import gzip

    return len(gzip.compress(payload, compresslevel=9))


def _canon_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def encoded_stream_bytes(encoded: EncodedStream) -> int:
    """Estimate encoded bytes from token stream bit packing."""
    bits = 0
    for _direction, _magnitude_idx, count in encoded.tokens:
        bits += 3
        if encoded.mode == CodecMode.CLINICAL:
            bits += 6
        bits += 1
        bits += 4 if count < 16 else 16
    return int((bits + 7) // 8)


def snr_db(original: np.ndarray, reconstructed: np.ndarray) -> float:
    length = min(original.shape[0], reconstructed.shape[0])
    src = original[:length].astype(np.float64)
    rec = reconstructed[:length].astype(np.float64)
    noise = src - rec
    src_power = float(np.mean(src * src))
    noise_power = float(np.mean(noise * noise))
    if noise_power <= 1e-15:
        return 200.0
    if src_power <= 1e-15:
        return 0.0
    return float(10.0 * math.log10(src_power / noise_power))


def load_wfdb_record(
    record_name: str,
    pn_dir: str,
    channel_index: int = 0,
    max_samples: int | None = None,
) -> dict[str, Any]:
    wfdb = _require_module("wfdb")
    try:
        record = wfdb.rdrecord(record_name, pn_dir=pn_dir, sampto=max_samples)
    except Exception as exc:
        raise WearableSourceError(f"Failed to load WFDB record {record_name} from {pn_dir}: {exc}") from exc

    if channel_index < 0 or channel_index >= record.p_signal.shape[1]:
        raise WearableWaveError(
            f"channel_index out of range: {channel_index} not in [0, {record.p_signal.shape[1] - 1}]"
        )

    signal = record.p_signal[:, channel_index].astype(np.float64)
    return {
        "record_name": record_name,
        "pn_dir": pn_dir,
        "sample_rate_hz": float(record.fs),
        "signal": signal,
        "channels": list(record.sig_name),
    }


def roundtrip_metrics(
    signal: np.ndarray,
    signal_type: str,
    mode: CodecMode = CodecMode.CLINICAL,
    thr_mode: str = "adaptive_rms",
    threshold: float | None = None,
    step: float | None = None,
) -> tuple[EncodedStream, np.ndarray, dict[str, Any]]:
    encoded = encode(
        signal,
        mode=mode,
        thr_mode=thr_mode,
        threshold=threshold,
        step=step,
        signal_type=signal_type,
    )
    reconstructed = decode(encoded)
    length = min(signal.shape[0], reconstructed.shape[0])
    original = signal[:length]
    rebuilt = reconstructed[:length]

    raw_bytes = int(length * 2)
    zpe_bytes_est = encoded_stream_bytes(encoded)
    gzip_bytes = _gzip_size(original.astype(np.float32).tobytes())
    prd = float(compute_prd(original, rebuilt))
    snr = float(snr_db(original, rebuilt))
    compression_ratio = float(raw_bytes / zpe_bytes_est) if zpe_bytes_est > 0 else 0.0

    payload = {
        "samples": int(length),
        "raw_bytes": raw_bytes,
        "gzip_bytes": int(gzip_bytes),
        "zpe_bytes_est": int(zpe_bytes_est),
        "compression_ratio": round(compression_ratio, 6),
        "prd_percent": round(prd, 6),
        "snr_db": round(snr, 6),
        "tokens": int(encoded.num_tokens),
        "mode": encoded.mode.value,
        "thr_mode": encoded.thr_mode,
        "threshold": float(encoded.threshold),
        "step": float(encoded.step),
    }
    return encoded, rebuilt, payload


def multiaxis_imu_metrics(
    axes: np.ndarray,
    threshold: float = 0.08,
    step: float = 0.08,
) -> dict[str, Any]:
    if axes.ndim != 2:
        raise WearableWaveError("axes must be a 2D [samples, channels] array")
    if axes.shape[1] < 3:
        raise WearableWaveError("expected at least 3 IMU axes")

    encoded_rows: list[dict[str, Any]] = []
    total_raw = 0
    total_zpe = 0
    total_gzip = 0
    cr_list = []

    for idx in range(axes.shape[1]):
        signal = axes[:, idx].astype(np.float64)
        encoded, _decoded, row = roundtrip_metrics(
            signal=signal,
            signal_type="ppg",
            mode=CodecMode.TRANSPORT,
            thr_mode="fixed",
            threshold=threshold,
            step=step,
        )
        # IMU raw baseline is float32 for each axis.
        axis_raw = int(signal.shape[0] * 4)
        axis_cr = float(axis_raw / row["zpe_bytes_est"]) if row["zpe_bytes_est"] > 0 else 0.0
        encoded_rows.append(
            {
                "axis_index": idx,
                "samples": row["samples"],
                "raw_bytes_float32": axis_raw,
                "zpe_bytes_est": row["zpe_bytes_est"],
                "gzip_bytes": row["gzip_bytes"],
                "compression_ratio_vs_float32": round(axis_cr, 6),
                "tokens": encoded.num_tokens,
            }
        )
        total_raw += axis_raw
        total_zpe += int(row["zpe_bytes_est"])
        total_gzip += int(row["gzip_bytes"])
        cr_list.append(axis_cr)

    aggregate_cr = float(total_raw / total_zpe) if total_zpe > 0 else 0.0
    return {
        "samples": int(axes.shape[0]),
        "axes": int(axes.shape[1]),
        "per_axis": encoded_rows,
        "aggregate": {
            "raw_bytes_float32": int(total_raw),
            "gzip_bytes": int(total_gzip),
            "zpe_bytes_est": int(total_zpe),
            "compression_ratio_vs_float32": round(aggregate_cr, 6),
            "mean_axis_cr": round(float(np.mean(cr_list)) if cr_list else 0.0, 6),
        },
    }


@dataclass
class MorphologyFeatures:
    qrs_ms: float
    pr_ms: float
    qtc_ms: float


def extract_ecg_morphology(signal: np.ndarray, sampling_rate_hz: float) -> MorphologyFeatures:
    nk = _require_module("neurokit2")

    clean = nk.ecg_clean(signal, sampling_rate=int(sampling_rate_hz))
    _peaks_df, peak_info = nk.ecg_peaks(clean, sampling_rate=int(sampling_rate_hz))
    r_peaks = peak_info.get("ECG_R_Peaks", [])
    if len(r_peaks) < 3:
        raise WearableWaveError("not enough R peaks for morphology extraction")
    _sig_df, info = nk.ecg_delineate(
        clean,
        r_peaks,
        sampling_rate=int(sampling_rate_hz),
        method="peak",
    )

    q = np.array([v for v in info.get("ECG_Q_Peaks", []) if v == v], dtype=np.float64)
    s = np.array([v for v in info.get("ECG_S_Peaks", []) if v == v], dtype=np.float64)
    p_on = np.array([v for v in info.get("ECG_P_Onsets", []) if v == v], dtype=np.float64)
    t_off = np.array([v for v in info.get("ECG_T_Offsets", []) if v == v], dtype=np.float64)
    r = np.array([v for v in r_peaks if v == v], dtype=np.float64)

    if min(q.size, s.size, p_on.size, t_off.size, r.size) < 2:
        raise WearableWaveError("insufficient delineation points for morphology metrics")

    qrs_ms = float(np.median((s[: q.size] - q[: s.size]) / sampling_rate_hz * 1000.0))
    pr_ms = float(np.median((q[: p_on.size] - p_on[: q.size]) / sampling_rate_hz * 1000.0))
    qt_ms = float(np.median((t_off[: q.size] - q[: t_off.size]) / sampling_rate_hz * 1000.0))
    rr_s = np.diff(r) / sampling_rate_hz
    rr = float(np.median(rr_s)) if rr_s.size > 0 else 1.0
    rr = max(rr, 1e-6)
    qtc_ms = float(qt_ms / math.sqrt(rr))
    return MorphologyFeatures(qrs_ms=qrs_ms, pr_ms=pr_ms, qtc_ms=qtc_ms)


def morphology_deviation_percent(
    original_signal: np.ndarray,
    reconstructed_signal: np.ndarray,
    sampling_rate_hz: float,
) -> dict[str, Any]:
    orig = extract_ecg_morphology(original_signal, sampling_rate_hz=sampling_rate_hz)
    reco = extract_ecg_morphology(reconstructed_signal, sampling_rate_hz=sampling_rate_hz)

    def deviation(a: float, b: float) -> float:
        denom = max(abs(a), 1e-9)
        return float(abs(b - a) / denom * 100.0)

    qrs_dev = deviation(orig.qrs_ms, reco.qrs_ms)
    pr_dev = deviation(orig.pr_ms, reco.pr_ms)
    qtc_dev = deviation(orig.qtc_ms, reco.qtc_ms)
    return {
        "original": {
            "qrs_ms": round(orig.qrs_ms, 6),
            "pr_ms": round(orig.pr_ms, 6),
            "qtc_ms": round(orig.qtc_ms, 6),
        },
        "reconstructed": {
            "qrs_ms": round(reco.qrs_ms, 6),
            "pr_ms": round(reco.pr_ms, 6),
            "qtc_ms": round(reco.qtc_ms, 6),
        },
        "deviation_percent": {
            "qrs": round(qrs_dev, 6),
            "pr": round(pr_dev, 6),
            "qtc": round(qtc_dev, 6),
            "max": round(max(qrs_dev, pr_dev, qtc_dev), 6),
        },
    }


def ecg_ppg_alignment_error_ms(ecg_signal: np.ndarray, ppg_signal: np.ndarray, sampling_rate_hz: float) -> dict[str, Any]:
    nk = _require_module("neurokit2")

    ecg_clean = nk.ecg_clean(ecg_signal, sampling_rate=int(sampling_rate_hz))
    ppg_clean = nk.ppg_clean(ppg_signal, sampling_rate=int(sampling_rate_hz))
    _ecg_df, ecg_info = nk.ecg_peaks(ecg_clean, sampling_rate=int(sampling_rate_hz))
    _ppg_df, ppg_info = nk.ppg_peaks(ppg_clean, sampling_rate=int(sampling_rate_hz))
    ecg_peaks = np.array(ecg_info.get("ECG_R_Peaks", []), dtype=np.int64)
    ppg_peaks = np.array(ppg_info.get("PPG_Peaks", []), dtype=np.int64)
    if ecg_peaks.size < 3 or ppg_peaks.size < 3:
        raise WearableWaveError("not enough ECG/PPG peaks for alignment analysis")

    min_delay = int(max(1, round(0.02 * sampling_rate_hz)))
    max_delay = int(max(min_delay + 1, round(0.30 * sampling_rate_hz)))
    offsets: list[int] = []
    for ecg_idx in ecg_peaks:
        candidates = ppg_peaks[(ppg_peaks > (ecg_idx + min_delay)) & (ppg_peaks < (ecg_idx + max_delay))]
        if candidates.size == 0:
            continue
        offsets.append(int(candidates[0] - ecg_idx))
    if len(offsets) < 3:
        raise WearableWaveError("insufficient paired ECG/PPG beats after transit-window matching")

    offsets_arr = np.array(offsets, dtype=np.float64)
    delay_samples = float(np.median(offsets_arr))
    residual = np.abs(offsets_arr - delay_samples)
    residual_ms = residual / sampling_rate_hz * 1000.0
    return {
        "estimated_delay_samples": round(delay_samples, 6),
        "estimated_delay_ms": round(delay_samples / sampling_rate_hz * 1000.0, 6),
        "alignment_error_ms_median": round(float(np.median(residual_ms)), 6),
        "alignment_error_ms_p95": round(float(np.percentile(residual_ms, 95)), 6),
        "paired_peak_count": int(offsets_arr.size),
    }


def confusion_metrics(labels: np.ndarray, preds: np.ndarray) -> dict[str, Any]:
    if labels.shape != preds.shape:
        raise WearableWaveError("labels and preds shape mismatch")
    labels_i = labels.astype(np.int32)
    preds_i = preds.astype(np.int32)

    tp = int(np.sum((labels_i == 1) & (preds_i == 1)))
    tn = int(np.sum((labels_i == 0) & (preds_i == 0)))
    fp = int(np.sum((labels_i == 0) & (preds_i == 1)))
    fn = int(np.sum((labels_i == 1) & (preds_i == 0)))

    sensitivity = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = sensitivity
    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "sensitivity": round(sensitivity, 6),
        "specificity": round(specificity, 6),
        "precision": round(precision, 6),
        "recall": round(recall, 6),
    }


def window_rr_irregularity(
    signal: np.ndarray,
    sampling_rate_hz: float,
    window_samples: int,
    step_samples: int,
) -> list[dict[str, Any]]:
    nk = _require_module("neurokit2")

    out: list[dict[str, Any]] = []
    for start in range(0, max(signal.shape[0] - window_samples, 1), step_samples):
        end = min(start + window_samples, signal.shape[0])
        window = signal[start:end]
        if window.shape[0] < 128:
            continue
        clean = nk.ecg_clean(window, sampling_rate=int(sampling_rate_hz))
        _df, info = nk.ecg_peaks(clean, sampling_rate=int(sampling_rate_hz))
        peaks = np.array(info.get("ECG_R_Peaks", []), dtype=np.int64)
        if peaks.size < 4:
            continue
        rr = np.diff(peaks) / sampling_rate_hz
        if rr.size < 3:
            continue
        cv = float(np.std(rr) / max(np.mean(rr), 1e-9))
        rmssd = float(np.sqrt(np.mean(np.square(np.diff(rr)))))
        out.append(
            {
                "start": int(start),
                "end": int(end),
                "rr_count": int(rr.size),
                "rr_cv": round(cv, 6),
                "rr_rmssd": round(rmssd, 6),
            }
        )
    return out


def payload_hash(payload: dict[str, Any]) -> str:
    return _canon_hash(payload)
