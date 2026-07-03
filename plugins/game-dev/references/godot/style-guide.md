# GDScript Style Guide

> **归档来源**: https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html
> **归档版本**: Godot Engine (stable)
> **状态**: 全量建档，本文件为本地权威参考。不要随意更改。即使原文档有更新，是否采纳也需主动考量，禁止无脑同步。

---

This style guide lists conventions to write elegant GDScript. The goal is to encourage writing clean, readable code and promote consistency across projects, discussions, and tutorials. Hopefully, this will also support the development of auto-formatting tools.

The guide is inspired by Python's PEP 8. It is **not** a hard rulebook — when you cannot apply a guideline, use your best judgment. Keeping code consistent within your project and team is more important than following this guide to the tee.

> **Note:** Godot's built-in script editor applies many of these conventions by default.

---

## Complete Class Example

```gdscript
class_name StateMachine
extends Node
## Hierarchical State machine for the player.
##
## Initializes states and delegates engine callbacks ([method Node._physics_process],
## [method Node._unhandled_input]) to the state.

signal state_changed(previous, new)

@export var initial_state: Node
var is_active = true:
    set = set_is_active

@onready var _state = initial_state:
    set = set_state
@onready var _state_name = _state.name


func _init():
    add_to_group("state_machine")


func _enter_tree():
    print("this happens before the ready method!")


func _ready():
    state_changed.connect(_on_state_changed)
    _state.enter()


func _unhandled_input(event):
    _state.unhandled_input(event)


func _physics_process(delta):
    _state.physics_process(delta)


func transition_to(target_state_path, msg={}):
    if not has_node(target_state_path):
        return

    var target_state = get_node(target_state_path)
    assert(target_state.is_composite == false)

    _state.exit()
    self._state = target_state
    _state.enter(msg)
    Events.player_state_changed.emit(_state.name)


func set_is_active(value):
    is_active = value
    set_physics_process(value)
    set_process_unhandled_input(value)
    set_block_signals(not value)


func set_state(value):
    _state = value
    _state_name = _state.name


func _on_state_changed(previous, new):
    print("state changed")
    state_changed.emit()


class State:
    var foo = 0

    func _init():
        print("Hello!")
```

---

## Formatting

### Encoding and Special Characters

- Use **LF** (line feed) characters for line breaks, not CRLF or CR. (Editor default)
- Use **one** line feed character at the end of each file. (Editor default)
- Use **UTF-8** encoding without a byte order mark. (Editor default)
- Use **Tabs** for indentation, not spaces. (Editor default)

### Indentation

Each indent level should be one greater than the block containing it.

**Good:**
```gdscript
for i in range(10):
    print("hello")
```

**Bad:**
```gdscript
for i in range(10):
  print("hello")

for i in range(10):
        print("hello")
```

Use **2 indent levels** to distinguish continuation lines from regular code blocks.

**Good:**
```gdscript
effect.interpolate_property(sprite, "transform/scale",
        sprite.get_scale(), Vector2(2.0, 2.0), 0.3,
        Tween.TRANS_QUAD, Tween.EASE_OUT)
```

**Bad:**
```gdscript
effect.interpolate_property(sprite, "transform/scale",
    sprite.get_scale(), Vector2(2.0, 2.0), 0.3,
    Tween.TRANS_QUAD, Tween.EASE_OUT)
```

**Exception:** Arrays, dictionaries, and enums use a **single** indentation level for continuation lines:

**Good:**
```gdscript
var party = [
    "Godot",
    "Godette",
    "Steve",
]

var character_dict = {
    "Name": "Bob",
    "Age": 27,
    "Job": "Mechanic",
}

enum Tile {
    BRICK,
    FLOOR,
    SPIKE,
    TELEPORT,
}
```

**Bad:**
```gdscript
var party = [
        "Godot",
        "Godette",
        "Steve",
]

var character_dict = {
        "Name": "Bob",
        "Age": 27,
        "Job": "Mechanic",
}

enum Tile {
        BRICK,
        FLOOR,
        SPIKE,
        TELEPORT,
}
```

### Trailing Comma

Use a trailing comma on the last line in arrays, dictionaries, and enums. This results in easier refactoring and better diffs in version control.

**Good:**
```gdscript
enum Tile {
    BRICK,
    FLOOR,
    SPIKE,
    TELEPORT,
}
```

