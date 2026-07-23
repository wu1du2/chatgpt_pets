# Moderation handling

Use this procedure for every image-generation request and every `moderation_blocked` error.

## Mandatory truthful preflight

1. Confirm that the referenced pet is genuinely user-DIY, user-owned original, or otherwise truthfully described as original. Never invent this rights basis.
2. Remove copyright-protected character names, franchise names, celebrity names, and nonessential third-party brand names from the prompt submitted to the image model.
3. Describe the subject positively and concretely as a DIY or original pet: species or shape, material, colors, proportions, clothing, wear, expression, and camera angle.
4. Do not say or imply that the subject is a particular protected character. Do not use phrases such as "identical to", "exactly like", or disguised spellings of a protected name.
5. Run `scripts/lint_generation_request.py`. Do not call an image-generation tool unless it exits successfully.
6. Record the exact submitted prompt, rights basis, lint result, and excluded-name count in the project state before generation.

These rules reduce irrelevant false positives; they are not permission to misrepresent a protected-character-copy request as original. If the description would be untrue, stop and ask the user to redesign it as an original pet.

## Required project-state record

```json
{
  "generationAudit": {
    "rightsBasis": "user-diy-original",
    "subjectFraming": "DIY green terry-cloth frog puppet",
    "protectedNamesPresentInSubmittedPrompt": false,
    "excludedNameCount": 1,
    "lintPassed": true,
    "submittedPromptPath": "prompts/directions-16.txt"
  }
}
```

## Handling `moderation_blocked`

1. Record `request_id`, `error.code`, `moderation_stage`, and `categories` exactly as returned.
2. Do not retry the unchanged request.
3. Re-run the mandatory truthful preflight against the actual model-bound prompt and input images.
4. If the block is at the input stage, fix genuine ambiguity or remove nonessential protected names, then lint and retry at most once.
5. If the block is at the output stage and the request already passes preflight, retry at most once with a simpler neutral composition or fewer figures.
6. After a second block, stop. Report the request ID for support or appeal; do not obfuscate names, split words, translate names, encode text, or switch models to probe the classifier.

Local post-processing may add benign user-authorized labels or deterministic layout details. Never use local post-processing to add unsafe content that the generation system blocked.
