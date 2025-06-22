# Конфигурация динамического эмбиента
# Настройка всех треков для системы

label setup_ambient:
    # Настройка базовых треков эмбиента
    
    # Обязательные фоновые треки (играют постоянно)
    $ ambient.add_track(
        track_id="base_ambient_1",
        filename="audio/ambient_base_1.ogg",
        track_type="mandatory",
        volume=0.6,
        fade_in_time=4.0,
        fade_out_time=4.0
    )
    
    $ ambient.add_track(
        track_id="base_ambient_2", 
        filename="audio/ambient_base_2.ogg",
        track_type="mandatory",
        volume=0.4,
        fade_in_time=5.0,
        fade_out_time=3.0
    )
    
    # Случайные атмосферные треки
    $ ambient.add_track(
        track_id="random_wind",
        filename="audio/ambient_wind.ogg", 
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
        filename="audio/ambient_nature.ogg",
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
        filename="audio/ambient_atmosphere.ogg",
        track_type="random",
        volume=0.7,
        play_chance=0.25,
        min_duration=60,
        max_duration=240,
        fade_in_time=8.0,
        fade_out_time=6.0
    )
    
    return

# Настройка основной темы меню
label setup_main_theme:
    # Устанавливаем основную тему меню
    $ ambient.set_main_theme(
        filename="audio/main_theme.ogg",
        duration=40,        # длительность в секундах
        volume=0.8,         # громкость основной темы
        fade_in_time=2.0,   # плавное появление
        fade_out_time=4.0   # плавное исчезновение
    )
    return

# Пример запуска последовательности: основная тема → эмбиент
label start_theme_and_ambient:
    # Настраиваем треки эмбиента
    call setup_ambient
    
    # Настраиваем основную тему
    call setup_main_theme
    
    # Запускаем последовательность: сначала тема, потом эмбиент
    $ ambient.start_with_main_theme()
    
    return

# Лейбл для остановки эмбиента при переходе в игру
label stop_main_menu_ambient:
    $ ambient.stop_ambient(fade_out=True)
    return

# Настройки громкости эмбиента
label adjust_ambient_volume:
    menu:
        "Громкость эмбиента:"
        
        "Тихо (30%)":
            $ ambient.set_base_volume(0.3)
            
        "Средне (50%)":
            $ ambient.set_base_volume(0.5)
            
        "Нормально (70%)":
            $ ambient.set_base_volume(0.7)
            
        "Громко (90%)":
            $ ambient.set_base_volume(0.9)
    
    return 