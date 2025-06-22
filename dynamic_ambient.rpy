init python:
    import random
    import threading
    import time
    
    class DynamicAmbientSystem:
        """
        Система динамического эмбиента для RenPy
        Управляет воспроизведением нескольких аудиодорожек с настраиваемыми параметрами
        """
        
        def __init__(self):
            # Основные настройки системы
            self.is_active = False
            self.is_main_menu = True
            self.base_volume = 0.7
            self.fade_duration = 2.0
            
            # Хранилище для дорожек и их состояний
            self.tracks = {}
            self.track_states = {}
            self.track_timers = {}
            
            # Список всех активных таймеров для корректной остановки
            self.active_timers = []
            
            # Настройки основной темы меню
            self.main_theme = {
                'filename': None,
                'duration': 0,
                'volume': 0.8,
                'fade_in_time': 2.0,
                'fade_out_time': 3.0,
                'is_playing': False
            }
            
            # Настройки каналов RenPy
            self.ambient_channels = [
                "ambient_1", "ambient_2", "ambient_3", 
                "ambient_4", "ambient_5", "ambient_6"
            ]
            
            # Регистрируем каналы в RenPy
            for channel in self.ambient_channels:
                renpy.music.register_channel(channel, "music", loop=True)
            
            # Отдельный канал для основной темы
            renpy.music.register_channel("main_theme", "music", loop=False)
        
        def add_track(self, track_id, filename, track_type="random", 
                        volume=1.0, play_chance=0.5, min_duration=30, 
                        max_duration=120, fade_in_time=3.0, fade_out_time=3.0):
            """
            Добавляет трек в систему эмбиента
            
            track_id: уникальный идентификатор трека
            filename: путь к аудиофайлу
            track_type: "mandatory" (обязательный) или "random" (случайный)
            volume: базовая громкость трека (0.0-1.0)
            play_chance: шанс воспроизведения для случайных треков (0.0-1.0)
            min_duration: минимальная длительность воспроизведения (секунды)
            max_duration: максимальная длительность воспроизведения (секунды)
            fade_in_time: время плавного появления (секунды)
            fade_out_time: время плавного исчезновения (секунды)
            """
            self.tracks[track_id] = {
                'filename': filename,
                'type': track_type,
                'volume': volume,
                'play_chance': play_chance,
                'min_duration': min_duration,
                'max_duration': max_duration,
                'fade_in_time': fade_in_time,
                'fade_out_time': fade_out_time,
                'channel': None,
                'current_volume': 0.0,
                'target_volume': 0.0,
                'is_playing': False,
                'play_start_time': 0
            }
            
            self.track_states[track_id] = {
                'last_play_time': 0,
                'next_play_time': 0,
                'is_scheduled': False
            }
        
        def set_main_theme(self, filename, duration=60, volume=0.8, 
                            fade_in_time=2.0, fade_out_time=3.0):
            """
            Устанавливает основную тему меню
            
            filename: путь к файлу основной темы
            duration: длительность воспроизведения (секунды)
            volume: громкость (0.0-1.0)
            fade_in_time: время плавного появления
            fade_out_time: время плавного исчезновения
            """
            self.main_theme['filename'] = filename
            self.main_theme['duration'] = duration
            self.main_theme['volume'] = volume
            self.main_theme['fade_in_time'] = fade_in_time
            self.main_theme['fade_out_time'] = fade_out_time
        
        def start_with_main_theme(self):
            """
            Запускает последовательность: основная тема → эмбиент
            """
            if self.main_theme['filename']:
                self._play_main_theme()
            else:
                # Если основной темы нет, сразу запускаем эмбиент
                self.start_ambient()
        
        def _play_main_theme(self):
            """Воспроизводит основную тему меню"""
            if not self.main_theme['filename']:
                return
            
            # Запускаем основную тему
            renpy.music.play(self.main_theme['filename'], 
                            channel="main_theme", 
                            fadein=self.main_theme['fade_in_time'],
                            if_changed=False)
            renpy.music.set_volume(self.main_theme['volume'], channel="main_theme")
            
            self.main_theme['is_playing'] = True
            
            # Планируем остановку основной темы и запуск эмбиента
            theme_duration = self.main_theme['duration']
            fade_out_time = self.main_theme['fade_out_time']
            
            # Начинаем плавное затухание темы за несколько секунд до конца
            fade_start_time = max(0, theme_duration - fade_out_time)
            
            self._create_timer(fade_start_time, self._fade_out_main_theme).start()
            self._create_timer(theme_duration, self._start_ambient_after_theme).start()
        
        def _fade_out_main_theme(self):
            """Плавно завершает основную тему"""
            if self.main_theme['is_playing']:
                renpy.music.stop(channel="main_theme", 
                                fadeout=self.main_theme['fade_out_time'])
        
        def _start_ambient_after_theme(self):
            """Запускает эмбиент после основной темы"""
            self.main_theme['is_playing'] = False
            self.start_ambient()

        def start_ambient(self, delay_after_main_theme=0):
            """
            Запускает систему эмбиента
            delay_after_main_theme: задержка в секундах после основной темы
            """
            if delay_after_main_theme > 0:
                self._create_timer(delay_after_main_theme, self._start_ambient_delayed).start()
            else:
                self._start_ambient_delayed()
        
        def _start_ambient_delayed(self):
            """Внутренний метод для отложенного запуска эмбиента"""
            self.is_active = True
            self._assign_channels()
            self._start_mandatory_tracks()
            self._schedule_random_tracks()
            self._start_volume_manager()
        
        def stop_ambient(self, fade_out=True):
            """
            Останавливает систему эмбиента
            fade_out: плавное затухание при остановке
            """
            self.is_active = False
            
            # Отменяем все активные таймеры
            self._cancel_all_timers()
            
            # Останавливаем основную тему если играет
            if self.main_theme['is_playing']:
                if fade_out:
                    renpy.music.stop(channel="main_theme", 
                                    fadeout=self.main_theme['fade_out_time'])
                else:
                    renpy.music.stop(channel="main_theme")
                self.main_theme['is_playing'] = False
            
            if fade_out:
                # Плавно снижаем громкость всех треков с индивидуальными временами
                max_fade_time = 0
                for track_id, track_data in self.tracks.items():
                    if track_data['is_playing']:
                        track_data['target_volume'] = 0.0
                        max_fade_time = max(max_fade_time, track_data['fade_out_time'])
                
                # Используем максимальное время затухания + небольшой запас
                if max_fade_time > 0:
                    self._create_timer(max_fade_time + 0.5, self._stop_all_tracks).start()
                else:
                    self._stop_all_tracks()
            else:
                self._stop_all_tracks()
        
        def _assign_channels(self):
            """Назначает каналы для треков"""
            channel_index = 0
            for track_id in self.tracks:
                if channel_index < len(self.ambient_channels):
                    self.tracks[track_id]['channel'] = self.ambient_channels[channel_index]
                    channel_index += 1
        
        def _start_mandatory_tracks(self):
            """Запускает обязательные треки"""
            for track_id, track_data in self.tracks.items():
                if track_data['type'] == 'mandatory':
                    self._play_track(track_id)
        
        def _schedule_random_tracks(self):
            """Планирует воспроизведение случайных треков"""
            if not self.is_active:
                return
                
            for track_id, track_data in self.tracks.items():
                if track_data['type'] == 'random' and not track_data['is_playing']:
                    if random.random() < track_data['play_chance']:
                        # Случайная задержка перед воспроизведением
                        delay = random.uniform(1, 15)
                        self._create_timer(delay, lambda tid=track_id: self._play_track(tid)).start()
            
            # Перепланируем через случайное время
            next_schedule = random.uniform(30, 90)
            self._create_timer(next_schedule, self._schedule_random_tracks).start()
        
        def _play_track(self, track_id):
            """Воспроизводит конкретный трек"""
            if not self.is_active:
                return
                
            track_data = self.tracks[track_id]
            channel = track_data['channel']
            
            if not channel:
                return
            
            # Запускаем трек с нулевой громкостью
            renpy.music.play(track_data['filename'], channel=channel, 
                            loop=True, if_changed=False)
            renpy.music.set_volume(0.0, channel=channel)
            
            # Устанавливаем параметры для плавного появления
            track_data['is_playing'] = True
            track_data['current_volume'] = 0.0
            track_data['target_volume'] = track_data['volume'] * self.base_volume
            track_data['play_start_time'] = time.time()
            
            # Планируем остановку для случайных треков
            if track_data['type'] == 'random':
                duration = random.uniform(track_data['min_duration'], 
                                        track_data['max_duration'])
                self.track_timers[track_id] = self._create_timer(
                    duration, lambda: self._stop_track(track_id))
                self.track_timers[track_id].start()
        
        def _stop_track(self, track_id):
            """Останавливает конкретный трек с плавным затуханием"""
            if track_id in self.tracks:
                track_data = self.tracks[track_id]
                
                # Устанавливаем целевую громкость в 0 для плавного затухания
                track_data['target_volume'] = 0.0
                
                # Используем индивидуальный fade_out_time трека
                fade_out_time = track_data['fade_out_time']
                
                # Планируем полную остановку после затухания
                self._create_timer(fade_out_time, 
                                lambda: self._force_stop_track(track_id)).start()
        
        def _force_stop_track(self, track_id):
            """Принудительно останавливает трек"""
            if track_id in self.tracks:
                track_data = self.tracks[track_id]
                if track_data['channel']:
                    renpy.music.stop(channel=track_data['channel'])
                track_data['is_playing'] = False
                track_data['current_volume'] = 0.0
                track_data['target_volume'] = 0.0
                
                # Отменяем таймер если он есть
                if track_id in self.track_timers:
                    self.track_timers[track_id].cancel()
                    del self.track_timers[track_id]
        
        def _stop_all_tracks(self):
            """Останавливает все треки"""
            for track_id in list(self.tracks.keys()):
                self._force_stop_track(track_id)
        
        def _start_volume_manager(self):
            """Запускает менеджер громкости для плавных переходов"""
            self._volume_update_loop()
        
        def _volume_update_loop(self):
            """Цикл обновления громкости треков"""
            if not self.is_active:
                return
            
            current_time = time.time()
            
            for track_id, track_data in self.tracks.items():
                if track_data['is_playing'] and track_data['channel']:
                    current = track_data['current_volume']
                    target = track_data['target_volume']
                    
                    if abs(current - target) > 0.01:
                        # Определяем скорость изменения на основе fade времени
                        if target > current:
                            # Плавное появление - используем fade_in_time
                            fade_time = track_data['fade_in_time']
                        else:
                            # Плавное исчезновение - используем fade_out_time
                            fade_time = track_data['fade_out_time']
                        
                        # Рассчитываем шаг изменения для плавного перехода
                        # За fade_time секунд должны достичь target громкости
                        max_change_per_update = abs(target - current) / (fade_time * 10)  # 10 обновлений в секунду
                        
                        # Ограничиваем скорость изменения
                        if target > current:
                            step = min(max_change_per_update, (target - current) * 0.15)
                        else:
                            step = -min(max_change_per_update, (current - target) * 0.15)
                        
                        new_volume = current + step
                        
                        # Ограничиваем диапазон
                        new_volume = max(0.0, min(target, new_volume)) if target > current else max(target, min(1.0, new_volume))
                        
                        track_data['current_volume'] = new_volume
                        renpy.music.set_volume(new_volume, channel=track_data['channel'])
            
            # Планируем следующее обновление
            self._create_timer(0.1, self._volume_update_loop).start()
        
        def set_base_volume(self, volume):
            """Устанавливает базовую громкость системы"""
            self.base_volume = max(0.0, min(1.0, volume))
            
            # Обновляем целевую громкость для всех треков
            for track_data in self.tracks.values():
                if track_data['is_playing']:
                    track_data['target_volume'] = track_data['volume'] * self.base_volume
        
        def pause_ambient(self):
            """Приостанавливает эмбиент"""
            for track_data in self.tracks.values():
                if track_data['is_playing'] and track_data['channel']:
                    renpy.music.set_pause(True, channel=track_data['channel'])
        
        def resume_ambient(self):
            """Возобновляет эмбиент"""
            for track_data in self.tracks.values():
                if track_data['is_playing'] and track_data['channel']:
                    renpy.music.set_pause(False, channel=track_data['channel'])
        
        def _create_timer(self, delay, callback):
            """Создаёт таймер с отслеживанием для корректной остановки"""
            timer = threading.Timer(delay, callback)
            timer.daemon = True  # Не блокирует выход из программы
            self.active_timers.append(timer)
            return timer
        
        def _cancel_all_timers(self):
            """Отменяет все активные таймеры"""
            for timer in self.active_timers:
                try:
                    if timer.is_alive():
                        timer.cancel()
                except:
                    pass
            self.active_timers.clear()
            
            # Отменяем также таймеры из track_timers
            for timer in self.track_timers.values():
                try:
                    if timer.is_alive():
                        timer.cancel()
                except:
                    pass
            self.track_timers.clear()

    # Создаём глобальный экземпляр системы
    ambient_system = DynamicAmbientSystem()

# Функции для удобного использования в скриптах
define ambient = ambient_system 

# Переменная для хранения настройки громкости
default ambient_volume_setting = 0.7

# Лейбл для запуска эмбиента в главном меню
label start_main_menu_ambient:
    # Проверяем, не запущена ли уже система
    if ambient.is_active or ambient.main_theme['is_playing']:
        return
    
    # Настраиваем треки только один раз
    if not hasattr(store, 'ambient_configured'):
        call setup_ambient
        call setup_main_theme
        $ ambient_configured = True
    
    # Синхронизируем настройку громкости
    $ ambient.set_base_volume(ambient_volume_setting)
    
    # Запускаем последовательность: основная тема → эмбиент
    $ ambient.start_with_main_theme()
    return
