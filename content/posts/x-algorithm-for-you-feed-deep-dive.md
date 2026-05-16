---
title: X Algorithm Deep Dive — For You Feed 推荐算法全景解析
date: '2026-05-16T10:00:00+08:00'
draft: false
categories:
- 社交媒体
- 算法解析
tags:
- X/Twitter
- 推荐算法
- For You Feed
- Phoenix
- 内容创作
- 社交媒体增长
- 开源代码分析
description: 基于 X 开源推荐算法代码库的逐行深度分析。覆盖完整 Pipeline、21 个评分维度、权重体系、流量池分层策略，以及面向不同体量博主的实操指南。
slug: x-algorithm-for-you-feed-deep-dive
---


<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

.xalgo-wrap {
--primary: #ff385c;
--primary-active: #e00b41;
--primary-disabled: #ffd1da;
--ink: #222222;
--body: #3f3f3f;
--muted: #6a6a6a;
--muted-soft: #929292;
--hairline: #dddddd;
--hairline-soft: #ebebeb;
--canvas: #ffffff;
--surface-soft: #f7f7f7;
--surface-strong: #f2f2f2;
--on-primary: #ffffff;
--star: #222222;
--error: #c13515;
--rounded-xs: 4px;
--rounded-sm: 8px;
--rounded-md: 14px;
--rounded-lg: 20px;
--rounded-xl: 32px;
--rounded-full: 9999px;
--shadow: rgba(0,0,0,0.02) 0 0 0 1px, rgba(0,0,0,0.04) 0 2px 6px 0, rgba(0,0,0,0.1) 0 4px 8px 0;
--sp-xxs: 2px;
--sp-xs: 4px;
--sp-sm: 8px;
--sp-md: 12px;
--sp-base: 16px;
--sp-lg: 24px;
--sp-xl: 32px;
--sp-xxl: 48px;
--sp-section: 64px;
}

.xalgo-wrap {
font-family: 'Inter', Circular, -apple-system, system-ui, Roboto, 'Helvetica Neue', sans-serif;
color: var(--ink);
line-height: 1.5;
-webkit-font-smoothing: antialiased;
}

/* ── Hero ────────────────────────────── */
.xalgo-wrap .hero {
background: var(--canvas);
padding: 80px var(--sp-lg) var(--sp-section);
text-align: center;
border-bottom: 1px solid var(--hairline-soft);
}
.xalgo-wrap .hero-content {
max-width: 680px;
margin: 0 auto;
}
.xalgo-wrap .hero-badge {
display: inline-flex;
align-items: center;
gap: var(--sp-sm);
background: var(--surface-soft);
border: 1px solid var(--hairline-soft);
border-radius: var(--rounded-full);
padding: 6px 16px;
font-size: 12px;
font-weight: 600;
color: var(--muted);
margin-bottom: var(--sp-lg);
}
.xalgo-wrap .hero-badge .dot {
width: 6px;
height: 6px;
border-radius: 50%;
background: var(--primary);
}
.xalgo-wrap .hero h1 {
font-size: 28px;
font-weight: 700;
line-height: 1.43;
letter-spacing: 0;
color: var(--ink);
margin-bottom: var(--sp-base);
}
.xalgo-wrap .hero h1 .accent {
color: var(--primary);
}
.xalgo-wrap .hero p {
font-size: 16px;
font-weight: 400;
color: var(--body);
line-height: 1.5;
max-width: 560px;
margin: 0 auto;
}

/* ── Nav ─────────────────────────────── */
.xalgo-wrap .nav-strip {
position: sticky;
top: 0;
z-index: 100;
background: var(--canvas);
border-bottom: 1px solid var(--hairline-soft);
padding: 0 var(--sp-lg);
}
.xalgo-wrap .nav-inner {
max-width: 1280px;
margin: 0 auto;
display: flex;
gap: var(--sp-xs);
overflow-x: auto;
scrollbar-width: none;
-ms-overflow-style: none;
}
.xalgo-wrap .nav-inner::-webkit-scrollbar { display: none; }
.xalgo-wrap .nav-item {
flex-shrink: 0;
padding: var(--sp-base) var(--sp-base);
font-size: 14px;
font-weight: 500;
color: var(--muted);
text-decoration: none;
border-bottom: 2px solid transparent;
transition: color 0.15s, border-color 0.15s;
white-space: nowrap;
}
.xalgo-wrap .nav-item:hover {
color: var(--ink);
border-bottom-color: var(--ink);
}

/* ── Container ──────────────────────── */
.xalgo-wrap .container {
max-width: 1080px;
margin: 0 auto;
padding: 0 var(--sp-lg);
}

/* ── Sections ───────────────────────── */
.xalgo-wrap section {
padding: var(--sp-section) 0;
}
.xalgo-wrap section + section {
border-top: 1px solid var(--hairline-soft);
}

/* ── Typography ─────────────────────── */
.xalgo-wrap h2 {
font-size: 22px;
font-weight: 500;
line-height: 1.18;
letter-spacing: -0.44px;
color: var(--ink);
margin-bottom: var(--sp-md);
}
.xalgo-wrap h3 {
font-size: 16px;
font-weight: 600;
line-height: 1.25;
color: var(--ink);
margin-bottom: var(--sp-sm);
margin-top: var(--sp-xl);
}
.xalgo-wrap h4 {
font-size: 14px;
font-weight: 600;
line-height: 1.25;
color: var(--ink);
margin-bottom: var(--sp-xs);
margin-top: var(--sp-lg);
}
.xalgo-wrap .section-subtitle {
font-size: 16px;
font-weight: 400;
color: var(--muted);
line-height: 1.5;
margin-bottom: var(--sp-xl);
max-width: 640px;
}

/* ── Card ────────────────────────────── */
.xalgo-wrap .card {
background: var(--canvas);
border: 1px solid var(--hairline);
border-radius: var(--rounded-md);
padding: var(--sp-lg);
margin-bottom: var(--sp-base);
transition: box-shadow 0.2s;
}
.xalgo-wrap .card:hover {
box-shadow: var(--shadow);
}

.xalgo-wrap .card-grid {
display: grid;
grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
gap: var(--sp-base);
}
.xalgo-wrap .card-grid-3 {
display: grid;
grid-template-columns: repeat(3, 1fr);
gap: var(--sp-base);
}
@media (max-width: 768px) {
.xalgo-wrap .card-grid-3 { grid-template-columns: 1fr; }
}

