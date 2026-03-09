#!/usr/bin/env python3
"""Benchmark transplanted multimodal smell/taste/touch/mental/fusion hot paths."""

from __future__ import annotations

import argparse
import json
import statistics
import time
import tracemalloc
from typing import Callable, Dict

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
    FusionScheduler,
    TasteQuality,
    pack_taste_zlayered,
    synthetic_quality_profiles,
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


def _bench(fn: Callable[[], None], iterations: int) -> Dict[str, float]:
    tracemalloc.start()
    samples_ms: list[float] = []

    for _ in range(iterations):
        t0 = time.perf_counter()
        fn()
        samples_ms.append((time.perf_counter() - t0) * 1000.0)

    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "mean_ms": round(statistics.fmean(samples_ms), 6),
        "p95_ms": round(sorted(samples_ms)[int(0.95 * (len(samples_ms) - 1))], 6),
        "max_ms": round(max(samples_ms), 6),
        "peak_kb": round(peak / 1024.0, 3),
    }


def _smell_workload() -> None:
    strokes = [synthetic_sniff_stroke(category) for category in OdorCategory]
    words = pack_odor_strokes(strokes, metadata={"sniff_hz": 8})
    _meta, recovered = unpack_odor_words(words)
    if len(recovered) != len(strokes):
        raise RuntimeError("smell roundtrip mismatch")


def _taste_workload() -> None:
    event = zlayered_event_from_vector(
        quality_vector=synthetic_quality_profiles()[TasteQuality.UMAMI],
        temporal_directions=(1, 1, 0, 0, 0, 7, 6, 6),
        flavor_link=(3, 2),
    )
    words = pack_taste_zlayered([event], adaptive=True)
    # Lazy import to keep module import path hot path clear.
    from zpe_bio.multimodal.taste import unpack_taste_zlayered

    _meta, decoded = unpack_taste_zlayered(words)
    if len(decoded) != 1:
        raise RuntimeError("taste roundtrip mismatch")


def _touch_workload() -> None:
    stroke = TouchStroke(
        commands=[TouchMoveTo(0, 0), TouchDrawDir(0), TouchDrawDir(6), TouchDrawDir(4)],
        receptor=ReceptorType.SA_I,
        region=BodyRegion.PALM_CENTER,
        pressure_profile=[2, 3, 2],
    )
    words = pack_touch_strokes([stroke])
    _touch_meta, decoded = unpack_touch_words(words)
    if len(decoded) != 1:
        raise RuntimeError("touch roundtrip mismatch")

    frame_words = pack_timed_simultaneous_frame(
        frame_id=3,
        contacts=[stroke],
        deltas_ms=[12],
    )
    timed_meta, timed_decoded = unpack_timed_simultaneous_frame(frame_words)
    if not timed_meta["cooccurrence_preserved"] or len(timed_decoded) != 1:
        raise RuntimeError("touch timed frame mismatch")


def _mental_workload() -> None:
    strokes = [
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

    rle_words = pack_mental_strokes(strokes, metadata={"use_rle": True})
    raw_words = pack_mental_strokes(strokes, metadata={"use_rle": False})
    _rle_meta, rle_decoded = unpack_mental_words(rle_words)
    _raw_meta, raw_decoded = unpack_mental_words(raw_words)
    if len(rle_decoded) != len(strokes) or len(raw_decoded) != len(strokes):
        raise RuntimeError("mental roundtrip mismatch")


def _fusion_workload() -> None:
    taste_event = zlayered_event_from_vector(
        quality_vector=synthetic_quality_profiles()[TasteQuality.SWEET],
        temporal_directions=(0, 0, 2, 2, 4, 4, 6, 6),
        flavor_link=(1, 1),
    )
    taste_words = pack_taste_zlayered([taste_event], adaptive=True)
    smell_words = pack_odor_strokes([synthetic_sniff_stroke(OdorCategory.FRUITY)])
    touch_words = [
        (0b10 << 18) | (1 << 16) | (0x0800 | 0x001F),
        (0b10 << 18) | (0 << 16) | (0x0800 | 0x0020),
        (0b10 << 18) | (0 << 16) | (0x0800 | 0x0030),
    ]

    scheduler = FusionScheduler()
    stats = scheduler.ingest_stream(taste_words + smell_words + touch_words)
    fused = scheduler.fuse_zlayer_events()
    if stats["taste_packets"] != 1 or stats["smell_packets"] != 1 or stats["touch_packets"] != 1:
        raise RuntimeError("fusion packet extraction mismatch")
    if len(fused) != 1:
        raise RuntimeError("fusion event mismatch")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark multimodal code paths with threshold checks.")
    parser.add_argument("--iterations", type=int, default=200)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--max-smell-ms", type=float, default=None)
    parser.add_argument("--max-taste-ms", type=float, default=None)
    parser.add_argument("--max-touch-ms", type=float, default=None)
    parser.add_argument("--max-mental-ms", type=float, default=None)
    parser.add_argument("--max-fusion-ms", type=float, default=None)
    parser.add_argument("--max-peak-kb", type=float, default=None)
    return parser


def _enforce_threshold(name: str, metric: float, limit: float | None) -> None:
    if limit is None:
        return
    if metric > limit:
        raise SystemExit(f"{name} threshold exceeded: {metric:.6f} > {limit:.6f}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.iterations < 1:
        raise SystemExit("iterations must be >= 1")

    result = {
        "iterations": args.iterations,
        "smell": _bench(_smell_workload, args.iterations),
        "taste": _bench(_taste_workload, args.iterations),
        "touch": _bench(_touch_workload, args.iterations),
        "mental": _bench(_mental_workload, args.iterations),
        "fusion": _bench(_fusion_workload, args.iterations),
    }

    _enforce_threshold("smell.mean_ms", result["smell"]["mean_ms"], args.max_smell_ms)
    _enforce_threshold("taste.mean_ms", result["taste"]["mean_ms"], args.max_taste_ms)
    _enforce_threshold("touch.mean_ms", result["touch"]["mean_ms"], args.max_touch_ms)
    _enforce_threshold("mental.mean_ms", result["mental"]["mean_ms"], args.max_mental_ms)
    _enforce_threshold("fusion.mean_ms", result["fusion"]["mean_ms"], args.max_fusion_ms)
    if args.max_peak_kb is not None:
        for key in ("smell", "taste", "touch", "mental", "fusion"):
            _enforce_threshold(f"{key}.peak_kb", result[key]["peak_kb"], args.max_peak_kb)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            "iters={iterations} smell_mean={smell[mean_ms]}ms taste_mean={taste[mean_ms]}ms "
            "touch_mean={touch[mean_ms]}ms mental_mean={mental[mean_ms]}ms "
            "fusion_mean={fusion[mean_ms]}ms".format(**result)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
