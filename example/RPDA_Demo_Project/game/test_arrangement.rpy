# Test Script for Arrangement System

label start_arrangement_test:
    scene bg room
    
    # Ensure ambient is configured
    # Check if we need to setup (first run OR after reload if arrangements are lost)
    # Ensure ambient is configured
    # Check if we need to setup (first run OR after reload if arrangements are lost)
    # NOTE: Initialization is now automatic via DynamicAmbientSystem.__init__ loading YAMLs.
    # We just check if arrangements are loaded to be safe, but no manual setup needed.
    if not ambient.arrangements:
        $ ambient.load_config() # Reload config if empty (e.g. after hard reset)
        $ ambient_test_configured = True
    
    e "Starting Arrangement System Test (Phase 2)."
    
    menu:
        "Test Intro -> Loop":
            jump test_intro_loop
            
        "Test Layers":
            jump test_layers

        "Test Dynamic Reconfig":
            jump test_reconfig
            
        "Stop Ambient":
            $ ambient.stop_ambient(fade_out=True)
            return

label test_intro_loop:
    ambient debug ui
    e "Playing 'Calm Morning Intro'. It should auto-switch to 'Loop' after 10s."
    
    # Auto-starts ambient system
    $ ambient.play_arrangement("calm_morning_intro")
    
    e "Waiting for transition..."
    pause 12.0
    
    e "Should now be in 'Calm Morning Loop' (louder volume)."

    $ ambient.stop_ambient(fade_out=True)
    
    jump start_arrangement_test

label test_layers:
    e "Playing 'Tense Evening' (Base Layer)."
    
    $ ambient.play_arrangement("tense_evening")
    
    e "Activating 'Rain Layer' (Wind sound)."
    $ ambient.set_layer("rain_layer", active=True)
    
    pause 5.0
    
    e "Deactivating 'Rain Layer' (Fast fade: 1.0s)."
    $ ambient.set_layer("rain_layer", active=False, fade_time=1.0)
    
    pause 5.0
    
    $ ambient.stop_ambient(fade_out=True)
    
    jump start_arrangement_test

label test_reconfig:
    e "Playing 'Storm Override'. 'random_wind' should become MANDATORY and loud."
    
    $ ambient.play_arrangement("storm_override")
    
    e "Listen... Wind should be constant now."
    pause 5.0
    
    e "Switching back to 'Calm Morning Loop'. Wind should be random again."
    $ ambient.play_arrangement("calm_morning_loop")
    
    pause 5.0
    
    $ ambient.stop_ambient(fade_out=True)
    
    jump start_arrangement_test
