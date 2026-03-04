---
title: 用 Cloudflare + Resend 打造无限邮箱：一人公司的邮件基础设施
date: '2026-03-04T11:48:19.315218+08:00'
draft: false
categories: []
tags: []
description: 用 Cloudflare Email Routing + Resend SMTP + Gmail，一个域名创建无限专业邮箱，收发闭环，年成本仅域名费
  $10。
slug: cloudflare-resend-unlimited-email-setup-2
lang: zh-CN
cover:
  image: /images/cloudflare-resend-unlimited-email-setup-2/card1.png
  alt: 用 Cloudflare + Resend 打造无限邮箱：一人公司的邮件基础设施
  relative: false
  hidden: false
---

## Core Idea

> 一个域名 + Cloudflare Email Routing + Resend SMTP = 无限专业邮箱，收发闭环，零成本。

## 为什么你需要这套方案

如果你是一人公司，同时跑着好几个项目，你一定遇到过这个问题：**每个项目都需要一个独立的邮箱身份**。

注册 SaaS 工具要邮箱，试用 AI 产品要邮箱，项目对外联络要邮箱。你总不能每个都去申请一个新的 Gmail 吧？那管理成本会把你逼疯。

Cloudflare 在这件事上堪称**赛博活佛**。它的 Email Routing 功能完全免费，只要你有一个域名，就能创建无限多的邮箱地址，全部转发到同一个 Gmail。`project-a@yourdomain.com`、`project-b@yourdomain.com`、`ai-tools@yourdomain.com` — 随便造，想加就加，一分钟一个。

具体能干什么：

- **SaaS 注册白嫖**：很多工具按邮箱给免费额度，不同邮箱 = 不同账号
- **AI 工具试用**：新工具出来了想试？换个邮箱注册就行
- **多项目管理**：每个项目有独立的对外邮箱身份，专业且不混乱
- **隐私保护**：不用暴露你的真实邮箱

## 架构总览

整个闭环分两条线路：

```
收邮件：
别人发到 project@company.com
  → Cloudflare Email Routing 转发
  → stometa@gmail.com 收到
  → Gmail Filter 按 To 地址自动打标签分类

发邮件：
Gmail 点击 "Send mail as" 选择 project@company.com
  → 通过 Resend SMTP 服务器发出
  → 对方收到的发件人是 project@company.com
  → 不进垃圾箱（因为有正确的 SPF/DKIM 记录）
```

| 组件 | 用途 | 费用 |
|------|------|------|
| Cloudflare Email Routing | 收邮件转发 | 免费 |
| Gmail | 邮件客户端 | 免费 |
| Resend | 发邮件 SMTP | 免费（3,000封/月） |
| 你的域名 | 邮箱地址后缀 | ~$10/年 |

总成本：**一年大约 $10，只是域名费用**。

## Part 1: 收邮件 — Cloudflare Email Routing

### 前置条件

- 你有一个域名（任何注册商都行）
- 域名的 DNS 已托管在 Cloudflare（免费计划就够）

### Step 1: 开启 Email Routing

1. 登录 Cloudflare Dashboard
2. 选择你的域名
3. 左侧菜单找到 **Email** → **Email Routing**
4. 点击 **Get started**

Cloudflare 会自动帮你配置好 MX 记录。如果之前有其他 MX 记录，它会提示你删除。

### Step 2: 添加目标邮箱

1. 在 **Destination addresses** 中添加你的 Gmail 地址
2. Cloudflare 会发一封验证邮件到你的 Gmail
3. 点击邮件中的链接完成验证

### Step 3: 创建路由规则

这里有两种玩法：

**方式 A：Catch-all（推荐懒人方案）**

开启 Catch-all，所有发到 `*@yourdomain.com` 的邮件都转发到你的 Gmail。这意味着你不需要提前创建邮箱地址 — 随便编一个就能用。

**方式 B：逐个添加**

在 **Routing rules** 中手动添加每个地址的转发规则：
- `admin@company.com` → `you@gmail.com`
- `project-a@company.com` → `you@gmail.com`

> 推荐用 Catch-all。一人公司经常要快速测试新项目，不想每次都回 Cloudflare 加规则。需要新邮箱？直接用就行，邮件自动到。

### Step 4: Gmail Filter 自动分类

邮件都涌到同一个 Gmail 里会很乱。用 Gmail Filter 解决：

1. 在 Gmail 搜索栏输入 `to:project-a@company.com`
2. 点击搜索栏右边的过滤图标
3. 点击 **Create filter**
4. 选择 **Apply the label** → 创建新标签（如 `Project-A`）
5. 勾选 **Also apply filter to matching conversations**

