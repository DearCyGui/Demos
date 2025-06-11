import asyncio
from demo_utils import documented, democode, push_group, pop_group, launch_demo, demosection
import dearcygui as dcg
from dearcygui.utils.asyncio_helpers import run_viewport_loop, AsyncPoolExecutor, AsyncThreadPoolExecutor
import gc
import math
import psutil
import random
import threading
import time
import sys



# decorators:
# - documented: the description (markdown) is displayed
# - democode: the code is displayed and can edited (and run again)
# - demosection: the section is displayed in the table of contents,
#    the section name is extracted from the function name.

@demosection
@documented
def _basics(C: dcg.Context):
    """
    # Basics

    In this section, we will cover the basics of DearCygui:
    - How to create and configure an item
    - How to manipulate the item tree
    - How to configure the context and viewport
    - How to create a window
    - How to create a menu bar
    - Various UI containers
    - Handlers
    - How to manage item positioning and size 
    - How to change the style of an item
    """
    pass


@demosection(dcg.Text, dcg.Button, dcg.Checkbox, dcg.Slider, dcg.InputText)
@documented
@democode
def _creating_basic_items(C: dcg.Context):
    """
    ## Creating Basic Items
    
    UI elements in DearCyGui are built by instantiating Python object.
    All UI items share these common features:
    
    - They take the Context as their first parameter
    - They can be configured using keyword arguments or by setting properties after creation
    - They return a reference that you can use to interact with them
    
    In this example, we'll create basic interface items:
    - Text: Displays static text
    - Button: A clickable button that triggers a callback function
    - Checkbox: A togglable option
    - Slider: A draggable control for setting numeric values
    """
    # Creating a simple text display
    dcg.Text(C, value="Hello, this is a text item!")
    
    # Creating a button with a callback function
    def button_callback(sender, target, data):
        dcg.Text(C, value=f"Button was clicked!", parent=target.parent)
        target.label = "Clicked!"
    
    dcg.Button(C, 
               label="Click Me", 
               callback=button_callback)
    with dcg.Tooltip(C):
        dcg.Text(C, value="This button will change its label when clicked")
    
    # Creating a checkbox
    def checkbox_callback(sender, target, data):
        dcg.Text(C, value=f"Checkbox value changed to: {data}", parent=target.parent)
    
    dcg.Checkbox(C, 
                 label="Toggle me", 
                 callback=checkbox_callback)
    
    # Creating a slider
    def slider_callback(sender, target, data):
        dcg.Text(C, value=f"Slider value changed to: {data}", parent=target.parent)
    
    dcg.Slider(C, 
               label="Adjust me", 
               min_value=0, 
               max_value=100, 
               format="int",
               callback=slider_callback)
    
    # Creating an input field
    dcg.InputText(C, 
                  label="Enter text", 
                  hint="Type here...")


@demosection(dcg.Button, dcg.Text)
@documented
@democode
def _configuring_items(C: dcg.Context):
    """
    ## Configuring Items
    
    DearCyGui items support many configuration options
    to tune how they behave and how they appear.
    The can be configured in two ways:
    
    1. **During creation** by passing keyword arguments
    2. **After creation** by setting attributes on the item reference

    Every property can be both read and written at any time.
    
    Most properties have sensible defaults, so you only need to set
    the ones you want to change.
    """
    # Method 1: Configure during creation
    button1 = dcg.Button(C, 
                         label="Configured during creation", 
                         width=300,
                         height=50,
                         enabled=True)
    
    # Method 2: Configure after creation
    button2 = dcg.Button(C, label="Default Button")
    
    # Now let's modify its properties
    button2.width = 300
    button2.height = 50
    button2.label = "Configured after creation"
    
    # You can also read properties at any time
    dcg.Text(C, value=f"Button2 width: {float(button2.width)}")
    
    # Some properties can affect appearance and behavior
    dcg.Button(C, 
               label="Disabled Button",
               enabled=False)
    
    dcg.Button(C, 
               label="Invisible Button (you can't see me)",
               show=False)
    
    # Creating an item with a callback and then changing it
    def original_callback(sender, target, data):
        dcg.Text(C, value="Original callback")
    
    def new_callback(sender, target, data):
        dcg.Text(C, value="New callback")
        target.label = "Callback changed!"
    
    button3 = dcg.Button(C, 
                         label="Change my callback",
                         callback=original_callback)
    
    # Change the callback
    button3.callback = new_callback


@demosection(dcg.ChildWindow, dcg.Text, dcg.Button)
@documented
@democode
def _item_tree(C: dcg.Context):
    """
    ## The Item Tree
    
    DearCyGui organizes UI elements in a **tree structure**. Each item can have:
    
    - A **parent** item that contains it
    - Multiple **children** items contained within it
    
    There are several ways to manage parent-child relationships:
    
    1. Using the `with` statement (most common)
    2. Setting the `parent` property when creating an item
    3. Directly manipulating the `parent` or `children` attributes
    
    The viewport is the ultimate root of the item tree.
    """
    # Method 1: Using the "with" statement
    with dcg.ChildWindow(C, width=-1, height=200, label="Parent Container"):
        # These items will automatically become children of the ChildWindow
        dcg.Text(C, value="I'm a child of the ChildWindow (using 'with')")
        dcg.Button(C, label="Me too!")
    
    # Method 2: Setting parent during creation
    parent_container = dcg.ChildWindow(C, width=-1, height=200, label="Another Parent")
    dcg.Text(C, value="I'm a child (using parent parameter)", parent=parent_container)
    dcg.Button(C, label="Same here", parent=parent_container)
    
    # Method 3: Setting parent after creation
    another_parent = dcg.ChildWindow(C, width=-1, height=200, label="Third Parent")
    text_item = dcg.Text(C, value="I'll be moved", attach=False)  # attach=False prevents automatic attachment
    button_item = dcg.Button(C, label="Me too", attach=False)
    
    # Now move the items to the parent
    text_item.parent = another_parent
    button_item.parent = another_parent
    
    # Method 4: Using the children list
    fourth_parent = dcg.ChildWindow(C, width=-1, height=200, label="Fourth Parent")
    floating_text = dcg.Text(C, value="Adding via children list", attach=False)
    
    # Append to the parent's children list
    fourth_parent.children += [floating_text]


