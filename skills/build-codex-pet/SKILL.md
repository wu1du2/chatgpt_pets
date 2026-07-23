---
name: build-codex-pet
description: Create custom Codex desktop pets from user-provided DIY or original pet photos through staged character, action, and direction reviews; generate chroma-key assets, assemble and validate a version-2 sprite atlas, install it under ~/.codex/pets, and optionally package it for GitHub. Use when a user asks to turn a handmade puppet, plush, toy, drawing, or other original pet reference into a Codex desktop pet, revise one of its animation poses, resume an interrupted pet project, or validate/install an existing Codex pet pack.
---

# Build Codex Pet

Create an installable pet through explicit review gates. Use the image-generation model only for new visual content; perform cropping, chroma removal, mirroring, frame layout, WebP encoding, validation, and installation locally.

## Non-negotiable generation gate

Before every image-generation call, satisfy all of these requirements:

1. Confirm truthfully that the reference is user-DIY, user-owned original, or otherwise legitimately described as original. If this is not true, stop; never relabel a protected-character-copy request as original.
2. Ensure the exact request submitted to the image model contains no copyright-protected character name, franchise name, celebrity name, or nonessential third-party brand name. Keep the pet's user-facing ID and display name outside the model prompt when either may match a protected name.
3. Explicitly describe the subject as a user-DIY or original pet and identify it by observable traits: animal or shape, material, color, proportions, clothing, seams, wear, expression, and camera angle. Do not identify it as a particular copyrighted character.
4. Do not use disguised spellings, translations, split words, code words, or indirect comparisons to hide a protected name.
5. Run `scripts/lint_generation_request.py` against the final model-bound prompt. Do not call the image-generation tool unless the linter exits successfully.
6. Record the rights basis, exact submitted prompt, excluded-name count, and successful lint result in the project state before generation.

Read `references/moderation-handling.md` before the first generation request and whenever a request returns `moderation_blocked`.

Example preflight:

```bash
python scripts/lint_generation_request.py \
  --rights-basis user-diy-original \
  --excluded-name '<protected name omitted from model prompt>' \
  --prompt 'Create a turntable of the user-provided DIY green terry-cloth frog puppet pet with long legs and a white handmade shirt.'
```

The excluded name is supplied only to the local linter. It must not occur in the prompt submitted to the image model.

## Project state

Create one project directory and keep all approved artifacts inside it. Maintain a state file containing:

```json
{
  "petId": "example-pet",
  "displayName": "Example Pet",
  "rightsBasis": "user-diy-original",
  "approved": {
    "anchor": false,
    "actions": false,
    "cardinals": false,
    "directions": false,
    "atlas": false
  },
  "generationAudit": {},
  "moderationEvents": []
}
```

Never regenerate an approved stage after interruption. Resume from the first unapproved stage.

## Review workflow

### 1. Audit references

- Inspect every local reference image before generation.
- Separate user-facing names from the physical description used by the model.
- Write the truthful DIY/original description and run the mandatory generation gate.

### 2. Generate the character anchor

- Use the existing `imagegen` skill and follow its complete instructions.
- Generate one neutral full-body front view first.
- Preserve material, proportions, clothing, wear, and expression.
- Present the anchor to the user and wait for explicit approval.
- Do not generate action or direction boards before approval.

Use the anchor template in `references/prompt-templates.md`.

### 3. Generate and review the action board

Create exactly nine actions in a 3 × 3 board:

```text
idle | walk right | walk left
wave | jump       | sad or overwhelmed
celebrate | work  | think
```

Present the board for review. If one pose fails, regenerate only that pose and replace only that cell. Verify pixels outside the target cell remain unchanged.

### 4. Generate and review directions

Generate four cardinal views first: front, right, back, and left. After approval, generate a 16-direction clockwise turntable. Validate:

- continuous rotation without duplicate angles;
- full body and feet inside every view;
- consistent material, proportions, clothing, and lighting;
- no front-only label showing through the back;
- no clipped final row.

Use a flat chroma-key background selected to avoid the subject color. For green pets, prefer `#FF00FF`.

### 5. Remove chroma and assemble locally

Use the imagegen skill's installed chroma-removal helper. Validate alpha, transparent corners, subject coverage, and edge fringing.

Place approved transparent boards at:

```text
work/actions/action-board-v2-alpha.png
review/angles/directions-16-v1.png
```

Build the atlas:

```bash
python scripts/build_spritesheet.py \
  --project <project-directory> \
  --pet-id <pet-id>
```

Read `references/atlas-v2-spec.md` for row meanings and frame counts.

### 6. Create the manifest and validate

Create `dist/<pet-id>/pet.json` with `id`, `displayName`, `description`, `spriteVersionNumber: 2`, and `spritesheetPath: spritesheet.webp`.

Validate before installation:

```bash
python scripts/validate_pet.py <project-directory>/dist/<pet-id>
```

Do not install a pet that fails validation.

### 7. Install and optionally publish

- Install only after atlas review: copy the pet directory to `~/.codex/pets/<pet-id>`.
- Compare source and installed hashes.
- Never overwrite another pet ID.
- If the user requests GitHub publication, use the GitHub publishing skill and stage only the requested pet directories.

## `moderation_blocked`

Treat `moderation_blocked` as a diagnosed failure, not a retry loop:

- Record the request ID, input/output stage, and categories exactly.
- Never retry the unchanged request.
- Re-run the truthful rights and naming gate against the actual submitted prompt.
- Retry at most once after a substantive, honest clarification or simpler composition.
- Stop after a second block and report the request ID for support or appeal.
- Never obfuscate names or switch models merely to probe or evade the classifier.

Follow the full procedure in `references/moderation-handling.md`.

## Resource map

- `scripts/lint_generation_request.py`: mandatory fail-closed prompt preflight.
- `scripts/build_spritesheet.py`: deterministic version-2 atlas builder.
- `scripts/validate_pet.py`: manifest, size, alpha, and transparency validation.
- `references/moderation-handling.md`: mandatory rights, naming, logging, retry, and stop rules.
- `references/prompt-templates.md`: name-free DIY pet prompt templates.
- `references/atlas-v2-spec.md`: atlas geometry, rows, and active-frame counts.
