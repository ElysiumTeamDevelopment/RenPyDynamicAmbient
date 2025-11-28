label test_cds:
    "Testing Creator-Defined Statements..."

    "1. Start Main Theme"
    ambient start_theme
    "Main theme should be playing."
    pause 2.0
    ambient stop

    "2. Play Arrangement 'calm_morning' with fade 2.0"
    ambient play "calm_morning" fade 2.0
    "Transitioning to calm_morning..."
    pause 3.0

    "3. Debug Info"
    ambient debug info
    ambient debug tracks
    "Check console for debug output."

    "4. Layer Control: Rain ON"
    ambient layer "rain" on fade 1.0
    "Rain layer should be active."
    pause 2.0

    "5. Volume Control: Set to 0.5"
    ambient volume 0.5
    "Volume should be lower."
    pause 2.0

    "6. Schedule: Storm in 3 seconds"
    ambient schedule "storm_override" in 3.0
    "Waiting for storm..."
    pause 4.0
    "Storm should be active now."

    "7. Pause Ambient"
    ambient pause
    "Ambient paused."
    pause 2.0

    "8. Resume Ambient"
    ambient resume
    "Ambient resumed."
    pause 2.0

    "9. Stop Ambient"
    ambient stop fade 2.0
    "Stopping ambient..."
    pause 3.0

    "Test Complete."
    return
