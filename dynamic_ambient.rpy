init python:
    import random
    import threading
    import time
    # ambient_templates will be accessed via store
    
    def apply_ambient_template(ambient, template_name):
        """
        Adds all tracks from the specified template to the ambient system.
        ambient: instance of DynamicAmbientSystem
        template_name: key from store.ambient_templates
        
        Example:
            apply_ambient_template(ambient, "street_ambient")
        or:
            ambient.use_template("street_ambient")
        """
        templates = getattr(store, "ambient_templates", None)
        if not templates or template_name not in templates:
            raise ValueError("Unknown ambient template: %s" % template_name)
        for params in templates[template_name]:
            ambient.add_track(**params)
    
    class DynamicAmbientSystem:
        """
        Dynamic ambient system for RenPy
        Manages playback of multiple audio tracks with customizable parameters
        """
        
        def __init__(self):
            # Main system settings
            self.is_active = False
            self.is_main_menu = True
            self.base_volume = 0.7
            self.fade_duration = 2.0
            
            # Storage for tracks and their states
            self.tracks = {}
            self.track_states = {}
            self.track_timers = {}
            
            # List of all active timers for proper stopping
            self.active_timers = []
            
            # Main menu theme settings
            self.main_theme = {
                'filename': None,
                'duration': 0,
                'volume': 0.8,
                'fade_in_time': 2.0,
                'fade_out_time': 3.0,
                'is_playing': False
            }
            
            # RenPy channel settings
            self.ambient_channels = [
                "ambient_1", "ambient_2", "ambient_3", 
                "ambient_4", "ambient_5", "ambient_6"
            ]
            
            # Register channels in RenPy
            for channel in self.ambient_channels:
                renpy.music.register_channel(channel, "music", loop=True)
            
            # Separate channel for the main theme
            renpy.music.register_channel("main_theme", "music", loop=False)
        
        def use_template(self, template_name):
            """
            Adds all tracks from a template (see ambient_templates.rpy)
            Example:
                ambient.use_template("street_ambient")
            """
            apply_ambient_template(self, template_name)
        
        def add_track(self, track_id, filename, track_type="random", 
                        volume=1.0, play_chance=0.5, min_duration=30, 
                        max_duration=120, fade_in_time=3.0, fade_out_time=3.0):
            """
            Adds a track to the ambient system
            
            track_id: unique track identifier
            filename: path to audio file
            track_type: "mandatory" or "random"
            volume: base track volume (0.0-1.0)
            play_chance: play chance for random tracks (0.0-1.0)
            min_duration: minimum playback duration (seconds)
            max_duration: maximum playback duration (seconds)
            fade_in_time: fade-in time (seconds)
            fade_out_time: fade-out time (seconds)
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
            Sets the main menu theme
            
            filename: path to main theme file
            duration: playback duration (seconds)
            volume: volume (0.0-1.0)
            fade_in_time: fade-in time
            fade_out_time: fade-out time
            """
            self.main_theme['filename'] = filename
            self.main_theme['duration'] = duration
            self.main_theme['volume'] = volume
            self.main_theme['fade_in_time'] = fade_in_time
            self.main_theme['fade_out_time'] = fade_out_time
        
        def start_with_main_theme(self):
            """
            Starts sequence: main theme → ambient
            """
            if self.main_theme['filename']:
                self._play_main_theme()
            else:
                # If no main theme, start ambient immediately
                self.start_ambient()
        
        def _play_main_theme(self):
            """Plays the main menu theme"""
            if not self.main_theme['filename']:
                return
            
            # Start main theme
            renpy.music.play(self.main_theme['filename'], 
                            channel="main_theme", 
                            fadein=self.main_theme['fade_in_time'],
                            if_changed=False)
            renpy.music.set_volume(self.main_theme['volume'], channel="main_theme")
            
            self.main_theme['is_playing'] = True
            
            # Schedule main theme stop and ambient start
            theme_duration = self.main_theme['duration']
            fade_out_time = self.main_theme['fade_out_time']
            
            # Start fade out a few seconds before the end
            fade_start_time = max(0, theme_duration - fade_out_time)
            
            self._create_timer(fade_start_time, self._fade_out_main_theme).start()
            self._create_timer(theme_duration, self._start_ambient_after_theme).start()
        
        def _fade_out_main_theme(self):
            """Smoothly finishes the main theme"""
            if self.main_theme['is_playing']:
                renpy.music.stop(channel="main_theme", 
                                fadeout=self.main_theme['fade_out_time'])
        
        def _start_ambient_after_theme(self):
            """Starts ambient after the main theme"""
            self.main_theme['is_playing'] = False
            self.start_ambient()

        def start_ambient(self, delay_after_main_theme=0):
            """
            Starts the ambient system
            delay_after_main_theme: delay in seconds after the main theme
            """
            if delay_after_main_theme > 0:
                self._create_timer(delay_after_main_theme, self._start_ambient_delayed).start()
            else:
                self._start_ambient_delayed()
        
        def _start_ambient_delayed(self):
            """Internal method for delayed ambient start"""
            self.is_active = True
            self._assign_channels()
            self._start_mandatory_tracks()
            self._schedule_random_tracks()
            self._start_volume_manager()
        
        def stop_ambient(self, fade_out=True):
            """
            Stops the ambient system
            fade_out: smooth fade out on stop
            """
            self.is_active = False
            
            # Cancel all active timers
            self._cancel_all_timers()
            
            # Stop main theme if playing
            if self.main_theme['is_playing']:
                if fade_out:
                    renpy.music.stop(channel="main_theme", 
                                    fadeout=self.main_theme['fade_out_time'])
                else:
                    renpy.music.stop(channel="main_theme")
                self.main_theme['is_playing'] = False
            
            if fade_out:
                # Smoothly decrease volume of all tracks with individual fade times
                max_fade_time = 0
                for track_id, track_data in self.tracks.items():
                    if track_data['is_playing']:
                        track_data['target_volume'] = 0.0
                        max_fade_time = max(max_fade_time, track_data['fade_out_time'])
                
                # Use max fade out time + small buffer
                if max_fade_time > 0:
                    self._create_timer(max_fade_time + 0.5, self._stop_all_tracks).start()
                else:
                    self._stop_all_tracks()
            else:
                self._stop_all_tracks()
        
        def _assign_channels(self):
            """Assigns channels for tracks"""
            channel_index = 0
            for track_id in self.tracks:
                if channel_index < len(self.ambient_channels):
                    self.tracks[track_id]['channel'] = self.ambient_channels[channel_index]
                    channel_index += 1
        
        def _start_mandatory_tracks(self):
            """Starts mandatory tracks"""
            for track_id, track_data in self.tracks.items():
                if track_data['type'] == 'mandatory':
                    self._play_track(track_id)
        
        def _schedule_random_tracks(self):
            """Schedules playback of random tracks"""
            if not self.is_active:
                return
                
            for track_id, track_data in self.tracks.items():
                if track_data['type'] == 'random' and not track_data['is_playing']:
                    if random.random() < track_data['play_chance']:
                        # Random delay before playback
                        delay = random.uniform(1, 15)
                        self._create_timer(delay, lambda tid=track_id: self._play_track(tid)).start()
            
            # Reschedule after a random time
            next_schedule = random.uniform(30, 90)
            self._create_timer(next_schedule, self._schedule_random_tracks).start()
        
        def _play_track(self, track_id):
            """Plays a specific track"""
            if not self.is_active:
                return
                
            track_data = self.tracks[track_id]
            channel = track_data['channel']
            
            if not channel:
                return
            
            # Start track with zero volume
            renpy.music.play(track_data['filename'], channel=channel, 
                            loop=True, if_changed=False)
            renpy.music.set_volume(0.0, channel=channel)
            
            # Set parameters for smooth fade in
            track_data['is_playing'] = True
            track_data['current_volume'] = 0.0
            track_data['target_volume'] = track_data['volume'] * self.base_volume
            track_data['play_start_time'] = time.time()
            
            # Schedule stop for random tracks
            if track_data['type'] == 'random':
                duration = random.uniform(track_data['min_duration'], 
                                        track_data['max_duration'])
                self.track_timers[track_id] = self._create_timer(
                    duration, lambda: self._stop_track(track_id))
                self.track_timers[track_id].start()
        
        def _stop_track(self, track_id):
            """Stops a specific track with smooth fade out"""
            if track_id in self.tracks:
                track_data = self.tracks[track_id]
                
                # Set target volume to 0 for smooth fade out
                track_data['target_volume'] = 0.0
                
                # Use individual track fade_out_time
                fade_out_time = track_data['fade_out_time']
                
                # Schedule full stop after fade out
                self._create_timer(fade_out_time, 
                                lambda: self._force_stop_track(track_id)).start()
        
        def _force_stop_track(self, track_id):
            """Forcibly stops a track"""
            if track_id in self.tracks:
                track_data = self.tracks[track_id]
                if track_data['channel']:
                    renpy.music.stop(channel=track_data['channel'])
                track_data['is_playing'] = False
                track_data['current_volume'] = 0.0
                track_data['target_volume'] = 0.0
                
                # Cancel timer if exists
                if track_id in self.track_timers:
                    self.track_timers[track_id].cancel()
                    del self.track_timers[track_id]
        
        def _stop_all_tracks(self):
            """Stops all tracks"""
            for track_id in list(self.tracks.keys()):
                self._force_stop_track(track_id)
        
        def _start_volume_manager(self):
            """Starts volume manager for smooth transitions"""
            self._volume_update_loop()
        
        def _volume_update_loop(self):
            """Track volume update loop"""
            if not self.is_active:
                return
            
            current_time = time.time()
            
            for track_id, track_data in self.tracks.items():
                if track_data['is_playing'] and track_data['channel']:
                    current = track_data['current_volume']
                    target = track_data['target_volume']
                    
                    if abs(current - target) > 0.01:
                        # Determine change speed based on fade time
                        if target > current:
                            # Smooth fade in - use fade_in_time
                            fade_time = track_data['fade_in_time']
                        else:
                            # Smooth fade out - use fade_out_time
                            fade_time = track_data['fade_out_time']
                        
                        # Calculate update step for smooth transition
                        # Should reach target volume in fade_time seconds
                        max_change_per_update = abs(target - current) / (fade_time * 10)  # 10 updates per second
                        
                        # Limit change speed
                        if target > current:
                            step = min(max_change_per_update, (target - current) * 0.15)
                        else:
                            step = -min(max_change_per_update, (current - target) * 0.15)
                        
                        new_volume = current + step
                        
                        # Limit range
                        new_volume = max(0.0, min(target, new_volume)) if target > current else max(target, min(1.0, new_volume))
                        
                        track_data['current_volume'] = new_volume
                        renpy.music.set_volume(new_volume, channel=track_data['channel'])
            
            # Schedule next update
            self._create_timer(0.1, self._volume_update_loop).start()
        
        def set_base_volume(self, volume):
            """Sets the base system volume"""
            self.base_volume = max(0.0, min(1.0, volume))
            
            # Update target volume for all tracks
            for track_data in self.tracks.values():
                if track_data['is_playing']:
                    track_data['target_volume'] = track_data['volume'] * self.base_volume
        
        def pause_ambient(self):
            """Pauses ambient"""
            for track_data in self.tracks.values():
                if track_data['is_playing'] and track_data['channel']:
                    renpy.music.set_pause(True, channel=track_data['channel'])
        
        def resume_ambient(self):
            """Resumes ambient"""
            for track_data in self.tracks.values():
                if track_data['is_playing'] and track_data['channel']:
                    renpy.music.set_pause(False, channel=track_data['channel'])
        
        def _create_timer(self, delay, callback):
            """Creates a timer with tracking for proper stopping"""
            timer = threading.Timer(delay, callback)
            timer.daemon = True  # Does not block program exit
            self.active_timers.append(timer)
            return timer
        
        def _cancel_all_timers(self):
            """Cancels all active timers"""
            for timer in self.active_timers:
                try:
                    if timer.is_alive():
                        timer.cancel()
                except:
                    pass
            self.active_timers.clear()
            
            # Also cancel timers from track_timers
            for timer in self.track_timers.values():
                try:
                    if timer.is_alive():
                        timer.cancel()
                except:
                    pass
            self.track_timers.clear()

    # Create global system instance
    ambient_system = DynamicAmbientSystem()

# Functions for convenient use in scripts
define ambient = ambient_system 

# Variable for storing volume setting
default ambient_volume_setting = 0.7

# Label for starting ambient in main menu
label start_main_menu_ambient:
    # Check if system is already running
    if ambient.is_active or ambient.main_theme['is_playing']:
        return
    
    # Configure tracks only once
    if not hasattr(store, 'ambient_configured'):
        call setup_ambient
        call setup_main_theme
        $ ambient_configured = True
    
    # Synchronize volume setting
    $ ambient.set_base_volume(ambient_volume_setting)
    
    # Start sequence: main theme → ambient
    $ ambient.start_with_main_theme()
    return
