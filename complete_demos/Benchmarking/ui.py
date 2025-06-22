from array import array
import asyncio
import dearcygui as dcg
from dearcygui.utils.asyncio_helpers import AsyncThreadPoolExecutor, run_viewport_loop
import math
import numpy as np
import time
import traceback

from benchmarks import benchmarks_list, BenchmarkInfo

benchmarks_running = False
summary_window: dcg.Window | None = None
plot_window: dcg.Window | None = None

if not hasattr(asyncio, 'TaskGroup'):
    # Fallback for Python versions < 3.11
    class TaskGroup:
        def __init__(self):
            self.tasks = []

        def create_task(self, coro):
            task = asyncio.create_task(coro)
            self.tasks.append(task)
            return task

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            await asyncio.gather(*self.tasks, return_exceptions=True)
    asyncio.TaskGroup = TaskGroup

class TerminateTaskGroup(Exception):
       """Exception raised to terminate a task group."""

class ScrollingBuffer:
    """
    A scrolling buffer with a large memory backing.
    Does copy only when the memory backing is full.
    """
    def __init__(self,
                 scrolling_size=50000, 
                 max_size=1000000):
        self.data = array('d', [0.0] * max_size)
        assert(2 * scrolling_size < max_size)
        self.size = 0
        self.scrolling_size = scrolling_size
        self.max_size = max_size

    def push(self, value):
        if self.size >= self.max_size:
            # We reached the end of the buffer.
            # Restart from the beginning
            self.data[:self.scrolling_size] = self.data[-self.scrolling_size:]
            self.size = self.scrolling_size
        self.data[self.size] = value
        self.size += 1

    def get(self, requested_size=None):
        if requested_size is None:
            requested_size = self.scrolling_size
        else:
            requested_size = min(self.scrolling_size, requested_size)
        start = max(0, self.size-requested_size)
        return self.data[start:self.size]

async def update_plotline(plotline: dcg.PlotLine,
                          buffer_x: ScrollingBuffer,
                          buffer_y: ScrollingBuffer):
    """
    Frequently update the plot line with new data.
    """
    plot = plotline.parent
    assert plot is not None
    x_axis = plot.X1
    while True:
        times = buffer_x.get()
        if len(times) == 0:
            #print("Empty times")
            await asyncio.sleep(0.1)
            continue
        #for i in range(len(times)):
        #    print(times[i])
        # Update the plot line with the new data
        plotline.X = times
        plotline.Y = buffer_y.get()
        # Move the x-axis to the right
        with x_axis.mutex:
            #delta = x_axis.max - x_axis.min
            #x_axis.min = times[len(times)-1] - delta
            x_axis.max = times[len(times)-1]
        plotline.context.viewport.wake()
        await asyncio.sleep(0.1)

async def run_benchmark(
        benchmark_generator, #async generator
        buffers_x: list[ScrollingBuffer],
        buffers_y: list[ScrollingBuffer]):
    """
    Run a benchmark in the background
    """
    global benchmarks_running
    benchmarks_running = True
    try:
        # Run the benchmark and collect results
        async for result in benchmark_generator:
            # Update the buffers with the results
            #print(result)
            try:
                dt = result[1] - result[0]
                t = result[1]
                for i, val in enumerate(result[2:]):
                    if val is None:
                        continue
                    #print(val, dt)
                    buffers_x[i].push(t)
                    buffers_y[i].push(val / dt if dt > 0 else 0.0)
                    #print(i, t, val / dt)
                #print(await anext(benchmark_generator))
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
    except asyncio.CancelledError:
        pass
    finally:
        benchmarks_running = False

