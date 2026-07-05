# Impact 文件格式规范

此文件定义 refactor-conductor → plan 的共享契约。refactor 时先生成此文件，plan skill 读取它以约束设计范围。

---

## 文件路径

```
{dev_dir}/refactor-{N}/impact.md
```

plan skill 检测到此文件存在时，必须在设计时遵守其中的约束。

---

## 格式

```markdown
# 影响范围分析

## 重构目标
{用户描述的重构目标，原样引用}

## 当前实现摘要
- 模式: {当前代码是怎么做的，一两句话}
- 关键文件: {涉及的核心文件列表}

## 修改范围（硬约束）

plan skill 必须在此范围内设计，不得超出。

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| game/screens.rpy | 修改 | screen xxx — 调整 widget 结构 |
| game/script.rpy | 修改 | label yyy — 修改跳转逻辑 |
| game/xxx.rpy | 新建 | 新的数据模块 |

## 排除范围

plan skill 不得触碰这些：

| 文件/目录 | 原因 |
|----------|------|
| game/libs/ | 第三方库 |
| game/tl/ | 翻译文件 |
| game/gui.rpy | 主题配置 |

## 已有测试

plan skill 必须在测试策略中保护这些测试不被破坏：

| 测试文件 | 测试内容 |
|---------|---------|
| game/tests/test_xxx.rpy | ... |

## 风险点

plan skill 在设计时需注意：

- {高风险改动区域及原因}
- {可能的级联影响}

## 测试基础设施

- 状态: {已就绪 / 需初始化}
- `RENPY_SDK` 必须指向可执行的 Ren'Py SDK
- 如 `game/tests/` 缺失: plan 必须添加 `[AI-0]` bootstrap 任务创建目录和 `testsuite global: teardown: exit`

## 特殊约束

{用户指定的约束，如"不改测试文件"、"保持现有 save 格式兼容"}
```
