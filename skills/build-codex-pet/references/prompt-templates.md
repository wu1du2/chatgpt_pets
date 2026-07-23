# Prompt templates

Never place the pet's display name into a model-bound prompt when it is also a protected character name. Refer to it by truthful physical traits instead.

## Character anchor

```text
Create a full-body studio reference image of the user-provided DIY pet.
The subject is a handmade <color> <material> <animal-or-shape> puppet with
<distinctive physical traits>. Preserve its actual seams, wear, proportions,
clothing, and expression. Treat the input as a reference to this specific
user-made physical object, not as a named fictional character.
```

## Action board

```text
Create a 3 by 3 contact sheet of the same user-DIY pet: idle, walk right,
walk left, wave, jump, sad, celebrate, work, and think. Preserve the approved
handmade materials, proportions, clothing, and identity. Exactly one pose per
cell; no labels or extra objects.
```

## Direction board

```text
Create a turntable contact sheet of the same user-DIY pet, rotating clockwise
in equal increments. Preserve its handmade material, proportions, clothing,
wear, and neutral pose. Use a uniform chroma-key background. No labels,
protected character names, franchise names, or unrelated brand names.
```
