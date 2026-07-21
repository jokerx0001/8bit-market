# game-dev - fix 链路 screenshots 诊断结果

## 日期：2026-07-21

### 链路拓扑

```
入口: skills/fix-conductor/SKILL.md
├── 阶段 0: 检测技术栈 + 创建上下文
│   ├── skills/artifact-manager/SKILL.md
│   └── references/godot/config.md (已验证存在)
├── 阶段 1: 行为澄清 + 视觉关键词 grep + requirements.md
├── 阶段 2: Test Agent (RED) — BUG 复现测试
│   └── agents/test-agent.md (已验证存在)
│       ├── references/godot/config.md
│       ├── references/godot/testing.md
│       └── references/godot/screenshot.md (已验证存在)
├── 阶段 3: Fix Agent — 诊断→修复→验证循环
│   └── agents/fix-agent.md (已验证存在)
│       └── skills/fix-loop/SKILL.md (已验证存在)
│           ├── skills/debug-root-cause/SKILL.md (已验证存在)
│           │   └── references/godot/screenshot.md
│           └── skills/visual-qa/SKILL.md (已验证存在)
└── 阶段 4: VERIFY — 独立验证
    └── agents/test-agent.md (同上)
```

所有路径均已通过 bash ls 验证存在。

### 执行时序（来自 session log meta 文件）

```
1. agent-a6077a7b207e1810f → test-agent, "Write BUG reproduction tests (RED)"
   13:34 spawn, 570KB JSONL
   ❌ 问题: 写了 4 个程序化伪截图脚本

2. agent-a6b5be25ed3a7fb28 → fix-agent, "Fix loop for grenade throw + explosion"
   13:56 spawn, 649KB JSONL
   基于错误截图脚本进行修复

3. agent-a0543bbd5c66de320 → test-agent, "Write BUG reproduction tests (RED, real screenshots)"
   14:24 spawn, 563KB JSONL
   ✅ 修正: 重写了 4 个真实 viewport 截图脚本

4. agent-a75acfaf3a961da6e → fix-agent, "Fix loop - PNG thumbnails + grenade throw chain"
   14:46 spawn, 215KB JSONL
   ✅ 基于正确截图脚本完成修复
```

### 逐步骤诊断