async def start_benchmark(sender: dcg.baseItem):
    """
    Start a benchmark when the button is clicked.
    """
    C = None
    bench_C = None
    try:
        global benchmarks_running, summary_window, plot_window
        if benchmarks_running:
            return  # A benchmark is already running

        # Get the benchmark info from the sender
        benchmark = sender.user_data
        if not isinstance(benchmark, BenchmarkInfo):
            raise TypeError("Sender data must be a BenchmarkInfo instance")

        async def create_benchmark_context() -> dcg.Context:
            # Create a new context for the benchmark
            C = dcg.Context()
            # initialize its viewport
            C.viewport.initialize(wait_for_input=False,
                                  decorated=True,
                                  disable_close=True,
                                  resizable=False,
                                  vsync=False,
                                  width=800,
                                  height=600,
                                  always_submit_to_gpu=False,
                                  clear_color = (0, 0, 0, 190),
                                  title=benchmark.short_description)
            return C

        context_pool = sender.context.viewport.user_data

        # Context must be created in the main thread
        bench_C = await asyncio.wrap_future(context_pool.submit(create_benchmark_context()))

        async def start_generator():
            # initialize the async benchmark generator
            # on the target loop executor
            return benchmark.run(bench_C)

        async def get_benchmark_metadata(benchmark_generator):
            """
            Get the metadata from the benchmark generator.
            """
            # Get the metadata from the benchmark generator
            metadata = await anext(benchmark_generator)
            return metadata

        if benchmark.rendering_thread:
            # The benchmark must run on the rendering thread,
            # The current loop is configured to have it accessible in run_in_executor
            
            benchmark_generator = await asyncio.wrap_future(context_pool.submit(start_generator()))
            metadata = await asyncio.wrap_future(
                context_pool.submit(get_benchmark_metadata(benchmark_generator)))
        else:
            # If the benchmark is not running on the rendering thread,
            # we can run it directly in the current loop
            benchmark_generator = await start_generator()
            metadata = await get_benchmark_metadata(benchmark_generator)

        # Create a new window for the benchmark
        C = sender.context
        buffers = [(ScrollingBuffer(), ScrollingBuffer()) for _ in range(len(metadata))]
        plot_lines = []
        # Create a plot window with subplots for each benchmark result
        if plot_window is None:
            def constrain_window_below_title_bar(sender, target: dcg.Window):
                """Constrain the plot window to be below the custom title bar."""
                # Ensure the plot window is below the title bar
                # At some point we will likely add an API for that.
                title_bar = C.viewport.children[0]  # Assuming the title bar is the first child
                min_y = title_bar.state.rect_size.y + title_bar.state.pos_to_viewport.y
                # This doesn't work very well with dragging and will have to be improved.
                if target.state.pos_to_viewport.y < min_y:
                    target.y = min_y / target.context.viewport.dpi
                    target.x = target.state.pos_to_viewport.x / target.context.viewport.dpi
                
            plot_window = dcg.Window(C, label="Benchmark stats", handlers=\
                                     [dcg.MotionHandler(C,
                                                        callback=constrain_window_below_title_bar,
                                                        pos_policy=(dcg.Positioning.DEFAULT, dcg.Positioning.REL_VIEWPORT))])
        else:
            # Reuse the previous plot window
            plot_window.show = True
            plot_window.focus()
        with dcg.ChildWindow(C, width="fillx", height="0.8*fully", parent=plot_window) as window:
            with dcg.HorizontalLayout(C):
                dcg.Text(C, value=benchmark.short_description + ": ")
                stop_handler = dcg.ActivatedHandler(C)
                stop_button = dcg.Button(C, label="Stop Benchmark", handlers=[stop_handler])
            num_rows = int(round(math.sqrt(len(metadata))))
            num_cols = int(math.ceil(len(metadata) / num_rows))
            with dcg.Subplots(C, rows=num_rows, cols=num_cols, width="fillx", height="filly") as subplots:
                shared_x_axis = dcg.PlotAxisConfig(C)
                shared_x_axis.no_initial_fit = True
                shared_x_axis.min = time.monotonic()
                shared_x_axis.max = time.monotonic() + 4 # 4 seconds of data
                shared_x_axis.lock_max = True
                shared_x_axis.constraint_min = shared_x_axis.min
                shared_x_axis.label = "Time (s)"

                for i, (short, _) in enumerate(metadata):
                    with dcg.Plot(C, label=short) as plot:
                        plot.X1 = shared_x_axis
                        plot.Y1.auto_fit = True
                        plot.Y1.min = 0.
                        plot.Y1.lock_min = True
                        plot.Y1.label = "ops/s"
                        # Create plot lines for each benchmark result
                    
                        plot_line = dcg.PlotLine(
                            C, no_legend=True)
                        plot_lines.append(plot_line)

            for i, (_, long) in enumerate(metadata):
                with dcg.Tooltip(C, target=subplots.children[i]):
                    dcg.Text(C, value=long)
        # Place at the top, with a separator:
        if plot_window.children[0] is not window:
            window.next_sibling = plot_window.children[0]
            dcg.Separator(C, previous_sibling=window)

        # Start concurrently the benchmark and the plot update
        async with asyncio.timeout(10.):
            try:
                async with asyncio.TaskGroup() as tg:
                    # Start the benchmark in the background
                    buffers_x = [b[0] for b in buffers]
                    buffers_y = [b[1] for b in buffers]
                    if benchmark.rendering_thread:
                        # Run the benchmark in the rendering thread
                        async def run_benchmark_in_executor():
                            await asyncio.wrap_future(
                                context_pool.submit(run_benchmark(benchmark_generator, buffers_x, buffers_y))
                            )
                            print("Benchmark done")
                        tg.create_task(run_benchmark_in_executor())
                    else:
                        # Run the benchmark directly in the current loop
                        tg.create_task(run_benchmark(benchmark_generator, 
                                                    [b[0] for b in buffers], 
                                                    [b[1] for b in buffers]))
                        # Render from time to time
                        async def viewport_loop():
                            await asyncio.wrap_future(
                                context_pool.submit(run_viewport_loop(bench_C.viewport, frame_rate=10))
                            )
                        tg.create_task(viewport_loop())

                    # Update the plot lines with the new data
                    for i, (buffer_x, buffer_y) in enumerate(buffers):
                        tg.create_task(update_plotline(plot_lines[i], buffer_x, buffer_y))

                    # Stop when the stop button is pressed
                    async def stop_benchmark():
                        global benchmarks_should_stop
                        await asyncio.wrap_future(dcg.utils.handler.future_from_handlers(stop_handler))
                        # Release X axis
                        plot.X1.lock_max = False # type: ignore
                        raise TerminateTaskGroup()
                    tg.create_task(stop_benchmark())
            except* TerminateTaskGroup:
                pass # stop button pressed
    except asyncio.TimeoutError:
        pass
    except Exception as e:
        if C is not None:
            with dcg.Window(C, modal=True):
                dcg.Text(C, value=f"Error starting benchmark: {e}")
                dcg.Text(C, value=traceback.format_exc())
        pass
    finally:
        if bench_C is not None:
            # Collect and display benchmark statistics in a modal window
            if 'buffers' in locals() and 'metadata' in locals():
                stats = []
                for i, ((buffer_x, buffer_y), (short, long)) in enumerate(zip(buffers, metadata)):
                    values = buffer_y.get()
                    if len(values) > 0:
                        avg_val = sum(values) / len(values)
                        max_val = max(values)
                        min_val = min(values)
                        stats.append((short, long, avg_val, min_val, max_val, len(values)))

                # Helper function to format values in a human-readable way
                def format_value(value):
                    if value < 1000:
                        return f"{value:.2f}"
                    elif value < 1_000_000:
                        return f"{value/1000:.1f}k"
                    elif value < 1_000_000_000:
                        return f"{value/1_000_000:.1f}M"
                    else:
                        return f"{value/1_000_000_000:.1f}B"
                
                # Create a modal window with the results
                C = sender.context
                if summary_window is None:
                    summary_window = dcg.Window(C, label="Benchmark Summary", modal=True, autosize=True, no_open_over_existing_popup=False)
                else:
                    # Append to previous results
                    summary_window.show = True
                    summary_window.focus()

                with summary_window:
                    dcg.Text(C, value=f"Summary for: {benchmark.short_description}")
                    
                    # Create a table for the results
                    table = dcg.Table(C, header=True, flags=dcg.TableFlag.BORDERS | dcg.TableFlag.SIZING_STRETCH_SAME)
                    
                    # Set column headers
                    table.col_config[0].label = "Metric"
                    table.col_config[1].label = "Average (ops/s)"
                    table.col_config[2].label = "Min (ops/s)"
                    table.col_config[3].label = "Max (ops/s)"
                    table.col_config[4].label = "Samples"
                    
                    # Add data rows
                    for short, long, avg, min_val, max_val, samples in stats:
                        with table.next_row:
                            dcg.Text(C, value=short)
                            with dcg.Tooltip(C):
                                dcg.Text(C, value=long)

                            # Format average value with tooltip showing exact number
                            avg_formatted = dcg.Text(C, value=format_value(avg))
                            with dcg.Tooltip(C, target=avg_formatted):
                                dcg.Text(C, value=f"Exact: {avg:.2f}")
                            
                            # Format min value with tooltip
                            min_formatted = dcg.Text(C, value=format_value(min_val))
                            with dcg.Tooltip(C, target=min_formatted):
                                dcg.Text(C, value=f"Exact: {min_val:.2f}")
                            
                            # Format max value with tooltip
                            max_formatted = dcg.Text(C, value=format_value(max_val))
                            with dcg.Tooltip(C, target=max_formatted):
                                dcg.Text(C, value=f"Exact: {max_val:.2f}")

                            dcg.Text(C, value=str(samples))
                            with dcg.Tooltip(C):
                                dcg.Text(C, value="This is the number of batches.\nActual number of ops is higher.")
            if "stop_button" in locals():
                stop_button.delete_item()

            # Close the benchmark context
            bench_C.viewport.children = []
            bench_C.running = False
            bench_C.viewport.visible = False
            # Process the viewport events.
            context_pool.submit(lambda: bench_C.viewport.wait_events(timeout_ms=0))


