"""Wave-2 biosignal helpers for ECG/EEG/chemosense multimodal CLI commands."""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import Any

import numpy as np

from zpe_bio.codec import CodecMode, EncodedStream, compute_prd, decode, encode
from zpe_bio.multimodal.mental import (
    DirectionProfile,
    DrawDir as MentalDrawDir,
    FormClass,
    MentalStroke,
    MoveTo as MentalMoveTo,
    SymmetryOrder,
    pack_mental_strokes,
    unpack_mental_words,
)
from zpe_bio.multimodal.smell import (
    OdorCategory,
    pack_odor_strokes,
    synthetic_sniff_stroke,
    unpack_odor_words,
)
from zpe_bio.multimodal.taste import (
    TasteQuality,
    pack_taste_strokes,
    pack_taste_zlayered,
    synthetic_quality_profiles,
    synthetic_taste_stroke_8phase,
    unpack_taste_words,
    unpack_taste_zlayered,
    zlayered_event_from_vector,
)


class Wave2Error(Exception):
    """Base Wave-2 exception type."""

    code = "WAVE2_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class DependencyError(Wave2Error):
    code = "BLOCKER_DEP_INSTALL"


class SourceError(Wave2Error):
    code = "BLOCKER_SOURCE_UNAVAILABLE"


class InputError(Wave2Error):
    code = "WAVE2_INVALID_INPUT"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_words(words: list[int]) -> str:
    return _sha256_text(json.dumps(words, separators=(",", ":"), sort_keys=False))


def _canon_hash(payload: dict[str, Any]) -> str:
    return _sha256_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def _gzip_size(payload: bytes) -> int:
    return len(gzip.compress(payload, compresslevel=9))


def _normalise_signal(signal: np.ndarray) -> np.ndarray:
    arr = signal.astype(np.float64)
    std = float(np.std(arr))
    if std < 1e-12:
        return np.zeros_like(arr)
    return (arr - float(np.mean(arr))) / std


def load_mitbih_record(
    record_id: str,
    lead_index: int = 0,
    max_samples: int | None = None,
    dataset_dir: Path | None = None,
) -> dict[str, Any]:
    try:
        import wfdb
    except ImportError as exc:  # pragma: no cover - exercised in CLI error path
        raise DependencyError(
            "WFDB is required for ECG ingest. Install with `.venv/bin/python -m pip install -e '.[validation]'`."
        ) from exc

    root = dataset_dir or _resolve_mitdb_dir()
    record_path = root / record_id
    if not (record_path.with_suffix(".hea").exists() and record_path.with_suffix(".dat").exists()):
        raise SourceError(f"MIT-BIH record not found for id={record_id} under {root}.")

    record = wfdb.rdrecord(str(record_path))
    if lead_index < 0 or lead_index >= record.p_signal.shape[1]:
        raise InputError(f"lead-index out of range: {lead_index}")

    signal = record.p_signal[:, lead_index].astype(np.float64)
    if max_samples is not None:
        if max_samples < 32:
            raise InputError("samples must be >= 32")
        signal = signal[:max_samples]
    return {
        "record_id": record_id,
        "lead_index": lead_index,
        "sample_rate_hz": float(record.fs),
        "signal": signal,
    }