@demosection(dcg.Window, dcg.Viewport)
@documented
def _windows(C: dcg.Context):
    """
    ## Windows
    
    Windows are containers that can be moved, resized, collapsed, and closed by the user.
    
    In DearCyGui, the `Window` class creates a window within the viewport. Windows have
    many configuration options to control their appearance and behavior.
    
    Windows serve as natural containers for other UI elements.
    
    **Note**: Windows automatically attach to the viewport, not to other windows.

    ### Supported attributes:
    
    #### Layout controls
    - `autosize`: Window automatically sizes itself to fit its contents
    - `min_size`: Minimum size of the window (width, height)
    - `max_size`: Maximum size of the window (width, height)
    
    #### Window behavior
    - `no_resize`: Disable window resizing
    - `no_move`: Prevent window from being moved
    - `no_collapse`: Disable window collapsing
    - `collapsed`: Initial collapsed state
    - `primary`: Sets this as the main application window
    - `modal`: Window blocks interaction with other windows
    - `popup`: Window appears as a popup
    
    #### Window appearance
    - `no_title_bar`: Hide the window title bar
    - `no_background`: Make window background transparent
    - `has_close_button`: Show or hide the close button
    - `no_saved_settings`: Don't save window position/size between sessions
    
    #### Scrolling
    - `no_scrollbar`: Hide window scrollbars
    - `no_scroll_with_mouse`: Disable mouse wheel scrolling
    - `horizontal_scrollbar`: Show horizontal scrollbar
    - `always_show_vertical_scrollvar`: Always show vertical scrollbar
    - `always_show_horizontal_scrollvar`: Always show horizontal scrollbar
    
    #### Input and focus
    - `no_mouse_inputs`: Window ignores mouse inputs
    - `no_keyboard_inputs`: Window ignores keyboard inputs
    - `no_focus_on_appearing`: Don't focus window when it appears
    - `no_bring_to_front_on_focus`: Don't bring window to front when focused
    
    #### Other
    - `menubar`: Show a menu bar at the top even if there is no menu attached
    - `unsaved_document`: Mark window as containing unsaved changes
    - `disallow_docking`: Prevent window from being used with docking
    - `no_open_over_existing_popup`: Don't open over existing popups
    - `on_close`: Callback function triggered when window is closed
    """

@demosection(dcg.MenuBar, dcg.Menu, dcg.MenuItem, dcg.ChildWindow, dcg.Separator)
@documented
@democode
def _menu_bars(C: dcg.Context):
    """
    ## Menu Bars and Menus
    
    Menu bars are a standard UI element used to organize commands and options.
    
    DearCyGui provides:
    - `MenuBar`: The container that holds all menus, typically at the top of a window
        It can be attached to a viewport, to a window or a child window.
    - `Menu`: A dropdown list that contains menu items
    - `MenuItem`: A clickable option in a menu

    Menus can be nested to create submenus. Each menu item can have a callback
    function that is executed when the item is clicked.
    """
    # Create a window with a menu bar
    with dcg.ChildWindow(C, 
                    label="Child Window with Menu Bar",
                    width=500, 
                    height=300,
                    x=100, y=100):
        
        # Create the menu bar
        with dcg.MenuBar(C):
            
            # File menu
            with dcg.Menu(C, label="File"):
                dcg.MenuItem(C, label="New", callback=lambda s, t, d: print("New file"))
                dcg.MenuItem(C, label="Open", callback=lambda s, t, d: print("Open file"))
                dcg.MenuItem(C, label="Save", callback=lambda s, t, d: print("Save file"))
                
                # Create a submenu
                with dcg.Menu(C, label="Export As"):
                    dcg.MenuItem(C, label="PDF", callback=lambda s, t, d: print("Export as PDF"))
                    dcg.MenuItem(C, label="PNG", callback=lambda s, t, d: print("Export as PNG"))
                
                dcg.Separator(C)  # Add a separator line
                dcg.MenuItem(C, label="Exit", callback=lambda s, t, d: print("Exit"))
            
            # Edit menu
            with dcg.Menu(C, label="Edit"):
                dcg.MenuItem(C, label="Cut", callback=lambda s, t, d: print("Cut"))
                dcg.MenuItem(C, label="Copy", callback=lambda s, t, d: print("Copy"))
                dcg.MenuItem(C, label="Paste", callback=lambda s, t, d: print("Paste"))
            
            # Checkable menu items
            with dcg.Menu(C, label="View"):
                dcg.MenuItem(C, label="Show Toolbar", check=True, 
                            callback=lambda s, t, d: print(f"Toolbar visible: {d}"))
                dcg.MenuItem(C, label="Show Statusbar", check=True, value=True,
                            callback=lambda s, t, d: print(f"Statusbar visible: {d}"))
        
        # Rest of window content
        dcg.Text(C, value="Try clicking on the menu items above!")


