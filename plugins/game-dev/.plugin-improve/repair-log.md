### 第 1 轮（2026-07-06）

- **节点：** skills/exec/SKILL.md
- **问题：** #2, #3, #6, #7, #8, #9, #10, #12, #17 — 日志铁律缺失、检查规则引用而非嵌入、VERIFY 无硬门、边界检查非独立门、REFACTOR 无触发规则、write-tutorial 无硬门
- **修复：**
  1. 在步骤 6 开头增加"日志铁律：spawn 返回后第一件事是追加日志"和"硬门：每个阶段不可跳过"
  2. 增加"回显确认（硬门）"块，初始化时回显已读取的参考文件清单
  3. 步骤 6b (RED) 嵌入逐项 checkbox 检查清单，日志提前到检查之前
  4. 步骤 6c (GREEN) 嵌入逐项 checkbox 检查清单，增加"GREEN 全绿不是跳过 VERIFY 的理由"硬门
  5. 步骤 6d (VERIFY) 嵌入逐项 checkbox 检查清单，日志提前到检查之前
  6. 步骤 6e (边界检查) 标题改为"独立质量门"，增加"对每个任务强制执行"声明，增加日志格式和 tdd-iterations.md 追加指令，通用检查增加 git diff 和 @abstract pass 例外说明
  7. 步骤 6f (REFACTOR) 增加"REFACTOR 触发规则"表（边界违规/多文件/多轮迭代→必须REFACTOR）
  8. 步骤 6g 嵌入逐项 checkbox 检查清单
  9. 步骤 10 (write-tutorial) 增加硬门声明
  10. Red Flags 增加 4 条新信号
- **来源：** diagnosis-result.md 第 2-17 行根因分析；harness-methodology.md 机制 #1, #3, #4, #6, #7, #8, #11, #13, #15
- **结果：** 待验证

---

- **节点：** agents/coding.md
- **问题：** #24 — "禁止 pass"规则未区分 @abstract stub
- **修复：** 规则2从"不允许 pass、# TODO 或 NotImplementedError"改为"不允许 # TODO、NotImplementedError、非 abstract 方法中的 pass（@abstract 方法的 pass stub 作为语言要求的占位符除外——但确保子类 override 了该方法）"
- **来源：** agent-structure.md §规则清晰性
- **结果：** 待验证

---

- **节点：** references/plan-format.md
- **问题：** #19, #20, #23 — grep 自检不扫描 class 名、方法名、Godot API 模式
- **修复：**
  1. 新增"扫描 Godot 代码级 API"grep 命令（func、connect、queue_free、_ready 等）
  2. 新增"扫描 PascalCase 标识符"grep 命令
  3. 新增"扫描 snake_case 标识符"grep 命令
  4. 格式校验清单增加 4 个对应 checkbox 条目
  5. 增加"语义复查"人工步骤
- **来源：** plan-format.md §禁止内容清单；diagnosis-result.md #19, #20, #23
- **结果：** 待验证

---

- **节点：** skills/exec/references/exec-logging.md
- **问题：** #5, #13, #18 — 双重日志源冲突，exec 和 agent 写同一文件但职责不清
- **修复：** 在文件开头增加"日志职责分离"表，明确：exec 写 spawn/check/判定记录，coding agent 写诊断过程记录。两者写同一文件但职责不重叠。
- **来源：** skill-structure.md §日志分离；diagnosis-result.md #5
- **结果：** 待验证

---

### 第 2 轮（2026-07-14）

- **节点：** skills/plan/SKILL.md
- **问题：** #8 — grill-interview.md 不存在时 plan 自行编造创建。refactor 流程无 grill 步骤，plan 不应自行补文件。
- **修复：** 步骤3 "用户描述澄清" 从简单的文件列表改为按 kind 的三行决策表（feat/refactor/fix），明确各模式下 grill-interview.md 的来源和"不存在时"的替代方案。增加 Red Flag："grill-interview.md 不存在，我来整理一份" → STOP。铁律：refactor/fix 模式绝不自行创建 grill-interview.md。
- **来源：** diagnosis-result.md #8 根因分析
- **结果：** 待验证

---

- **节点：** skills/refactor-conductor/SKILL.md
- **问题：** #8 补充 — refactor-conductor 未声明 grill-interview.md 由谁创建
- **修复：** 步骤2（写入 impact.md）后增加注意："refactor 流程不创建 grill-interview.md。impact.md 的'重构目标'节包含用户原始描述，plan 以 impact.md 作为用户上下文来源。"
- **来源：** diagnosis-result.md #8
- **结果：** 待验证

---

- **节点：** skills/domain-modeling/SKILL.md
- **问题：** #10, #18, #19 — "容错与配置校验"被列为独立模块，违反"可独立建设、独立验证"标准
- **修复：** 步骤2 增加"横切关注点不作为独立模块"规则（含判断标准）。防遗漏自查增加检查项："有没有模块自述横切？→ 拆散归属。"
- **来源：** diagnosis-result.md #10, #18, #19
- **结果：** 待验证

---

- **节点：** skills/exec/SKILL.md
- **问题：** #25, #35 — .work/coding/ 空无一物；#26 — exec 直接修改 test 文件
- **修复：** GREEN 检查清单增加 `.work/coding/` 日志检查项。增加 test bug 处理规则：exec 不直接改 test 文件，重新 spawn test-agent 修复。
- **来源：** diagnosis-result.md #25, #35, #26
- **结果：** 待验证

---

- **节点：** agents/coding.md
- **问题：** #25, #35 — 未保存测试日志到 .work/coding/；#33 — 初始化摘要未持久化；#39 — tdd-iterations.md 充当设计文档
- **修复：** 核心铁律增加第5条"每次测试运行必须保存原始输出到 .work/coding/"。启动初始化增加步骤6"初始化摘要写入 init.log"。Step 2c 增加格式约束"根因分析不超过 5 行，禁止写入实现计划/架构决策/代码片段"。
- **来源：** diagnosis-result.md #25, #35, #33, #39
- **结果：** 待验证

---

- **节点：** skills/exec/references/exec-logging.md
- **问题：** #39 — coding agent 在 tdd-iterations.md GREEN 条目写入 44 行实现方案文档
- **修复：** GREEN 条目格式后增加长度限制："coding agent 的 GREEN 条目总计不超过 40 行。禁止写入：实现计划、实现细节、架构决策。"
- **来源：** diagnosis-result.md #39
- **结果：** 待验证

---

- **节点：** references/plan-format.md
- **问题：** #15 — 任务列表被包裹在代码块中
- **修复：** 任务列表格式模板后增加约束："任务列表不使用代码块（\`\`\`）包裹。AI 任务列表项是普通 markdown 无序列表。"
- **来源：** diagnosis-result.md #15
- **结果：** 待验证

---

- **节点：** skills/plan/SKILL.md
- **问题：** #17 — logic 任务缺少行为语言示例
- **修复：** 好/坏对照增加一组 logic 任务示例："❌ 实现关卡剧本的可配置数据 schema: Inspector 中可编辑..." vs "✅ 关卡设计师在编辑器中配置关卡剧本..."
- **来源：** diagnosis-result.md #17
- **结果：** 待验证
