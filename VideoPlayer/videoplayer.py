# This code is inspired from https://github.com/Akascape/tkVideoPlayer

import av
import argparse
import pyaudio
import time
import threading
import logging
from typing import Tuple, Dict

import dearcygui as dcg
from iipv.viewer import ViewerImage

from collections import deque
import heapq
import traceback

logging.getLogger('libav').setLevel(logging.CRITICAL)  # removes warning: deprecated pixel format used


class VideoDecoder:
    def __init__(self, path, prefetch_duration=2.):
        self.video_queue = []
        self.audio_queue = []
        self.stream_container = av.open(path, "r")
        self.has_audio = len(self.stream_container.streams.audio) > 0
        if self.has_audio:
            self.stream = self.stream_container.decode(video=0, audio=0)
        else:
            self.stream = self.stream_container.decode(video=0)
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
        self.decoding_thread.start()

    def decode_frame(self):
        frame = next(self.stream)
        if isinstance(frame, av.VideoFrame):
            time = frame.time
            array = frame.to_ndarray(format=self.target_video_format)
            with self.mutex:
                heapq.heappush(self.video_queue, (time, self.frame_uuid))
                self.video_frames[self.frame_uuid] = array
                if len(self.video_queue) == 1:
                    self.has_video_frames.set()
                self.frame_uuid += 1
                self.max_timestamp_decoded = max(self.max_timestamp_decoded, time)
        elif isinstance(frame, av.AudioFrame):
            time = frame.time
            array = frame.to_ndarray()
            with self.mutex:
                heapq.heappush(self.audio_queue, (time, self.frame_uuid))
                self.audio_frames[self.frame_uuid] = array
                if len(self.audio_frames) == 1:
                    self.has_audio_frames.set()
                self.frame_uuid += 1
                self.max_timestamp_decoded = max(self.max_timestamp_decoded, time)

    def background_decode(self):
      try:
        while True:
            while True:
                # Wait if needed
                with self.mutex:
                    delta = self.max_timestamp_decoded - self.max_timestamp_consumed
                if delta < self.prefetch_duration:
                    break
                self.consumed_data.wait()
            self.decode_frame()
      except Exception:
        print(traceback.format_exc())

    def consume_video(self):
        self.has_video_frames.wait(timeout=0.5)
        if not(self.has_video_frames.is_set()):
            raise KeyError("No more video")
        with self.mutex:
            (timestamp, uuid) = heapq.heappop(self.video_queue)
            image = self.video_frames.pop(uuid)
            if len(self.video_queue) == 0:
                self.has_video_frames.clear()
            self.max_timestamp_consumed = max(self.max_timestamp_consumed, timestamp)
            self.consumed_data.set()
        return (timestamp, image)

    def consume_audio(self):
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

class VideoPlayer(dcg.Window):
    def __init__(self, context, path, **kwargs):
        super().__init__(context, **kwargs)
        self.decoder = VideoDecoder(path)
        self.no_scroll_with_mouse = True
        self.no_scrollbar = True
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
        plot.fit_button = 4 # we don't want that, so set to an useless button
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
        self.presenting_thread.start()
        self.audio_thread.start()

    def on_resize(self):
        self.image_viewer.update_image()

    def run_audio(self):
        last_t_sound = 0
        if not(self.decoder.has_audio):
            return
        audio_stream = self.decoder.stream_container.streams.audio[0]
        samplerate = audio_stream.rate # this will work as the video clock
        channels = audio_stream.channels
        audio_player = pyaudio.PyAudio()
        audio_device = audio_player.open(format=pyaudio.paFloat32,
                                         channels=channels,
                                         rate=samplerate,
                                         output=True)
        while True:
            (last_t_sound, sound) = self.decoder.consume_audio()
            audio_data = sound.astype('float32')
            interleaved_data = audio_data.T.flatten().tobytes()
            audio_device.write(interleaved_data)
            # If we pause sending frames, underrun will occur,
            # thus we would need to resample to fit
            # exactly to time.time(). Instead sync the video
            # to the sound
            self.current_time = last_t_sound

    def run_video(self):
        last_t_video = 0
        n_frames_shown = 0
        n_frames_decoded = 0
        presentation_time_avg = 0
        while True:
            if not(self.decoder.has_audio):
                self.current_time = (time.time()-self.start_time)
            current_time = self.current_time - presentation_time_avg

            if current_time < last_t_video:
                time.sleep(0.0001)
                continue
            new_frame = False
            while current_time >= last_t_video:
                (last_t_video, image) = self.decoder.consume_video()
                n_frames_decoded += 1
                new_frame = True
            if new_frame:
                t_current = time.time()
                self.image_viewer.display(image)
                presentation_time_avg = 0.99 * presentation_time_avg + 0.01 * (time.time()-t_current)
                n_frames_shown += 1
            #print(n_frames_shown, n_frames_decoded, presentation_time_avg)

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

    VideoPlayer(C, args.infile, primary=True, no_bring_to_front_on_focus=True)
    while C.running:
        # can_skip_presenting: no GPU re-rendering on input that has no impact (such as mouse motion) 
        C.viewport.render_frame(can_skip_presenting=True)

if __name__ == '__main__':
    main()