@demosection(dcg.VerticalLayout, dcg.HorizontalLayout, dcg.ChildWindow, dcg.CollapsingHeader, dcg.TreeNode, dcg.TabBar, dcg.Tab)
@documented
@democode
def _containers(C: dcg.Context):
    """
    ## UI Containers
    
    Containers help organize and arrange UI elements. DearCyGui provides several container types:
    
    - **VerticalLayout**: Arranges items vertically (top to bottom)
    - **HorizontalLayout**: Arranges items horizontally (left to right)
    - **ChildWindow**: A scrollable container within a window
    - **CollapsingHeader**: A collapsible section that can be expanded/collapsed
    - **TreeNode**: A hierarchical collapsible item, useful for tree structures
    - **TabBar/TabItem**: Organizes content into tabs
    - **Layout**: A generic container, typically used by subclassing it when creating custom widgets.
    
    Containers help create structured and responsive interfaces.
    """
    # Horizontal Layout - arranges items side by side
    dcg.Text(C, value="HorizontalLayout Example:")
    with dcg.HorizontalLayout(C):
        dcg.Button(C, label="Button 1", width=100, height=30)
        dcg.Button(C, label="Button 2", width=100, height=30)
        dcg.Button(C, label="Button 3", width=100, height=30)
    
    dcg.Spacer(C, height=10)
    
    # Vertical Layout - arranges items top to bottom (default behavior)
    dcg.Text(C, value="VerticalLayout Example:")
    with dcg.VerticalLayout(C):
        dcg.Button(C, label="Button A", width=200)
        dcg.Button(C, label="Button B", width=200)
        dcg.Button(C, label="Button C", width=200)
    
    dcg.Spacer(C, height=10)
    
    # Child Window - creates a scrollable area
    dcg.Text(C, value="ChildWindow Example:")
    with dcg.ChildWindow(C, width=300, height=100, border=True):
        for i in range(10):
            dcg.Text(C, value=f"Item {i+1}")
    
    dcg.Spacer(C, height=10)
    
    # Collapsing Header - can be expanded or collapsed
    dcg.Text(C, value="CollapsingHeader Example:")
    with dcg.CollapsingHeader(C, label="Click to expand/collapse"):
        dcg.Text(C, value="This content can be hidden")
        dcg.Button(C, label="Hidden Button")
    
    dcg.Spacer(C, height=10)
    
    # Tree Node - hierarchical collapsible items
    dcg.Text(C, value="TreeNode Example:")
    with dcg.TreeNode(C, label="Parent Node"):
        dcg.Text(C, value="Child Item 1")
        dcg.Text(C, value="Child Item 2")
        with dcg.TreeNode(C, label="Nested Node"):
            dcg.Text(C, value="Nested Child Item")
    
    dcg.Spacer(C, height=10)
    
    # Tab Bar - organizes content into tabs
    dcg.Text(C, value="TabBar Example:")
    with dcg.TabBar(C):
        with dcg.Tab(C, label="Tab 1"):
            dcg.Text(C, value="Content for Tab 1")
            dcg.Button(C, label="Tab 1 Button")
        
        with dcg.Tab(C, label="Tab 2"):
            dcg.Text(C, value="Content for Tab 2")
            dcg.Checkbox(C, label="Tab 2 Checkbox")
        
        with dcg.Tab(C, label="Tab 3"):
            dcg.Text(C, value="Content for Tab 3")


@demosection(dcg.GotHoverHandler, dcg.LostHoverHandler, dcg.ClickedHandler, dcg.ActivatedHandler, dcg.DeactivatedHandler, dcg.HandlerList, dcg.HandlerListOP)
@documented
@democode
def _handlers(C: dcg.Context):
    """
    ## Handlers
    
    Handlers let UI elements respond to events. Unlike callbacks that run when a specific action occurs
    (like clicking a button), handlers can monitor continuous state changes like hovering or focusing.
    
    Key concepts:
    
    - **Handlers** are attached to items using the `handlers` property
    - Multiple handlers can be attached to a single item
    - Handlers can be combined for complex conditions
    - Built-in handlers include: `HoverHandler`, `ClickedHandler`, `FocusHandler`, etc.
    
    Handlers help create interactive, dynamic interfaces with minimal performance impact.

    Usage of handlers and the various types of handlers are explained in more depth
    in the related sections of this demo.
    """
    # Create a text element that will display status information
    status_text = dcg.Text(C, value="Hover over or click elements to see events")
    
    # Basic hover handler
    button_with_hover = dcg.Button(C, label="Hover over me")
    
    def hover_callback(sender, target):
        status_text.value = "Button is being hovered!"
    
    def lost_hover_callback(sender, target):
        status_text.value = "No longer hovering over button"
    
    # Add hover handlers to the button
    button_with_hover.handlers += [
        dcg.GotHoverHandler(C, callback=hover_callback),
        dcg.LostHoverHandler(C, callback=lost_hover_callback)
    ]
    
    # Click handler example
    button_with_click = dcg.Button(C, label="Click me")
    
    def clicked_callback(sender, target):
        status_text.value = "Button was clicked!"
    
    button_with_click.handlers += [
        dcg.ClickedHandler(C, callback=clicked_callback)
    ]
    
    # Active handler - triggers when an item is active (being interacted with)
    input_with_active = dcg.InputText(C, label="Type here")
    
    def active_callback(sender, target):
        status_text.value = "Input field is active (being edited)"
    
    def inactive_callback(sender, target):
        status_text.value = "Input field is no longer active"
    
    input_with_active.handlers += [
        dcg.ActivatedHandler(C, callback=active_callback),
        dcg.DeactivatedHandler(C, callback=inactive_callback)
    ]
    
    # Combining handlers with HandlerList
    # This creates a complex condition (hover AND visible)
    complex_button = dcg.Button(C, label="Complex handler")
    
    def complex_handler_callback(sender, target):
        status_text.value = "Complex condition met (hover AND ctrl key press)"
    
    # Create a handler list that requires ALL conditions (AND)
    combined_handler = dcg.HandlerList(C, op=dcg.HandlerListOP.ALL, callback=complex_handler_callback)
    with combined_handler:
        dcg.HoverHandler(C)  # Is the item hovered?
        dcg.KeyPressHandler(C, key=dcg.Key.LEFTCTRL)  # Is ctrl pressed ?
    
    # Attach the combined handler to the button
    complex_button.handlers += [combined_handler]
    
    # Toggle visibility to demonstrate the complex handler
    toggle_button = dcg.Button(C, label="Toggle visibility of complex button")
    
    def toggle_visibility(sender, target, data):
        complex_button.show = not complex_button.show
    
    toggle_button.callback = toggle_visibility

push_group("Asyncio")

@demosection(dcg.Viewport, dcg.Context, \
             run_viewport_loop, \
             AsyncPoolExecutor, \
             AsyncThreadPoolExecutor)