**Bad:**
```gdscript
enum Tile {
    BRICK,
    FLOOR,
    SPIKE,
    TELEPORT
}
```

Trailing commas are unnecessary in single-line lists:

**Good:**
```gdscript
enum Tile {BRICK, FLOOR, SPIKE, TELEPORT}
```

**Bad:**
```gdscript
enum Tile {BRICK, FLOOR, SPIKE, TELEPORT,}
```

### Blank Lines

Surround functions and class definitions with **two blank lines**:

```gdscript
func heal(amount):
    health += amount
    health = min(health, max_health)
    health_changed.emit(health)


func take_damage(amount, effect=null):
    health -= amount
    health = max(0, health)
    health_changed.emit(health)
```

Use **one** blank line inside functions to separate logical sections.

### Line Length

Keep individual lines of code under **100 characters**. When possible, try to keep lines under **80 characters**. This helps with readability on small displays and with side-by-side code diff views.

### One Statement Per Line

Never combine multiple statements on a single line.

**Good:**
```gdscript
if position.x > width:
    position.x = 0

if flag:
    print("flagged")
```

**Bad:**
```gdscript
if position.x > width: position.x = 0

if flag: print("flagged")
```

**Exception:** The only exception to this rule is the ternary operator:

```gdscript
next_state = "idle" if is_on_floor() else "fall"
```

### Format Multiline Statements for Readability

Wrap long `if` statements or nested ternaries over multiple lines. Use **2 indent levels** for continuation. GDScript allows wrapping statements across multiple lines using parentheses (no backslashes needed). Place the boolean operators (`and`, `or`) at the **beginning** of continuation lines.

**Good:**
```gdscript
var angle_degrees = 135
var quadrant = (
        "northeast" if angle_degrees <= 90
        else "southeast" if angle_degrees <= 180
        else "southwest" if angle_degrees <= 270
        else "northwest"
)

var position = Vector2(250, 350)
if (
        position.x > 200 and position.x < 400
        and position.y > 300 and position.y < 400
):
    pass
```

**Bad:**
```gdscript
var angle_degrees = 135
var quadrant = "northeast" if angle_degrees <= 90 else "southeast" if angle_degrees <= 180 else "southwest" if angle_degrees <= 270 else "northwest"

var position = Vector2(250, 350)
if position.x > 200 and position.x < 400 and position.y > 300 and position.y < 400:
    pass
```

### Avoid Unnecessary Parentheses

Avoid parentheses in expressions and conditional statements. Unless necessary for order of operations or if they're used for line wrapping, they only reduce readability.

**Good:**
```gdscript
if is_colliding():
    queue_free()
```

**Bad:**
```gdscript
if (is_colliding()):
    queue_free()
```

### Boolean Operators

Prefer the plain English versions of boolean operators:
- Use `and` instead of `&&`
- Use `or` instead of `||`
- Use `not` instead of `!`

You may use parentheses around boolean operators to clear any ambiguity. This can make long expressions easier to read.

**Good:**
```gdscript
if (foo and bar) or not baz:
    print("condition is true")
```

**Bad:**
```gdscript
if foo && bar || !baz:
    print("condition is true")
```

### Comment Spacing

Regular comments (`#`) and documentation comments (`##`) should begin with a space to separate them from the comment text. Note that **commented-out code** should **not** have a space after `#`. Code region tags (`#region` / `#endregion`) must follow the exact syntax without a space.

**Good:**
```gdscript
# This is a comment.
#print("This is disabled code")
```

**Bad:**
```gdscript
#This is a comment.
# print("This is disabled code")
```

Prefer writing comments on their own line as opposed to inline comments. Inline comments are allowed only for very short notes.

**Good:**
```gdscript
# This is a long comment that would make the line below too long if written inline.
print("Example") # Short comment.
```

### Whitespace

Always use one space around operators and after commas. No extra spaces in dictionary references / function calls. For single-line dictionary declarations, add a space after `{` and before `}`.

**Good:**
```gdscript
position.x = 5
position.y = target_position.y + 10
dict["key"] = 5
my_array = [4, 5, 6]
my_dictionary = { key = "value" }
print("foo")
```

**Bad:**
```gdscript
position.x=5
position.y = mpos.y+10
dict ["key"] = 5
myarray = [4,5,6]
my_dictionary = {key = "value"}
print ("foo")
```

