import asyncio
import colorsys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import dearcygui as dcg
from dearcygui.utils.asyncio_helpers import AsyncPoolExecutor, run_viewport_loop, AsyncThreadPoolExecutor
import gc
import inspect
import math
import numpy as np
import random
import sys
import threading
from time import monotonic, sleep
from typing import Callable, List, Generator, Tuple, Any

sys.setswitchinterval(1e-9)

# Benchmark tracking
@dataclass
class BenchmarkInfo:
    """Information about a benchmark function."""
    name: str
    short_description: str
    long_description: str
    category: str
    rendering_thread: bool
    code: str
    run: Callable

benchmarks_list: List[BenchmarkInfo] = []

def benchmark(category: str, rendering_thread: bool = False):
    """
    Decorator to register a function as a benchmark.
    
    Args:
        category: The category to which the benchmark belongs
        rendering_thread: Whether the benchmark requires the rendering thread
    """
    def decorator(func):
        docstring = inspect.getdoc(func)
        if docstring:
            lines = docstring.split('\n', 1)
            short_description = lines[0].strip()
            long_description = lines[1].strip() if len(lines) > 1 else ""
        else:
            short_description = func.__name__
            long_description = ""
        
        # Get the source code without docstring and indentation
        source = inspect.getsource(func)
        source_lines = source.splitlines()
        # Find function definition line
        func_def_index = next((i for i, line in enumerate(source_lines) 
                             if line.strip().startswith('async def ')), 0)
        
        # Extract body, skip docstring and remove indentation
        body_lines = source_lines[func_def_index + 1:]
        if not body_lines:
            code = ""
        else:
            # Find initial indentation level
            indent_level = next((len(line) - len(line.lstrip()) 
                              for line in body_lines if line.strip()), 4)
            
            # Skip docstring if present
            first_non_empty = next((line.strip() for line in body_lines if line.strip()), "")
            if first_non_empty.startswith('"""') or first_non_empty.startswith("'''"):
                # Determine quote type
                quote_type = '"""' if first_non_empty.startswith('"""') else "'''"
                
                # Find the end of docstring
                docstring_end = -1
                
                # Check if docstring ends on same line
                if first_non_empty.endswith(quote_type) and len(first_non_empty) > 3:
                    docstring_end = next((i for i, line in enumerate(body_lines) 
                                    if line.strip() == first_non_empty), 0)
                else:
                    # Find end quote
                    for i, line in enumerate(body_lines):
                        if i > 0 and quote_type in line:
                            docstring_end = i
                            break
                
                if docstring_end != -1:
                    # Skip all docstring lines including the closing quotes
                    body_lines = body_lines[docstring_end + 1:]
            
            # Remove indentation
            code = "\n".join(
                line[indent_level:] if line.strip() else line 
                for line in body_lines
            )
        
        info = BenchmarkInfo(
            name=func.__name__,
            short_description=short_description,
            long_description=long_description,
            category=category,
            rendering_thread=rendering_thread,
            code=code,
            run=func
        )
        
        benchmarks_list.append(info)
        return func
    
    return decorator

# All tests assume starting in a fresh Context,
# with initialized viewport and no children.

@benchmark(category="Rendering", rendering_thread=True)
async def light_window(C: dcg.Context):
    """Minimal window
    
    This benchmark measures the rendering performance of
    a simple window with just a text element.
    """
    # Graph metadata
    yield (("Frames", "Frames rendered per second"),)

    # Prepare the benchmark
    with dcg.Window(C, label="Minimal Window", width=300, height=300):
        dcg.Text(C, value="Hello")
    
    # Render frames in small batches and yield results
    
    while True:
        prev_time = monotonic()
        target_time = prev_time + 0.05

        ops = 0
        while monotonic() < target_time:
            for _ in range(10): # we batch to reduce the overhead of monotonic
                C.viewport.render_frame()
            ops += 10
        
        current_time = monotonic()
        yield (prev_time, current_time, ops)
        await asyncio.sleep(0)