@documented
def _asyncio_introduction(C: dcg.Context):
    """
    ## Asyncio Integration

    The `dearcygui.utils.asyncio_helpers` module provides tools to integrate
    DearCyGui with asyncio, allowing you to run background tasks without blocking the UI.

    The interest of using asyncio with DearCyGui are:
    - Integrate with existing asyncio applications and libraries
    - Running one or several light background tasks with time dependencies.
    - Simplifying the management of applications that could spawn multiple viewports.

    If you want to run DearCyGui entirely in an asyncio event loop, two components are provided:
    - `run_viewport_loop`: A coroutine that runs the DearCyGui's `render_frame` loop asynchronously.
        This allows you to run the DearCyGui event and rendering loop alongside your asyncio tasks.
    - `AsyncPoolExecutor`: A replacement for the Context queue that runs tasks in the target (or current) event loop.
        Setting this executor in the `Context` allows you to run the callbacks and the handlers
        into your asyncio event loop, instead of in a separate thread.

    When using `run_viewport_loop`, you probably want to set the `Context.queue`
    to an `AsyncPoolExecutor` instance, in order to have all DearCyGui callbacks
    and handlers run in the same event loop as your other asyncio tasks.

    One noticeable advantage of `AsyncPoolExecutor` is that the callbacks and handlers
    are run in the same thread as the rendering. This is important for some operations
    that require the execution to occur in the thread the context was created in.

    Operations that require running in the thread that created the context:
    - Creating a new context (to have multiple viewports)
    - Running rendering
    - Some `dcg.os` functions
    - Some viewport attributes and methods

    `AsyncPoolExecutor` is not the default executor because while it can be
    advantageous to run in the main thread for the above reasons, it is more
    sensitive to the heaviness of the tasks submitted to it. Indeed with the default
    executor if a callback takes too long to run, the UI rendering is not blocked. Only
    the callback processing is delayed. Meanwhile with `AsyncPoolExecutor`, if a callback
    takes too long to run (heavy computations such as numpy operations), the UI rendering
    is blocked until the callback finishes. Be careful ! Besides that, there is not a huge
    performance difference as the rendering itself is very lightweight.

    The module also provides `AsyncThreadPoolExecutor`: A
    thread pool executor that runs tasks in a separate thread. The main difference
    with the default executor (which also runs tasks in a separate thread) is that
    `AsyncThreadPoolExecutor` is designed to work with asyncio and can run `async def`
    callbacks. It can be used as a drop-in replacement for the standard Context queue
    and adds only a minor overhead compared to the default executor.

    The main interest of `AsyncThreadPoolExecutor` is it allows running
    `async def` callbacks, which can be useful for callbacks that need to
    perform asynchronous operations without blocking the UI. `AsyncPoolExecutor` also
    supports `async def` callbacks, running them in the main thread rather than in a separate thread.

    This demo runs using `run_viewport_loop` and `AsyncPoolExecutor`, and thus we can demonstrate
    in this section the interest of async callbacks and running callbacks in the main thread.
    """

@demosection(dcg.DrawArrow)
@documented
@democode
def _timed_updates(C: dcg.Context):
    """
    ## Timed Updates with Async Callbacks

    Any heavy computation in callbacks should be prohibited, as it
    will block callback processing, and in the worst case
    block the UI rendering (when using `AsyncPoolExecutor`).
    Such heavy computations should be run in a separate thread.

    That said, spawning threads for lightweight, but long-running
    operations is not ideal. That's where asyncio comes in handy.

    This section demonstrates how to use async callbacks to
    create many objects with timed updates without blocking the UI.

    Notice how with a huge number of arrows, the UI becomes less
    responsible with `AsyncPoolExecutor`, while it remains
    responsive with `AsyncThreadPoolExecutor`. This is because
    `AsyncPoolExecutor` runs the callbacks in the same thread
    as the rendering.

    Note due to the GIL, on non-freethreaded builds,
    `AsyncThreadPoolExecutor` will have trouble executing
    many arrows due to GIL conflicts with the rendering thread.
    """
    number_of_arrows = 0
    def number_of_arrows_callback(sender, target: dcg.Text):
        nonlocal number_of_arrows
        target.value = f"Number of arrows: {number_of_arrows}"
    dcg.Text(C, value="Number of arrows: 0",
             handlers=dcg.RenderHandler(C, callback=number_of_arrows_callback))

    async def update_cpu_usage(sender, target: dcg.ProgressBar):
        process = psutil.Process()
        while target.state.visible:
            # Update CPU usage
            cpu_percent = process.cpu_percent()
            target.value = cpu_percent / 100.
            target.overlay = f"{cpu_percent:.2f}% CPU Usage"
            C.viewport.wake()
            await asyncio.sleep(0.5)  # Update every half-second

    async def update_fps_usage(sender, target: dcg.ProgressBar):
        last_frame_count = C.viewport.metrics["frame_count"]
        while target.state.visible:
            # Update FPS
            current_frame_count = C.viewport.metrics["frame_count"]
            fps = current_frame_count - last_frame_count  
            target.value = min(fps / 100., 1.0)  # Normalize to 100fps max
            target.overlay = f"{fps} FPS"
            last_frame_count = current_frame_count
            C.viewport.wake()
            await asyncio.sleep(1.)  # Update every second

    main_loop = asyncio.get_event_loop()
    def select_executor(sender, target, value: str):
        if value == "AsyncPoolExecutor":
            C.queue = AsyncPoolExecutor(loop=main_loop)
        else:
            C.queue = AsyncThreadPoolExecutor()

    use_threads = False

    with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.JUSTIFIED):
        dcg.RadioButton(C, items=["AsyncPoolExecutor", "AsyncThreadPoolExecutor"],
                        value="AsyncPoolExecutor",
                        callback=select_executor)
        with dcg.VerticalLayout(C):
            def toggle_gc(sender, target, value: bool):
                if value:
                    gc.disable()
                else:
                    gc.enable()
            dcg.Checkbox(C, label="Disable GC", callback=toggle_gc, value=False)
            with dcg.Tooltip(C):
                dcg.Text(C, value=\
                    "Disabling GC can help with performance and stutter when creating/deleting many items\n"
                    "but can lead to memory leaks if not managed properly.\n"
                    "A compeling alternative is to use gc.collect() when you detect\n"
                    "the program is idle")


            def toggle_switchinterval(sender, target, value: bool):
                if value:
                    sys.setswitchinterval(0.001)  # Set to 1ms
                else:
                    sys.setswitchinterval(0.05)  # Set to 50ms (default)

            dcg.Checkbox(C, label="Mitigate GIL", callback=toggle_switchinterval, value=False)
            with dcg.Tooltip(C):
                dcg.Text(C, value=\
                    "Setting a lower switch interval can help mitigate GIL contention\n"
                    "but can reduce performance for certain tasks.\n"
                    "For a responsive UI, it is recommended to reduce the switch interval\n"
                    "Note for the free-threaded build, this is not needed,\n"
                    "as the GIL is not a problem in that case.\n")

            def toggle_threads(sender, target, value: bool):
                nonlocal use_threads
                use_threads = value

            dcg.Checkbox(C, label="Use threads", callback=toggle_threads, value=False)
            with dcg.Tooltip(C):
                dcg.Text(C, value=\
                    "Using one thread per arrow is suboptimal here, due to the\n"
                    " overhead of thread management. Toggle this option to see\n"
                    " the difference.")

    with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.CENTER):
        cpu_usage = dcg.ProgressBar(C, value=0.0, overlay="0% CPU Usage", width="0.3*fullx")
        dcg.Spacer(C, width="0.1*fullx")
        fps_bar = dcg.ProgressBar(C, value=0.0, overlay="0 FPS", width="0.3*fullx")
        cpu_usage.handlers += [dcg.GotRenderHandler(C, callback=update_cpu_usage)]
        fps_bar.handlers += [dcg.GotRenderHandler(C, callback=update_fps_usage)]

    dcg.Spacer(C, height=50)

    async def create_and_move_arrow(target: dcg.uiItem):
        """
        An async callback that creates an temporary moving arrow below the target item.

        A similar code not using async would need to submit
        a new function to a thread queue, and resubmitting
        every time a new function when the arrow needs to be moved.
        """
        nonlocal number_of_arrows
        C = target.context
        pos = target.state.pos_to_viewport
        pos.x += random.randint(0, int(target.state.rect_size.x))
        pos.y += target.state.rect_size.y + 2  # Position it below the item
        with dcg.ViewportDrawList(C) as arrow_parent:
            arrow = dcg.DrawArrow(C, p1=pos, p2=(pos.x, pos.y + 20), color=(255, 0, 0), thickness=-1.)
        number_of_arrows += 1
        # move the arrow downward then upward three times, then delete it
        for _ in range(3):
            # Move the arrow down
            for i in range(20):
                arrow.p1 = pos + (0, i)
                arrow.p2 = pos + (0, i+20)
                C.viewport.wake()
                await asyncio.sleep(0.01) # never use sleep in a non-async callback.
            # Move the arrow up
            for i in range(20):
                arrow.p1 = pos + (0, 20-i)
                arrow.p2 = pos + (0, 40-i)
                C.viewport.wake()
                await asyncio.sleep(0.01)
        number_of_arrows -= 1
        arrow_parent.delete_item()  # Remove the arrow after the animation
        C.viewport.wake()

    def own_thread(func):
        """
        Decorator to spawn a function in a separate thread
        """
        def wrapper(*args, **kwargs):
            thread = threading.Thread(target=func, args=args, kwargs=kwargs)
            thread.start()
        return wrapper

    @own_thread
    def create_and_move_arrow_threaded(target: dcg.uiItem):
        """
        An async callback that creates an temporary moving arrow below the target item.

        A similar code not using async would need to submit
        a new function to a thread queue, and resubmitting
        every time a new function when the arrow needs to be moved.
        """
        nonlocal number_of_arrows
        C = target.context
        pos = target.state.pos_to_viewport
        pos.x += random.randint(0, int(target.state.rect_size.x))
        pos.y += target.state.rect_size.y + 2  # Position it below the item
        with dcg.ViewportDrawList(C) as arrow_parent:
            arrow = dcg.DrawArrow(C, p1=pos, p2=(pos.x, pos.y + 20), color=(255, 0, 0), thickness=-1.)
        number_of_arrows += 1
        # move the arrow downward then upward three times, then delete it
        for _ in range(3):
            # Move the arrow down
            for i in range(20):
                arrow.p1 = pos + (0, i)
                arrow.p2 = pos + (0, i+20)
                C.viewport.wake()
                time.sleep(0.01)
            # Move the arrow up
            for i in range(20):
                arrow.p1 = pos + (0, 20-i)
                arrow.p2 = pos + (0, 40-i)
                C.viewport.wake()
                time.sleep(0.01)
        number_of_arrows -= 1
        arrow_parent.delete_item()  # Remove the arrow after the animation
        C.viewport.wake()

    async def create_and_move_many_arrows(target: dcg.uiItem):
        """
        An async callback that creates many temporary arrows below the target item.
        """
        nonlocal use_threads
        if use_threads:
            for _ in range(40):
                create_and_move_arrow_threaded(target)
            return
        # Use asyncio.TaskGroup to run multiple tasks concurrently
        async with asyncio.TaskGroup() as tg:
            for _ in range(40):
                tg.create_task(create_and_move_arrow(target))


    with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.CENTER):
        dcg.Button(C, label="Click me to create temporary arrows",
                   callback=create_and_move_many_arrows, repeat=True)
    dcg.Spacer(C, height=50) 