/* ── Pills ── */
.xalgo-wrap .pill {
display: inline-flex;
align-items: center;
gap: 4px;
padding: 4px 10px;
border-radius: var(--rounded-full);
font-size: 11px;
font-weight: 600;
line-height: 1.18;
}
.xalgo-wrap .pill-primary { background: var(--primary-disabled); color: var(--primary-active); }
.xalgo-wrap .pill-ink { background: var(--surface-strong); color: var(--ink); }
.xalgo-wrap .pill-muted { background: var(--surface-soft); color: var(--muted); }
.xalgo-wrap .pill-error { background: #fde8e4; color: var(--error); }
.xalgo-wrap .pill-high { background: #fff0e6; color: #c45500; }
.xalgo-wrap .pill-mid { background: var(--surface-soft); color: var(--body); }

/* ── Pipeline / Funnel ──────────────── */
.xalgo-wrap .funnel-step {
display: flex;
align-items: stretch;
gap: var(--sp-lg);
}
.xalgo-wrap .funnel-track {
display: flex;
flex-direction: column;
align-items: center;
flex-shrink: 0;
width: 40px;
}
.xalgo-wrap .funnel-number {
width: 32px;
height: 32px;
border-radius: 50%;
display: flex;
align-items: center;
justify-content: center;
font-size: 13px;
font-weight: 700;
color: var(--on-primary);
background: var(--primary);
flex-shrink: 0;
}
.xalgo-wrap .funnel-number-muted {
background: var(--ink);
}
.xalgo-wrap .funnel-line {
flex: 1;
width: 1px;
background: var(--hairline);
margin: var(--sp-xs) 0;
}
.xalgo-wrap .funnel-body {
flex: 1;
padding-bottom: var(--sp-xl);
}
.xalgo-wrap .funnel-title {
font-size: 16px;
font-weight: 600;
line-height: 1.25;
color: var(--ink);
margin-bottom: var(--sp-xs);
}
.xalgo-wrap .funnel-desc {
font-size: 14px;
font-weight: 400;
color: var(--body);
line-height: 1.43;
}

/* ── Weight bars ────────────────────── */
.xalgo-wrap .weight-bar-wrap { margin-bottom: var(--sp-md); }
.xalgo-wrap .weight-bar-label {
display: flex;
justify-content: space-between;
align-items: center;
margin-bottom: var(--sp-xs);
font-size: 14px;
}
.xalgo-wrap .weight-bar-label .name {
font-weight: 400;
color: var(--body);
}
.xalgo-wrap .weight-bar-label .value {
font-weight: 600;
font-size: 14px;
font-variant-numeric: tabular-nums;
color: var(--ink);
}
.xalgo-wrap .weight-bar-track {
height: 6px;
background: var(--surface-strong);
border-radius: var(--rounded-full);
overflow: hidden;
}
.xalgo-wrap .weight-bar-fill {
height: 100%;
border-radius: var(--rounded-full);
background: var(--primary);
transition: width 0.6s ease;
}

/* ── DO / DON'T ─────────────────────── */
.xalgo-wrap .do-dont-grid {
display: grid;
grid-template-columns: 1fr 1fr;
gap: var(--sp-base);
}
@media (max-width: 768px) {
.xalgo-wrap .do-dont-grid { grid-template-columns: 1fr; }
}
.xalgo-wrap .do-card {
border-top: 3px solid var(--ink);
}
.xalgo-wrap .dont-card {
border-top: 3px solid var(--primary);
}
.xalgo-wrap .do-item, .xalgo-wrap .dont-item {
display: flex;
gap: var(--sp-sm);
padding: var(--sp-md) 0;
font-size: 14px;
font-weight: 400;
line-height: 1.43;
color: var(--body);
border-bottom: 1px solid var(--hairline-soft);
}
.xalgo-wrap .do-item:last-child, .xalgo-wrap .dont-item:last-child { border-bottom: none; }
.xalgo-wrap .do-icon {
flex-shrink: 0;
font-size: 14px;
font-weight: 700;
color: var(--ink);
}
.xalgo-wrap .dont-icon {
flex-shrink: 0;
font-size: 14px;
font-weight: 700;
color: var(--primary);
}

/* ── Tier cards ─────────────────────── */
.xalgo-wrap .tier-card {
background: var(--canvas);
border: 1px solid var(--hairline);
border-radius: var(--rounded-md);
padding: var(--sp-lg);
position: relative;
}
.xalgo-wrap .tier-card:hover {
box-shadow: var(--shadow);
}
.xalgo-wrap .tier-name {
font-size: 20px;
font-weight: 600;
line-height: 1.2;
letter-spacing: -0.18px;
color: var(--ink);
margin-bottom: var(--sp-xs);
}
.xalgo-wrap .tier-range {
font-size: 14px;
font-weight: 400;
color: var(--muted);
margin-bottom: var(--sp-base);
}
.xalgo-wrap .tier-stat-row {
display: flex;
gap: var(--sp-sm);
margin-bottom: var(--sp-base);
flex-wrap: wrap;
}
.xalgo-wrap .tier-stat {
padding: var(--sp-sm) var(--sp-md);
border-radius: var(--rounded-sm);
background: var(--surface-soft);
font-size: 12px;
text-align: center;
min-width: 72px;
}
.xalgo-wrap .tier-stat .num {
font-size: 16px;
font-weight: 600;
display: block;
color: var(--ink);
margin-bottom: 1px;
}
.xalgo-wrap .tier-stat .label {
color: var(--muted);
font-weight: 400;
}

/* ── Table ──────────────────────────── */
.xalgo-wrap .metric-table {
width: 100%;
border-collapse: collapse;
font-size: 14px;
}
.xalgo-wrap .metric-table th {
text-align: left;
padding: var(--sp-md) var(--sp-base);
font-weight: 600;
font-size: 12px;
color: var(--muted);
text-transform: uppercase;
letter-spacing: 0.3px;
border-bottom: 1px solid var(--hairline);
background: var(--canvas);
}
.xalgo-wrap .metric-table td {
padding: var(--sp-md) var(--sp-base);
border-bottom: 1px solid var(--hairline-soft);
vertical-align: top;
font-weight: 400;
color: var(--body);
}
.xalgo-wrap .metric-table td strong {
color: var(--ink);
font-weight: 600;
}
.xalgo-wrap .metric-table tr:last-child td { border-bottom: none; }
.xalgo-wrap .metric-table tr:hover td { background: var(--surface-soft); }

/* ── Code ref ───────────────────────── */
.xalgo-wrap .code-ref {
font-family: 'SF Mono', 'Fira Code', ui-monospace, monospace;
font-size: 12px;
background: var(--surface-soft);
padding: 2px 6px;
border-radius: var(--rounded-xs);
color: var(--muted);
border: 1px solid var(--hairline-soft);
}

/* ── Callout ────────────────────────── */
.xalgo-wrap .callout {
background: var(--surface-soft);
border: 1px solid var(--hairline-soft);
border-radius: var(--rounded-md);
padding: var(--sp-lg);
margin: var(--sp-lg) 0;
font-size: 14px;
font-weight: 400;
line-height: 1.43;
color: var(--body);
}
.xalgo-wrap .callout-title {
font-weight: 600;
font-size: 14px;
color: var(--ink);
margin-bottom: var(--sp-xs);
display: flex;
align-items: center;
gap: var(--sp-sm);
}
.xalgo-wrap .callout-warn {
background: #fff8f6;
border-color: #fde8e4;
}

/* ── Formula box ────────────────────── */
.xalgo-wrap .formula-box {
background: var(--surface-soft);
border: 1px solid var(--hairline);
color: var(--ink);
padding: var(--sp-lg);
border-radius: var(--rounded-md);
font-family: 'SF Mono', 'Fira Code', ui-monospace, monospace;
font-size: 13px;
line-height: 1.8;
overflow-x: auto;
margin: var(--sp-lg) 0;
}
.xalgo-wrap .formula-box .comment { color: var(--muted-soft); }
.xalgo-wrap .formula-box .keyword { color: var(--ink); font-weight: 600; }
.xalgo-wrap .formula-box .number { color: var(--primary); font-weight: 600; }
.xalgo-wrap .formula-box .highlight { color: var(--ink); font-weight: 700; }
.xalgo-wrap .formula-box .neg { color: var(--error); }

/* ── Checklist ──────────────────────── */
.xalgo-wrap .checklist { list-style: none; padding: 0; }
.xalgo-wrap .checklist li {
display: flex;
align-items: flex-start;
gap: var(--sp-sm);
padding: var(--sp-sm) 0;
font-size: 14px;
font-weight: 400;
line-height: 1.43;
color: var(--body);
border-bottom: 1px solid var(--hairline-soft);
}
.xalgo-wrap .checklist li:last-child { border-bottom: none; }
.xalgo-wrap .checklist .check {
flex-shrink: 0;
width: 18px;
height: 18px;
border-radius: var(--rounded-xs);
border: 1.5px solid var(--hairline);
margin-top: 2px;
}

/* ── Footer ─────────────────────────── */
.xalgo-wrap .footer-section {
background: var(--canvas);
border-top: 1px solid var(--hairline-soft);
padding: var(--sp-xxl) var(--sp-lg);
text-align: center;
}
.xalgo-wrap .footer-section p {
font-size: 13px;
font-weight: 400;
color: var(--muted);
line-height: 1.5;
}
.xalgo-wrap .footer-section a {
color: var(--ink);
text-decoration: underline;
}
.xalgo-wrap .footer-section code {
font-family: 'SF Mono', 'Fira Code', ui-monospace, monospace;
font-size: 12px;
background: var(--surface-soft);
padding: 1px 4px;
border-radius: var(--rounded-xs);
}

/* ── Responsive ─────────────────────── */
@media (max-width: 744px) {
.xalgo-wrap .hero { padding: var(--sp-xxl) var(--sp-base) var(--sp-xxl); }
.xalgo-wrap .hero h1 { font-size: 22px; }
.xalgo-wrap .container { padding: 0 var(--sp-base); }
.xalgo-wrap section { padding: var(--sp-xxl) 0; }
.xalgo-wrap .do-dont-grid { grid-template-columns: 1fr; }
.xalgo-wrap .card-grid-3 { grid-template-columns: 1fr; }
.xalgo-wrap .metric-table { font-size: 13px; }
.xalgo-wrap .metric-table th, .xalgo-wrap .metric-table td { padding: var(--sp-sm); }
}
</style>

<div class="xalgo-wrap">

<!-- ═══ Nav ═══ -->
<nav class="nav-strip">
<div class="nav-inner">
<a class="nav-item" href="#pipeline">Pipeline</a>
<a class="nav-item" href="#dimensions">21 个维度</a>
<a class="nav-item" href="#weights">权重体系</a>
<a class="nav-item" href="#formula">评分公式</a>
<a class="nav-item" href="#do-dont">DO / DON'T</a>
<a class="nav-item" href="#tiers">流量池分层</a>
<a class="nav-item" href="#playbook">实操手册</a>
</div>
</nav>

<div class="container">

<!-- ═══ PIPELINE ═══ -->
<section id="pipeline">
<h2>Pipeline: 从发帖到展示的 7 步旅程</h2>
<p class="section-subtitle">每条推文经历以下完整链路。任何一步不通过，都不会出现在用户 For You Feed 中。</p>

<div class="funnel-step">
<div class="funnel-track">
<div class="funnel-number">1</div>
<div class="funnel-line"></div>
</div>
<div class="funnel-body">
<div class="funnel-title">Query Hydration — 理解"谁在刷"</div>
<div class="funnel-desc">
系统加载查看者的完整上下文：<strong>互动历史</strong>（点赞、回复、转推记录）、<strong>关注列表</strong>、<strong>屏蔽/静音列表</strong>、<strong>订阅信息</strong>、<strong>话题偏好</strong>、<strong>地理位置</strong>、<strong>设备类型</strong>、<strong>已看过的帖子 Bloom Filter</strong>。
<br><span class="code-ref">home-mixer/query_hydrators/</span> 共 15+ 个 hydrator 并行加载
</div>
</div>
</div>

<div class="funnel-step">
<div class="funnel-track">
<div class="funnel-number">2</div>
<div class="funnel-line"></div>
</div>
<div class="funnel-body">
<div class="funnel-title">Candidate Sourcing — 从哪里找帖子</div>
<div class="funnel-desc">
<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;margin-bottom:12px;">
<span class="pill pill-primary">Thunder (In-Network)</span>
<span class="pill pill-primary">Phoenix Retrieval (OON)</span>
<span class="pill pill-ink">Phoenix Topics</span>
<span class="pill pill-ink">Phoenix MoE</span>
<span class="pill pill-muted">TweetMixer</span>
<span class="pill pill-muted">Cached Posts</span>
</div>
<strong>Thunder</strong>：你关注的人发的帖子，亚毫秒内存检索。
<strong>Phoenix Retrieval</strong>：Two-Tower 模型 + 向量相似度搜索全站内容。
</div>
</div>
</div>

<div class="funnel-step">
<div class="funnel-track">
<div class="funnel-number">3</div>
<div class="funnel-line"></div>
</div>
<div class="funnel-body">
<div class="funnel-title">Hydration — 补充帖子特征</div>
<div class="funnel-desc">
给每条候选帖子补充：核心元数据、作者信息（粉丝数、screen name）、视频时长、是否含媒体、订阅状态、被屏蔽关系、语言代码、互关 Jaccard 分数、话题分类、引用帖展开。
<br><span class="code-ref">home-mixer/candidate_hydrators/</span> 共 16 个 hydrator
</div>
</div>
</div>

<div class="funnel-step">
<div class="funnel-track">
<div class="funnel-number">4</div>
<div class="funnel-line"></div>
</div>
<div class="funnel-body">
<div class="funnel-title">Pre-Scoring Filters — 过滤不合格候选</div>
<div class="funnel-desc">
<table class="metric-table" style="margin-top:8px;">
<tr><td><strong>DropDuplicatesFilter</strong></td><td>去重复帖子 ID</td></tr>
<tr><td><strong>CoreDataHydrationFilter</strong></td><td>移除加载失败的帖子</td></tr>
<tr><td><strong>AgeFilter</strong></td><td>移除超过保留期的旧帖</td></tr>
<tr><td><strong>SelfTweetFilter</strong></td><td>移除查看者自己的帖子</td></tr>
<tr><td><strong>RetweetDeduplicationFilter</strong></td><td>同一原始内容的转推去重</td></tr>
<tr><td><strong>IneligibleSubscriptionFilter</strong></td><td>移除无权查看的付费内容</td></tr>
<tr><td><strong>PreviouslySeenPostsFilter</strong></td><td>移除已看过的帖子 (Bloom Filter)</td></tr>
<tr><td><strong>PreviouslyServedPostsFilter</strong></td><td>移除本次会话已展示的帖子</td></tr>
<tr><td><strong>MutedKeywordFilter</strong></td><td>移除含用户静音关键词的帖子</td></tr>
<tr><td><strong>AuthorSocialgraphFilter</strong></td><td>移除被屏蔽/静音作者的帖子</td></tr>
<tr><td><strong>VideoFilter</strong></td><td>按设置过滤视频</td></tr>
<tr><td><strong>TopicIdsFilter</strong></td><td>话题匹配过滤</td></tr>
</table>
</div>
</div>
</div>

<div class="funnel-step">
<div class="funnel-track">
<div class="funnel-number">5</div>
<div class="funnel-line"></div>
</div>
<div class="funnel-body">
<div class="funnel-title">Scoring — 核心排名（最关键的一步）</div>
<div class="funnel-desc">
三个 Scorer 依次运行：<br>
<strong>① PhoenixScorer</strong> — Grok-based Transformer 预测 15+ 种互动概率<br>
<strong>② RankingScorer</strong> — 加权合成 + Author Diversity 衰减 + OON 权重调整<br>
<strong>③ VMRanker</strong> — Value Model 服务端重排序（可选）
</div>
</div>
</div>

<div class="funnel-step">
<div class="funnel-track">
<div class="funnel-number funnel-number-muted">6</div>
<div class="funnel-line"></div>
</div>
<div class="funnel-body">
<div class="funnel-title">Selection — 取 Top K</div>
<div class="funnel-desc">按最终得分排序，选取前 K 条候选。<span class="code-ref">TopKScoreSelector</span></div>
</div>
</div>

<div class="funnel-step">
<div class="funnel-track">
<div class="funnel-number funnel-number-muted">7</div>
<div class="funnel-line" style="background:transparent;"></div>
</div>
<div class="funnel-body">
<div class="funnel-title">Post-Selection + Ads Blending</div>
<div class="funnel-desc">
最终安全过滤（VFFilter：删除/垃圾/暴力等）、对话去重、广告安全插入。Premium+ 用户看到的广告更少。
</div>
</div>
</div>
</section>


<!-- ═══ DIMENSIONS ═══ -->
<section id="dimensions">
<h2>21 个评分维度</h2>
<p class="section-subtitle">Phoenix Transformer 模型预测每条帖子在每个维度上的互动概率，然后加权合成最终得分。</p>

<h3 style="margin-top:0;">正向信号</h3>
<p style="font-size:14px;color:var(--muted);margin-bottom:var(--sp-base);">越高越好——这些信号推高帖子在 Feed 中的排名</p>

<div class="card" style="overflow-x:auto;padding:0;">
<table class="metric-table">
<thead>
<tr>
<th>维度</th>
<th>代码字段</th>
<th>含义</th>
<th>权重级别</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>P(favorite)</strong></td>
<td><span class="code-ref">favorite_score</span></td>
<td>用户点赞的概率</td>
<td><span class="pill pill-primary">最高 ≈ 1.0</span></td>
</tr>
<tr>
<td><strong>P(reply)</strong></td>
<td><span class="code-ref">reply_score</span></td>
<td>用户回复的概率</td>
<td><span class="pill pill-high">高 ≈ 0.5</span></td>
</tr>
<tr>
<td><strong>P(retweet)</strong></td>
<td><span class="code-ref">retweet_score</span></td>
<td>用户转推的概率</td>
<td><span class="pill pill-high">高 ≈ 0.3</span></td>
</tr>
<tr>
<td><strong>P(quote)</strong></td>
<td><span class="code-ref">quote_score</span></td>
<td>用户引用转推的概率</td>
<td><span class="pill pill-mid">中等</span></td>
</tr>
<tr>
<td><strong>P(share)</strong></td>
<td><span class="code-ref">share_score</span></td>
<td>用户分享的概率</td>
<td><span class="pill pill-mid">中等</span></td>
</tr>
<tr>
<td><strong>P(share_via_dm)</strong></td>
<td><span class="code-ref">share_via_dm_score</span></td>
<td>用户通过私信分享的概率</td>
<td><span class="pill pill-mid">中等</span></td>
</tr>
<tr>
<td><strong>P(share_via_copy_link)</strong></td>
<td><span class="code-ref">share_via_copy_link_score</span></td>
<td>用户复制链接分享的概率</td>
<td><span class="pill pill-mid">中等</span></td>
</tr>
<tr>
<td><strong>P(click)</strong></td>
<td><span class="code-ref">click_score</span></td>
<td>用户点击帖子的概率</td>
<td><span class="pill pill-mid">中等</span></td>
</tr>
<tr>
<td><strong>P(profile_click)</strong></td>
<td><span class="code-ref">profile_click_score</span></td>
<td>用户点击作者头像的概率</td>
<td><span class="pill pill-mid">中等</span></td>
</tr>
<tr>
<td><strong>P(dwell)</strong></td>
<td><span class="code-ref">dwell_score</span></td>
<td>用户停留阅读的概率</td>
<td><span class="pill pill-mid">中等 ≈ 0.2</span></td>
</tr>
<tr>
<td><strong>Dwell Time</strong></td>
<td><span class="code-ref">dwell_time</span></td>
<td>预测停留时长（连续值）</td>
<td><span class="pill pill-muted">连续</span></td>
</tr>
<tr>
<td><strong>Click Dwell Time</strong></td>
<td><span class="code-ref">click_dwell_time</span></td>
<td>点击后停留时长</td>
<td><span class="pill pill-muted">连续</span></td>
</tr>
<tr>
<td><strong>P(video_quality_view)</strong></td>
<td><span class="code-ref">vqv_score</span></td>
<td>视频质量观看概率（需满足最低时长）</td>
<td><span class="pill pill-muted">有条件</span></td>
</tr>
<tr>
<td><strong>P(photo_expand)</strong></td>
<td><span class="code-ref">photo_expand_score</span></td>
<td>用户展开图片的概率</td>
<td><span class="pill pill-muted">较低</span></td>
</tr>
<tr>
<td><strong>P(follow_author)</strong></td>
<td><span class="code-ref">follow_author_score</span></td>
<td>用户关注作者的概率</td>
<td><span class="pill pill-ink">加分</span></td>
</tr>
<tr>
<td><strong>P(quoted_click)</strong></td>
<td><span class="code-ref">quoted_click_score</span></td>
<td>点击引用帖子的概率</td>
<td><span class="pill pill-muted">较低</span></td>
</tr>
<tr>
<td><strong>P(quoted_vqv)</strong></td>
<td><span class="code-ref">quoted_vqv_score</span></td>
<td>引用帖视频观看概率</td>
<td><span class="pill pill-muted">较低</span></td>
</tr>
</tbody>
</table>
</div>

<h3 style="margin-top:40px;">负向信号</h3>
<p style="font-size:14px;color:var(--muted);margin-bottom:var(--sp-base);">越高越糟糕——这些信号会直接把帖子排名拉到底部</p>

<div class="card" style="overflow-x:auto;padding:0;">
<table class="metric-table">
<thead>
<tr>
<th>维度</th>
<th>代码字段</th>
<th>含义</th>
<th>危害级别</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>P(not_interested)</strong></td>
<td><span class="code-ref">not_interested_score</span></td>
<td>用户点"不感兴趣"的概率</td>
<td><span class="pill pill-error">严重</span></td>
</tr>
<tr>
<td><strong>P(block_author)</strong></td>
<td><span class="code-ref">block_author_score</span></td>
<td>用户屏蔽作者的概率</td>
<td><span class="pill pill-error">致命</span></td>
</tr>
<tr>
<td><strong>P(mute_author)</strong></td>
<td><span class="code-ref">mute_author_score</span></td>
<td>用户静音作者的概率</td>
<td><span class="pill pill-error">严重</span></td>
</tr>
<tr>
<td><strong>P(report)</strong></td>
<td><span class="code-ref">report_score</span></td>
<td>用户举报帖子的概率</td>
<td><span class="pill pill-error">致命</span></td>
</tr>
<tr>
<td><strong>P(not_dwelled)</strong></td>
<td><span class="code-ref">not_dwelled_score</span></td>
<td>用户快速滑过不停留的概率</td>
<td><span class="pill pill-high">中等</span></td>
</tr>
</tbody>
</table>
</div>

<div class="callout callout-warn" style="margin-top:var(--sp-lg);">
<div class="callout-title">负向信号的杠杆效应</div>
负向信号不是简单地扣分。当加权得分 &lt; 0 时，offset 公式会将得分压缩到 <code>[0, NEGATIVE_SCORES_OFFSET]</code> 范围内，这意味着一条被频繁举报的帖子几乎不可能出现在任何人的 Feed 中。一次批量举报可能永久压低你的帖子在模型中的预测概率。
</div>
</section>


<!-- ═══ WEIGHTS ═══ -->
<section id="weights">
<h2>权重体系可视化</h2>
<p class="section-subtitle">基于 <span class="code-ref">run_pipeline.py:356</span> 示例权重和代码分析推断的相对权重。生产权重通过 Feature Switches 动态配置。</p>

<div class="card" style="padding:var(--sp-lg);">
<h4 style="margin-top:0;">正向互动权重</h4>

<div class="weight-bar-wrap">
<div class="weight-bar-label"><span class="name">Favorite (点赞)</span><span class="value">1.00</span></div>
<div class="weight-bar-track"><div class="weight-bar-fill" style="width:100%;"></div></div>
</div>

<div class="weight-bar-wrap">
<div class="weight-bar-label"><span class="name">Reply (回复)</span><span class="value">0.50</span></div>
<div class="weight-bar-track"><div class="weight-bar-fill" style="width:50%; opacity:0.85;"></div></div>
</div>

<div class="weight-bar-wrap">
<div class="weight-bar-label"><span class="name">Retweet (转推)</span><span class="value">0.30</span></div>
<div class="weight-bar-track"><div class="weight-bar-fill" style="width:30%; opacity:0.7;"></div></div>
</div>

<div class="weight-bar-wrap">
<div class="weight-bar-label"><span class="name">Dwell (停留)</span><span class="value">0.20</span></div>
<div class="weight-bar-track"><div class="weight-bar-fill" style="width:20%; opacity:0.6;"></div></div>
</div>

<div class="weight-bar-wrap">
<div class="weight-bar-label"><span class="name">Share (分享 / DM / Copy Link)</span><span class="value">~0.15</span></div>
<div class="weight-bar-track"><div class="weight-bar-fill" style="width:15%; opacity:0.5;"></div></div>
</div>

<div class="weight-bar-wrap">
<div class="weight-bar-label"><span class="name">Quote / Click / Profile Click</span><span class="value">~0.10</span></div>
<div class="weight-bar-track"><div class="weight-bar-fill" style="width:10%; opacity:0.4;"></div></div>
</div>

<div class="weight-bar-wrap">
<div class="weight-bar-label"><span class="name">VQV / Photo Expand / Follow Author</span><span class="value">~0.05–0.10</span></div>
<div class="weight-bar-track"><div class="weight-bar-fill" style="width:7%; opacity:0.3;"></div></div>
</div>

<h4>后处理乘数</h4>

<div class="weight-bar-wrap">
<div class="weight-bar-label"><span class="name">In-Network (关注列表) 内容</span><span class="value">×1.0</span></div>
<div class="weight-bar-track"><div class="weight-bar-fill" style="width:100%;background:var(--ink);"></div></div>
</div>

<div class="weight-bar-wrap">
<div class="weight-bar-label"><span class="name">Out-of-Network 内容 (OON)</span><span class="value">×OON_WEIGHT_FACTOR</span></div>
<div class="weight-bar-track"><div class="weight-bar-fill" style="width:65%;background:var(--ink);opacity:0.6;"></div></div>
</div>

<div class="weight-bar-wrap">
<div class="weight-bar-label"><span class="name">新用户 OON 加成</span><span class="value">×NEW_USER_OON_WEIGHT</span></div>
<div class="weight-bar-track"><div class="weight-bar-fill" style="width:85%;background:var(--ink);opacity:0.4;"></div></div>
</div>

<div class="weight-bar-wrap">
<div class="weight-bar-label"><span class="name">Author Diversity 衰减 (同一作者第 2 条)</span><span class="value">×decay^1</span></div>
<div class="weight-bar-track"><div class="weight-bar-fill" style="width:45%;background:var(--muted-soft);"></div></div>
</div>

<div class="weight-bar-wrap">
<div class="weight-bar-label"><span class="name">Author Diversity 衰减 (同一作者第 3 条)</span><span class="value">×decay^2</span></div>
<div class="weight-bar-track"><div class="weight-bar-fill" style="width:25%;background:var(--hairline);"></div></div>
</div>
</div>
</section>


<!-- ═══ FORMULA ═══ -->
<section id="formula">
<h2>核心评分公式</h2>
<p class="section-subtitle">三段式评分：加权合成 → 多样性调整 → OON 系数</p>

<div class="formula-box">
<span class="comment">// Step 1: Phoenix Transformer 预测互动概率</span>
<span class="keyword">P</span> = PhoenixModel(user_context, candidate)  <span class="comment">→ 15+ 维概率向量</span>

<span class="comment">// Step 2: 加权合成</span>
<span class="highlight">weighted_score</span> = <span class="number">1.0</span>×P(fav) + <span class="number">0.5</span>×P(reply) + <span class="number">0.3</span>×P(rt) + <span class="number">0.2</span>×P(dwell)
+ w_share×P(share) + w_click×P(click) + ...
<span class="neg">- w_block×P(block) - w_mute×P(mute) - w_report×P(report)</span>

<span class="comment">// Step 3: Offset (确保负分不会跌破 0)</span>
<span class="keyword">if</span> weighted_score &lt; <span class="number">0</span>:
score = (weighted_score + negative_sum) / total_sum × NEGATIVE_OFFSET
<span class="keyword">else</span>:
score = weighted_score + NEGATIVE_OFFSET

<span class="comment">// Step 4: Author Diversity 衰减</span>
<span class="highlight">multiplier</span> = (1 - floor) × decay^position + floor
adjusted_score = score × multiplier  <span class="comment">// position = 同一作者已出现次数</span>

<span class="comment">// Step 5: OON 调整</span>
<span class="keyword">if</span> !in_network:
<span class="highlight">final_score</span> = adjusted_score × effective_oon_weight
<span class="keyword">else</span>:
<span class="highlight">final_score</span> = adjusted_score  <span class="comment">// 关注列表内容不打折</span>
</div>

<div class="callout">
<div class="callout-title">关键洞察</div>
具体的权重数值<strong>不在开源代码中</strong>。它们通过 <span class="code-ref">FeatureSwitches</span> 系统在运行时注入，并且根据用户的 <code>user_roles</code>（订阅等级）、<code>account_age_days</code>（账号年龄）、<code>country</code>（国家）、<code>has_phone_number</code>（是否绑定手机）动态调整。这意味着 X 可以在不部署代码的情况下，随时改变任何用户群体的推荐策略。
</div>
</section>


<!-- ═══ DO / DON'T ═══ -->
<section id="do-dont">
<h2>DO / DON'T 操作指南</h2>
<p class="section-subtitle">基于算法代码逻辑推导的确定性建议</p>

<div class="do-dont-grid">
<div class="card do-card">
<h3 style="margin-top:0;">DO — 一定要做</h3>

<div class="do-item">
<span class="do-icon">+</span>
<div><strong>优化点赞触发</strong> — 点赞权重是回复的 2 倍、转推的 3.3 倍。写能让人"随手点赞"的内容（金句、共鸣、实用信息）是 ROI 最高的策略。</div>
</div>
<div class="do-item">
<span class="do-icon">+</span>
<div><strong>引导回复和讨论</strong> — 回复权重 0.5，仅次于点赞。用提问、投票、争议性话题引发评论区讨论。</div>
</div>
<div class="do-item">
<span class="do-icon">+</span>
<div><strong>提高停留时长</strong> — 用 Thread、信息密度高的图文、吸引人的开头。dwell_time 是连续值预测——停留越久加分越多。</div>
</div>
<div class="do-item">
<span class="do-icon">+</span>
<div><strong>激励分享/私信转发</strong> — DM 分享和复制链接分享是独立的正向信号。</div>
</div>
<div class="do-item">
<span class="do-icon">+</span>
<div><strong>发视频超过最低时长门槛</strong> — 视频必须超过 <code>MIN_VIDEO_DURATION_MS</code> 才能获得 VQV 权重加成。太短的视频等于放弃了一个完整的正向信号维度。</div>
</div>
<div class="do-item">
<span class="do-icon">+</span>
<div><strong>建立互关网络</strong> — <code>mutual_follow_jaccard</code> 是后排序信号。与目标受众互关，提高你在他们 In-Network 源中的优先级。</div>
</div>
<div class="do-item">
<span class="do-icon">+</span>
<div><strong>保持发帖频率适中</strong> — Author Diversity Scorer 指数衰减同一作者的第 2、3 条帖子。3 条精品 > 10 条灌水。</div>
</div>
<div class="do-item">
<span class="do-icon">+</span>
<div><strong>关注 Banger 质量分 ≥ 0.4</strong> — Grok VLM 初筛评估内容质量。有实质内容 + 相关媒体是通过门槛的基础。</div>
</div>
<div class="do-item">
<span class="do-icon">+</span>
<div><strong>带有媒体（图片/视频）</strong> — <code>has_media</code> 是独立布尔信号，会被传入模型。纯文字帖少了一个维度的信号。</div>
</div>
<div class="do-item">
<span class="do-icon">+</span>
<div><strong>保持帖子新鲜度</strong> — <code>post_age_bucket</code> 是模型输入特征。超过 4800 分钟（80 小时）会进入溢出桶。</div>
</div>
</div>

<div class="card dont-card">
<h3 style="margin-top:0;">DON'T — 千万不要做</h3>

<div class="dont-item">
<span class="dont-icon">×</span>
<div><strong>不要发容易被举报的内容</strong> — P(report) 有负权重。模型学会"你的内容容易被举报"后，这个概率会持续影响所有帖子。</div>
</div>
<div class="dont-item">
<span class="dont-icon">×</span>
<div><strong>不要让人屏蔽/静音你</strong> — P(block_author) 和 P(mute_author) 是致命信号。被 100 人屏蔽的伤害远大于被 1000 人忽略。</div>
</div>
<div class="dont-item">
<span class="dont-icon">×</span>
<div><strong>不要刷屏发帖</strong> — Author Diversity 使用指数衰减。第 3 条以后的帖子分数可能不到第 1 条的 25%。</div>
</div>
<div class="dont-item">
<span class="dont-icon">×</span>
<div><strong>不要发 AI 灌水内容</strong> — Banger 初筛有 <code>slop_score</code>（AI 灌水检测）。批量 AI 生成的低质内容会被检测并降分。</div>
</div>
<div class="dont-item">
<span class="dont-icon">×</span>
<div><strong>不要发让人快速滑走的内容</strong> — <code>not_dwelled_score</code> 是独立的负向信号。开头无聊 = 快速滑走 = 负分。</div>
</div>
<div class="dont-item">
<span class="dont-icon">×</span>
<div><strong>不要触发"不感兴趣"</strong> — P(not_interested) 权重极高。投喂错误的受众群体会导致大量"不感兴趣"反馈。</div>
</div>
<div class="dont-item">
<span class="dont-icon">×</span>
<div><strong>不要在付费墙后面放重要内容</strong> — <code>IneligibleSubscriptionFilter</code> 会直接过滤非订阅者看不到的内容。</div>
</div>
<div class="dont-item">
<span class="dont-icon">×</span>
<div><strong>不要使用常见的静音关键词</strong> — <code>MutedKeywordFilter</code> 在评分前就过滤。含有广泛被静音关键词的帖子会从很多人的候选池中直接消失。</div>
</div>
<div class="dont-item">
<span class="dont-icon">×</span>
<div><strong>不要发超短无实质视频</strong> — 低于 <code>MIN_VIDEO_DURATION_MS</code> 的视频会让 VQV 权重直接为 0。</div>
</div>
<div class="dont-item">
<span class="dont-icon">×</span>
<div><strong>不要忽视帖子新鲜度</strong> — 帖子超过 80 小时进入溢出桶，模型对旧帖的推荐概率显著下降。不要指望旧帖"慢热"。</div>
</div>
</div>
</div>
</section>


<!-- ═══ TIERS ═══ -->
<section id="tiers">
<h2>流量池分层策略</h2>
<p class="section-subtitle">算法对不同体量的博主有结构性的差异化处理</p>

<div class="card-grid" style="margin-top:var(--sp-lg);">

<div class="tier-card">
<div class="tier-name">种子期 · Seed Stage</div>
<div class="tier-range">0 – 1,000 粉丝</div>

<div class="tier-stat-row">
<div class="tier-stat"><span class="num">In</span><span class="label">主要流量源</span></div>
<div class="tier-stat"><span class="num">小</span><span class="label">OON 候选池</span></div>
<div class="tier-stat"><span class="num">冷启动</span><span class="label">模型状态</span></div>
</div>

<h4 style="margin-top:var(--sp-base);">算法行为</h4>
<ul style="font-size:14px;line-height:1.7;padding-left:20px;color:var(--body);">
<li><strong>In-Network 为主</strong> — 你的内容主要展示给关注你的人。Thunder 源直接推送到粉丝的候选池。</li>
<li><strong>OON 突破门槛高</strong> — Phoenix Retrieval 需要你的帖子 embedding 与海量候选竞争。粉丝少 = 互动数据少 = embedding 向量缺乏独特性。</li>
<li><strong>Author Embedding 弱</strong> — 模型通过 <code>author_hashes</code> 编码你的身份。互动历史少的作者，其 embedding 不够"锐利"。</li>
<li><strong>P(follow_author) 是突破点</strong> — 当 OON 用户看到你的帖子并关注你，这直接扩大你的 In-Network 覆盖。</li>
<li><strong>Mutual Follow Jaccard 极低</strong> — 几乎没有共同关注网络，在排名后处理中处于劣势。</li>
</ul>

<h4>关键策略</h4>
<div style="font-size:14px;line-height:1.7;color:var(--body);">
<strong>1. 利用 Topic 系统破圈</strong> — 发帖紧贴 Grok Topics 分类，确保帖子被 <code>PhoenixTopicsSource</code> 检索到。这是小号进入 OON 候选池的最可靠路径。<br>
<strong>2. 极致单帖质量</strong> — Author Diversity 衰减意味着你的第 2、3 条帖子分数大幅打折。用 1 条高质量帖击穿阈值，比发 5 条平庸帖效果好得多。<br>
<strong>3. 引导关注转化</strong> — P(follow_author) 是独立正向权重。每一个新关注者都直接扩大你的 In-Network 池。<br>
<strong>4. 互关策略建网络</strong> — 主动关注并与同领域创作者互动，提高 <code>mutual_follow_jaccard</code> 分数。
</div>
</div>

<div class="tier-card">
<div class="tier-name">增长期 · Growth Stage</div>
<div class="tier-range">1,000+ 粉丝</div>

<div class="tier-stat-row">
<div class="tier-stat"><span class="num">In+OON</span><span class="label">双流量源</span></div>
<div class="tier-stat"><span class="num">大</span><span class="label">OON 候选池</span></div>
<div class="tier-stat"><span class="num">成熟</span><span class="label">模型状态</span></div>
</div>

<h4 style="margin-top:var(--sp-base);">算法行为</h4>
<ul style="font-size:14px;line-height:1.7;padding-left:20px;color:var(--body);">
<li><strong>In-Network + OON 双引擎</strong> — 粉丝互动为帖子提供强初始信号，Phoenix Retrieval 将高互动帖推向全站。</li>
<li><strong>Author Embedding 成熟</strong> — 大量互动数据让模型能准确预测"谁会喜欢你的内容"，OON 检索精准度更高。</li>
<li><strong><code>author_followers_count</code> 作为 VMRanker 输入</strong> — 粉丝数量是 VMRanker 请求中的特征字段，影响 Value Model 的重排序。</li>
<li><strong>Author Diversity 是核心约束</strong> — 粉丝量大后，你可能同时有多条帖子进入同一用户的候选池。衰减效应更明显。</li>
<li><strong>负向信号杠杆更大</strong> — 覆盖面广意味着更多人可能触发 block/mute/report。负面信号的统计显著性更强。</li>
</ul>

<h4>关键策略</h4>
<div style="font-size:14px;line-height:1.7;color:var(--body);">
<strong>1. 保护负向指标</strong> — 避免被屏蔽/举报比追求更多点赞更重要。一次争议事件引发的批量屏蔽，可能需要数周才能恢复。<br>
<strong>2. 利用引用推文</strong> — <code>quoted_click_score</code> 和 <code>quoted_vqv_score</code> 是独立维度。引用其他热门帖子可以搭载其互动热度。<br>
<strong>3. 分享驱动</strong> — DM 分享和复制链接是独立信号。创作"值得转给朋友"的内容在这个阶段 ROI 更高。<br>
<strong>4. 视频战略</strong> — 发布超过最低时长门槛的视频，解锁 VQV 权重通道。大 KOL 的视频更容易被推荐给 OON 用户。<br>
<strong>5. 订阅等级</strong> — Premium/Premium+ 通过 Feature Switches 获得不同的排名参数。参数差异化的架构已确认存在。
</div>
</div>
</div>

<h3 style="margin-top:40px;">流量池对比矩阵</h3>

<div class="card" style="overflow-x:auto;padding:0;">
<table class="metric-table">
<thead>
<tr>
<th>维度</th>
<th>种子期 (0–1K)</th>
<th>增长期 (1K+)</th>
<th>代码出处</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>主要流量源</strong></td>
<td>Thunder (In-Network)</td>
<td>Thunder + Phoenix (In + OON)</td>
<td><span class="code-ref">phoenix_candidate_pipeline.rs</span></td>
</tr>
<tr>
<td><strong>OON 检索精度</strong></td>
<td>低 — embedding 向量模糊</td>
<td>高 — 大量互动训练数据</td>
<td><span class="code-ref">recsys_retrieval_model.py</span></td>
</tr>
<tr>
<td><strong>Author Diversity 衰减</strong></td>
<td>影响小 — 候选池中很少出现多条</td>
<td>影响大 — 频繁多条同时候选</td>
<td><span class="code-ref">ranking_scorer.rs</span></td>
</tr>
<tr>
<td><strong>负向信号风险</strong></td>
<td>低 — 曝光少，绝对数量少</td>
<td>高 — 广泛曝光，批量 block 风险</td>
<td><span class="code-ref">ranking_scorer.rs</span></td>
</tr>
<tr>
<td><strong>VQV 收益</strong></td>
<td>基础 — 视频触达有限</td>
<td>放大 — OON 推荐扩大视频曝光</td>
<td><span class="code-ref">weighted_scorer.rs</span></td>
</tr>
<tr>
<td><strong>Mutual Follow 影响</strong></td>
<td>关键 — 唯一排名加成来源</td>
<td>辅助 — 互动信号已足够强</td>
<td><span class="code-ref">mutual_follow_jaccard_hydrator.rs</span></td>
</tr>
<tr>
<td><strong>Topic 系统价值</strong></td>
<td>核心 — 进入 OON 的主要通道</td>
<td>补充 — 已有强自然检索</td>
<td><span class="code-ref">phoenix_topics_source.rs</span></td>
</tr>
<tr>
<td><strong>Feature Switch 参数</strong></td>
<td>标准参数（可能因新用户有特殊值）</td>
<td>可能因 user_roles / 订阅等级获得优化参数</td>
<td><span class="code-ref">server.rs</span></td>
</tr>
</tbody>
</table>
</div>
</section>


<!-- ═══ PLAYBOOK ═══ -->
<section id="playbook">
<h2>实操手册 — 一条帖子的完整优化</h2>
<p class="section-subtitle">按照算法的评分公式，一条帖子的优化 Checklist</p>

<div class="card-grid-3">
<div class="card">
<h4 style="margin-top:0;">点赞优化</h4>
<div style="font-size:13px;color:var(--muted);margin-bottom:var(--sp-sm);">权重 ≈ 1.0（最高）</div>
<ul class="checklist">
<li><span class="check"></span>内容是否包含可共鸣的观点/金句？</li>
<li><span class="check"></span>是否提供了即时价值（实用、有趣、震惊）？</li>
<li><span class="check"></span>第一行是否就能让人产生"说得好"的反应？</li>
</ul>
</div>

<div class="card">
<h4 style="margin-top:0;">回复优化</h4>
<div style="font-size:13px;color:var(--muted);margin-bottom:var(--sp-sm);">权重 ≈ 0.5</div>
<ul class="checklist">
<li><span class="check"></span>帖子末尾是否有明确的问题/讨论引导？</li>
<li><span class="check"></span>话题是否有多个合理立场（引发辩论）？</li>
<li><span class="check"></span>发布后 30 分钟内是否回复了评论？</li>
</ul>
</div>

<div class="card">
<h4 style="margin-top:0;">转推优化</h4>
<div style="font-size:13px;color:var(--muted);margin-bottom:var(--sp-sm);">权重 ≈ 0.3</div>
<ul class="checklist">
<li><span class="check"></span>内容是否是"必须让别人也看到"类型？</li>
<li><span class="check"></span>是否包含原创数据/洞察/独家信息？</li>
<li><span class="check"></span>是否适合引用转推（QT 是独立信号）？</li>
</ul>
</div>

<div class="card">
<h4 style="margin-top:0;">停留优化</h4>
<div style="font-size:13px;color:var(--muted);margin-bottom:var(--sp-sm);">权重 ≈ 0.2 + 连续值</div>
<ul class="checklist">
<li><span class="check"></span>开头是否足够吸引人阻止快速滑动？</li>
<li><span class="check"></span>内容长度是否足够支撑 5+ 秒阅读？</li>
<li><span class="check"></span>图片/视频是否值得仔细看？</li>
</ul>
</div>

<div class="card">
<h4 style="margin-top:0;">视频优化</h4>
<div style="font-size:13px;color:var(--muted);margin-bottom:var(--sp-sm);">VQV 有最低时长门槛</div>
<ul class="checklist">
<li><span class="check"></span>视频时长是否超过最低阈值？</li>
<li><span class="check"></span>前 3 秒是否有足够的吸引力？</li>
<li><span class="check"></span>引用帖中的视频也会被单独评分</li>
</ul>
</div>

<div class="card">
<h4 style="margin-top:0;">负向防护</h4>
<div style="font-size:13px;color:var(--muted);margin-bottom:var(--sp-sm);">负权重 — 最优先避免</div>
<ul class="checklist">
<li><span class="check"></span>内容是否可能引发举报？</li>
<li><span class="check"></span>是否会让不感兴趣的人群看到？</li>
<li><span class="check"></span>是否含有常见静音关键词？</li>
<li><span class="check"></span>是否可能触发批量屏蔽？</li>
</ul>
</div>
</div>

<div class="callout" style="margin-top:var(--sp-xl);">
<div class="callout-title">最终总结：算法的本质</div>
<div style="margin-top:var(--sp-sm);font-size:15px;line-height:1.6;">
X 推荐算法的核心是一个 <strong>Grok-based Transformer</strong>，它从你的历史互动中学习模式，然后预测你会如何与每条候选帖子互动。没有手工特征、没有人工干预规则——<strong>一切都是互动数据驱动</strong>。
<br><br>
这意味着：<strong>你的受众的行为定义了你的帖子的分数</strong>。吸引到正确的受众（高点赞、高回复、低屏蔽），比任何"黑科技"都有效。算法不是一个需要"破解"的黑箱，而是一面反映你内容质量和受众匹配度的镜子。
</div>
</div>
</section>

</div>

<!-- ═══ Footer ═══ -->
<div class="xalgo-wrap">
<div class="footer-section">
<div style="max-width:600px;margin:0 auto;">
<p style="font-size:14px;font-weight:600;color:var(--ink);margin-bottom:var(--sp-sm);">基于 X Algorithm 开源代码的技术分析</p>
<p>Commit <code>0bfc279</code> · 2026-05-15</p>
<p style="margin-top:var(--sp-sm);">By <a href="https://x.com/stometaverse">@stometaverse</a> · Builder of <a href="https://github.com/stone16/claude-review-loop">claude-review-loop</a> & <a href="https://github.com/stone16/Invoice-Manager">Invoice-Manager</a></p>
<p style="margin-top:var(--sp-sm);font-size:12px;color:var(--muted-soft);">Design reference: Airbnb Design System</p>
</div>
</div>
</div>