@benchmark(category="Rendering", rendering_thread=True)
async def many_buttons(C: dcg.Context):
    """20000 Buttons
    
    This benchmark measures the rendering performance of
    a heavy window of 20000 buttons.
    """
    # Graph metadata
    yield (("Frames", "Frames rendered per second"),)

    # Prepare the benchmark
    with dcg.Window(C, width="fullx", height="fully", primary=True):
        with dcg.HorizontalLayout(C):
            for i in range(20000):
                dcg.Button(C, label=f"Btn{i}")
    
    # Render frames in small batches and yield results
    while True:
        prev_time = monotonic()
        target_time = prev_time + 0.05

        ops = 0
        while monotonic() < target_time:
            C.viewport.render_frame()
            ops += 1
        
        current_time = monotonic()
        yield (prev_time, current_time, ops)
        await asyncio.sleep(0)

@benchmark(category="Rendering", rendering_thread=True)
async def many_lines(C: dcg.Context):
    """20000 lines

    This benchmark measures the rendering performance of
    a heavy window of 20000 lines drawn using the drawing API.
    """
    # First yield provides graph metadata
    yield (("Frames", "Frames rendered per second"),)

    # Prepare the benchmark
    with dcg.Window(C, width="fullx", height="fully", primary=True):
        with dcg.DrawInWindow(C, width="fillx", height="filly", relative=True):
            for i in range(20000):
                # We make the lines in  the viewport to not be skipped
                dcg.DrawLine(C, p1=(i/20000, 0), p2=(0.5, 0.5), color=(255, 0, 0, 20), thickness=-1.1)
    
    # Render frames in small batches and yield results
    while True:
        prev_time = monotonic()
        target_time = prev_time + 0.05

        ops = 0
        while monotonic() < target_time:
            C.viewport.render_frame()
            ops += 1
        
        current_time = monotonic()
        yield (prev_time, current_time, ops)
        await asyncio.sleep(0)

@benchmark(category="Operations", rendering_thread=False)
async def button_creation(C: dcg.Context):
    """Button creation
    
    This benchmark tests the speed of creating simple UI items.
    """
    # First yield provides graph metadata
    yield (("Button creation", "Simple button instantiation"),)

    window = dcg.Window(C, width="fullx", height="fully", primary=True)
    
    # Run operations in small batches and yield results
    batch_size = 100
    gc_state = gc.isenabled()
    try:
        gc.disable()
        while True:
            prev_time = monotonic()
            target_time = prev_time + 0.05

            ops = 0
            with window.mutex:
                while monotonic() < target_time:
                    for i in range(batch_size):
                        dcg.Button(C, label=str(ops), parent=window, no_newline=(i != batch_size - 1))
                    ops += batch_size
            
            current_time = monotonic()
            yield (prev_time, current_time, ops)
            await asyncio.sleep(0)  # Allow other tasks to run
            window.children = [] # Clear previous child list
            gc.collect() # collect previous items manually
    finally:
        # Reset GC state
        if gc_state:
            gc.enable()
        else:
            gc.disable()

@benchmark(category="Operations", rendering_thread=False)
async def property_setting_speed(C: dcg.Context):
    """Setting properties
    
    Creates a grid of stars and tests setting different
    properties (direction and color).
    """
    # First yield provides graph metadata
    yield (
        ("Direction Property", "Setting rotation/angle properties"),
        ("Color Property", "Setting color/visual properties")
    )
    
    # Create the container and stars
    stars = []
    num_stars_x = 200
    num_stars_y = 100
    radius = 0.45 / num_stars_x
    inner_radius = radius * 0.4
    thickness = radius * 0.1
    total_stars = num_stars_x * num_stars_y
    
    with dcg.Window(C, label="Property Setting Benchmark", primary=True):
        with dcg.DrawInWindow(C, width="fillx", height="filly", relative=True):
            # Create a grid of stars
            for y in range(num_stars_y):
                for x in range(num_stars_x):
                    # Calculate position as a fraction of window size
                    pos_x = (x + 0.5) / num_stars_x
                    pos_y = (y + 0.5) / num_stars_y
                    
                    # Create a star with initial properties
                    star = dcg.DrawStar(C, 
                                       center=(pos_x, pos_y),
                                       radius=radius,
                                       inner_radius=inner_radius,
                                       num_points=5,
                                       direction=0.0,
                                       thickness=thickness,
                                       color=0,
                                       fill=(255, 255, 0))
                    stars.append(star)
    
    # Animation parameters
    direction = 0.0
    hue = 0.0

    # Run benchmark in a loop
    
    while True:
        # Update animation parameters
        direction = monotonic() % (2 * math.pi)  # Rotate direction
        hue = (monotonic() / 10) % 1.0  # Cycle hue over time
        
        # Convert HSV to RGB using colorsys
        r, g, b = colorsys.hsv_to_rgb(hue, 0.9, 0.9)
        current_color = (r, g, b)
        
        # Test direction property updates
        # Doing 10 times to reduce impact of for loop
        direction_start = monotonic()
        for star in stars:
            star.direction = direction
            star.direction = direction
            star.direction = direction
            star.direction = direction
            star.direction = direction
            star.direction = direction
            star.direction = direction
            star.direction = direction
            star.direction = direction
            star.direction = direction
        
        direction_end = monotonic()
        
        # Test color property updates
        for star in stars:
            star.fill = current_color
            star.fill = current_color
            star.fill = current_color
            star.fill = current_color
            star.fill = current_color
            star.fill = current_color
            star.fill = current_color
            star.fill = current_color
            star.fill = current_color
            star.fill = current_color
        
        color_end = monotonic()
        
        # Yield results
        yield (direction_start, direction_end, 10 * total_stars, None)
        yield (direction_end, color_end, None, 10 * total_stars)
        
        await asyncio.sleep(0)  # Let other tasks run

