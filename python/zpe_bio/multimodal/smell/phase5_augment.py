from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Iterable, List, Sequence, Tuple

from ..core.constants import DEFAULT_VERSION, Mode
from ..diagram.quantize import DrawDir, MoveTo

from .adaptation import AdaptationParams
from .molecular_bridge import descriptor_complexity_hint, descriptor_to_tree_ops_safe
from .odor_space import project_odor_vector3_to_pom, project_quality_vector_to_pom
from .pack import DATA_MASK, OP_HEADER_A, OP_HEADER_B, OP_MASK, OP_META, OP_SHIFT, OP_STEP, SMELL_TYPE_BIT
from .types import OdorCategory, OdorStroke, SmellZLevel


class TreeOp(IntEnum):
    BRANCH_LEFT = 0
    BRANCH_RIGHT = 1
    DESCEND = 2
    ASCEND = 3


DEFAULT_TREE_DEPTH = 3
DEFAULT_COMPLEXITY_BITS = 4
DEFAULT_POM_RESOLUTION = 8

Z_HEADER_MARKER = 0x30
ADAPT_HALF_MARKER = 0x20
ADAPT_FLOOR_MARKER = 0x10


@dataclass(frozen=True)
class AugmentedOdorRecord:
    stroke: OdorStroke
    tree_ops: Tuple[TreeOp, TreeOp, TreeOp]
    complexity_axis: int  # 4-bit axis, 0..15
    chirality: int = 0     # 0/1 physical chirality marker
    label: str | None = None

    def __post_init__(self) -> None:
        if len(self.tree_ops) != 3:
            raise ValueError("tree_ops must have length 3")
        for op in self.tree_ops:
            if not isinstance(op, TreeOp):
                raise TypeError("tree_ops must contain TreeOp values")
        if not 0 <= int(self.complexity_axis) <= 15:
            raise ValueError("complexity_axis must be in [0, 15]")
        if int(self.chirality) not in (0, 1):
            raise ValueError("chirality must be 0 or 1")


def _ext_word(payload: int) -> int:
    return (Mode.EXTENSION.value << 18) | (DEFAULT_VERSION << 16) | (payload & 0xFFFF)


def _payload(op: int, data: int) -> int:
    return SMELL_TYPE_BIT | ((op & OP_MASK) << OP_SHIFT) | (data & DATA_MASK)


def _decode_smell_word(word: int) -> tuple[int, int] | None:
    if not isinstance(word, int):
        return None
    mode = (word >> 18) & 0x3
    version = (word >> 16) & 0x3
    payload = word & 0xFFFF
    if mode != Mode.EXTENSION.value or version != DEFAULT_VERSION:
        return None
    if (payload & SMELL_TYPE_BIT) == 0:
        return None
    op = (payload >> OP_SHIFT) & OP_MASK
    data = payload & DATA_MASK
    return op, data


def _meta_word(data: int) -> int:
    return _ext_word(_payload(OP_META, data & DATA_MASK))


def encode_tree_ops(tree_ops: Sequence[TreeOp]) -> int:
    if len(tree_ops) != 3:
        raise ValueError("tree_ops must have length 3")
    code = 0
    for idx, op in enumerate(tree_ops):
        if not isinstance(op, TreeOp):
            raise TypeError("tree_ops must contain TreeOp values")
        code |= (int(op) & 0x3) << (idx * 2)
    return code & DATA_MASK


def decode_tree_ops(code: int) -> Tuple[TreeOp, TreeOp, TreeOp]:
    c = int(code) & DATA_MASK
    return (
        TreeOp((c >> 0) & 0x3),
        TreeOp((c >> 2) & 0x3),
        TreeOp((c >> 4) & 0x3),
    )


