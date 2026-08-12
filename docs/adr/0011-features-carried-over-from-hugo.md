---
status: accepted
---
# Search, Links Hub and social cards carry over; Now, Projects and contributions do not

The Hugo site has features the template has no equivalent for. Three are carried
into stometa.dev — full-text search, the `/links` hub, and per-post social cards
— and three are deliberately dropped: the "What I'm doing now" section, the
Projects directory, and the GitHub contributions graph.

## Consequences

- **Search** was a static JSON index built at compile time. Against D1 it becomes
  a real query. SQLite FTS5 with a CJK-capable tokenizer is the candidate;
  standard tokenizers do not segment Chinese, so this needs deliberate choice and
  testing rather than a default.
- **Social cards** are the expensive one. Four card images per post exist today,
  generated outside the site. On Workers this needs either an image pipeline
  (satori/resvg in WASM) or Cloudflare Browser Rendering. It is a subsystem, not
  a setting, and should be scoped as such.
- **Dropping Projects** is partly forced: `data/projects.yaml` lists
  **stometa.top** as a project, which this migration deletes. Dropping "Now"
  removes a section already stale (stamped 2026-04-10). Both were maintenance
  the author was not doing, and an unmaintained section reads as neglect — the
  exact impression the redesign exists to remove.
