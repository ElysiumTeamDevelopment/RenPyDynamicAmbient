# Dynamic Ambient System for Ren'Py

**English** | [Русский](assets/README_ru.md)

A flexible dynamic ambient audio management system for Ren'Py 8.4+ that allows playing multiple audio tracks simultaneously with configurable randomness, volume, smooth transitions, and complex audio scene arrangements.

**Version:** 2.0.0  
**CDS Version:** Ren'Py 8.5.0+  
**License:** MIT

## Key Features

- **YAML Configuration** — No Python code needed, just clean YAML files
- **Arrangements** — Define audio scenes as presets with layers
- **CDS Commands** — Native Ren'Py statements: `ambient play`, `ambient layer`, `ambient stop`
- **Mandatory tracks** — Play continuously from startup
- **Random tracks** — Play with configurable probability via wave system
- **Smooth transitions** — All volume changes occur smoothly
- **Layers** — Dynamic track groups (weather, tension, time-of-day)
- **Strict isolation** — Tracks not in current arrangement automatically stop
- **Random containers** — Multiple files per track for variety
- **Auto-transitions** — Arrangements can auto-switch (intro → loop)
- **Debug UI** — Real-time monitoring overlay

## Quick Start

### 1. Install PyYAML

```bash
pip install pyyaml -t game/python-packages
```

### 2. Copy Files

Copy to your `game/` folder:
- `dynamic_ambient.rpy` (required)
- `audio_assets.yaml` (required)
- `arrangements.yaml` (required)
- `ambient_auto_start.rpy` (optional — main menu auto-start)
- `ambient_integration.rpy` (optional — settings UI)
- `libs/rpda/02-rpda-cds.rpy` (optional — CDS commands)

### 3. Configure Tracks

```yaml
# audio_assets.yaml
tracks:
  forest_base:
    file: "audio/forest.ogg"
    type: "mandatory"
    volume: 0.6

  birds:
    file: "audio/birds.ogg"
    type: "random"
    volume: 0.5
    chance: 0.4
    interval: [30, 90]
```

### 4. Create Arrangements

```yaml
# arrangements.yaml
arrangements:
  forest_day:
    tracks:
      forest_base: { volume: 0.6 }
      birds: { volume: 0.5 }
    layers:
      rain:
        rain_sound: { volume: 0.7 }
```

### 5. Use in Script

```renpy
label forest_scene:
    ambient play "forest_day"
    "You enter the forest..."
    
    ambient layer "rain" on fade 3.0
    "It starts to rain."
```

## CDS Commands (Ren'Py 8.5.0+)

```renpy
ambient play "arrangement_name"       # Play arrangement
ambient play "name" fade 3.0          # Play with custom fade
ambient stop                          # Stop system
ambient layer "rain" on               # Enable layer
ambient layer "rain" off fade 2.0     # Disable layer with fade
ambient volume 0.5                    # Set volume
ambient pause                         # Pause playback
ambient resume                        # Resume playback
ambient schedule "name" in 30.0       # Schedule transition
ambient debug ui                      # Toggle debug overlay
```

## Python API

```renpy
$ ambient.play_arrangement("forest_day")
$ ambient.play_arrangement("forest_day", fade_time=3.0)
$ ambient.set_layer("rain", True, fade_time=2.0)
$ ambient.set_base_volume(0.5)
$ ambient.stop_ambient()
$ ambient.pause_ambient()
$ ambient.resume_ambient()
```

## Demo Project

A complete demo project is included in `example/RPDA_Demo_Project/`. See the [Demo Project Guide](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Demo-Project) for setup instructions.

## Documentation

Full documentation available on the **[Wiki](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki)**:

- [Installation](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Installation)
- [Quick Start](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Quick-Start)
- [Track Types](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Track-Types)
- [Arrangements](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Arrangements)
- [Layers](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Layers)
- [CDS Reference](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/CDS-Reference)
- [Python API](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Python-API)
- [Configuration Reference](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Configuration-Reference)

## Requirements

- **Ren'Py:** 8.4+ (core system)
- **Ren'Py:** 8.5.0+ (for CDS commands)
- **PyYAML:** Required for YAML parsing

## File Structure

```
game/
├── dynamic_ambient.rpy       # Core system
├── ambient_auto_start.rpy    # Auto-start (optional)
├── ambient_integration.rpy   # Settings UI (optional)
├── audio_assets.yaml         # Track configuration
├── arrangements.yaml         # Arrangement configuration
└── libs/rpda/
    └── 02-rpda-cds.rpy       # CDS commands (optional)
```

## Changelog v2.0.0

- **YAML Configuration** — Replaced Python config with `audio_assets.yaml` and `arrangements.yaml`
- **CDS Commands** — Added `ambient` statements for script control
- **Arrangement System** — Audio scenes with layers and auto-transitions
- **Strict Isolation** — Tracks not in arrangement automatically stop
- **Random Containers** — Multiple files per track ID
- **Automatic Initialization** — No manual setup calls needed
- **Debug UI** — Enhanced debugging with `ambient debug ui`

## License

MIT License — Free to use and modify in any project.

## Links

- [GitHub Repository](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient)
- [Wiki Documentation](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki)
- [Issues](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/issues)
