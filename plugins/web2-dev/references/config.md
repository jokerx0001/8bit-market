# Web2-dev Configuration

## 产物目录

```
dev_dir: .web2-dev
```

所有设计文档和进度跟踪存放在 `.web2-dev/` 下。

## 目录结构

```
.web2-dev/
├── current-state.json      # 计数器状态
├── requirements.md         # 项目级需求（跨任务持久）
├── architecture.md         # 项目级架构（跨任务持久，--update 合并）
├── new-{N}/                # 新项目任务
├── feat-{N}/               # 新功能任务
├── refactor-{N}/           # 重构任务
├── fix-{N}/                # BUG 修复任务
├── test-lessons.md         # 测试经验积累
└── coding-lessons.md       # 编码经验积累
```

## 技术栈检测

通过文件特征识别：requirements.txt/go.mod/package.json/pom.xml 等。
详见 skills/stack-detector/SKILL.md。
