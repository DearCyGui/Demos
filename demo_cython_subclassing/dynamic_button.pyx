from PIL import Image
import numpy as np
from libcpp.vector cimport vector
from cpython.time cimport time
cimport dearcygui as dcg

cdef class GifButton(dcg.ImageButton):
    cdef list _frames        # List of texture objects for each frame
    cdef vector[double] _frame_delays  # List of delays between frames
    cdef double _start_time  # Start time of animation
    cdef double _total_duration
    cdef int _current_frame  # Current frame index
    
    def __init__(self, context, str gif_path, **kwargs):
        super().__init__(context, **kwargs)
        self._frames = []
        self._current_frame = 0
        self._total_duration = 0
        self._start_time = time()
        cdef dcg.Texture texture
        cdef double frame_duration
        
        # Load the GIF and extract frames
        gif = Image.open(gif_path)
        try:
            while True:
                # Convert frame to RGBA
                frame = np.array(gif.convert('RGBA'))/255.
                # Create texture from frame
                texture = dcg.Texture(context)
                texture.set_content(frame)
                self._frames.append(texture)
                # Store frame delay (convert to seconds)
                frame_duration = gif.info['duration'] / 1000.0
                self._frame_delays.push_back(frame_duration)
                self._total_duration += frame_duration
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass

        # Set initial texture
        if self._frames:
            self._texture = self._frames[0]

    cdef bint draw_item(self) noexcept nogil:
        # Calculate elapsed time
        cdef double current_time = time()
        cdef double elapsed = current_time - self._start_time
        elapsed = elapsed % self._total_duration  # Loop animation

        if <int>self._frame_delays.size() == 0:
            return False
        
        # Calculate current frame based on elapsed time and frame delays
        cdef double total_delay = 0
        cdef int i = 0
        for i in range(<int>self._frame_delays.size()):
            total_delay += self._frame_delays[i]
            if total_delay > elapsed:
                break

        i = min(i, <int>self._frame_delays.size()-1)
        if i != self._current_frame:
            # Note: it is possible to do without the gil
            # using a vector of PyObjects
            with gil:  # Need GIL for Python list access
                self._texture = self._frames[i]
        self._current_frame = i
        
        return dcg.ImageButton.draw_item(self)
