# Debug screen for Dynamic Ambient System

# Debug screen for Dynamic Ambient System

# Variable to toggle debug screen
default debug_ambient = True

init python:
    def toggle_ambient_debug():
        store.debug_ambient = not store.debug_ambient
        if store.debug_ambient:
            renpy.show_screen("ambient_debug_overlay")
        else:
            renpy.hide_screen("ambient_debug_overlay")

screen ambient_debug_overlay():
    zorder 1000
    
    # Update screen every 0.1 seconds for real-time info
    timer 0.1 repeat True action Function(renpy.restart_interaction)
    
    frame:
            xalign 0.0
            yalign 0.0
            xpadding 10
            ypadding 10
            background "#00000080"
            
            vbox:
                spacing 5
                
                text "Ambient System Debug" size 20 bold True color "#ffffff"
                null height 5
                
                # System Status
                hbox:
                    spacing 10
                    text "Active:" size 16 color "#aaaaaa"
                    if ambient.is_active:
                        text "YES" size 16 color "#00ff00" bold True
                    else:
                        text "NO" size 16 color "#ff0000" bold True
                
                # Arrangement
                $ arr_name = ambient.active_arrangement.name if ambient.active_arrangement else "None"
                $ arr_color = "#ffff00" if ambient.active_arrangement else "#888888"
                hbox:
                    spacing 10
                    text "Arrangement:" size 16 color "#aaaaaa"
                    text "[arr_name]" size 16 color arr_color
                
                # Layers
                hbox:
                    spacing 10
                    text "Layers:" size 16 color "#aaaaaa"
                    if ambient.active_layers:
                        text "[', '.join(ambient.active_layers)]" size 16 color "#00ffff"
                    else:
                        text "None" size 16 color "#888888"
                
                # Stats
                text "Elevated Tracks: [ambient.elevated_tracks_count]" size 14 color "#cccccc"
                if ambient.is_fading_out:
                    text "STATUS: FADING OUT" size 14 color "#ffaa00" bold True
                
                null height 10
                text "Tracks:" size 16 bold True color "#ffffff"
                
                # Track List
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    draggable True
                    ysize 400
                    
                    vbox:
                        spacing 2
                        for track_id in sorted(ambient.tracks.keys()):
                            $ track = ambient.tracks[track_id]
                            hbox:
                                spacing 10
                                if track['is_playing']:
                                    text "●" size 14 color "#00ff00" yalign 0.5
                                else:
                                    text "○" size 14 color "#444444" yalign 0.5
                                
                                vbox:
                                    text "[track_id]" size 14 color "#ffffff"
                                    hbox:
                                        spacing 5
                                        text "Vol: [track['current_volume']:.2f] -> [track['target_volume']:.2f]" size 12 color "#aaaaaa"
                                        if track['channel']:
                                            text "([track['channel']])" size 12 color "#888888"
                                        if track.get('is_elevated'):
                                            text "ELEVATED" size 10 color "#ffaa00"
                                        if track.get('temp_fade_time'):
                                            text "F:[track['temp_fade_time']]" size 10 color "#00ffff"



# Add to overlay screens so it's always visible (controlled by debug_ambient flag)
init python:
    # config.overlay_screens.append("ambient_debug_overlay")