@demosection(dcg.Context, dcg.Viewport)
@documented
@democode
def _multiviewport(C: dcg.Context):
    """
    ## Multiple Viewports
    DearCyGui supports multiple viewports, allowing you to create separate UI contexts
    that can run independently. Each viewport has its own context, allowing you to
    create isolated UI elements that do not interfere with each other.

    Constraints:
    - Objects cannot be moved between contexts. Each base item contains a
       `copy` method which takes a `target_context` parameter to copy between contexts.
    - The `Context` items must all be created in the same thread.
    - Rendering must be done in the same thread as the `Context` was created in.

    Here we demonstrate creating multiple viewports using `AsyncPoolExecutor`.

    Note: You do not **need** to use `AsyncPoolExecutor` or asyncio for multiple viewports, you can
    have a custom loop rendering all your open viewports for instance, and append to them.
    """

    async def create_viewport():
        # Create a new viewport context
        try:
            new_context = dcg.Context()
            new_context.viewport.initialize(width=400, height=300, title="New Viewport")
        except Exception as e:
            with dcg.Window(C, modal=True):
                dcg.Text(C, value=f"Error creating new viewport: {e}")
            return
        
        # Add some items to the new viewport
        with dcg.Window(new_context, primary=True):
            dcg.Text(new_context, value="This is a new viewport!", x=10, y=10)

            with dcg.DrawInWindow(new_context, width="fillx", height="filly"):
                stars = []
                for i in range(20):
                    for j in range(10):
                        star = dcg.DrawStar(new_context,
                                            center=(50+100*i, 50+100*j),
                                            direction=(i + j) * 0.1,  # Rotate based on position
                                            radius=50,
                                            inner_radius=20,
                                            color=(0, 255, 0),
                                            thickness=2.0)
                        stars.append(star)

        async def star_loop(new_context, stars):
            """
            An async loop that updates the star position in the new viewport.
            This demonstrates how to run a separate loop for each viewport.
            """
            while new_context.running:
                # Update the star position randomly
                for star in stars:
                    star.direction += 0.01  # Rotate the star
                new_context.viewport.wake()
                await asyncio.sleep(0.01)  # Sleep to allow other tasks to run

        await asyncio.gather(
            run_viewport_loop(new_context.viewport),  # Run the viewport loop
            star_loop(new_context, stars)  # Run the star animation
        )
        # Hide the viewport right away rather than wait garbage collection
        new_context.viewport.visible = False
        new_context.viewport.wait_events(0.) # process the visibility change

    # Create a button to trigger the creation of a new viewport
    dcg.Button(C, label="Create New Viewport", callback=lambda: create_viewport())


