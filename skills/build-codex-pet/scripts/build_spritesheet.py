#!/usr/bin/env python3
"""Build a Codex pet sprite atlas from approved review boards."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw


CELL_W = 192
CELL_H = 208
COLS = 8
ROWS = 11
ROW_NAMES = (
    "idle",
    "walk-right",
    "walk-left",
    "wave",
    "jump",
    "sad",
    "celebrate",
    "work",
    "think",
    "turn-right",
    "turn-left",
)
ROW_COUNTS = (7, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8)


@dataclass(frozen=True)
class Transform:
    angle: float = 0.0
    lift: int = 0
    dx: int = 0
    scale: float = 1.0


def _runs(values: list[bool], minimum: int = 6) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for index, value in enumerate(values + [False]):
        if value and start is None:
            start = index
        elif not value and start is not None:
            if index - start >= minimum:
                runs.append((start, index))
            start = None
    return runs


def _projection_bands(alpha: Image.Image, axis: str, expected: int) -> list[tuple[int, int]]:
    mask = alpha.point(lambda value: 255 if value > 8 else 0)
    width, height = mask.size
    pixels = mask.load()
    if axis == "y":
        values = [any(pixels[x, y] for x in range(width)) for y in range(height)]
    else:
        values = [any(pixels[x, y] for y in range(height)) for x in range(width)]
    bands = _runs(values)
    if len(bands) != expected:
        raise RuntimeError(f"Expected {expected} {axis}-bands, found {len(bands)}: {bands}")
    return bands


def extract_grid(board: Image.Image, rows: int, cols: int) -> list[list[Image.Image]]:
    """Split a transparent contact sheet by the actual subject gaps."""
    board = board.convert("RGBA")
    alpha = board.getchannel("A")
    y_bands = _projection_bands(alpha, "y", rows)
    result: list[list[Image.Image]] = []

    for y0, y1 in y_bands:
        row_alpha = alpha.crop((0, y0, board.width, y1))
        x_bands = _projection_bands(row_alpha, "x", cols)
        row: list[Image.Image] = []
        for x0, x1 in x_bands:
            tile = board.crop((x0, y0, x1, y1))
            bbox = tile.getchannel("A").getbbox()
            if bbox is None:
                raise RuntimeError("Encountered an empty contact-sheet cell")
            left = max(0, bbox[0] - 2)
            top = max(0, bbox[1] - 2)
            right = min(tile.width, bbox[2] + 2)
            bottom = min(tile.height, bbox[3] + 2)
            row.append(tile.crop((left, top, right, bottom)))
        result.append(row)
    return result


def mirrored(image: Image.Image) -> Image.Image:
    return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def render_sprite(
    source: Image.Image,
    base_scale: float,
    transform: Transform = Transform(),
) -> Image.Image:
    """Place one source pose into a 192x208 Codex frame."""
    source = source.convert("RGBA")
    scale = base_scale * transform.scale
    width = max(1, round(source.width * scale))
    height = max(1, round(source.height * scale))
    sprite = source.resize((width, height), Image.Resampling.LANCZOS)
    if transform.angle:
        sprite = sprite.rotate(
            transform.angle,
            resample=Image.Resampling.BICUBIC,
            expand=True,
        )

    frame = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    x = (CELL_W - sprite.width) // 2 + transform.dx
    baseline = CELL_H - 4 - transform.lift
    y = baseline - sprite.height
    frame.alpha_composite(sprite, (x, y))
    return frame


def action_scale(actions: list[Image.Image]) -> float:
    idle_height = actions[0].height
    return min(
        188 / idle_height,
        180 / max(image.width for image in actions),
        194 / max(image.height for image in actions),
    )


def direction_scale(directions: list[Image.Image]) -> float:
    return min(
        188 / directions[0].height,
        180 / max(image.width for image in directions),
        194 / max(image.height for image in directions),
    )


def build_rows(actions: list[Image.Image], directions: list[Image.Image]) -> list[list[Image.Image]]:
    a_scale = action_scale(actions)
    d_scale = direction_scale(directions)

    idle_motion = (
        Transform(),
        Transform(angle=-0.25, lift=1, scale=1.002),
        Transform(lift=1, scale=1.004),
        Transform(angle=0.25, lift=1, scale=1.002),
        Transform(),
        Transform(angle=-0.2, scale=0.998),
        Transform(),
    )
    idle = [render_sprite(actions[0], a_scale, motion) for motion in idle_motion]

    right_a = actions[1]
    right_b = mirrored(actions[2])
    left_a = actions[2]
    left_b = mirrored(actions[1])
    walk_motion = (
        Transform(angle=-0.8),
        Transform(angle=0.8, lift=3),
        Transform(angle=-0.4, lift=1),
        Transform(angle=0.8, lift=3),
        Transform(angle=-0.8),
        Transform(angle=0.8, lift=3),
        Transform(angle=-0.4, lift=1),
        Transform(angle=0.8, lift=3),
    )
    walk_right = [
        render_sprite(right_a if index % 2 == 0 else right_b, a_scale, motion)
        for index, motion in enumerate(walk_motion)
    ]
    walk_left = [
        render_sprite(left_a if index % 2 == 0 else left_b, a_scale, motion)
        for index, motion in enumerate(walk_motion)
    ]

    wave = [
        render_sprite(actions[0], a_scale),
        render_sprite(actions[3], a_scale, Transform(angle=-0.5, lift=1)),
        render_sprite(actions[3], a_scale, Transform(angle=0.7, lift=2)),
        render_sprite(actions[3], a_scale, Transform(angle=-0.3, lift=1)),
    ]

    jump = [
        render_sprite(actions[0], a_scale, Transform(scale=0.99)),
        render_sprite(actions[4], a_scale, Transform(lift=16, angle=-0.6)),
        render_sprite(actions[4], a_scale, Transform(lift=34)),
        render_sprite(actions[4], a_scale, Transform(lift=18, angle=0.6)),
        render_sprite(actions[0], a_scale, Transform(scale=0.99)),
    ]

    sad_motion = (
        (actions[0], Transform()),
        (actions[5], Transform(angle=-0.4, scale=0.985)),
        (actions[5], Transform(angle=0.3, scale=0.98)),
        (actions[5], Transform(lift=-1, scale=0.975)),
        (actions[5], Transform(angle=-0.3, lift=-1, scale=0.975)),
        (actions[5], Transform(angle=0.3, scale=0.98)),
        (actions[5], Transform(angle=-0.2, scale=0.985)),
        (actions[0], Transform()),
    )
    sad = [render_sprite(image, a_scale, motion) for image, motion in sad_motion]

    celebrate_motion = (
        (actions[0], Transform()),
        (actions[6], Transform(lift=7, angle=-0.8)),
        (actions[6], Transform(lift=16, angle=0.6)),
        (actions[6], Transform(lift=10, angle=-0.4)),
        (actions[6], Transform(lift=5, angle=0.4)),
        (actions[0], Transform()),
    )
    celebrate = [render_sprite(image, a_scale, motion) for image, motion in celebrate_motion]

    work_motion = (
        Transform(angle=-0.5),
        Transform(angle=0.3, lift=1),
        Transform(angle=-0.2),
        Transform(angle=0.4, lift=1),
        Transform(angle=-0.3),
        Transform(),
    )
    work = [render_sprite(actions[7], a_scale, motion) for motion in work_motion]

    think_motion = (
        Transform(),
        Transform(angle=-0.8, dx=-1),
        Transform(angle=-1.2, dx=-1, lift=1),
        Transform(angle=-0.6),
        Transform(angle=0.3, dx=1),
        Transform(),
    )
    think = [render_sprite(actions[8], a_scale, motion) for motion in think_motion]

    # The approved sheet supplies complete 0°, 22.5°, 45°, 67.5° and 90° views.
    # Repeat intermediate poses to fill Codex's eight-frame turning rows. The left
    # row is mirrored from the complete right row so no clipped source is used.
    turn_sources = (directions[0], directions[1], directions[1], directions[2],
                    directions[2], directions[3], directions[3], directions[4])
    turn_right = [render_sprite(image, d_scale) for image in turn_sources]
    turn_left = [render_sprite(mirrored(image), d_scale) for image in turn_sources]

    rows = [idle, walk_right, walk_left, wave, jump, sad, celebrate, work, think, turn_right, turn_left]
    for name, expected, frames in zip(ROW_NAMES, ROW_COUNTS, rows):
        if len(frames) != expected:
            raise RuntimeError(f"{name}: expected {expected} frames, got {len(frames)}")
    return rows


def checker_preview(atlas: Image.Image) -> Image.Image:
    background = Image.new("RGB", atlas.size, (34, 37, 42))
    draw = ImageDraw.Draw(background)
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2:
                draw.rectangle(
                    (col * CELL_W, row * CELL_H, (col + 1) * CELL_W - 1, (row + 1) * CELL_H - 1),
                    fill=(47, 51, 58),
                )
    background.paste(atlas, mask=atlas.getchannel("A"))
    return background


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--pet-id", required=True)
    args = parser.parse_args()
    project = args.project.resolve()

    actions_board = Image.open(project / "work/actions/action-board-v2-alpha.png")
    directions_board = Image.open(project / "review/angles/directions-16-v1.png")
    actions_grid = extract_grid(actions_board, 3, 3)
    directions_grid = extract_grid(directions_board, 4, 4)
    actions = [image for row in actions_grid for image in row]

    # Only these five complete views are needed by the Codex directional rows.
    directions = [
        directions_grid[0][0],
        directions_grid[0][1],
        directions_grid[0][2],
        directions_grid[0][3],
        directions_grid[1][0],
    ]
    rows = build_rows(actions, directions)

    atlas = Image.new("RGBA", (CELL_W * COLS, CELL_H * ROWS), (0, 0, 0, 0))
    frames_dir = project / "build/frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for row_index, (name, frames) in enumerate(zip(ROW_NAMES, rows)):
        for col_index, frame in enumerate(frames):
            atlas.alpha_composite(frame, (col_index * CELL_W, row_index * CELL_H))
            frame.save(frames_dir / f"{row_index:02d}-{name}-{col_index:02d}.png")

    build_png = project / "build/spritesheet.png"
    dist_webp = project / f"dist/{args.pet_id}/spritesheet.webp"
    preview = project / f"review/final/{args.pet_id}-spritesheet-preview.jpg"
    build_png.parent.mkdir(parents=True, exist_ok=True)
    dist_webp.parent.mkdir(parents=True, exist_ok=True)
    preview.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(build_png)
    atlas.save(dist_webp, "WEBP", lossless=True, method=6)
    checker_preview(atlas).save(preview, "JPEG", quality=92, subsampling=0)

    alpha = atlas.getchannel("A")
    if alpha.getpixel((0, 0)) != 0 or alpha.getpixel((atlas.width - 1, atlas.height - 1)) != 0:
        raise RuntimeError("Atlas corners are not transparent")
    if alpha.getbbox() is None:
        raise RuntimeError("Atlas contains no visible pixels")

    print(f"actions={len(actions)} directions={len(directions)}")
    print(f"atlas={atlas.width}x{atlas.height} mode={atlas.mode}")
    print(f"frames={sum(ROW_COUNTS)} active of {COLS * ROWS} slots")
    print(f"wrote {build_png}")
    print(f"wrote {dist_webp}")
    print(f"wrote {preview}")


if __name__ == "__main__":
    main()
