# Dynamic ambient configuration
# Setup of all tracks for the system

label setup_ambient:
    # Base ambient tracks setup
    
    # Mandatory background tracks (play constantly)
    $ ambient.add_track(
        track_id="base_ambient_1",
        filename="audio/base_ambient_1.ogg",
        track_type="mandatory",
        volume=0.6,
        fade_in_time=4.0,
        fade_out_time=4.0
    )
    
    $ ambient.add_track(
        track_id="base_ambient_2", 
        filename="audio/base_ambient_2.ogg",
        track_type="mandatory",
        volume=0.4,
        fade_in_time=5.0,
        fade_out_time=3.0
    )
    
    # Random atmospheric tracks
    $ ambient.add_track(
        track_id="random_wind",
        filename="audio/wind_ambient.ogg", 
        track_type="random",
        volume=0.8,
        play_chance=0.3,
        min_duration=45,
        max_duration=180,
        fade_in_time=6.0,
        fade_out_time=4.0
    )
    
    $ ambient.add_track(
        track_id="random_nature",
        filename="audio/nature_ambient.ogg",
        track_type="random", 
        volume=0.5,
        play_chance=0.4,
        min_duration=30,
        max_duration=120,
        fade_in_time=3.0,
        fade_out_time=3.0
    )
    
    $ ambient.add_track(
        track_id="random_atmosphere",
        filename="audio/atmosphere_ambient.ogg",
        track_type="random",
        volume=0.7,
        play_chance=0.25,
        min_duration=60,
        max_duration=240,
        fade_in_time=8.0,
        fade_out_time=6.0
    )
    
    return

# Main menu theme setup
label setup_main_theme:
    # Set main menu theme
    $ ambient.set_main_theme(
        filename="audio/main_theme.mp3",
        duration=40,        # duration in seconds
        volume=0.8,         # main theme volume
        fade_in_time=2.0,   # fade in
        fade_out_time=4.0   # fade out
    )
    return

# Example of sequence start: main theme → ambient
label start_theme_and_ambient:
    # Set up ambient tracks
    call setup_ambient
    
    # Set up main theme
    call setup_main_theme
    
    # Start sequence: first theme, then ambient
    $ ambient.start_with_main_theme()
    
    return

# Label to stop ambient when entering game
label stop_main_menu_ambient:
    $ ambient.stop_ambient(fade_out=True)
    return

# Ambient volume settings
label adjust_ambient_volume:
    menu:
        "Ambient Volume:"
        
        "Quiet (30%)": 
            $ ambient.set_base_volume(0.3)
            
        "Medium (50%)": 
            $ ambient.set_base_volume(0.5)
            
        "Normal (70%)": 
            $ ambient.set_base_volume(0.7)
            
        "Loud (90%)": 
            $ ambient.set_base_volume(0.9)
    
    return 