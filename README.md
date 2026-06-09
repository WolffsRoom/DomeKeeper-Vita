<p align="center">
  <img src="Assets/DomeKeeper-Vita.png" alt="Dome Keeper - PS Vita Port">
</p>

# Dome Keeper - PS Vita Port

Experimental PlayStation Vita port of **Dome Keeper**, adapted from the Godot PC release and tested with the custom **Godot 3.5 RC5 Vita** runtime.

> **Current status:** early technical preview. The included VPK can boot on PS Vita hardware, but the stable Vita-compatible `game.pck` is still being developed. This is not a playable release yet.

---

## Release Status

The current Vita build reached these milestones on real hardware:

- The game boots without the initial `C2-12828-1` crash.
- The title menu opens and background music plays.
- Controller input works in the title flow.
- `New Game` / loadout flow was reached during development.
- The project reached the in-game `LevelStage` / map scene during testing, but the gameplay scene is still unstable, visually broken in some attempts, and not yet playable.

The current blocker is producing a stable and performant `game.pck` for the Vita. The original `Map.tscn` is heavy and uses several Godot viewport/shader/audio systems that need careful reduction for PS Vita memory and renderer limits.

---

## Downloads

For now, this repository publishes only the experimental VPK from the `Release` folder.

The final `game.pck` is **not included** and is still under development.

You must own the original game. No commercial game assets are provided here.

---

## Installation

1. Download the latest VPK from the [Releases](../../releases) page.
2. Install the VPK on your PS Vita using VitaShell or [FMVita](https://github.com/WolffsRoom/FMVita).
3. A compatible `game.pck` will be required at the app folder once the data package is stable.

Expected target path:

```text
ux0:app/DOMEKEE01/game.pck
```

At this stage, the stable `game.pck` package is still being worked on.

---

## Controls

| Button | Action |
| :--- | :--- |
| Left Stick / D-Pad | Move / Navigate |
| Cross | Confirm / Interact |
| Circle | Cancel / Back |
| Triangle | Gadget / Context action |
| Square | Secondary action |
| L / R | Game actions, depending on state |
| Start | Pause |

Controls are still subject to change while the gameplay scene is being stabilized.

---

## Technical Progress

The port has gone through several Vita-specific fixes:

- Project resolution reduced to Vita-friendly dimensions to avoid excessive VRAM/CDRAM pressure.
- Export filters updated so required data files such as `.yaml`, `.json`, `.txt`, and `.csv` are included in the PCK.
- Safety checks added around data loading to avoid infinite loops when files fail to open on Vita.
- GodotSteam, PlayFab, and other PC-only integrations were removed or bypassed.
- Audio memory usage was investigated; uncompressed WAV imports are a major RAM risk on Vita.
- Shader syntax incompatibilities were identified, especially PC-style constants such as `0f`, `0.5f`, and `1f`.
- The title/menu boot crash was fixed during development.
- The loadout/new-game flow was simplified enough to run during testing.
- Several lightweight fallback experiments were made for `Dome`, `Relichunt`, and `Map` to isolate the crash path.

More detail is available in [DetailsVitaPort.txt](DetailsVitaPort.txt).

---

## Known Issues

- Not playable yet.
- Stable Vita-compatible `game.pck` is still in development.
- `Map.tscn` / `LevelStage` still need major optimization and compatibility work.
- Some map shaders, viewport textures, rocks, lights, and audio nodes can fail or render incorrectly on Vita.
- Performance reached about 7 FPS in one fallback test that got into the gameplay scene, so the real map pipeline still needs substantial work.

---

## Main Tools Used

### GDRE Tools

Used to inspect and extract Godot PCK data during research.

[https://github.com/GDRETools/gdsdecomp](https://github.com/GDRETools/gdsdecomp)

### Godot PSVita

Custom Godot 3.5 Vita runtime used for hardware testing.

[https://github.com/SonicMastr/godot-vita](https://github.com/SonicMastr/godot-vita)

### PrincessLog / NetLoggingMgr

PS Vita network logging tool being evaluated to capture better hardware logs for errors such as `ERR 16` during scene loading.

### godotpcktool

Used during PCK repacking experiments.

[https://github.com/hhyyrylainen/GodotPckTool](https://github.com/hhyyrylainen/GodotPckTool)

---

## AI Notice

This project used AI-assisted debugging and code review during the porting process. The work included crash-log analysis, Godot scene inspection, script compatibility fixes, and documentation of Vita-specific issues.

---

## Follow My Work

[https://wolffsroom.wordpress.com/](https://wolffsroom.wordpress.com/)