@benchmark(category="Operations", rendering_thread=False)
async def item_creation_methods(C: dcg.Context):
    """Item creation: Direct vs Parameters vs Subclassing
    
    Tests creation performance differences between simple instantiation,
    creation with many parameters, and subclass instantiation.
    """
    # Define subclass and parameters for testing
    class ButtonSub(dcg.Button):
        __slots__ = []
        def __init__(self, context, **kwargs):
            return dcg.Button.__init__(self, context, **kwargs)
    
    params = {
        "width": 4, "height": 8, "x": 0, "y": 0,
        "arrow": dcg.ButtonDirection.UP, "show": True, "context": C,
        "enabled": True, "no_newline": True, "scaling_factor": 2.
    }
    
    # First yield provides graph metadata
    yield (
        ("Direct Creation", "Creating items with no parameters"),
        ("Creation with parameters", "Creating items with many parameters"),
        ("Subclass Creation", "Creating items through subclassing")
    )
    
    # Run operations in small batches and yield results
    batch_size = 50

    gc_state = gc.isenabled()

    try:
        gc.disable()
        while True:
            time0 = monotonic()
            # Test simple creation
            for _ in range(batch_size):
                dcg.Button(C)
                dcg.Button(C)
                dcg.Button(C)
                dcg.Button(C)
                dcg.Button(C)
                dcg.Button(C)
                dcg.Button(C)
                dcg.Button(C)
                dcg.Button(C)
                dcg.Button(C)
            
            time1 = monotonic()
            
            # Test creation with parameters
            for _ in range(batch_size):
                dcg.Button(**params)
                dcg.Button(**params)
                dcg.Button(**params)
                dcg.Button(**params)
                dcg.Button(**params)
                dcg.Button(**params)
                dcg.Button(**params)
                dcg.Button(**params)
                dcg.Button(**params)
                dcg.Button(**params)
            
            time2 = monotonic()
            
            # Test subclass creation
            for _ in range(batch_size):
                ButtonSub(**params)
                ButtonSub(**params)
                ButtonSub(**params)
                ButtonSub(**params)
                ButtonSub(**params)
                ButtonSub(**params)
                ButtonSub(**params)
                ButtonSub(**params)
                ButtonSub(**params)
                ButtonSub(**params)
            
            time3 = monotonic()
            
            yield (time0, time1, batch_size*10, None, None)
            yield (time1, time2, None, batch_size*10, None)
            yield (time2, time3, None, None, batch_size*10)

            await asyncio.sleep(0)
            gc.collect()
    finally:
        # Reset GC state
        if gc_state:
            gc.enable()
        else:
            gc.disable()

