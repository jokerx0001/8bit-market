# Lessons Format

`test-lessons.md` 和 `coding-lessons.md` 的记录格式契约。collect-lessons skill 按此格式写入。

## 文件位置

```
.renpy-dev/test-lessons.md    # 测试相关经验
.renpy-dev/coding-lessons.md  # 编码相关经验
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
| 测试框架使用问题（testcase/testsuite 语法、assert 用法、click id 失败） | test-lessons.md |
| 测试配置问题（RENPY_SDK、renpy.sh、测试发现机制） | test-lessons.md |
| 测试隔离问题（测试间状态污染、persistent 数据残留） | test-lessons.md |
| Ren'Py 语法/API 使用问题（screen 语法、label jump、python 块） | coding-lessons.md |
| Ren'Py 框架行为问题（回滚、存档、persistent、样式继承） | coding-lessons.md |
| Ren'Py 组件使用问题（widget id、布局容器、样式属性） | coding-lessons.md |
| 工作流/工具链问题（agent 协作、进度恢复） | 不记录 |

## CLAUDE.md 更新规则

项目的 CLAUDE.md 只记录**高频或影响大的经验**，格式简洁：

```markdown
## Ren'Py 开发经验

- **{问题}** → {解决方案一行总结}
```

不重复记录 test-lessons.md 和 coding-lessons.md 中已有的详细内容——CLAUDE.md 是快速索引。