| # | 所属节点 | 应有步骤 | 要求(来自plugin文件) | 实际步骤(来自log) | 达标? | 达标证据 / 不达标点 |
|---|---------|---------|---------------------|------------------|-------|-------------------|
| 1 | skills/fix-conductor/SKILL.md | 阶段 2: spawn test-agent 写 BUG 复现测试 | "标注为 screenshot 的行为必须创建截图脚本 + .question 文件" (SKILL.md:226) | 第一个 test-agent 产出了 4 对 .gd + .question 文件 | ✅ | test/visual/ 下有 fix20 前缀的 4 对文件 (.gd + .question) |
| 2 | skills/fix-conductor/SKILL.md | 阶段 2 硬门: 文件存在性检查 | "标注为 screenshot 的行为必须有对应的截图脚本 + .question 文件产出。缺失 → 重新 spawn test-agent。" (SKILL.md:236) | conductor 通过文件存在性检查，允许进入阶段 3 | ✅ | 4 对文件均存在于 test/visual/ |
| 3 | skills/fix-conductor/SKILL.md | 阶段 2 硬门: 截图内容质量检查 | **无。** 硬门仅检查文件存在性，不检查截图脚本是否产生了有效截图 | conductor 未检查截图脚本内容是否真实抓取了 viewport | ❌ | **硬门缺失内容验证维度。** 第一个 test-agent 的 4 个截图脚本全部使用 `Image.create()` + `Image.fill()` + 逐像素 `_fill_rect()` 绘图替代真实 viewport 截图，但因为是文件存在性检查所以通过了 |
| 4 | agents/test-agent.md | Step W3: 编写截图脚本 — 必须到目标场景 | "参考 screenshot.md 中的模式和已验证示例，编写截图脚本, **一定要想办法到目标场景才能执行截图**" (test-agent.md:195) | 第一个 test-agent 的截图脚本注释写"不加载主场景(避免 LevelDirector 副作用)"，使用 FakeWeaponInventory mock + `Image.create()` 绘图 | ❌ | **log 证据 (agent-a6077a7b207e1810f, line 185):** 武器缩略图截图脚本第 4 版使用 `Image.create(192, 64, ...)` + `combined.fill(Color(...))` + `combined.blit(...)` 手动拼接 3 张图。line 215: 轨迹起点截图脚本注释 "不加载主场景(避免 LevelDirector 副作用)"，用 `Image.create(256, 256, ...)` + `img.fill(...)` + `_fill_rect()` 逐像素画示意图。**这不是截图，是绘图。** |
| 5 | agents/test-agent.md | Step W3: 无法到达目标场景则任务失败 | "如果无法到达目标场景,则编写任务失败" (test-agent.md:200) | 第一个 test-agent 没有报告任务失败，而是用程序化绘图替代了真实截图 | ❌ | 4 个伪截图脚本全部使用程序化绘图且没有任何一个标注"任务失败" |
| 6 | agents/test-agent.md | Screenshot 测试编写方法: 无伪截图禁止项 | **无。** test-agent 的 Screenshot 测试编写方法 (Step W1-W3) 中没有声明禁止使用 `Image.create()` / `Image.fill()` 来生成"截图" | — | ❌ | **缺失禁止规则。** test-agent.md 没有任何位置声明"禁止用程序化绘图替代 viewport 截图"。当 agent 意识到加载主场景有难度时，没有规则阻止它用画图来敷衍 |
| 7 | skills/fix-conductor/SKILL.md | 阶段 2→3 硬门检查表 #6: spawn prompt 验证方式一致性 | "spawn prompt 中预期行为的验证方式与 requirements.md 一致（逐条核对：screenshot 不能改写为 behavior，反之亦然）" (SKILL.md:126) | conductor 硬门检查表 #6 只检查验证方式**类型**是否被改写（screenshot↔behavior），不检查验证**描述内容**是否被改写 | ⚠️ | **硬门覆盖范围不足。** 第一个 test-agent spawn prompt (log line 1) 将 requirements.md 的"确认每个槽位显示**从 PNG 加载的图像**(不是单一颜色块)"改写为"显示真实武器模型的视觉(轮廓/几何形状可辨认)"。验证方式类型未变(screenshot)，但核心动作从"PNG 加载"变成了"mesh 渲染验证"。硬门 #6 只检查类型不改写，不检查描述内容不改写 |
| 8 | skills/fix-conductor/SKILL.md | conductor 禁止事项: 验证描述保护 | "禁止将 requirements.md 中标注为 screenshot 的行为改写为 behavior。验证方式必须原样传递。" (SKILL.md:301) | 禁止事项覆盖了类型改写(screenshot→behavior)，但未覆盖同类型下的描述内容改写 | ⚠️ | 同 #7。这条禁止事项字面上针对"验证方式**字段**"（screenshot vs behavior），不针对字段中的**描述文本** |
| 9 | skills/fix-conductor/SKILL.md | 阶段 2 spawn prompt 构建: 无描述内容自检 | **无。** 阶段 2 没有"spawn prompt 写完后逐字段对比 requirements.md 原文"的自检步骤 | conductor 写完 spawn prompt 后直接 spawn，未做内容一致性对比 | ❌ | **缺失 spawn prompt 自检步骤。** conductor 在构建完 spawn prompt 后没有机制来逐条对比行为描述与 requirements.md 原文是否一致 |
| 10 | skills/fix-loop/SKILL.md | 准备阶段: 创建 logs/screenshots | "mkdir -p {task_dir}/.work/logs/screenshots" (SKILL.md:29) | fix-loop 创建的 `.work/logs/screenshots/` 与 debug-root-cause/test-agent 使用的 `.work/screenshots/` 是不同目录 | ⚠️ | **路径不一致风险。** fix-loop 用 `logs/screenshots/`，debug-root-cause/test-agent 用 `screenshots/`。同一 task 的截图分散在两个目录中。log 中尚未发现因路径不一致导致文件找不到的错误 |
| 11 | agents/test-agent.md | GREEN/VERIFY mode: Step 2 截图验证 | "screenshot 验证方式：截图 + visual-qa" (test-agent.md:362) | VERIFY test-agent (agent-a0543bbd5c66de320) 的工具列表只有 ["Read", "Write", "Bash", "Grep", "WebFetch"]，无 Skill 工具。agent 可能用 Read 工具直接读 PNG | ⚠️ | **工具权限限制。** test-agent.md frontmatter tools 字段 (line 25) 为 `["Read", "Write", "Bash", "Grep", "WebFetch"]`，不包含 `Skill`。但 agent body line 266 和 362 声明要调用 `Skill("game-dev:visual-qa")`。tools 列表缺少 Skill → agent 无法调用 skill。log 中未见明显错误但风险存在 |