@benchmark(category="Concurrency", rendering_thread=True)
async def thread_contention(C: dcg.Context):
    """Measures UI performance under thread contention.
    
    Creates a window with buttons and launches threads that continuously
    add and remove buttons, measuring both frame rate and operation throughput.
    """
    with dcg.Window(C, label="Contention Test", width=600, height=600) as main_window:
        buttons = []
        with dcg.HorizontalLayout(C):
            for i in range(100):
                btn = dcg.Button(C, label=f"Btn{i}")
                buttons.append(btn)
    
    # First yield provides graph metadata
    yield (
        ("Frames", "Frames rendered per second"),
        ("Operations", "Button add/remove operations per second")
    )
    
    # Shared state for threads
    running = True
    operations_count = 0
    lock = threading.Lock()
    
    def modify_buttons():
        nonlocal operations_count
        while running:
            # Add a new button
            new_btn = dcg.Button(C, label=f"Btn{len(buttons)}")
            buttons.append(new_btn)
            # Remove the oldest button
            old_btn = buttons.pop(0)
            old_btn.parent = None
            new_btn.parent = main_window
            with lock:
                operations_count += 2  # One add and one remove
            sleep(0.001)  # Small delay to prevent overwhelming
    
    # Start threads
    threads = [threading.Thread(target=modify_buttons) for _ in range(4)]
    for thread in threads:
        thread.start()
    
    try:
        # Run in small batches and yield results
        batch_frames = 5
        prev_time = monotonic()
        
        while True:
            frames = 0
            operations_before = operations_count
            
            for _ in range(batch_frames):
                C.viewport.render_frame()
                frames += 1
            
            with lock:
                operations_after = operations_count
                operations_delta = operations_after - operations_before
            
            current_time = monotonic()
            yield (prev_time, current_time, frames, operations_delta)
            prev_time = current_time
            await asyncio.sleep(0)
    
    finally:
        # Cleanup
        running = False
        for thread in threads:
            thread.join(0.5)

@benchmark(category="Textures", rendering_thread=False)
async def texture_update_formats(C: dcg.Context):
    """Texture update speed
    
    Tests how quickly textures can be updated using NumPy arrays (direct path) versus
    Python lists.
    """
    # Setup textures and data
    texture_numpy = dcg.Texture(C)
    texture_list = dcg.Texture(C)
    
    numpy_data = np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)
    list_data = numpy_data.tolist()
    
    # First yield provides graph metadata
    yield (
        ("NumPy Updates", "Texture updates using NumPy arrays"),
        ("List Updates", "Texture updates using Python lists")
    )

    # Create window for visualization
    with dcg.Window(C, label="Texture Update Performance", width=700, height=500) as main_window:
        # Performance metrics
        with dcg.HorizontalLayout(C, width=-1):
            numpy_rate = dcg.TextValue(C, print_format="NumPy: %.1f updates/sec", 
                                       shareable_value=dcg.SharedFloat(C, 0.0))
            dcg.Spacer(C, width=20)
            list_rate = dcg.TextValue(C, print_format="List: %.1f updates/sec", 
                                      shareable_value=dcg.SharedFloat(C, 0.0))
            dcg.Spacer(C, width=20)
            ratio_display = dcg.TextValue(C, print_format="NumPy is %.1fx faster", 
                                          shareable_value=dcg.SharedFloat(C, 1.0))
        
        dcg.Separator(C)
        
        # Live preview
        dcg.Text(C, value="Live Texture Updates:")
        with dcg.HorizontalLayout(C, width=-1):
            # NumPy texture display
            with dcg.VerticalLayout(C, width=300):
                dcg.Text(C, value="NumPy Array Texture:")
                dcg.Image(C, texture=texture_numpy, 
                          width=300, height=300)
            
            # List texture display
            with dcg.VerticalLayout(C, width=300):
                dcg.Text(C, value="Python List Texture:")
                dcg.Image(C, texture=texture_list, 
                          width=300, height=300)
    
    # Create texture generator function
    def generate_texture_data(t):
        # Generate time-varying texture
        noise = np.random.randint(0, 50, (300, 300, 3), dtype=np.uint8)
        
        # Base color cycles through RGB
        r = int(127 + 127 * np.sin(t * 0.5))
        g = int(127 + 127 * np.sin(t * 0.5 + np.pi * 2/3))
        b = int(127 + 127 * np.sin(t * 0.5 + np.pi * 4/3))
        
        # Create a pattern with the base color
        base = np.zeros((300, 300, 3), dtype=np.uint8)
        base[:, :, 0] = r
        base[:, :, 1] = g
        base[:, :, 2] = b
        
        # Add some geometric patterns
        cx, cy = 150, 150
        radius = 100 * (0.5 + 0.5 * np.sin(t * 2))
        y, x = np.ogrid[-cy:300-cy, -cx:300-cx]
        mask = x*x + y*y <= radius*radius
        base[mask, 0] = 255
        base[mask, 1] = 255
        base[mask, 2] = 255
        
        # Add noise
        result = np.clip(base + noise, 0, 255)
        return result
    
    # Run operations in small batches and yield results
    batch_size = 10
    
    while True:
        current_time = monotonic()
        
        # Generate new texture data for this frame
        numpy_data = generate_texture_data(current_time)
        list_data = numpy_data.tolist()
        
        time0 = monotonic()
        # Test NumPy updates
        for _ in range(batch_size):
            texture_numpy.set_value(numpy_data)
        
        time1 = monotonic()
        
        # Test list updates
        for _ in range(batch_size):
            texture_list.set_value(list_data)
        
        time2 = monotonic()

        # Calculate deltas
        numpy_delta = time1 - time0
        list_delta = time2 - time1
        
        # Calculate rates
        numpy_rate.value = batch_size / numpy_delta
        list_rate.value = batch_size / list_delta
            
        # Calculate ratio if both are valid
        ratio_display.value = numpy_rate.value / list_rate.value
        
        yield (time0, time1, batch_size, None)
        yield (time1, time2, None, batch_size)

        await asyncio.sleep(0)

