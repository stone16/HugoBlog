# Design System — V3 AI Editorial

## Aesthetic
Dark mode editorial publication. Sophisticated, not hacker. Clean, readable, professional.

## Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--accent-1` | `#a855f7` (purple) | Primary accent, badges, hover states |
| `--accent-2` | `#06b6d4` (cyan) | Links, secondary accent, success states |
| `--accent-grad` | `135deg purple → cyan` | Gradients, hover borders, progress bar |
| `--bg-base` | `#08080f` | Page background |
| `--bg-surface` | `#0d0d18` | Code backgrounds |
| `--bg-raised` | `#12121f` | Elevated surfaces, hover bg |
| `--bg-overlay` | `#181828` | Tooltips, overlays |
| `--bg-card` | `#0f0f1c` | Card backgrounds |
| `--text-primary` | `#f0f0f8` | Headings |
| `--text-secondary` | `#8888a8` | Body, descriptions |
| `--text-muted` | `#50506a` | Meta, labels |

## Typography

| Role | Font | Weights |
|------|------|---------|
| Display / Headings | Plus Jakarta Sans | 400-800 |
| Body | Inter | 400-600 |
| Code | JetBrains Mono | 400-600 |

## Spacing & Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | 6px | Small elements, badges |
| `--radius-md` | 10px | Buttons, inputs, code blocks |
| `--radius-lg` | 16px | Cards |
| `--radius-xl` | 24px | Large containers |
| 99px | Pill shapes | Tags, badges |

## Interaction Patterns

- **Cards**: hover → `translateY(-3px)` + `box-shadow: var(--shadow-lg), var(--shadow-glow)` + gradient border
- **Links**: cyan by default, purple on hover
- **Badges**: pill-shaped, uppercase, letter-spaced, dim background
- **Buttons**: `var(--bg-raised)` + `var(--border-default)`, hover brightens
- **Transitions**: `var(--ease)` = `cubic-bezier(0.16, 1, 0.3, 1)` (spring-like)

## Components

### Post Cards
- `var(--bg-card)` background, `var(--border-subtle)` border
- Gradient border on hover (mask-composite trick)
- Cover image with `aspect-ratio: 16/9`
- Featured post: `aspect-ratio: 21/9`, gradient top-border

### Back-to-Top
- 40px rounded square (`--radius-md`), NOT circle
- `var(--bg-raised)` + `var(--border-default)`
- Chevron icon in `--text-muted`

### Progress Bar
- 2px fixed at top, `var(--accent-grad)`
- z-index: 101 (above nav)

### Social Icons
- 36px square containers with `--border-default`
- 18px SVG icons
- Hover: lift + brighten

## Brand Assets
- **Favicon**: Gradient "S" (purple → cyan) on rounded square
- **Company**: ZentaStone (zentastone.com)
- **Twitter**: @stometaverse
