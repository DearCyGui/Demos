# Demo video player implementation using DearCyGui
# Note that right now (2024) the playback will not
# replay at full rate (some frames are skipped).
# This is likely due to the GIL and thread scheduling
# issues that should hopefully be resolved with nogil.
import av  # PyAV library for video decoding
import argparse  # For parsing command line arguments
import time
import threading  # For running video/audio processing in background threads
import logging

import dearcygui as dcg
# Here we reuse iipv viewer code to manage frame upload
# and frame skipping. And alternative could be to implement
# a texture pool and upload in advance the video frames.
from iipv.viewer import ViewerImageInPlot, AtomicCounter

import heapq  # For priority queue used in frame ordering
import traceback
import numpy as np
from typing import Tuple
import sdl3  # SDL library for audio playback

# Reduce logging noise from the AV library
logging.getLogger('libav').setLevel(logging.CRITICAL)


class VideoDecoder:
    """
    Video decoder with buffering based on PyAV.

    Decoding a video requires reading in advance
    the video content as the content of the current
    frame can depend of the future frames for some
    codecs. In additions, video and audio information
    can be stored in blocks. Thus this class intends
    to decode in advance a subsection of the video.
    
    Frame Buffer Management:
       - Maintains separate queues for video and audio
       - Uses priority queues to ensure correct frame ordering
       - Prefetches frames ahead of playback times
       
    Synchronization:
       - Maintains precise timestamps for audio and video
       - Uses threading.Event for thread synchronization
       - Implements producer-consumer pattern for frame handling
    """
    def __init__(self, path: str, prefetch_duration: float = 2.) -> None:
        # Queues to store decoded video and audio frames
        self.video_queue = []  # Stores (timestamp, frame_id) pairs
        self.audio_queue = []
        
        # Try to initialize hardware decoding for better performance
        # Note this requires the python packages of av/ffmpeg
        # need to be compiled with GPU acceleration support.
        self.hw_device = None
        # Open the video file
        self.stream_container = av.open(path, 'r')
        self.video_stream = self.stream_container.streams.video[0]
        codec_name = self.video_stream.codec_context.name

        # List of hardware decoders to try
        # Each entry is (codec name, human-readable description)
        hw_codecs = [
            # NVIDIA GPU acceleration
            (f'{codec_name}_cuvid', 'NVIDIA CUDA'),
            ('h264_cuvid', 'NVIDIA CUDA H264'),
            ('hevc_cuvid', 'NVIDIA CUDA HEVC'),
            ('av1_cuvid', 'NVIDIA CUDA AV1'),
            # VAAPI (Linux)
            (f'{codec_name}_vaapi', 'VAAPI'),
            ('h264_vaapi', 'VAAPI H264'),
            ('hevc_vaapi', 'VAAPI HEVC'),
            ('av1_vaapi', 'VAAPI AV1'),
            # VideoToolbox (macOS)
            (f'{codec_name}_videotoolbox', 'VideoToolbox'),
            ('h264_videotoolbox', 'VideoToolbox H264'),
            ('hevc_videotoolbox', 'VideoToolbox HEVC'),
            # D3D11VA (Windows)
            (f'{codec_name}_d3d11va', 'D3D11VA'),
            ('h264_d3d11va', 'D3D11VA H264'),
            ('hevc_d3d11va', 'D3D11VA HEVC'),
            # QSV (Intel)
            (f'{codec_name}_qsv', 'Intel QuickSync'),
            ('h264_qsv', 'Intel QuickSync H264'),
            ('hevc_qsv', 'Intel QuickSync HEVC'),
            # AMF (AMD)
            (f'{codec_name}_amf', 'AMD AMF'),
            ('h264_amf', 'AMD AMF H264'),
            ('hevc_amf', 'AMD AMF HEVC'),
        ]
        
        # Try each hardware decoder
        self.hw_codec_ctx = None
        for codec_name, desc in hw_codecs:
            try:
                codec = av.Codec(codec_name, 'r')
                if codec:
                    self.hw_codec_ctx = codec.create()
                    try:
                        # Try to decode one frame to see if it actually works
                        for packet in self.stream_container.demux(self.video_stream):
                            if packet.stream == self.video_stream:
                                frame = next(self.hw_codec_ctx.decode(packet))
                                if frame:
                                    print(f"Using hardware decoder: {desc}")
                                    break
                    except Exception as e:
                        self.hw_codec_ctx = None
                        print(f"Failed to decode with {desc}: {e}")
                    if self.hw_codec_ctx:
                        break
            except Exception as e:
                print(f"Failed to initialize {desc}: {e}")
        if self.hw_codec_ctx is not None:
            self.stream = self.stream_container.demux(self.video_stream)
        else:
            self.stream = self.stream_container.decode(video=0, audio=0)
                
        self.has_audio = len(self.stream_container.streams.audio) > 0
        if self.has_audio:
            # Audio stream uses default decoder
            self.audio_stream = self.stream_container.streams.audio[0]
            
        self.prefetch_duration = prefetch_duration
        self.target_video_format = av.VideoFormat('rgb24')
        self.frame_uuid = 0
        self.video_frames = {}
        self.audio_frames = {}
        self.mutex = threading.Lock()
        self.has_video_frames = threading.Event()
        self.has_audio_frames = threading.Event()
        self.consumed_data = threading.Event()
        self.decoding_thread = threading.Thread(target=self.background_decode, args=(), daemon=True)
        self.max_timestamp_consumed = 0.
        self.max_timestamp_decoded = 0.
        self._running = True
        self.error = None
        self.duration = float(self.stream_container.duration / av.time_base)
        self.frame_rate = self.stream_container.streams.video[0].average_rate
        self.width = self.stream_container.streams.video[0].width
        self.height = self.stream_container.streams.video[0].height
        self.codec = self.stream_container.streams.video[0].codec_context.codec.name
        self.decoding_thread.start()

    def stop(self) -> None:
        self._running = False
        self.consumed_data.set()  # Wake up decoder thread
        self.decoding_thread.join()
        self.stream_container.close()
        if self.hw_device:
            self.hw_device.close()

    def decode_frame(self) -> None:
        """
        Decode the next frame from the video stream.
        
        This method handles both hardware and software decoding paths:
        - Hardware path: Uses specialized decoders (e.g., NVDEC, QuickSync)
        - Software path: Uses standard CPU-based decoding
        
        The decoded frames are processed and added to the appropriate queues
        (video_queue or audio_queue) for later consumption.
        """
        try:
            if self.hw_codec_ctx:
                # Hardware decoding path
                with self.mutex:
                    packet = next(self.stream)
                if packet.stream == self.video_stream:
                    for frame in self.hw_codec_ctx.decode(packet):
                        if frame:
                            self._process_video_frame(frame)
                            return
                elif self.has_audio and packet.stream == self.audio_stream:
                    for frame in packet.decode():
                        if frame:
                            self._process_audio_frame(frame)
                            return
            else:
                # Software decoding path
                with self.mutex:
                    frame = next(self.stream)
                if isinstance(frame, av.VideoFrame):
                    self._process_video_frame(frame)
                elif isinstance(frame, av.AudioFrame):
                    self._process_audio_frame(frame)
                    
        except Exception as e:
            print(f"Decode error: {e}")
            raise

    def _process_video_frame(self, frame):
        """
        Retrieve the numpy array from a video frame and store it in the queue.
        """
        time = frame.time
        try:
            # Always convert to RGB24 for display
            frame = frame.reformat(format='rgb24')
            array = frame.to_ndarray()
            
            with self.mutex:
                heapq.heappush(self.video_queue, (time, self.frame_uuid))
                self.video_frames[self.frame_uuid] = array
                if len(self.video_queue) == 1:
                    self.has_video_frames.set()
                self.frame_uuid += 1
                self.max_timestamp_decoded = max(self.max_timestamp_decoded, time)
        except Exception as e:
            print(f"Video frame processing error: {e}")

    def _process_audio_frame(self, frame):
        """
        Retrieve the numpy array from an audio frame and store it in the queue.
        """
        time = frame.time
        array = frame.to_ndarray()
        with self.mutex:
            heapq.heappush(self.audio_queue, (time, self.frame_uuid))
            self.audio_frames[self.frame_uuid] = array
            if len(self.audio_frames) == 1:
                self.has_audio_frames.set()
            self.frame_uuid += 1
            self.max_timestamp_decoded = max(self.max_timestamp_decoded, time)

    def background_decode(self) -> None:
        """
        Background thread for continuous frame decoding.
        
        This method:
        1. Monitors buffer fullness using prefetch_duration
        2. Decodes new frames when buffer is getting low
        3. Uses threading.Event to coordinate with playback thread
        4. Handles end-of-stream and error conditions
        
        The prefetch system ensures smooth playback by maintaining
        a buffer of decoded frames.
        """
        try:
            while self._running:
                while True:
                    # Wait if the background thread is too far ahead of the main thread
                    with self.mutex:
                        delta = self.max_timestamp_decoded - self.max_timestamp_consumed
                    if delta < self.prefetch_duration:
                        break
                    self.consumed_data.wait()
                self.decode_frame()
        except StopIteration:
            self.error = "End of stream"
        except Exception as e:
            self.error = str(e)
            print(traceback.format_exc())

    def consume_video(self) -> Tuple[float, np.ndarray]:
        """
        Return the next video frame from the queue.
        """
        self.has_video_frames.wait(timeout=0.5)
        if not(self.has_video_frames.is_set()):
            raise KeyError("No more video")
        with self.mutex:
            if not self.video_queue:
                raise KeyError("No more video")
            timestamp, uuid = heapq.heappop(self.video_queue)
            image = self.video_frames.pop(uuid)
            if len(self.video_queue) == 0:
                self.has_video_frames.clear()
            self.max_timestamp_consumed = max(self.max_timestamp_consumed, timestamp)
            self.consumed_data.set()
        return (timestamp, image)

    def consume_audio(self) -> Tuple[float, np.ndarray]:
        """
        Return the next audio frame from the queue.
        """
        self.has_audio_frames.wait(timeout=0.5)
        if not(self.has_audio_frames.is_set()):
            raise KeyError("No more audio")
        with self.mutex:
            if not self.audio_queue:
                raise KeyError("No more audio")
            (timestamp, uuid) = heapq.heappop(self.audio_queue)
            audio = self.audio_frames.pop(uuid)
            if len(self.audio_queue) == 0:
                self.has_audio_frames.clear()
            self.max_timestamp_consumed = max(self.max_timestamp_consumed, timestamp)
            self.consumed_data.set()
        return (timestamp, audio)

    def seek(self, timestamp: float) -> None:
        """
        Seek to a specific timestamp in the video.
        """
        try:
            with self.mutex:
                self.video_queue.clear()
                self.audio_queue.clear()
                self.video_frames.clear()
                self.audio_frames.clear()
                self.has_video_frames.clear()
                self.has_audio_frames.clear()
                self.max_timestamp_consumed = timestamp
                self.max_timestamp_decoded = timestamp
                # Convert timestamp to AV's timebase
                ts = int(timestamp * av.time_base)
                self.stream_container.seek(ts)
                if self.hw_codec_ctx:
                    self.hw_codec_ctx.flush_buffers()  # Clear hardware decoder buffers
                self.error = None
        except Exception as e:
            self.error = f"Seek error: {str(e)}"
            print(traceback.format_exc())


