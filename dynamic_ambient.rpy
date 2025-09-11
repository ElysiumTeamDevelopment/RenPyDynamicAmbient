init python:
    import random
    import threading
    import time
    
    class DynamicAmbientSystem:
        """
        Dynamic ambient system for RenPy
        Manages playback of multiple audio tracks with configurable parameters
        """
        
        def __init__(self):
            # Main system settings
            self.is_active = False
            self.is_main_menu = True
            self.base_volume = 0.7
            self.fade_duration = 2.0
            self.minimum_volume = 0.00  # Minimum volume for random tracks
            
            # System runtime tracking
            self.ambient_start_time = 0
            self.last_update_time = 0
            
            # Pseudo-random system for controlling track elevations
            self.global_cooldown_end_time = 0  # End time of global cooldown
            self.minimum_rest_time = 10.0      # Minimum rest between waves (seconds)
            self.maximum_rest_time = 30.0      # Maximum rest between waves (seconds)
            self.elevated_tracks_count = 0     # Number of currently elevated tracks
            
            # Control of elevation wave sizes
            self.min_tracks_per_wave = 1       # Minimum tracks per wave
            self.max_tracks_per_wave = 3       # Maximum tracks per wave  
            self.current_wave_limit = 0        # Track limit for current wave
            self.wave_elevation_count = 0      # How many tracks elevated in current wave
            
            # Initial cooldown
            self.initial_cooldown_time = 15.0  # Time until first random tracks (seconds)
            self.tracks_fading_out = set()     # Tracks still fading to minimum_volume
            
            # Storage for tracks and their states
            self.tracks = {}
            self.track_states = {}
            self.track_timers = {}
            
            # List of all active timers for proper cleanup
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
            
            # Separate channel for main theme
            renpy.music.register_channel("main_theme", "music", loop=False)
        
        def add_track(self, track_id, filename, track_type="random", 
                        volume=1.0, play_chance=0.5, min_duration=30, 
                        max_duration=120, fade_in_time=3.0, fade_out_time=3.0):
            """
            Adds track to the ambient system
            
            track_id: unique track identifier
            filename: path to audio file
            track_type: "mandatory" (always plays) or "random" (plays occasionally)
            volume: base track volume (0.0-1.0)
            play_chance: playback chance for random tracks (0.0-1.0)
            min_duration: minimum playback duration (seconds)
            max_duration: maximum playback duration (seconds)
            fade_in_time: fade in duration (seconds)
            fade_out_time: fade out duration (seconds)
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
            Sets main menu theme
            
            filename: path to main theme file
            duration: playback duration (seconds)
            volume: volume level (0.0-1.0)
            fade_in_time: fade in duration
            fade_out_time: fade out duration
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
                # If no main theme, start ambient directly
                self.start_ambient()
        
        def _play_main_theme(self):
            """Plays main menu theme"""
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
            
            # Start monitor for main theme
            self._main_theme_monitor()

            # Start fade out and ambient switch timers
            fade_out_time = self.main_theme['fade_out_time']
            fade_start_time = max(0, theme_duration - fade_out_time)
            
            self._create_timer(fade_start_time, self._fade_out_main_theme).start()
            self._create_timer(theme_duration, self._start_ambient_after_theme).start()
        
        def _main_theme_monitor(self):
            """Checks if main theme is playing and restarts if needed."""
            if not self.main_theme.get('is_playing', False):
                return

            # Check if something is playing on main theme channel
            if not renpy.music.get_playing(channel="main_theme"):
                # If nothing is playing but should be, restart theme
                renpy.music.play(self.main_theme['filename'], 
                                channel="main_theme", 
                                fadein=0,  # No fadein on restart
                                if_changed=False)
                renpy.music.set_volume(self.main_theme['volume'], channel="main_theme")

            # Schedule next check
            self._create_timer(1.0, self._main_theme_monitor).start()
        
        def _fade_out_main_theme(self):
            """Smoothly fades out main theme"""
            if self.main_theme['is_playing']:
                renpy.music.stop(channel="main_theme", 
                                fadeout=self.main_theme['fade_out_time'])
        
        def _start_ambient_after_theme(self):
            """Starts ambient after main theme"""
            self.main_theme['is_playing'] = False
            self._cancel_all_timers() # Clear timers before starting ambient
            self.start_ambient()

        def start_ambient(self, delay_after_main_theme=0):
            """
            Starts ambient system
            delay_after_main_theme: delay in seconds after main theme
            """
            if delay_after_main_theme > 0:
                self._create_timer(delay_after_main_theme, self._start_ambient_delayed).start()
            else:
                self._start_ambient_delayed()
        
        def _start_ambient_delayed(self):
            """Internal method for delayed ambient start"""
            self.is_active = True
            self.ambient_start_time = time.time()  # Mark ambient start time
            self.last_update_time = self.ambient_start_time
            self._assign_channels()
            self._start_mandatory_tracks()
            self._start_all_random_tracks()  # Start all random tracks at minimum volume
            self._schedule_random_volume_changes()  # Schedule volume changes
            self._start_volume_manager()
        
        def stop_ambient(self, fade_out=True):
            """
            Stops ambient system
            fade_out: smooth fade out on stop
            """
            self.is_active = False
            self.ambient_start_time = 0  # Reset start time
            self.last_update_time = 0
            
            # Reset pseudo-random system
            self.global_cooldown_end_time = 0
            self.elevated_tracks_count = 0
            self.current_wave_limit = 0
            self.wave_elevation_count = 0
            self.tracks_fading_out.clear()
            
            # Stop main theme if playing
            self.main_theme['is_playing'] = False
            
            # Cancel all active timers
            self._cancel_all_timers()
            
            if fade_out:
                renpy.music.stop(channel="main_theme", 
                                fadeout=self.main_theme['fade_out_time'])
            else:
                renpy.music.stop(channel="main_theme")
            
            if fade_out:
                # Smoothly reduce volume of all tracks with individual timings
                max_fade_time = 0
                for track_id, track_data in self.tracks.items():
                    if track_data['is_playing']:
                        track_data['target_volume'] = 0.0
                        max_fade_time = max(max_fade_time, track_data['fade_out_time'])
                
                # Use maximum fade time + small buffer
                if max_fade_time > 0:
                    self._create_timer(max_fade_time + 0.5, self._stop_all_tracks).start()
                else:
                    self._stop_all_tracks()
            else:
                self._stop_all_tracks()
        
        def _assign_channels(self):
            """Assigns channels to tracks"""
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
        
        def _start_all_random_tracks(self):
            """Starts all random tracks at minimum volume"""
            for track_id, track_data in self.tracks.items():
                if track_data['type'] == 'random':
                    self._play_track_at_minimum_volume(track_id)
        
        def _schedule_random_volume_changes(self):
            """Starts initial cycles for random tracks with startup cooldown"""
            if not self.is_active:
                return
                
            # Set startup cooldown for smooth mandatory track introduction
            initial_delay = self.initial_cooldown_time + random.uniform(5, 15)
                
            for track_id, track_data in self.tracks.items():
                if (track_data['type'] == 'random' 
                    and track_data['is_playing']
                    and not track_data.get('is_elevated', False)):
                    # Start individual cycle for each track
                    # with startup cooldown + random offset to avoid simultaneous triggers
                    track_delay = initial_delay + random.uniform(0, 10)
                    timer = self._create_timer(track_delay, self._make_elevation_callback(track_id))
                    timer.start()
        
        def _play_track(self, track_id):
            """Plays specific track (for mandatory tracks)"""
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
            
        def _play_track_at_minimum_volume(self, track_id):
            """Plays random track at minimum volume"""
            if not self.is_active:
                return
                
            track_data = self.tracks[track_id]
            channel = track_data['channel']
            
            if not channel:
                return
            
            # Start track with minimum volume
            renpy.music.play(track_data['filename'], channel=channel, 
                            loop=True, if_changed=False)
            renpy.music.set_volume(self.minimum_volume, channel=channel)
            
            # Set parameters for minimum volume
            track_data['is_playing'] = True
            track_data['current_volume'] = self.minimum_volume
            track_data['target_volume'] = self.minimum_volume  # Currently minimum
            track_data['play_start_time'] = time.time()
            track_data['is_elevated'] = False  # Flag to track "elevation"
        
        def _elevate_track_volume(self, track_id):
            """Elevates random track volume to normal level"""
            if track_id not in self.tracks or not self.is_active:
                return
                
            track_data = self.tracks[track_id]
            if track_data['type'] != 'random' or not track_data['is_playing']:
                return
                
            # If track is already elevated, don't elevate again
            if track_data.get('is_elevated', False):
                return
                
            # Elevate to normal volume
            track_data['target_volume'] = track_data['volume'] * self.base_volume
            track_data['is_elevated'] = True
            track_data['elevation_start_time'] = time.time()  # Mark elevation time
            
            # Increment elevated track counters
            self.elevated_tracks_count += 1
            self.wave_elevation_count += 1
            
            # Immediately schedule lowering after random time within limits
            duration = random.uniform(track_data['min_duration'], track_data['max_duration'])
            
            # Cancel previous timer if exists
            if track_id in self.track_timers:
                self.track_timers[track_id].cancel()
                
            # Schedule lowering
            self.track_timers[track_id] = self._create_timer(
                duration, self._make_lower_callback(track_id))
            self.track_timers[track_id].start()
        
        def _lower_track_volume(self, track_id):
            """Lowers random track volume to minimum level"""
            if track_id not in self.tracks or not self.is_active:
                return
                
            track_data = self.tracks[track_id]
            if track_data['type'] != 'random' or not track_data['is_playing']:
                return
                
            # Lower to minimum volume
            track_data['target_volume'] = self.minimum_volume
            track_data['is_elevated'] = False
            
            # Add to list of fading out tracks
            self.tracks_fading_out.add(track_id)
            
            # Decrease elevated tracks counter
            self.elevated_tracks_count = max(0, self.elevated_tracks_count - 1)
            
            # Clear timer for this track
            if track_id in self.track_timers:
                del self.track_timers[track_id]
        
        def _check_wave_completion(self):
            """Checks wave completion and starts cooldown if needed"""
            # Check only if no active elevated tracks and no fading tracks
            if self.elevated_tracks_count == 0 and len(self.tracks_fading_out) == 0:
                # Reset wave counters
                self.current_wave_limit = 0
                self.wave_elevation_count = 0
                
                # Set global cooldown - rest before next wave
                cooldown_duration = random.uniform(self.minimum_rest_time, self.maximum_rest_time)
                self.global_cooldown_end_time = time.time() + cooldown_duration
                
                # Schedule new elevation attempts for all non-elevated random tracks AFTER cooldown
                next_attempt_delay = cooldown_duration + random.uniform(5, 20)
                for track_id, track_data in self.tracks.items():
                    if (track_data['type'] == 'random' 
                        and track_data['is_playing'] 
                        and not track_data.get('is_elevated', False)):
                        # Each track gets base delay + small random offset
                        track_delay = next_attempt_delay + random.uniform(0, 10)
                        # Fix closure problem - use generator function
                        timer = self._create_timer(track_delay, self._make_elevation_callback(track_id))
                        timer.start()
        
        def _make_elevation_callback(self, track_id):
            """Creates callback for track elevation attempt (fixes closure problem)"""
            return lambda: self._attempt_track_elevation(track_id)
        
        def _make_lower_callback(self, track_id):
            """Creates callback for track lowering (fixes closure problem)"""
            return lambda: self._lower_track_volume(track_id)
        
        def _attempt_track_elevation(self, track_id):
            """Attempts to elevate track volume considering chance and cooldown"""
            if track_id not in self.tracks or not self.is_active:
                return
                
            track_data = self.tracks[track_id]
            if track_data['type'] != 'random' or not track_data['is_playing']:
                return
                
            # If track is already elevated, skip
            if track_data.get('is_elevated', False):
                return
                
            # Check global cooldown - can we elevate now
            current_time = time.time()
            if current_time < self.global_cooldown_end_time:
                # Cooldown hasn't passed - exit, new attempts will be after cooldown
                return
                
            # If no active wave or wave limit exhausted - start new wave
            if self.current_wave_limit == 0 or self.wave_elevation_count >= self.current_wave_limit:
                # If there are active elevated tracks, exit - wait for wave completion
                if self.elevated_tracks_count > 0:
                    return
                else:
                    # Can start new wave
                    self._start_new_wave()
                    # If still no available wave after start, return
                    if self.current_wave_limit == 0:
                        return
                
            # If we reached here, it means we have active wave with slots available
            # Check elevation chance
            chance_roll = random.random()
            if chance_roll < track_data['play_chance']:
                self._elevate_track_volume(track_id)
            else:
                # If chance failed, only schedule retry if wave is not full yet
                if self.wave_elevation_count < self.current_wave_limit:
                    retry_delay = random.uniform(5, 15)  # Quick retry in same wave
                    timer = self._create_timer(retry_delay, self._make_elevation_callback(track_id))
                    timer.start()
        
        def _stop_track(self, track_id):
            """Stops mandatory track or lowers volume of random track"""
            if track_id in self.tracks:
                track_data = self.tracks[track_id]
                
                if track_data['type'] == 'mandatory':
                    # For mandatory tracks - full stop
                    track_data['target_volume'] = 0.0
                    fade_out_time = track_data['fade_out_time']
                    self._create_timer(fade_out_time, 
                                    lambda: self._force_stop_track(track_id)).start()
                elif track_data['type'] == 'random':
                    # For random tracks - only lower to minimum
                    self._lower_track_volume(track_id)
        
        def _force_stop_track(self, track_id):
            """Forcibly stops only mandatory tracks"""
            if track_id in self.tracks:
                track_data = self.tracks[track_id]
                
                # Stop only mandatory tracks
                if track_data['type'] == 'mandatory':
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
                track_data = self.tracks[track_id]
                if track_data['channel']:
                    renpy.music.stop(channel=track_data['channel'])
                track_data['is_playing'] = False
                track_data['current_volume'] = 0.0
                track_data['target_volume'] = 0.0
                if hasattr(track_data, 'is_elevated'):
                    track_data['is_elevated'] = False
                    
            # Clear all timers
            for timer in self.track_timers.values():
                try:
                    if timer.is_alive():
                        timer.cancel()
                except:
                    pass
            self.track_timers.clear()
        
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
                    
                    # For minimum_volume (0.0) requires precision, for others - 0.01
                    tolerance = 0.001 if target == self.minimum_volume else 0.01
                    if abs(current - target) > tolerance:
                        # Determine change speed based on fade time
                        if target > current:
                            # Fade in - use fade_in_time
                            fade_time = track_data['fade_in_time']
                        else:
                            # Fade out - use fade_out_time
                            fade_time = track_data['fade_out_time']
                        
                        # Calculate change step for smooth transition
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
                    
                    # Final check for minimum_volume - ensure track reached 0.0
                    elif target == self.minimum_volume and current > self.minimum_volume:
                        track_data['current_volume'] = self.minimum_volume
                        renpy.music.set_volume(self.minimum_volume, channel=track_data['channel'])
                        
                        # Remove track from fading list if it's there
                        if track_id in self.tracks_fading_out:
                            self.tracks_fading_out.discard(track_id)
                            # Check wave completion
                            self._check_wave_completion()
                    
                    # Also check if track is already at minimum_volume and in fading list
                    elif target == self.minimum_volume and abs(current - self.minimum_volume) <= 0.001:
                        if track_id in self.tracks_fading_out:
                            self.tracks_fading_out.discard(track_id)
                            # Check wave completion
                            self._check_wave_completion()
            
            # Schedule next update
            self._create_timer(0.1, self._volume_update_loop).start()
        
        def set_base_volume(self, volume):
            """Sets system base volume"""
            self.base_volume = max(0.0, min(1.0, volume))
            
            # Update target volume for all tracks
            for track_data in self.tracks.values():
                if track_data['is_playing']:
                    if track_data['type'] == 'mandatory':
                        # Mandatory tracks always at normal volume
                        track_data['target_volume'] = track_data['volume'] * self.base_volume
                    elif track_data['type'] == 'random':
                        # Random tracks: at normal volume only if elevated
                        if track_data.get('is_elevated', False):
                            track_data['target_volume'] = track_data['volume'] * self.base_volume
                        else:
                            track_data['target_volume'] = self.minimum_volume
        
        def get_ambient_runtime(self):
            """Returns ambient runtime in seconds"""
            if not self.is_active or self.ambient_start_time == 0:
                return 0
            return time.time() - self.ambient_start_time
        
        def get_formatted_runtime(self):
            """Returns formatted ambient runtime"""
            runtime = self.get_ambient_runtime()
            hours = int(runtime // 3600)
            minutes = int((runtime % 3600) // 60)
            seconds = int(runtime % 60)
            
            if hours > 0:
                return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
            else:
                return "{:02d}:{:02d}".format(minutes, seconds)
        
        def get_track_runtime(self, track_id):
            """Returns specific track runtime in seconds"""
            if track_id not in self.tracks:
                return 0
            track_data = self.tracks[track_id]
            if not track_data['is_playing'] or track_data['play_start_time'] == 0:
                return 0
            return time.time() - track_data['play_start_time']
        
        def get_track_elevation_time(self, track_id):
            """Returns how long track has been playing at elevated volume"""
            if track_id not in self.tracks:
                return 0
            track_data = self.tracks[track_id]
            if not track_data.get('is_elevated', False) or not track_data.get('elevation_start_time', 0):
                return 0
            return time.time() - track_data['elevation_start_time']
        
        def _start_new_wave(self):
            """Starts new elevation wave, determining its size"""
            # Determine track count for new wave (only non-elevated random tracks)
            available_random_tracks = sum(1 for t in self.tracks.values() 
                                        if t['type'] == 'random' 
                                        and t['is_playing'] 
                                        and not t.get('is_elevated', False))
            
            # Limit cannot be greater than available tracks
            max_possible = min(self.max_tracks_per_wave, available_random_tracks)
            
            if max_possible > 0:
                self.current_wave_limit = random.randint(
                    min(self.min_tracks_per_wave, max_possible), 
                    max_possible
                )
                self.wave_elevation_count = 0
                self.global_cooldown_end_time = 0  # Remove cooldown for new wave
            else:
                # If no available tracks, set minimal values but don't reset cooldown
                self.current_wave_limit = 0
                self.wave_elevation_count = 0
                # Keep existing cooldown to prevent constant attempts
        
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
            """Creates timer with tracking for proper cleanup"""
            timer = threading.Timer(delay, callback)
            timer.daemon = True  # Doesn't block program exit
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

# Variable to store volume setting
default ambient_volume_setting = 0.7

# Label to start ambient in main menu
label start_main_menu_ambient:
    # Check if system is not already running
    if ambient.is_active or ambient.main_theme['is_playing']:
        return
    
    # Set up tracks only once
    if not hasattr(store, 'ambient_configured'):
        call setup_ambient
        call setup_main_theme
        $ ambient_configured = True
    
    # Synchronize volume setting
    $ ambient.set_base_volume(ambient_volume_setting)
    
    # Start sequence: main theme → ambient
    $ ambient.start_with_main_theme()
    return
