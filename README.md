<p align="center">
  <img src="Assets/DomeKeeper-Vita.png" alt="Dome Keeper - PS Vita Port">
</p>

# Dome Keeper - PS Vita Port

Experimental PlayStation Vita port of **Dome Keeper**, adapted from the Godot PC release and tested with the custom **Godot 3.5 RC5 Vita** runtime.

> **Current status:** technical preview under active development. The build boots on PS Vita hardware and reaches the in-game `LevelStage`. The three hard `LevelStage` blockers — a VRAM out-of-memory crash, texture WebP decode crashes, and map shaders exceeding the GPU's texture-unit limit — have now been addressed, and we are verifying that the map renders on hardware. Remaining work is gameplay rendering and performance. This is not a playable release yet.

---

## Release Status

The current Vita build reached these steos on real hardware:

```text
Boot / no C2-12828-1       ████████████████████  done
Title menu + music         ████████████████████  done
Controller input           ████████████████████  done
New Game / Loadout flow     ████████████████████  done
Enter LevelStage / Map      ████████████████████  done
VRAM / OOM crash fixed       ████████████████████  done
Texture decode (stale stex)  ████████████████████  done
Map shaders within limits    ████████████████████  done
Map renders on hardware      ████████████░░░░░░░░  testing
Playable gameplay           ███████░░░░░░░░░░░░░  pending
Performance tuning          ███░░░░░░░░░░░░░░░░░  pending

Overall  ██████████████████░░░░░░░░  ~72%
```

### Project steps
- [x] Game boots without the initial `C2-12828-1` crash.
- [x] Title menu opens and background music plays.
- [x] Controller input works in the title and menu flow.
- [x] `New Game` / loadout flow runs.
- [x] The build reaches the in-game `LevelStage` / map scene.
- [x] **CDRAM / VRAM out-of-memory crash on `LevelStage` fixed** (`ViewportLights` forced to 2D).
- [x] Stage-transition / shockwave GPU freezes fixed.
- [x] **Texture decode crashes fixed** — 136 stale `.stex` (resized PNGs, never re-imported) regenerated.
- [x] **Map shaders brought under the Vita's 8-sampler hardware limit** (`map_main_stones`, `map_background_edges`).
- [ ] Confirm the map renders on hardware (Dome, Keeper, tiles, HUD).
- [ ] Playable gameplay loop.
- [ ] Stable / performant frame rate.

Three separate hard blockers inside `LevelStage` have now been addressed: (1) a VRAM out-of-memory crash from the map's `ViewportLights` allocating a 3D+HDR render target; (2) "Failed decoding WebP" crashes from stale `.stex` files holding old oversized image dimensions that overflowed the Vita's WebP decoder; and (3) the two main map shaders exceeding the PowerVR SGX543's limit of 8 fragment texture units (they used 13 and 14 samplers and could not compile). The next step is confirming the map actually renders on hardware.

---

## Downloads

For now, this repository publishes only the experimental VPK from the [Releases](../../releases) page.

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

The port has gone through several Vita-specific fixes. The most impactful, in order:

- **`.stex` (StreamTexture) WebP format.** The correct layout is `GDST` header followed by `WEBP` then `RIFF` **directly**. A bad bulk "fix" had inserted an extra size field on one texture (`Load.png`), which the Vita GLES2 WebP decoder rejected (`Error unpacking WEBP image`). Reverting it to the standard layout fixed the title screen. The same standard layout works on both PC and the Vita fork.
- **`SCREEN_TEXTURE` + 2D light = GPU freeze.** A `canvas_item` material that samples `SCREEN_TEXTURE` while drawn under a `Light2D` makes Godot compile the heavy LIGHT variant of the canvas shader, which **hangs the PowerVR SGX543 compiler** (hard freeze, not an error). `render_mode unshaded;` does **not** prevent this on the Vita fork. The fix is to remove the screen-texture dependency from non-essential overlays (shockwave distortion, vignette, screen-cover dissolve).
- **Out-of-memory on `LevelStage`.** `Map.gd` sizes several Viewports to the **full map resolution** (`tilemap_size * TILE_SIZE`, ~3768x3768). `ViewportLights` additionally used the Godot defaults (`usage = USAGE_3D`, `hdr = true`), allocating a 16-bit float render target with mipmaps and a depth buffer — over 150 MB on its own. Forcing it to 2D RGBA8 removed the crash (`Cannot allocate mipmaps for 3D post processing effects`).
- **Stage-transition freeze.** The `dissolveTransition` effect made a full-screen `ScreenCover` visible (compiling another lit canvas vertex variant that froze the GPU) and also did an expensive `get_viewport().get_texture().get_data()` framebuffer read-back. Both were disabled; the level now appears directly.
- **Stale `.stex` → WebP decode crash.** Many source PNGs were resized by scripts but never re-imported, so the imported `.stex` files still held the **old oversized dimensions** (e.g. a flag stored at 2560x1536, a sprite sheet at 5175x316). Decoding those huge images overflowed the Vita's WebP decoder (`Failed decoding WebP image` after an out-of-memory). 136 stale textures were regenerated from the current PNGs.
- **Map shaders exceeding the 8-sampler hardware limit.** The PowerVR SGX543 GPU exposes only 8 fragment texture units. `map_main_stones` (13 samplers) and `map_background_edges` (14 samplers) could not compile and hung the GLES2 compiler. Both were reduced to ≤7 samplers by dropping detail maps (damage/cracks, procedural cave noise, small-stone highlights) and reusing the noise map. Core look (tile shape, biome color, lit edges, falloff, gradient) is preserved.
- **On-screen loading diagnostics.** `StageManager` was instrumented to load each scene dependency one at a time and show the current resource, item count, percentage and per-item timing on the Vita screen (and a `user://stage_load_trace.txt` log), which is how the blockers above were pinpointed.
- Project resolution reduced to Vita-friendly dimensions (960x540) to reduce VRAM/CDRAM pressure.
- Export filters updated so required data files (`.yaml`, `.json`, `.txt`, `.csv`) are included in the PCK.
- Safety checks added around data loading to avoid infinite loops when files fail to open on Vita.
- GodotSteam, PlayFab, and other PC-only integrations were removed or bypassed.
- Shader syntax incompatibilities were corrected (PC-style constants such as `0f`, `0.5f`, `1f`; the `SCREEN_UV` / `SCREEN_TEXTURE` double-define workaround).

