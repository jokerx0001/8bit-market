# Ren'Py 技术栈配置

game-dev orchestrator 通过读项目 CLAUDE.md 检测技术栈。当 CLAUDE.md 中出现 "Ren'Py" / "renpy" 时加载本文件。

---

## 项目检测

- **CLAUDE.md 关键词**: `Ren'Py`, `renpy`
- **验证**: `game/` 目录存在且包含 `*.rpy` 文件

## 产物目录

- **根目录**: `.renpy-dev/`
- **任务目录格式**: `.renpy-dev/{kind}-{N}/`
- **计数器**: `feat`, `refactor`, `fix`

## 测试

### 环境检测

```bash
echo $RENPY_SDK && test -x "$RENPY_SDK" && echo "SDK_OK" || echo "SDK_MISSING"
ls game/tests/ 2>/dev/null && echo "TESTS_OK" || echo "TESTS_MISSING"
grep -rl "teardown:" game/tests/ 2>/dev/null | xargs grep -l "exit" 2>/dev/null && echo "EXIT_OK" || echo "EXIT_MISSING"
```

### 测试命令

```bash
# 全量运行
renpy.sh <project> test --report-detailed

# 指定 testsuite
renpy.sh <project> test <testsuite> --report-detailed

# 单个 testcase
renpy.sh <project> test <testsuite>::<testcase> --report-detailed
```

### 输出解析

- 搜索 `During testcase execution:` 段落获取失败详情
- 退出码: `0` = 全部通过

### 已知坑

- **teardown: exit 必须存在** — 没有则 `renpy test` 进程永不退出，TDD 循环卡死
- **sensitive False 的 button 文本不可被测试框架搜索** — 必须用 `id` 选择器

## 源码

- **脚本路径**: `game/**/*.rpy`
- **测试路径**: `game/tests/test_*.rpy`
- **不修改**: `game/libs/`, `game/tl/`

## 文档

- **官方文档**: `https://www.renpy.org/doc/html/`
- **查询方式**: `WebFetch` + `curl` fallback
- **常用页面**: 见 `references/renpy/docs.md`