@demosection(dcg.Context, dcg.Viewport)
@documented
@democode
def Programing(C: dcg.Context):
    """
    ## Programing Style
    
    Using asyncio versus normal callbacks for timed animations and updates
    are a matter of preference. It can lead to various code styles.

    Below we demonstrate various styles to achieve the same result:
    - Animation loop using asyncio in a callback
    - Animation loop using a normal callback to start a thread
    - Animation loop using a normal callback and class-based item
    - Animation loop using asyncio not in a callback
    """
    # Make font with huge digits only
    glyphset = dcg.make_extended_latin_font(200)
    reduced_glyphset = dcg.GlyphSet(glyphset.height, glyphset.origin_y)
    for i in range(10):
        reduced_glyphset.add_glyph(ord(str(i)), *glyphset[ord(str(i))])
    font_texture = dcg.FontTexture(C)
    font_texture.add_custom_font(reduced_glyphset)
    font_texture.build()
    font = font_texture[0]

    # 1. Animation loop using asyncio in a callback
    def create_asyncio_callback_clock(width=200, running=threading.Event()):
        with dcg.DrawInWindow(C, width=width, height=width, relative=True) as draw_window:
            # Create the railroad pattern
            railroad_pattern = dcg.Pattern.railroad(C, scale_factor=5)
            
            # Create the visual elements
            arc = dcg.DrawArc(C, center=(0.5, 0.5), radius=(0.4, 0.4), 
                              start_angle=0, end_angle=2*math.pi,
                              color=(255, 255, 255), thickness=0.05,
                              pattern=railroad_pattern,
                              fill=(100, 100, 255, 100))
            
            time_text = dcg.DrawText(C, pos=(0.22, 0.15), 
                                     text="00", font=font,
                                     size=0.7, color=(255, 255, 255))
            
        # Attach the async callback as a handler
        async def async_animation_handler(sender, target: dcg.DrawInWindow):
            # Animation loop
            while target.state.visible:
                # Get current time and calculate rotation
                now = time.time()
                seconds = int(now % 60)
                minute_progress = (now % 60) / 60.0
                rotation = minute_progress * 2 * math.pi
                
                # Update the arc rotation
                arc.rotation = rotation
                
                # Update the time text
                time_text.text = f"{seconds:02d}"
                
                # Wake up the viewport to render the changes
                C.viewport.wake()
                
                # Sleep until next update
                await asyncio.sleep(0.05)  # Update 20 times per second
            
        draw_window.handlers += [dcg.GotRenderHandler(C, callback=async_animation_handler)]
        return draw_window

    # 2. Animation loop using a normal callback to start a thread
    def create_threaded_clock(width=200):
        with dcg.DrawInWindow(C, width=width, height=width, relative=True) as draw_window:
            # Create the railroad pattern
            railroad_pattern = dcg.Pattern.railroad(C, scale_factor=5)
            
            # Create the visual elements
            arc = dcg.DrawArc(C, center=(0.5, 0.5), radius=(0.4, 0.4), 
                              start_angle=0, end_angle=2*math.pi,
                              color=(255, 255, 255), thickness=0.05,
                              pattern=railroad_pattern,
                              fill=(100, 100, 255, 100))
            
            time_text = dcg.DrawText(C, pos=(0.22, 0.15), 
                                     text="00", font=font,
                                     size=0.7, color=(255, 255, 255))
            
            # Define the update function that will run in a thread
            def update_thread():
                while draw_window.state.visible:
                    # Get current time and calculate rotation
                    now = time.time()
                    seconds = int(now % 60)
                    minute_progress = (now % 60) / 60.0
                    rotation = minute_progress * 2 * math.pi

                    # Update the arc rotation
                    arc.rotation = rotation
  
                    # Update the time text
                    time_text.text = f"{seconds:02d}"

                    # Wake up the viewport to render the changes
                    C.viewport.wake()

                    # Sleep until next update
                    time.sleep(0.05)  # Update 20 times per second

            def start_thread():
                # Start the update thread
                thread = threading.Thread(target=update_thread, daemon=True)
                thread.start()
            # Attach the callback to start the thread when the draw window is created
            draw_window.handlers += [dcg.GotRenderHandler(C, callback=start_thread)]
        
        return draw_window
    
    # 3. Animation loop using a normal callback and class-based item
    class ClockWidget(dcg.DrawInWindow):
        def __init__(self, context, width=200, height="self.width", **kwargs):
            super().__init__(context, width=width, height=height, relative=True, **kwargs)
            
            # Create the railroad pattern
            railroad_pattern = dcg.Pattern.railroad(context, scale_factor=5)
            
            # Create the visual elements
            with self:
                self._arc = dcg.DrawArc(C, center=(0.5, 0.5), radius=(0.4, 0.4), 
                                       start_angle=0, end_angle=2*math.pi,
                                       color=(255, 255, 255), thickness=0.05,
                                       pattern=railroad_pattern,
                                       fill=(100, 100, 255, 100))
            
                self._time_text = dcg.DrawText(C, pos=(0.22, 0.15), 
                                              text="00", font=font,
                                              size=0.7, color=(255, 255, 255))
            # Attach the render handler
            self.handlers += [dcg.RenderHandler(context, callback=self._update_clock)]

        # Add a render handler to update the clock
        def _update_clock(self):
            # Get current time and calculate rotation
            now = time.time()
            seconds = int(now % 60)
            minute_progress = (now % 60) / 60.0
            rotation = minute_progress * 2 * math.pi
            
            # Update the arc rotation
            self._arc.rotation = rotation
            
            # Update the time text
            self._time_text.text = f"{seconds:02d}"
            
            # Wake up the viewport to render the changes
            self.context.viewport.wake()

    # 4. Animation loop using asyncio not in a callback
    def create_async_generator_clock(width=200):
        with dcg.DrawInWindow(C, width=width, height=width, relative=True) as draw_window:
            # Create the railroad pattern
            railroad_pattern = dcg.Pattern.railroad(C, scale_factor=5)
            
            # Create the visual elements
            arc = dcg.DrawArc(C, center=(0.5, 0.5), radius=(0.4, 0.4), 
                              start_angle=0, end_angle=2*math.pi,
                              color=(255, 255, 255), thickness=0.05,
                              pattern=railroad_pattern,
                              fill=(100, 100, 255, 100))
            
            time_text = dcg.DrawText(C, pos=(0.22, 0.15), 
                                     text="00", font=font,
                                     size=0.7, color=(255, 255, 255))
            
            # Create a render handler to use with the async generator
            render_handler = dcg.RenderHandler(C)
            draw_window.handlers += [render_handler]
            
            # Define the async animation function
            async def run_animation():
                # Using async generator from handlers attached to the DrawInWindow
                async for _ in dcg.utils.handler.async_generator_from_handlers(render_handler):
                    # Get current time and calculate rotation
                    now = time.time()
                    seconds = int(now % 60)
                    minute_progress = (now % 60) / 60.0
                    rotation = minute_progress * 2 * math.pi
                    
                    # Update the arc rotation
                    arc.rotation = rotation
                    
                    # Update the time text
                    time_text.text = f"{seconds:02d}"
                    
                    # Wake up the viewport to render the changes
                    C.viewport.wake()
            
            # Submit the async animation task
            C.queue.submit(run_animation())
        
        return draw_window

    # Display all clocks side by side in a horizontal layout
    with dcg.HorizontalLayout(C) as hl:
        parent_window = hl.parent
        target_width = dcg.parse_size("parent_window.width/4.2")
        # 1. Async callback version
        with dcg.TreeNode(C, label="20 fps refresh rate animations",
                          span_text_width=True, value=True):
            with dcg.HorizontalLayout(C, width=2*target_width, no_wrap=True):
                with dcg.VerticalLayout(C):
                    dcg.Text(C, value="Asyncio in Callback")
                    create_asyncio_callback_clock(width=target_width)

        # 2. Threaded version
                with dcg.VerticalLayout(C):
                    dcg.Text(C, value="Thread-based")
                    create_threaded_clock(width=target_width)

        with dcg.TreeNode(C, label="Full fps animations (watch cpu usage when enabling)",
                          span_text_width=True):
        # 3. Class-based version
            with dcg.HorizontalLayout(C, no_wrap=True):
                with dcg.VerticalLayout(C):
                    dcg.Text(C, value="Class-based")
                    ClockWidget(C, width=target_width)
        
        # 4. Async generator version
                with dcg.VerticalLayout(C):
                    dcg.Text(C, value="Asyncio Generator")
                    create_async_generator_clock(width=target_width)
    

