#!/usr/bin/env python3
"""Validate a version-2 Codex pet manifest and sprite atlas."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pet_dir", type=Path)
    args = parser.parse_args()
    pet_dir = args.pet_dir.resolve()
    manifest_path = pet_dir / "pet.json"
    manifest = json.loads(manifest_path.read_text("utf-8"))
    atlas_path = pet_dir / manifest.get("spritesheetPath", "")
    image = Image.open(atlas_path)
    errors: list[str] = []

    if not manifest.get("id"):
        errors.append("pet.json id is required")
    if not manifest.get("displayName"):
        errors.append("pet.json displayName is required")
    if manifest.get("spriteVersionNumber") != 2:
        errors.append("spriteVersionNumber must be 2")
    if image.size != (1536, 2288):
        errors.append(f"spritesheet must be 1536x2288, got {image.size}")
    if "A" not in image.getbands():
        errors.append("spritesheet must contain an alpha channel")
    else:
        alpha = image.getchannel("A")
        if alpha.getbbox() is None:
            errors.append("spritesheet has no visible pixels")
        corners = ((0, 0), (image.width - 1, 0), (0, image.height - 1), (image.width - 1, image.height - 1))
        if any(alpha.getpixel(point) != 0 for point in corners):
            errors.append("all four spritesheet corners must be transparent")

    result = {
        "ok": not errors,
        "pet_dir": str(pet_dir),
        "pet_id": manifest.get("id"),
        "atlas_size": list(image.size),
        "atlas_mode": image.mode,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
