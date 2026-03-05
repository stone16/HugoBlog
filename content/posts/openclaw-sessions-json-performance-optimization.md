---
title: OpenClaw sessions.json 性能优化：从 38MB 到 2.8MB
date: '2026-03-05T10:55:14.250345+08:00'
draft: false
categories:
- 技术
- 开发效率
tags:
- openclaw
- 性能优化
- debugging
- discord
- nodejs
- event-loop
- infrastructure
description: OpenClaw sessions.json 因 skillsSnapshot 重复存储膨胀至 38MB，导致 Discord event
  loop 阻塞 9 分钟。本文记录根因分析与自动化清理方案。
slug: openclaw-sessions-json-performance-optimization
lang: zh-CN
cover:
  image: /images/openclaw-sessions-json-performance-optimization/card1.png
  alt: OpenClaw sessions.json 性能优化：从 38MB 到 2.8MB
  relative: false
  hidden: false
---

## 背景：Discord 大面积无响应

某天早晨，多个 Discord 频道突然停止响应。日志显示 `DiscordMessageListener` 处理时间严重超标：

```
[02:11] 32.8 seconds
[02:16] 91.5 seconds  → health-monitor 自动重启
[02:27] 再次重启
[02:47] 再次重启
[02:52] 543.6 seconds（9分钟！）
[03:19] 132.8 seconds
```

一个上午触发了 5 次以上 gateway 重启，用户体验完全崩溃。

## 根因诊断

### 第一层：sessions.json 文件异常膨胀

```
sessions.json 大小：38.6 MB
session entries 总数：500（已达上限）
其中 cron sessions：427 个（85%）
Discord sessions：31 个
其他（Telegram/Feishu）：42 个
```

### 第二层：skillsSnapshot 是罪魁祸首

OpenClaw 在每个 session entry 里存储了一份完整的 `skillsSnapshot`，包含所有 79 个 workspace skills 的系统提示文本。

```
skillsSnapshot 大小：~75KB / 每个 entry
有快照的 entry 数：495 / 500
总占用：35.4 MB（占文件的 92%！）
其余元数据：仅 2.8 MB
```

**为什么要存 skillsSnapshot？** 设计上服务三个功能：

1. **技能变更检测**：文件 watcher 监控 SKILL.md 变化，session 检测到版本不匹配时重新构建系统提示
2. **Env 变量覆盖恢复**：某些 skill 配置了 API key 等环境变量，tool call 时从 snapshot 恢复
3. **系统提示缓存**：避免每次 turn 重新读取 79 个 SKILL.md 文件

**设计缺陷**：prompt 全文（~70KB）应该全局共享一份 + 各 session 存 hash 引用，而不是每个 session 存一份完整拷贝。500 entries × 75KB vs 1 × 75KB + 500 × 64B，相差约 37 倍。

### 第三层：同步 I/O 阻塞 event loop

源码中 `loadSessionStore()` 在 turn 处理的关键路径使用同步读取：

```javascript
// sessions-D-LKdTsU.js
const raw = fs.readFileSync(storePath, "utf-8");  // 同步读 38MB
const parsed = JSON.parse(raw);                     // CPU 密集解析
return structuredClone(store);                       // 深拷贝 38MB 对象
```

每条 Discord 消息都触发这个流程。加上 OpenClaw 的 turn 队列是串行的，一个慢 turn 会阻塞所有频道。

### 第四层：cron session 无限积累

40+ 个 cron job 每次运行都创建新的 isolated session entry，每个携带 75KB 的 skillsSnapshot。427 个 cron entries 贡献了约 31MB。

## 解决方案

### 立即修复：清理脚本

编写 `cleanup-sessions.py`，逻辑与 OpenClaw 原生 maintenance 行为对齐：

```python
# 1. 剥离 cron session 的 skillsSnapshot（省空间，不影响功能）
if ":cron:" in key and "skillsSnapshot" in entry:
    del entry["skillsSnapshot"]

# 2. 删除超过 3 天不活跃的 session entry
if age_days > STALE_DAYS:
    # 归档 .jsonl 文件（rename → .deleted.TIMESTAMP）
    archive_session_file(session_file, reason="deleted")
    del data[key]

# 3. 保护主 session 永不删除
# agent:main:main → skip
```

关键细节：
- 删除 entry 时同步归档对应的 `.jsonl` transcript 文件
- 归档方式：`rename → xxx.jsonl.deleted.2026-03-04T…Z`（与 OpenClaw 行为一致）
- OpenClaw 自身会在 30 天后清理 `.deleted.` 文件

### 优化效果

| 指标 | 之前 | 之后 |
|------|------|------|
| sessions.json | 39.7 MB | 2.8 MB（↓93%） |
| entries 总数 | 511 | 447 |
| 归档 Discord thread | 13 个占着 | 已清除 |
| 过期 session | 51 个 | 已清除 |

### 长期维护：每日 Cron

```
Job: sessions-cleanup
Schedule: 每天 3:45 AM CST
Model: claude-haiku-4-5（轻量级）
逻辑: 执行 cleanup-sessions.py --apply --days 3
```

## Discord Thread 操作与 Session 的关系

| 操作 | Discord 历史 | sessions.json | .jsonl 文件 |
|------|:---:|:---:|:---:|
| `/new` | ✅ 保留 | ✅ 新 sessionId | 旧 → `.reset.` 归档 |
| Close thread | ✅ 保留 | ❌ 不动 | ❌ 不动 |
| Lock thread | ✅ 保留 | ❌ 不动 | ❌ 不动 |
| Delete thread | ❌ 删除 | ❌ 不动 | ❌ 不动 |

**`/new` 是唯一真正重置 AI session 的方式。** Discord 的 close/lock/delete 只影响 Discord 侧，不碰 OpenClaw 的 session 状态。清理已关闭 thread 的正确姿势：先 `/new`，然后 Lock thread。

## 关联 Issues

- **#15145**（open）：skillsSnapshot per-session 存储导致 sessions.json 膨胀 — 已提交详细诊断数据
- **#11950**（open）：提议 per-session 文件替代单一 sessions.json
- **#12289**（closed）：cron session 无限积累
- **#9238**：Discord 消息队列卡死

## 后续计划

- 持续关注 #15145 是否有官方修复
- 监控 sessions.json 大小，必要时降低 `--days` 阈值
- 考虑提 PR：cron `:run:` entry 不写入 skillsSnapshot（一行代码修复根因）

---

脚本存档路径：`~/.openclaw/workspace/memory/reference/scripts/cleanup-sessions.py`