@benchmark(category="Memory", rendering_thread=True)
async def gc_performance(C: dcg.Context):
    """Garbage collection impact
    
    Tests GC performance with circular references, and
    deep object hierarchies to identify collection bottlenecks.
    """
    # First yield provides graph metadata
    yield (
        ("Collecting Circular Refs", "Number of items collectable per second (simple circular references)"),
        ("Traversing Deep Hierarchy", "Number of items traversable per second (deep object hierarchy, uncollectable)")
    )
    
    # Create test classes outside the loop
    class CircularTest:
        def __init__(self):
            self.window = dcg.Window(C, attach=False)
            self.button = dcg.Button(C, parent=self.window)
            self.button.user_data = self  # Create circular reference
    
    class DeepTest(dcg.Layout):
        def __init__(self, C, depth, **kwargs):
            super().__init__(C, **kwargs)
            if depth > 0:
                self.child1 = DeepTest(C, depth-1, parent=self)
                self.child2 = DeepTest(C, depth-1, parent=self)
    
    # Track which test to run next
    test_number = 0
    gc_was_enabled = gc.isenabled()
    try:
        if not gc_was_enabled:
            gc.enable()
        while True:
            prev_time = monotonic()
            
            if test_number == 0:
                # Test 1: Circular references
                # Create circular reference objects
                for _ in range(1000):
                    CircularTest()
                gc.collect()
                test_result = 1000  # Number of objects collected
                
            else:  # test_number == 1
                # Test 3: Deep hierarchy
                # Create and collect a deep hierarchy
                top = DeepTest(C, 12)
                gc.collect()
                del top
                test_result = 2**12 - 1  # Approximate number of nodes in binary tree
            
            current_time = monotonic()
            
            # Yield results specific to the current test
            if test_number == 0:
                yield (prev_time, current_time, test_result, None)
            else:
                yield (prev_time, current_time, None, test_result)
            
            # Advance to next test
            test_number = (test_number + 1) % 2
            
            # Clear everything between tests
            gc.collect()
            
            # Give other tasks a chance to run
            await asyncio.sleep(0.)
    finally:
        # Reset GC state
        if not gc_was_enabled:
            gc.disable()

