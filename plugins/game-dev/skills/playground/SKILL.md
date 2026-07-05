---
name: playground
description: 测试 references 路径解析，不要在正式任务中使用
user-invocable: true
---

按顺序执行以下四种方法。**每种方法必须输出结果后才能进入下一种。** 读不到内容就输出"未读到"，不许跳过。

---

## 方法 1：相对路径

Read `references/treasure.md`

输出：
```
=== 方法1：相对路径 ===
结果: {读到则输出内容，否则输出"未读到"}
```

---

## 方法 2：环境变量拼接

Read `${CLAUDE_PLUGIN_ROOT}/references/treasure.md`

输出：
```
=== 方法2：环境变量拼接 ===
结果: {读到则输出内容，否则输出"未读到"}
```

---

## 方法 3：neonbit 方式
获取 plugin 目录的绝对路径作为 `{PLUGIN_ROOT}`（即当前 plugin 根目录）。
Read `${PLUGIN_ROOT}/references/treasure.md`

输出：
```
=== 方法3：neonbit ===
PLUGIN_ROOT: {找到的 plugin 根目录路径}
结果: {读到则输出内容，否则输出"未读到"}
```

