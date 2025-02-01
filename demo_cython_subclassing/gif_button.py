import dearcygui as dcg
from PIL import Image
import numpy as np

"""
This file contains a Python implementation of a GifButton,
which is a button that displays an animated GIF.

See dynamic_button.pyx for the Cython equivalent.

Note that in this case, the Python implementation is preferred
because:
- Better portability (see limitations about Cython subclassing)
- Simplicity of implementation
- Better performance (using DrawStream enables to directly
    use battery life optimizations in DearCyGui). Basically
    we don't redraw before the gif needs to change its content.
"""

class DrawGif(dcg.utils.DrawStream):
    def __init__(self, context, gif_path, pmin=(0., 0.), pmax=(1., 1.), **kwargs):
        super().__init__(context, **kwargs)
        total_duration = 0
        
        # Load the GIF and extract frames
        gif = Image.open(gif_path)
        try:
            while True:
                # Convert frame to RGBA
                frame = np.array(gif.convert('RGBA'))
                # Create texture from frame
                texture = dcg.Texture(context)
                texture.set_value(frame)
                
                # Get frame duration in seconds
                frame_duration = gif.info['duration'] / 1000.0
                total_duration += frame_duration
                
                # Create DrawImage for this frame and add to stream
                image = dcg.DrawImage(context,
                                    texture=texture,
                                    pmin=pmin,
                                    pmax=pmax,
                                    parent=self)
                self.push(image, total_duration)
                
                # Move to next frame
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass

        # Set stream to loop
        self.time_modulus = total_duration

class GifButton(dcg.DrawInWindow):
    def __init__(self, context, gif_path, width=16, height=16, **kwargs):
        super().__init__(context, button=True, width=width, height=height, **kwargs)
        self.relative = True
        self.button = True
        self.frame = True
        DrawGif(context, gif_path, parent=self)

class Gif(dcg.DrawInWindow):
    def __init__(self, context, gif_path, width=16, height=16, **kwargs):
        super().__init__(context, button=True, width=width, height=height, **kwargs)
        self.relative = True
        DrawGif(context, gif_path, parent=self)