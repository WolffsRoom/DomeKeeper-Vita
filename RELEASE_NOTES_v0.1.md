# DomeKeeper-Vita v0.1

Initial experimental PS Vita VPK release.

## Current Status

This is **not a playable release yet**.

The VPK can boot on PS Vita hardware, but the stable Vita-compatible `game.pck` is still under development.

## Development Progress

- Fixed the initial `C2-12828-1` crash before the title menu.
- Reached the title menu on real Vita hardware.
- Restored background music on the title flow.
- Confirmed controller input in the title/menu flow.
- Reached the New Game / loadout flow during testing.
- Reached the in-game LevelStage / map scene during fallback testing, but it was not yet functional or performant.

## Known Blocker

The main blocker is `Map.tscn` / `LevelStage` compatibility and performance on Vita hardware.

The original map scene uses multiple viewports, shaders, audio nodes, rock/lights layers, and procedural systems that need further reduction for PS Vita memory and renderer limits.

## Included

- Experimental VPK.
- README with setup/status notes.
- DetailsVitaPort.txt with technical progress notes.

## Not Included

- No commercial game assets.
- No stable `game.pck` yet.

You must own the original game.
