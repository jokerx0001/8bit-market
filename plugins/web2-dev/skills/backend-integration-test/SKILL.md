---
name: web2-dev:backend-integration-test
description: |
  后端集成测试
  <example>
  assistant: "coding agent 调用 backend-integration-test：后端集成测试"
  </example>
---

# Backend Integration Test

后端集成测试。验证业务主流程在真实环境下跑通，数据流转正确。

## Iron Law

```
FAILURE MUST BE DIAGNOSED BEFORE IT IS FIXED.

看到测试失败后第一反应不是"改代码试试"，而是"为什么失败"。
收集完整失败上下文 → 分析根因 → 修复 → 重跑全量确认。
```

## 测试用例

从设计文档推导，**骨架是业务主流程，不是接口清单**：

1. **主流程**：读 `architecture.md` 数据流 + `design.md` 模块交互，画出业务主流程（如 爬取→MQ→消费→入库→精炼→页面查询可见）。沿流程走通，每段断言数据流转正确（A 环节写的数据 B 环节读到一致），不 mock 其他模块
2. **接口契约**：从 `design.md` API 设计节取主流程途经接口的契约——方法/路径/参数/响应结构/错误码
3. **业务规则**：从 `requirements.md` 取核心规则的违反场景（重复/冲突/限制）

用例顺序：先流程，再契约，最后规则。

**主流程硬门（强制）：** 每环成功路径必须走通 **返回体包含**该批次数据（只验 200 不算）。主流程首环（如爬取）依赖外部输入时：

- 真实触发必须产生**有证据的降级结果**：数据到达 → 被过滤/去重 → itemsNew=0，中间必须有记录支撑（日志/DB 证明爬取成功、过滤发生）——"没有新数据"一句话不算证据
- 降级链路有证据后，才允许等价种子数据补"有数据"成功路径，且 消费→落库→查询可见 必须走通
- 首环异常（爬取失败、外部不可达）是链路故障，不是环境受限 → **不得用种子数据替代**，修复或 BLOCKED

任一环成功路径未执行 → BLOCKED，禁止宣布全链路 PASS。

## 测试环境（强制）

- 中间件必须真实（开发环境或 testcontainers），**禁止 Mock / H2**——并发、锁、唯一约束只有真库才有
- 测试数据按中间件自身规则隔离（DB → test schema；Redis → 独立 db/前缀；MQ → 测试 vhost/队列前缀），由测试侧 setup 创建、测后清理，不依赖 ops
- 地址从项目配置读取（ops-local.md 环境地址清单 / 应用测试配置），禁止硬编码
- 集成测试线性执行（单一执行者），不做并行会话共享测试数据

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
  ├── 2c. 调用 Skill("web2-dev:debug-root-cause") 深度根因分析（每个失败用例必须调用——自行内联诊断不算）
  │      → 产出 {task_dir}/.work/debug-analysis-{case}.md（逆向追踪 + 最小验证 + 证据链；不产出文件 = 本轮修复无效）
  ├── 2d. 按已验证根因修复：接口代码问题 → 修复代码 / 测试写法问题 → 修复测试
  ├── 2e. 重跑该用例 → 通过 → 下一个 / 失败 → 追加失败详情到 fix-attempts.md → 回到 2a
  └── 全部通过 → Phase 3

Phase 3: 重跑全量确认 → 报告
```

### 环境受限路径（强制）

成功路径因环境限制无法验证时（如 LLM key 占位 → 精炼成功路径不可执行）**允许跳过**，但必须：

- 给出**实际理由**：具体配置/证据（如"openai_api_key 为占位符，请求返回 401"）——"环境问题"一句话不算理由
- 输出跳过内容：用例 + 环境限制 + 证据，列入 BLOCKED 表

### Phase 2 → Phase 3 硬门（强制）

每轮失败修复后必须：

- [ ] 追加失败详情到 `{task_dir}/.work/fix-attempts.md`（按用例分节 `## {case} 第 {N} 轮`）
- [ ] 每个失败用例必须产出 `{task_dir}/.work/debug-analysis-{case}.md`（见 Phase 2c——诊断一律走 debug-root-cause，无豁免条件）

**机械检查（Phase 3 重跑全量前强制执行，不可跳过）：**

```bash
# 1) 失败经验已记录（有失败用例时必有 case 节）
C=$(grep -c '^## case=' {task_dir}/.work/fix-attempts.md 2>/dev/null || echo 0); test "$C" -ge 1 && echo "ATTEMPTS_OK ($C cases)" || echo "ATTEMPTS_MISSING"
# 2) 每个失败用例有独立 debug-analysis 文件
A=$(ls {task_dir}/.work/debug-analysis-*.md 2>/dev/null | wc -l); test "$A" -ge "$C" && echo "ANALYSIS_OK ($A files)" || echo "ANALYSIS_MISSING (need $C, have $A)"
```

- `ATTEMPTS_MISSING` 或 `ANALYSIS_MISSING` → **STOP。** 回到 Phase 2 补记录（文件不存在就补写，case 没诊断过就补 debug-root-cause）。不记录不得进入 Phase 3——没有失败经验文件的修复记录 = 本轮修复无效。

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

### 用例覆盖
| 用例 | 结果 | 轮次 |
|------|------|------|
| 主流程: 爬取→MQ→消费→落库→精炼→查询可见 | ✅ | 1 |
| 契约: POST /api/v1/users/register 响应结构 | ✅ | 1 |
| 规则: 重复邮箱 409 | ✅ | 2 |

### 阻塞用例（如有）
| # | 用例 | 根因 | 轮次 | 建议 |
|---|------|------|------|------|

### 自修复轮次: {N}/5
```

### 结论硬门（强制）

**结论声明必须与验证范围一致。**

- 核心业务成功路径（如精炼成功回写 is_refined=true、数据经页面数据源查询接口可见）未执行或环境不可验证 → 结论**必须**标注 BLOCKED/部分验证，禁止宣布"全链路通过/PASS"
- 降级路径断言（如 LLM disabled、空批次）只能证明"降级行为存在"，**不能替代成功路径验证**
- 报告完成前自检（Checklist with Consequences）：
  - [ ] 结论中每个"通过"都有对应成功路径的执行证据（日志/DB/接口返回）
  - [ ] "阻塞用例/未验证路径"表列出了所有因环境限制未执行的成功路径
  - [ ] 结论与"阻塞用例"表无矛盾

**任何一项不通过 → 修正结论后重新报告。宣布 PASS 前必须逐项勾选。**

## Red Flags — STOP

- "测试失败不多，直接批量修完再跑" → STOP。逐个用例击破，不一锅端
- "这看起来是环境问题，不是代码问题" → STOP。先诊断再下结论
- "测试写法有问题但功能正常，跳过" → STOP。测试正确性等于代码正确性的证明
- "已经修复了 3 个，剩下的看起来是同一个原因" → STOP。每个用例独立诊断——不做假设
- "根因很明显不用走诊断流程" → STOP。跳过诊断直接改代码 = 本轮无效
- "查询接口 200 就说明数据可见了" → STOP。200 不等于返回体包含该批次数据——必须断言返回内容

**以上任一条 → STOP。回到 Phase 2 逐个用例诊断。**