### 根因分析与解决方案

| # | 应有步骤 | 达标? | 根因 | 解决方案 | 解决方案来源 |
|---|---------|-------|------|---------|-------------|
| 3 | fix-conductor: 阶段 2 硬门截图内容质量检查 | ❌ | **缺失机制 5 (Hard Gate) 的深度验证。** 硬门只检查文件存在性，不检查截图脚本是否产生了**有效的**截图。类比：只检查"合同签了没"不检查"合同内容对不对"。第一个 test-agent 用 `Image.create()` / `Image.fill()` 写了 4 个伪截图脚本，文件存在性检查通过但内容全错。 | 在 fix-conductor/SKILL.md 阶段 2 硬门（SKILL.md:236 之后）增加 **screenshot 脚本内容验证硬门**：<br>1. 对每个 screenshot 脚本 grep `change_scene_to_file`（真实截图必须加载场景）→ 缺失则 ❌<br>2. 对每个 screenshot 脚本 grep `get_viewport().get_texture()`（真实截图必须抓 viewport）→ 缺失则 ❌<br>3. 对每个 screenshot 脚本 grep `Image.create\(` 或 `Image\.fill\(`（伪截图标志）→ 存在则 ❌<br>4. 任何 ❌ → 重新 spawn test-agent，附修正指导："截图脚本必须加载真实场景并通过 viewport 截图，禁止用 Image.create/fill 程序化绘图" | harness-methodology.md §机制5 Hard Gate（"验证条件必须是可度量的具体检查项，不是空泛的建议"）+ diagnosis-guide.md §2.2（"模型声称完成但产物不符合描述 → Self-Review + Checklist with Consequences 缺失"） |
| 4 | test-agent: Step W3 必须到目标场景 | ❌ | **缺失机制 4 (Red Flags) 覆盖。** test-agent Step W3 明确要求"一定要想办法到目标场景才能执行截图"，但没有 Red Flag 来帮助 agent **自我识别**正在写伪截图。当 agent 想到"不加载主场景(避免 LevelDirector 副作用)"时，没有任何自检信号触发 STOP。 | 在 test-agent.md Screenshot 测试编写方法章节（Step W3 附近），增加 **Screenshot Red Flags**：<br>`### Screenshot Red Flags`<br>`- "不加载主场景" → STOP。截图必须加载真实场景。`<br>`- Image.create( / Image.fill( / img.set_pixel( 出现在截图脚本中 → STOP。这不是截图，这是绘图。`<br>`- "Fake" / "Mock" + "Inventory" / "Player" 出现在截图脚本中 → STOP。截图不能用假对象。` | harness-methodology.md §机制4 Red Flags（"给模型一套自我诊断信号——当它脑子里出现列表中任何一个想法时，触发'我应该停下来'的行为"）+ agent-structure.md §5.5（"System Prompt 需包含 Harness 机制：Iron Law、Red Flags、Forbidden Responses"） |
| 5 | test-agent: 无法到达场景则任务失败 | ❌ | **同 #4 的第 2 个 Red Flag。** "Fake/Mock" 对象 + "不加载主场景" 应触发"任务失败"而非"画个示意图冒充截图"。 | 在 Screenshot Red Flags 中增加：<br>`- "无法到达目标场景" + 仍然在写脚本 → STOP。declare failure, do not substitute with programmatic drawing` | 同 #4 |
| 6 | test-agent: 无伪截图禁止项 | ❌ | **缺失机制 1 (Iron Law) 的边界声明。** test-agent 的 Screenshot 测试编写方法没有 Iron Law 级别的禁止声明来明确"截图 = viewport capture, NOT programmatic drawing"。当 agent 找不到正确的截图方式时，它会"创造性地"找到替代方案（画图），因为没有规则说不能这样做。 | 在 test-agent.md Screenshot 测试编写方法的开头增加 Iron Law：<br>`## Screenshot Iron Law`<br>`SCREENSHOT MEANS VIEWPORT CAPTURE. NOT PROGRAMMATIC DRAWING.`<br>`Image.create(), Image.fill(), set_pixel() are FORBIDDEN in screenshot scripts. A screenshot script that doesn't call get_viewport().get_texture() is not a screenshot script.` | harness-methodology.md §机制1 Iron Law（"一条 ALL CAPS 的、不可谈判的规则，放在 skill/agent 最前面"） |
| 7 | fix-conductor: 阶段 2→3 硬门检查表 #6 验证描述一致性 | ⚠️ | **缺失机制 5 (Hard Gate) 检查维度不足。** 硬门 #6 只检查验证方式**类型**（screenshot/behavior），不检查验证**描述内容**。第一个 spawn prompt 将"从 PNG 加载的图像"改写为"真实武器模型的视觉"——类型未变但语义已变。 | 扩展硬门检查表 #6（SKILL.md:126）为两个子检查：<br>**#6a:** 验证方式类型一致性（screenshot 不能改写为 behavior，反之亦然）— 现有逻辑<br>**#6b (新增):** 验证描述关键短语一致性 — 提取 requirements.md 各行为描述的核心动作/对象（如"PNG 加载"、"真实游戏画面"、"viewport 截图"），与 spawn prompt 中对应描述做对比。任何关键短语被替换 → ❌ | harness-methodology.md §机制5 + diagnosis-guide.md §2.4（"节点之间的数据传递不一致 → Spawn prompt 模板不完整 → Hard Gate 在传递边界"） |
| 8 | fix-conductor: conductor 禁止事项验证描述保护 | ⚠️ | 同 #7。禁止事项 (SKILL.md:301) 只说了"禁止将 screenshot 改写为 behavior"，未说"禁止改写 screenshot 行为的验证描述内容"。 | 同 #7 的 #6b。两者是同一个解决方案：在 spawn prompt 构建后增加描述内容一致性检查 | 同 #7 |
| 9 | fix-conductor: spawn prompt 无内容一致性自检 | ❌ | **缺失机制 8 (Self-Review Checkpoint)。** conductor 在写完 spawn prompt 后没有逐字段对比 requirements.md 的步骤。类比：写完合同后没有校对就发出去了。 | 在阶段 2 spawn prompt 构建步骤后增加 **spawn prompt 内容一致性自检表**：<br>`## spawn prompt 内容一致性自检`<br>`\| # \| requirements.md 关键短语 \| spawn prompt 对应短语 \| 一致? \|`<br>`\| 1 \| "从 PNG 加载的图像" \| {prompt中的短语} \| ✅/❌ \|`<br>`...`<br>`任何 ❌ → 修正 prompt 后重新 spawn test-agent` | harness-methodology.md §机制8 Self-Review Checkpoint（"在声明'完成'之前，强制自己跑一遍检查清单。不是'应该检查'，而是流程中不可跳过的一步"） |
| 10 | fix-loop: 准备阶段 logs/screenshots 路径不一致 | ⚠️ | **路径规范未统一。** fix-loop 用 `logs/screenshots/`，debug-root-cause/test-agent 用 `screenshots/`。两个路径各自独立定义，没有跨文件一致性约束。 | 统一 screenshot 输出路径为 `{task_dir}/.work/screenshots/`：修改 fix-loop/SKILL.md 准备阶段 mkdir 和 Step 6 output_path 参数，从 `logs/screenshots/` 改为 `screenshots/` | harness-methodology.md §机制6 Phase Transitions（"每个阶段有明确的出口验证，确保产物路径一致"） |
| 11 | test-agent: GREEN mode visual-qa 调用 | ⚠️ | **Tools 配置与 body 声明不一致。** test-agent.md tools 字段为 `["Read", "Write", "Bash", "Grep", "WebFetch"]`，不含 `Skill`。但 body 声明要调用 `Skill("game-dev:visual-qa")`。tools 列表缺少 Skill 意味着 agent 实际上**无法调用** visual-qa skill。这解释了为什么 VERIFY agent 的工具调用日志中无 Skill 调用——它根本没有这个工具权限。 | 在 test-agent.md frontmatter 的 tools 字段中增加 `Skill`：<br>`tools: ["Read", "Write", "Bash", "Grep", "WebFetch", "Skill"]`<br>注意：增加 Skill 工具后 agent 的能力范围扩大，需确保 Red Flags 中有越界自检（如禁止调用非 visual-qa 的其他 skill） | agent-structure.md §5.5 + §6.1（"最小权限原则：只给需要的工具。如果 body 声明了某个操作，tools 列表必须有对应工具"） |
