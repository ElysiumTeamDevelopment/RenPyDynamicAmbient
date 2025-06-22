# Dynamic Ambient System for RenPy

**English** | [Русский](assets/README_ru.md)

## Description

A flexible dynamic ambient management system that allows playing multiple audio tracks simultaneously with customizable randomness, volume, and smooth transition parameters.

## Key Features

- **Mandatory tracks**: Play continuously from the moment of startup
- **Random tracks**: Play with customizable probability and duration
- **Smooth transitions**: All volume changes occur smoothly
- **Volume control**: Individual volume settings for each track
- **Main menu theme**: Plays before the ambient without sound overlay
- **Automatic sequence**: Theme smoothly transitions into ambient

## System Files

### Required Files
1. **dynamic_ambient.rpy** - Main system class
2. **ambient_config.rpy** - Track configuration
3. **ambient_auto_start.rpy** - Automatic start in main menu

### Optional Files
4. **ambient_integration.rpy** - Settings interface and debug tools (can be excluded if you don't need UI controls)

### Universal Usage
The system can be used anywhere in the game, not just in the main menu:
- In any scenes and dialogues
- In mini-games and custom screens
- Can work parallel with game music
- Different ambient configs for different locations

## Setup and Usage

### 1. Setting up the main menu theme

Set the main theme that will play before the ambient:

```renpy
$ ambient.set_main_theme(
    filename="audio/main_theme.mp3",
    duration=60,         # duration in seconds
    volume=0.8,          # volume (0.0-1.0)
    fade_in_time=2.0,    # fade-in time
    fade_out_time=4.0    # fade-out time
)
```

### 2. Setting up ambient tracks

In the `ambient_config.rpy` file, there is a `setup_ambient` label where all tracks are configured:

```renpy
$ ambient.add_track(
    track_id="unique_id",
    filename="path/to/file.ogg",
    track_type="mandatory",  # or "random"
    volume=0.7,              # volume (0.0-1.0)
    play_chance=0.3,         # play probability (for random only)
    min_duration=30,         # minimum duration (seconds)
    max_duration=120,        # maximum duration (seconds)
    fade_in_time=3.0,        # fade-in time
    fade_out_time=3.0        # fade-out time
)
```

### 2. Track Types

#### Mandatory tracks
- Start immediately when the system starts
- Play continuously until the system stops
- Suitable for basic background

#### Random tracks
- Play with a certain probability
- Have limited duration
- Add dynamics and variety

### 3. Starting the System

#### Automatic start in the main menu
The system automatically starts in the main menu through the `start_main_menu_ambient` label.
First the main theme plays, then smoothly transitions to ambient.

#### Manual start

**Start with main theme:**
```renpy
# Sequential: main theme → ambient
$ ambient.start_with_main_theme()
```

**Start ambient only:**
```renpy
# Immediate ambient start
$ ambient.start_ambient()

# Start with delay
$ ambient.start_ambient(delay_after_main_theme=5)
```

### 4. System Control

#### Stopping
```renpy
# Smooth stop
$ ambient.stop_ambient()

# Instant stop
$ ambient.stop_ambient(fade_out=False)
```

#### Pause and resume
```renpy
$ ambient.pause_ambient()
$ ambient.resume_ambient()
```

#### Volume change
```renpy
$ ambient.set_base_volume(0.5)  # 50% of base volume
```

### 5. Game Integration

#### Starting in specific locations
```renpy
label forest_location:
    scene bg forest
    
    # Stop current ambient
    $ ambient.stop_ambient()
    
    # Configure new ambient for forest
    $ ambient.add_track("forest_base", "audio/forest_base.ogg", "mandatory", 0.6)
    $ ambient.add_track("birds", "audio/birds.ogg", "random", 0.4, 0.3, 20, 80)
    
    # Start
    $ ambient.start_ambient()
    
    "You enter the forest..."
    
    return
```

#### Stopping when transitioning to game
```renpy
label start:
    # Stop main menu ambient
    call stop_main_menu_ambient
    
    # Start game
    scene bg room
    "The game has started..."
    
    return
```

## Parameter Configuration

### Track Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| track_id | string | Unique track identifier |
| filename | string | Audio file path |
| track_type | string | "mandatory" or "random" |
| volume | float | Track volume (0.0-1.0) |
| play_chance | float | Play probability (0.0-1.0) |
| min_duration | int | Minimum duration (seconds) |
| max_duration | int | Maximum duration (seconds) |
| fade_in_time | float | Fade-in time |
| fade_out_time | float | Fade-out time |

### Recommended Settings

#### For basic background
```renpy
track_type="mandatory"
volume=0.4-0.7
fade_in_time=4.0-8.0
fade_out_time=3.0-6.0
```

#### For atmospheric effects
```renpy
track_type="random"
volume=0.3-0.8
play_chance=0.2-0.5
min_duration=30-60
max_duration=120-300
fade_in_time=2.0-6.0
fade_out_time=2.0-4.0
```

## Interface Control

### Ambient settings screen
Available through "Settings" → "Ambient Settings":

- **Volume slider**: Adjusts overall system volume
- **System status**: Shows whether the system is active
- **Control buttons**: Start, stop, pause, resume
- **Track information**: Current state of each track

### Game settings integration
The "Ambient Settings" button is added to the standard RenPy settings screen.

## Technical Features

### Audio channels
The system uses 7 separate audio channels:
- main_theme - for the main menu theme
- ambient_1 to ambient_6 - for ambient tracks
- Channels are automatically registered during initialization

### Smooth transitions
- All volume changes occur smoothly
- Update frequency: 10 times per second
- Exponential interpolation for natural sound

### Multithreading
- System uses Threading for independent control
- Timers for scheduling random tracks
- Does not block the main game thread

## Disabling Main Menu Auto-Start

If you don't want automatic ambient in the main menu:

1. **Don't include** the `ambient_auto_start.rpy` file
2. **Or comment out** the auto-start lines in it:
```renpy
# Comment these lines to disable auto-start:
# on "show" action Function(renpy.call_in_new_context, "start_main_menu_ambient")
# on "hide" action Function(ambient.stop_ambient)
```

This way you can use the system only where you explicitly call it with `$ ambient.start_ambient()`.

## Usage Examples

### Main menu ambient with main theme
```renpy
# Main theme setup
$ ambient.set_main_theme("audio/main_theme.mp3", 45, 0.8, 2.0, 3.0)

# Basic ambient atmosphere
$ ambient.add_track("menu_base", "audio/menu_ambient.ogg", "mandatory", 0.5)

# Random additions
$ ambient.add_track("wind", "audio/wind.ogg", "random", 0.3, 0.4, 45, 120)
$ ambient.add_track("distant_sound", "audio/distant.ogg", "random", 0.6, 0.2, 60, 180)

# Start sequence
$ ambient.start_with_main_theme()
```

### Ambient for different locations
```renpy
# City location
$ ambient.add_track("city_traffic", "audio/traffic.ogg", "mandatory", 0.4)
$ ambient.add_track("city_voices", "audio/voices.ogg", "random", 0.3, 0.5)

# Nature location  
$ ambient.add_track("forest_base", "audio/forest.ogg", "mandatory", 0.6)
$ ambient.add_track("birds", "audio/birds.ogg", "random", 0.4, 0.3)
$ ambient.add_track("wind_trees", "audio/wind_trees.ogg", "random", 0.5, 0.4)
```

## Usage Recommendations

1. **Audio quality**: Use OGG format for better compatibility
2. **Duration**: Mandatory tracks should be looped
3. **Volume**: Leave volume headroom for track layering
4. **Frequency**: Don't make random tracks too frequent
5. **Performance**: Limit the number of simultaneous tracks

## Troubleshooting

### Tracks don't play
- Check file paths are correct
- Ensure files are in OGG format
- Check that the system is running

### Too loud/quiet
- Adjust the volume parameter for individual tracks
- Use ambient.set_base_volume() for overall adjustment
- Check RenPy volume settings

### Performance
- Limit the number of simultaneous tracks
- Use compressed audio files
- Optimize update frequency if needed

## Author and License

Created for RenPy projects with free use and modification permissions. 