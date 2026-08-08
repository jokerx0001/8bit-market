---
name: web2-dev:backend-integration-test
description: |
  后端 API 集成测试 + 自修复循环。
  coding agent 被 exec spawn 后调用此 skill 完成：
  启动服务 → 运行 API 测试 → 收集失败 → 诊断根因 → 修复 → 重新测试 → 全部通过。

  <example>
  Context: exec 阶段 3 — 所有任务 TDD 完成后
  assistant: "coding agent 调用 backend-integration-test：启动服务 → 跑测试 → 自修复。"
  </example>
---

# Backend Integration Test

后端 API 集成测试。验证每个接口在实际运行环境中返回正确结果。

## Iron Law

```
FAILURE MUST BE DIAGNOSED BEFORE IT IS FIXED.

看到测试失败后第一反应不是"改代码试试"，而是"为什么失败"。
收集完整失败上下文 → 分析根因 → 修复 → 重跑全量确认。
```

## 测试范围

对 `{task_dir}/.work/design.md` 中每个模块的 API 设计节，验证：

| 场景 | 覆盖 |
|------|------|
| 正常请求 | 每个接口至少 1 个成功场景 |
| 参数验证 | 必填字段缺失、格式错误 |
| 业务规则 | 重复注册、库存不足等 |
| 鉴权 | 未登录、权限不足（如适用） |

## 测试方式

使用项目自身的测试框架，脚本放在 `{task_dir}/.work/integration/` 下。
参考 `${CLAUDE_PLUGIN_ROOT}/references/web/backend-testing.md` 获取各语言模板。

---

## 自修复循环

```
Phase 1: 启动服务 → 运行全量测试 → 收集结果
  ├── 全部通过 → 返回成功报告
  └── 有失败 → Phase 2

Phase 2: 逐个失败用例系统性循环
  ├── 2a. 读取 {task_dir}/.work/fix-attempts.md 失败经验（告诉自己：不重复错误路径，必须换思路）
  ├── 2b. 收集失败上下文（错误信息、响应内容、预期值）
  ├── 2c. 调用 Skill("web2-dev:debug-root-cause") 深度根因分析
  │      → 产出 {task_dir}/.work/debug-analysis-{case}.md（逆向追踪 + 最小验证 + 证据链）
  ├── 2d. 按已验证根因修复：接口代码问题 → 修复代码 / 测试写法问题 → 修复测试
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
| 阻塞路径不阻塞其他路径 | 继续其他用例 |
| 失败经验记录 | 每轮失败追加到 `{task_dir}/.work/fix-attempts.md`（按用例分节 `## {case} 第 {N} 轮`），2a 先读取 |

**全部阻塞 → 报告 exec，列出所有阻塞用例和根因。**

---

## 输出格式

```
## Backend Integration Test 报告

### 测试统计
- 总用例: {N}
- 通过: {N}
- 失败: {N}
- 阻塞: {N}

### API 覆盖
| 接口 | 场景 | 结果 | 轮次 |
|------|------|------|------|
| POST /api/v1/users/register | 正常注册 | ✅ | 1 |
| POST /api/v1/users/register | 重复邮箱 | ✅ | 2 |
| GET /api/v1/users/{id} | 查询存在用户 | ✅ | 1 |

### 阻塞用例（如有）
| # | 用例 | 根因 | 轮次 | 建议 |
|---|------|------|------|------|

### 自修复轮次: {N}/5
```

## Red Flags — STOP

- "测试失败不多，直接批量修完再跑" → STOP。逐个用例击破，不一锅端
- "这看起来是环境问题，不是代码问题" → STOP。先诊断再下结论
- "测试写法有问题但功能正常，跳过" → STOP。测试正确性等于代码正确性的证明
- "已经修复了 3 个，剩下的看起来是同一个原因" → STOP。每个用例独立诊断——不做假设
- "根因很明显不用走诊断流程" → STOP。跳过诊断直接改代码 = 本轮无效

**以上任一条 → STOP。回到 Phase 2 逐个用例诊断。**
