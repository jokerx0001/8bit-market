# Lessons Format

`test-lessons.md` 和 `coding-lessons.md` 的记录格式契约。collect-lessons skill 按此格式写入。

## 文件位置

```
{dev_dir}/test-lessons.md    # 测试相关经验
{dev_dir}/coding-lessons.md  # 编码相关经验
```

## 文件格式

每个文件由多个任务节组成，按时间顺序追加。同一任务（feat-N / fix-N / refactor-N）只出现一次节——后续追加内容合并到同一节。

```markdown
# {Test | Coding} Lessons

## {kind}-{N}: {任务简述}
> 日期: YYYY-MM-DD

### {问题标题}
- **问题**: {具体遇到的问题描述}
- **原因**: {根本原因}
- **解决**: {解决方案}

### {问题标题}
- **问题**: ...
- **原因**: ...
- **解决**: ...

---
```

## 分类规则

| 问题类型 | 归入文件 |
|---------|---------|
| 测试框架使用问题（assert 方法、选择器语法、测试发现机制、测试运行器行为） | test-lessons.md |
| 测试配置问题（SDK/CLI 路径、环境变量、测试隔离） | test-lessons.md |
| 源码语法/API 使用问题 | coding-lessons.md |
| 框架行为问题（生命周期、状态管理、UI 系统） | coding-lessons.md |
| 资源文件格式问题（场景文件、资源引用） | coding-lessons.md |
| 工作流/工具链问题（agent 协作、进度恢复） | 不记录 |

技术栈特定的识别细节由 `references/{tech}/config.md` 的 `## 已知坑` 和 sesion 上下文提供，
不在此文件中硬编码。

## CLAUDE.md 更新规则

项目的 CLAUDE.md 只记录**高频或影响大的经验**，格式简洁：

```markdown
## {tech} 开发经验

- **{问题}** → {解决方案一行总结}
```

优先复用已有的 `## .*开发经验` 节（兼容历史数据），不存在时新建 `## {tech} 开发经验`。
不重复记录 test-lessons.md 和 coding-lessons.md 中已有的详细内容——CLAUDE.md 是快速索引。
