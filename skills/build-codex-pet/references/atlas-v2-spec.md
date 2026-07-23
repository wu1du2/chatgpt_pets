# Codex pet atlas version 2

- Canvas: 1536 × 2288 pixels
- Cell: 192 × 208 pixels
- Grid: 8 columns × 11 rows
- Format: lossless WebP with alpha
- Manifest: `spriteVersionNumber: 2`

| Row | Meaning | Active frames |
| --- | --- | ---: |
| 0 | Idle | 7 |
| 1 | Walk right | 8 |
| 2 | Walk left | 8 |
| 3 | Wave | 4 |
| 4 | Jump | 5 |
| 5 | Sad or overwhelmed | 8 |
| 6 | Celebrate | 6 |
| 7 | Work | 6 |
| 8 | Think | 6 |
| 9 | Turn front to right | 8 |
| 10 | Turn front to left | 8 |

Leave unused cells fully transparent. Require transparent corners, visible-pixel coverage, and a matching `spritesheetPath` in `pet.json`.
