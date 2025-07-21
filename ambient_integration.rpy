# Integration of the ambient system with the main menu

# Ambient settings screen
screen ambient_settings():
    tag menu
    
    use game_menu(_("Ambient Settings"), scroll="viewport"):
        
        style_prefix "ambient"
        
        vbox:
            spacing 20
            
            # Main volume
            hbox:
                spacing 20
                
                text "Ambient volume:" xalign 0.0
                
                bar:
                    xsize 300
                    value VariableValue("ambient_volume_setting", 0.7, 1.0, step=0.01)
                    changed Function(ambient.set_base_volume, ambient_volume_setting)
                    
                text "{:.2f}".format(ambient_volume_setting) xalign 1.0
            
            # System status
            hbox:
                spacing 20
                
                text "System status:" 
                
                if ambient.main_theme['is_playing']:
                    text "Main theme playing" color "#ffaa00"
                elif ambient.is_active:
                    text "Ambient active" color "#00ff00"
                else:
                    text "Inactive" color "#ff0000"
            
            # System control
            hbox:
                spacing 20
                
                if ambient.is_active:
                    textbutton "Stop ambient":
                        action Function(ambient.stop_ambient)
                        
                    textbutton "Pause":
                        action Function(ambient.pause_ambient)
                        
                    textbutton "Resume":
                        action Function(ambient.resume_ambient)
                else:
                    textbutton "Start ambient":
                        action [Function(renpy.call_in_new_context, "setup_ambient"), 
                                Function(ambient.start_ambient)]
            
            # Track information
            text "Active tracks:" size 20
            
            for track_id, track_data in ambient.tracks.items():
                hbox:
                    spacing 10
                    
                    text track_id + ":"
                    
                    if track_data['is_playing']:
                        text "Playing" color "#00ff00"
                        text "({:.1f}%)".format(track_data['current_volume'] * 100)
                    else:
                        text "Stopped" color "#888888"
                    
                    text "Type: " + track_data['type']
                    
                    if track_data['type'] == 'random':
                        text "Chance: {:.0f}%".format(track_data['play_chance'] * 100)

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
    
    use game_menu(_("Settings"), scroll="viewport"):
        
        vbox:
            hbox:
                box_wrap True
                
                if renpy.variant("pc") or renpy.variant("web"):
                    
                    vbox:
                        style_prefix "radio"
                        label _("Screen mode")
                        textbutton _("Windowed") action Preference("display", "window")
                        textbutton _("Fullscreen") action Preference("display", "fullscreen")
                        
                vbox:
                    style_prefix "radio"
                    label _("Rollback side")
                    textbutton _("Disable") action Preference("rollback side", "disable")
                    textbutton _("Left") action Preference("rollback side", "left")
                    textbutton _("Right") action Preference("rollback side", "right")
                    
                vbox:
                    style_prefix "check"
                    label _("Skip")
                    textbutton _("Unread text") action Preference("skip", "toggle")
                    textbutton _("After choices") action Preference("after choices", "toggle")
                    textbutton _("Transitions") action InvertSelected(Preference("transitions", "toggle"))
                    
            null height (4 * gui.pref_spacing)
            
            hbox:
                style_prefix "slider"
                box_wrap True
                
                vbox:
                    label _("Text speed")
                    bar value Preference("text speed")
                    
                    label _("Auto-forward speed")
                    bar value Preference("auto-forward time")
                    
                vbox:
                    
                    if config.has_music:
                        label _("Music volume")
                        hbox:
                            bar value Preference("music volume")
                            
                    if config.has_sound:
                        label _("Sound volume")
                        hbox:
                            bar value Preference("sound volume")
                            
                        if config.sample_sound:
                            textbutton _("Test") action Play("sound", config.sample_sound)
                            
                    if config.has_voice:
                        label _("Voice volume")
                        hbox:
                            bar value Preference("voice volume")
                            
                        if config.sample_voice:
                            textbutton _("Test") action Play("voice", config.sample_voice)
                            
                    if config.has_music or config.has_sound or config.has_voice:
                        null height gui.pref_spacing
                        
                        textbutton _("Mute all"):
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