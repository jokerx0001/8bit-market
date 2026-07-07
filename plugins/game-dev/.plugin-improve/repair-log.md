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
