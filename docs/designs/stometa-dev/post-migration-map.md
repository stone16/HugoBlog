# Post migration map: `stometa.top` → `stometa.dev`

Status: migration input for the 14 published files in `content/posts/`, measured on branch `stone16/hugo-improvement` at `ddcd814` on 2026-08-11.

## Decision summary

- Import **11 Chinese posts at the root** and **3 English posts under `/en/`**. Locale is determined from body prose, not title or the site-wide `languageCode`.
- Preserve the **resolved Hugo URL segment**, not the literal filename. Eight posts already have explicit `slug`; six need that resolved segment written into D1 before cutover.
- Install the three English exceptions before the bulk redirect. A bulk redirect alone would strand all three at the Chinese root.
- There are no duplicate resolved slugs among the 14 current files. The hard migration blockers are six missing slugs, six missing `description` fields (one has `summary` instead), one empty category, and one post whose body is a 1,299-line custom HTML/CSS document rather than ordinary Markdown.

## How the current URL is resolved

This is confirmed from the repository and a local Hugo render, rather than inferred from filenames:

1. [`hugo.yaml`](../../../hugo.yaml#L1) sets `baseURL` to `https://stometa.top`, selects PaperMod at [line 4](../../../hugo.yaml#L4), and defines no `permalinks` override. The `posts` section therefore uses Hugo's default `/<section>/<content-basename>/` pattern.
2. PaperMod is pinned as a Git submodule in [`.gitmodules`](../../../.gitmodules#L7) at gitlink commit `3bb0ca281fd17eff8e3489011a444f326d7c4c72`. Its templates consume Hugo's already-resolved `.Permalink` (`layouts/_default/list.html`, `layouts/_default/single.html`, and `layouts/partials/post_meta.html`); the theme does not rewrite post paths. The repository override likewise links with `.Permalink` in [`layouts/index.html`](../../../layouts/index.html#L137).
3. `hugo list all` on Hugo `v0.152.2` emitted the exact URLs recorded below. For a page with frontmatter `slug`, Hugo uses it. Otherwise Hugo URLizes the filename stem: case folds to lowercase, spaces become hyphens, and CJK remains in the path and is percent-encoded in the emitted absolute URL.

The non-obvious case is [`content/posts/BRAR 因子.md`](../../../content/posts/BRAR%20%E5%9B%A0%E5%AD%90.md#L1): it has no `slug`, so the live URL is exactly `https://stometa.top/posts/brar-%E5%9B%A0%E5%AD%90/`. The space is **not** `%20`; Hugo URLizes it to `-` before encoding the Chinese characters.

## Counting method

“Word count” below means countable reading units in body prose after removing YAML frontmatter, fenced-code contents, raw `<style>`/`<script>` blocks, HTML tags, and link destinations. For `zh`, the unit is a Han character and reading time is `ceil(characters / 350)` minutes. For `en`, the unit is an English word and reading time is `ceil(words / 220)` minutes. This makes the estimates comparable and prevents the 500+ lines of embedded CSS in the X article from being presented as reader prose. PaperMod's displayed value is different: `showReadingTime: true` in [`hugo.yaml`](../../../hugo.yaml#L15) delegates to Hugo `.ReadingTime` through PaperMod's `layouts/partials/post_meta.html` at the pinned theme commit.

## Complete inventory

`Slug source` is `explicit` when frontmatter supplies `slug`; otherwise `derived` is the decoded Hugo URL segment that must be persisted in D1. `Cover` reports the frontmatter path and whether `static/<path>` exists.

| Filename | Resolved live URL today | Locale | Title | Date | Slug source → migration slug | Categories | Tags | Description | Cover | Count / reading time | Proposed section | Editorial rationale |
|---|---|---:|---|---|---|---|---|---|---|---|---|---|
| `BRAR 因子.md` | `https://stometa.top/posts/brar-%E5%9B%A0%E5%AD%90/` | zh | BRAR 因子 | 2025-03-04 | derived → `brar-因子` | Quant | FactorAnalysis; quant; 能量型因子 | **missing** | — | 403 zh chars / 2 min | 量化 | Factor definition, signal thresholds, and implementation code; a direct quant reference. |
| `Confirmation Bias.md` | `https://stometa.top/posts/confirmation-bias/` | en | Confirmation Bias | 2025-02-02 | derived → `confirmation-bias` | General | psychology; NoteTaking; 2ndBrain; humanPitfalls | **missing** | — | 132 en words / 1 min | 随笔/思考 | A short personal mental-model note, with no engineering or market method. |
| `Flywheel effect.md` | `https://stometa.top/posts/flywheel-effect/` | en | Flywheel effect | 2025-02-10 | derived → `flywheel-effect` | General | efficiencyBump; routine; psychology | **missing** | — | 164 en words / 1 min | 随笔/思考 | Applies the flywheel metaphor to motivation and learning habits. |
| `Google UCP Goes Live: The Search-to-Checkout Era Begins.md` | `https://stometa.top/posts/google-ucp-goes-live-the-search-to-checkout-era-begins/` | en | Google UCP Goes Live: The Search-to-Checkout Era Begins | 2026-02-13 | derived → `google-ucp-goes-live-the-search-to-checkout-era-begins` | Tech | google; ecommerce; ai-agents; seo; ucp | **missing** (`summary` exists) | — | 627 en words / 3 min | AI 工具 | UCP is an agentic-commerce protocol and platform shift; “AI 工具” is the closest available theme, though the taxonomy should eventually gain “产品/商业”. |
| `cloudflare-resend-unlimited-email-setup.md` | `https://stometa.top/posts/cloudflare-resend-unlimited-email-setup/` | zh | 用 Cloudflare + Resend 打造无限邮箱：一人公司的邮件基础设施 | 2026-03-04T11:48:11.065946+08:00 | explicit → `cloudflare-resend-unlimited-email-setup` | **none** | **none** | present | `/images/cloudflare-resend-unlimited-email-setup/card1.png` — **exists** | 1,444 zh chars / 5 min | 工程实践 | Reproducible Cloudflare, DNS, Resend SMTP, and Gmail setup guide. |
| `conductor-ai-concurrent-development-experience.md` | `https://stometa.top/posts/conductor-ai-concurrent-development-experience/` | zh | Conductor：AI 时代的并发开发体验 | 2026-03-02T08:43:54.128203+08:00 | explicit → `conductor-ai-concurrent-development-experience` | AI工具; 开发效率 | Conductor; Claude Code; AI编程; Git Worktree; 并发开发; Agent编排; 开发工具; 工作流 | present | — | 2,080 zh chars / 6 min | AI 工具 | Product/workflow review centered on parallel coding Agents. |
| `enterprise-background-agent-ramp-stripe.md` | `https://stometa.top/posts/enterprise-background-agent-ramp-stripe/` | zh | 企业级 Background Agent 实践：从概念框架到 Ramp/Stripe 落地 | 2026-03-02T16:01:55.907388+08:00 | explicit → `enterprise-background-agent-ramp-stripe` | AI工具; 技术 | background-agent; coding-agent; MicroVM; Firecracker; Ramp; Stripe; AI基础设施; 沙箱 | present | — | 2,614 zh chars / 8 min | 工程实践 | Architecture-level treatment of isolation, orchestration, feedback, and governance. |
| `from-em-to-ai-agent-manager-career-reflection.md` | `https://stometa.top/posts/from-em-to-ai-agent-manager-career-reflection/` | zh | 从管理团队到管理 AI Agent：一个程序员的裸辞跑路思考 | 2026-03-06T15:37:53.168144+08:00 | explicit → `from-em-to-ai-agent-manager-career-reflection` | AI工具; 创业 | AI Agent; Engineering Manager; 职业转型; 杠杆结构; Claude Code; 独立开发; 裸辞; 程序员 | present | `/images/from-em-to-ai-agent-manager-career-reflection/card1.png` — **exists** | 3,423 zh chars / 10 min | 随笔/思考 | First-person career thesis and decision record; AI is evidence for the reflection, not a tool tutorial. |
| `openclaw-guide-for-indie-developers.md` | `https://stometa.top/posts/openclaw-guide-for-indie-developers/` | zh | OpenClaw 避坑指南：独立开发者的正确打开方式 | 2026-03-18T21:17:10.742391+08:00 | explicit → `openclaw-guide-for-indie-developers` | AI工具; 开发效率 | OpenClaw; 独立开发; SOP; 工作流自动化; AI工具; 效率; Skill | present | `/images/openclaw-guide-for-indie-developers/card1.png` — **exists** | 1,483 zh chars / 5 min | AI 工具 | Opinionated usage guide for turning SOPs into executable Skills. |
| `openclaw-sessions-json-performance-optimization.md` | `https://stometa.top/posts/openclaw-sessions-json-performance-optimization/` | zh | OpenClaw sessions.json 性能优化：从 38MB 到 2.8MB | 2026-03-05T10:55:14.250345+08:00 | explicit → `openclaw-sessions-json-performance-optimization` | 技术; 开发效率 | openclaw; 性能优化; debugging; discord; nodejs; event-loop; infrastructure | present | `/images/openclaw-sessions-json-performance-optimization/card1.png` — **exists** | 534 zh chars / 2 min | 工程实践 | Concrete incident diagnosis, measured root cause, cleanup code, and prevention. |
| `why-yc-ceo-ai-is-10x-better-than-yours.md` | `https://stometa.top/posts/why-yc-ceo-ai-is-10x-better-than-yours/` | zh | 同样用Claude，为什么YC CEO的AI比你好用10倍 | 2026-03-18T20:30:31.734925+08:00 | explicit → `why-yc-ceo-ai-is-10x-better-than-yours` | AI工具; 开发效率 | AI; Prompt工程; Gary Tan; YCombinator; gstack; Claude; 代码审查; AI工作流 | present | `/images/why-yc-ceo-ai-is-10x-better-than-yours/card1.png` — **exists** | 663 zh chars / 2 min | AI 工具 | Skill/prompt teardown aimed at improving AI-assisted review. |
| `x-algorithm-for-you-feed-deep-dive.md` | `https://stometa.top/posts/x-algorithm-for-you-feed-deep-dive/` | zh | X Algorithm Deep Dive — For You Feed 推荐算法全景解析 | 2026-05-16T10:00:00+08:00 | explicit → `x-algorithm-for-you-feed-deep-dive` | 社交媒体; 算法解析 | X/Twitter; 推荐算法; For You Feed; Phoenix; 内容创作; 社交媒体增长; 开源代码分析 | present | — | 3,158 zh chars / 10 min | 工程实践 | Source-driven pipeline and scoring-system analysis, despite its creator-growth application. |
| `氛围编程 vibe coding.md` | `https://stometa.top/posts/%E6%B0%9B%E5%9B%B4%E7%BC%96%E7%A8%8B-vibe-coding/` | zh | 氛围编程 vibe coding | 2025-03-27 | derived → `氛围编程-vibe-coding` | General | AgentAI; projectDevelopment | **missing** | — | 939 zh chars / 3 min | AI 工具 | Early field note on Cursor, rules, prompting, feedback, and Vibe Coding limitations. |
| `资金费率.md` | `https://stometa.top/posts/%E8%B5%84%E9%87%91%E8%B4%B9%E7%8E%87/` | zh | 资金费率 | 2025-04-04 | derived → `资金费率` | Quant | blockchain; 套利; TradeStrategy | **missing** | — | 715 zh chars / 3 min | 量化 | Explains perpetual funding and includes backtest results for a trading strategy. |

Source anchors: every inventory value comes from the respective frontmatter/body, beginning at [`BRAR 因子.md`](../../../content/posts/BRAR%20%E5%9B%A0%E5%AD%90.md#L1), [`Confirmation Bias.md`](../../../content/posts/Confirmation%20Bias.md#L1), [`Flywheel effect.md`](../../../content/posts/Flywheel%20effect.md#L1), [`Google UCP…md`](../../../content/posts/Google%20UCP%20Goes%20Live%3A%20The%20Search-to-Checkout%20Era%20Begins.md#L1), [`cloudflare-resend…md`](../../../content/posts/cloudflare-resend-unlimited-email-setup.md#L1), [`conductor…md`](../../../content/posts/conductor-ai-concurrent-development-experience.md#L1), [`enterprise-background…md`](../../../content/posts/enterprise-background-agent-ramp-stripe.md#L1), [`from-em…md`](../../../content/posts/from-em-to-ai-agent-manager-career-reflection.md#L1), [`openclaw-guide…md`](../../../content/posts/openclaw-guide-for-indie-developers.md#L1), [`openclaw-sessions…md`](../../../content/posts/openclaw-sessions-json-performance-optimization.md#L1), [`why-yc…md`](../../../content/posts/why-yc-ceo-ai-is-10x-better-than-yours.md#L1), [`x-algorithm…md`](../../../content/posts/x-algorithm-for-you-feed-deep-dive.md#L1), [`氛围编程…md`](../../../content/posts/%E6%B0%9B%E5%9B%B4%E7%BC%96%E7%A8%8B%20vibe%20coding.md#L1), and [`资金费率.md`](../../../content/posts/%E8%B5%84%E9%87%91%E8%B4%B9%E7%8E%87.md#L1). Cover existence was checked against [`static/images/`](../../../static/images/).

## Exact redirect table

Order matters: deploy the three exact English rules first, then the catch-all. Preserve the query string in the Worker/redirect engine. Paths below are encoded exactly as they appear on the wire.

| Priority | Match | 301 destination | Purpose |
|---:|---|---|---|
| 1 | `https://stometa.top/posts/confirmation-bias/` | `https://stometa.dev/en/posts/confirmation-bias/` | English locale prefix |
| 2 | `https://stometa.top/posts/flywheel-effect/` | `https://stometa.dev/en/posts/flywheel-effect/` | English locale prefix |
| 3 | `https://stometa.top/posts/google-ucp-goes-live-the-search-to-checkout-era-begins/` | `https://stometa.dev/en/posts/google-ucp-goes-live-the-search-to-checkout-era-begins/` | English locale prefix |
| 4 | `https://stometa.top/*` | `https://stometa.dev/$1` | Bulk 301 preserving every other path and query string |

The bulk rule therefore sends the 11 Chinese post URLs to the same root path on `stometa.dev`, including the percent-encoded CJK paths. Do not add filename-based aliases such as `%20`, literal uppercase, or raw `.md`: Hugo never published those URLs.

## DEFECTS

### Blockers before D1 import

| Defect | Affected post(s) | Required migration action |
|---|---|---|
| Missing explicit `slug` | `BRAR 因子.md`, `Confirmation Bias.md`, `Flywheel effect.md`, `Google UCP Goes Live: The Search-to-Checkout Era Begins.md`, `氛围编程 vibe coding.md`, `资金费率.md` | Populate D1 with the **derived migration slugs in the inventory**, then assert uniqueness on `(locale, slug)`. Do not derive them again in the new app. Evidence: the older frontmatter stops at `tags`, e.g. [`BRAR 因子.md`](../../../content/posts/BRAR%20%E5%9B%A0%E5%AD%90.md#L2) and [`Confirmation Bias.md`](../../../content/posts/Confirmation%20Bias.md#L2). |
| Missing `description` | The same five older posts except Google UCP: `BRAR 因子`, `Confirmation Bias`, `Flywheel effect`, `氛围编程 vibe coding`, `资金费率` | Write editorial descriptions before import; do not silently generate them at request time. |
| `summary` cannot map automatically | Google UCP | Copy `summary` to D1 `description` after editorial review. The only summary is at [`Google UCP…md`](../../../content/posts/Google%20UCP%20Goes%20Live%3A%20The%20Search-to-Checkout%20Era%20Begins.md#L13); the target schema has no `summary` column. |
| No category and no tags | Cloudflare + Resend | Set `category = 工程实践`; source arrays are explicitly empty at [`cloudflare-resend…md`](../../../content/posts/cloudflare-resend-unlimited-email-setup.md#L5). Tags will otherwise be lost because D1 has no tags column. |
| Multi-category source vs one `category` column | Conductor, enterprise Background Agent, EM reflection, OpenClaw guide, sessions optimization, YC CEO Skill, X algorithm | Use the single proposed editorial section as `category`. Do not join source values into one opaque string. Examples begin at [`conductor…md`](../../../content/posts/conductor-ai-concurrent-development-experience.md#L5) and [`x-algorithm…md`](../../../content/posts/x-algorithm-for-you-feed-deep-dive.md#L5). |
| Frontmatter fields absent from the new schema | All posts: `draft`, `tags`; Google UCP: `summary`; five covered posts: `cover.alt`, `cover.relative`, `cover.hidden` | Map `draft: false` to `status = published`; accept that tags and cover presentation metadata are deliberately dropped or add normalized tables/columns before import. Map only `cover.image` to `cover_image`. |
| Locale is absent from current source | All 14 | Import the detected locale from this map. Do not use site `languageCode: en-us` ([`hugo.yaml`](../../../hugo.yaml#L2)); it would misclassify 11 Chinese bodies. Use one `translation_group_id` per post for now because no cross-language pairs exist in this set. |
| `editor_mode` has no source value | All 14 | Default conventional posts to `markdown`; treat X Algorithm as `html`/legacy-HTML only if the new renderer explicitly supports it. |
| Custom HTML/CSS body masquerading as Markdown | X Algorithm | The source begins a raw `<style>` block at [`x-algorithm…md`](../../../content/posts/x-algorithm-for-you-feed-deep-dive.md#L21) and is 1,319 physical lines. Its scoped classes, tables, and nested HTML require an HTML-capable/sanitized legacy renderer or a deliberate Markdown rewrite. Storing it blindly as ordinary `body_markdown` risks broken presentation or unsafe HTML. It also imports Google Fonts from the body, which should move to the site shell or be removed. |

### Filename and URL hazards

- **Six filenames contain spaces and/or CJK**: `BRAR 因子.md`, `Confirmation Bias.md`, `Flywheel effect.md`, `Google UCP Goes Live: The Search-to-Checkout Era Begins.md`, `氛围编程 vibe coding.md`, and `资金费率.md`. The three CJK path cases require percent encoding. These are source-management hazards, not permission to rename: the user-facing slugs in this map are frozen.
- **No duplicate current slug was found** across the 14 rendered pages. Enforce unique `(locale, slug)` in D1 anyway; relying on filenames recreated the historical race below.
- The percent-encoded CJK URLs must be tested using the encoded request path. In particular, `BRAR 因子.md` resolves to `brar-%E5%9B%A0%E5%AD%90`, while `氛围编程 vibe coding.md` resolves to `%E6%B0%9B%E5%9B%B4%E7%BC%96%E7%A8%8B-vibe-coding`.

### Historical publish/race and Markdown rendering defects

- **Duplicate/race pair:** commit `9a43da6` removed `content/posts/cloudflare-resend-unlimited-email-setup-2.md` and its four `static/images/...-2/card*.png` assets with the message `chore: remove duplicate post with -2 suffix (publish race condition)`. The two historical posts were the surviving [`cloudflare-resend-unlimited-email-setup.md`](../../../content/posts/cloudflare-resend-unlimited-email-setup.md#L1) and the deleted `-2` twin; there are not two current files to import. Earlier commits `6e11725`, its revert `2c6a5b1`, `36ca34b`, and `a4a96ad` show repeated publication attempts. Import exactly the surviving canonical row and add an idempotency key/unique `(locale, slug)` constraint to the D1 publishing path.
- **Mixed CJK + ASCII code block:** commit `5dd7bf6` replaced a mixed-language ASCII flow block in the Cloudflare/Resend post with Markdown paragraphs after it rendered with overlapping text. The repaired body is visible at [`cloudflare-resend…md`](../../../content/posts/cloudflare-resend-unlimited-email-setup.md#L31). Do not reconstruct the old fenced diagram during migration.
- **ASCII-art diagram:** commit `54c3b5d` replaced the enterprise Background Agent stack diagram with a Markdown table because CJK fonts broke alignment. The repaired table begins in [`enterprise-background…md`](../../../content/posts/enterprise-background-agent-ramp-stripe.md#L330). Preserve the current table, not the historical box-drawing block.
- **Current fence integrity:** all current triple-backtick fences are balanced: BRAR 2, funding rate 2, Conductor 2, Google UCP 4, OpenClaw sessions 12, and zero or an even count elsewhere. A full Hugo build renders all 14 post `index.html` pages. No currently unclosed code block was found.

## Featured, merge, or unpublish

### Featured candidates

| Rank | Post | Decision |
|---:|---|---|
| 1 | Enterprise Background Agent | **Featured.** Strongest durable engineering piece: named architecture layers, company implementations, operational constraints, and a repaired portable Markdown table. |
| 2 | From EM to AI Agent Manager | **Featured.** Best identity/author thesis and the clearest bridge between technical work and personal stakes. |
| 3 | OpenClaw sessions.json performance optimization | **Featured.** Concrete 38 MB → 2.8 MB incident story, root cause, code, and prevention; unusually high proof density despite its short prose count. |
| 4 | X Algorithm Deep Dive | **Featured only after body conversion.** It has the deepest source analysis and a specific upstream commit, but its 1,319-line bespoke HTML/CSS payload is a migration liability. Do not let visual volume substitute for editorial portability. |

If the front page has one slot, choose **Enterprise Background Agent**. The constraint ruling out X Algorithm for launch-day featured status is renderer portability, not content depth.

### Merge or unpublish

| Post | Blunt recommendation |
|---|---|
| Confirmation Bias | **Unpublish as a standalone post.** Eighteen physical lines and 132 words, with grammar/spelling errors and an overconfident “start from all data” solution. Preserve the old URL with a 301 to a future mental-models essay once merged; until then, return the migrated page so the domain cutover does not create a 404. |
| Flywheel effect | **Merge with Confirmation Bias into a rewritten “mental models for work” essay, or unpublish.** At 164 words it is a note fragment, not a durable article. Its only advantage over Confirmation Bias is a usable five-step loop. |
| BRAR 因子 | **Merge into a broader quant-factor reference unless expanded with validation.** It defines the indicator and shows code, but gives no empirical result, source, or limitations. |
| 氛围编程 vibe coding | **Keep but rewrite.** It is short and dated to the Cursor-era Vibe Coding frame, yet it contains an early version of the durable rules/context/feedback thesis. It is more valuable as an archival viewpoint than the two English fragments. |
| Why YC CEO's AI is 10× better | **Keep, but drop the “10×” claim unless measured.** At 663 Han characters it is thin and promotional; fold it into the OpenClaw/Skill article if a rewrite cannot add direct prompt evidence. |
| X Algorithm Deep Dive | **Do not merge or unpublish based on line count.** The 1,319 lines are mostly bespoke presentation; after stripping CSS/markup it still contains 3,158 Han characters and substantive analysis. Convert the body and fact-check upstream drift before featuring it. |

## Import contract

For each row, set `status = published`, `editor_mode = markdown` except the explicitly handled X legacy body, `published_at = date`, `category = proposed section`, `cover_image = cover.image or NULL`, and a unique per-post `translation_group_id`. Import should fail closed on a missing slug, description, locale, or duplicate `(locale, slug)`. After import, compare the 14 generated canonical destinations against this document and issue an HTTP request for every old URL to verify one 301 hop to the exact final locale path.