**Do not** use spaces to vertically align expressions:

```gdscript
# Don't do this:
x        = 100
y        = 100
velocity = 500
```

### Quotes

Use **double quotes** by default. Use single quotes only to avoid the need to escape double quotes within the string.

```gdscript
# Normal string.
print("hello world")

# Use double quotes as usual to avoid escapes.
print("hello 'world'")

# Use single quotes as an exception to the rule to avoid escapes.
print('hello "world"')

# Both quote styles would require 2 escapes; prefer double quotes if it's a tie.
print("'hello' \"world\"")
```

### Numbers

Don't omit the leading or trailing zero in floating-point numbers.

**Good:**
```gdscript
var float_number = 0.234
var other_float_number = 13.0
```

**Bad:**
```gdscript
var float_number = .234
var other_float_number = 13.
```

Use **lowercase** letters in hexadecimal numbers:

**Good:** `var hex_number = 0xfb8c0b`
**Bad:** `var hex_number = 0xFB8C0B`

Use underscores in large numbers to make them more readable:

**Good:**
```gdscript
var large_number = 1_234_567_890
var large_hex_number = 0xffff_f8f8_0000
var large_bin_number = 0b1101_0010_1010
var small_number = 12345
```

**Bad:**
```gdscript
var large_number = 1234567890
var large_hex_number = 0xfffff8f80000
var large_bin_number = 0b110100101010
var small_number = 12_345
```

---

## Naming Conventions

These naming conventions follow the Godot Engine style. Breaking them makes your code clash with the built-in naming conventions, leading to inconsistent code.

| Type | Convention | Example |
|------|-----------|---------|
| File names | snake_case | `yaml_parser.gd` |
| Class names (`class_name`) | PascalCase | `class_name YAMLParser` |
| Node names | PascalCase | `Camera3D`, `Player` |
| Functions | snake_case | `func load_level():` |
| Variables | snake_case | `var particle_effect` |
| Signals | snake_case (past tense) | `signal door_opened` |
| Constants | CONSTANT_CASE | `const MAX_SPEED = 200` |
| Enum names | PascalCase | `enum Element` |
| Enum members | CONSTANT_CASE | `{EARTH, WATER, AIR, FIRE}` |

### File Names

Use **snake_case** for all file names. For named classes, convert the PascalCase class name to snake_case for the filename:

```gdscript
# This file should be saved as `weapon.gd`.
class_name Weapon
extends Node

# This file should be saved as `yaml_parser.gd`.
class_name YAMLParser
extends Object
```

This convention is also applied when a file holds a script without a named class (`class_name`), but the file still represents a discrete functionality.

### Classes and Nodes

Use **PascalCase** for class and node names:

```gdscript
extends CharacterBody3D
```

Also use PascalCase when loading a class into a constant or variable:

```gdscript
const Weapon = preload("res://weapon.gd")
```

### Functions and Variables

Use **snake_case** for both functions and variables:

```gdscript
var particle_effect
func load_level():
```

Prepend a single underscore (`_`) to virtual methods (functions the user must override), private functions, and private variables:

```gdscript
var _counter = 0
func _recalculate_path():
```

### Signals

Use **snake_case** in the past tense to name signals:

```gdscript
signal door_opened
signal score_changed
```

### Constants and Enums

Constants use **CONSTANT_CASE**: all capital letters with an underscore (`_`) to separate words:

```gdscript
const MAX_SPEED = 200
```

**Enum names** use **PascalCase**, while their members use **CONSTANT_CASE** (since they are constant values). Use the singular form for enum names as they represent a type.

**Good:**
```gdscript
enum Element {
    EARTH,
    WATER,
    AIR,
    FIRE,
}
```

**Bad:**
```gdscript
enum Element { EARTH, WATER, AIR, FIRE }
```

Writing each enum member on its own line allows you to add documentation comments above each element. It also makes for cleaner diffs in version control when elements are added or removed.

---

## Code Order

This is the recommended order for the content of a GDScript file, from top to bottom:

```
01. @tool, @icon, @static_unload
02. class_name
03. extends
04. ## doc comment

05. signals
06. enums
07. constants
08. static variables
09. @export variables
10. remaining regular variables
11. @onready variables

12. _static_init()
13. remaining static methods
14. overridden built-in virtual methods:
    1. _init()
    2. _enter_tree()
    3. _ready()
    4. _process()
    5. _physics_process()
    6. remaining virtual methods
15. overridden custom methods
16. remaining methods
17. inner classes
```

