---
status: accepted
---
# Markdown is the storage format; rich mode must prove it is lossless

Posts are stored as markdown. Both a raw markdown editor and a rich-text editor
are offered per post, because code-heavy technical writing and prose 随笔 want
different surfaces. The round-trip `markdown → HTML → turndown → markdown` is
lossy. **Corrected 2026-08-11 by testing the template's actual markdown-it and
turndown configs:** fenced code blocks *with* language hints round-trip
unchanged; **markdown tables do not** — turndown emits plain paragraphs and the
table structure is destroyed on the first save, not gradually. Tables, raw HTML
(disabled on input) and exact whitespace are the real hazards.

## Consequences

Rich mode is therefore **refused rather than discouraged**: toggling a post to
rich mode first runs the round-trip and blocks if the trip is lossy, showing the
diff it would have caused. Revisions cover the residual risk.

**Corrected 2026-08-11 — the comparison is semantic, not textual.** This ADR
originally specified a byte-identical comparison of the markdown. Measured
against the real configs, byte comparison fails for **every** input, including
`## 标题` and a plain link: turndown legitimately re-spaces list markers
(`- a` → `-   a`) and normalises punctuation without changing meaning. A
byte-identical gate is not a gate, it is a permanent refusal.

The gate therefore compares **re-rendered HTML**: `md → html₁`, then
`html₁ → turndown → md′ → html₂`. Rich mode is permitted iff `html₁ == html₂`,
i.e. the trip is *semantically* lossless even where the markdown text differs
cosmetically. Measured results: fenced code with language hints, nested lists,
footnotes, block HTML, CJK and links all pass; **tables** (structure destroyed
into paragraphs) and **blockquotes** (internal line breaks collapsed) fail.
