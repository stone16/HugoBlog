# Hugo Square Cover Rendering Proof

## Why this exists

The homepage cards were rendering square social posters (`card1.png`) inside landscape cover slots, which cropped key text off the image.

This branch fixes that by marking generated social-card covers as `contain` on the Hugo side and rendering them with full visibility on list cards.

## Verification

Automated check:

```bash
python3 scripts/check_square_cover_render.py
```

Manual proof screenshots:

- `before-live-first-entry.png`
- `after-local-first-entry.png`
- `before-live-openclaw-card.png`
- `after-local-openclaw-card.png`

## What to compare

1. `before-live-openclaw-card.png` vs `after-local-openclaw-card.png`
   - The live card crops off the top headline.
   - The local fixed card shows the full square poster.

2. `before-live-first-entry.png` vs `after-local-first-entry.png`
   - The featured card keeps the square poster fully visible instead of edge-cropping it.
