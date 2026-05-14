# 技术栈检测规则

按优先级从高到低排列。命中即止（一个槽位只取第一个命中的规则）。

## Backend 检测

| 优先级 | 检测文件 | 匹配条件 | 结果 |
|--------|----------|----------|------|
| 1 | `pom.xml` | 存在且含 `spring-boot` | java (spring-boot) |
| 2 | `build.gradle` / `build.gradle.kts` | 存在且含 `org.springframework.boot` | java/kotlin (spring-boot) |
| 3 | `pom.xml` | 存在（不含 spring-boot） | java |
| 4 | `build.gradle.kts` | 存在且含 `kotlin` | kotlin |
| 5 | `go.mod` | 存在 | golang |
| 6 | `Cargo.toml` | 存在 | rust |
| 7 | `requirements.txt` / `pyproject.toml` / `setup.py` | 存在 | python |
| 8 | `*.csproj` / `*.sln` | 存在 | csharp |
| 9 | `Package.swift` | 存在 | swift |
| 10 | `pubspec.yaml` | 存在且含 `flutter` | dart |
| 11 | `composer.json` | 存在 | php |

## Frontend 检测

| 优先级 | 检测文件 | 匹配条件 | 结果 |
|--------|----------|----------|------|
| 1 | `package.json` | 含 `"vue"` 依赖 | typescript (vue3) |
| 2 | `package.json` | 含 `"react"` 依赖 | typescript (react) |
| 3 | `package.json` | 含 `"@angular/core"` 依赖 | typescript (angular) |
| 4 | `package.json` | 含 `"svelte"` 依赖 | typescript (svelte) |
| 5 | `package.json` | 存在但无上述框架 | typescript |

## 检测方法

1. 从项目根目录开始查找
2. 对 monorepo：优先检测根目录，再检测一级子目录
3. `build.gradle.kts` 中含 `kotlin("jvm")` 或 `kotlin("spring")` → 语言判定为 kotlin
4. `package.json` 中 `dependencies` 或 `devDependencies` 含目标包名即算命中
5. 前端框架检测时，若 `tsconfig.json` 不存在则语言降级为 `javascript`

## 未识别处理

若所有规则均未命中：
- 输出 `未识别`
- 不阻断流程
- 用户可在确认门手动指定

## 特殊情况

- **Monorepo（Java + Vue）**：backend 和 frontend 各自独立检测，两个槽位都填
- **纯后端项目**：frontend = null
- **纯前端项目**：backend = null
- **Kotlin Spring Boot**：`build.gradle.kts` 含 `kotlin("spring")` → backend = kotlin (spring-boot)