这样每个项目的邮件自动归类，一目了然。

## Part 2: 发邮件 — Resend SMTP + Gmail

收邮件搞定了。但如果你只能收不能发，别人给 `admin@company.com` 发邮件，你回复的时候发件人却是你的私人 Gmail — 这就很不专业。

### 为什么不用 Gmail 原生方案

Gmail 自带 **Send mail as** 功能，理论上可以用其他邮箱地址发邮件。但有个致命问题：**Gmail 的免费 SMTP 发出去的邮件，SPF/DKIM 对不上你的域名**，大概率进垃圾箱。

### 为什么选 Resend

- **每月 3,000 封免费**：一人公司完全够用
- **SMTP 服务**：可以直接挂载到 Gmail
- **自动配置 SPF/DKIM**：邮件不进垃圾箱
- **设置简单**：10 分钟搞定

### Step 1: 注册 Resend 并验证域名

1. 去 [resend.com](https://resend.com) 注册账号
2. 进入 Dashboard → **Domains** → **Add Domain**
3. 输入你的域名（如 `company.com`）
4. Resend 会给你几条 DNS 记录，需要去 Cloudflare 添加

### Step 2: 在 Cloudflare 添加 DNS 记录

Resend 通常需要你添加：
- 1 条 **SPF** 记录（TXT）
- 几条 **DKIM** 记录（TXT 或 CNAME）

去 Cloudflare Dashboard → 你的域名 → **DNS** → **Records**，按 Resend 给的值逐条添加。

> **注意 SPF 合并**：如果你的域名已经有一条 SPF 记录，不要再加一条新的。**一个域名只能有一条 SPF 记录**。你需要把 Resend 的 `include:` 值合并到现有的 SPF 记录里。
>
> 例如：`v=spf1 include:_spf.mx.cloudflare.net include:amazonses.com ~all`

添加完 DNS 记录后，回到 Resend 点击 **Verify**。通常几分钟内就能验证通过。

### Step 3: 生成 API Key

1. 在 Resend Dashboard → **API Keys** → **Create API Key**
2. 权限选 **Sending access**，限定到你的域名
3. 复制生成的 API Key（只显示一次）

这个 API Key 就是你接下来在 Gmail 里配置 SMTP 时的"密码"。

### Step 4: Gmail 配置 Send mail as

1. 打开 Gmail → **Settings** → **Accounts and Import**
2. 找到 **Send mail as** → **Add another email address**
3. 填写发件人名称和邮箱地址，取消勾选 **Treat as an alias**
4. 配置 SMTP 服务器：

| 字段 | 值 |
|------|----|
| SMTP Server | `smtp.resend.com` |
| Port | `465` |
| Username | `resend` |
| Password | 你刚才生成的 API Key |
| 安全连接 | SSL |

5. 点击 **Add Account**
6. Gmail 会发一封验证邮件到该地址 — 因为你已配好 Cloudflare Email Routing，邮件会转发到你的 Gmail，点击确认链接即可

## 验证 & 实际效果

配置完成后，做两个测试：

**测试收邮件**：用另一个邮箱发邮件到 `admin@company.com`，确认 Gmail 能收到且 Filter 正确打了标签。

**测试发邮件**：在 Gmail 写新邮件，From 下拉选择 `admin@company.com`，确认对方收到时发件人显示正确且不在垃圾箱。

两个测试都通过 — **闭环完成**。

## 进阶玩法

### 新项目 1 分钟添加

以后每启动一个新项目，只需要：

1. 去 Gmail **Send mail as** 加一个新地址（用同样的 Resend SMTP）
2. 加一条 Gmail Filter 自动打标签

如果用了 Catch-all，第一步都省了。**1 分钟搞定，零额外成本。**

### Gmail Filter 高级用法

除了按 `To` 地址打标签，还可以：
- 自动标记为已读（不重要的通知邮件）
- 自动归档（不出现在收件箱）
- 自动转发到其他邮箱

### 配合其他工具

这套邮箱系统可以和很多工具联动：
- **Newsletter 订阅**：用 `newsletter@yourdomain.com` 统一接收，不污染主邮箱
- **客服邮箱**：`support@yourdomain.com` 对外，背后还是你一个人
- **自动化流程**：配合 Zapier/Make 做邮件触发的自动化

## 总结

这套方案的核心优势：**一次配置，终身受益**。

花一个小时把基础设施搭好，之后每个新项目的邮箱身份 1 分钟就能就位。对于一人公司来说，这种低成本、高扩展性的基础设施，是让你能同时运转多个项目的关键。
