from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .types import DirectionProfile, DrawDir, FormClass, MentalStroke, MoveTo, SymmetryOrder


@dataclass(frozen=True)
class IngestResult:
    stroke: MentalStroke
    used_fallback: bool
    rationale: str


_FORM_KEYWORDS: dict[FormClass, tuple[str, ...]] = {
    FormClass.TUNNEL: (
        "tunnel",
        "funnel",
        "concentric",
        "radial",
        "rays",
        "converging",
    ),
    FormClass.SPIRAL: (
        "spiral",
        "helical",
        "rotating",
        "coil",
        "vortex",
        "swirl",
    ),
    FormClass.LATTICE: (
        "lattice",
        "checkerboard",
        "grid",
        "honeycomb",
        "hexagon",
        "hexagonal",
        "zigzag",
        "fortification",
        "tiling",
    ),
    FormClass.COBWEB: (
        "cobweb",
        "filigree",
        "branch",
        "branching",
        "tree",
        "spiderweb",
        "web",
    ),
}


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def infer_form_class(description: str) -> tuple[FormClass, bool, str]:
    text = _normalize(description)

    best_class = FormClass.COBWEB
    best_score = 0
    for form_class, keywords in _FORM_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_class = form_class
            best_score = score

    if best_score == 0:
        return FormClass.COBWEB, True, "no keyword match; fallback to COBWEB"

    return best_class, False, f"matched {best_score} keyword(s)"


def infer_symmetry(description: str, form_class: FormClass) -> SymmetryOrder:
    text = _normalize(description)

    if any(token in text for token in ("hexagon", "hexagonal", "honeycomb", "tiling")):
        return SymmetryOrder.D6
    if form_class == FormClass.LATTICE:
        return SymmetryOrder.D2
    if form_class == FormClass.COBWEB:
        return SymmetryOrder.D4
    return SymmetryOrder.D4


def infer_profile(symmetry: SymmetryOrder) -> DirectionProfile:
    if symmetry == SymmetryOrder.D6:
        return DirectionProfile.D6_12
    return DirectionProfile.COMPASS_8


def _base_directions(
    form_class: FormClass,
    profile: DirectionProfile,
    chirality: int = 1,
) -> list[int]:
    if profile == DirectionProfile.D6_12:
        if form_class == FormClass.TUNNEL:
            return [0, 0, 6, 6, 0, 0, 6, 6]
        if form_class == FormClass.SPIRAL:
            step = 1 if chirality >= 0 else -1
            return [((i * step) % 12) for i in range(12)]
        if form_class == FormClass.LATTICE:
            return [0, 2, 4, 6, 8, 10, 0, 6]
        return [0, 1, 11, 2, 6, 7, 5, 9]

    if form_class == FormClass.TUNNEL:
        return [0, 0, 4, 4, 0, 0, 4, 4]
    if form_class == FormClass.SPIRAL:
        step = 1 if chirality >= 0 else -1
        return [((i * step) % 8) for i in range(8)]
    if form_class == FormClass.LATTICE:
        return [0, 0, 2, 2, 4, 4, 6, 6]
    return [0, 1, 0, 3, 4, 3, 6, 7]


def ingest_clinical_entry(
    entry: Mapping[str, object],
    center: tuple[int, int] = (128, 128),
) -> IngestResult:
    description = str(entry.get("description", ""))
    form_class, used_fallback, rationale = infer_form_class(description)
    symmetry = infer_symmetry(description, form_class)
    profile = infer_profile(symmetry)

    chirality = 1
    text = _normalize(description)
    if "counter-clockwise" in text or "ccw" in text:
        chirality = -1

    directions = _base_directions(form_class, profile, chirality=chirality)
    commands = [MoveTo(center[0], center[1])] + [
        DrawDir(d, profile=profile) for d in directions
    ]

    stroke = MentalStroke(
        commands=commands,
        form_class=form_class,
        symmetry=symmetry,
        direction_profile=profile,
        spatial_frequency=4,
        drift_speed=1,
        frame_index=None,
        delta_ms=0,
    )
    return IngestResult(stroke=stroke, used_fallback=used_fallback, rationale=rationale)


def ingest_clinical_dataset(
    entries: Iterable[Mapping[str, object]],
    center: tuple[int, int] = (128, 128),
) -> list[IngestResult]:
    return [ingest_clinical_entry(entry, center=center) for entry in entries]
