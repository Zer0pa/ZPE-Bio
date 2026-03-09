"""Regression tests for transplanted smell codec modules."""

from __future__ import annotations

from zpe_bio.multimodal.smell import (
    OdorCategory,
    augmented_signature,
    descriptor_to_tree_ops_safe,
    pack_augmented_records,
    pack_odor_strokes,
    profile_to_augmented_record,
    synthetic_sniff_stroke,
    unpack_augmented_words,
    unpack_odor_words,
)


def test_smell_pack_unpack_roundtrip_and_type_bits() -> None:
    strokes = [synthetic_sniff_stroke(category) for category in OdorCategory]
    words = pack_odor_strokes(strokes, metadata={"sniff_hz": 8})
    metadata, recovered = unpack_odor_words(words)

    assert metadata == {"sniff_hz": 8}
    assert len(recovered) == len(strokes)

    for src, dst in zip(strokes, recovered):
        assert src.category == dst.category
        assert src.pleasantness_start == dst.pleasantness_start
        assert src.intensity_start == dst.intensity_start
        assert [cmd.direction for cmd in src.commands[1:]] == [cmd.direction for cmd in dst.commands[1:]]

    for word in words:
        assert (word & 0x0200) != 0
        assert (word & (0x8000 | 0x4000 | 0x2000 | 0x1000 | 0x0800)) == 0


def test_smell_augmented_roundtrip_and_chirality_distinction() -> None:
    l_profile = {
        "name": "L-carvone",
        "category": "MINTY_CAMPHOR",
        "quality": [0.10, 0.10, 0.05, 0.20, 0.85],
        "complexity": 0.55,
        "chirality": "L",
    }
    d_profile = {
        "name": "D-carvone",
        "category": "SPICY_HERBAL",
        "quality": [0.10, 0.25, 0.15, 0.75, 0.20],
        "complexity": 0.55,
        "chirality": "D",
    }

    l_record = profile_to_augmented_record(l_profile)
    d_record = profile_to_augmented_record(d_profile)

    l_roundtrip = unpack_augmented_words(pack_augmented_records([l_record]))[0]
    d_roundtrip = unpack_augmented_words(pack_augmented_records([d_record]))[0]

    assert augmented_signature(l_roundtrip) != augmented_signature(d_roundtrip)
    assert l_roundtrip.chirality != d_roundtrip.chirality


def test_molecular_bridge_safe_fallback() -> None:
    fallback = (1, 2, 3)
    descriptor = {
        "molecular_weight": 0.0,
        "vapor_pressure_kpa": 0.0,
        "functional_groups": [],
    }
    assert descriptor_to_tree_ops_safe(descriptor, fallback=fallback) == fallback