def derive_tree_ops(pleasantness: int, intensity: int, complexity_axis: int) -> Tuple[TreeOp, TreeOp, TreeOp]:
    op0 = TreeOp.BRANCH_RIGHT if pleasantness >= 4 else TreeOp.BRANCH_LEFT
    op1 = TreeOp.DESCEND if intensity >= 4 else TreeOp.ASCEND
    if complexity_axis <= 5:
        op2 = TreeOp.BRANCH_LEFT
    elif complexity_axis <= 10:
        op2 = TreeOp.BRANCH_RIGHT
    else:
        op2 = TreeOp.DESCEND
    return (op0, op1, op2)


def derive_trajectory(quality: Sequence[float], complexity: float) -> List[int]:
    if len(quality) != 5:
        raise ValueError("quality vector must have length 5")

    pleasantness, intensity = project_quality_vector_to_pom(quality)
    dominant = max(range(5), key=lambda idx: quality[idx])
    sorted_idx = sorted(range(5), key=lambda idx: quality[idx], reverse=True)
    secondary = sorted_idx[1]
    dominance_margin = quality[sorted_idx[0]] - quality[sorted_idx[1]]

    dominant_to_dir = {
        0: 1,  # floral
        1: 0,  # fruity
        2: 3,  # spicy
        3: 4,  # woody
        4: 3,  # chemical/putrid
    }

    secondary_to_dir = {
        0: 7,
        1: 0,
        2: 3,
        3: 4,
        4: 5,
    }

    onset = 2 if intensity >= 5 else (1 if intensity >= 3 else 0)
    expressive = dominant_to_dir[dominant]
    complexity_turn = 4 if complexity >= 0.66 else (0 if complexity <= 0.33 else secondary_to_dir[secondary])

    if dominance_margin < 0.08:
        decay = secondary_to_dir[secondary]
    elif pleasantness >= 5 and complexity <= 0.45:
        decay = 7
    elif pleasantness <= 2:
        decay = 5
    else:
        decay = 6

    return [onset, expressive, complexity_turn, decay]


def _parse_category(value: object) -> OdorCategory:
    if isinstance(value, OdorCategory):
        return value
    if isinstance(value, int):
        return OdorCategory(value)
    if isinstance(value, str):
        key = value.strip().upper().replace("-", "_").replace("/", "_").replace(" ", "_")
        if key in OdorCategory.__members__:
            return OdorCategory[key]
    raise ValueError(f"cannot parse category from {value!r}")