Within methods and variables, place **public** before **private**.

**Four rules of thumb:**

1. Properties and signals come first, followed by methods.
2. Public comes before private.
3. Virtual callbacks come before the class's interface.
4. The construction and initialization functions of objects (`_init` and `_ready`) should come before functions that modify the object at runtime.

### Class Declaration

If the code is meant to run in the editor, place the `@tool` annotation on the first line of the script. Place `@icon` on the next line (if needed). Then `class_name` (with `@abstract` before it if the class is abstract). Then `extends`. Follow with the **documentation comment** (docstring).

```gdscript
@tool
@icon("res://path/to/optional/icon.svg")
class_name MyNode
extends Node
## A brief description of the class's role and functionality.
##
## The description of the script, what it can do,
## and any further detail.
```

For **inner classes**, you can use a more concise single-line declaration:

```gdscript
## A brief description of the class's role and functionality.
##
## The description of the script, what it can do,
## and any further detail.
@abstract class MyNode extends Node:
    pass
```

### Signals and Properties

Declare signals first, followed by enums and constants. Then exported variables, public and private member variables, and `@onready` variables, in that order.

```gdscript
signal player_spawned(position)

enum Job {
    KNIGHT,
    WIZARD,
    ROGUE,
    HEALER,
    SHAMAN,
}

const MAX_LIVES = 3

@export var job: Job = Job.KNIGHT
@export var max_health = 50
@export var attack = 5

var health = max_health:
    set(new_health):
        health = new_health

var _speed = 300.0

@onready var sword = get_node("Sword")
@onready var gun = get_node("Gun")
```

### Member Variables

Don't declare member variables if they are only used locally in a method — declare them as the method's local variables instead.

### Local Variables

Declare local variables as close as possible to their first use. This makes it easier to follow the code without having to scroll too much to find where a variable was declared.

### Methods and Static Functions

After the class's properties come the methods. Start with the `_init()` callback method, then the `_ready()` callback, then pick up with the remaining built-in virtual callbacks: `_unhandled_input()`, `_physics_process()`, etc. After that, include the rest of the class's interface, presenting public methods before private methods.

```gdscript
func _init():
    add_to_group("state_machine")


func _ready():
    state_changed.connect(_on_state_changed)
    _state.enter()


func _unhandled_input(event):
    _state.unhandled_input(event)


func transition_to(target_state_path, msg={}):
    if not has_node(target_state_path):
        return

    var target_state = get_node(target_state_path)
    assert(target_state.is_composite == false)

    _state.exit()
    self._state = target_state
    _state.enter(msg)
    Events.player_state_changed.emit(_state.name)


func _on_state_changed(previous, new):
    print("state changed")
    state_changed.emit()
```

---

## Static Typing

Since Godot 3.1, GDScript supports optional static typing.

### Declared Types

Use `<variable>: <type>` to declare the type of a variable:

```gdscript
var health: int = 0
```

Use `-> <type>` to declare the return type of a function:

```gdscript
func heal(amount: int) -> void:
```

### Inferred Types

Use the `:=` assignment operator to let Godot infer the type. Prefer `:=` when the type is written on the same line as the assignment. Write the type explicitly when it would be ambiguous otherwise.

**Good:**
```gdscript
var health: int = 0                # The type is written on the same line
var direction := Vector3(1, 2, 3)  # The type is clear from the right-hand side
```

**Bad:**
```gdscript
var health := 0                    # Type ambiguous — is it int or float?
var direction: Vector3 = Vector3(1, 2, 3)  # Verbose — type can be inferred
var value := complex_function()    # Type unclear — what does the function return?
```

For methods like `get_node()` that can't infer a specific type, you **must** set the type explicitly:

**Good:**
```gdscript
@onready var health_bar: ProgressBar = get_node("UI/LifeBar")
```

**Bad:**
```gdscript
@onready var health_bar := get_node("UI/LifeBar")
```

Alternatively, you can use `as` to cast the return type:

```gdscript
@onready var health_bar := get_node("UI/LifeBar") as ProgressBar
```

> This option is considered more type-safe than type hints, but also less null-safe as it silently casts the variable to `null` in case of a type mismatch at runtime, without an error or warning.
