# Project Organization

> **归档来源**: https://docs.godotengine.org/en/stable/tutorials/best_practices/project_organization.html
> **归档版本**: Godot Engine (stable)
> **状态**: 全量建档，本文件为本地权威参考。不要随意更改。即使原文档有更新，是否采纳也需主动考量，禁止无脑同步。

---

## Introduction

Since Godot has no restrictions on project structure or filesystem usage, organizing files when learning the engine can seem challenging. This tutorial suggests a workflow which should be a good starting point. It also covers how to integrate version control with the engine.

## Organization Principles

Godot is scene-based in nature, and uses the filesystem as-is, without metadata or an asset database. Compared to other engines, many resources are contained within the scene itself, so the amount of files on the filesystem is considerably smaller.

The core recommendation is: **group assets as closely as possible to the scenes that use them.** As a project grows, keeping assets close to their scenes becomes increasingly important for maintainability.

### Example Directory Layout

```
/project.godot
/docs/.gdignore
/docs/learning.html
/models/town/house/house.dae
/models/town/house/window.png
/models/town/house/door.png
/characters/player/cubio.dae
/characters/player/cubio.png
/characters/enemies/goblin/goblin.dae
/characters/enemies/goblin/goblin.png
/characters/npcs/suzanne/suzanne.dae
/characters/npcs/suzanne/suzanne.png
/levels/riverdale/riverdale.scn
```

In this pattern, basic assets (sprites, 3D meshes, materials, audio, etc.) live in their own folders, while built levels (scenes) are separate.

### Key Principles

1. **Group assets close to scenes that use them.** Co-location improves maintainability as the project grows.
2. **Let the filesystem do the organizing.** Godot doesn't impose an asset database — the folder structure IS the organization.
3. **Scenes contain many of their own resources.** Compared to other engines, fewer loose files exist on disk because resources are embedded in scenes.

---

## Style Guide

For consistency across projects, follow these file naming and organization conventions:

| Item | Convention | Rationale |
|------|-----------|-----------|
| Folder and file names | **snake_case** | Avoids case-sensitivity issues after Windows export. **Exception:** C# scripts use PascalCase to match class name conventions. |
| Node names | **PascalCase** | Matches built-in node naming in the engine. |
| Third-party resources | Top-level `addons/` folder | Makes it easy to identify which files are external. **Exception:** third-party assets for a specific character may belong alongside that character's scenes and scripts. |

---

## Import Process

Since Godot 3.0, assets are now transparently imported from within the project folder. The old approach of external asset management caused organizational friction, so the engine now handles everything inside the project directory.

### Ignoring Specific Folders

To prevent Godot from importing files in a particular folder, create an empty file named **`.gdignore`** inside that folder (the leading dot is mandatory).

- On Windows, name it `.gdignore.` — the trailing dot is removed automatically when the name is confirmed.
- Alternatively, from a command prompt: `type nul > .gdignore`

**Effects of `.gdignore`:**
- Resources inside the folder become inaccessible to `load()` and `preload()`.
- The folder is hidden from the FileSystem dock, reducing visual clutter.
- Can speed up the initial project importing.

> **Important:** The `.gdignore` file's contents are ignored — the file must be **empty**. It does **not** support pattern matching like `.gitignore` does.

---

## Case Sensitivity

Case sensitivity differs across platforms:
- **Windows and recent macOS:** case-insensitive filesystems by default (can be configured).
- **Linux distributions:** case-sensitive filesystem by default.

**The risk:** Godot's PCK virtual filesystem is case-sensitive. A project that works during development can break after export if filenames differ only by case.

**Recommended approach:** Stick to **`snake_case`** naming for all files in the project (and lowercase characters in general). The lone exception is when language-specific style guides (e.g., C#) dictate otherwise, but consistency remains the top priority.

### Windows 10 Case-Sensitivity (Optional)

To further prevent case-related mistakes, you can make a project folder case-sensitive after enabling the Windows Subsystem for Linux feature.

**Enable case-sensitivity:**
```
fsutil file setcasesensitiveinfo <path to project folder> enable
```

**Disable case-sensitivity:**
```
fsutil file setcasesensitiveinfo <path to project folder> disable
```

**If WSL is not yet enabled** (run PowerShell as Administrator, then reboot):
```
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
```

---

## Summary

1. **Keep scenes and their assets close together** — co-location improves maintainability as the project grows.
2. **Use snake_case for files and folders**, and PascalCase for node names.
3. **Third-party code goes in `/addons/`** — unless it's tightly coupled to a specific character or scene.
4. **Use `.gdignore`** to exclude folders from import and hide them from the FileSystem dock.
5. **Treat case sensitivity seriously** — what works on your dev machine may break on another platform after export.
6. **Import happens inside the project folder** (post-3.0), so keep everything in-tree and avoid external asset databases.