@benchmark(category="Tables", rendering_thread=True)
async def table_performance(C: dcg.Context):
    """Table rendering and filling speed
    
    Tests both rendering performance with large tables and the speed
    of filling tables with content to identify API bottlenecks.
    """
    # First yield provides graph metadata
    yield (
        ("Frames", "Frames rendered per second with large table"),
        ("Cells", "Table cells filled per second")
    )
    
    # Create a table for rendering test
    with dcg.Window(C, label="Table Benchmark", width=600, height=600):
        render_table = dcg.Table(C, width=-1, height=-1)
        for i in range(1000):
            for j in range(10):
                render_table[i, j] = "Hello"
    
    # Create a separate unrendered table for filling test
    fill_table = dcg.Table(C, width=-1, height=-1)
    cells_per_batch = 1000
    
    # Run in alternating batches and yield results
    batch_frames = 10
    
    while True:
        time0 = monotonic()
        # Test rendering
        for _ in range(batch_frames):
            C.viewport.render_frame()
        
        time1 = monotonic()
        
        # Test filling
        fill_table.clear()
        for i in range(cells_per_batch // 10):
            for j in range(10):
                fill_table[i, j] = "Hello"
        
        time2 = monotonic()
        
        yield (time0, time1, batch_frames, None)
        yield (time1, time2, None, cells_per_batch)

        await asyncio.sleep(0)

@benchmark(category="Drawing", rendering_thread=True)
async def shape_rendering_speed(C: dcg.Context):
    """Shape drawing operations
    
    Renders stars, arcs, and ellipses to measure relative performance
    of different drawing operations to identify optimization opportunities.
    """
    # Setup windows for each shape type
    
    # Stars window
    with dcg.Window(C, label="Star Drawing", width=600, height=600):
        with dcg.DrawInWindow(C, width=-1, height=-1):
            for i in range(5000):
                dcg.DrawStar(C, center=(35, 35),
                            color=(0, 0, 255), radius=-21, thickness=-1,
                            fill=(0, 255, 255, 100),
                            inner_radius=-11, num_points=5)
    
    # Arcs window
    with dcg.Window(C, label="Arc Drawing", width=600, height=600):
        with dcg.DrawInWindow(C, width=-1, height=-1):
            for i in range(5000):
                dcg.DrawArc(C, center=(100, 100),
                            color=(0, 0, 255), radius=(50, 80), thickness=-1,
                            fill=(0, 255, 255, 100),
                            start_angle=0, end_angle=360)
    
    # Ellipses window
    with dcg.Window(C, label="Ellipse Drawing", width=600, height=600):
        with dcg.DrawInWindow(C, width=-1, height=-1):
            for i in range(5000):
                dcg.DrawEllipse(C, pmin=(0, 0), pmax=(100, 100), segments=41,
                                color=(0, 0, 255), thickness=-1,
                                fill=(0, 255, 255, 100))

    # Rectangle window
    with dcg.Window(C, label="Rectangle Drawing", width=600, height=600):
        with dcg.DrawInWindow(C, width=-1, height=-1):
            for i in range(5000):
                dcg.DrawRect(C, pmin=(0, 0), pmax=(100, 100),
                             color=(0, 0, 255), thickness=-1,
                             fill=(0, 255, 255, 100))
    
    # First yield provides graph metadata
    yield (
        ("Stars", "Star shape rendering performance"),
        ("Arcs", "Arc shape rendering performance"),
        ("Ellipses", "Ellipse shape rendering performance"),
        ("Rectangles", "Rectangle shape rendering performance")
    )
    
    # Run in rotating window focus and yield results
    windows = C.viewport.children
    shapes_per_window = 5000
    
    while True:
        for i, window in enumerate(windows):
            for win in windows: # Hide all windows
                win.show = False
            window.show = True # show the target one

            time0 = monotonic()

            C.viewport.render_frame()
            
            time1 = monotonic()
            
            if i == 0:  # Stars window
                yield (time0, time1, shapes_per_window, None, None, None)
            elif i == 1:  # Arcs window
                yield (time0, time1, None, shapes_per_window, None, None)
            elif i == 2:  # Ellipses window
                yield (time0, time1, None, None, shapes_per_window, None)
            else:  # Rectangles window
                yield (time0, time1, None, None, None, shapes_per_window)

            await asyncio.sleep(0)

@benchmark(category="Callbacks", rendering_thread=True)
async def sync_callback_performance(C: dcg.Context):
    """Callback performance
    
    Tests execution speed of standard synchronous callbacks,
    using the default pool.
    """
    # First yield provides graph metadata
    yield (("Normal callback", "Default callback performance"),)
    
    # Setup for synchronous callbacks
    num_callbacks = 0
    def empty_callback(sender, target, data):
        """A simple callback that does nothing."""
        nonlocal num_callbacks
        num_callbacks += 1

    C.queue = ThreadPoolExecutor(max_workers=1)

    with dcg.Window(C, label="Sync Callbacks", width=300, height=300) as window:
        value_feedback = dcg.TextValue(C, print_format="Number of callbacks called: %d", shareable_value=dcg.SharedInt(C, 0))
        
    window.handlers = [
        dcg.RenderHandler(C, callback=empty_callback) for _ in range(500)
    ]
        
    while True:
        # Test synchronous callbacks
        prev_time = monotonic()
        for _ in range(10):
            C.viewport.render_frame()
        # Wait all callbacks are run
        C.queue.submit(lambda: None).result()
        sync_time = monotonic()
        sync_calls = 5000  # One frame with 500 handlers
        value_feedback.value = num_callbacks
        
        yield (prev_time, sync_time, sync_calls)
        await asyncio.sleep(0.)

@benchmark(category="Callbacks", rendering_thread=True)
async def thread_pool_callback_performance(C: dcg.Context):
    """Callback performance (Async Thread Pool)
    
    Tests execution speed of callbacks using the async thread pool execution.
    """
    # First yield provides graph metadata
    yield (("Normal callback", "Async thread pool executor callback performance"),)
    
    # Setup for thread pool callbacks
    num_callbacks = 0
    def empty_callback(sender, target, data):
        """A simple callback that does nothing."""
        nonlocal num_callbacks
        num_callbacks += 1
        
    C.queue = AsyncThreadPoolExecutor()
    
    with dcg.Window(C, label="Thread Pool Callbacks", width=300, height=300) as window:
        value_feedback = dcg.TextValue(C, print_format="Number of callbacks called: %d", shareable_value=dcg.SharedInt(C, 0))
        
    window.handlers = [
        dcg.RenderHandler(C, callback=empty_callback) for _ in range(500)
    ]

    while True:
        # Test thread pool callbacks
        prev_time = monotonic()
        for _ in range(10):
            C.viewport.render_frame()
        # Wait all callbacks are run
        C.queue.submit(lambda: None).result()
        thread_time = monotonic()
        thread_calls = 5000  # One frame with 500 handlers
        value_feedback.value = num_callbacks
        
        yield (prev_time, thread_time, thread_calls)
        await asyncio.sleep(0.)

@benchmark(category="Callbacks", rendering_thread=True)
async def coroutine_callback_performance(C: dcg.Context):
    """Async callback performance (Async Thread Pool)
    
    Tests execution speed of asynchronous coroutine callbacks.
    """
    # First yield provides graph metadata
    yield (("Async callback", "Async coroutine callback performance"),)
    
    # Setup for coroutine callbacks
    num_callbacks = 0
    async def empty_async_callback(sender, target, data):
        """A simple async callback that does nothing."""
        nonlocal num_callbacks
        num_callbacks += 1

    C.queue = AsyncThreadPoolExecutor()

    with dcg.Window(C, label="Coroutine Callbacks", width=300, height=300) as window:
        value_feedback = dcg.TextValue(C, print_format="Number of callbacks called: %d", shareable_value=dcg.SharedInt(C, 0))
        
    window.handlers = [
        dcg.RenderHandler(C, callback=empty_async_callback) for _ in range(500)
    ]

    while True:
        # Test coroutine callbacks
        prev_time = monotonic()
        for _ in range(10):
            C.viewport.render_frame()
        # Wait all callbacks are run
        C.queue.submit(lambda: None).result()
        coro_time = monotonic()
        coro_calls = 5000  # One frame with 500 handlers
        value_feedback.value = num_callbacks
        
        yield (prev_time, coro_time, coro_calls)
        await asyncio.sleep(0.)

@benchmark(category="Callbacks", rendering_thread=True)
async def event_loop_callback_performance(C: dcg.Context):
    """Async callback performance (Async Pool)
    
    Tests execution speed of callbacks using the full asyncio event loop.
    """
    # First yield provides graph metadata
    yield (("Async callback", "Full asyncio event loop + 500 callbacks performance (single thread)"),)
    
    # Setup for event loop callbacks
    num_callbacks = 0
    async def empty_async_callback(sender, target, data):
        """A simple async callback that does nothing."""
        nonlocal num_callbacks
        num_callbacks += 1

    C.queue = AsyncPoolExecutor()

    with dcg.Window(C, label="Event Loop Callbacks", width=300, height=300) as window:
        value_feedback = dcg.TextValue(C, print_format="Number of callbacks called: %d", shareable_value=dcg.SharedInt(C, 0))
    
    window.handlers = [
        dcg.RenderHandler(C, callback=empty_async_callback) for _ in range(500)
    ]

    while True:
        # For the asyncio test, we need to use the event loop
        start_frame = C.viewport.metrics["frame_count"]
        async_start_time = monotonic()

        try:
            async with asyncio.timeout(0.05):
                await run_viewport_loop(C.viewport, frame_rate=math.inf)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            print(f"Asyncio test error: {e}")
            
        async_end_time = monotonic()
        stop_frame = C.viewport.metrics["frame_count"]
        frames = stop_frame - start_frame
        asyncio_calls = frames * 500  # 500 callbacks per frame
        value_feedback.value = num_callbacks
        
        yield (async_start_time, async_end_time, asyncio_calls)
        await asyncio.sleep(0.)


async def run_benchmark_with_timeout(benchmark_info, duration=10):
    """Run a benchmark for a specified duration and return metrics."""
    # Create a context for the benchmark
    C = dcg.Context()
    
    # Initialize viewport
    C.viewport.initialize(
        wait_for_input=False,
        visible=False,
        width=600, height=400, vsync=False,
        title=benchmark_info.short_description
    )
    
    metrics = []
    try:
        # Start the benchmark generator
        benchmark_generator = benchmark_info.run(C)
        
        # Get metadata from first yield
        metadata = await anext(benchmark_generator)
        metrics = [(name, desc, []) for name, desc in metadata]
        
        # Run the benchmark for the specified duration
        end_time = monotonic() + duration
        while monotonic() < end_time:
            try:
                result = await anext(benchmark_generator)
                dt = result[1] - result[0]
                
                if dt > 0:
                    for i, val in enumerate(result[2:]):
                        if val is not None:
                            metrics[i][2].append(val / dt)
            except StopAsyncIteration:
                break
                
            await asyncio.sleep(0.01)
    finally:
        # Clean up resources
        C.viewport.children = []
        C.running = False
        gc.collect()
    
    return metrics

def format_number(value):
    """Format a number for display with K/M/B suffixes for large values."""
    if value < 1000:
        return f"{value:.2f}"
    elif value < 1_000_000:
        return f"{value/1000:.1f}K"
    elif value < 1_000_000_000:
        return f"{value/1_000_000:.1f}M"
    else:
        return f"{value/1_000_000_000:.1f}B"

async def run_all_benchmarks(duration_per_benchmark=10):
    """Run all benchmarks sequentially and print results."""
    total_benchmarks = len(benchmarks_list)
    
    for i, benchmark_info in enumerate(benchmarks_list):
        print(f"\nBenchmark [{i+1}/{total_benchmarks}]: {benchmark_info.short_description}")
        print(f"Category: {benchmark_info.category}")
        if benchmark_info.long_description:
            print(f"{benchmark_info.long_description}")
        print(f"Running for {duration_per_benchmark} seconds...")
        
        try:
            metrics = await run_benchmark_with_timeout(benchmark_info, duration_per_benchmark)
            
            # Print results
            print("\nResults:")
            for name, description, values in metrics:
                if values:
                    avg = sum(values) / len(values)
                    min_val = min(values)
                    max_val = max(values)
                    print(f"  {name}: {format_number(avg)} ops/sec")
                    print(f"    Min: {format_number(min_val)}, Max: {format_number(max_val)}, Samples: {len(values)}")
                    print(f"    {description}")
                else:
                    print(f"  {name}: No data collected")
                    print(f"    {description}")
            
        except Exception as e:
            print(f"Error running benchmark: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 80)
        
    print("\nAll benchmarks completed!")

if __name__ == "__main__":
    import sys
    
    # Default duration is 10 seconds per benchmark
    duration = 10
    
    # Allow specifying duration from command line
    if len(sys.argv) > 1:
        try:
            duration = float(sys.argv[1])
        except ValueError:
            print(f"Invalid duration: {sys.argv[1]}, using default of 10 seconds")
    
    print(f"Running all benchmarks with {duration} seconds per benchmark")
    asyncio.run(run_all_benchmarks(duration))