More detail is available in [DetailsVitaPort.txt](DetailsVitaPort.txt).

---

## Tooling (`scripts/`)

The [`scripts/`](scripts) folder holds the Python utilities written during the port. They operate on the local Vita build folder (absolute paths are embedded in each script — adjust them to your setup). See [`scripts/README.md`](scripts/README.md) for the full layout and safety notes.

| Folder | Purpose | Key scripts |
| :--- | :--- | :--- |
| `stex/` | `.stex` (StreamTexture) WebP format inspection and repair | `revert_all_stex.py` (the official B→A fix), `scan_stex_format.py`, `check_stex.py`, `check_mip.py` |
| `textures/` | Texture / atlas size reduction for the 4096 px and VRAM limits | `scan_textures_vita.py`, `optimize_vita.py`, `resize_stex_v2.py`, `restore_atlas_stex_v2.py` |
| `shaders/` | Applies the `SCREEN_UV` → local-variable (`_suv`) workaround | `fix_shaders_vita.py` |
| `validate/` | Pre-PCK checks of shaders, textures, refs and project settings | `validate_vitabuild.py`, `validate_refs.py` |
| `restore/` | Restore resources from the original/reference PCK | `restore_all_from_original.py`, `restore_all_missing.py` |
| `audio/` | WAV → IMA-ADPCM compression and audio bus patching | `compress_audio.py`, `patch_audio.py` |
| `_history/` | Archived one-off patches and the original combined script blobs (reference only — not meant to be re-run) | — |

> **Warning:** never run a `fix_all_stex`-style script. The harmful logic survives only inside `_history/combined_scripts_fb1d.py`; it re-inserts the broken WebP size prefix. Use `stex/revert_all_stex.py` to repair instead.

---

## Next Steps

- **Confirm the map renders on hardware** now that textures decode and the map shaders fit the sampler limit (Dome, Keeper, tiles, HUD) and the stage is interactive.
- Fix the sprite-sheet atlas alignment: several sheets were resized but their `AtlasTexture` pixel rects were not rescaled, so animations can be misaligned (loads without crashing, but looks wrong).
- Cap the map Viewport render-target sizes (currently full-map resolution) to further reduce CDRAM and shorten the long shader/scene load time.
- Investigate and recompress audio (IMA-ADPCM / 22050 Hz) to cut RAM usage.
- Performance pass once the scene is stable, targeting a playable frame rate.

---

## Known Issues

- Not playable yet — currently verifying that the gameplay scene renders on hardware.
- Stable Vita-compatible `game.pck` is still in development.
- Entering `LevelStage` still has a long load (the map's many custom shaders compile on the Vita's slow GLES2 compiler).
- Resized sprite sheets can be visually misaligned until their atlas rects are rescaled.
- Some visual effects (screen distortion, vignette, dissolve transition, tile damage/crack detail, fine background cave detail) are intentionally simplified or disabled on Vita to fit hardware limits.
- Performance is not yet tuned.

---

## Main Tools Used

### GDRE Tools

Used to inspect and extract Godot PCK data during research.

[https://github.com/GDRETools/gdsdecomp](https://github.com/GDRETools/gdsdecomp)

### Godot PSVita

Custom Godot 3.5 Vita runtime used for hardware testing.

[https://github.com/SonicMastr/godot-vita](https://github.com/SonicMastr/godot-vita)

### PrincessLog / NetLoggingMgr

PS Vita network logging tool used to capture hardware crash logs (the `princesslog-*.log` files that drive most of the debugging above).

### godotpcktool

Used during PCK repacking experiments.

[https://github.com/hhyyrylainen/GodotPckTool](https://github.com/hhyyrylainen/GodotPckTool)

---

## AI Notice

This project used AI-assisted debugging and code review during the porting process. The work included crash-log analysis, Godot scene inspection, script compatibility fixes, and documentation of Vita-specific issues.

---

## Follow My Work

[https://wolffsroom.wordpress.com/](https://wolffsroom.wordpress.com/)