def _parse_chirality(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return 1 if value != 0 else 0
    if isinstance(value, str):
        token = value.strip().upper()
        if token in {"L", "R", "+", "LEFT", "1"}:
            return 1
        if token in {"D", "S", "-", "RIGHT", "0", "ACHIRAL", "NONE"}:
            return 0
    return 0


def _descriptor_from_profile(profile: dict) -> dict | None:
    descriptor = profile.get("molecular_descriptors")
    if isinstance(descriptor, dict):
        return descriptor

    keys = {"molecular_weight", "vapor_pressure_kpa", "functional_groups"}
    if keys & set(profile.keys()):
        return {
            "molecular_weight": profile.get("molecular_weight", 0.0),
            "vapor_pressure_kpa": profile.get("vapor_pressure_kpa", 0.0),
            "functional_groups": profile.get("functional_groups", []),
        }
    return None


def _validate_ablation_params(tree_depth: int, complexity_bits: int, pom_resolution: int) -> None:
    if not 1 <= int(tree_depth) <= 4:
        raise ValueError("tree_depth must be in [1, 4]")
    if not 2 <= int(complexity_bits) <= 4:
        raise ValueError("complexity_bits must be in [2, 4]")
    if int(pom_resolution) not in (4, 6, 8):
        raise ValueError("pom_resolution must be one of {4, 6, 8}")


def _quantize_axis_0_7(value_0_7: int, resolution: int) -> int:
    if resolution <= 1:
        return 0
    scaled = (float(value_0_7) / 7.0) * float(resolution - 1)
    return max(0, min(resolution - 1, int(round(scaled))))


def _dequantize_axis_0_7(bin_value: int, resolution: int) -> int:
    if resolution <= 1:
        return 0
    scaled = (float(bin_value) / float(resolution - 1)) * 7.0
    return max(0, min(7, int(round(scaled))))


def _quantize_complexity(complexity: float, complexity_bits: int) -> tuple[int, int]:
    levels = (1 << int(complexity_bits)) - 1
    clipped = max(0.0, min(1.0, float(complexity)))
    idx = max(0, min(levels, int(round(clipped * float(levels)))))
    return idx, levels


def _scale_complexity_to_4bit(bin_value: int, levels: int) -> int:
    if levels <= 0:
        return 0
    scaled = (float(bin_value) / float(levels)) * 15.0
    return max(0, min(15, int(round(scaled))))


def _derive_tree_ops_ablation(
    pleasantness_bin: int,
    intensity_bin: int,
    complexity_bin: int,
    tree_depth: int,
) -> Tuple[TreeOp, ...]:
    op0 = TreeOp.BRANCH_RIGHT if pleasantness_bin >= 4 else TreeOp.BRANCH_LEFT
    op1 = TreeOp.DESCEND if intensity_bin >= 4 else TreeOp.ASCEND

    if complexity_bin <= 5:
        op2 = TreeOp.BRANCH_LEFT
    elif complexity_bin <= 10:
        op2 = TreeOp.BRANCH_RIGHT
    else:
        op2 = TreeOp.DESCEND

    parity = (pleasantness_bin + intensity_bin + complexity_bin) % 2
    op3 = TreeOp.ASCEND if parity == 0 else TreeOp.DESCEND

    ops = (op0, op1, op2, op3)
    depth = max(1, min(4, int(tree_depth)))
    return ops[:depth]


def _normalize_tree_ops_for_record(tree_ops: Sequence[TreeOp]) -> Tuple[TreeOp, TreeOp, TreeOp]:
    if not tree_ops:
        return (TreeOp.ASCEND, TreeOp.ASCEND, TreeOp.ASCEND)
    ops = list(tree_ops)
    while len(ops) < 3:
        ops.append(ops[-1])
    return (ops[0], ops[1], ops[2])


def profile_to_augmented_record(
    profile: dict,
    tree_depth: int = DEFAULT_TREE_DEPTH,
    complexity_bits: int = DEFAULT_COMPLEXITY_BITS,
    pom_resolution: int = DEFAULT_POM_RESOLUTION,
) -> AugmentedOdorRecord:
    _validate_ablation_params(tree_depth, complexity_bits, pom_resolution)

    quality = [float(v) for v in profile["quality"]]
    if len(quality) != 5:
        raise ValueError("quality vector must have length 5")

    complexity = max(0.0, min(1.0, float(profile.get("complexity", 0.5))))
    chirality = _parse_chirality(profile.get("chirality", 0))
    category = _parse_category(profile["category"])
    descriptor = _descriptor_from_profile(profile)

    if descriptor is not None:
        hint = descriptor_complexity_hint(
            molecular_weight=descriptor.get("molecular_weight", 0.0),
            functional_groups=descriptor.get("functional_groups", []),
        )
        complexity = max(0.0, min(1.0, 0.5 * complexity + 0.5 * hint))

    pleasantness_raw, intensity_raw = project_quality_vector_to_pom(quality)
    pleasantness_bin = _quantize_axis_0_7(pleasantness_raw, pom_resolution)
    intensity_bin = _quantize_axis_0_7(intensity_raw, pom_resolution)
    pleasantness = _dequantize_axis_0_7(pleasantness_bin, pom_resolution)
    intensity = _dequantize_axis_0_7(intensity_bin, pom_resolution)

    directions = derive_trajectory(quality, complexity)
    complexity_bin, complexity_levels = _quantize_complexity(complexity, complexity_bits)
    complexity_axis = _scale_complexity_to_4bit(complexity_bin, complexity_levels)
    fallback_ops = _derive_tree_ops_ablation(pleasantness_bin, intensity_bin, complexity_bin, tree_depth)
    bridge_ops = descriptor_to_tree_ops_safe(
        descriptor=descriptor,
        fallback=tuple(int(op) for op in fallback_ops),
        pleasant_bias=float(pleasantness),
    )
    tree_ops = _normalize_tree_ops_for_record(tuple(TreeOp(int(op)) for op in bridge_ops))

    stroke = OdorStroke(
        commands=[MoveTo(pleasantness, 7 - intensity)] + [DrawDir(d) for d in directions],
        category=category,
        pleasantness_start=pleasantness,
        intensity_start=intensity,
    )

    return AugmentedOdorRecord(
        stroke=stroke,
        tree_ops=tree_ops,
        complexity_axis=complexity_axis,
        chirality=chirality,
        label=profile.get("name"),
    )


def vector3_to_augmented_record(
    vector3: Sequence[float],
    category: OdorCategory = OdorCategory.FRUITY,
    tree_depth: int = DEFAULT_TREE_DEPTH,
    complexity_bits: int = DEFAULT_COMPLEXITY_BITS,
    pom_resolution: int = DEFAULT_POM_RESOLUTION,
) -> AugmentedOdorRecord:
    _validate_ablation_params(tree_depth, complexity_bits, pom_resolution)

    if len(vector3) != 3:
        raise ValueError("vector3 must have length 3")

    pleasantness_raw, intensity_raw = project_odor_vector3_to_pom(vector3)
    pleasantness_bin = _quantize_axis_0_7(pleasantness_raw, pom_resolution)
    intensity_bin = _quantize_axis_0_7(intensity_raw, pom_resolution)
    pleasantness = _dequantize_axis_0_7(pleasantness_bin, pom_resolution)
    intensity = _dequantize_axis_0_7(intensity_bin, pom_resolution)

    complexity = max(0.0, min(1.0, float(vector3[2])))
    complexity_bin, complexity_levels = _quantize_complexity(complexity, complexity_bits)
    complexity_axis = _scale_complexity_to_4bit(complexity_bin, complexity_levels)
    tree_ops = _normalize_tree_ops_for_record(
        _derive_tree_ops_ablation(pleasantness_bin, intensity_bin, complexity_bin, tree_depth)
    )

    directions = [
        2,
        0 if pleasantness >= 4 else 4,
        2 if complexity_axis >= 8 else 6,
        6,
    ]

    stroke = OdorStroke(
        commands=[MoveTo(pleasantness, 7 - intensity)] + [DrawDir(d) for d in directions],
        category=category,
        pleasantness_start=pleasantness,
        intensity_start=intensity,
    )

    return AugmentedOdorRecord(
        stroke=stroke,
        tree_ops=tree_ops,
        complexity_axis=complexity_axis,
        chirality=0,
        label=None,
    )


def pack_augmented_records(records: Iterable[AugmentedOdorRecord]) -> List[int]:
    words: List[int] = []
    for record in records:
        stroke = record.stroke
        draw_cmds = [cmd for cmd in stroke.commands[1:] if isinstance(cmd, DrawDir)]

        header_a = _payload(OP_HEADER_A, ((int(stroke.category) & 0x7) << 3) | (stroke.pleasantness_start & 0x7))
        header_b = _payload(OP_HEADER_B, ((stroke.intensity_start & 0x7) << 3) | (len(draw_cmds) & 0x7))
        words.append(_ext_word(header_a))
        words.append(_ext_word(header_b))

        for idx, cmd in enumerate(draw_cmds):
            direction = cmd.direction & 0x7
            phase = min(idx, 3)
            words.append(_ext_word(_payload(OP_STEP, (direction << 3) | phase)))

        tree_code = encode_tree_ops(record.tree_ops)
        words.append(_ext_word(_payload(OP_META, tree_code)))

        chirality_complexity = ((int(record.chirality) & 0x1) << 4) | (int(record.complexity_axis) & 0xF)
        words.append(_ext_word(_payload(OP_META, chirality_complexity)))

    return words


def unpack_augmented_words(words: Iterable[int]) -> List[AugmentedOdorRecord]:
    word_list = list(words)
    records: List[AugmentedOdorRecord] = []

    idx = 0
    while idx < len(word_list):
        parsed = _decode_smell_word(word_list[idx])
        if parsed is None:
            idx += 1
            continue

        op_a, data_a = parsed
        if op_a != OP_HEADER_A or idx + 1 >= len(word_list):
            idx += 1
            continue

        parsed_b = _decode_smell_word(word_list[idx + 1])
        if parsed_b is None:
            idx += 1
            continue

        op_b, data_b = parsed_b
        if op_b != OP_HEADER_B:
            idx += 1
            continue

        category_raw = (data_a >> 3) & 0x7
        pleasantness = data_a & 0x7
        intensity = (data_b >> 3) & 0x7
        step_count = data_b & 0x7

        try:
            category = OdorCategory(category_raw)
        except ValueError:
            idx += 2
            continue

        commands: List[MoveTo | DrawDir] = [MoveTo(pleasantness, 7 - intensity)]

        cursor = idx + 2
        consumed_steps = 0
        while consumed_steps < step_count and cursor < len(word_list):
            parsed_step = _decode_smell_word(word_list[cursor])
            if parsed_step is None:
                break
            op_s, data_s = parsed_step
            if op_s != OP_STEP:
                break
            direction = (data_s >> 3) & 0x7
            commands.append(DrawDir(direction))
            consumed_steps += 1
            cursor += 1

        tree_code = 0
        chirality = 0
        complexity_axis = 0

        parsed_tree = _decode_smell_word(word_list[cursor]) if cursor < len(word_list) else None
        if parsed_tree is not None and parsed_tree[0] == OP_META:
            tree_code = parsed_tree[1]
            cursor += 1

        parsed_cc = _decode_smell_word(word_list[cursor]) if cursor < len(word_list) else None
        if parsed_cc is not None and parsed_cc[0] == OP_META:
            cc_data = parsed_cc[1]
            chirality = (cc_data >> 4) & 0x1
            complexity_axis = cc_data & 0xF
            cursor += 1

        records.append(
            AugmentedOdorRecord(
                stroke=OdorStroke(
                    commands=commands,
                    category=category,
                    pleasantness_start=pleasantness,
                    intensity_start=intensity,
                ),
                tree_ops=decode_tree_ops(tree_code),
                complexity_axis=complexity_axis,
                chirality=chirality,
                label=None,
            )
        )

        idx = cursor

    return records


def pack_z_episode(
    records: Sequence[AugmentedOdorRecord],
    z_level: SmellZLevel = SmellZLevel.INSTANT,
    adaptation: AdaptationParams | None = None,
) -> List[int]:
    if not isinstance(z_level, SmellZLevel):
        raise TypeError("z_level must be a SmellZLevel")

    sniff_count = len(records)
    if sniff_count < 1:
        raise ValueError("records must contain at least one sniff")
    if sniff_count > 4:
        raise ValueError("z-episode supports at most 4 sniffs")

    if adaptation is None:
        adaptation = AdaptationParams(half_life=0, floor=0)

    header_data = Z_HEADER_MARKER | ((int(z_level) & 0x3) << 2) | ((sniff_count - 1) & 0x3)
    words: List[int] = [
        _meta_word(header_data),
        _meta_word(ADAPT_HALF_MARKER | (int(adaptation.half_life) & 0xF)),
        _meta_word(ADAPT_FLOOR_MARKER | (int(adaptation.floor) & 0xF)),
    ]
    words.extend(pack_augmented_records(records))
    return words


def unpack_z_episode(
    words: Iterable[int],
) -> tuple[SmellZLevel, AdaptationParams | None, List[AugmentedOdorRecord]]:
    word_list = list(words)
    if not word_list:
        return SmellZLevel.INSTANT, None, []

    cursor = 0
    sniff_count = None
    z_level = SmellZLevel.INSTANT
    adaptation: AdaptationParams | None = None

    header = _decode_smell_word(word_list[cursor])
    if header is not None and header[0] == OP_META and (header[1] & Z_HEADER_MARKER) == Z_HEADER_MARKER:
        data = header[1]
        z_raw = (data >> 2) & 0x3
        sniff_count = (data & 0x3) + 1
        if z_raw in (SmellZLevel.INSTANT, SmellZLevel.ADAPTATION, SmellZLevel.EPISODIC):
            z_level = SmellZLevel(z_raw)
        cursor += 1

        half = 0
        floor = 0
        half_word = _decode_smell_word(word_list[cursor]) if cursor < len(word_list) else None
        if half_word is not None and half_word[0] == OP_META and (half_word[1] & Z_HEADER_MARKER) == ADAPT_HALF_MARKER:
            half = half_word[1] & 0xF
            cursor += 1

        floor_word = _decode_smell_word(word_list[cursor]) if cursor < len(word_list) else None
        if floor_word is not None and floor_word[0] == OP_META and (floor_word[1] & Z_HEADER_MARKER) == ADAPT_FLOOR_MARKER:
            floor = floor_word[1] & 0xF
            cursor += 1

        adaptation = AdaptationParams(half_life=half, floor=floor)

    records = unpack_augmented_words(word_list[cursor:])
    if sniff_count is not None:
        records = records[:sniff_count]

    return z_level, adaptation, records


def unpack_instant_layer(words: Iterable[int]) -> List[AugmentedOdorRecord]:
    _z, _adapt, records = unpack_z_episode(words)
    return records


def direction_sequence(record: AugmentedOdorRecord) -> Tuple[int, ...]:
    return tuple(cmd.direction for cmd in record.stroke.commands[1:] if isinstance(cmd, DrawDir))


def augmented_signature(record: AugmentedOdorRecord) -> Tuple[int, ...]:
    return (
        int(record.stroke.category),
        record.stroke.pleasantness_start,
        record.stroke.intensity_start,
        *direction_sequence(record),
        encode_tree_ops(record.tree_ops),
        record.complexity_axis,
        int(record.chirality),
    )


def ablation_signature(
    profile: dict,
    tree_depth: int = DEFAULT_TREE_DEPTH,
    complexity_bits: int = DEFAULT_COMPLEXITY_BITS,
    pom_resolution: int = DEFAULT_POM_RESOLUTION,
) -> Tuple[int, ...]:
    _validate_ablation_params(tree_depth, complexity_bits, pom_resolution)

    quality = [float(v) for v in profile["quality"]]
    if len(quality) != 5:
        raise ValueError("quality vector must have length 5")

    complexity = max(0.0, min(1.0, float(profile.get("complexity", 0.5))))
    category = _parse_category(profile["category"])
    chirality = _parse_chirality(profile.get("chirality", 0))

    pleasantness_raw, intensity_raw = project_quality_vector_to_pom(quality)
    pleasantness_bin = _quantize_axis_0_7(pleasantness_raw, pom_resolution)
    intensity_bin = _quantize_axis_0_7(intensity_raw, pom_resolution)

    complexity_bin, _levels = _quantize_complexity(complexity, complexity_bits)
    tree_ops = _derive_tree_ops_ablation(pleasantness_bin, intensity_bin, complexity_bin, tree_depth)
    directions = derive_trajectory(quality, complexity)

    return (
        int(category),
        pleasantness_bin,
        intensity_bin,
        *directions,
        *[int(op) for op in tree_ops],
        complexity_bin,
        chirality,
    )


def estimated_bits_per_event(tree_depth: int, complexity_bits: int) -> int:
    _validate_ablation_params(tree_depth, complexity_bits, DEFAULT_POM_RESOLUTION)
    # Augmentation overhead bits (tree + complexity payload components).
    return (int(tree_depth) * 2) + int(complexity_bits)
