from demo_utils import documented, democode, push_group, pop_group, launch_demo, demosection
import dearcygui as dcg



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
    - how to manipulate the item tree
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
    
    UI elements in DearCyGui are called **items**. All items share these common features:
    
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
               callback=button_callback,
               tip="This button will change its label when clicked")
    
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
    dcg.Text(C, value=f"Button2 width: {button2.width}")
    
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
    with dcg.ChildWindow(C, width=300, height=200, label="Parent Container"):
        # These items will automatically become children of the ChildWindow
        dcg.Text(C, value="I'm a child of the ChildWindow (using 'with')")
        dcg.Button(C, label="Me too!")
    
    # Method 2: Setting parent during creation
    parent_container = dcg.ChildWindow(C, width=300, height=200, label="Another Parent")
    dcg.Text(C, value="I'm a child (using parent parameter)", parent=parent_container)
    dcg.Button(C, label="Same here", parent=parent_container)
    
    # Method 3: Setting parent after creation
    another_parent = dcg.ChildWindow(C, width=300, height=200, label="Third Parent")
    text_item = dcg.Text(C, value="I'll be moved", attach=False)  # attach=False prevents automatic attachment
    button_item = dcg.Button(C, label="Me too", attach=False)
    
    # Now move the items to the parent
    text_item.parent = another_parent
    button_item.parent = another_parent
    
    # Method 4: Using the children list
    fourth_parent = dcg.ChildWindow(C, width=300, height=200, label="Fourth Parent")
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
                    pos_to_default=(100, 100)):
        
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
    
    - **Default Flow Layout**: Items are placed at the current cursor position
    - **Size Control**: Using `width` and `height` to set dimensions
    - **Positioning Attributes**: `pos_to_parent`, `pos_to_window`, and `pos_to_viewport`
    - **Flow Control**: `no_newline` to place items horizontally
    - **Layout Helpers**: Spacers, Separators, and Layout containers
    
    Size values can be:
    - **Positive**: Exact pixel size (scaled by global scale)
    - **Negative**: Relative to parent size (`-1` means "remaining size - 1")
    - **Zero**: Default/automatic size
    - A string describing a formula to update the size every time the item is rendered
        This is useful for instance if you want some items to be a percentage of the
        size of a target item.

    ### Supported size string formulas:

    The following keywords are supported:
    - `fillx`: Fill available width
    - `filly`: Fill available height
    - `fullx`: Full parent width (no position offset)
    - `fully`: Full parent height (no position offset)
    - `min`: Take minimum of two size values
    - `max`: Take maximum of two size values
    - `mean`: Calculate the mean (average) of two or more size values
    - `dpi`: Current global scale factor
    - `self.width`: Reference to the width of the current item
    - `self.height`: Reference to the height of the current item
    - `item.width`/`item.height`: Reference to another item's size (item must be in globals()/locals())
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
    
    # Create a container to demonstrate positions
    with dcg.ChildWindow(C, width=400, height=200, border=True, label="Positioning Demo"):
        # Position relative to window
        dcg.Button(C, label="pos_to_window", width=120, pos_to_window=(50, 30))
        
        # Position relative to parent (same as window in this case)
        dcg.Button(C, label="pos_to_parent", width=120, pos_to_parent=(50, 80))
        
        # Position relative to viewport (application window)
        dcg.Button(C, label="pos_to_viewport", width=120, pos_to_viewport=(500, 30))
    
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
    
    - **Item Properties**: Some items accept attributes such as `color`and `fill`
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
