# Routing Table 渲染规则

本文件定义了 routing-table.md 的渲染规则。stack-detector 根据 stack.json 扫描实际目录并生成路由表。

## 目录结构约定

references/rules/ 下的每个语言/技术目录遵循：

```
{lang}/
├── code/       ← *.md 文件 → coding agent
├── test/       ← *.md 文件 → test agent
└── *.md        ← 根目录文件 → coding + test 两个 agent
```

## 框架过滤约定

`code/` 和 `test/` 下的文件命名决定是否加载：

- **无框架后缀**（如 `coding-style.md`、`testing.md`）→ **总是**包含，无论检测到什么框架
- **有框架后缀**（如 `coding-springboot.md`、`test-springboot.md`）→ 文件名中 `-{framework}.md` 部分与 `stack.json` 的 `framework` 字段匹配时才包含

匹配规则：从文件名中提取 `-{name}.md` 后缀，将 `{name}` 与 `framework` 值做小写相等比较。

例：
- 检测到 `framework: spring-boot` → `coding-springboot.md` 匹配 ✓，`test-quarkus.md` 不匹配 ✗
- 检测到 `framework: null`（纯语言）→ 所有带框架后缀的文件都跳过

## 渲染流程

stack-detector 第五步按以下顺序扫描并生成 routing-table.md：

### 1. 扫描 common 目录

```
common/code/*.md      → Applies to: coding（无框架后缀的全部包含）
common/test/*.md      → Applies to: test（无框架后缀的全部包含）
common/*.md           → Applies to: coding, test（根目录文件两个角色都需要）
```

### 2. 扫描 backend 语言目录

读取 `stack.json` 的 `backend.language`，取其值作为 `{LANG}`。若 backend 为 null，跳过此步。

```
{LANG}/code/*.md      → 应用框架过滤后，Applies to: coding
{LANG}/test/*.md      → 应用框架过滤后，Applies to: test
{LANG}/*.md           → Applies to: coding, test
```

### 3. 扫描 frontend 语言目录

读取 `stack.json` 的 `frontend.language`，取其值作为 `{LANG}`。若 frontend 为 null，跳过此步。

```
{LANG}/code/*.md      → Applies to: coding
{LANG}/test/*.md      → Applies to: test
{LANG}/*.md           → Applies to: coding, test
```

### 4. 扫描 web 目录（仅当 frontend 非 null）

```
web/code/*.md         → Applies to: coding, e2e
web/test/*.md         → Applies to: test, e2e
web/*.md              → Applies to: coding, test, e2e
```

## 生成格式

routing-table.md 输出为 Markdown 表格，按角色分组：

```markdown
# Rules Routing Table

> 本文件由 stack-detector 自动生成，记录各 agent 角色应加载的 rules 文件路径。
> conductor 派发 agent 时读取本文件，按角色注入对应路径列表。

- Generated: {ISO timestamp}
- Stack: backend={backend.language}/{backend.framework}, frontend={frontend.language}/{frontend.framework}

## Coding Rules

| # | File | Applies to |
|---|------|-----------|
| 1 | {path} | coding |
| ...

## Test Rules

| # | File | Applies to |
|---|------|-----------|
| 1 | {path} | test |
| ...

## Shared Rules

| # | File | Applies to |
|---|------|-----------|
| 1 | {path} | coding, test |
| ...
```

## 渲染注意事项

1. `{PLUGIN_ROOT}` 渲染时替换为 plugin 的绝对路径
2. 每条路径在渲染时校验文件真实存在，不存在则跳过并加注释 `<!-- skipped: <path> not found -->`
3. 文件按目录扫描的字母序排列，保证每次生成结果一致
4. 如果某目录不存在或为空，对应段输出 "(empty)"
