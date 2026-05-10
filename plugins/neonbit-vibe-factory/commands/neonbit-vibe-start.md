---
name: neonbit-vibe-start
description: 启动新的开发任务工作流（全流程：需求→架构→详设→API→计划→TDD开发）
argument-hint: <任务描述>
allowed-tools: ["Read", "Write", "Bash", "Agent", "Skill"]
---

# /neonbit-vibe-start

启动一个新功能的完整开发工作流。

## 使用方式

```
/neonbit-vibe-start 开发一个用户管理模块，包含增删改查功能
/neonbit-vibe-start 开发商品展示页面，支持分类筛选和搜索
```

## 参数

- `任务描述`: 简洁描述需要开发的功能

## 调用 orchestrator

```javascript
await Skill("neonbit-vibe-factory:orchestrator")
```

加载 skill 后，将用户提供的任务描述传递给 orchestrator，严格按照 orchestrator skill 指令执行完整工作流。

**绝对不要**跳过 orchestrator 直接编码。