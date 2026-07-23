#!/usr/bin/env python3
"""Fail closed when a DIY pet image request misses the required prompt guardrails."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


DIY_MARKERS = (
    "diy",
    "handmade",
    "home-made",
    "homemade",
    "user-made",
    "user made",
    "self-made",
    "original pet",
    "原创",
    "自制",
    "手作",
    "自己做",
)

PET_MARKERS = (
    "pet",
    "puppet",
    "plush",
    "doll",
    "toy",
    "桌宠",
    "宠物",
    "布偶",
    "玩偶",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a model-bound DIY pet image-generation prompt."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--prompt", help="Prompt text to validate")
    source.add_argument("--prompt-file", type=Path, help="UTF-8 prompt file")
    parser.add_argument(
        "--rights-basis",
        required=True,
        choices=("user-diy-original", "user-owned-original"),
        help="Truthful rights basis confirmed before generation",
    )
    parser.add_argument(
        "--excluded-name",
        action="append",
        default=[],
        help="Protected or third-party proper name that must not occur in the submitted prompt",
    )
    return parser.parse_args()


def contains_term(text: str, term: str) -> bool:
    if not term.strip():
        return False
    escaped = re.escape(term.strip())
    return re.search(rf"(?<!\w){escaped}(?!\w)", text, flags=re.IGNORECASE) is not None


def main() -> int:
    args = parse_args()
    prompt = args.prompt if args.prompt is not None else args.prompt_file.read_text("utf-8")
    normalized = prompt.casefold()
    errors: list[str] = []

    if not prompt.strip():
        errors.append("prompt is empty")
    if not any(marker in normalized for marker in DIY_MARKERS):
        errors.append("prompt must truthfully identify the subject as DIY, handmade, or original")
    if not any(marker in normalized for marker in PET_MARKERS):
        errors.append("prompt must identify the subject as a pet, puppet, plush, doll, or toy")

    leaked_names = [name for name in args.excluded_name if contains_term(prompt, name)]
    if leaked_names:
        errors.append(
            "submitted prompt contains excluded protected proper name(s): "
            + ", ".join(leaked_names)
        )

    result = {
        "ok": not errors,
        "rights_basis": args.rights_basis,
        "diy_or_original_marker": any(marker in normalized for marker in DIY_MARKERS),
        "pet_marker": any(marker in normalized for marker in PET_MARKERS),
        "excluded_name_count": len(args.excluded_name),
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
