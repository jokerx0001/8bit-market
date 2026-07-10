# 3D Construction Reference

coding agent 在没有 GLB 文件时，用 Godot 内置能力构建 3D 场景的方法参考。

---

## Common Node Compositions

**3D Physics Object:**
```gdscript
var body := RigidBody3D.new()
var collision := CollisionShape3D.new()
var mesh := MeshInstance3D.new()
var shape := BoxShape3D.new()
shape.size = Vector3(1, 1, 1)
collision.shape = shape
body.add_child(collision)
body.add_child(mesh)
```

**Camera Rig:**
```gdscript
var pivot := Node3D.new()
var camera := Camera3D.new()
camera.position.z = 5
pivot.add_child(camera)
```

---

## Asset Loading (GLB)

```gdscript
# MUST type as PackedScene, use = (not :=) for instantiate()
var model_scene: PackedScene = load("res://assets/glb/car.glb")
var model = model_scene.instantiate()
model.name = "CarModel"

# Measure for scaling — find MeshInstance3D (GLB structure varies, may be nested)
var mesh_inst: MeshInstance3D = find_mesh_instance(model)
var aabb: AABB = mesh_inst.get_aabb() if mesh_inst else AABB(Vector3.ZERO, Vector3.ONE)

# Scale to target size (e.g., car should be ~2 units long)
var target_length := 2.0
var scale_factor: float = target_length / aabb.size.x
model.scale = Vector3.ONE * scale_factor
model.position.y = -aabb.position.y * scale_factor  # Fix vertical alignment

parent_node.add_child(model)

func find_mesh_instance(node: Node) -> MeshInstance3D:
    if node is MeshInstance3D:
        return node
    for child in node.get_children():
        var found = find_mesh_instance(child)  # Recursive — use = not :=
        if found:
            return found
    return null
```

**GLB orientation:** Imported models often face the wrong axis. After instantiating, check the AABB: the longest dimension tells you which local axis the model faces. If a car's AABB is longest on Z but your game expects forward=negative Z, no rotation needed; if longest on X, rotate 90°. For animals/characters, the forward-facing axis must align with the direction of movement — an animal moving sideways is a clear bug. Verify this in screenshots.

**Collision shapes for 3D models:** Always use simple primitives (BoxShape3D, SphereShape3D, CapsuleShape3D). Never use `create_convex_shape()` or `create_trimesh_shape()` on imported GLB meshes — causes <1 FPS on high-poly models (100k+ triangles).
```gdscript
var box := BoxShape3D.new()
box.size = aabb.size * model.scale
collision_shape.shape = box
```

**Textures (PNG):**
```gdscript
var mat := StandardMaterial3D.new()
mat.albedo_texture = load("res://assets/img/grass.png")
mesh_instance.set_surface_override_material(0, mat)
```

**Texture UV tiling:** For large surfaces, scale UVs to avoid stretched textures:
```gdscript
mat.uv1_scale = Vector3(10, 10, 1)  # Tile every 2m on a 20m floor
```

---

## CSG for Rapid Prototyping

CSG nodes generate collision automatically — no separate CollisionShape needed:

```gdscript
var floor := CSGBox3D.new()
floor.size = Vector3(20, 0.5, 20)
floor.use_collision = true
floor.material = ground_mat
root.add_child(floor)

# Subtraction (carve holes): child CSG on parent CSG
var hole := CSGCylinder3D.new()
hole.operation = CSGShape3D.OPERATION_SUBTRACTION
hole.radius = 1.0
hole.height = 1.0
floor.add_child(hole)
```

---

## Noise/Procedural Textures

```gdscript
var noise := FastNoiseLite.new()
noise.noise_type = FastNoiseLite.TYPE_CELLULAR
noise.frequency = 0.02
noise.fractal_type = FastNoiseLite.FRACTAL_FBM
noise.fractal_octaves = 5

var tex := NoiseTexture2D.new()
tex.noise = noise
tex.width = 1024
tex.height = 1024
tex.seamless = true       # tileable
tex.as_normal_map = true  # for normal maps
tex.bump_strength = 2.0
```

---

## StandardMaterial3D Extended Properties

Beyond basic albedo, useful properties for richer materials:
- `normal_enabled = true` + `normal_texture` + `normal_scale = 2.0`
- `rim_enabled = true` + `rim_tint = 1.0` — silhouette glow
- `emission_enabled = true` + `emission_texture` — self-illumination
- `texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC`

---

## Visual Effects (Flash, Burst, Trail)

