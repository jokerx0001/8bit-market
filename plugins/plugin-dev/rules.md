# Plugin Patterns

## Design Patterns
1. Skill 做协调，Agent 做执行
 - Skill 在主会话运行，有 Agent/Skill 工具，适合编排
 - Agent 是叶子节点工人，接收任务、干活、汇报
2. Agent 层级永远是扁平的
 - 主会话 → Agent（只有一层）
 - 永远不要 Agent → Agent
3. 一个职责一个组件，不重复
 - 如果 skill 和 agent 描述同一件事，合并为一个
4. Command 是入口，Skill 是大脑，Agent 是手脚
 - Command 触发 Skill
 - Skill 决定做什么、按什么顺序
 - Agent 被 Skill 指挥去执行具体工作

