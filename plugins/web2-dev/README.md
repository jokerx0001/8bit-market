# web2-dev

Web 服务开发全流程编排插件。覆盖后端与前端，从需求分析到生产部署的完整 TDD 工作流。

## 概述

web2-dev 是 neonbit-vibe-factory 的重构版本，核心理念：
- **环境即一等公民**：基础设施 + 开发服务器由专业运维 skill 管理
- **安全第一**：所有操作使用权限受限账户，超管操作只输出不执行
- **TDD 重构**：告别无效测试，只对有逻辑的方法进行 TDD
- **集成测试必选**：后端 API 测试 + 前端 Playwright E2E
- **极简 Agent**：agent 只定义约束，流程逻辑在 skill 中编排

## 命令

| 命令 | 用途 |
|------|------|
| `/web2-dev:new` | 新项目开发（项目级需求+架构文档） |
| `/web2-dev:feat` | 新功能开发（模块级需求+架构文档） |
| `/web2-dev:refactor` | 代码重构 |
| `/web2-dev:fix` | BUG 修复 |

所有命令支持 `--auto` 标志跳过人工审查点。

## 开发流程

```
new/feat:
  技术栈检测 → grill → requirements → architecture → design
  → [frontend-design] → [设计审查] → plan(任务分解) → [审查]
  → exec:
      ops(基础设施) → 按任务循环(后端TDD + code-review)
      → 后端集成测试 → 部署 → 部署后集成测试
      → 前端开发 → 前端E2E → code-review → 部署前端 → 前端E2E
  → completed
```

## 依赖插件

- `grilling`（用户级 skill，`~/.claude/skills/grilling`）— Grill 前置采访。来自 Matt Pocock 的 skills 仓库，通过 `setup-matt-pocock-skills` 安装为裸名用户级 skill。
- `tdd`（用户级 skill，`~/.claude/skills/tdd`）— TDD RED→GREEN 循环。安装方式同上。
  - 注意：本插件按裸名 `grilling` / `tdd` 引用——用户级全局 skill 的调用名就是裸名（目录名），不存在插件前缀形式。Skill 工具做精确匹配，**调用失败报 `Unknown skill: web2-dev:grilling` 说明是本次调用被误加了插件前缀（模型模式补全），用裸名重试即可**；报 `Unknown skill: grilling` 才是依赖缺失。
- `frontend-design` — UI 设计稿生成

## 环境要求

项目 CLAUDE.md 需声明：
- 开发服务器地址、账户（非 root）
- 基础设施服务器地址、账户（非 root）
- Ansible 项目路径
- 数据库账户（非超管）
- 服务部署/启停方式

## 目录结构

```
web2-dev/
├── commands/        # 入口命令（薄包装）
├── skills/          # 核心流程逻辑
├── agents/          # 极简 agent（角色+工具+约束）
├── references/      # 技术栈规则 + 运维规范
└── scripts/         # 辅助脚本
```