pop_group()  # End of the asyncio group

@demosection(dcg.ChildWindow, dcg.Button, dcg.Text, dcg.Spacer, dcg.HorizontalLayout, dcg.VerticalLayout, dcg.Alignment)
@documented
@democode
def _positioning(C: dcg.Context):
    """
    ## Item Positioning and Size
    
    DearCyGui uses a top-left origin coordinate system for positioning UI elements.
    When items are rendered, they affect an internal cursor that determines where the 
    next item will be placed.
    
    Several approaches are available for controlling position and size:
    
    - **Default Flow Layout**: Items are placed at the current cursor position. The cursor
        moves down to the next line after each item, unless `no_newline` is used.
    - **Size Control**: Using `width` and `height` to set dimensions
    - **Positioning Attributes**: `x` and `y` for manual positioning
    - **Flow Control**: `no_newline` to place items horizontally
    - **Layout Helpers**: Spacers, Separators, and Layout containers
    
    Size values can be:
    - **Positive**: Exact pixel size (scaled by global scale)
    - **Negative**: Relative to parent size (`-1` means "remaining size - 1")
    - **Zero**: Default/automatic size
    - A string describing a formula to update the size every time the item is rendered
        This is useful for instance if you want some items to be a percentage of the
        size of a target item.

    Position values can be:
    - **Positive**: Exact pixel offset from the current cursor position (scaled by global scale)
    - **Zero**: Default position (current cursor position)
    - A string describing a formula to update the position every time the item is rendered,
        in viewport coordinates.

    ### Supported size and position string formulas:

    The following keywords are supported:
    - `fillx`: Fill available width
    - `filly`: Fill available height
    - `fullx`: Full parent content width (no position offset)
    - `fully`: Full parent content height (no position offset)
    - `parent.width`: Width of the parent item (larger than fullx as contains parent borders)
    - `parent.height`: Height of the parent item (larger than fully as contains parent borders)
    - `viewport.width`: Width of the viewport (application window)
    - `viewport.height`: Height of the viewport (application window)
    - `min`: Take minimum of two size values
    - `max`: Take maximum of two size values
    - `mean`: Calculate the mean (average) of two or more size values
    - `dpi`: Current global scale factor
    - `self.width`: Reference to the width of the current item
    - `self.height`: Reference to the height of the current item
    - `item.width`/`item.height`: Reference to another item's size (item must be in globals()/locals())
    - `{self, parent, item}.{x1, x2, xc, y1, y2, yc}`: Reference to left/center/right/top/bottom of the current, parent, or a target item.
    - `+`, `-`, `*`, `/`, `//`, `%`, `**`: Arithmetic operators. Parentheses can be used for grouping.
    - `abs()`: Absolute value function
    - Numbers: Fixed size in pixels (NOT dpi scaled. Use dpi keyword for that)

    For instance:
    - `"fillx - 50"` will fill the available width minus 50 pixels
    - `"fillx / 2"` will fill half of the available width
    - setting height to `"self.width * 0.5"` will set the height to half of the width

    """
    # Width and height demonstration
    dcg.Text(C, value="Size Properties:")
    dcg.Button(C, label="Default size")
    dcg.Button(C, label="Width = 200", width=200)
    dcg.Button(C, label="Width = 300, Height = 60", width=300, height=60)
    
    # Negative size (relative to parent)
    with dcg.ChildWindow(C, width=400, height=100, border=True):
        dcg.Button(C, label="Width = -50 (fill width minus 50px)", width=-50)
    
    dcg.Spacer(C, height=20)
    
    # Flow layout with no_newline
    dcg.Text(C, value="Using no_newline for horizontal layout:")
    dcg.Text(C, value="Item 1", no_newline=True)
    dcg.Text(C, value="Item 2", no_newline=True)
    dcg.Text(C, value="Item 3")  # This continues on the same line, but next item will go below
    dcg.Text(C, value="Item 4 (new line)")
    
    dcg.Spacer(C, height=20)
    
    # Different positioning methods
    dcg.Text(C, value="Positioning Methods:")
    
    # Create a container to demonstrate positions (here applied only on x)
    with dcg.ChildWindow(C, width=400, height=200, border=True, label="Positioning Demo"):
        # Position relative to cursor
        dcg.Button(C, label="Relative to cursor", x=10, y=10)

        # Position relative to parent
        b2 = dcg.Button(C, label="Relative to parent", x="parent.x1 + 50")

        # Position relative to another item (using globals)
        dcg.Button(C, label="Relative to a sibling", x="b2.xc - self.width/2")
        
        # Position relative to viewport (application window)
        dcg.Button(C, label="Relative to viewport", x="100")
    
    dcg.Spacer(C, height=20)
    
    # Using spacers for layout control
    dcg.Text(C, value="Using Spacers for Layout Control:")
    with dcg.HorizontalLayout(C):
        dcg.Button(C, label="Button 1")
        dcg.Spacer(C, width=50)  # Add horizontal space
        dcg.Button(C, label="Button 2")
        dcg.Spacer(C, width=20)  # Add horizontal space
        dcg.Button(C, label="Button 3")
    
    dcg.Spacer(C, height=20)  # Add vertical space
    
    # Using separators
    dcg.Text(C, value="Using Separators:")
    dcg.Button(C, label="Above separator")
    dcg.Separator(C)  # Add a horizontal line
    dcg.Button(C, label="Below separator")
    
    dcg.Spacer(C, height=20)
    
    # Layout containers for alignment
    dcg.Text(C, value="Alignment with Layout Containers:")
    
    # Left alignment (default)
    with dcg.HorizontalLayout(C, width=400, alignment_mode=dcg.Alignment.LEFT):
        dcg.Button(C, label="Left Aligned")
    
    # Center alignment
    with dcg.HorizontalLayout(C, width=400, alignment_mode=dcg.Alignment.CENTER):
        dcg.Button(C, label="Center Aligned")
    
    # Right alignment
    with dcg.HorizontalLayout(C, width=400, alignment_mode=dcg.Alignment.RIGHT):
        dcg.Button(C, label="Right Aligned")
        
    # Justified alignment
    with dcg.HorizontalLayout(C, width=400, alignment_mode=dcg.Alignment.JUSTIFIED):
        dcg.Button(C, label="Button 1", width=100)
        dcg.Button(C, label="Button 2", width=100)
        dcg.Button(C, label="Button 3", width=100)


