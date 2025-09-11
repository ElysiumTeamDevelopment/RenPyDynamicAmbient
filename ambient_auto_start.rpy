# Automatic ambient start when showing main menu

# Override main menu screen for automatic start
screen main_menu():

    ## This tag ensures that any other screen with the same tag will
    ## replace this one.
    tag menu

    # Automatic ambient start when screen is shown
    on "show" action Function(renpy.call_in_new_context, "start_main_menu_ambient")
    
    # Stop ambient when screen is hidden (entering game or exit)
    on "hide" action Function(ambient.stop_ambient)

    add gui.main_menu_background

    ## This empty frame shadows the main menu.
    frame:
        style "main_menu_frame"

    ## The use statement includes another screen within this one. The actual
    ## contents of the main menu are on the navigation screen.
    use navigation

    if gui.show_name:

        vbox:
            style "main_menu_vbox"

            text "[config.name!t]":
                style "main_menu_title"

            text "[config.version]":
                style "main_menu_version"

# Game exit handler for proper cleanup
init python:
    def quit_callback():
        """Properly stops ambient system on game exit"""
        try:
            ambient.stop_ambient(fade_out=False)
        except:
            pass
    
    # Register callback on exit
    config.quit_callbacks.append(quit_callback) 