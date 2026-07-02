# Ren'Py 文档查询约定

所有 agent（plan 主会话、coding、test-agent）使用同一工具和同一文档源查询 Ren'Py 知识。

## 文档地址

```
https://www.renpy.org/doc/html/
```

## 查询工具

使用 `WebFetch` 工具查询文档。格式：

```
WebFetch(url="https://www.renpy.org/doc/html/{page}.html", prompt="{查询内容}")
```

## 常用文档页面

| 页面 | URL | 何时查询 |
|------|-----|---------|
| Screens | `screens.html` | 写 screen 语句、widget 属性、style |
| Screen Actions | `screen_actions.html` | 按钮 action、bar action、key binding |
| Screen Special | `screen_special.html` | 特殊 screen 名（main_menu, save, load 等） |
| Transforms | `transforms.html` | transform 属性、ATL 动画 |
| Transitions | `transitions.html` | 预定义 transition、自定义 transition |
| Displayables | `displayables.html` | Image、Text、Frame 等 displayable |
| Persistent Data | `persistent.html` | persistent 变量、multi-game persistence |
| Save/Load | `save_load_rollback.html` | 存档系统、FileSave/FileLoad |
| Python | `python.html` | Ren'Py 中的 Python 语句、define/default |
| Labels/Flow | `label.html` | label 定义、jump/call/return |
| Style Properties | `style_properties.html` | 所有 style 属性参考 |
| Audio | `audio.html` | play/music/sound/voice |
| Input | `input.html` | renpy.input()、key binding |
| Config Variables | `config.html` | config.xxx 全局配置变量 |
| Custom Displayables | `udd.html` | Creator-defined displayables |
| CDD | `cdd.html` | Creator-defined displayables (新版) |
| GUI Customization | `gui.html` | gui.rpy 定制指南 |
| Translation | `translation.html` | 多语言翻译 |
| Statement Equivalents | `statement_equivalents.html` | Python 等效语句 |
| Quickstart | `quickstart.html` | 新手入门 |

## 查询模式

1. **查找 API 语法：** 如不确定某个 screen statement 或 action 的准确语法 → `WebFetch` 对应页面
2. **查找属性/参数：** 如不确定 transform 有哪些属性 → 查 `transforms.html`
3. **查找最佳实践：** 如不确定 persist vs save → 查 `persistent.html` + `save_load_rollback.html`
4. **查找错误原因：** 如遇到 Ren'Py 报错 → 用错误信息中的关键词构造查询

## 示例

```
# 查询 screen 的 button 属性
WebFetch(url="https://www.renpy.org/doc/html/screens.html#button", prompt="button 有哪些属性？特别是 action 的用法")

# 查询 transform 动画
WebFetch(url="https://www.renpy.org/doc/html/transforms.html#atl", prompt="如何用 ATL 写一个渐入+滑入的 transform？")
```