def _resolve_mitdb_dir() -> Path:
    env_value = os.getenv("ZPE_BIO_MITDB_DIR")
    candidates: list[Path] = []
    if env_value:
        candidates.append(Path(env_value).expanduser())
    candidates.extend(
        [
            Path.cwd() / "validation" / "datasets" / "mitdb",
            Path(__file__).resolve().parents[2] / "validation" / "datasets" / "mitdb",
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[-1]


def ecg_roundtrip_metrics(
    signal: np.ndarray,
    mode: CodecMode = CodecMode.CLINICAL,
    thr_mode: str = "adaptive_rms",
    threshold: float | None = None,
    step: float | None = None,
) -> tuple[EncodedStream, np.ndarray, dict[str, Any]]:
    t0 = time.perf_counter()
    encoded = encode(
        signal,
        mode=mode,
        thr_mode=thr_mode,
        threshold=threshold,
        step=step,
        signal_type="ecg",
    )
    t1 = time.perf_counter()
    reconstructed = decode(encoded)
    t2 = time.perf_counter()

    min_len = min(len(signal), len(reconstructed))
    original = signal[:min_len]
    rebuilt = reconstructed[:min_len]
    prd = float(compute_prd(original, rebuilt))

    raw_bytes = int(len(signal) * 2)  # normalized 16-bit baseline
    gzip_bytes = _gzip_size(signal.astype(np.float32).tobytes())
    encoded_bits = (len(signal) * 16) / encoded.compression_ratio if encoded.compression_ratio > 0 else 0.0
    zpe_bytes_est = int(math.ceil(encoded_bits / 8.0))

    metrics = {
        "samples": int(len(signal)),
        "tokens": int(encoded.num_tokens),
        "compression_ratio": round(float(encoded.compression_ratio), 6),
        "prd_percent": round(prd, 6),
        "raw_bytes": raw_bytes,
        "raw_bytes_16bit": raw_bytes,
        "gzip_bytes": int(gzip_bytes),
        "zpe_bytes_est": zpe_bytes_est,
        "gzip_cr": round(raw_bytes / gzip_bytes, 6) if gzip_bytes > 0 else 0.0,
        "zpe_cr_est": round(raw_bytes / zpe_bytes_est, 6) if zpe_bytes_est > 0 else 0.0,
        "encode_ms": round((t1 - t0) * 1000.0, 6),
        "decode_ms": round((t2 - t1) * 1000.0, 6),
        "encode_latency_ms": round((t1 - t0) * 1000.0, 6),
        "decode_latency_ms": round((t2 - t1) * 1000.0, 6),
        "stream_hash": _sha256_text(json.dumps(encoded.tokens, separators=(",", ":"), default=list)),
        "mode": encoded.mode.value,
        "thr_mode": encoded.thr_mode,
        "threshold": float(encoded.threshold),
        "step": float(encoded.step),
    }
    return encoded, reconstructed, metrics


def _quantize_12(values: np.ndarray) -> tuple[np.ndarray, float, float]:
    lo = float(np.min(values))
    hi = float(np.max(values))
    if abs(hi - lo) < 1e-12:
        return np.zeros(values.shape[0], dtype=np.int32), lo, hi
    scaled = (values - lo) / (hi - lo)
    bins = np.clip(np.rint(scaled * 11.0), 0, 11).astype(np.int32)
    return bins, lo, hi


def _dequantize_12(q: np.ndarray, lo: float, hi: float) -> np.ndarray:
    if abs(hi - lo) < 1e-12:
        return np.full(q.shape[0], lo, dtype=np.float64)
    return lo + (q.astype(np.float64) / 11.0) * (hi - lo)


def _mental_strokes_from_bins(
    bins: np.ndarray,
    chunk_size: int = 120,
    frame_offset: int = 0,
) -> list[MentalStroke]:
    strokes: list[MentalStroke] = []
    if chunk_size < 8:
        raise InputError("chunk_size must be >= 8")
    for idx in range(0, bins.shape[0], chunk_size):
        chunk = bins[idx : idx + chunk_size]
        if chunk.size == 0:
            continue
        commands = [MentalMoveTo(128, 128)] + [
            MentalDrawDir(int(direction), profile=DirectionProfile.D6_12) for direction in chunk
        ]
        strokes.append(
            MentalStroke(
                commands=commands,
                form_class=FormClass.LATTICE,
                symmetry=SymmetryOrder.D6,
                direction_profile=DirectionProfile.D6_12,
                spatial_frequency=4,
                drift_speed=1,
                frame_index=frame_offset + (idx // chunk_size),
                delta_ms=4,
            )
        )
    return strokes


def _read_edf_with_pyedflib(edf_path: Path, max_channels: int, max_samples: int) -> dict[str, Any]:
    import pyedflib

    reader = pyedflib.EdfReader(str(edf_path))
    try:
        n_signals = int(reader.signals_in_file)
        channels = min(max_channels, n_signals)
        names = reader.getSignalLabels()[:channels]
        sfreqs = [float(reader.getSampleFrequency(i)) for i in range(channels)]
        signals = []
        for ch in range(channels):
            raw = reader.readSignal(ch).astype(np.float64)
            signals.append(raw[:max_samples] if max_samples > 0 else raw)
        return {
            "backend": "pyedflib",
            "channel_names": list(names),
            "sample_rate_hz": float(sfreqs[0]) if sfreqs else 0.0,
            "signals": signals,
        }
    finally:
        reader.close()


def _read_edf_with_mne(edf_path: Path, max_channels: int, max_samples: int) -> dict[str, Any]:
    import mne

    raw = mne.io.read_raw_edf(str(edf_path), preload=True, verbose="ERROR")
    channels = min(max_channels, len(raw.ch_names))
    data = raw.get_data(picks=list(range(channels)))
    if max_samples > 0:
        data = data[:, :max_samples]
    return {
        "backend": "mne",
        "channel_names": list(raw.ch_names[:channels]),
        "sample_rate_hz": float(raw.info.get("sfreq", 0.0)),
        "signals": [data[idx].astype(np.float64) for idx in range(data.shape[0])],
    }


def load_eeg_signals(
    edf_path: Path | None,
    max_channels: int,
    max_samples: int,
    synthetic: bool,
    seed: int = 20260220,
) -> dict[str, Any]:
    if synthetic:
        rng = np.random.default_rng(seed)
        t = np.linspace(0.0, 4.0, max_samples, endpoint=False, dtype=np.float64)
        signals = []
        channel_names = []
        for idx in range(max_channels):
            base = 0.40 * np.sin(2.0 * np.pi * (6 + idx) * t)
            mod = 0.20 * np.sin(2.0 * np.pi * (12 + idx) * t + (idx * 0.2))
            noise = 0.03 * rng.normal(size=max_samples)
            signals.append((base + mod + noise).astype(np.float64))
            channel_names.append(f"SYNTH_CH{idx + 1}")
        return {
            "mode": "synthetic",
            "backend": "synthetic",
            "channel_names": channel_names,
            "sample_rate_hz": 256.0,
            "signals": signals,
            "source_path": None,
        }

    if edf_path is None:
        raise SourceError("No EEG file provided. Use --edf <path> or --synthetic-eeg.")
    if not edf_path.exists():
        raise SourceError(f"EEG file not found: {edf_path}")

    pyedflib_error: Exception | None = None
    try:
        data = _read_edf_with_pyedflib(edf_path, max_channels=max_channels, max_samples=max_samples)
        data["mode"] = "real_file"
        data["source_path"] = str(edf_path)
        return data
    except ImportError as exc:
        pyedflib_error = exc
    except Exception:
        # Keep fallback path alive for files pyedflib cannot parse in this environment.
        pyedflib_error = None

    try:
        data = _read_edf_with_mne(edf_path, max_channels=max_channels, max_samples=max_samples)
        data["mode"] = "real_file"
        data["source_path"] = str(edf_path)
        return data
    except ImportError as exc:
        if pyedflib_error is not None:
            raise DependencyError(
                "EEG file mode requires `pyedflib` or `mne`. Install via `.venv/bin/python -m pip install mne pyedflib`."
            ) from exc
        raise DependencyError(
            "EEG file mode requires `mne`. Install via `.venv/bin/python -m pip install mne`."
        ) from exc


def encode_eeg_to_mental(
    edf_path: Path | None,
    max_channels: int = 2,
    max_samples: int = 2048,
    synthetic: bool = False,
) -> dict[str, Any]:
    t_all_start = time.perf_counter()
    eeg = load_eeg_signals(
        edf_path=edf_path,
        max_channels=max_channels,
        max_samples=max_samples,
        synthetic=synthetic,
    )
    channels_metrics: list[dict[str, Any]] = []
    total_words = 0
    total_strokes = 0
    total_raw_bytes = 0
    total_zpe_bytes = 0
    encode_ms_total = 0.0
    decode_ms_total = 0.0
    gzip_source_bytes: list[bytes] = []

    for idx, signal in enumerate(eeg["signals"]):
        norm = _normalise_signal(signal)
        bins, lo, hi = _quantize_12(norm)
        strokes = _mental_strokes_from_bins(bins=bins, frame_offset=idx * 100)
        t_encode_start = time.perf_counter()
        words = pack_mental_strokes(strokes, metadata={"use_rle": True})
        t_encode_end = time.perf_counter()
        t_decode_start = time.perf_counter()
        meta, decoded = unpack_mental_words(words)
        t_decode_end = time.perf_counter()

        decoded_dirs: list[int] = []
        for stroke in decoded:
            decoded_dirs.extend(
                cmd.direction
                for cmd in stroke.commands
                if isinstance(cmd, MentalDrawDir)
            )
        decoded_arr = np.array(decoded_dirs[: bins.shape[0]], dtype=np.int32)
        quant_match = bool(np.array_equal(decoded_arr, bins[: decoded_arr.shape[0]]))
        rec_norm = _dequantize_12(decoded_arr, lo=float(lo), hi=float(hi))
        sig_slice = norm[: decoded_arr.shape[0]]
        rmse = float(np.sqrt(np.mean((sig_slice - rec_norm) ** 2))) if decoded_arr.size else 0.0

        raw_bytes = int(signal.shape[0] * 2)  # normalized 16-bit baseline
        zpe_bytes_est = int(math.ceil((len(words) * 20) / 8.0))
        encode_ms = (t_encode_end - t_encode_start) * 1000.0
        decode_ms = (t_decode_end - t_decode_start) * 1000.0
        gzip_source_bytes.append(signal.astype(np.float32).tobytes())

        total_words += len(words)
        total_strokes += len(strokes)
        total_raw_bytes += raw_bytes
        total_zpe_bytes += zpe_bytes_est
        encode_ms_total += encode_ms
        decode_ms_total += decode_ms
        channels_metrics.append(
            {
                "channel_index": idx,
                "channel_name": eeg["channel_names"][idx],
                "samples": int(signal.shape[0]),
                "strokes": len(strokes),
                "word_count": len(words),
                "decoded_strokes": len(decoded),
                "quantized_direction_match": quant_match,
                "signal_rmse": round(rmse, 6),
                "raw_bytes": raw_bytes,
                "gzip_bytes": _gzip_size(signal.astype(np.float32).tobytes()),
                "zpe_bytes_est": zpe_bytes_est,
                "encode_ms": round(encode_ms, 6),
                "decode_ms": round(decode_ms, 6),
                "word_hash": _sha256_words(words),
                "mental_encoding": meta["encoding"] if isinstance(meta, dict) and "encoding" in meta else "unknown",
            }
        )

    gzip_bytes = _gzip_size(b"".join(gzip_source_bytes)) if gzip_source_bytes else 0
    result = {
        "mode": eeg["mode"],
        "backend": eeg["backend"],
        "source_path": eeg["source_path"],
        "channel_count": len(channels_metrics),
        "sample_rate_hz": eeg["sample_rate_hz"],
        "total_words": total_words,
        "total_strokes": total_strokes,
        "raw_bytes": total_raw_bytes,
        "gzip_bytes": int(gzip_bytes),
        "zpe_bytes_est": int(total_zpe_bytes),
        "encode_ms": round(encode_ms_total, 6),
        "decode_ms": round(decode_ms_total, 6),
        "total_runtime_ms": round((time.perf_counter() - t_all_start) * 1000.0, 6),
        "channels": channels_metrics,
    }
    # Stream hash excludes volatile timing fields so deterministic replay stays stable.
    hash_channels = [
        {k: v for k, v in row.items() if k not in {"encode_ms", "decode_ms"}}
        for row in channels_metrics
    ]
    hash_payload = {
        "mode": result["mode"],
        "backend": result["backend"],
        "source_path": result["source_path"],
        "channel_count": result["channel_count"],
        "sample_rate_hz": result["sample_rate_hz"],
        "total_words": result["total_words"],
        "total_strokes": result["total_strokes"],
        "raw_bytes": result["raw_bytes"],
        "gzip_bytes": result["gzip_bytes"],
        "zpe_bytes_est": result["zpe_bytes_est"],
        "channels": hash_channels,
    }
    result["stream_hash"] = _canon_hash(hash_payload)
    return result


def benchmark_ecg_records(
    record_ids: list[str],
    lead_index: int,
    samples: int,
    mode: CodecMode,
    thr_mode: str,
    threshold: float | None = None,
    step: float | None = None,
    dataset_dir: Path | None = None,
) -> dict[str, Any]:
    records = []
    for record_id in record_ids:
        loaded = load_mitbih_record(
            record_id=record_id,
            lead_index=lead_index,
            max_samples=samples,
            dataset_dir=dataset_dir,
        )
        _enc, _rec, metrics = ecg_roundtrip_metrics(
            loaded["signal"],
            mode=mode,
            thr_mode=thr_mode,
            threshold=threshold,
            step=step,
        )
        records.append(
            {
                "record_id": record_id,
                "lead_index": lead_index,
                "sample_rate_hz": loaded["sample_rate_hz"],
                **metrics,
            }
        )

    aggregate = {
        "records_processed": len(records),
        "mean_cr": round(float(np.mean([r["compression_ratio"] for r in records])), 6),
        "mean_prd": round(float(np.mean([r["prd_percent"] for r in records])), 6),
        "max_prd": round(float(np.max([r["prd_percent"] for r in records])), 6),
        "mean_encode_latency_ms": round(float(np.mean([r["encode_latency_ms"] for r in records])), 6),
        "mean_decode_latency_ms": round(float(np.mean([r["decode_latency_ms"] for r in records])), 6),
    }
    result = {
        "lane": "ecg",
        "mode": mode.value,
        "thr_mode": thr_mode,
        "threshold": threshold,
        "step": step,
        "records": records,
        "aggregate": aggregate,
    }
    result["stream_hash"] = _canon_hash(result)
    return result


def build_multimodal_stream(
    ecg_record_id: str,
    lead_index: int,
    ecg_samples: int,
    eeg_path: Path | None,
    eeg_channels: int,
    eeg_samples: int,
    synthetic_eeg: bool,
) -> dict[str, Any]:
    ecg_loaded = load_mitbih_record(
        record_id=ecg_record_id,
        lead_index=lead_index,
        max_samples=ecg_samples,
    )
    encoded_ecg, decoded_ecg, ecg_metrics = ecg_roundtrip_metrics(
        ecg_loaded["signal"],
        mode=CodecMode.CLINICAL,
        thr_mode="adaptive_rms",
    )
    eeg_metrics = encode_eeg_to_mental(
        edf_path=eeg_path,
        max_channels=eeg_channels,
        max_samples=eeg_samples,
        synthetic=synthetic_eeg,
    )

    hash_safe_eeg_channels = [
        {k: v for k, v in row.items() if k not in {"encode_ms", "decode_ms"}}
        for row in eeg_metrics["channels"]
    ]

    lane_payload = {
        "version": 1,
        "lanes": [
            {
                "lane": "ecg",
                "record_id": ecg_record_id,
                "lead_index": lead_index,
                "tokens": [list(token) for token in encoded_ecg.tokens],
                "start_value": encoded_ecg.start_value,
                "threshold": encoded_ecg.threshold,
                "step": encoded_ecg.step,
                "num_samples": encoded_ecg.num_samples,
            },
            {
                "lane": "eeg_mental",
                "source_mode": eeg_metrics["mode"],
                "backend": eeg_metrics["backend"],
                "channel_count": eeg_metrics["channel_count"],
                "total_words": eeg_metrics["total_words"],
                "channels": hash_safe_eeg_channels,
            },
        ],
    }
    stream_hash = _canon_hash(lane_payload)

    replay_hash = _canon_hash(lane_payload)
    replay_stable = stream_hash == replay_hash

    min_len = min(ecg_loaded["signal"].shape[0], decoded_ecg.shape[0])
    ecg_prd = float(compute_prd(ecg_loaded["signal"][:min_len], decoded_ecg[:min_len]))

    return {
        "stream_version": 1,
        "lane_count": len(lane_payload["lanes"]),
        "stream_hash": stream_hash,
        "replay_hash": replay_hash,
        "replay_hash_stable": replay_stable,
        "ecg_lane": {
            "record_id": ecg_record_id,
            "samples": int(ecg_loaded["signal"].shape[0]),
            "tokens": int(encoded_ecg.num_tokens),
            "prd_percent": round(ecg_prd, 6),
            "compression_ratio": ecg_metrics["compression_ratio"],
        },
        "eeg_lane": {
            "mode": eeg_metrics["mode"],
            "backend": eeg_metrics["backend"],
            "channel_count": eeg_metrics["channel_count"],
            "total_words": eeg_metrics["total_words"],
            "all_channels_direction_match": all(
                row["quantized_direction_match"] for row in eeg_metrics["channels"]
            ),
        },
        "aggregate": {
            "total_words": int(eeg_metrics["total_words"] + encoded_ecg.num_tokens),
            "total_samples": int(ecg_loaded["signal"].shape[0] + (eeg_channels * eeg_samples)),
        },
    }


def chemosense_bio_demo() -> dict[str, Any]:
    smell_strokes = [synthetic_sniff_stroke(category) for category in OdorCategory]
    smell_words = pack_odor_strokes(smell_strokes, metadata={"sniff_hz": 8})
    smell_meta, smell_decoded = unpack_odor_words(smell_words)

    taste_strokes = [synthetic_taste_stroke_8phase(quality) for quality in TasteQuality]
    taste_words = pack_taste_strokes(taste_strokes)
    _taste_meta, taste_decoded = unpack_taste_words(taste_words)

    flavor_event = zlayered_event_from_vector(
        quality_vector=synthetic_quality_profiles()[TasteQuality.UMAMI],
        flavor_link=(2, 1),
    )
    zlayer_words = pack_taste_zlayered([flavor_event], adaptive=True)
    _z_meta, zlayer_decoded = unpack_taste_zlayered(zlayer_words)

    payload = {
        "mode": "chemosense-bio",
        "smell": {
            "word_count": len(smell_words),
            "stroke_count": len(smell_decoded),
            "metadata": smell_meta,
        },
        "taste": {
            "word_count": len(taste_words),
            "stroke_count": len(taste_decoded),
            "zlayer_word_count": len(zlayer_words),
            "zlayer_event_count": len(zlayer_decoded),
            "flavor_link_present": bool(zlayer_decoded and zlayer_decoded[0].flavor_link is not None),
            "claim_status": "runtime_measured_no_clinical_claim",
        },
    }
    payload["stream_hash"] = _canon_hash(payload)
    return payload
