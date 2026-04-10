---
title: 同样用Claude，为什么YC CEO的AI比你好用10倍
date: '2026-03-18T20:30:31.734925+08:00'
draft: false
categories:
- AI工具
- 开发效率
tags:
- AI
- Prompt工程
- Gary Tan
- YCombinator
- gstack
- Claude
- 代码审查
- AI工作流
description: YC CEO Gary Tan 开源了一套结构化 AI Skill，让 AI 像技术合伙人一样 Review 代码方案。拆解其核心框架，看懂
  Prompt 深度与思考深度的关系。
slug: why-yc-ceo-ai-is-10x-better-than-yours
cover:
  image: /images/why-yc-ceo-ai-is-10x-better-than-yours/card1.png
  alt: 同样用Claude，为什么YC CEO的AI比你好用10倍
  relative: false
  hidden: false
---

## 同样用 Claude，为什么 YC CEO 的 AI 比你好用 10 倍？

Y Combinator 的 CEO Gary Tan，最近把自己用 AI 的方式完全开源了。

不是那种「我用 ChatGPT 写邮件」的分享，而是一整套结构化的 AI Skill。他让 AI 像一个真正的技术合伙人一样帮他 Review 代码方案。

我认真拆解了其中最核心的一个：**Founder CEO Review**。

---

## 普通人 vs. Gary：从第一步就不一样

- 普通人用 AI：「这个代码怎么写？」
- Gary 用 AI：先回答三个问题

① 这是正确的问题吗？换个框架会不会更简单？

② 什么都不做会怎样？这是真痛点还是假设的？

③ 12 个月后的理想状态是什么？这个方案是最直接的路径吗？

光这一步，就已经超过 90% 的人用 AI 的水平了。大多数人拿到需求就开干，Gary 的 AI 第一件事是**质疑需求本身**。

---

## 三种模式，像换挡一样切换

**📈 EXPANSION 模式**

>「10 倍野心、2 倍投入的版本是什么？世界上最好的工程师会怎么做？」

**⚖️ HOLD 模式**

> 「最少改动达到目标？超过 8 个文件或 2 个新类 = 警报」

**✂️ REDUCTION 模式**

> 「最低可用版本是什么？什么可以砍到下一个 PR？」

你用 AI 有几种模式？大概率只有一种。而 Gary 连什么时候该激进、什么时候该保守，都帮 AI 定义好了。

---

## 10 段深度审查，每一段都像独立面试

从架构、错误处理、安全、性能、测试到部署，共 10 个维度逐一过堂。

但最聪明的不是审查本身，而是他给 AI 设的**行为锁**：

- 选了扩张模式就不许偷偷缩小范围
- 一个问题一个问题问，不许批量轰炸
- 没问题就说没问题，不许编造问题来显得有用
- 绝对不改代码，只分析

这些约束解决的是 AI 最常见的毛病：保守偏向、生造问题、和稀泥。Gary 用「不要做什么」来驯服 AI，这比「要做什么」难 10 倍。

---

## 模型是一样的，Prompt 是不一样的

大家都在用同一个大模型。Claude 也好，GPT 也好，API 是一样的。

但 Gary 的 Skill 里，你能清晰看到一个连续创业者 20+ 年积累的思考框架：

- 什么时候该质疑方向 ↔ 什么时候该扎进细节
- 什么时候该全力扩张 ↔ 什么时候该极致克制

这些东西不是 AI 教他的，是**他教给 AI 的**。

Prompt 的深度，就是你思考的深度。

所以与其追最新的模型版本，不如先想清楚：你到底要 AI 帮你做什么？你能给它什么样的思考框架？

Gary 的 gstack 已经开源，GitHub 搜 `gstack` 就能找到，强烈建议每个用 AI 写代码的人都看看。
