# Routing Table 渲染模板

本文件定义了 routing-table.md 的渲染规则。stack-detector 根据 stack.json 中的语言字段选取对应段落渲染。

## 模板结构

routing-table.md 由以下段组成：
1. 头部（固定）
2. common 段（所有项目都有）
3. backend 段（按 backend.language 选取）
4. frontend 段（按 frontend.language 选取）
5. web 段（仅当 frontend 非 null 时）

## 头部模板

```markdown
# Rules Routing Table

> 本文件由 stack-detector 自动生成，记录各 agent 角色应加载的 rules 文件路径。
> conductor 派发 agent 时读取本文件，按角色注入对应路径列表。

- Generated: {ISO timestamp}
- Stack: backend={backend.language}/{backend.framework}, frontend={frontend.language}/{frontend.framework}
```

## Common 段（所有项目）

```markdown
## Common Rules (所有角色共享)

| # | File | Applies to |
|---|------|-----------|
| 1 | {PLUGIN_ROOT}/references/rules/common/coding-style.md | coding, test |
| 2 | {PLUGIN_ROOT}/references/rules/common/documentation.md | coding |
| 3 | {PLUGIN_ROOT}/references/rules/common/error-handling.md | coding, test |
| 4 | {PLUGIN_ROOT}/references/rules/common/naming-conventions.md | coding, test |
| 5 | {PLUGIN_ROOT}/references/rules/common/performance.md | coding |
| 6 | {PLUGIN_ROOT}/references/rules/common/security.md | coding, test |
| 7 | {PLUGIN_ROOT}/references/rules/common/testing.md | test |
```

## Backend 段

按 `backend.language` 选取。`{LANG}` 替换为实际语言目录名。

```markdown
## Backend Rules ({LANG})

| # | File | Applies to |
|---|------|-----------|
| 1 | {PLUGIN_ROOT}/references/rules/{LANG}/coding-style.md | coding |
| 2 | {PLUGIN_ROOT}/references/rules/{LANG}/error-handling.md | coding |
| 3 | {PLUGIN_ROOT}/references/rules/{LANG}/naming-conventions.md | coding |
| 4 | {PLUGIN_ROOT}/references/rules/{LANG}/performance.md | coding |
| 5 | {PLUGIN_ROOT}/references/rules/{LANG}/security.md | coding |
| 6 | {PLUGIN_ROOT}/references/rules/{LANG}/testing.md | test |
| 7 | {PLUGIN_ROOT}/references/rules/{LANG}/tooling.md | coding |
```

## Frontend 段

按 `frontend.language` 选取（通常是 `typescript`）。

```markdown
## Frontend Rules ({LANG})

| # | File | Applies to |
|---|------|-----------|
| 1 | {PLUGIN_ROOT}/references/rules/{LANG}/coding-style.md | coding |
| 2 | {PLUGIN_ROOT}/references/rules/{LANG}/error-handling.md | coding |
| 3 | {PLUGIN_ROOT}/references/rules/{LANG}/naming-conventions.md | coding |
| 4 | {PLUGIN_ROOT}/references/rules/{LANG}/performance.md | coding |
| 5 | {PLUGIN_ROOT}/references/rules/{LANG}/security.md | coding |
| 6 | {PLUGIN_ROOT}/references/rules/{LANG}/testing.md | test |
| 7 | {PLUGIN_ROOT}/references/rules/{LANG}/tooling.md | coding |
```

## Web 段（仅当 frontend 非 null）

```markdown
## Web Rules

| # | File | Applies to |
|---|------|-----------|
| 1 | {PLUGIN_ROOT}/references/rules/web/accessibility.md | coding, e2e |
| 2 | {PLUGIN_ROOT}/references/rules/web/css.md | coding |
| 3 | {PLUGIN_ROOT}/references/rules/web/html.md | coding |
| 4 | {PLUGIN_ROOT}/references/rules/web/performance.md | coding |
| 5 | {PLUGIN_ROOT}/references/rules/web/security.md | coding, test |
```

## 渲染规则

1. `{PLUGIN_ROOT}` 在渲染时替换为 plugin 的**绝对路径**（conductor 在派发前解析）
2. `{LANG}` 替换为 stack.json 中对应的 language 值
3. 若 backend 为 null → 跳过 Backend 段
4. 若 frontend 为 null → 跳过 Frontend 段和 Web 段
5. e2e 段：仅当 frontend 槽位非 null 时输出（无前端则无 e2e）

## 路径有效性

每条路径在渲染时校验文件是否真实存在于 `<plugin_root>/references/rules/<rel>`：
- 存在 → 写入
- 不存在 → 跳过该条并在末尾加注释 `<!-- skipped: <path> not found -->`

例：rules 中没有 `cpp/security.md`，渲染时该条被跳过并加注释。
