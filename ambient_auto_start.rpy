# Автоматический запуск эмбиента при показе главного меню

# Переопределяем экран главного меню для автоматического запуска
screen main_menu():

    ## Этот тег гарантирует, что любой другой экран с тем же тегом будет
    ## заменять этот.
    tag menu

    # Автоматический запуск эмбиента при показе экрана
    on "show" action Function(renpy.call_in_new_context, "start_main_menu_ambient")
    
    # Остановка эмбиента при скрытии экрана (переход в игру или выход)
    on "hide" action Function(ambient.stop_ambient)

    add gui.main_menu_background

    ## Эта пустая рамка затеняет главное меню.
    frame:
        style "main_menu_frame"

    ## Оператор use включает отображение другого экрана в данном. Актуальное
    ## содержание главного меню находится на экране навигации.
    use navigation

    if gui.show_name:

        vbox:
            style "main_menu_vbox"

            text "[config.name!t]":
                style "main_menu_title"

            text "[config.version]":
                style "main_menu_version"

# Обработчик завершения игры для корректной остановки
init python:
    def quit_callback():
        """Корректно останавливает систему эмбиента при выходе из игры"""
        try:
            ambient.stop_ambient(fade_out=False)
        except:
            pass
    
    # Регистрируем callback на выход
    config.quit_callbacks.append(quit_callback) 