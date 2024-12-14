import av
import argparse
import time
import threading
import logging
from typing import Tuple, Dict
import warnings

import dearcygui as dcg
from iipv.viewer import ViewerImage

from collections import deque
import heapq
import traceback
import numpy as np
import sdl3

logging.getLogger('libav').setLevel(logging.CRITICAL)  # removes warning: deprecated pixel format used


class VideoDecoder:
    """
    Video decoder with buffering based on PyAV.
    """
    def __init__(self, path: str, prefetch_duration: float = 2.) -> None:
        self.video_queue = []
        self.audio_queue = []
        
        # Try to initialize hardware decoding
        self.hw_device = None
        self.stream_container = av.open(path, 'r')
        self.video_stream = self.stream_container.streams.video[0]
        codec_name = self.video_stream.codec_context.name
        
        # Try hardware decoders in order of preference
        hw_codecs = [
            # NVIDIA
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
        """
        try:
            if self.hw_codec_ctx:
                # Hardware decoding path
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
                ts = int(timestamp / av.time_base)
                self.stream_container.seek(ts)
                if self.hw_codec_ctx:
                    self.hw_codec_ctx.flush_buffers()  # Clear hardware decoder buffers
                self.error = None
        except Exception as e:
            self.error = f"Seek error: {str(e)}"
            print(traceback.format_exc())


class ButtonWithTooltip(dcg.Button):
    """
    Button with a tooltip.
    """
    def __init(self, context : dcg.Context, *args, **kwargs):
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
                                            target=self):
                dcg.Text(self.context, value=self._tooltip)

class SliderWithTooltip(dcg.Slider):
    """
    Slider with a tooltip.
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
                                            target=self):
                dcg.Text(self.context, value=self._tooltip)

