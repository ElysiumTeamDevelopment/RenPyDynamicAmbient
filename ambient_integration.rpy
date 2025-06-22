# Интеграция системы эмбиента с главным меню

# Экран настроек эмбиента
screen ambient_settings():
    tag menu
    
    use game_menu(_("Настройки эмбиента"), scroll="viewport"):
        
        style_prefix "ambient"
        
        vbox:
            spacing 20
            
            # Основная громкость
            hbox:
                spacing 20
                
                text "Громкость эмбиента:" xalign 0.0
                
                bar:
                    xsize 300
                    value VariableValue("ambient_volume_setting", 0.7, 1.0, step=0.01)
                    changed Function(ambient.set_base_volume, ambient_volume_setting)
                    
                text "{:.2f}".format(ambient_volume_setting) xalign 1.0
            
            # Статус системы
            hbox:
                spacing 20
                
                text "Статус системы:" 
                
                if ambient.main_theme['is_playing']:
                    text "Играет основная тема" color "#ffaa00"
                elif ambient.is_active:
                    text "Активен эмбиент" color "#00ff00"
                else:
                    text "Неактивна" color "#ff0000"
            
            # Управление системой
            hbox:
                spacing 20
                
                if ambient.is_active:
                    textbutton "Остановить эмбиент":
                        action Function(ambient.stop_ambient)
                        
                    textbutton "Пауза":
                        action Function(ambient.pause_ambient)
                        
                    textbutton "Продолжить":
                        action Function(ambient.resume_ambient)
                else:
                    textbutton "Запустить эмбиент":
                        action [Function(renpy.call_in_new_context, "setup_ambient"), 
                                Function(ambient.start_ambient)]
            
            # Информация о треках
            text "Активные треки:" size 20
            
            for track_id, track_data in ambient.tracks.items():
                hbox:
                    spacing 10
                    
                    text track_id + ":"
                    
                    if track_data['is_playing']:
                        text "Играет" color "#00ff00"
                        text "({:.1f}%)".format(track_data['current_volume'] * 100)
                    else:
                        text "Остановлен" color "#888888"
                    
                    text "Тип: " + track_data['type']
                    
                    if track_data['type'] == 'random':
                        text "Шанс: {:.0f}%".format(track_data['play_chance'] * 100)

style ambient_hbox:
    spacing 10
    
style ambient_text:
    size 16
    
style ambient_button:
    padding (10, 5)
    
style ambient_button_text:
    size 14

# Добавляем кнопку в меню настроек
screen preferences():
    tag menu
    
    use game_menu(_("Настройки"), scroll="viewport"):
        
        vbox:
            hbox:
                box_wrap True
                
                if renpy.variant("pc") or renpy.variant("web"):
                    
                    vbox:
                        style_prefix "radio"
                        label _("Режим экрана")
                        textbutton _("Оконный") action Preference("display", "window")
                        textbutton _("Полный") action Preference("display", "fullscreen")
                        
                vbox:
                    style_prefix "radio"
                    label _("Сторона отката")
                    textbutton _("Отключить") action Preference("rollback side", "disable")
                    textbutton _("Левая") action Preference("rollback side", "left")
                    textbutton _("Правая") action Preference("rollback side", "right")
                    
                vbox:
                    style_prefix "check"
                    label _("Пропускать")
                    textbutton _("Непрочитанный текст") action Preference("skip", "toggle")
                    textbutton _("После выборов") action Preference("after choices", "toggle")
                    textbutton _("Переходы") action InvertSelected(Preference("transitions", "toggle"))
                    
            null height (4 * gui.pref_spacing)
            
            hbox:
                style_prefix "slider"
                box_wrap True
                
                vbox:
                    label _("Скорость текста")
                    bar value Preference("text speed")
                    
                    label _("Скорость авточтения")
                    bar value Preference("auto-forward time")
                    
                vbox:
                    
                    if config.has_music:
                        label _("Громкость музыки")
                        hbox:
                            bar value Preference("music volume")
                            
                    if config.has_sound:
                        label _("Громкость звуков")
                        hbox:
                            bar value Preference("sound volume")
                            
                        if config.sample_sound:
                            textbutton _("Тест") action Play("sound", config.sample_sound)
                            
                    if config.has_voice:
                        label _("Громкость голоса")
                        hbox:
                            bar value Preference("voice volume")
                            
                        if config.sample_voice:
                            textbutton _("Тест") action Play("voice", config.sample_voice)
                            
                    if config.has_music or config.has_sound or config.has_voice:
                        null height gui.pref_spacing
                        
                        textbutton _("Выключить всё"):
                            action Preference("all mute", "toggle")
                            style "mute_all_button"
            
            # Кнопка настроек эмбиента
            null height (2 * gui.pref_spacing)
            
            textbutton _("Настройки эмбиента"):
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