class ButtonWithTooltip(dcg.Button):
    """
    This class is DearCyGui Button which automatically
    attaches a tooltip when hovered.
    
    Usage:
        button = ButtonWithTooltip(context, 
                                 label="Play",
                                 tooltip="Click to play/pause")
    """
    def __init__(self, context : dcg.Context, *args, **kwargs):
        self._tooltip = None
        super().__init__(context, *args, **kwargs)
        self.handlers += [
            dcg.GotHoverHandler(context, callback=self.show_tooltip)
        ]

    # Defining the property getters/setters means
    # one can pass tooltip="..." during item creation.
    # For DearCyGui items, the base __init__ converts
    # unused kwargs arguments to properties.
    @property
    def tooltip(self):
        return self._tooltip

    @tooltip.setter
    def tooltip(self, value):
        self._tooltip = value

    def show_tooltip(self):
        # To display a tooltip when hovered, two options are
        # available:
        # 1. During item creation, attach a dcg.Tooltip
        #    instance to the same parent as the target
        # 2. When hovered dynamically attach a dcg.Tooltip
        #    and delete it when done.
        # Here the second option is demonstrated.
        # In our case the first option would be good
        # as well, but if creating the content of the tooltip
        # is not cheap, the second option might be preferred.
        if self._tooltip:
            with dcg.utils.TemporaryTooltip(self.context,
                                            target=self,
                                            parent=self.parent):
                dcg.Text(self.context, value=self._tooltip)

