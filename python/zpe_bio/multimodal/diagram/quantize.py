from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple, Union

# Eight cardinal/diagonal directions (R, UR, U, UL, L, DL, D, DR)
DIRS: Tuple[Tuple[int, int], ...] = (
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
)

STYLE_COLORS: Tuple[str, ...] = (
    "#000000",
    "#ffffff",
    "#ff0000",
    "#00ff00",
    "#0000ff",
    "#ffff00",
    "#00ffff",
    "#ff00ff",
)

STYLE_DASHES: Tuple[str, ...] = (
    "solid",
    "dash",
    "dot",
    "dashdot",
)


@dataclass(frozen=True)
class MoveTo:
    x: int
    y: int


@dataclass(frozen=True)
class DrawDir:
    direction: int  # 0-7

    def delta(self) -> Tuple[int, int]:
        dx, dy = DIRS[self.direction]
        return dx, dy


@dataclass
class PolylineShape:
    points: List[Tuple[float, float]]
    stroke: str | None = None
    stroke_width: float | None = None
    fill: str | None = None
    dash: str | None = None


@dataclass
class StrokePath:
    commands: List[Union[MoveTo, DrawDir]]
    stroke: str | None = None
    stroke_width: float | None = None
    fill: str | None = None
    dash: str | None = None


StrokeCommand = Union[MoveTo, DrawDir]


def _normalize_color(color: str | None) -> str:
    if not color:
        return STYLE_COLORS[0]
    c = color.strip().lower()
    if len(c) == 4 and c.startswith("#"):
        # Expand short hex form, e.g. #f0c -> #ff00cc
        c = "#" + "".join(ch * 2 for ch in c[1:])
    return c if c in STYLE_COLORS else STYLE_COLORS[0]


def encode_style(path: StrokePath) -> tuple[int, int, int] | None:
    """Encode style to compact (width, color_idx, dash_idx)."""
    has_style = path.stroke is not None or path.stroke_width is not None or path.dash is not None
    if not has_style:
        return None

    width = int(round(path.stroke_width if path.stroke_width is not None else 1.0))
    width = max(1, min(width, 10))

    color = _normalize_color(path.stroke)
    color_idx = STYLE_COLORS.index(color)

    dash = (path.dash or STYLE_DASHES[0]).strip().lower()
    if dash not in STYLE_DASHES:
        dash = STYLE_DASHES[0]
    dash_idx = STYLE_DASHES.index(dash)

    return width, color_idx, dash_idx


def decode_style(width_code: int, color_idx: int, dash_idx: int) -> dict[str, object]:
    width = float(max(1, min(int(width_code), 10)))
    color = STYLE_COLORS[max(0, min(int(color_idx), len(STYLE_COLORS) - 1))]
    dash = STYLE_DASHES[max(0, min(int(dash_idx), len(STYLE_DASHES) - 1))]
    return {
        "stroke_width": width,
        "stroke": color,
        "dash": dash,
    }


def quantize_polylines(polylines: Sequence[PolylineShape]) -> List[PolylineShape]:
    """Snap normalized polylines to integer grid coordinates, preserving style."""
    quantized: List[PolylineShape] = []
    for poly in polylines:
        snapped: List[Tuple[int, int]] = []
        for x, y in poly.points:
            snapped.append((int(round(x)), int(round(y))))

        deduped: List[Tuple[int, int]] = []
        for pt in snapped:
            if not deduped or deduped[-1] != pt:
                deduped.append(pt)

        if len(deduped) >= 2:
            quantized.append(
                PolylineShape(
                    points=deduped,
                    stroke=poly.stroke,
                    stroke_width=poly.stroke_width,
                    fill=poly.fill,
                    dash=poly.dash,
                )
            )
    return quantized


def _direction_for_step(dx: int, dy: int) -> int:
    try:
        return DIRS.index((dx, dy))
    except ValueError as exc:
        raise ValueError(f"invalid step ({dx}, {dy}); expected unit step") from exc


def _emit_segment_steps(commands: List[StrokeCommand], cx: int, cy: int, nx_i: int, ny_i: int) -> tuple[int, int]:
    dx = nx_i - cx
    dy = ny_i - cy
    while dx != 0 or dy != 0:
        step_dx = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_dy = 0 if dy == 0 else (1 if dy > 0 else -1)
        dir_idx = _direction_for_step(step_dx, step_dy)
        commands.append(DrawDir(dir_idx))
        cx += step_dx
        cy += step_dy
        dx = nx_i - cx
        dy = ny_i - cy
    return cx, cy


def polylines_to_strokes(polylines: Sequence[PolylineShape]) -> List[StrokePath]:
    """Convert integer polylines into move + 8-direction draw steps, preserving style."""
    paths: List[StrokePath] = []
    for poly in polylines:
        if len(poly.points) < 2:
            continue
        commands: List[StrokeCommand] = []
        x0, y0 = poly.points[0]
        commands.append(MoveTo(int(x0), int(y0)))
        cx, cy = int(x0), int(y0)
        for nx, ny in poly.points[1:]:
            cx, cy = _emit_segment_steps(commands, cx, cy, int(nx), int(ny))

        paths.append(
            StrokePath(
                commands=commands,
                stroke=poly.stroke,
                stroke_width=poly.stroke_width,
                fill=poly.fill,
                dash=poly.dash,
            )
        )
    return paths


def polylines_to_strokes_liberated(polylines: Sequence[PolylineShape]) -> List[StrokePath]:
    """
    Enhanced construction mode: re-anchor with MoveTo at every control vertex.

    This keeps the same reconstructed geometry but avoids long chained drift when
    later transforms or edits mutate intermediate points.
    """
    paths: List[StrokePath] = []
    for poly in polylines:
        if len(poly.points) < 2:
            continue

        commands: List[StrokeCommand] = []
        for idx in range(len(poly.points) - 1):
            sx, sy = poly.points[idx]
            ex, ey = poly.points[idx + 1]
            sx_i, sy_i = int(sx), int(sy)
            ex_i, ey_i = int(ex), int(ey)

            commands.append(MoveTo(sx_i, sy_i))
            _, _ = _emit_segment_steps(commands, sx_i, sy_i, ex_i, ey_i)

        paths.append(
            StrokePath(
                commands=commands,
                stroke=poly.stroke,
                stroke_width=poly.stroke_width,
                fill=poly.fill,
                dash=poly.dash,
            )
        )

    return paths


def strokes_to_polylines(paths: Iterable[StrokePath]) -> List[PolylineShape]:
    """Reconstruct polylines (with style) from stroke paths."""
    out: List[PolylineShape] = []
    for path in paths:
        points: List[Tuple[int, int]] = []
        cx = cy = 0

        for cmd in path.commands:
            if isinstance(cmd, MoveTo):
                if points:
                    out.append(
                        PolylineShape(
                            points=points,
                            stroke=path.stroke,
                            stroke_width=path.stroke_width,
                            fill=path.fill,
                            dash=path.dash,
                        )
                    )
                    points = []
                cx, cy = cmd.x, cmd.y
                points.append((cx, cy))
            elif isinstance(cmd, DrawDir):
                dx, dy = cmd.delta()
                cx += dx
                cy += dy
                points.append((cx, cy))
            else:
                raise TypeError(f"unknown stroke command {cmd!r}")

        if points:
            out.append(
                PolylineShape(
                    points=points,
                    stroke=path.stroke,
                    stroke_width=path.stroke_width,
                    fill=path.fill,
                    dash=path.dash,
                )
            )
    return out