@demosection(dcg.Text, dcg.Button, dcg.ThemeColorImGui, dcg.ThemeStyleImGui, dcg.ChildWindow)
@documented
@democode
def _styling(C: dcg.Context):
    """
    ## Styling Items
    
    DearCyGui provides multiple ways to customize the appearance of UI elements:
    
    - **Item Properties**: Some items accept attributes such as `color` and `fill`
    - **Theme Colors**: Apply color settings using `ThemeColorImGui` and `ThemeColorImPlot`
    - **Theme Styles**: Adjust spacing and sizes using `ThemeStyleImGui` and `ThemeStyleImPlot`
    - **Fonts**: Change text appearance using custom fonts
    
    Themes can be applied to individual items or hierarchically to affect all children.
    All theme values are automatically scaled by the global scale factor.
    """
    # Individual item styling
    dcg.Text(C, value="Item-specific Styling:")
    
    # Text styling
    dcg.Text(C, value="Colored text", color=(255, 0, 0))  # Red text
    dcg.Text(C, value="Colored text with alpha", color=(0, 255, 0, 150))  # Semi-transparent green
    
    dcg.Spacer(C, height=20)
    
    # Theme colors
    dcg.Text(C, value="Theme Colors:")
    
    # Create a color theme
    color_theme = dcg.ThemeColorImGui(C,
                                     Text=(255, 255, 0),        # Yellow text
                                     Button=(100, 0, 0),        # Dark red button
                                     ButtonHovered=(150, 0, 0), # Lighter red when hovered
                                     ButtonActive=(80, 0, 0))   # Darker red when clicked
        
    # Apply theme to individual items
    dcg.Text(C, value="This text uses the color theme", theme=color_theme)
    dcg.Button(C, label="Themed button", theme=color_theme)
    
    dcg.Spacer(C, height=10)
    
    # Theme styles (spacing, rounding, etc.)
    dcg.Text(C, value="Theme Styles:")
    
    # Create a style theme
    style_theme = dcg.ThemeStyleImGui(C,
                                     FrameRounding=10.0,    # Rounded corners
                                     FramePadding=(12, 6),  # More padding
                                     ItemSpacing=(15, 8))   # More space between items
    
    # Apply style theme
    dcg.Button(C, label="Default style")
    dcg.Button(C, label="Rounded with more padding", theme=style_theme)
    
    dcg.Spacer(C, height=20)
    
    # Hierarchical theming with child elements
    dcg.Text(C, value="Hierarchical Theming:")
    
    # Create a container with a theme that affects all children
    with dcg.ChildWindow(C, width=300, height=150, border=True, theme=color_theme):
        dcg.Text(C, value="All items in this container inherit the theme")
        dcg.Button(C, label="Themed button 1")
        dcg.Button(C, label="Themed button 2")
        
        # You can override the parent theme
        dcg.Text(C, value="This text has its own color", color=(0, 255, 255))
    
    dcg.Spacer(C, height=20)
    
    # Font styling example
    dcg.Text(C, value="Font Styling:")
    
    # In a real application, you might create a custom font:
    # custom_font = dcg.AutoFont(C, base_size=24)
    # dcg.Text(C, value="Text with custom font", font=custom_font)
    
    # For this demo, we'll just show a text describing font options
    dcg.Text(C, value="Fonts can be created with dcg.AutoFont()")
    dcg.Text(C, value="Example: custom_font = dcg.AutoFont(C, base_size=24)")


if __name__ == "__main__":
    launch_demo(title="Basics")
