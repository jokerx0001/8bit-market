# Visual Spec 输出 Schema

art-spec-builder 的输出必须严格遵循此 YAML 结构。

```yaml
usage:
type:
aspect_ratio:
target_platform:

subject:
subject_focus:
pose:
expression:

environment:
environment_detail:
time_of_day:
weather:

composition:
shot_type:
camera_angle:
lens:

depth:
foreground:
midground:
background:

lighting:
lighting_style:
rim_light:              # none / subtle / strong
volumetric_effects:     # none / light fog / god rays / dust particles / atmospheric haze

materials:
surface_details:
texture_quality:

color_palette:
primary_colors:
contrast_level:         # low / medium / high
saturation:             # desaturated / natural / vibrant

mood:
energy_level:           # calm / moderate / intense

style:
style_family:
rendering_style:
art_direction:

detail_level:           # minimal / moderate / high / ultra
quality_level:          # standard / high / production

visual_priority:        # 最想让观众看到的第一眼内容
negative_space:         # minimal / moderate / generous
readability_priority:   # low / medium / high

generation_bias:        # controlled
model_behavior_control: # stable
consistency_priority:   # high

negative_prompt:
```
