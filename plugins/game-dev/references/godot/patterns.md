# Godot 架构映射指引

plan 步骤 7（架构设计）时读取本文件。本文件回答：**领域模型中的模式，在 Godot 中用什么构造来表达？**

所有规则均来自 [Godot 官方最佳实践](https://docs.godotengine.org/en/stable/tutorials/best_practices/index.html)，每条标注来源页面。

---

## 一、核心设计哲学

Godot 以场景树为骨架，以**单一职责**和**封装**为原则，将"场景 + 脚本"视为 OOP 中的类来组织代码。

> 来源：[Introduction](https://docs.godotengine.org/en/stable/tutorials/best_practices/introduction_best_practices.html)

| OOP 原则 | 在 Godot 中的含义 |
|----------|------------------|
| 单一职责 | 每个场景/节点只做一件事 |
| 封装 | 场景自包含，不依赖外部环境的具体细节 |
| SOLID | 脚本和场景作为引擎类的扩展，应遵守全部 SOLID 原则 |
| DRY / KISS / YAGNI | 同样适用 |

> 来源：[Scene Organization](https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html)

---

## 二、构造选型速查

> 综合自：[Scenes vs Scripts](https://docs.godotengine.org/en/stable/tutorials/best_practices/scenes_versus_scripts.html)、[Autoloads vs Regular Nodes](https://docs.godotengine.org/en/stable/tutorials/best_practices/autoloads_versus_regular_nodes.html)、[Node Alternatives](https://docs.godotengine.org/en/stable/tutorials/best_practices/node_alternatives.html)、[Data Preferences](https://docs.godotengine.org/en/stable/tutorials/best_practices/data_preferences.html)

### 游戏专属概念 → 场景（Scene）

官方原话："如果希望创建一个特定于自己游戏的概念，那么它应该始终是一个场景。"

场景是声明式的节点组合，性能优于脚本（序列化批量创建），安全性更高。

### 跨项目复用工具 → 脚本类（class_name）

适用于可跨项目复用的基础工具，注册 `class_name` 后出现在编辑器创建对话框。如果同时希望保留场景的声明式结构，可以在脚本中用 `const MyScene = preload(...)` 引用场景。

### 宽域系统（任务/对话等）→ Autoload

仅当同时满足以下条件才用 Autoload：
1. 系统内部自行管理所有数据
2. 需要全局可访问
3. 应独立存在（不依赖特定场景）

**Autoload 不一定是单例**——可以手动实例化副本。Godot 4.1+ 的 `static func` 和 `static var` 让工具库可以不创建 Autoload 实例。

不满足上述条件的 → 优先用普通节点，逻辑局限在场景内。

### 共享数据（多实体读写同一数据）→ Resource（.tres）

自定义 `Resource` 类型来共享数据。和节点属性的区别：
- Resource：可序列化、可在 Inspector 编辑、可被多个对象引用同一实例、不占用场景树
- 节点属性：局限在单个场景内、适合场景私有状态

### 纯数据结构（不需要场景树生命周期）→ Object / RefCounted / Resource

按复杂度递增：
| 基类 | 特点 | 适用场景 |
|------|------|---------|
| `Object` | 最轻量，手动管理内存 | 节点内部批量管理的子数据结构 |
| `RefCounted` | 自动引用计数 | 大多数需要自定义数据类的情况 |
| `Resource` | RefCounted + 序列化 + Inspector | 需要在编辑器配置的数据 |

官方以 `Tree` 节点为例：视觉渲染由节点完成，但数据层由 `TreeItem`（继承 Object）构成——"Rather than working with the entire Node library, one creates an abbreviated set of Objects"。

### 数据容器选型（Array / Dictionary / Object）

| 容器 | 快 | 慢 | 适用 |
|------|-----|-----|------|
| Array | 迭代、位置读写 | 查找 | 有序列表、同类型数据 |
| Dictionary | key 读写、插入/删除 | 按值查找 | 键值映射、需要快速查找 |
| Object | 属性可靠性、信号 | 属性访问（多源查找） | 需要封装、继承、信号 |

> 来源：[Data Preferences](https://docs.godotengine.org/en/stable/tutorials/best_practices/data_preferences.html)

---

## 三、场景组织原则

> 来源：[Scene Organization](https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html)

### 场景 = 自包含单元

场景应设计为**无依赖**——把所有需要的内容保留在自身内部。需要与外部交互时，通过**依赖注入**实现松耦合：

| 注入方式 | 用途 | 说明 |
|---------|------|------|
| 信号连接 | 响应行为 | 信号名用过去时动词（`entered`、`item_collected`） |
| 调用方法 | 发起行为 | 父节点指定方法名，子节点调用 |
| Callable 属性 | 发起行为 | 比方法更安全，无需所有权 |
| 节点引用 | 数据传递 | 父节点注入引用 |
| NodePath | 路径引用 | 父节点注入路径 |

### 父子关系判定

**核心测试：移除父节点是否合理意味着子节点也应被移除？**

不成立 → 该节点应作为兄弟节点或其他关系存在。

"以关系而非空间位置来思考场景树"——场景树表达的是逻辑关系，不是空间位置。

### 推荐根结构

```
Node "Main" (main.gd)       ← 游戏入口控制器
  ├── Node "World"           ← 游戏世界（关卡切换时替换子节点）
  └── Control "GUI"          ← 主界面（独立于 World，不随关卡切换被删除）
```

### 避免"特殊案例"

如果你需要写文档来解释"为什么这个节点的处理方式和别的不同"，停下来——重新设计结构，消除特殊案例。文档维护实现细节是危险的。

### 场景嵌套 = 聚合（Aggregation）

节点树形成的是聚合关系，而非组合。节点有被移动的灵活性，但最好的设计是让移动成为不需要的默认状态。

---

## 四、逻辑组织原则

> 来源：[Logic Preferences](https://docs.godotengine.org/en/stable/tutorials/best_practices/logic_preferences.html)

### 属性初始化

**在将节点添加到场景树之前修改属性值**——某些属性的 setter 会触发额外更新，在程序化生成等繁重场景中会导致卡顿。

### 资源加载

| 方式 | 时机 | 适用 |
|------|------|------|
| `preload()` | 脚本加载时 | 稳定不变的依赖（常量） |
| `load()` / `@export` | 运行时 | 可变依赖、需要运行时卸载 |

`preload()` 将加载操作前置，避免在性能敏感代码中途加载；`load()` 用于可能变更或被覆盖的依赖。

### 关卡加载策略

- 小型游戏 → 静态加载（一次性加载所有内容）
- 中/大型 → 动态加载（拆分场景，代码管理创建/卸载）
- 有时间和精力 → 封装为可复用的库或插件

---

## 五、领域模式 → Godot 构造映射

以下映射综合了上述全部官方原则。

### 状态机 → enum + match

每个状态的行为在 `match` 分支中处理。状态变化时发信号通知外部。

原则依据：场景自包含 + 单一职责。状态机逻辑封装在拥有它的节点内，外部通过信号感知变化。

### 数据流（实体间通信）→ 信号

信号是 Godot 推荐的解耦方式。在代码中连接（`button.pressed.connect(_on_pressed)`），不在编辑器中连接——保持可追溯性。

原则依据：依赖注入（信号连接是注入方式之一）+ 松耦合。

### 全局服务 → Autoload（谨慎使用）

仅用于宽域 + 自管理的系统。不满足条件时优先用 `class_name` 静态方法。

### 共享配置/数据 → Resource（.tres）

多个实体需要访问同一份数据时，用自定义 Resource。编辑器可配置，运行时单例加载。

### 边界校验 → 状态转换函数中

领域模型中的边界规则（"满弹不换弹"、"换弹中不能射击"）在状态转换的入口校验——不是在 `_input` 中散落校验逻辑，而是在改变状态的函数中集中校验。

原则依据：封装 + 单一职责。校验逻辑和状态管理在一起，不分散在输入处理中。

### 时序控制 → Timer 节点

领域模型中的时间驱动行为（reload 延迟、技能冷却）用 `Timer` 节点表达——不用 `_process` 手动累积 delta。

原则依据：声明式优于命令式。Timer 节点是场景的一部分，在场景树中可见、可调试。

### 可配置参数 → @export

领域模型中可调整的数值（reload_time、magazine_size、move_speed）用 `@export` 暴露给编辑器，不硬编码。

原则依据：数据与逻辑分离 + 编辑器可用性。

### 领域实体 → 场景（Scene）

领域模型中的"玩家"、"敌人"、"武器"等实体，每个做成独立场景。场景内部封装自己的节点树和行为脚本。

原则依据：游戏专属概念 → 场景。场景 = 类，实例 = 对象。

---

## 六、参考页面索引

需要更深入理解某个主题时，访问对应页面：

| 主题 | URL |
|------|-----|
| 总览 | `tutorials/best_practices/index.html` |
| OOP 原则 | `tutorials/best_practices/what_are_godot_classes.html` |
| 场景组织 | `tutorials/best_practices/scene_organization.html` |
| 场景 vs 脚本 | `tutorials/best_practices/scenes_versus_scripts.html` |
| Autoload vs 普通节点 | `tutorials/best_practices/autoloads_versus_regular_nodes.html` |
| 节点替代方案 | `tutorials/best_practices/node_alternatives.html` |
| 数据选型 | `tutorials/best_practices/data_preferences.html` |
| 逻辑组织 | `tutorials/best_practices/logic_preferences.html` |
| Godot 接口 | `tutorials/best_practices/godot_interfaces.html` |
| Godot 通知 | `tutorials/best_practices/godot_notifications.html` |
| 项目组织 | `tutorials/best_practices/project_organization.html` |
| 版本控制 | `tutorials/best_practices/version_control_systems.html` |

基础 URL：`https://docs.godotengine.org/en/stable/`
