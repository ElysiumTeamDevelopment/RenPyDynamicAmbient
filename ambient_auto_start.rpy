# Automatic ambient start when main menu is shown

# Override main menu screen for automatic start
screen main_menu():

    ## This tag ensures that any other screen with the same tag will replace this one.
    tag menu

    # Automatic ambient start when screen is shown
    on "show" action Function(renpy.call_in_new_context, "start_main_menu_ambient")
    
    # Stop ambient when screen is hidden (switch to game or exit)
    on "hide" action Function(ambient.stop_ambient)

    add gui.main_menu_background

    ## This empty frame shades the main menu.
    frame:
        style "main_menu_frame"

    ## The use operator includes another screen here. Actual main menu content is on the navigation screen.
    use navigation

    if gui.show_name:

        vbox:
            style "main_menu_vbox"

            text "[config.name!t]":
                style "main_menu_title"

            text "[config.version]":
                style "main_menu_version"

# Game quit handler for proper ambient stop
init python:
    def quit_callback():
        """Properly stops the ambient system on game exit"""
        try:
            ambient.stop_ambient(fade_out=False)
        except:
            pass
    
    # Register callback on quit
    config.quit_callbacks.append(quit_callback) 