async def ui_loop(viewport: dcg.Viewport):
    """
    Main UI loop that processes events and renders frames.
    
    The main difference with run_viewport_loop (asyncio_helpers)
    is that it pauses when a benchmark is running.
    """
    global benchmarks_running
    while viewport.context.running:
        # Check if there are events waiting to be processed
        if viewport.wait_for_input:
            # Note: viewport.wait_for_input must be set to True
            # for wait_events to not always return True
            has_events = viewport.wait_events(timeout_ms=0)
        else:
            has_events = True

        # Render a frame if there are events
        if has_events:
            if not viewport.render_frame():
                # frame needs to be re-rendered
                # we still yield to allow other tasks to run
                await asyncio.sleep(0)
                continue

        await asyncio.sleep(0.2 if benchmarks_running else 0.01)


def create_benchmark_theme(C: dcg.Context):
    """Create a modern gray theme for the benchmarking application."""
    # Create main theme list
    theme = dcg.ThemeList(C)
    
    # Colors - using a refined palette of grays with subtle blue accents
    with theme:
        # Base colors
        dcg.ThemeColorImGui(C,
            # Window and background colors
            window_bg=(45, 45, 48),           # Dark gray background
            child_bg=(40, 40, 43),            # Slightly darker for child windows
            popup_bg=(50, 50, 53),            # Slightly lighter for popups
            border=(60, 60, 70),             # Subtle border
            modal_window_dim_bg=(30, 30, 35, 100),      # Dim background for modal windows
            
            # Text colors
            text=(220, 220, 225),            # Light gray text
            text_disabled=(140, 140, 145),    # Disabled text
            
            # Interactive element colors
            button=(60, 60, 70),             # Dark button
            button_hovered=(80, 85, 95),      # Hover state with slight blue tint
            button_active=(70, 75, 85),       # Active state
            
            # Frame colors for inputs, etc.
            frame_bg=(55, 55, 60),            # Input background
            frame_bg_hovered=(65, 65, 75),     # Hovered input
            frame_bg_active=(75, 75, 85),      # Active input
            
            # Headers (for TreeNode, etc.)
            header=(60, 65, 80),             # Header with slight blue tint
            header_hovered=(70, 75, 90),      # Hovered header
            header_active=(80, 85, 100),      # Active header
            
            # Title bar
            title_bg=(45, 48, 58),            # Title background with blue tint
            title_bg_active=(50, 55, 70),      # Active title with stronger blue
            title_bg_collapsed=(40, 43, 53),   # Collapsed title
            
            # Tables
            table_header_bg=(55, 60, 75),      # Table header with blue tint
        )
        
        # Styles
        dcg.ThemeStyleImGui(C,
            # Rounding
            window_rounding=4.0,              # Rounded window corners
            frame_rounding=4.0,               # Rounded frames
            popup_rounding=4.0,               # Rounded popups
            scrollbar_rounding=3.0,           # Rounded scrollbars
            grab_rounding=3.0,                # Rounded grab handles
            tab_rounding=4.0,                 # Rounded tabs
            
            # Sizing and spacing
            window_padding=(12, 12),          # More padding for windows
            frame_padding=(8, 4),             # Padding for frames
            item_spacing=(8, 6),              # Space between items
            item_inner_spacing=(6, 4),         # Inner item spacing
            cell_padding=(6, 3),              # Cell padding for tables
            
            # Alignment
            button_text_align=(0.5, 0.5),      # Center button text
            
            # Borders
            frame_border_size=1.0,             # Subtle border for frames
        )
    return theme


