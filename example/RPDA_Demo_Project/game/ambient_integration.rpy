# Ambient system integration with main menu

# Ambient settings screen
screen ambient_settings():
    tag menu
    
    # Automatic screen update every second
    timer 1.0 repeat True action Function(renpy.restart_interaction)
    
    use game_menu(_("Ambient Settings"), scroll="viewport"):
        
        style_prefix "ambient"
        
        vbox:
            spacing 20
            
            # Main volume
            hbox:
                spacing 20
                
                text "Ambient Volume:" xalign 0.0
                
                bar:
                    xsize 300
                    value VariableValue("ambient_volume_setting", 0.7, 1.0, step=0.01)
                    changed Function(ambient.set_base_volume, ambient_volume_setting)
                    
                text "{:.2f}".format(ambient_volume_setting) xalign 1.0
            
            # System status
            vbox:
                spacing 10
                
                hbox:
                    spacing 20
                text "System Status:" 
                
                if ambient.main_theme['is_playing']:
                    text "Playing Main Theme" color "#ffaa00"
                elif ambient.is_active:
                    text "Ambient Active" color "#00ff00"
                else:
                    text "Inactive" color "#ff0000"
                
                # Ambient runtime
                if ambient.is_active:
                    hbox:
                        spacing 20
                        text "Ambient Runtime:"
                        text ambient.get_formatted_runtime() color "#00ff00" size 18
                        
                # Number of active tracks
                if ambient.is_active and len(ambient.tracks) > 0:
                    $ mandatory_count = sum(1 for t in ambient.tracks.values() if t['type'] == 'mandatory' and t['is_playing'])
                    $ elevated_count = sum(1 for t in ambient.tracks.values() if t['type'] == 'random' and t.get('is_elevated', False))
                    $ total_random = sum(1 for t in ambient.tracks.values() if t['type'] == 'random')
                    
                    hbox:
                        spacing 15
                        text "Tracks:"
                        text "Base: [mandatory_count]" color "#00ff00"
                        text "Audible Layers: [elevated_count]/[total_random]" color "#ffaa00"
            
            # System control
            hbox:
                spacing 20
                
                if ambient.is_active:
                    textbutton "Stop Ambient":
                        action Function(ambient.stop_ambient)
                        
                    textbutton "Pause":
                        action Function(ambient.pause_ambient)
                        
                    textbutton "Resume":
                        action Function(ambient.resume_ambient)
                else:
                    textbutton "Start Ambient":
                        action [Function(renpy.call_in_new_context, "setup_ambient"), 
                                Function(ambient.start_ambient)]
            
            # Track information
            text "Detailed Track Information:" size 20
            
            for track_id, track_data in ambient.tracks.items():
                frame:
                    background "#2a2a2a"
                    padding (10, 5)
                    margin (0, 2)
                    
                    vbox:
                        spacing 5
                        
                        hbox:
                            spacing 10
                            
                            # Track name
                            text "[track_id]:" size 16 color "#ffffff"
                            
                            # Playback status
                            if track_data['is_playing']:
                                if track_data['type'] == 'mandatory':
                                    text "PLAYING" color "#00ff00" size 14
                                elif track_data['type'] == 'random':
                                    if track_data.get('is_elevated', False):
                                        text "AUDIBLE" color "#00ff00" size 14
                                    else:
                                        text "BACKGROUND" color "#ffaa00" size 14
                            else:
                                text "STOPPED" color "#ff0000" size 14
                        
                        hbox:
                            spacing 15
                            
                            # Track type and parameters
                            text "Type: [track_data['type']]" size 12
                            
                            # Volume
                            text "Volume: {:.1f}%".format(track_data.get('current_volume', 0) * 100) size 12 color "#aaaaaa"
                            
                            # Track runtime
                            if track_data['is_playing']:
                                $ track_runtime_seconds = ambient.get_track_runtime(track_id)
                                $ track_minutes = int(track_runtime_seconds // 60)
                                $ track_seconds = int(track_runtime_seconds % 60)
                                text "Runtime: {:02d}:{:02d}".format(track_minutes, track_seconds) size 12 color "#aaaaaa"
                                
                                # For random tracks show elevated volume time
                                if track_data['type'] == 'random' and track_data.get('is_elevated', False):
                                    $ elevation_time = ambient.get_track_elevation_time(track_id)
                                    $ elevation_minutes = int(elevation_time // 60)
                                    $ elevation_seconds = int(elevation_time % 60)
                                    text "Audible: {:02d}:{:02d}".format(elevation_minutes, elevation_seconds) size 11 color "#ffff00"
                            
                            # Additional information for random tracks
                            if track_data['type'] == 'random':
                                text "Chance: {:.0f}%".format(track_data['play_chance'] * 100) size 12 color "#aaaaaa"
                                
                                # Duration indicator for random tracks
                                text "Duration: {:.0f}-{:.0f}s".format(track_data['min_duration'], track_data['max_duration']) size 11 color "#888888"
            
            # Debug system statistics
            if ambient.is_active:
                null height 20
                
                text "System Statistics:" size 18 color "#cccccc"
                
                frame:
                    background "#1a1a1a"
                    padding (10, 8)
                    
                    hbox:
                        spacing 30
                        
                        vbox:
                            spacing 5
                            text "General:" size 14 color "#ffffff"
                            text "Total Tracks: {}".format(len(ambient.tracks)) size 12
                            text "Playing: {}".format(sum(1 for t in ambient.tracks.values() if t['is_playing'])) size 12
                            text "Base Volume: {:.0f}%".format(ambient.base_volume * 100) size 12
                            
                        vbox:
                            spacing 5
                            text "Timers:" size 14 color "#ffffff"
                            text "Active: {}".format(len(ambient.active_timers)) size 12
                            text "Track Timers: {}".format(len(ambient.track_timers)) size 12
                            
                        vbox:
                            spacing 5
                            text "Channels:" size 14 color "#ffffff"
                            text "Available: {}".format(len(ambient.ambient_channels)) size 12
                            $ used_channels = sum(1 for t in ambient.tracks.values() if t.get('channel') and t['is_playing'])
                            text "Used: {}".format(used_channels) size 12
                            
                        vbox:
                            spacing 5
                            text "Pseudo-Random:" size 14 color "#ffffff"
                            
                            # Current wave information
                            if ambient.current_wave_limit > 0:
                                text "Wave: {}/{}".format(ambient.wave_elevation_count, ambient.current_wave_limit) size 11 color "#00aa00"
                            else:
                                text "No Active Wave" size 11 color "#888888"
                                
                            # Debug: available random tracks count
                            $ available_random = sum(1 for t in ambient.tracks.values() if t['type'] == 'random' and t['is_playing'])
                            text "Available Random: {}".format(available_random) size 10 color "#666666"
                                
                            if ambient.elevated_tracks_count > 0:
                                text "Elevated: {}".format(ambient.elevated_tracks_count) size 11 color "#00ff00"
                            else:
                                text "All Tracks in Background" size 11 color "#888888"
                                
                            # Fading tracks
                            if len(ambient.tracks_fading_out) > 0:
                                text "Fading: {}".format(len(ambient.tracks_fading_out)) size 11 color "#ffaa00"
                                
                            # Show cooldown
                            $ import time as time_module
                            $ current_time = time_module.time()
                            if current_time < ambient.global_cooldown_end_time:
                                $ cooldown_left = int(ambient.global_cooldown_end_time - current_time)
                                text "Cooldown: {}s".format(cooldown_left) size 11 color "#ffaa00"
                            else:
                                # Check startup cooldown (approximate)
                                $ runtime = ambient.get_ambient_runtime()
                                if runtime < ambient.initial_cooldown_time:
                                    $ startup_left = int(ambient.initial_cooldown_time - runtime)
                                    text "Startup: {}s".format(startup_left) size 11 color "#ff8800"
                                else:
                                    text "Ready for Wave" size 11 color "#00aa00"

style ambient_hbox:
    spacing 10
    
style ambient_text:
    size 16
    
style ambient_button:
    padding (10, 5)
    
style ambient_button_text:
    size 14

# Add button to settings menu
screen preferences():
    tag menu
    
    use game_menu(_("Preferences"), scroll="viewport"):
        
        vbox:
            hbox:
                box_wrap True
                
                if renpy.variant("pc") or renpy.variant("web"):
                    
                    vbox:
                        style_prefix "radio"
                        label _("Display")
                        textbutton _("Window") action Preference("display", "window")
                        textbutton _("Fullscreen") action Preference("display", "fullscreen")
                        
                vbox:
                    style_prefix "radio"
                    label _("Rollback Side")
                    textbutton _("Disable") action Preference("rollback side", "disable")
                    textbutton _("Left") action Preference("rollback side", "left")
                    textbutton _("Right") action Preference("rollback side", "right")
                    
                vbox:
                    style_prefix "check"
                    label _("Skip")
                    textbutton _("Unseen Text") action Preference("skip", "toggle")
                    textbutton _("After Choices") action Preference("after choices", "toggle")
                    textbutton _("Transitions") action InvertSelected(Preference("transitions", "toggle"))
                    
            null height (4 * gui.pref_spacing)
            
            hbox:
                style_prefix "slider"
                box_wrap True
                
                vbox:
                    label _("Text Speed")
                    bar value Preference("text speed")
                    
                    label _("Auto-Forward Time")
                    bar value Preference("auto-forward time")
                    
                vbox:
                    
                    if config.has_music:
                        label _("Music Volume")
                        hbox:
                            bar value Preference("music volume")
                            
                    if config.has_sound:
                        label _("Sound Volume")
                        hbox:
                            bar value Preference("sound volume")
                            
                        if config.sample_sound:
                            textbutton _("Test") action Play("sound", config.sample_sound)
                            
                    if config.has_voice:
                        label _("Voice Volume")
                        hbox:
                            bar value Preference("voice volume")
                            
                        if config.sample_voice:
                            textbutton _("Test") action Play("voice", config.sample_voice)
                            
                    if config.has_music or config.has_sound or config.has_voice:
                        null height gui.pref_spacing
                        
                        textbutton _("Mute All"):
                            action Preference("all mute", "toggle")
                            style "mute_all_button"
            
            # Ambient settings button
            null height (2 * gui.pref_spacing)
            
            textbutton _("Ambient Settings"):
                action ShowMenu("ambient_settings")
                style "ambient_settings_button"

style ambient_settings_button:
    padding (20, 10)
    background "#2a2a2a"
    hover_background "#3a3a3a"
    
style ambient_settings_button_text:
    size 18
    color "#ffffff"
    hover_color "#00ff00" 