Prefer Tween + simple nodes over particle systems. Particle nodes (CPUParticles2D, GPUParticles2D) do NOT render in `--headless` or `--write-movie` capture modes, making them invisible in automated screenshots. Use Tween-animated ColorRect/Sprite2D nodes instead — they render reliably everywhere and give full control.

### Jump/impact flash (runtime GDScript)

```gdscript
func _emit_jump_fx() -> void:
    var colors := [
        Color(1.0, 0.95, 0.4, 1.0),   # bright yellow
        Color(1.0, 0.7, 0.1, 0.9),    # orange-yellow
        Color(1.0, 0.4, 0.0, 0.8),    # orange
    ]
    for i in range(8):
        var dot := ColorRect.new()
        var size := randf_range(4.0, 12.0)
        dot.size = Vector2(size, size)
        dot.position = Vector2(
            global_position.x + randf_range(-15, 15),
            global_position.y + randf_range(20, 40)
        )
        dot.color = colors[i % colors.size()]
        dot.z_index = 5
        get_tree().current_scene.add_child(dot)
        var dur := randf_range(0.2, 0.5)
        var tw_move := create_tween()
        tw_move.tween_property(dot, "position:y", dot.position.y + randf_range(20, 50), dur)
        var tw_fx := create_tween()
        tw_fx.set_parallel(true)
        tw_fx.tween_property(dot, "modulate:a", 0.0, dur)
        tw_fx.tween_property(dot, "scale", Vector2(2.0, 2.0), dur)
        tw_fx.tween_callback(dot.queue_free)
```

### When to use particle systems vs Tween nodes

| Effect type | Recommended approach | Why |
|-------------|---------------------|-----|
| Jump/land flash | Tween + ColorRect | Simple, testable |
| Collect item sparkle | Tween + Sprite2D | Need custom shapes |
| Trail behind character | GPUParticles2D | Continuous emission, performance-critical |
| Explosion/impact burst | Tween + Sprite2D | Testable, controllable |
| Ambient particles (dust, rain) | CPUParticles2D | Continuous, not screenshot-critical |

Rule of thumb: If the effect needs to be visible in automated screenshots (QA, capture), use Tween nodes. If it's ambient/continuous and only seen by human players, particle systems are fine.

### Particle system reference (if needed)

**GPUParticles2D** — GPU-driven, all physics on `ParticleProcessMaterial`:
```gdscript
var pmat := ParticleProcessMaterial.new()
pmat.direction = Vector3(0, 1, 0)
pmat.spread = 45.0
pmat.gravity = Vector3(0, 400, 0)
pmat.initial_velocity_min = 80.0
pmat.initial_velocity_max = 160.0
pmat.scale_min = 0.5
pmat.scale_max = 1.5
particles.process_material = pmat
```

**CPUParticles2D** — CPU-driven, all properties on the node:
```gdscript
particles.direction = Vector2(0, 1)
particles.spread = 45.0
particles.gravity = Vector2(0, 400)
particles.scale_amount_min = 0.5
particles.scale_amount_max = 1.5
particles.color_ramp = Gradient.new()  # NOT GradientTexture1D
```

See `quirks.md` for the full list of particle system gotchas.

---

## Environment & Lighting (3D Scenes)

When building 3D scenes, set up environment and lighting programmatically:

```gdscript
# WorldEnvironment
var world_env := WorldEnvironment.new()
var env := Environment.new()
env.background_mode = Environment.BG_SKY
env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
env.ambient_light_color = Color.WHITE
env.ambient_light_sky_contribution = 0.5
var sky := Sky.new()
sky.sky_material = ProceduralSkyMaterial.new()
env.sky = sky
world_env.environment = env
root.add_child(world_env)

# Sun (DirectionalLight3D)
var sun := DirectionalLight3D.new()
sun.shadow_enabled = true
sun.shadow_bias = 0.05
sun.shadow_blur = 2.0
sun.directional_shadow_max_distance = 30.0
sun.sky_mode = DirectionalLight3D.SKY_MODE_LIGHT_AND_SKY
sun.rotation_degrees = Vector3(-45, -30, 0)
root.add_child(sun)
```

---

## Animated Sprites Runtime Loading

Sprite sheets generated at runtime have no `.import` files. Godot's `load()` returns null without `.import` files. Use `Image.load_from_file()` instead:

```gdscript
func _load_image(path: String) -> ImageTexture:
    var image := Image.load_from_file(path)
    if not image:
        push_warning("Failed to load: " + path)
        return null
    return ImageTexture.create_from_image(image)
```

Always use `float()` casts for region calculations — integer division truncates in GDScript, causing wrong frame crops.
