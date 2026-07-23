# ChatGPT / Codex Pets

Custom desktop-pet sprite packs for Codex.

## Included pets

- `kermit` — green handmade cloth frog puppet
- `pingu` — cheerful clay penguin

Each pet directory contains:

- `pet.json` — Codex pet manifest
- `spritesheet.webp` — transparent 8 × 11 animation atlas

## Install

Copy either pet directory into `~/.codex/pets/`:

```bash
mkdir -p ~/.codex/pets
cp -R pets/kermit ~/.codex/pets/
cp -R pets/pingu ~/.codex/pets/
```

Restart Codex if the pet picker is already open.

These custom assets are intended for personal, non-commercial use.

## Included skill

- `build-codex-pet` — staged DIY pet generation, review, sprite-atlas
  assembly, validation, and installation

Install the skill with:

```bash
mkdir -p ~/.codex/skills
cp -R skills/build-codex-pet ~/.codex/skills/
```