class VideoPlayer(dcg.Window):
    """
    Video player with playback controls.
    
    This class basically implements the interface
    around the VideoDecoder class to display video,
    and uses iipv.viewer.ViewerImage to display the
    video frames.
    """
    def __init__(self, context : dcg.Context, path: str, **kwargs):
        super().__init__(context, **kwargs)
        self.decoder = VideoDecoder(path)
        self.no_scroll_with_mouse = True
        self.no_scrollbar = True
        # Add playback controls
        self.paused = False
        self.loop = False
        self.controls = dcg.HorizontalLayout(context, parent=self, horizontal=True)
        self.volume = 1.0
        self.audio_device = None  # Store audio device reference
        self.audio_paused_time = 0  # Store time when audio was paused
        self._running = True  # Add stop flag
        self.audio_mutex = threading.Lock()  # Add mutex for audio queue access
        self.audio_time = 0.0  # Track audio timing
        self.sync_threshold = 0.01  # 10ms threshold for sync
        with self.controls:
            self.play_button = \
                ButtonWithTooltip(context,
                                  label="Play/Pause", 
                                  callback=self.toggle_pause,
                                  tooltip="Space: Play/Pause")
            self.step_back = \
                ButtonWithTooltip(context,
                                  arrow=True,
                                  direction=dcg.ButtonDirection.LEFT,
                                  callback=lambda: self.step_frame(-1),
                                  tooltip="Previous frame (when paused)")
            self.step_forward = \
                ButtonWithTooltip(context,
                                  arrow=True,
                                  direction=dcg.ButtonDirection.RIGHT, 
                                  callback=lambda: self.step_frame(1),
                                  tooltip="Next frame (when paused)")
            self.progress = \
                SliderWithTooltip(context,
                                  width=200,
                                  format="float",
                                  callback=lambda s : self.seek(s.value),
                                  min_value=0., 
                                  max_value=self.decoder.duration,
                                  tooltip="Seek position")
            self.volume_slider = \
                SliderWithTooltip(context,
                                  label="Volume",
                                  format='float',
                                  value=1.0,
                                  min_value=0.0, 
                                  max_value=1.0, 
                                  width=100,
                                  callback=self.set_volume)
            self.loop_button = \
                ButtonWithTooltip(context,
                                  label="Loop", 
                                  callback=self.toggle_loop,
                                  tooltip="Toggle video loop")
            self.fullscreen_button = \
                ButtonWithTooltip(context,
                                  label="Full", 
                                  callback=self.toggle_fullscreen,
                                  tooltip="Toggle fullscreen (F11)")
            self.metadata_text = \
                dcg.Text(context, 
                         value=(f"{self.decoder.width}x{self.decoder.height} "
                                f"[{self.decoder.codec}]"))
            self.info_text = \
                dcg.Text(context, 
                         value=f"FPS: {self.decoder.frame_rate}")
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
        # Set a handler to update the images when the plot min/max change
        plot.handlers += [
            dcg.AxesResizeHandler(context, callback=self.on_resize)
        ]
        # Remove empty borders
        plot.theme = dcg.ThemeStyleImPlot(self.context, PlotPadding=(0, 0))
        # Image viewer
        self.image_viewer = ViewerImage(context, parent=plot)
        self.plot = plot

        self.presenting_thread = threading.Thread(target=self.run_video, args=(), daemon=True)
        self.audio_thread = threading.Thread(target=self.run_audio, args=(), daemon=True)


        self.time = 0.
        self.current_time = 0.
        self.start_time = time.time()

        # Add keyboard handlers
        self.handlers += [
            dcg.KeyPressHandler(context, key=dcg.Key.SPACE, callback=self.handle_keyboard),
            dcg.KeyPressHandler(context, key=dcg.Key.LEFTARROW, callback=self.handle_keyboard),
            dcg.KeyPressHandler(context, key=dcg.Key.RIGHTARROW, callback=self.handle_keyboard),
            dcg.KeyPressHandler(context, key=dcg.Key.F11, callback=self.handle_keyboard),
        ]

        # Initialize SDL audio once
        sdl3.SDL_Init(sdl3.SDL_INIT_AUDIO)
            
        self.audio_mutex = threading.Lock()
        self.audio_queue = deque(maxlen=256)  # Increased buffer size
        self.audio_time = 0.0
        self.sync_threshold = 0.02  # Increased to 20ms for more tolerance
        self.min_audio_buffer = 8192  # Minimum audio buffer size
        self.max_audio_buffer = 32768  # Maximum audio buffer size (~0.2s at 48kHz stereo)
        self.audio_device = None
        
        if self.decoder.has_audio:
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
                    self.start_time = time.time() - self.current_time

    def toggle_fullscreen(self):
        self.context.viewport.fullscreen = not self.context.viewport.fullscreen

    def toggle_loop(self):
        self.loop = not self.loop

    def step_frame(self, direction: int):
        if not self.paused:
            return
        try:
            if direction > 0:
                timestamp, image = self.decoder.consume_video()
                self.image_viewer.display(image)
                self.current_time = timestamp
            else:
                # Approximate previous frame position
                self.seek(max(0, self.current_time - 1/self.decoder.frame_rate))
        except KeyError:
            if self.loop:
                self.seek(0)

    def update_status(self):
        if self.decoder.error:
            self.status_text.value = f"Error: {self.decoder.error}"
        else:
            self.status_text.value = f"Time: {self.current_time:.2f}s"
        self.progress.value = self.current_time
        self.info_text.value = (f"FPS: {self.decoder.frame_rate:.1f} | "
                               f"Time: {self.current_time:.1f}/{self.decoder.duration:.1f}s")

    def cleanup(self):
        """Safe cleanup of all resources"""
        self._running = False  # Signal threads to stop
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
        # Finally stop the decoder
        self.decoder.stop()

    def on_resize(self):
        self.image_viewer.update_image()

    def handle_keyboard(self, sender, key):
        if key == dcg.Key.SPACE:
            self.toggle_pause()
        elif key == dcg.Key.LEFTARROW:
            if self.paused:
                self.step_frame(-1)
            else:
                self.seek(max(0, self.current_time - 5))
        elif key == dcg.Key.RIGHTARROW:
            if self.paused:
                self.step_frame(1)
            else:
                self.seek(min(self.decoder.duration, self.current_time + 5))
        elif key == dcg.Key.F11:
            self.toggle_fullscreen()

    def seek(self, value):
        if value < 0:
            value = 0
        elif value > self.decoder.duration:
            value = self.decoder.duration
            
        with self.audio_mutex:
            self.decoder.seek(value)
            self.current_time = value
            self.audio_time = value
            self.start_time = time.time() - value
            if self.audio_stream:
                sdl3.SDL_ClearAudioStream(self.audio_stream)

    def set_volume(self, sender):
        self.volume = sender.value

    def run_audio(self):
        if not self.decoder.has_audio:
            return
            
        try:
            while self._running:
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                try:
                    queued = sdl3.SDL_GetAudioStreamQueued(self.audio_stream)
                    # Keep larger buffer to handle GIL delays
                    if queued < self.min_audio_buffer:
                        # Fill buffer up to max size
                        while queued < self.max_audio_buffer and self._running and not self.paused:
                            (last_t_sound, sound) = self.decoder.consume_audio()
                            self._queue_audio(sound)
                            queued = sdl3.SDL_GetAudioStreamQueued(self.audio_stream)
                        with self.audio_mutex:
                            self.current_time = self.audio_time
                    else:
                        time.sleep(0.001)
                            
                except KeyError:
                    if self.decoder.error and not self.decoder.error.startswith("End of stream"):
                        break
                    time.sleep(0.1)
                    
        except Exception as e:
            self.decoder.error = f"Audio error: {str(e)}"

    def _queue_audio(self, audio_data):
        """Queue audio data to SDL device"""
        if not self.audio_device:
            return
            
        with self.audio_mutex:
            # Calculate audio duration
            samples = audio_data.shape[0] if len(audio_data.shape) == 1 else audio_data.shape[1]
            audio_duration = samples / self.decoder.stream_container.streams.audio[0].rate
            
            # Convert to float32 and apply volume
            if len(audio_data.shape) > 1 and audio_data.shape[0] == 2:
                audio_data = np.ascontiguousarray(audio_data.transpose((1, 0)))
            data = (audio_data.astype('float32') * self.volume).tobytes()
            
            # Update audio timing
            if sdl3.SDL_PutAudioStreamData(self.audio_stream, data, len(data)):
                self.audio_time += audio_duration

    def run_video(self):
        last_t_video = 0
        n_frames_shown = 0
        n_frames_decoded = 0
        last_fps_update = time.time()
        actual_fps = 0
        buffer_compensation = 0.1  # 100ms compensation for audio buffering
        
        while self._running:
            current_time = time.time()
            # Update FPS counter every second
            if current_time - last_fps_update >= 1.0:
                actual_fps = n_frames_shown / (current_time - last_fps_update)
                n_frames_shown = 0
                last_fps_update = current_time
                
            if self.paused:
                time.sleep(0.1)
                continue
                
            if self.decoder.error and not self.decoder.error.startswith("End of stream"):
                self.update_status()
                break

            try:
                if not self.decoder.has_audio:
                    self.current_time = (time.time()-self.start_time)
                
                with self.audio_mutex:
                    # Add buffer compensation to account for audio buffering
                    target_time = self.current_time + buffer_compensation

                if abs(target_time - last_t_video) > self.sync_threshold:
                    if target_time < last_t_video:
                        time.sleep(0.001)
                        continue
                    
                    while target_time >= last_t_video and not self.paused:
                        (last_t_video, image) = self.decoder.consume_video()
                        if sdl3.SDL_GetAudioStreamQueued(self.audio_stream) < self.min_audio_buffer:
                            time.sleep(0.001) # Give audio thread a chance
                        n_frames_decoded += 1
                        if abs(target_time - last_t_video) > 2 * self.sync_threshold:
                            # Skip frames if too far behind
                            continue
                        self.image_viewer.display(image)
                        n_frames_shown += 1
                else:
                    time.sleep(0.001)  # Give other threads a chance
                    
            except KeyError:
                # Handle end of stream or seeking
                if self.loop and self.decoder.error and self.decoder.error.startswith("End of stream"):
                    self.seek(0)
                time.sleep(0.1)
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
    # wait_for_input: Do not refresh until a change is detected (C.viewport.wake() to help)
    C.viewport.initialize(vsync=True,
                          wait_for_input=True,
                          title="Integrated Image Processing Viewer")
    # primary: use the whole window area
    # no_bring_to_front_on_focus: enables to have windows on top to
    # add your custom UI, and not have them hidden when clicking on the image.

    player = VideoPlayer(C, args.infile, primary=True, no_bring_to_front_on_focus=True)
    try:
        while C.running:
            # can_skip_presenting: no GPU re-rendering on input that has no impact (such as mouse motion) 
            C.viewport.render_frame(can_skip_presenting=True)
    finally:
        player.cleanup()

if __name__ == '__main__':
    main()