def setup_ui(C: dcg.Context):
    """Setup the UI visuals"""
    ## For a simple viewport visual
    #main_window = dcg.Window(C, label="Benchmarking Suite", primary=True, no_scrollbar=True, no_scroll_with_mouse=True)

    ## Custom viewport visual
    # Here we demonstrate a custom viewport decoration
    C.viewport.decorated = False
    C.viewport.clear_color = (30, 30, 35, 100)  # Transparent Dark background color -> will be used for borders
    border_size = "3*dpi"
    title_theme = dcg.ThemeList(C)
    with title_theme:
        # Title bar theme
        dcg.ThemeColorImGui(C,
            window_bg=(30, 30, 35, 255),  # Dark background for title bar
            text=(230, 240, 255),         # Light text color for title
        )
        dcg.ThemeStyleImGui(C,
            window_border_size=0,
            window_rounding=0
        )
    title_bar = dcg.Window(C, x=border_size, y=border_size,
                           width="viewport.width - 2 *"+border_size,
                           height="80*dpi",
                           no_scrollbar=True, no_move=True, no_resize=True, no_title_bar=True,
                           theme=title_theme)
    with title_bar:
        with dcg.DrawInWindow(C, x=0, y=0, width="fillx", height="filly", relative=True):
            dcg.DrawTextQuad(C, text="DearCyGui Performance Benchmarks",
                             p1=(0, 1), p2=(1, 1), p3=(1, 0), p4=(0, 0),
                             preserve_ratio=True)
        # attach a large font to the title bar
        glyphset = dcg.make_extended_latin_font(size=55)
        font_texture = dcg.FontTexture(C)
        font_texture.add_custom_font(glyphset)
        font_texture.build()
        title_bar.font = font_texture[0]
        # Close button
        def close(sender):
            """Close the application when the close button is clicked."""
            sender.context.running = False
        with dcg.DrawInWindow(C, x="parent.x3 - 30*dpi", y="10*dpi",
                              width="20*dpi", height="20*dpi", relative=True, button=True,
                              callback=close) as close_button:
            # dark X
            dcg.DrawLine(C, p1=(0, 0), p2=(1, 1), color=(0, 0, 0), thickness=-2)
            dcg.DrawLine(C, p1=(0, 1), p2=(1, 0), color=(0, 0, 0), thickness=-2)

    def make_hit_map(sender, target: dcg.Window, close_button=close_button) :
        """Create a hit map for custom decoration."""
        # Create hit test surface that defines draggable and resizable areas
        # Values: 0=normal, 1=top resize, 2=left resize, 4=bottom resize, 8=right resize
        # 15=draggable area, 3/6/9/12=corners

        # Create need to recreate it when the dpi changes.
        # Before viewport initialization, dpi may not be known.
        prev_dpi = getattr(make_hit_map, 'prev_dpi', None)
        prev_maximized = getattr(make_hit_map, 'prev_maximized', None)
        if prev_dpi is not None and prev_dpi == C.viewport.dpi and prev_maximized == C.viewport.maximized:
            return # up to date
        make_hit_map.prev_dpi = C.viewport.dpi
        make_hit_map.prev_maximized = C.viewport.maximized

        # target is title_bar
        if C.viewport.maximized:
            border_width = 0
            if prev_maximized is not True:
                target.x = "0"
                target.y = "0"
                target.width = "viewport.width"
        else:
            border_width = int(3 * C.viewport.dpi)
            border_size = "3*dpi"
            if prev_maximized is not False:
                target.x = border_size
                target.y = border_size
                target.width = "viewport.width - 2 * "+border_size

        title_bar_height = int(target.state.rect_size.y)
        # center_width doesn't matter as long as it is large enough
        center_width = 2 * (title_bar_height + border_width)

        hit_test = np.zeros((border_width + title_bar_height + center_width,
                                  2 * border_width + center_width + 1), dtype=np.uint8)
        # Set title bar as draggable area (value 15)
        hit_test[border_width:(border_width+title_bar_height), border_width:hit_test.shape[1]-border_width] = 15
        
        # Set resizable borders
        for i in range(hit_test.shape[0]):
            for j in range(hit_test.shape[1]):
                if i < border_width:  # Top border (top of title bar)
                    hit_test[i, j] |= 1
                elif i >= hit_test.shape[0] - border_width:  # Bottom border
                    hit_test[i, j] |= 4

                if j < border_width:  # Left border
                    hit_test[i, j] |= 2
                elif j >= hit_test.shape[1] - border_width:  # Right border
                    hit_test[i, j] |= 8

        # Remove the close button area from the draggable area
        button_size = close_button.state.rect_size
        close_button_x = int(close_button.state.pos_to_viewport.x)
        close_button_y = int(close_button.state.pos_to_viewport.y)
        close_button_width = int(button_size.x)
        close_button_height = int(button_size.y)
        # Reposition x (we use a smaller hit test surface)
        pixels_to_border = C.viewport.pixel_width - close_button_x - close_button_width
        if pixels_to_border >= 0:
            close_button_x = hit_test.shape[1] - close_button_width - pixels_to_border
            if close_button_x >= 0:
                hit_test[close_button_y:close_button_y+close_button_height,
                         close_button_x:close_button_x+close_button_width] = 0
    
        # Apply the hit test surface to define window behavior
        target.context.viewport.hit_test_surface = hit_test
    title_bar.handlers = [dcg.ResizeHandler(C, callback=make_hit_map)]

    dcg.os.set_application_metadata(name="DCG Performance Benchmarks")

    main_window = dcg.Window(C, x=title_bar.x.x0, y=title_bar.y.y3,
                             width=title_bar.width,
                             height="viewport.height-self.y0-self.x0", # x0 is equal to border_size is any.
                             no_scrollbar=True, no_move=True,
                             no_resize=True, no_title_bar=True,
                             theme=dcg.ThemeStyleImGui(C, window_rounding=0, window_border_size=0))
    ## End of custom viewport decoration

    # Header section with title and description
    header = dcg.VerticalLayout(C, parent=main_window)
    selection = dcg.ChildWindow(C, parent=main_window, border=True, width=-1)
    footnotes = dcg.VerticalLayout(C, parent=main_window)

    selection.height = "filly-footnotes.height-theme.item_spacing.y"

    with header:
        with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.CENTER):
            dcg.Text(C, value="DCG Performance Benchmarks", color=(230, 240, 255))
        with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.CENTER):
            dcg.Text(C, value="Select a benchmark to evaluate performance metrics")
        dcg.Separator(C)
        dcg.Spacer(C)
        dcg.Spacer(C)
        
    # Organize benchmarks in a scrollable area
    prev_category = None
    with selection:
        for benchmark in benchmarks_list:
            if not isinstance(benchmark, BenchmarkInfo):
                continue
            cur_category = benchmark.category
            if prev_category != cur_category:
                # Add a category header if it changed
                if prev_category is not None:
                    dcg.Separator(C)
                dcg.Text(C, value=f"Category: {cur_category}", color=(200, 200, 220), scaling_factor=1.5)
                prev_category = cur_category
            
            # Create a more visually appealing button
            button = dcg.Button(C, label=benchmark.short_description,
                                user_data=benchmark,
                                callback=start_benchmark,
                                width=-1,  # Full width buttons
                                height=35)  # Taller buttons for better visibility
            
            with dcg.Tooltip(C, target=button):
                dcg.Text(C, value=benchmark.long_description)
        
    # Footer with info
    with footnotes:
        dcg.Separator(C)
        with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.JUSTIFIED):
            dcg.Text(C, value=" 2025, DCG Development Team", color=(180, 180, 190))
            dcg.Text(C, value="Version 1.0 ", color=(160, 160, 180))


def start_ui(**kwargs):
    """Setup and start the UI event loop."""
    context_pool = AsyncThreadPoolExecutor()
    def initialize_context(wait_for_input=True, **kwargs):
        """Initialize the context with the given parameters."""
        # Create a new context and set the viewport
        C = dcg.Context()
        C.queue = AsyncThreadPoolExecutor()
        setup_ui(C)
        C.viewport.initialize(wait_for_input=wait_for_input, **kwargs)
        C.viewport.theme = create_benchmark_theme(C)
        # We will use this to run other UI loops in the same thread.
        C.viewport.user_data = context_pool
        return C

    # Start the Context in an async thread pool executor.
    initialize_future = context_pool.submit(initialize_context, **kwargs)
    C = initialize_future.result()
    
    context_pool.submit(ui_loop, C.viewport).result()

if __name__ == "__main__":
    # Start the UI loop
    start_ui(
        title="Benchmarking Demos",
        width=800,
        height=600,
        wait_for_input=True
    )
