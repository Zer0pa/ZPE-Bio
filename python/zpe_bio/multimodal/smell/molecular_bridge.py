from __future__ import annotations

from typing import Any, Iterable, Sequence, Tuple


# Tree op indices aligned to phase5_augment.TreeOp.
TREE_BRANCH_LEFT = 0
TREE_BRANCH_RIGHT = 1
TREE_DESCEND = 2
TREE_ASCEND = 3


PLEASANT_GROUPS = {
    "ester",
    "terpene",
    "alcohol",
    "aldehyde",
    "lactone",
    "ketone",
}

AVERSIVE_GROUPS = {
    "sulfur",
    "thiol",
    "amine",
    "halogen",
    "nitro",
}


def _normalize_groups(groups: Iterable[str] | None) -> set[str]:
    if groups is None:
        return set()
    out = set()
    for token in groups:
        if token is None:
            continue
        out.add(str(token).strip().lower())
    return out


def descriptor_complexity_hint(molecular_weight: float | int, functional_groups: Sequence[str] | None) -> float:
    groups = _normalize_groups(functional_groups)
    mw = float(max(0.0, molecular_weight))

    group_score = min(6.0, float(len(groups))) / 6.0
    weight_score = min(1.0, mw / 220.0)
    aromatic_bonus = 0.15 if "aromatic" in groups else 0.0

    hint = 0.55 * group_score + 0.35 * weight_score + aromatic_bonus
    return max(0.0, min(1.0, hint))


def descriptor_to_tree_ops(
    molecular_weight: float | int,
    vapor_pressure_kpa: float | int,
    functional_groups: Sequence[str] | None,
    pleasant_bias: float | None = None,
) -> Tuple[int, int, int]:
    groups = _normalize_groups(functional_groups)
    mw = float(max(0.0, molecular_weight))
    vapor = float(max(0.0, vapor_pressure_kpa))

    if groups & AVERSIVE_GROUPS:
        op0 = TREE_BRANCH_LEFT
    elif groups & PLEASANT_GROUPS:
        op0 = TREE_BRANCH_RIGHT
    elif pleasant_bias is not None and float(pleasant_bias) >= 4.0:
        op0 = TREE_BRANCH_RIGHT
    else:
        op0 = TREE_BRANCH_LEFT

    op1 = TREE_DESCEND if vapor >= 1.6 else TREE_ASCEND

    complexity_score = len(groups)
    if "aromatic" in groups:
        complexity_score += 1
    if mw >= 150:
        complexity_score += 1

    if complexity_score <= 2:
        op2 = TREE_BRANCH_LEFT
    elif complexity_score <= 4:
        op2 = TREE_BRANCH_RIGHT
    else:
        op2 = TREE_DESCEND

    return op0, op1, op2


def descriptor_to_tree_ops_safe(
    descriptor: dict[str, Any] | None,
    fallback: Tuple[int, int, int],
    pleasant_bias: float | None = None,
) -> Tuple[int, int, int]:
    if not descriptor:
        return fallback

    try:
        molecular_weight = float(descriptor.get("molecular_weight", 0.0))
        vapor_pressure = float(descriptor.get("vapor_pressure_kpa", 0.0))
        groups = descriptor.get("functional_groups", [])
        if not isinstance(groups, list):
            groups = []
    except Exception:
        return fallback

    if molecular_weight <= 0.0 and vapor_pressure <= 0.0 and not groups:
        return fallback

    return descriptor_to_tree_ops(
        molecular_weight=molecular_weight,
        vapor_pressure_kpa=vapor_pressure,
        functional_groups=groups,
        pleasant_bias=pleasant_bias,
    )
