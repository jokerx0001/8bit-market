---
name: web2-dev:frontend-e2e-test
description: |
  前端 Playwright E2E 测试 + 自修复循环。
  coding agent 被 exec spawn 后调用此 skill 完成：
  打开网页 → 执行操作 → 截图/断言 → 收集失败 → 诊断根因 → 修复 → 重新测试。

  <example>
  Context: exec 阶段 7 — 前端开发完成后
  assistant: "coding agent 调用 frontend-e2e-test：启动前端 → Playwright E2E → 自修复。"
  </example>
---

# Frontend E2E Test

Playwright E2E 测试。在真实浏览器中验证用户操作路径。

## Iron Law

```
FAILURE MUST BE DIAGNOSED BEFORE IT IS FIXED.
EVERY FAILURE GETS A SCREENSHOT. NO SCREENSHOT = NO DIAGNOSIS.
```

## 测试范围

对 `{task_dir}/.work/layouts/` 的 UI 设计稿 + `{task_dir}/.work/design.md` 的前端设计，验证：

| 场景 | 覆盖 |
|------|------|
| 页面加载 | 每个页面能正常渲染 |
| 表单交互 | 输入 → 提交 → 验证反馈 |
| 导航流转 | 页面间跳转、路由 |
| 错误处理 | 网络错误、后端返回错误时的 UI 反馈 |
| 状态变更 | 操作后页面状态正确更新 |

## 测试方式

使用 Playwright，测试文件放在 `{task_dir}/.work/e2e/` 下。
参考 `${CLAUDE_PLUGIN_ROOT}/references/web/frontend-e2e.md` 获取模板。

使用 `data-testid` 选择器定位元素——不依赖 CSS 类名或 DOM 结构。

---

## 自修复循环

```
Phase 1: 启动前端 → 运行全量 E2E → 收集结果
  ├── 全部通过 → 返回成功报告
  └── 有失败 → Phase 2

Phase 2: 逐个失败用例系统性循环
  ├── 2a. 读取 {task_dir}/.work/fix-attempts.md 失败经验（告诉自己：不重复错误路径，必须换思路）
  ├── 2b. 查看失败截图 + 错误信息（必须先看到实际渲染状态）
  ├── 2c. 调用 Skill("web2-dev:debug-root-cause") 深度根因分析
  │      → 产出 {task_dir}/.work/debug-analysis-{case}.md（逆向追踪 + 最小验证 + 证据链）
  ├── 2d. 按已验证根因修复：UI 代码问题 → 修复前端代码 / 选择器问题 → 修复测试
  ├── 2e. 重跑该用例 → 通过 → 下一个 / 失败 → 追加失败详情到 fix-attempts.md → 回到 2a
  └── 全部通过 → Phase 3

Phase 3: 重跑全量确认 → 报告
```

### 深度根因分析

每个失败用例的诊断由 `web2-dev:debug-root-cause` 完成，产出 `{task_dir}/.work/debug-analysis-{case}.md`：

- **逆向追踪**：从失败点逐层追到"正确输入→错误输出"的转换点，不猜根因
- **最小验证**：临时修改 → 重跑 → FAIL→PASS → 撤销（未验证的根因 = 猜测）
- **跨轮经验**：每轮修复失败后追加到 `fix-attempts.md`，2a 先读取、避开已验证的错误路径

### 重试限制

| 限制 | 值 |
|------|-----|
| 整体最大轮次 | 5 |
| 同一用例连续同一原因 | 3 轮 → 标记 BLOCKED |
| 截图失败（空白/超时） | 重试 2 次 → BLOCKED |
| 失败经验记录 | 每轮失败追加到 `{task_dir}/.work/fix-attempts.md`（按用例分节 `## {case} 第 {N} 轮`），2a 先读取 |

---

## 输出格式

```
## Frontend E2E Test 报告

### 测试统计
- 总用例: {N}
- 通过: {N}
- 失败: {N}
- 阻塞: {N}

### 页面覆盖
| 页面 | 场景 | 结果 | 轮次 |
|------|------|------|------|
| /register | 正常注册 | ✅ | 1 |
| /register | 邮箱格式错误 | ✅ | 1 |
| /login | 登录成功跳转 | ✅ | 2 |

### 阻塞用例（如有）
| # | 用例 | 根因 | 轮次 | 截图 | 建议 |
|---|------|------|------|------|------|

### 自修复轮次: {N}/5
```

## Red Flags — STOP

- "截图看不清，但我大概知道什么问题" → STOP。看不清 = 重新截 = 不确定 = 不能修
- "跳过截图直接看代码更快" → STOP。截图是 UI 问题的唯一真相来源
- "几个用例失败看起来是同一个原因，一起修" → STOP。逐个击破——不假设根因相同
- "Playwright 选择器不稳定，换个定位方式就行" → STOP。先诊断为什么不稳定，不要跳过根因分析
- "这个元素渲染位置偏了几个像素，不影响功能" → STOP。与设计稿不一致 = 不合格

**以上任一条 → STOP。回到 Phase 2 逐个诊断。**