class SliderWithTooltip(dcg.Slider):
    """
    This class is DearCyGui Slider which automatically
    attaches a tooltip when hovered.
    Used for both the progress bar and volume control.
    
    Usage:
        slider = SliderWithTooltip(context,
                                 min_value=0,
                                 max_value=100,
                                 tooltip="Drag to adjust")
    """
    def __init__(self, context : dcg.Context, *args, **kwargs):
        self._tooltip = None
        super().__init__(context, *args, **kwargs)
        self.handlers += [
            dcg.GotHoverHandler(context, callback=self.show_tooltip)
        ]

    @property
    def tooltip(self):
        return self._tooltip

    @tooltip.setter
    def tooltip(self, value):
        self._tooltip = value

    def show_tooltip(self):
        if self._tooltip:
            with dcg.utils.TemporaryTooltip(self.context,
                                            target=self,
                                            parent=self.parent):
                dcg.Text(self.context, value=self._tooltip)

class VideoPlayer(dcg.Window):
    """
    Video player with playback controls.
    
    UI Controls:
    1. Playback Controls:
       - Play/Pause button: Toggle playback (Space key)
       - Progress slider: Seek through video
       - Volume slider: Adjust audio volume
       - Loop button: Toggle video looping
       - Fullscreen button: Toggle fullscreen mode (F11 key)
       
    2. Status Display:
       - Resolution and codec information
       - Current/total time
       - Target and actual FPS
       - Error messages if any
       
    3. Keyboard Shortcuts:
       - Space: Play/Pause
       - Left Arrow: Seek backward 60 seconds
       - Right Arrow: Seek forward 60 seconds
       - F11: Toggle fullscreen
       
    4. Window Features:
       - Borderless design
       - Auto-fitting video display
       - Tooltip help system
    """
    def __init__(self, context : dcg.Context, path: str, **kwargs):
        super().__init__(context, **kwargs)
        self.decoder = VideoDecoder(path)
        # dcg.Window attributes with impact on rendering
        self.no_scroll_with_mouse = True
        self.no_scrollbar = True
        # Add playback controls
        self.paused = False
        self.loop = False
        self.volume = 1.0
        self._running = True  # Add stop flag
        # Here we store in instance variables each item created
        # Note this is not needed, as attaching them will already
        # have them stored in the children attribute.
        self.controls = dcg.HorizontalLayout(context, parent=self, horizontal=True)
        with self.controls:
            # Play/Pause Button
            self.play_button = \
                ButtonWithTooltip(context,
                                  label="Play/Pause", 
                                  callback=self.toggle_pause,
                                  tooltip="Space: Play/Pause")
            
            # Video Progress Slider
            # Shows current position and allows seeking
            self.progress = \
                SliderWithTooltip(context,
                                  width=200,
                                  format="float",  # Shows time in seconds
                                  callback=lambda s : self.seek(s.value),
                                  min_value=0., 
                                  max_value=self.decoder.duration,
                                  tooltip="Seek position")
            
            # Volume Control Slider
            self.volume_slider = \
                SliderWithTooltip(context,
                                  label="Volume",
                                  format='float',
                                  value=1.0,  # Default full volume
                                  min_value=0.0,  # Mute
                                  max_value=1.0,  # Maximum volume
                                  width=100,
                                  tooltip="Volume factor"
                                  callback=self.set_volume)
            
            # Loop Toggle Button
            self.loop_button = \
                ButtonWithTooltip(context,
                                  label="Loop", 
                                  callback=self.toggle_loop,
                                  tooltip="Loop back when the video ends")
            
            # Fullscreen Toggle Button
            self.fullscreen_button = \
                ButtonWithTooltip(context,
                                  label="Full", 
                                  callback=self.toggle_fullscreen,
                                  tooltip="Toggle fullscreen (F11)")
            
            # Video Information Display
            self.metadata_text = \
                dcg.Text(context,
                         value=(f"{self.decoder.width}x{self.decoder.height} "
                                f"[{self.decoder.codec}]"))
            
            # Performance Information Display
            self.info_text = \
                dcg.Text(context, 
                         value=f"FPS: {self.decoder.frame_rate}")
            
            # Status/Error Display
            self.status_text = dcg.Text(context, value="")

        # Make the window content use the whole size
        self.theme = \
            dcg.ThemeStyleImGui(context,
                                WindowPadding=(0, 0),
                                WindowBorderSize=0)
        plot = dcg.Plot(context, parent=self, width=-1, height=-1)
        # Disable all plot features we don't want
        plot.X1.no_label = True
        plot.X1.no_gridlines = True
        plot.X1.no_tick_marks = True
        plot.X1.no_tick_labels = True
        plot.X1.no_menus = True
        plot.X1.no_side_switch = True
        plot.X1.no_highlight = True
        plot.Y1.no_label = True
        plot.Y1.no_gridlines = True
        plot.Y1.no_tick_marks = True
        plot.Y1.no_tick_labels = True
        plot.Y1.no_menus = True
        plot.Y1.no_side_switch = True
        plot.Y1.no_highlight = True
        # invert Y
        plot.Y1.invert = True
        plot.X1.auto_fit = True
        plot.Y1.auto_fit = True
        plot.no_title = True
        plot.no_mouse_pos = True
        plot.equal_aspects = True # We do really want that for images
        plot.no_frame = True
        plot.no_legend = True
        # Remove empty borders
        plot.theme = dcg.ThemeStyleImPlot(self.context, PlotPadding=(0, 0))
        # Image viewer
        self.image_viewer = ViewerImageInPlot(context, parent=plot)
        self.plot = plot

        self.presenting_thread = threading.Thread(target=self.run_video, args=(), daemon=True)
        self.audio_thread = threading.Thread(target=self.run_audio, args=(), daemon=True)


        self.time = 0.
        self.current_time = 0.
        self.start_time = time.monotonic()

        # Add keyboard handlers
        # Register Keyboard Event Handlers
        self.handlers += [
            # Play/Pause toggle
            dcg.KeyPressHandler(context, 
                                key=dcg.Key.SPACE, 
                                callback=self.handle_keyboard),
            # Seek backward 60 seconds
            dcg.KeyPressHandler(context, 
                                key=dcg.Key.LEFTARROW, 
                                callback=self.handle_keyboard),
            # Seek forward 60 seconds
            dcg.KeyPressHandler(context, 
                                key=dcg.Key.RIGHTARROW, 
                                callback=self.handle_keyboard),
            # Toggle fullscreen
            dcg.KeyPressHandler(context, 
                              key=dcg.Key.F11, 
                              callback=self.handle_keyboard),
        ]
            
        self.audio_mutex = threading.Lock()
        self.audio_time = 0.0 # Last timestamp of scheduled audio.
        self.sync_threshold = 0.02  # 20ms
        self.video_delay_to_screen = 0.01  # Estimated (updated every frame) presentation delay to screen
        self.min_audio_buffer = 32768   # Minimum audio buffer size (~0.2s at 48kHz stereo)
        self.max_audio_buffer = 65536   # Maximum audio buffer size (~0.4s at 48kHz stereo) 
        self.audio_device = None
        
        if self.decoder.has_audio:
            # Initialize SDL audio
            sdl3.SDL_Init(sdl3.SDL_INIT_AUDIO)

            audio_format = self.decoder.stream_container.streams.audio[0]
            self.audio_device = sdl3.SDL_OpenAudioDevice(
                sdl3.SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK,  # default device
                sdl3.SDL_AudioSpec(
                    freq=audio_format.rate,
                    format=sdl3.SDL_AUDIO_F32,
                    channels=audio_format.channels,
                )
            )
            
            if not self.audio_device:
                raise RuntimeError(f"Failed to open audio device: {sdl3.SDL_GetError().decode()}")

            self.audio_stream = sdl3.SDL_CreateAudioStream(
                sdl3.SDL_AudioSpec(
                    format=sdl3.SDL_AudioFormat(sdl3.SDL_AUDIO_F32),
                    channels=audio_format.channels,
                    freq=audio_format.rate),
                sdl3.SDL_AudioSpec(
                    format=sdl3.SDL_AudioFormat(sdl3.SDL_AUDIO_F32),
                    channels=audio_format.channels,
                    freq=audio_format.rate)
            )

            if not self.audio_stream:
                raise RuntimeError(f"Failed to create audio stream: {sdl3.SDL_GetError().decode()}")

            if not sdl3.SDL_BindAudioStream(self.audio_device, self.audio_stream):
                raise RuntimeError(f"Failed to bind audio stream: {sdl3.SDL_GetError().decode()}")

            sdl3.SDL_SetAudioStreamFormat(
                self.audio_stream,
                sdl3.SDL_AudioSpec(
                    format=sdl3.SDL_AudioFormat(sdl3.SDL_AUDIO_F32),
                    channels=audio_format.channels,
                    freq=audio_format.rate),
                sdl3.SDL_AudioSpec(
                    format=sdl3.SDL_AudioFormat(sdl3.SDL_AUDIO_F32),
                    channels=audio_format.channels,
                    freq=audio_format.rate)
            )
                
            # Start playing
            sdl3.SDL_ResumeAudioDevice(self.audio_device)

        # Start video and audio consumer threads
        self.presenting_thread.start()
        self.audio_thread.start()

    def toggle_pause(self):
        with self.audio_mutex:
            self.paused = not self.paused
            if self.audio_device:
                if self.paused:
                    sdl3.SDL_PauseAudioDevice(self.audio_device)
                else:
                    sdl3.SDL_ClearAudioStream(self.audio_stream)
                    sdl3.SDL_ResumeAudioDevice(self.audio_device)
            self.start_time = time.monotonic() - self.current_time

    def toggle_fullscreen(self):
        self.context.viewport.fullscreen = not self.context.viewport.fullscreen

    def toggle_loop(self):
        self.loop = not self.loop

    def update_status(self):
        """
        Updates the status display with current playback information.
        
        Shows either:
        - Current playback time
        - Error message if something goes wrong
        Also updates the progress slider position.
        """
        if self.decoder.error:
            self.status_text.value = f"Error: {self.decoder.error}"
        else:
            self.status_text.value = f"Time: {self.current_time:.2f}s"
        self.progress.value = self.current_time

    def cleanup(self):
        """
        Performs clean shutdown of the video player.
        
        This method ensures all resources are properly released:
        1. Stops background threads
        2. Closes audio device
        3. Shuts down SDL audio
        4. Stops the video decoder
        
        This should be called when closing the application.
        """
        # Stop the decoder
        self.decoder.stop()

        # Signal threads to stop
        self._running = False
        # Wait they stop
        if self.presenting_thread.is_alive():
            self.presenting_thread.join()
        if self.audio_thread.is_alive():
            self.audio_thread.join()
            
        # Clean up audio resources
        if self.audio_device:
            try:
                sdl3.SDL_CloseAudioDevice(self.audio_device)
                self.audio_device = None
            except:
                pass
            sdl3.SDL_Quit()

    def handle_keyboard(self, sender : dcg.KeyPressHandler):
        """
        Handles keyboard input for video control.
        
        Key Mappings:
        - Space: Toggle play/pause
        - Left Arrow: Seek backward 60 seconds (when playing)
        - Right Arrow: Seek forward 60 seconds (when playing)
        - F11: Toggle fullscreen mode
        
        Parameters:
            sender: Event sender (here can only be KeyPressHandler)
        """
        key = sender.key
        if key == dcg.Key.SPACE:
            self.toggle_pause()
        elif key == dcg.Key.LEFTARROW:
            if not(self.paused):
                self.seek(self.audio_time - 60)
        elif key == dcg.Key.RIGHTARROW:
            if not(self.paused):
                self.seek(self.audio_time + 60)
        elif key == dcg.Key.F11:
            self.toggle_fullscreen()

    def seek(self, value):
        """
        Seeks to a specific position in the video.
        
        Parameters:
            value (float): Target timestamp in seconds
            
        This method:
        1. Clamps the seek position to valid range
        2. Resets decoder state and clears buffers
        3. Updates timing information
        4. Clears audio buffers to prevent audio glitches
        """
        if value < 0:
            value = 0
        elif value > self.decoder.duration:
            value = self.decoder.duration

        with self.audio_mutex:
            self.decoder.seek(value)
            self.current_time = value
            self.audio_time = value
            self.start_time = time.monotonic() - value
            if self.audio_stream:
                sdl3.SDL_ClearAudioStream(self.audio_stream)

    def set_volume(self, sender):
        self.volume = sender.value

    def run_audio(self):
        """
        Audio playback management thread.
        
        Buffer Management:
        1. Maintains optimal buffer size:
           - min_audio_buffer: Minimum to prevent underruns (~0.2s)
           - max_audio_buffer: Maximum to limit latency (~0.4s)
           
        2. Dynamic Buffer Control:
           - Monitors buffer fullness
           - Adjusts decode rate to maintain target buffer size
           - Prevents buffer overflow/underflow
           
        3. Timing Control:
           - Updates audio_time for video sync
           - Handles pause/seek operations
           - Manages audio device state
        """
        if not self.decoder.has_audio:
            return
            
        try:
            while self._running:
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                try:
                    # Get current buffer size in bytes
                    queued = sdl3.SDL_GetAudioStreamQueued(self.audio_stream)
                    
                    # If buffer is getting low, queue more audio
                    if queued < self.min_audio_buffer:
                        (timestamp, sound) = self.decoder.consume_audio()
                        self._queue_audio(sound, timestamp)
                    elif queued > self.max_audio_buffer:
                        # Buffer is full enough, wait a bit
                        time.sleep(0.005)
                    else:
                        # Buffer is in good range, the small
                        # wait is to give other threads a chance to run.
                        time.sleep(0.001)
                            
                except KeyError:
                    if self.decoder.error and not self.decoder.error.startswith("End of stream"):
                        break
                    time.sleep(0.1)
                    
        except Exception as e:
            self.decoder.error = f"Audio error: {str(e)}"
            raise(e)

    def _queue_audio(self, audio_data, timestamp):
        """
        Queues audio data to the SDL audio device with volume control.
        
        Parameters:
            audio_data (np.ndarray): Raw audio samples
            timestamp (float): Timestamp of this audio chunk
            
        The audio data is converted to float32 format and the volume
        is applied before sending to SDL. This method also updates
        the audio timing used for synchronization.
        """
        if not self.audio_device:
            return
            
        with self.audio_mutex:
            # Convert to float32 and apply volume
            if len(audio_data.shape) > 1 and audio_data.shape[0] == 2:
                audio_data = np.ascontiguousarray(audio_data.transpose((1, 0)))
            data = (audio_data.astype('float32') * self.volume).tobytes()
            
            # Update audio timing
            if sdl3.SDL_PutAudioStreamData(self.audio_stream, data, len(data)):
                self.audio_time = timestamp

    def inc_frame_shown(self, future, counter : AtomicCounter=None, target_time=None):
        """Increment frame counter when a frame is shown"""
        if future.cancelled():
            return
        # Here iipv's viewer decreases the counter
        # when the content has been prepared for display
        # and is submitted to imgui.
        # We retrieve the timestamp when this happens.
        timestamp_zero = counter.timestamp_zero()
        if timestamp_zero == 0:
            # Skipped frame (because of a more recent frame),
            # counter was never decreased.
            return
        self.n_frames_shown += 1
        # time when it was actually displayed on the screen.
        # The 1/60 is a rough estimation (because 60 fps), 
        # but getting the true value requires OS specific extensions
        # not available to us right now. A 'real' video player would use
        # these. The 0.95 is to compute a running average.
        self.video_delay_to_screen = 0.95 * self.video_delay_to_screen + \
            0.05 * (counter.timestamp_zero() + 1/60. - target_time)

    def run_video(self):
        """
        Main video playback loop that runs in a separate thread.
        
        Frame Timing & Synchronization:
        1. Calculates target_video_time based on:
           - Current audio playback position
           - Estimated display latency (video_delay_to_screen)
           - Frame interval (1/fps)

        2. Frame Dropping Logic:
           - Compares frame timestamps with target time
           - Drops frames if playback falls behind
           - Limits maximum consecutive drops to prevent stalls
           
        3. Performance Monitoring:
           - Tracks actual vs target FPS
           - Updates UI with playback statistics
           - Monitors sync accuracy
        """
        last_frame_time = 0
        frame_interval = 1.0 / self.decoder.frame_rate
        self.n_frames_shown = 0
        # Note monotonic is used through this test as it cannot
        # go back in time (time.time() can be a bit random
        # if the computer tries to sync time with various
        # servers).
        last_fps_update = time.monotonic()
        actual_fps = 0
        skipped = 0
        
        while self._running:
            if self.paused:
                time.sleep(0.1)
                continue

            try:
                # Get current playback position
                if self.decoder.has_audio:
                    # audio: sync to currently running audio.
                    with self.audio_mutex:
                        queued = sdl3.SDL_GetAudioStreamQueued(self.audio_stream)
                        self.current_time = self.audio_time - queued / (self.decoder.stream_container.streams.audio[0].rate * 4)
                else:
                    # No audio: sync to elapsed time since start
                    self.current_time = time.monotonic() - self.start_time
                # current_time is the time of the data that is currently being played.
                # video_delay_to_screen is the delay for a scheduled frame to hit the screen
                # target_video_time: the timestamp that must be scheduled right now
                # such that the video data hits the screen at the desired time.
                target_video_time = self.current_time - self.video_delay_to_screen
                next_video_time = last_frame_time + frame_interval

                # Check if it's time to show next frame
                next_frame_due = target_video_time >= (next_video_time - self.sync_threshold)
                if next_frame_due or skipped > 20:
                    timestamp, image = self.decoder.consume_video()
                    
                    # Skip frames if we're significantly behind
                    while timestamp < (target_video_time - frame_interval) and skipped < 20:
                        try:
                            timestamp, image = self.decoder.consume_video()
                            skipped += 1
                        except KeyError:
                            break
                    skipped = 0
                    last_frame_time = timestamp
                    counter = AtomicCounter(1)
                    submission_time = time.monotonic()
                    future = self.image_viewer.display(image,
                                                       counter=counter)
                    def update_timing(future, counter=counter, submission_time=submission_time):
                        self.inc_frame_shown(future, counter, submission_time)
                    future.add_done_callback(update_timing)

                    # Update FPS counter
                    now = time.monotonic()
                    if now - last_fps_update >= 1.0:
                        actual_fps = self.n_frames_shown / (now - last_fps_update)
                        self.n_frames_shown = 0
                        last_fps_update = now
                else:
                    skipped += 1
                    time.sleep(frame_interval / 4.)

            except KeyError:
                if self.loop and self.decoder.error and self.decoder.error.startswith("End of stream"):
                    self.seek(0)
                time.sleep(frame_interval / 4.)
                continue
                
            self.update_status()
            self.info_text.value = (f"Target FPS: {self.decoder.frame_rate:.1f} | "
                                  f"Actual FPS: {actual_fps:.1f} | "
                                  f"Time: {self.current_time:.1f}/{self.decoder.duration:.1f}s")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help=('Input file'))
    args = parser.parse_args()

    C = dcg.Context()
    # vsync: limit to screen refresh rate and have no tearing
    # wait_for_input: Do not refresh until a change is detected (C.viewport.wake())
    C.viewport.initialize(vsync=True,
                          wait_for_input=True,
                          title="Integrated Image Processing Viewer")
    # primary: use the whole window area
    # no_bring_to_front_on_focus: enables to have windows on top to
    # add the custom UI, and not have them hidden when clicking on the image.

    player = VideoPlayer(C, args.infile, primary=True, no_bring_to_front_on_focus=True)
    try:
        while C.running:
            # can_skip_presenting: no GPU re-rendering on input that has no impact (such as mouse motion) 
            C.viewport.render_frame(can_skip_presenting=True)
    finally:
        player.cleanup()

if __name__ == '__main__':
    main()
