"""Command line interface for the ZPE-Bio codec."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

from zpe_bio import __version__
from zpe_bio.bio_wave2 import (
    DependencyError,
    InputError,
    SourceError,
    Wave2Error,
    benchmark_ecg_records,
    build_multimodal_stream,
    chemosense_bio_demo,
    ecg_roundtrip_metrics,
    encode_eeg_to_mental,
    load_mitbih_record,
)
from zpe_bio.codec import CodecMode, compute_prd, decode, encode


def _roundtrip(args: argparse.Namespace) -> int:
    t = np.linspace(0.0, 2.0 * np.pi, num=args.samples, dtype=np.float64)
    signal = np.sin(t)

    encoded = encode(
        signal,
        mode=CodecMode(args.mode),
        thr_mode=args.thr_mode,
        threshold=args.threshold,
        step=args.step,
        signal_type=args.signal_type,
    )
    reconstructed = decode(encoded)
    prd = compute_prd(signal, reconstructed)

    result = {
        "mode": encoded.mode.value,
        "thr_mode": encoded.thr_mode,
        "samples": encoded.num_samples,
        "tokens": encoded.num_tokens,
        "compression_ratio": round(encoded.compression_ratio, 4),
        "prd_percent": round(prd, 4),
        "threshold": encoded.threshold,
        "step": encoded.step,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            "mode={mode} thr_mode={thr_mode} samples={samples} tokens={tokens} "
            "cr={compression_ratio}x prd={prd_percent}% threshold={threshold} step={step}".format(
                **result
            )
        )

    return 0


def _version(_args: argparse.Namespace) -> int:
    print(__version__)
    return 0


def _emit_result(args: argparse.Namespace, payload: dict[str, Any]) -> int:
    output_path = getattr(args, "output", None)
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload, sort_keys=True))
    return 0


def _emit_error(
    args: argparse.Namespace,
    code: str,
    message: str,
    remediation: str | None = None,
) -> int:
    payload = {
        "ok": False,
        "error": {
            "code": code,
            "message": message,
            "remediation": remediation,
        },
    }
    output_path = getattr(args, "output", None)
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2))
    else:
        print(f"{code}: {message}", file=sys.stderr)
        if remediation:
            print(f"remediation: {remediation}", file=sys.stderr)
    return 1


def _default_eeg_path() -> Path | None:
    roots: list[Path] = []
    env_root = os.getenv("ZPE_BIO_EEG_DIR")
    if env_root:
        roots.append(Path(env_root).expanduser())
    roots.extend(
        [
            Path.cwd() / "validation" / "datasets" / "eeg",
            Path(__file__).resolve().parents[2] / "validation" / "datasets" / "eeg",
        ]
    )
    candidates: list[Path] = []
    for root in roots:
        candidates.extend(
            [
                root / "SC4001E0-PSG.edf",
                root / "chb01_01.edf",
            ]
        )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _encode_ecg(args: argparse.Namespace) -> int:
    try:
        loaded = load_mitbih_record(
            record_id=args.record_id,
            lead_index=args.lead_index,
            max_samples=args.samples,
            dataset_dir=Path(args.dataset_dir) if args.dataset_dir else None,
        )
        encoded, _decoded, metrics = ecg_roundtrip_metrics(
            loaded["signal"],
            mode=CodecMode(args.mode),
            thr_mode=args.thr_mode,
            threshold=args.threshold,
            step=args.step,
        )
        payload = {
            "ok": True,
            "command": "encode-ecg",
            "record_id": args.record_id,
            "lead_index": args.lead_index,
            "sample_rate_hz": loaded["sample_rate_hz"],
            "metrics": metrics,
            "mode": encoded.mode.value,
            "thr_mode": encoded.thr_mode,
        }
        return _emit_result(args, payload)
    except Wave2Error as exc:
        remediation = None
        if isinstance(exc, DependencyError):
            remediation = ".venv/bin/python -m pip install -e '.[validation]'"
        return _emit_error(args, exc.code, exc.message, remediation=remediation)
    except Exception as exc:  # pragma: no cover - defensive path
        return _emit_error(args, "WAVE2_UNHANDLED", str(exc))


def _encode_eeg(args: argparse.Namespace) -> int:
    edf_path: Path | None = Path(args.edf) if args.edf else None
    if edf_path is None and not args.synthetic_eeg:
        edf_path = _default_eeg_path()

    try:
        metrics = encode_eeg_to_mental(
            edf_path=edf_path,
            max_channels=args.channels,
            max_samples=args.samples,
            synthetic=args.synthetic_eeg,
        )
        payload = {
            "ok": True,
            "command": "encode-eeg",
            "metrics": metrics,
        }
        return _emit_result(args, payload)
    except Wave2Error as exc:
        remediation = None
        if isinstance(exc, DependencyError):
            remediation = ".venv/bin/python -m pip install mne pyedflib"
        if isinstance(exc, SourceError):
            remediation = (
                "curl -fL -o validation/datasets/eeg/chb01_01.edf "
                "https://physionet.org/files/chbmit/1.0.0/chb01/chb01_01.edf"
            )
        return _emit_error(args, exc.code, exc.message, remediation=remediation)
    except Exception as exc:  # pragma: no cover - defensive path
        return _emit_error(args, "WAVE2_UNHANDLED", str(exc))


def _benchmark(args: argparse.Namespace) -> int:
    try:
        if args.lane == "ecg":
            record_ids = [item.strip() for item in args.record_ids.split(",") if item.strip()]
            if not record_ids:
                raise InputError("record-ids must include at least one MIT-BIH id")
            payload = {
                "ok": True,
                "command": "benchmark",
                "lane": "ecg",
                "result": benchmark_ecg_records(
                    record_ids=record_ids,
                    lead_index=args.lead_index,
                    samples=args.samples,
                    mode=CodecMode(args.mode),
                    thr_mode=args.thr_mode,
                    threshold=args.threshold,
                    step=args.step,
                    dataset_dir=Path(args.dataset_dir) if args.dataset_dir else None,
                ),
            }
            return _emit_result(args, payload)

        edf_path: Path | None = Path(args.edf) if args.edf else None
        if edf_path is None and not args.synthetic_eeg:
            edf_path = _default_eeg_path()
        payload = {
            "ok": True,
            "command": "benchmark",
            "lane": "eeg",
            "result": encode_eeg_to_mental(
                edf_path=edf_path,
                max_channels=args.channels,
                max_samples=args.samples,
                synthetic=args.synthetic_eeg,
            ),
        }
        return _emit_result(args, payload)
    except Wave2Error as exc:
        remediation = None
        if isinstance(exc, DependencyError):
            remediation = ".venv/bin/python -m pip install mne pyedflib"
        return _emit_error(args, exc.code, exc.message, remediation=remediation)
    except Exception as exc:  # pragma: no cover - defensive path
        return _emit_error(args, "WAVE2_UNHANDLED", str(exc))


def _multimodal_stream_cmd(args: argparse.Namespace) -> int:
    edf_path: Path | None = Path(args.edf) if args.edf else None
    if edf_path is None and not args.synthetic_eeg:
        edf_path = _default_eeg_path()

    try:
        payload = {
            "ok": True,
            "command": "multimodal-stream",
            "result": build_multimodal_stream(
                ecg_record_id=args.record_id,
                lead_index=args.lead_index,
                ecg_samples=args.ecg_samples,
                eeg_path=edf_path,
                eeg_channels=args.eeg_channels,
                eeg_samples=args.eeg_samples,
                synthetic_eeg=args.synthetic_eeg,
            ),
        }
        return _emit_result(args, payload)
    except Wave2Error as exc:
        return _emit_error(args, exc.code, exc.message)
    except Exception as exc:  # pragma: no cover - defensive path
        return _emit_error(args, "WAVE2_UNHANDLED", str(exc))


def _chemosense_bio(args: argparse.Namespace) -> int:
    try:
        payload = {
            "ok": True,
            "command": "chemosense-bio",
            "result": chemosense_bio_demo(),
        }
        return _emit_result(args, payload)
    except Exception as exc:  # pragma: no cover - defensive path
        return _emit_error(args, "WAVE2_UNHANDLED", str(exc))


def _multimodal_smoke(args: argparse.Namespace) -> int:
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
        augmented_signature,
        pack_augmented_records,
        pack_odor_strokes,
        profile_to_augmented_record,
        synthetic_sniff_stroke,
        unpack_augmented_words,
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
    from zpe_bio.multimodal.touch import (
        BodyRegion,
        DrawDir as TouchDrawDir,
        MoveTo as TouchMoveTo,
        ReceptorType,
        TouchStroke,
        pack_timed_simultaneous_frame,
        pack_touch_strokes,
        unpack_timed_simultaneous_frame,
        unpack_touch_words,
    )

    smell_strokes = [synthetic_sniff_stroke(category) for category in OdorCategory]
    smell_words = pack_odor_strokes(smell_strokes, metadata={"sniff_hz": 8})
    smell_meta, smell_decoded = unpack_odor_words(smell_words)

    augmented_profile = {
        "name": "limonene_reference",
        "category": "FRUITY",
        "quality": [0.2, 0.8, 0.1, 0.1, 0.1],
        "complexity": 0.45,
        "chirality": "L",
        "molecular_descriptors": {
            "molecular_weight": 136.24,
            "vapor_pressure_kpa": 0.19,
            "functional_groups": ["alkene", "terpene"],
        },
    }
    augmented_record = profile_to_augmented_record(augmented_profile)
    augmented_words = pack_augmented_records([augmented_record])
    augmented_decoded = unpack_augmented_words(augmented_words)

    taste_strokes = [synthetic_taste_stroke_8phase(quality) for quality in TasteQuality]
    taste_words = pack_taste_strokes(taste_strokes)
    _taste_meta, taste_decoded = unpack_taste_words(taste_words)

    sweet_event = zlayered_event_from_vector(
        quality_vector=synthetic_quality_profiles()[TasteQuality.SWEET],
        flavor_link=(1, 2),
    )
    zlayer_words = pack_taste_zlayered([sweet_event], adaptive=True)
    _z_meta, zlayer_decoded = unpack_taste_zlayered(zlayer_words)

    touch_stroke = TouchStroke(
        commands=[TouchMoveTo(0, 0), TouchDrawDir(0), TouchDrawDir(6), TouchDrawDir(4)],
        receptor=ReceptorType.SA_I,
        region=BodyRegion.PALM_CENTER,
        pressure_profile=[2, 3, 2],
    )
    touch_words = pack_touch_strokes([touch_stroke])
    touch_meta, touch_decoded = unpack_touch_words(touch_words)

    touch_timed_words = pack_timed_simultaneous_frame(
        frame_id=7,
        contacts=[touch_stroke],
        deltas_ms=[12],
    )
    touch_timed_meta, touch_timed_decoded = unpack_timed_simultaneous_frame(touch_timed_words)

    mental_strokes = [
        MentalStroke(
            commands=[
                MentalMoveTo(10, 10),
                MentalDrawDir(0, profile=DirectionProfile.COMPASS_8),
                MentalDrawDir(2, profile=DirectionProfile.COMPASS_8),
                MentalDrawDir(4, profile=DirectionProfile.COMPASS_8),
                MentalDrawDir(6, profile=DirectionProfile.COMPASS_8),
            ],
            form_class=FormClass.LATTICE,
            symmetry=SymmetryOrder.D4,
            direction_profile=DirectionProfile.COMPASS_8,
            spatial_frequency=4,
            drift_speed=1,
            delta_ms=16,
        ),
        MentalStroke(
            commands=[
                MentalMoveTo(12, 12),
                MentalDrawDir(0, profile=DirectionProfile.D6_12),
                MentalDrawDir(2, profile=DirectionProfile.D6_12),
                MentalDrawDir(4, profile=DirectionProfile.D6_12),
                MentalDrawDir(6, profile=DirectionProfile.D6_12),
                MentalDrawDir(8, profile=DirectionProfile.D6_12),
                MentalDrawDir(10, profile=DirectionProfile.D6_12),
            ],
            form_class=FormClass.SPIRAL,
            symmetry=SymmetryOrder.D6,
            direction_profile=DirectionProfile.D6_12,
            spatial_frequency=5,
            drift_speed=2,
            delta_ms=24,
        ),
    ]
    mental_words_rle = pack_mental_strokes(mental_strokes, metadata={"use_rle": True})
    mental_words_raw = pack_mental_strokes(mental_strokes, metadata={"use_rle": False})
    mental_meta_rle, mental_decoded_rle = unpack_mental_words(mental_words_rle)
    mental_meta_raw, mental_decoded_raw = unpack_mental_words(mental_words_raw)

    result = {
        "smell_word_count": len(smell_words),
        "smell_stroke_count": len(smell_decoded),
        "smell_metadata": smell_meta,
        "smell_roundtrip_ok": len(smell_decoded) == len(smell_strokes),
        "smell_augmented_word_count": len(augmented_words),
        "smell_augmented_signature": list(augmented_signature(augmented_decoded[0])),
        "taste_word_count": len(taste_words),
        "taste_stroke_count": len(taste_decoded),
        "taste_roundtrip_ok": len(taste_decoded) == len(taste_strokes),
        "taste_zlayer_word_count": len(zlayer_words),
        "taste_zlayer_count": len(zlayer_decoded),
        "taste_zlayer_has_flavor_link": zlayer_decoded[0].flavor_link is not None,
        "touch_word_count": len(touch_words),
        "touch_stroke_count": len(touch_decoded),
        "touch_metadata": touch_meta,
        "touch_roundtrip_ok": len(touch_decoded) == 1,
        "touch_timed_word_count": len(touch_timed_words),
        "touch_timed_contact_count": len(touch_timed_decoded),
        "touch_timed_cooccurrence_ok": touch_timed_meta["cooccurrence_preserved"],
        "mental_rle_word_count": len(mental_words_rle),
        "mental_raw_word_count": len(mental_words_raw),
        "mental_rle_metadata": mental_meta_rle,
        "mental_raw_metadata": mental_meta_raw,
        "mental_rle_roundtrip_ok": len(mental_decoded_rle) == len(mental_strokes),
        "mental_raw_roundtrip_ok": len(mental_decoded_raw) == len(mental_strokes),
        "mental_profile_roundtrip_ok": [
            stroke.direction_profile for stroke in mental_decoded_rle
        ]
        == [stroke.direction_profile for stroke in mental_strokes],
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            "smell_words={smell_word_count} smell_strokes={smell_stroke_count} "
            "aug_words={smell_augmented_word_count} taste_words={taste_word_count} "
            "taste_strokes={taste_stroke_count} zlayer_words={taste_zlayer_word_count}".format(
                **result
            )
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zpe-bio",
        description="CLI for ZPE-Bio deterministic biosignal compression.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    roundtrip = subparsers.add_parser(
        "roundtrip",
        help="Run encode/decode on a synthetic signal and print compression/fidelity metrics.",
    )
    roundtrip.add_argument(
        "--mode",
        choices=[mode.value for mode in CodecMode],
        default=CodecMode.CLINICAL.value,
    )
    roundtrip.add_argument("--thr-mode", choices=["fixed", "adaptive_rms"], default="fixed")
    roundtrip.add_argument("--threshold", type=float, default=None)
    roundtrip.add_argument("--step", type=float, default=None)
    roundtrip.add_argument("--signal-type", choices=["ecg", "ppg"], default="ecg")
    roundtrip.add_argument("--samples", type=int, default=250)
    roundtrip.add_argument("--json", action="store_true")
    roundtrip.set_defaults(func=_roundtrip)

    version = subparsers.add_parser("version", help="Print package version.")
    version.set_defaults(func=_version)

    multimodal = subparsers.add_parser(
        "multimodal",
        help="Run a multimodal smell/taste/touch/mental encode-decode smoke check.",
    )
    multimodal.add_argument("--json", action="store_true")
    multimodal.set_defaults(func=_multimodal_smoke)

    encode_ecg = subparsers.add_parser(
        "encode-ecg",
        help="Encode/decode an MIT-BIH ECG record and emit roundtrip metrics.",
    )
    encode_ecg.add_argument("--record-id", default="100")
    encode_ecg.add_argument("--lead-index", type=int, default=0)
    encode_ecg.add_argument("--samples", type=int, default=3600)
    encode_ecg.add_argument("--mode", choices=[mode.value for mode in CodecMode], default=CodecMode.CLINICAL.value)
    encode_ecg.add_argument("--thr-mode", choices=["fixed", "adaptive_rms"], default="adaptive_rms")
    encode_ecg.add_argument("--threshold", type=float, default=None)
    encode_ecg.add_argument("--step", type=float, default=None)
    encode_ecg.add_argument("--dataset-dir", default=None)
    encode_ecg.add_argument("--json", action="store_true")
    encode_ecg.add_argument("--output", default=None)
    encode_ecg.set_defaults(func=_encode_ecg)

    encode_eeg = subparsers.add_parser(
        "encode-eeg",
        help="Encode EEG windows into deterministic mental-lane streams.",
    )
    encode_eeg.add_argument("--edf", default=None, help="Path to EDF/BDF file.")
    encode_eeg.add_argument("--synthetic-eeg", action="store_true")
    encode_eeg.add_argument("--channels", type=int, default=2)
    encode_eeg.add_argument("--samples", type=int, default=2048)
    encode_eeg.add_argument("--json", action="store_true")
    encode_eeg.add_argument("--output", default=None)
    encode_eeg.set_defaults(func=_encode_eeg)

    benchmark = subparsers.add_parser(
        "benchmark",
        help="Run lane benchmark outputs (raw/gzip/zpe, PRD, latency).",
    )
    benchmark.add_argument("--lane", choices=["ecg", "eeg"], default="ecg")
    benchmark.add_argument("--record-ids", default="100,103,114,200,223")
    benchmark.add_argument("--lead-index", type=int, default=0)
    benchmark.add_argument("--samples", type=int, default=3600)
    benchmark.add_argument("--mode", choices=[mode.value for mode in CodecMode], default=CodecMode.CLINICAL.value)
    benchmark.add_argument("--thr-mode", choices=["fixed", "adaptive_rms"], default="adaptive_rms")
    benchmark.add_argument("--threshold", type=float, default=None)
    benchmark.add_argument("--step", type=float, default=None)
    benchmark.add_argument("--dataset-dir", default=None)
    benchmark.add_argument("--edf", default=None)
    benchmark.add_argument("--synthetic-eeg", action="store_true")
    benchmark.add_argument("--channels", type=int, default=2)
    benchmark.add_argument("--json", action="store_true")
    benchmark.add_argument("--output", default=None)
    benchmark.set_defaults(func=_benchmark)

    multimodal_stream = subparsers.add_parser(
        "multimodal-stream",
        help="Encode/decode ECG+EEG in one unified stream contract.",
    )
    multimodal_stream.add_argument("--record-id", default="100")
    multimodal_stream.add_argument("--lead-index", type=int, default=0)
    multimodal_stream.add_argument("--ecg-samples", type=int, default=3600)
    multimodal_stream.add_argument("--edf", default=None)
    multimodal_stream.add_argument("--synthetic-eeg", action="store_true")
    multimodal_stream.add_argument("--eeg-channels", type=int, default=2)
    multimodal_stream.add_argument("--eeg-samples", type=int, default=2048)
    multimodal_stream.add_argument("--json", action="store_true")
    multimodal_stream.add_argument("--output", default=None)
    multimodal_stream.set_defaults(func=_multimodal_stream_cmd)

    chemosense = subparsers.add_parser(
        "chemosense-bio",
        help="Run combined smell+taste chemosense demo metrics.",
    )
    chemosense.add_argument("--json", action="store_true")
    chemosense.add_argument("--output", default=None)
    chemosense.set_defaults(func=_chemosense_bio)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # Allow in-process callers (tests/scripts) to assert exit codes
        # without bubbling argparse's SystemExit.
        code = exc.code
        return int(code) if isinstance(code, int) else 1
    return args.func(args)
