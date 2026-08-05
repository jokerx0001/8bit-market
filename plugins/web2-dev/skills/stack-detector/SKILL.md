---
name: web2-dev:stack-detector
description: |
  技术栈检测 skill。分析项目文件特征，识别编程语言和框架。
  产出 stack.json 和 routing-table.md，供后续 skill 选择对应 rules。

  <example>
  Context: orchestrator 阶段 0
  assistant: "检测到 Python/FastAPI 技术栈 → 加载对应 rules。"
  </example>
---

# Stack Detector

识别项目技术栈，生成 rules 路由表。

## 检测规则

分析项目根目录文件特征：

| 特征 | 语言 | 框架推断 |
|------|------|---------|
| `requirements.txt` + `*.py` | Python | FastAPI / Flask / Django（按 import 判断） |
| `go.mod` + `*.go` | Go | Gin / Echo / Chi（按 go.mod 依赖判断） |
| `package.json` + `*.ts` | TypeScript | Express / NestJS / Next.js |
| `pom.xml` + `*.java` | Java | Spring Boot |
| `Cargo.toml` + `*.rs` | Rust | Actix / Axum |
| `build.gradle*` + `*.kt` | Kotlin | Spring Boot / Ktor |
| `composer.json` + `*.php` | PHP | Laravel / Symfony |
| `pubspec.yaml` + `*.dart` | Dart | Shelf / Serverpod |
| `*.csproj` + `*.cs` | C# | ASP.NET |
| `CMakeLists.txt` + `*.cpp` | C++ | Crow / Drogon |
| `Package.swift` + `*.swift` | Swift | Vapor |
| `cpanfile` + `*.pl` | Perl | Mojolicious / Dancer2 |
| `package.json` + `*.vue/*.tsx/*.jsx` | Web | Vue / React（按依赖判断） |

## 检测流程

1. 用 Glob/Grep 扫描项目根目录的特征文件
2. 结合 pip freeze / go.mod / package.json 等确认框架
3. 输出检测结果，**必须向用户确认**：

```
## 技术栈检测结果

语言: Python 3.12
框架: FastAPI
数据库: PostgreSQL（从 CLAUDE.md）

确认后回复 OK，或指定正确的技术栈。
```

**强制确认门：未收到用户 OK 确认前不落盘。**

## 产出

### stack.json
```json
{
  "language": "python",
  "framework": "fastapi",
  "database": "postgresql",
  "frontend": "react"
}
```

### routing-table.md
```markdown
| 语言 | rules 路径 |
|------|-----------|
| python | ${CLAUDE_PLUGIN_ROOT}/references/rules/python/ |
```

## 约束

- 不猜测——不确定时询问用户
- 不跳过确认门
- 检测结果必须落盘到 task_dir
