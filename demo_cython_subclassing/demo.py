import dearcygui as dcg
# For the purpose of this demo
import pyximport
import numpy as np
# Using pyximport to compile Cython code on the fly
# This is not recommended for production code, but is useful for demos
# One advantage is that it copes with the fact that the Cython code
# needs to be recompiled whenever dearcygui changes.
script_args = ["--cython-cplus"]
setup_args = {
    "include_dirs":np.get_include(),
    "script_args": script_args,
}
pyximport.install(setup_args=setup_args, language_level="3")

import time
import gc
from dynamic_button import *
from heavy import *

from gif_button import GifButton as GifButtonPython

C = dcg.Context()


def benchmark_circles(C: dcg.Context):
    gc.collect()
    gc.disable()
    
    results = {}
    num_points_list = [8, 32, 128]
    
    for num_points in num_points_list:
        # Benchmark CircleLinesMonolithic
        t1 = time.time()
        for i in range(30):
            CircleLinesMonolithic(C, num_points=num_points, radius=100)
        t2 = time.time()
        mono_time = (t2-t1) * 1000 / 30  # Average ms per creation
        
        # Benchmark CircleLinesList
        t1 = time.time()
        for i in range(30):
            CircleLinesList(C, num_points=num_points, radius=100) 
        t2 = time.time()
        list_time = (t2-t1) * 1000 / 30  # Average ms per creation
        
        results[num_points] = (mono_time, list_time)
    
    gc.enable()
    return results

def create_demo_window(C : dcg.Context):
    # Run benchmark first to get results
    benchmark_results = benchmark_circles(C)

    with dcg.Window(C, primary=True, label="Demo window") as window:
        with dcg.VerticalLayout(C, x="parent.x1 + theme.indent_spacing.x"):
            # Fun animated button to demonstrate the use of
            # cython subclassing with custom draw() override for dynamic content
            dcg.Text(C, value="This button is made with a custom draw() method in Cython")
            GifButton(C, "demo.gif", label="Hello Word", width=200, height=200)
            dcg.Separator(C)
            dcg.Text(C, value="This button is made with Python subclassing")
            GifButtonPython(C, "demo.gif", label="Hello Word (Python)", width=200, height=200)
            dcg.Separator(C)
            
            # Visual comparison section
            dcg.Text(C, value="This demo shows two different approaches to build complex objects:")
            dcg.Text(C, value="1. MonolithicCircle: A single item, but with a custom draw override")
            dcg.Text(C, value="2. CircleList: A separate DrawLine item for each connection")
            dcg.Text(C, value="Below are visual examples comparing both implementations with different point counts.")
            dcg.Text(C, value="For each example we show:")
            dcg.Text(C, value="- Creation time: How long it takes to instantiate the object")
            dcg.Text(C, value="- Render time: Real-time measurement of rendering duration (updated each frame)")
            
            for num_points in [8, 32, 128]:
                with dcg.ChildWindow(C, auto_resize_y=True, label=f"num_points={num_points}"):
                    dcg.Text(C, value=f"Test with {num_points} points ({num_points * (num_points-1) // 2} lines total)")
                    with dcg.VerticalLayout(C, no_newline=True):
                        dcg.Text(C, value="Monolithic Implementation", color=(200,200,255))
                        dcg.Text(C, value="Single item overriding draw() in Cython")
                        dcg.Text(C, value=f"Time to create: {benchmark_results[num_points][0]:.2f} ms")
                        b1_text = dcg.TextValue(C, print_format="Time to render: %.3f ms")
                        with BenchmarkDrawInWindow(C, width=180, height=130) as b1:
                            CircleLinesMonolithic(C, num_points=num_points, radius=50,
                                            center=(105, 65), color=(255,0,0,255))
                        b1_text.shareable_value = b1.shareable_value
                    with dcg.VerticalLayout(C, no_newline=True):
                        dcg.Text(C, value="Item list Implementation", color=(200,200,255))
                        dcg.Text(C, value="One item, many children:")
                        dcg.Text(C, value=f"Time to create: {benchmark_results[num_points][1]:.2f} ms")
                        b2_text = dcg.TextValue(C, print_format="Time to render: %.3f ms")
                        with BenchmarkDrawInWindow(C, width=180, height=130) as b2:
                            CircleLinesList(C, num_points=num_points, radius=50,
                                            center=(105, 65), color=(255,0,0,255))
                        b2_text.shareable_value = b2.shareable_value

            dcg.Text(C, value="Moral of the story: rendering times are similar, " \
                    "but the monolithic approach is faster to create.")
            dcg.Text(C, value="However one big downside to Cython subclassing is that it "\
                    "requires to recompile everytime dearcygui changes.")
            dcg.Text(C, value="Prefer normal Python subclassing and reserve Cython subclassing "\
                    "for:")
            dcg.Text(C, value="- When you would need a HUGE amount of items to render what you want")
            dcg.Text(C, value="- When you need highly dynamic content")

    


def launch_demo():
    C = dcg.Context()
    # vsync: limit to screen refresh rate and have no tearing
    # wait_for_input: Do not refresh until a change is detected (C.viewport.wake() to help)
    C.viewport.initialize(vsync=True,
                          wait_for_input=False,
                          title="Cython subclassing demo")
    # primary: use the whole window area
    # no_bring_to_front_on_focus: enables to have windows on top to
    # add your custom UI, and not have them hidden when clicking on the image.

    # Declarative way of creating items
    create_demo_window(C)

    while C.running:
        C.viewport.render_frame()

if __name__ == '__main__':
    launch_demo()
