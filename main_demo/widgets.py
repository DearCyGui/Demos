from demo_utils import documented, democode, push_group, pop_group,\
    launch_demo, demosection, display_item_documentation
import dearcygui as dcg

import datetime
import numpy as np
import time

# decorators:
# - documented: the description (markdown) is displayed
# - democode: the code is displayed and can edited (and run again)
# - demosection: the section is displayed in the table of contents,
#    the section name is extracted from the function name.

@demosection
@documented
def _widgets_intro(C: dcg.Context):
    """
    # What are "Widgets"?

    Widgets are the building blocks of a graphical user interface (GUI).
    They are interactive elements that allow users to interact with the application.
    In DearCyGui, widgets can be buttons, sliders, text inputs, checkboxes, and more.
    You can even build your own !

    DearCyGui provides a rich set of widgets that can be easily customized and combined to create complex interfaces.

    In this section, we'll explore the various widgets available in DearCyGui.
    Note each widget has its own set of properties and methods that allow you to control its behavior and appearance.
    """
    pass

push_group("Basic Widgets")

@demosection(dcg.Text, dcg.TextValue, dcg.SharedFloat)
@documented
@democode
def _text_widgets(C: dcg.Context):
    """
    ## Text Display Widgets
    
    DearCyGui offers various ways to display text:
    
    - `Text`: Simple text display with optional coloring and formatting
    - `TextValue`: Displays the value from a shared variable

    Text widgets supports various wrapping and formatting options.
    They are the foundation for labels, descriptions, and displaying information.
    """
    # Basic text display
    dcg.Text(C, value="This is a basic text widget")
    
    # Colored text
    dcg.Text(C, value="This text is red", color=(255, 0, 0))
    
    # Text with a bullet point
    dcg.Text(C, value="Bullet point text", marker="bullet")
    
    # Text with indentation
    dcg.Text(C, value="Indented text", x=20)

    # Text with default indentation (TreeNode, etc)
    dcg.Text(C, value="Default indentation", x="parent.x1 + theme.item_spacing.x")

    # Text with wrapping
    dcg.Text(C, value="This is a long text that will wrap to the next line if it exceeds the available width. You can control the wrapping behavior with the 'wrap' parameter.", wrap=300)
    
    # TextValue widget with a changeable value
    counter_value = dcg.SharedFloat(C, value=0)
    dcg.TextValue(C, shareable_value=counter_value, print_format="Counter: %.0f")
    
    # Button to increment the counter
    def inc_counter():
        counter_value.value += 1
        C.viewport.wake()  # Display the updated value
    dcg.Button(C, label="Increment Counter", 
               callback=inc_counter)

@demosection(dcg.Button, dcg.ButtonDirection, dcg.SharedFloat)
@documented
@democode
def _button_widgets(C: dcg.Context):
    """
    ## Button Widgets
    
    Buttons are interactive widgets that trigger actions when clicked:
    
    Buttons are essential for user interaction and triggering actions in your application.
    """
    # Basic button with a callback
    def button_callback(sender, target, data):
        print(f"Button clicked: {sender.label}")
    
    dcg.Button(C, label="Click Me", callback=button_callback)
    
    # Small button
    dcg.Button(C, label="Small Button", small=True, callback=button_callback)
    
    # Arrow buttons (with different directions)
    with dcg.HorizontalLayout(C):
        dcg.Text(C, value="Arrow buttons:")
        dcg.Button(C, arrow=dcg.ButtonDirection.LEFT, callback=button_callback)
        dcg.Button(C, arrow=dcg.ButtonDirection.RIGHT, callback=button_callback)
        dcg.Button(C, arrow=dcg.ButtonDirection.UP, callback=button_callback)
        dcg.Button(C, arrow=dcg.ButtonDirection.DOWN, callback=button_callback)
    
    # Button with a tooltip
    button_with_tooltip = dcg.Button(C, label="Hover me", callback=button_callback)
    with dcg.Tooltip(C, target=button_with_tooltip):
        dcg.Text(C, value="This is a tooltip for the button")
    
    # Repeat button (triggers repeatedly while being held down)
    repeat_counter = dcg.SharedFloat(C, value=0)
    def inc_counter():
        repeat_counter.value += 1
        C.viewport.wake()  # Display the updated value
    dcg.Button(C, label="Repeat Button (hold down)", repeat=True,
              callback=inc_counter)
    dcg.TextValue(C, shareable_value=repeat_counter, print_format="Repeat count: %.0f")

@demosection(dcg.Checkbox, dcg.RadioButton, dcg.Separator)
@documented
@democode
def _checkbox_radio(C: dcg.Context):
    """
    ## Checkboxes and Radio Buttons
    
    Checkboxes and radio buttons are common UI elements for selecting options:
    
    - **Checkbox**: Allow selecting multiple independent options
    - **RadioButton**: Allow selecting exactly one option from a group
    
    Both elements support callbacks to react to user interaction.
    """
    # Simple checkbox
    dcg.Checkbox(C, label="Simple Checkbox")
    
    # Checkbox with callback
    def checkbox_callback(sender, target, data):
        print(f"Checkbox changed to: {data}")
    
    dcg.Checkbox(C, label="Checkbox with callback", callback=checkbox_callback)
    
    # Disabled checkbox
    dcg.Checkbox(C, label="Disabled Checkbox", enabled=False)
    
    # Checkbox with initial value
    dcg.Checkbox(C, label="Initially checked", value=True)
    
    dcg.Separator(C)
    
    # Radio buttons (vertical layout by default)
    dcg.RadioButton(C, 
                    items=["Option 1", "Option 2", "Option 3"],
                    label="Vertical Radio Group")
    
    # Radio buttons with callback
    def radio_callback(sender, target, data):
        print(f"Radio selection changed to: {data}")
    
    dcg.RadioButton(C, 
                    items=["Red", "Green", "Blue"],
                    label="Radio with callback",
                    callback=radio_callback)
    
    # Horizontal radio buttons
    dcg.RadioButton(C, 
                    items=["Small", "Medium", "Large"],
                    label="Horizontal Radio Group",
                    horizontal=True)
    
    # Radio with initial selection
    dcg.RadioButton(C, 
                    items=["Low", "Medium", "High"],
                    label="With initial selection",
                    value="Medium",
                    horizontal=True)

@demosection(dcg.InputText, dcg.InputValue, dcg.Separator)
@documented
@democode
def _input_fields(C: dcg.Context):
    """
    ## Input Fields
    
    Input fields allow users to enter and edit text or numeric values:
    
    - `InputText`: For text entry with optional validation
    - `InputValue`: For numeric entry with format control
    
    Input fields support various options including:
    - Password masking
    - Multi-line input
    - Read-only display
    - Input filtering and validation
    """
    # Basic text input
    def input_callback(sender, target, data):
        print(f"Input '{sender.label}' changed to: {data}")
    
    dcg.InputText(C, label="Name", callback=input_callback)
    
    # Input text with initial value
    dcg.InputText(C, label="Email", value="user@example.com", callback=input_callback)
    
    # Input text with placeholder hint
    dcg.InputText(C, label="Address", hint="Enter your address", callback=input_callback)
    
    # Password input (masked text)
    dcg.InputText(C, label="Password", password=True, callback=input_callback)
    
    # Multiline text input
    dcg.InputText(C, label="Comment", multiline=True, height=100, callback=input_callback)
    
    dcg.Separator(C)
    
    # Numeric inputs
    dcg.InputValue(C, label="Age", print_format="%.0f", callback=input_callback)
    
    dcg.InputValue(C, label="Price", print_format="$%.2f", callback=input_callback)
    
    # Input with min/max constraints
    dcg.InputValue(C, label="Rating (1-5)", print_format="%.0f", 
                  min_value=1, max_value=5, callback=input_callback)
    
    # Vector input (multiple values)
    dcg.InputValue(C, label="RGB Color", size=3, 
                  value=[1.0, 0.5, 0.2], callback=input_callback)

@demosection(dcg.Slider)
@documented
@democode
def _sliders(C: dcg.Context):
    """
    ## Sliders and Drag Controls
    
    Sliders and drag controls provide intuitive ways to adjust numeric values
    They support:
    - Adjusting values by dragging along a track
    - Vertical and horizontal orientations
    - Integer, float, and multi-component options
    - Logarithmic scaling
    - Drag controls for precision adjustment
    
    These widgets are ideal for controlling parameters with visual feedback.
    """
    # Basic integer slider
    def slider_callback(sender, target, data):
        print(f"Slider '{sender.label}' changed to: {data}")

    dcg.Slider(C, label="Volume", print_format="%.0f",
              min_value=0, max_value=100, value=50,
              callback=slider_callback)

    # Float slider with formatting
    dcg.Slider(C, label="Opacity", print_format="%.2f", 
              min_value=0.0, max_value=1.0, value=0.75, keyboard_clamped=True,
              callback=slider_callback)

    # Slider with dragging enabled
    dcg.Slider(C, label="Zoom",
              min_value=0.1, max_value=10.0, value=1.0, 
              drag=True, callback=slider_callback)

    # Logarithmic slider
    dcg.Slider(C, label="Log Scale",
                min_value=1e-3, max_value=1e3, value=1.0,
                logarithmic=True, callback=slider_callback)

    # Multi-component slider (vector). Max 4 components
    dcg.Slider(C, label="Position", size=2,
                min_value=-10.0, max_value=10.0,
                value=[3.0, 0.0], callback=slider_callback)

    # Vertical slider
    with dcg.HorizontalLayout(C):
        dcg.Text(C, value="Vertical slider:")
        dcg.Slider(C, format="int", vertical=True, width=50, height=150, 
                  min_value=0, max_value=100, value=25,
                  callback=slider_callback)

    # Multiple sliders with shared value
    shared_value = dcg.SharedFloat(C, value=5.0)
    dcg.Text(C, value="Sliders with shared value:")
    dcg.Slider(C, label="Slider 1", min_value=0, max_value=10,
             shareable_value=shared_value, callback=slider_callback)
    dcg.Slider(C, label="Slider 2", min_value=0, max_value=10,
             shareable_value=shared_value, callback=slider_callback)
    dcg.TextValue(C, shareable_value=shared_value, print_format="Shared value: %.2f")

pop_group()  # End Basic Widgets

push_group("Selection Widgets")

@demosection(dcg.Combo)
@documented
@democode
def _combo_boxes(C: dcg.Context):
    """
    ## Combo Boxes
    
    Combo boxes (also known as dropdowns) allow users to select one option from a list
    while taking minimal screen space. They expand to show options only when clicked.
    
    Key features:
    - Can have a default selected item
    - Support callbacks when selection changes
    - Can be configured with various height modes and appearance options
    """
    # Simple combo box
    dcg.Combo(C, 
            items=["Apple", "Banana", "Cherry", "Orange", "Strawberry"],
            label="Simple Combo")
    
    # Combo with callback
    def combo_callback(sender, target, data):
        print(f"Selected: {data}")
    
    dcg.Combo(C, 
            items=["Red", "Green", "Blue", "Yellow", "Purple"],
            label="Combo with callback",
            callback=combo_callback)
    
    # Combo with initial value
    dcg.Combo(C, 
            items=["Small", "Medium", "Large", "X-Large"],
            label="With initial value",
            value="Medium")
    
    # Combo with different height mode
    dcg.Combo(C, 
            items=["Item " + str(i) for i in range(1, 15)],
            label="Larger height (more items in the displayed list)",
            height_mode="large")
    
    # Combo with width specification
    dcg.Combo(C, 
            items=["Short", "Medium length item", "Very long item text that extends beyond normal width"],
            label="Fixed width",
            width=200)
    
    # Disabled combo
    dcg.Combo(C, 
            items=["Cannot", "Select", "These", "Items"],
            label="Disabled combo",
            enabled=False)
    
    # Combo with no preview (shows label when closed)
    dcg.Combo(C, 
            items=["Hidden", "Until", "Expanded"],
            label="No preview", 
            no_preview=True)

@demosection(dcg.ListBox)
@documented
@democode
def _list_boxes(C: dcg.Context):
    """
    ## List Boxes
    
    List boxes display a scrollable list of selectable items, all visible at once.
    Unlike combo boxes, list boxes always display multiple items and take up more space.
    
    Key features:
    - Show multiple items at once
    - Support selection with callback
    - Configurable height and appearance
    """
    # Simple list box
    dcg.ListBox(C, 
             items=["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"],
             label="Simple ListBox")
    
    # List box with callback
    def listbox_callback(sender, target, data):
        print(f"Selected list item: {data}")
    
    dcg.ListBox(C, 
             items=["Red", "Green", "Blue", "Yellow", "Purple"],
             label="ListBox with callback",
             callback=listbox_callback)
    
    # List box with initial selection
    dcg.ListBox(C, 
             items=["Option A", "Option B", "Option C", "Option D"],
             label="With initial selection",
             value="Option B")
    
    # List box with height constraint
    dcg.ListBox(C, 
             items=["Item " + str(i) for i in range(1, 15)],
             label="List with height limit",
             num_items_shown_when_open=5)
    
    # List box with horizontal layout
    with dcg.HorizontalLayout(C):
        dcg.ListBox(C, 
                 items=["Left", "List", "Items"],
                 label="Side by side", 
                 width=150)
        
        dcg.ListBox(C, 
                 items=["Right", "List", "Items"],
                 label="ListBoxes", 
                 width=150)

@demosection(dcg.Selectable)
@documented
@democode
def _selectables(C: dcg.Context):
    """
    ## Selectable Items
    
    Selectables are text items that can be selected by clicking them.
    They are useful for creating custom lists where items can be highlighted.
    
    Key features:
    - Can be toggled on and off
    - Support callbacks when selected
    - Can be configured for different selection behaviors
    """
    # Simple selectable items
    dcg.Text(C, value="Basic selectable items:")
    dcg.Selectable(C, label="Click to select me")
    dcg.Selectable(C, label="I'm also selectable")
    dcg.Selectable(C, label="Select me too")
    
    dcg.Separator(C)
    
    # Selectable with callback
    def selectable_callback(sender, target, data):
        print(f"Selectable '{sender.label}' changed to: {data}")
    
    dcg.Text(C, value="Selectables with callback:")
    dcg.Selectable(C, label="Selectable with callback", callback=selectable_callback)
    dcg.Selectable(C, label="Another with callback", callback=selectable_callback)
    
    dcg.Separator(C)
    
    # Implementing single-selection behavior
    dcg.Text(C, value="Single selection group (try clicking multiple):")
    
    # Create a group of selectables where only one can be selected at a time
    items = []
    def exclusive_select(sender, target, data):
        # Deselect all other items in the group if this one was selected
        if data:
            for item in items:
                if item != sender:
                    item.value = False
    
    for i in range(5):
        items.append(dcg.Selectable(C, 
                               label=f"Option {i+1} (exclusive)", 
                               callback=exclusive_select))
    
    # After creating all items, assign the list to each item's user_data
    for sel in items:
        sel.user_data = items
    
    dcg.Separator(C)
    
    # Disabled selectable
    dcg.Text(C, value="Disabled selectable:")
    dcg.Selectable(C, label="Can't select this", enabled=False)
    
    # Initially selected
    dcg.Text(C, value="Initially selected:")
    dcg.Selectable(C, label="I start selected", value=True)

@demosection(dcg.TreeNode, dcg.CollapsingHeader)
@documented
@democode
def _tree_node(C: dcg.Context):
    """
    ## Tree Nodes and Collapsing Headers
    
    Tree nodes and collapsing headers provide expandable containers for creating
    hierarchical interfaces.
    
    Key features:
    - Can be expanded and collapsed to show or hide content
    - Support nesting for hierarchical organization
    - Can be configured with various appearance options
    """
    # Basic Tree Node
    with dcg.TreeNode(C, label="Basic Tree Node"):
        dcg.Text(C, value="I'm inside the tree node")
        dcg.Button(C, label="A button in a tree")
        dcg.Checkbox(C, label="A checkbox in a tree")
    
    # Tree Node with default open state
    with dcg.TreeNode(C, label="Tree Node (open by default)", value=True):
        dcg.Text(C, value="This tree node starts expanded")
        dcg.Button(C, label="Button in expanded tree")
    
    # Nested Tree Nodes
    with dcg.TreeNode(C, label="Nested Tree Nodes"):
        dcg.Text(C, value="Level 1 content")
        
        with dcg.TreeNode(C, label="Level 2 Node A"):
            dcg.Text(C, value="Level 2 content")
            
            with dcg.TreeNode(C, label="Level 3 Node"):
                dcg.Text(C, value="Level 3 content")
                dcg.Button(C, label="Deep button")
        
        with dcg.TreeNode(C, label="Level 2 Node B"):
            dcg.Text(C, value="More level 2 content")
            dcg.Button(C, label="Another button")
    
    # Tree Node with callback
    def tree_callback(sender, target, data):
        print(f"Tree node '{sender.label}' is now {'open' if data else 'closed'}")
    
    dcg.TreeNode(C, label="Tree with callback", callback=tree_callback)
    
    # Tree Node with bullet
    with dcg.TreeNode(C, label="Tree with bullet", bullet=True):
        dcg.Text(C, value="This tree has a bullet instead of an arrow")
        dcg.Button(C, label="Bulleted button")
    
    # Collapsing Header (similar to TreeNode but with different styling)
    dcg.Separator(C)
    dcg.Text(C, value="Collapsing Headers:")
    
    with dcg.CollapsingHeader(C, label="Basic Collapsing Header"):
        dcg.Text(C, value="Content inside collapsing header")
        dcg.Button(C, label="Header button")
    
    # Collapsing Header with close button
    with dcg.CollapsingHeader(C, label="Closable Header", closable=True):
        dcg.Text(C, value="This header has a close button")
        dcg.Text(C, value="Clicking the X will hide this header completely")
    
    # Collapsing Header initially open
    with dcg.CollapsingHeader(C, label="Initially Open Header", value=True):
        dcg.Text(C, value="This header starts expanded")
        with dcg.HorizontalLayout(C):
            dcg.Button(C, label="Button 1")
            dcg.Button(C, label="Button 2")

pop_group()  # End Selection Widgets

push_group("Layout Containers")

@demosection(dcg.ChildWindow)
@documented
@democode
def _child_windows(C: dcg.Context):
    """
    ## Child Windows
    
    Child windows are independent scrollable regions within a window:
    
    - Create scrollable areas for content
    - Control borders, scrollbars, and backgrounds
    - Provide content clipping
    - Can contain any widgets including other child windows
    
    Child windows help manage complex layouts and scrolling regions.
    """
    # Basic child window with border
    with dcg.ChildWindow(C, width=300, height=200, border=True, label="Basic Child Window"):
        dcg.Text(C, value="This is a child window with a border")
        dcg.Button(C, label="Button inside child window")
        dcg.Checkbox(C, label="Checkbox inside child window")
    
    # Child window with scrollbars (auto-appearing)
    with dcg.ChildWindow(C, width=300, height=150, border=True, label="Scrollable Content"):
        # Add enough content to make scrollbars appear
        for i in range(20):
            dcg.Text(C, value=f"Line {i+1} of content")
    
    # Child window with horizontal scrollbar
    with dcg.ChildWindow(C, width=300, height=100, border=True, 
                      label="Horizontal Scrolling", horizontal_scrollbar=True):
        # Create content that extends beyond the width
        dcg.Text(C, value="This is a very long text that will extend beyond the width of the child window, causing a horizontal scrollbar to appear.")
        dcg.Button(C, label="Wide button", width=500)
    
    # Nested child windows
    with dcg.ChildWindow(C, width=400, height=300, border=True, label="Parent Child Window"):
        dcg.Text(C, value="This is the outer child window")
        
        # Inner child window with different style
        with dcg.ChildWindow(C, width=200, height=150, border=True, 
                          label="Nested Child Window"):
            dcg.Text(C, value="This is a nested child window")
            dcg.Button(C, label="Nested Button")
    
    # Child window with no border
    with dcg.ChildWindow(C, width=300, height=100, border=False, label="No Border"):
        dcg.Text(C, value="This child window has no visible border")
        dcg.Button(C, label="Button in borderless child")
    
    # Child window with auto-resize
    with dcg.ChildWindow(C, auto_resize_x=True, height=100, border=True, no_scrollbar=True,
                      label="Auto-Resize Width"):
        dcg.Text(C, value="This child window automatically resizes its width to fit content")
        dcg.Button(C, label="Button")
        dcg.Button(C, label="Another Button With Longer Text")

@demosection(dcg.HorizontalLayout, dcg.VerticalLayout, dcg.Alignment)
@documented
@democode
def _horizontal_vertical_layout(C: dcg.Context):
    """
    ## Horizontal and Vertical Layouts
    
    Layout containers organize widgets in horizontal or vertical arrangements:
    
    - `HorizontalLayout`: Arranges widgets left-to-right
    - `VerticalLayout`: Arranges widgets top-to-bottom
    - Control alignment, spacing, and positioning
    
    Layouts help create structured, responsive interfaces with minimal effort.
    """
    # Basic Horizontal Layout
    dcg.Text(C, value="Basic Horizontal Layout:")
    with dcg.HorizontalLayout(C):
        dcg.Button(C, label="Button 1")
        dcg.Button(C, label="Button 2")
        dcg.Button(C, label="Button 3")
    
    # Horizontal Layout with spacing
    dcg.Text(C, value="Horizontal Layout with spacing:")
    with dcg.HorizontalLayout(C):
        dcg.Button(C, label="Spaced 1")
        dcg.Spacer(C, width=10)  # 10px horizontal space
        dcg.Button(C, label="Spaced 2")
        dcg.Spacer(C, width=10)  # 10px horizontal space
        dcg.Button(C, label="Spaced 3")
    
    # Horizontal Layout with alignment
    dcg.Text(C, value="Horizontal Layout with center alignment:")
    with dcg.HorizontalLayout(C, width=400, alignment_mode=dcg.Alignment.CENTER):
        dcg.Button(C, label="Centered 1")
        dcg.Button(C, label="Centered 2")
        dcg.Button(C, label="Centered 3")
    
    # Horizontal Layout with right alignment
    dcg.Text(C, value="Horizontal Layout with right alignment:")
    with dcg.HorizontalLayout(C, width=400, alignment_mode=dcg.Alignment.RIGHT):
        dcg.Button(C, label="Right 1")
        dcg.Button(C, label="Right 2")
        dcg.Button(C, label="Right 3")

    # Horizontal Layout with justified alignment
    dcg.Text(C, value="Horizontal Layout with justified alignment:")
    with dcg.HorizontalLayout(C, width=400, alignment_mode=dcg.Alignment.JUSTIFIED):
        dcg.Button(C, label="Justified 1")
        dcg.Button(C, label="Justified 2")
        dcg.Button(C, label="Justified 3")
    
    dcg.Separator(C)
    
    # Basic Vertical Layout
    dcg.Text(C, value="Basic Vertical Layout:")
    with dcg.VerticalLayout(C, width=200):
        dcg.Button(C, label="Button A")
        dcg.Button(C, label="Button B")
        dcg.Button(C, label="Button C")
    
    # Vertical Layout with spacing
    dcg.Text(C, value="Vertical Layout with spacing:")
    with dcg.VerticalLayout(C, width=200):
        dcg.Button(C, label="Spaced A")
        dcg.Spacer(C, height=10)  # 10px vertical space
        dcg.Button(C, label="Spaced B")
        dcg.Spacer(C, height=10)  # 10px vertical space
        dcg.Button(C, label="Spaced C")
    
    # Nested layouts
    dcg.Text(C, value="Nested layouts for complex arrangements:")
    with dcg.HorizontalLayout(C):
        # Left side - vertical layout
        with dcg.VerticalLayout(C, width=150):
            dcg.Text(C, value="Left Column")
            dcg.Button(C, label="Left 1")
            dcg.Button(C, label="Left 2")
        
        # Right side - vertical layout
        with dcg.VerticalLayout(C, width=150):
            dcg.Text(C, value="Right Column")
            dcg.Button(C, label="Right 1")
            dcg.Button(C, label="Right 2")
    
    # Vertical layout containing horizontal layouts - grid-like structure
    dcg.Text(C, value="Grid-like structure with nested layouts:")
    with dcg.VerticalLayout(C):
        # Row 1
        with dcg.HorizontalLayout(C):
            dcg.Button(C, label="1,1", width=80)
            dcg.Button(C, label="1,2", width=80)
            dcg.Button(C, label="1,3", width=80)
        
        # Row 2
        with dcg.HorizontalLayout(C):
            dcg.Button(C, label="2,1", width=80)
            dcg.Button(C, label="2,2", width=80)
            dcg.Button(C, label="2,3", width=80)

@demosection(dcg.Tab, dcg.TabBar, dcg.TabButton)
@documented
@democode
def _tabs_and_tabbar(C: dcg.Context):
    """
    ## Tabs and Tab Bars
    
    Tab bars organize content into separate, selectable views:
    
    - `TabBar`: Container for multiple tabs
    - `Tab`: Individual page of content
    - Tab reordering, closing, and customization
    
    Tabs help manage screen space and organize related content into categories.
    """
    # Basic Tab Bar with multiple tabs
    dcg.Text(C, value="Basic Tab Bar:")
    with dcg.TabBar(C):
        with dcg.Tab(C, label="Tab 1"):
            dcg.Text(C, value="Content for Tab 1")
            dcg.Button(C, label="Button on Tab 1")
        
        with dcg.Tab(C, label="Tab 2"):
            dcg.Text(C, value="Content for Tab 2")
            dcg.Checkbox(C, label="Checkbox on Tab 2")
        
        with dcg.Tab(C, label="Tab 3"):
            dcg.Text(C, value="Content for Tab 3")
            dcg.InputText(C, label="Input on Tab 3")
    
    dcg.Separator(C, height=10)
    
    # Tab Bar with closable tabs
    dcg.Text(C, value="Tabs with close buttons:")
    with dcg.TabBar(C) as tab_bar_closable:
        with dcg.Tab(C, label="Tab A", closable=True):
            dcg.Text(C, value="This tab can be closed")
        
        with dcg.Tab(C, label="Tab B", closable=True):
            dcg.Text(C, value="This tab can also be closed")
        
        with dcg.Tab(C, label="Tab C"):
            dcg.Text(C, value="This tab cannot be closed")

        dcg.TabButton(C, label="I'm a button")
    
    dcg.Separator(C, height=10)
    
    # Tab Bar with reorderable tabs
    dcg.Text(C, value="Tabs that can be reordered (try dragging):")
    with dcg.TabBar(C, reorderable=True):
        with dcg.Tab(C, label="Draggable 1"):
            dcg.Text(C, value="You can drag these tabs to reorder them")
        
        with dcg.Tab(C, label="Draggable 2"):
            dcg.Text(C, value="Try dragging this tab to a different position")
        
        with dcg.Tab(C, label="Draggable 3"):
            dcg.Text(C, value="These tabs can be reordered")
    

@demosection(dcg.Spacer, dcg.Separator, dcg.baseSizing, dcg.parse_size, dcg.HorizontalLayout,
             dcg.VerticalLayout)
@documented
@democode
def _positioning_and_sizing(C: dcg.Context):
    """
    ## Positioning and Sizing
    
    DearCyGui provides several ways to control item position and size:
    
    - Set width and height explicitly
    - Use negative values for relative sizing
    - Control item alignment within layouts
    - Use position controls for specific placement
    - Spacers and separators for layout control
    
    These tools help create precisely arranged, responsive interfaces.
    """
    
    dcg.Text(C, value="Explicit sizing:")
    dcg.Button(C, label="Width=200, Height=40", width=200, height=40)
    
    # Relative sizing using negative values
    dcg.Text(C, value="Relative sizing with negative values:")
    with dcg.ChildWindow(C, width=400, height=100, border=True):
        # Will fill width minus 50 pixels
        dcg.Button(C, label="Width=-50 (fill width minus 50px)", width=-50)
    
    # Spacers for layout control
    dcg.Text(C, value="Spacers for layout control:")
    with dcg.HorizontalLayout(C):
        dcg.Button(C, label="Left")
        dcg.Spacer(C, width=100)  # 100px horizontal space
        dcg.Button(C, label="Right")
    
    dcg.Spacer(C, height=20)  # 20px vertical space
    
    # Separators
    dcg.Text(C, value="Separators:")
    dcg.Button(C, label="Above separator")
    dcg.Separator(C)  # horizontal separator
    dcg.Button(C, label="Below separator")
    
    dcg.Spacer(C, height=20)
    
    # Size strings and formulas
    dcg.Text(C, value="Size strings and formulas:")
    
    # Define a reference button to use in size formulas
    ref_button = dcg.Button(C, label="Reference Button", width=400, height=40)
    
    # Button with size relative to another item
    dcg.Button(C, label="Half width of reference", 
             width="ref_button.width * 0.5", 
             height="ref_button.height")
    
    # Fill available width minus a margin
    with dcg.ChildWindow(C, width=400, height=80, border=True):
        dcg.Button(C, label="Fill width minus 20px margin", width="fillx - 20")
    
    # Dynamically sized items
    with dcg.ChildWindow(C, width=300, height=150, border=True):
        # Two buttons that together fill available width
        with dcg.HorizontalLayout(C):
            dcg.Button(C, label="33% width", width="fullx / 3")
            dcg.Button(C, label="66% width", width="fullx * 2 / 3")
    
    dcg.Spacer(C, height=20)
    
    # Positioned items
    dcg.Text(C, value="Positioned items:")
    
    # Container for positioned items
    with dcg.ChildWindow(C, width=300, height=200, border=True):
        # Anchored to specific positions
        dcg.Button(C, label="Top Left", x="parent.x1+10 * dpi", y="parent.y1+10*dpi", width=100)
        dcg.Button(C, label="Top Right", x="parent.x2-self.width-10*dpi", y="parent.y1+10*dpi", width=100)
        dcg.Button(C, label="Bottom Left", x="parent.x1+10 * dpi", y="parent.y2-self.height-10*dpi", width=100)
        dcg.Button(C, label="Bottom Right", x="parent.x2-self.width-10*dpi", y="parent.y2-self.height-10*dpi", width=100)
        dcg.Button(C, label="Center", x="parent.xc-self.width/2", y="parent.yc-self.height/2", width=100)
    
    dcg.Spacer(C, height=20)
    
    # Different layout alignments
    dcg.Text(C, value="Layout alignments:")
    
    # Left alignment (default)
    with dcg.HorizontalLayout(C, width=400, alignment_mode=dcg.Alignment.LEFT):
        dcg.Button(C, label="Left aligned")
    
    # Center alignment
    with dcg.HorizontalLayout(C, width=400, alignment_mode=dcg.Alignment.CENTER):
        dcg.Button(C, label="Center aligned")
    
    # Right alignment
    with dcg.HorizontalLayout(C, width=400, alignment_mode=dcg.Alignment.RIGHT):
        dcg.Button(C, label="Right aligned")

    # Justified alignment
    with dcg.HorizontalLayout(C, width=400, alignment_mode=dcg.Alignment.JUSTIFIED):
        dcg.Button(C, label="Justified 1", width=100)
        dcg.Button(C, label="Justified 2", width=100)
        dcg.Button(C, label="Justified 3", width=100)

@demosection(dcg.HorizontalLayout, dcg.VerticalLayout, dcg.ChildWindow, dcg.utils.DraggableBar)
@documented
@democode
def _dashboards(C: dcg.Context):
    """
    ## Dashboards

    While DearCyGui does not have a dedicated dashboard widget, you can create
    complex dashboard-like interfaces by combining various layout containers.

    - Child windows for scrollable content areas
    - Use horizontal and vertical layouts for simple organization
    - Use string positioning for advanced control
    - Draggable bars for custom resizing sections
    """

    dcg.Text(C, value="Dashboard example:")
    
    with dcg.ChildWindow(C, border=False, resizable_y=False, resizable_x=True,
                         width=300, no_newline=True,
                         no_scroll_with_mouse=True,
                         no_scrollbar=True) as c1:
        dcg.ChildWindow(C, width="fillx", height=200,
                        border=True, resizable_y=True, resizable_x=False)
        dcg.ChildWindow(C, width="fillx", height=200,
                        border=True, resizable_y=True, resizable_x=False)
        dcg.ChildWindow(C, width="fillx", height="filly",
                        border=True, resizable_y=False, resizable_x=False)
    with dcg.ChildWindow(C, border=False, resizable_y=False, resizable_x=True,
                         width=300, no_newline=True,
                         no_scroll_with_mouse=True,
                         no_scrollbar=True) as c2:
        dcg.ChildWindow(C, width="fillx", height=300, border=True,
                        resizable_y=True, resizable_x=False)
        dcg.ChildWindow(C, width="fillx", height="filly", border=True)
    with dcg.ChildWindow(C, border=False, resizable_y=False, resizable_x=False,
                         width="fillx",
                         no_scroll_with_mouse=True,
                         no_scrollbar=True) as c3:
        dcg.ChildWindow(C, width="fillx", height=200,
                        border=True, resizable_y=True, resizable_x=False)
        dcg.ChildWindow(C, width="fillx", height=200,
                        border=True, resizable_y=True, resizable_x=False)
        dcg.ChildWindow(C, width="fillx", height="filly",
                        border=True, resizable_y=False, resizable_x=False)

    # Link heights
    c1.height = "min(filly, 600*dpi)"
    c2.height = c1.height
    c3.height = c1.height

    dcg.Text(C, value="Same example with custom draggable sections:")
    
    with dcg.VerticalLayout(C) as col1:
        dcg.ChildWindow(C, width="fillx", height=200,
                        border=True, resizable_y=True, resizable_x=False)
        dcg.ChildWindow(C, width="fillx", height=200,
                        border=True, resizable_y=True, resizable_x=False)
        dcg.ChildWindow(C, width="fillx", height="filly",
                        border=True, resizable_y=False, resizable_x=False)
    with dcg.VerticalLayout(C) as col2:
        dcg.ChildWindow(C, width="fillx", height=300, border=True,
                        resizable_y=True, resizable_x=False)
        dcg.ChildWindow(C, width="fillx", height="filly", border=True)
    with dcg.VerticalLayout(C) as col3:
        dcg.ChildWindow(C, width="fillx", height=200,
                        border=True, resizable_y=True, resizable_x=False)
        dcg.ChildWindow(C, width="fillx", height=200,
                        border=True, resizable_y=True, resizable_x=False)
        dcg.ChildWindow(C, width="fillx", height="filly",
                        border=True, resizable_y=False, resizable_x=False)

    # Custom resize sections between columns
    sep1 = dcg.utils.DraggableBar(C, vertical=True, position=0.2, no_newline=True)
    sep2 = dcg.utils.DraggableBar(C, vertical=True, position=0.6, no_newline=True)
    col1.x = 0
    col1.width = "sep1.x1 - self.x1"
    col1.no_newline = True
    col2.x = "sep1.x2"
    col2.width = "sep2.x1 - self.x1"
    col2.no_newline = True
    col3.x = "sep2.x2"
    col3.width = "fillx"
    sep1.y = col1.y
    sep2.y = col1.y

    # Link heights
    sep1.height = col1.height
    sep2.height = col1.height
    col2.height = col1.height
    col3.height = col1.height

    # Define height
    col1.height = "min(filly, 600*dpi)"


pop_group()  # End Layout Containers

push_group("Advanced Widgets")

@demosection(dcg.ColorPicker, dcg.ColorEdit, dcg.ColorButton)
@documented
@democode
def _color_pickers(C: dcg.Context):
    """
    ## Color Pickers
    
    Color selection widgets allow users to choose and manipulate colors:
    
    - `ColorEdit`: Compact color editor with RGB/HSV input
    - `ColorPicker`: Full-featured color selection dialog
    - `ColorButton`: Color swatch that opens a picker when clicked
    
    Color widgets support different formats, alpha channels, and preview options.
    """
    # Simple color editor - compact RGB controls
    dcg.Text(C, value="ColorEdit - Compact RGB Controls:")
    color_value = dcg.SharedColor(C, value=(100, 150, 200, 255))
    color_edit = dcg.ColorEdit(C, 
                              label="RGB Color",
                              shareable_value=color_value)

    # Color editor with HSV mode
    dcg.Text(C, value="ColorEdit - HSV Mode:")
    dcg.ColorEdit(C, 
                label="HSV Color", 
                shareable_value=color_value,
                display_mode="hsv")

    # Color editor with no alpha
    dcg.Text(C, value="ColorEdit - No Alpha Channel:")
    dcg.ColorEdit(C, 
                label="RGB No Alpha", 
                no_alpha=True,
                value=(255, 100, 0))

    dcg.Separator(C)

    # Full color picker dialog
    dcg.Text(C, value="ColorPicker - Full Color Selection Dialog:")
    dcg.ColorPicker(C, 
                   label="Color Picker", 
                   shareable_value=color_value,
                   width=300)

    # Color picker with no small preview
    dcg.Text(C, value="ColorPicker - No Small Preview:")
    dcg.ColorPicker(C, 
                   label="No Preview", 
                   no_small_preview=True,
                   width=250)

    dcg.Separator(C)

    # Color button that opens a picker when clicked
    dcg.Text(C, value="ColorButton:")
    
    dcg.ColorButton(C, 
                   label="Choose Color", 
                   shareable_value=color_value)

    # Color button with no border
    dcg.Text(C, value="ColorButton - No Border:")
    dcg.ColorButton(C, 
                   value=(255, 0, 0, 255), 
                   no_border=True)

    # Color button with custom size
    dcg.Text(C, value="ColorButton - Custom Size:")
    dcg.ColorButton(C, 
                   value=(0, 255, 0, 255), 
                   width=60, 
                   height=60)

    dcg.Separator(C)

    # Display the selected color
    dcg.Text(C, value="Currently Selected Color:")
    with dcg.HorizontalLayout(C):
        # Show a color swatch
        dcg.ColorButton(C, 
                        shareable_value=color_value,
                        enabled=False)
        
        # Show the RGB values
        dcg.TextValue(C, 
                     shareable_value=color_value,
                     print_format="RGB: %f, %f, %f, %f")

@demosection(dcg.Image)
@documented
@democode
def _image_display(C: dcg.Context):
    """
    ## Images
    
    DearCyGui can display images and image-based controls:
    
    - `Image`: Simple display of image data
    - `Image` with `button=True`: Clickable image that works like a button
    - Control scaling, tinting, and borders
    
    Images can be loaded from textures and customized with various display options.
    """
    # Create some sample image data (a gradient)
    width, height = 200, 100
    gradient = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create a horizontal gradient (red to blue)
    for x in range(width):
        red = int(255 * (1 - x / width))
        blue = int(255 * (x / width))
        gradient[:, x] = [red, 0, blue]
    
    # Create a texture from the gradient
    gradient_texture = dcg.Texture(C, gradient)
    
    # Basic image display
    dcg.Text(C, value="Basic Image Display:")
    dcg.Image(C, texture=gradient_texture)
    
    # Image with tinting
    dcg.Text(C, value="Image with Tinting (Cyan):")
    dcg.Image(C, 
             texture=gradient_texture,
             color_multiplier=(0, 255, 255, 150))

    # Image with border
    dcg.Text(C, value="Image with Tinting, Background and Border:")
    theme_border = dcg.ThemeList(C)
    with theme_border:
        dcg.ThemeColorImGui(C, border=(255, 0, 0, 255))
        dcg.ThemeStyleImGui(C, frame_border_size=1)

    dcg.Image(C, 
             texture=gradient_texture,
             background_color=(255, 0, 255, 255),
             color_multiplier=(0, 255, 255, 150),
             theme=theme_border)
    
    # Image with custom size
    dcg.Text(C, value="Image with Custom Size:")
    dcg.Image(C, 
             texture=gradient_texture,
             width=300,
             height=50)
    
    dcg.Separator(C)
    
    # Create a checkered pattern for the next examples
    checker = np.zeros((100, 100, 3), dtype=np.uint8)
    checker[0:50, 0:50] = [200, 0, 0]    # Top left: red
    checker[0:50, 50:100] = [0, 200, 0]  # Top right: green
    checker[50:100, 0:50] = [0, 0, 200]  # Bottom left: blue
    checker[50:100, 50:100] = [200, 200, 0]  # Bottom right: yellow
    
    checker_texture = dcg.Texture(C, checker)
    
    # Image Button - clickable image
    dcg.Text(C, value="Image Button:")
    def image_button_callback(sender, target, data):
        print("Image button clicked!")
    
    dcg.Image(C,
              button=True,
              texture=checker_texture,
              callback=image_button_callback)
    
    # Image Button with frame padding
    dcg.Text(C, value="Image Button with Frame Padding:")
    dcg.Image(C,
              button=True,
              texture=checker_texture,
              theme=dcg.ThemeStyleImGui(C, frame_padding=(10, 10)),
              callback=image_button_callback)
    
    # Image Button with tinting
    dcg.Text(C, value="Image Button with Tinting:")
    dcg.Image(C, 
              button=True,
              texture=checker_texture,
              color_multiplier=(255, 255, 255, 150),
              callback=image_button_callback)

    # Image Button with background color
    dcg.Text(C, value="Image Button with Tinting, Background and Border:")
    dcg.Image(C,
              button=True,
              texture=checker_texture,
              background_color=(100, 100, 100, 255),
              color_multiplier=(255, 255, 255, 150),
              theme=theme_border,
              callback=image_button_callback)

@demosection(dcg.ProgressBar, dcg.SimplePlot)
@documented
@democode
def _progress_bars(C: dcg.Context):
    """
    ## Progress Bars and Simple Plots
    
    Visualize progress and simple data:
    
    - `ProgressBar`: Show completion status of operations
    - `SimplePlot`: Display simple data visualizations (See the Plot section for more advanced plots)
    
    These widgets help provide visual feedback for processes and data trends.
    """
    # Basic progress bar
    dcg.Text(C, value="Basic Progress Bar:")
    dcg.ProgressBar(C, 
                   value=0.45,
                   overlay="45%")
    
    # Progress bar with custom size and colors
    dcg.Text(C, value="Custom Progress Bar:")
    dcg.ProgressBar(C, 
                   value=0.75,
                   width=300, 
                   height=25,
                   overlay="75%")
    
    # Animated progress bar
    dcg.Text(C, value="Animated Progress Bar:")
    progress_bar = dcg.ProgressBar(C, 
                                  value=0.,
                                  overlay="Loading...")
    
    # Animation function for progress bar
    def animate_progress():
        # Calculate progress based on time
        t = time.time() % 3  # Cycle every 3 seconds
        progress_bar.value = (t / 3.0)
        C.viewport.wake()  # Refresh the viewport to update the progress bar
        
    progress_bar.handlers += [
        dcg.RenderHandler(C, callback=animate_progress)
    ]
    
    dcg.Separator(C)
    
    # Simple data plots
    dcg.Text(C, value="Simple Line Plot:")
    
    # Generate sine wave data
    x = np.linspace(0, 4*np.pi, 100)
    y = np.sin(x)
    
    # Display as simple line plot
    dcg.SimplePlot(C, 
                  label="Sine Wave",
                  value=y.tolist(),
                  height=80,
                  overlay="sin(x)")
    
    # Histogram plot
    dcg.Text(C, value="Simple Histogram:")
    
    # Generate random data with normal distribution
    hist_data = np.random.normal(0, 1, 1000).tolist()
    
    # Display as histogram
    dcg.SimplePlot(C, 
                  label="Normal Distribution",
                  value=hist_data,
                  height=80,
                  histogram=True,
                  overlay="center=0, std=1")

pop_group()  # End Advanced Widgets

push_group("Interactivity Features")

@demosection(dcg.Tooltip, dcg.Window, dcg.HoverHandler, dcg.utils.TemporaryTooltip)
@documented
@democode
def _tooltips(C: dcg.Context):
    """
    ## Tooltips
    
    Tooltips provide helpful information when users hover over elements:
    
    - Attach tooltips to any widget
    - Control timing, appearance, and content
    - Create rich tooltip content with any widgets
    
    Tooltips enhance usability by providing context without cluttering the interface.
    """
    # Basic tooltip
    button1 = dcg.Button(C, label="Hover me for basic tooltip")
    with dcg.Tooltip(C, target=button1):
        dcg.Text(C, value="This is a simple tooltip")
    
    dcg.Separator(C)
    
    # Tooltip with delay
    button2 = dcg.Button(C, label="Hover me for delayed tooltip")
    with dcg.Tooltip(C, target=button2, delay=1.0):
        dcg.Text(C, value="This tooltip appears after 1 second")
    
    dcg.Separator(C)
    
    # Rich tooltip content
    button3 = dcg.Button(C, label="Hover for rich tooltip")
    with dcg.Tooltip(C, target=button3):
        dcg.Text(C, value="Tooltips can contain any widgets:")
        dcg.Separator(C)
        with dcg.HorizontalLayout(C):
            dcg.Button(C, label="Buttons")
            dcg.Checkbox(C, label="Checkboxes")
        dcg.Slider(C, label="Even sliders", min_value=0.0, max_value=1.0)
    
    dcg.Separator(C)
    
    # Hide on activity (tooltip disappears when mouse moves)
    button4 = dcg.Button(C, label="Hover and move mouse to hide")
    with dcg.Tooltip(C, target=button4, hide_on_activity=True):
        dcg.Text(C, value="This tooltip disappears when you move the mouse")
    
    dcg.Separator(C)
    
    # Tooltip on an input field with more detailed help
    input_field = dcg.InputText(C, label="Email", hint="Enter your email")
    with dcg.Tooltip(C, target=input_field):
        dcg.Text(C, value="Valid email format required")
        dcg.Text(C, value="Example: user@example.com", color=(150, 150, 150))
    
    dcg.Separator(C)
    
    # Dynamic tooltip using a handler
    dcg.Text(C, value="Dynamic Tooltip Example:")
    dynamic_btn = dcg.Button(C, label="Hover me for dynamic tooltip")
    
    # Function to create a tooltip dynamically when hovering
    def create_dynamic_tooltip(sender, target):
        # Create a temporary tooltip that will be automatically removed later
        with dcg.utils.TemporaryTooltip(C, target=target, parent=target.parent):
            dcg.Text(C, value=f"Current time: {datetime.datetime.now().strftime('%H:%M:%S')}")
            dcg.Text(C, value="This tooltip is created dynamically")
        C.viewport.wake()
    
    # Attach hover handler to create tooltip
    dynamic_btn.handlers += [
        dcg.GotHoverHandler(C, callback=create_dynamic_tooltip)
    ]
    
    dcg.Separator(C)
    
    # Tooltip with custom appearance
    styled_btn = dcg.Button(C, label="Hover for styled tooltip")
    
    # Create a theme for the tooltip
    tooltip_theme = dcg.ThemeColorImGui(C, 
                                        window_bg=(50, 50, 70, 230),  # Dark blue background
                                        text=(220, 220, 255))        # Light text
    
    with dcg.Tooltip(C, target=styled_btn, theme=tooltip_theme):
        dcg.Text(C, value="This tooltip has custom styling")
        dcg.Text(C, value="You can customize colors and appearance")
    
    dcg.Separator(C)
    
    # Multiple tooltips with shared value
    shared_tooltip_text = dcg.SharedStr(C, value="I'm a shared tooltip message!")
    
    with dcg.HorizontalLayout(C):
        for i in range(3):
            btn = dcg.Button(C, label=f"Button {i+1}")
            with dcg.Tooltip(C, target=btn):
                dcg.Text(C, shareable_value=shared_tooltip_text)
    
    # Control to change the shared tooltip text
    dcg.InputText(C, 
                 label="Change shared tooltip", 
                 shareable_value=shared_tooltip_text,
                 width=300)

@demosection(dcg.Window, dcg.os.show_open_file_dialog, dcg.os.show_open_folder_dialog, dcg.os.show_save_file_dialog)
@documented
@democode
def _popups_and_modals(C: dcg.Context):
    """
    ## Popups and Modal Windows
    
    Create temporary UI elements that appear on demand:
    
    - Context menus and popup windows
    - Modal dialogs that block interaction with other windows
    - Customizable positioning and behavior
    - OS-native file and folder selection dialogs
    
    Popups and modals help manage complex interfaces by showing content only when needed.
    """
    # Status text to show results of interactions
    status_text = dcg.Text(C, value="Click buttons to show popups and modals")
    
    dcg.Separator(C)
    
    # Basic popup window
    def show_basic_popup():
        # Create a popup window that appears near the button
        popup = dcg.Window(C, 
                          label="Basic Popup", 
                          popup=True,
                          width=300,
                          height=200,
                          x=400, y=300)
        
        with popup:
            dcg.Text(C, value="This is a basic popup window")
            dcg.Text(C, value="Click outside to close")
            
            def close_popup():
                popup.delete_item()
                status_text.value = "Basic popup was closed with button"
                C.viewport.wake()
                
            dcg.Button(C, label="Close Popup", callback=close_popup)
        C.viewport.wake()
    
    dcg.Button(C, label="Show Basic Popup", callback=show_basic_popup)
    
    dcg.Separator(C)
    
    # Modal dialog window
    def show_modal_dialog():
        # Create a modal window that blocks interaction with other windows
        modal = dcg.Window(C, 
                          label="Modal Dialog", 
                          modal=True,
                          no_resize=True,
                          width=350,
                          height=200,
                          x=400, y=300)
        
        with modal:
            dcg.Text(C, value="This is a modal dialog")
            dcg.Text(C, value="You must interact with this window before continuing")
            
            def close_modal():
                modal.delete_item()
                status_text.value = "Modal dialog was closed"
                C.viewport.wake()
                
            with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.CENTER):
                dcg.Button(C, label="OK", width=100, callback=close_modal)
    
    dcg.Button(C, label="Show Modal Dialog", callback=show_modal_dialog)
    
    dcg.Separator(C)
    
    # Confirmation dialog
    def show_confirmation_dialog():
        confirm_modal = dcg.Window(C, 
                                  label="Confirm Action", 
                                  modal=True,
                                  no_resize=True,
                                  width=350,
                                  height=150,
                                  x=400, y=300)
        
        with confirm_modal:
            dcg.Text(C, value="Are you sure you want to proceed?")
            
            def on_confirm():
                confirm_modal.delete_item()
                status_text.value = "Action confirmed!"
                C.viewport.wake()
                
            def on_cancel():
                confirm_modal.delete_item()
                status_text.value = "Action cancelled"
                C.viewport.wake()
                
            with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.RIGHT):
                dcg.Button(C, label="Cancel", width=100, callback=on_cancel)
                dcg.Button(C, label="Confirm", width=100, callback=on_confirm)
    
    dcg.Button(C, label="Show Confirmation Dialog", callback=show_confirmation_dialog)
    
    dcg.Separator(C)
    
    # Context menu example
    context_area = dcg.ChildWindow(C, 
                                  width=300, 
                                  height=100, 
                                  border=True, 
                                  label="Right-click here for context menu")
    
    with context_area:
        dcg.Text(C, value="Right click anywhere in this area")
    
    # Context menu functions
    def show_context_menu():
        menu = dcg.Window(C, 
                         label="Context Menu", 
                         popup=True, 
                         no_title_bar=True,
                         no_resize=True,
                         x=C.get_mouse_position()[0],
                         y=C.get_mouse_position()[1])
        
        with menu:
            dcg.Text(C, value="Context Menu")
            dcg.Separator(C)
            
            def menu_action(action):
                menu.delete_item()
                status_text.value = f"Selected: {action}"
                C.viewport.wake()
                
            dcg.Button(C, label="Cut", callback=lambda: menu_action("Cut"))
            dcg.Button(C, label="Copy", callback=lambda: menu_action("Copy"))
            dcg.Button(C, label="Paste", callback=lambda: menu_action("Paste"))
            dcg.Separator(C)
            dcg.Button(C, label="Cancel", callback=menu.delete_item)
    
    # Add right click handler to show context menu
    context_area.handlers += [
        dcg.MouseClickHandler(C, 
                             callback=lambda s, t: show_context_menu(),
                             button=dcg.MouseButton.RIGHT)
    ]
    
    dcg.Separator(C)
    
    # Form in a popup
    def show_form_popup():
        form_popup = dcg.Window(C, 
                               label="Form Popup", 
                               popup=True,
                               width=400,
                               height=300,
                               x=400, y=250)
        
        # Form data
        name = dcg.SharedStr(C, value="")
        email = dcg.SharedStr(C, value="")
        age = dcg.SharedFloat(C, value=25)
        subscribe = dcg.SharedBool(C, value=False)
        
        with form_popup:
            dcg.Text(C, value="Please fill out the form:")
            
            dcg.InputText(C, label="Name", shareable_value=name)
            dcg.InputText(C, label="Email", shareable_value=email)
            dcg.Slider(C, label="Age", print_format="%.0f", min_value=18, max_value=100, shareable_value=age)
            dcg.Checkbox(C, label="Subscribe to newsletter", shareable_value=subscribe)
            
            def submit_form():
                form_popup.delete_item()
                status_text.value = f"Form submitted: {name.value}, {email.value}, {age.value}, {subscribe.value}"
                C.viewport.wake()
                
            def cancel_form():
                form_popup.delete_item()
                status_text.value = "Form cancelled"
                C.viewport.wake()
                
            with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.RIGHT):
                dcg.Button(C, label="Cancel", width=100, callback=cancel_form)
                dcg.Button(C, label="Submit", width=100, callback=submit_form)
        C.viewport.wake()
    
    dcg.Button(C, label="Show Form Popup", callback=show_form_popup)
    
    dcg.Separator(C)
    
    # Notification/toast popup
    def show_notification():
        # Create notification at bottom right
        notif = dcg.Window(C, 
                          popup=True,
                          no_title_bar=True,
                          no_resize=True,
                          width=250,
                          height=80,
                          x=float(C.viewport.width) - 260, y=float(C.viewport.height) - 90)
        
        with notif:
            dcg.Text(C, value="Notification", color=(255, 255, 0))
            dcg.Text(C, value="This is a temporary notification popup")
            
        # Auto-close after 3 seconds
        def start_timer():
            notif.user_data = time.monotonic()
        def close_notification():
            if time.monotonic() - notif.user_data > 3.0:
                notif.delete_item()
                C.viewport.wake()
        notif.handlers = [
            dcg.GotRenderHandler(C, callback=start_timer),
            dcg.RenderHandler(C, callback=close_notification)
        ]
        C.viewport.wake()
    
    dcg.Button(C, label="Show Notification", callback=show_notification)

    # Section for OS File Dialogs
    dcg.Separator(C, height=20)
    dcg.Text(C, value="OS Native File Dialogs:", color=(255, 255, 0))
    
    # Open file dialog
    def open_file_callback(file_paths):
        if file_paths and len(file_paths) > 0:
            status_text.value = f"Selected file(s): {', '.join(file_paths)}"
        else:
            status_text.value = "File selection cancelled or no files selected"
        C.viewport.wake()
    
    def show_open_file():
        # Define filter types
        filters = [
            ("Text Files", "txt"),
            ("Python Files", "py"),
            ("All Files", "*")
        ]
        
        # Show the open file dialog
        dcg.os.show_open_file_dialog(
            C,
            callback=open_file_callback,
            default_location="~/Documents",
            allow_multiple_files=True,
            filters=filters,
            title="Select File(s) to Open"
        )
    
    dcg.Button(C, label="Open File Dialog", callback=show_open_file)
    
    # Save file dialog
    def save_file_callback(file_paths):
        if file_paths and len(file_paths) > 0:
            status_text.value = f"File will be saved to: {file_paths[0]}"
        else:
            status_text.value = "Save operation cancelled"
        C.viewport.wake()
    
    def show_save_file():
        # Define filter types
        filters = [
            ("Text Files", "txt"),
            ("CSV Files", "csv"),
            ("All Files", "*")
        ]
        
        # Show the save file dialog
        dcg.os.show_save_file_dialog(
            C,
            callback=save_file_callback,
            default_location="~/Documents/myfile.txt",
            filters=filters,
            title="Save File As"
        )
    
    dcg.Button(C, label="Save File Dialog", callback=show_save_file)
    
    # Folder select dialog
    def folder_callback(folder_paths):
        if folder_paths and len(folder_paths) > 0:
            status_text.value = f"Selected folder(s): {', '.join(folder_paths)}"
        else:
            status_text.value = "Folder selection cancelled or no folder selected"
        C.viewport.wake()
    
    def show_folder_dialog():
        # Show the folder selection dialog
        dcg.os.show_open_folder_dialog(
            C,
            callback=folder_callback,
            default_location="~/Documents",
            allow_multiple_files=False,
            title="Select a Folder"
        )
    
    dcg.Button(C, label="Select Folder Dialog", callback=show_folder_dialog)
    
    # Example with custom button labels
    def show_custom_dialog():
        # Define filter types
        filters = [
            ("Image Files", "png;jpg;jpeg")
        ]
        
        # Show the open file dialog with custom button labels
        dcg.os.show_open_file_dialog(
            C,
            callback=open_file_callback,
            default_location="~/Pictures",
            filters=filters,
            title="Choose Image",
            accept="Select Image",
            cancel="Nevermind"
        )
    
    dcg.Button(C, label="Dialog with Custom Labels", callback=show_custom_dialog)

@demosection
@documented
def _handlers_events(C: dcg.Context):
    """
    ## Handlers and Event Management
    
    DearCyGui's handler system provides rich interaction control:
    
    - Respond to hovering, clicking, focusing, and other events
    - Combine multiple conditions with handler lists
    - Create custom handlers for specialized behavior
    
    Handlers allow fine-grained control over how widgets respond to user interaction.

    Essentially each UI items has a set of internal states.
    These states can be:
    - `active`: Is the item pressed ? It is selected ? etc.
    - `focused`: For windows it means the window is at the top,
        while for items it could mean the keyboard inputs are redirected to it.
    - `hovered`: Is the mouse over the item ?
    - `visible`: Is the item 'visible'/cpu rendered (might still be clipped though)

    These states can be read as item attributes. Not all of them are accessible depending
    on the item type. For example, `active` is not available for text.

    
    In addition to these states, the items also track transient states:
    `activated`, `deactivated`, `clicked`, `double_clicked`, `edited`, `resized`,
    `toggled`. However as there states may change every frame rendered, it is not
    reliable to check them frequently (unless done in the thread that calls `render_frame`).

    Rather than checking theses states, it is recommanded to instead use handlers to
    trigger actions when a specific state combination is met.
    Handlers are basically cheap functions that check the state of the items they
    are attached to, and trigger a callback when the state is met.

    Handlers must be attached to the `handlers` attribute of an item.

    """
    for handler in [
        # State handlers
        dcg.ActiveHandler,
        dcg.FocusHandler,
        dcg.HoverHandler,
        
        # State transition handlers
        dcg.ActivatedHandler,
        dcg.DeactivatedHandler,
        dcg.GotFocusHandler,
        dcg.LostFocusHandler,
        dcg.GotHoverHandler,
        dcg.LostHoverHandler,
        
        # Mouse interaction handlers
        dcg.ClickedHandler,
        dcg.DoubleClickedHandler,
        dcg.MouseOverHandler,
        dcg.GotMouseOverHandler,
        dcg.LostMouseOverHandler,
        dcg.MouseCursorHandler,
        dcg.MouseInRect,
        
        # Mouse event handlers
        dcg.MouseClickHandler,
        dcg.MouseDoubleClickHandler,
        dcg.MouseDownHandler,
        dcg.MouseReleaseHandler,
        dcg.MouseMoveHandler,
        dcg.MouseDragHandler,
        dcg.MouseWheelHandler,
        
        # Dragging handlers
        dcg.DraggedHandler,
        dcg.DraggingHandler,

        # Editing handlers
        dcg.EditedHandler,
        dcg.DeactivatedAfterEditHandler,
        dcg.MotionHandler,
        
        # Layout/window handlers
        dcg.ResizeHandler,
        dcg.ContentResizeHandler,
        dcg.AxesResizeHandler,
        
        # Tree/collapsing handlers
        dcg.OpenHandler,
        dcg.CloseHandler,
        dcg.ToggledOpenHandler,
        dcg.ToggledCloseHandler,
        
        # Keyboard handlers
        dcg.KeyDownHandler,
        dcg.KeyPressHandler,
        dcg.KeyReleaseHandler,
        
        # Rendering handlers
        dcg.RenderHandler,
        dcg.GotRenderHandler,
        dcg.LostRenderHandler,
        
        # Advanced handlers
        dcg.CustomHandler,
        dcg.ConditionalHandler,
        dcg.HandlerList,
    ]:
        with dcg.TreeNode(C, label=handler.__name__):
            display_item_documentation(C, handler)

pop_group()  # End Interactivity Features

push_group("Styling and Theming")

@demosection(dcg.ThemeColorImGui, dcg.ThemeStyleImGui)
@documented
@democode
def _theme_colors(C: dcg.Context):
    """
    ## Theme Colors
    
    Control the appearance of widgets with theme colors:
    
    - Apply colors to specific widgets or widget categories
    - Create and reuse theme objects
    - Hierarchical theme application
    
    Themes help create visually cohesive interfaces and customize appearance.
    """
    # Create a theme with custom colors
    custom_theme = dcg.ThemeColorImGui(C,
        # Text and background colors
        text=(255, 255, 255),          # White text
        text_disabled=(128, 128, 128),  # Gray text for disabled items
        window_bg=(40, 40, 40),         # Dark background
        
        # Button colors
        button=(70, 70, 170),          # Blue button
        button_hovered=(90, 90, 200),   # Lighter blue when hovered
        button_active=(110, 110, 240),  # Even lighter blue when pressed
        
        # Frame colors (sliders, input fields, etc.)
        frame_bg=(60, 60, 60),          # Dark gray frames
        frame_bg_hovered=(80, 80, 80),   # Lighter when hovered
        frame_bg_active=(100, 100, 100), # Even lighter when active
        
        # Header colors (collapsing headers, tree nodes)
        header=(70, 100, 170),         # Blue headers
        header_hovered=(90, 120, 200),  # Lighter when hovered
        header_active=(110, 140, 240),  # Even lighter when active
    )

    # Create a demo section with the custom theme
    with dcg.ChildWindow(C, width=500, height=300, border=True, theme=custom_theme):
        dcg.Text(C, value="This section uses a custom dark blue theme")
        
        # Basic widgets with the theme applied
        dcg.Button(C, label="Themed Button")
        dcg.Checkbox(C, label="Themed Checkbox")
        dcg.Slider(C, label="Themed Slider", min_value=0.0, max_value=1.0, value=0.5)
        
        # Input fields
        dcg.InputText(C, label="Themed Text Input", hint="Enter text here")
        
        # Tree nodes
        with dcg.TreeNode(C, label="Themed Tree Node"):
            dcg.Text(C, value="Tree node content")
            dcg.Button(C, label="Button in tree")

    # Example of applying themes to specific widgets
    dcg.Text(C, value="\nThemes can be applied to individual widgets:")
    
    # Create themes for specific widgets
    red_button_theme = dcg.ThemeColorImGui(C,
        button=(180, 50, 50),           # Red button
        button_hovered=(220, 80, 80),    # Lighter red when hovered
        button_active=(255, 100, 100),   # Even lighter red when pressed
    )
    
    green_button_theme = dcg.ThemeColorImGui(C,
        button=(50, 180, 50),           # Green button
        button_hovered=(80, 220, 80),    # Lighter green when hovered
        button_active=(100, 255, 100),   # Even lighter green when pressed
    )
    
    # Apply themes to individual widgets
    with dcg.HorizontalLayout(C):
        dcg.Button(C, label="Default Button")
        dcg.Button(C, label="Red Button", theme=red_button_theme)
        dcg.Button(C, label="Green Button", theme=green_button_theme)
    
    # Theme overriding and inheritance
    dcg.Text(C, value="\nThemes can be combined using ThemeList:")
    
    # Create a base theme and an accent theme
    base_theme = dcg.ThemeColorImGui(C,
        text=(220, 220, 220),          # Light gray text
        window_bg=(50, 50, 60),         # Dark blue-gray background
        frame_bg=(70, 70, 80),          # Slightly lighter frames
    )
    
    accent_theme = dcg.ThemeColorImGui(C,
        button=(180, 100, 100),        # Red-ish button
        check_mark=(255, 128, 128),     # Light red checkmarks
    )
    
    # Combine themes using ThemeList
    with dcg.ThemeList(C) as combined_theme:
        base_theme
        accent_theme
    
    # Apply the combined theme
    with dcg.ChildWindow(C, width=500, height=150, border=True, theme=combined_theme):
        dcg.Text(C, value="This section uses a combined theme (base + accent)")
        dcg.Button(C, label="Combined Theme Button")
        dcg.Checkbox(C, label="Combined Theme Checkbox")
        dcg.InputText(C, label="Combined Theme Input")

@demosection(dcg.ThemeColorImGui, dcg.ThemeStyleImGui)
@documented
@democode
def _theme_styles(C: dcg.Context):
    """
    ## Theme Styles
    
    Theme styles control widget sizing, spacing, and geometry:
    
    - Adjust padding, margins, and spacing
    - Control rounding and borders
    - Set default sizes and alignments
    
    Style themes complement color themes to create a complete visual identity.
    """
    # Create a style theme with modified properties
    rounded_style = dcg.ThemeStyleImGui(C,
        # Rounding
        window_rounding=10.0,           # Rounded window corners
        frame_rounding=5.0,             # Rounded frames
        popup_rounding=5.0,             # Rounded popups
        scrollbar_rounding=12.0,        # Rounded scrollbars
        grab_rounding=5.0,              # Rounded grab handles (sliders)
        tab_rounding=6.0,               # Rounded tabs
        button_text_align=(0.5, 0.5),    # Center button text
        
        # Border and frame sizes
        window_border_size=1.0,          # Window borders
        frame_border_size=1.0,           # Frame borders
        popup_border_size=1.0,           # Popup borders
        
        # Padding and spacing
        window_padding=(12, 12),        # Window padding
        frame_padding=(8, 4),           # Frame padding
        item_spacing=(8, 6),            # Spacing between items
        item_inner_spacing=(6, 4),       # Inner item spacing
        cell_padding=(5, 5),            # Table cell padding
        
        # Scrollbar and grab sizes
        scrollbar_size=16.0,            # Width of scrollbars
        grab_min_size=12.0,              # Min size of slider grab
    )
    
    # Create a color theme to pair with the style
    modern_color = dcg.ThemeColorImGui(C,
        text=(220, 220, 220),          # Light text
        window_bg=(45, 45, 48),         # Dark background
        border=(60, 60, 70),           # Visible border
        popup_bg=(55, 55, 63),          # Slightly lighter popup background
        frame_bg=(65, 65, 70),          # Frame background
        
        # Button colors
        button=(75, 75, 85),           # Button color
        button_hovered=(95, 95, 105),   # Button hover
        button_active=(125, 125, 140),  # Button active
        
        # Highlight colors
        header_active=(85, 130, 170),   # Active header
        check_mark=(130, 160, 200),     # Checkmark
        slider_grab=(130, 150, 190),    # Slider grab
        slider_grab_active=(150, 170, 210), # Active slider
    )
    
    # Combine style and color themes
    with dcg.ThemeList(C) as modern_theme:
        modern_color
        rounded_style
    
    # Apply the combined theme
    with dcg.ChildWindow(C, width=500, height=350, border=True, theme=modern_theme):
        dcg.Text(C, value="This section uses a modern theme with custom styling")
        
        # Display various widgets to show the styling
        dcg.Button(C, label="Rounded Button")
        
        with dcg.HorizontalLayout(C):
            dcg.Checkbox(C, label="Checkbox 1")
            dcg.Checkbox(C, label="Checkbox 2")
        
        dcg.Slider(C, label="Styled Slider", min_value=0.0, max_value=1.0, value=0.7)
        dcg.InputText(C, label="Styled Input", hint="Type here")
        
        # Show tabs with the styling
        with dcg.TabBar(C):
            with dcg.Tab(C, label="Tab 1"):
                dcg.Text(C, value="Content of Tab 1")
                dcg.Button(C, label="Button in Tab 1")
                
            with dcg.Tab(C, label="Tab 2"):
                dcg.Text(C, value="Content of Tab 2")
                dcg.Checkbox(C, label="Checkbox in Tab 2")
    
    # Demonstrating style variations
    dcg.Text(C, value="\nComparing different style configurations:")
    
    with dcg.HorizontalLayout(C):
        # Default style reference
        with dcg.ChildWindow(C, width=200, height=200, border=True, label="Default Style"):
            dcg.Button(C, label="Button")
            dcg.Checkbox(C, label="Checkbox")
            dcg.Slider(C, label="Slider", value=0.5)
            with dcg.TreeNode(C, label="Tree Node"):
                dcg.Text(C, value="Content")
        
        # Compact style
        compact_style = dcg.ThemeStyleImGui(C,
            window_padding=(4, 4),
            frame_padding=(4, 2),
            item_spacing=(4, 3),
            item_inner_spacing=(3, 2),
            frame_rounding=0,
        )
        
        with dcg.ChildWindow(C, width=200, height=200, border=True, label="Compact Style", theme=compact_style):
            dcg.Button(C, label="Button")
            dcg.Checkbox(C, label="Checkbox")
            dcg.Slider(C, label="Slider", value=0.5)
            with dcg.TreeNode(C, label="Tree Node"):
                dcg.Text(C, value="Content")
        
        # Highly rounded style
        rounded_bold_style = dcg.ThemeStyleImGui(C,
            window_padding=(12, 12),
            frame_padding=(10, 8),
            item_spacing=(10, 8),
            window_rounding=12.0,
            frame_rounding=12.0,
            grab_rounding=12.0,
            frame_border_size=2.0,
            grab_min_size=20.0,
        )
        
        with dcg.ChildWindow(C, width=200, height=200, border=True, label="Bold Rounded", theme=rounded_bold_style):
            dcg.Button(C, label="Button")
            dcg.Checkbox(C, label="Checkbox")
            dcg.Slider(C, label="Slider", value=0.5)
            with dcg.TreeNode(C, label="Tree Node"):
                dcg.Text(C, value="Content")

@demosection(dcg.SharedValue)
@documented
@democode
def _shared_values(C: dcg.Context):
    """
    ## Shared Values
    
    Shared values provide a way to connect and synchronize widgets:
    
    - Link multiple widgets to the same data source
    - Update UI automatically when values change
    - Support various types: bool, float, string, etc.
    
    Shared values simplify state management and keep your interface consistent.
    """
    # Create shared values of different types
    text_value = dcg.SharedStr(C, value="Hello, World!")
    int_value = dcg.SharedFloat(C, value=50)
    float_value = dcg.SharedFloat(C, value=0.75)
    bool_value = dcg.SharedBool(C, value=True)
    color_value = dcg.SharedColor(C, value=(100, 150, 200, 255))
    
    # Create a section for text value demonstration
    with dcg.ChildWindow(C, width=500, height=150, border=True, label="Shared Text Value") as cw:
        # Multiple widgets connected to the same text value
        dcg.Text(C, value="Shared text value demonstration:")
        
        # Input field that modifies the shared value
        dcg.InputText(C, label="Edit Text", shareable_value=text_value)
        
        # Displays that show the same value
        dcg.Text(C, shareable_value=text_value)
        dcg.Text(C, shareable_value=text_value)
        
        # Button that modifies the shared value
        def change_text():
            text_value.value = "Text changed by button!"
            C.viewport.wake()
            
        dcg.Button(C, label="Change Text", callback=change_text)
    
    # Create a section for numeric value demonstration
    with dcg.ChildWindow(C, width=500, height=200, border=True, label="Shared Numeric Values"):
        # Shared integer value
        dcg.Text(C, value="Shared integer value:")
        
        # Slider that modifies the integer
        dcg.Slider(C, label="Integer Slider", print_format="%.0f", 
                  min_value=0, max_value=100, shareable_value=int_value)
        
        # Input that modifies the same integer
        dcg.InputValue(C, label="Integer Input", print_format="%.0f", shareable_value=int_value)

        
        # Shared float value
        dcg.Text(C, value="Shared float value:")
        
        # Slider for the float
        dcg.Slider(C, label="Float Slider", 
                  min_value=0.0, max_value=1.0, shareable_value=float_value)
        
        # Input for the same float
        dcg.InputValue(C, label="Float Input",
                      min_value=0.0, max_value=1.0, shareable_value=float_value)

        # Progress bar that shows the same value
        dcg.ProgressBar(C, shareable_value=float_value)
    
    # Create a section for boolean and color values
    with dcg.ChildWindow(C, width=500, height=200, border=True, label="Boolean and Color Values"):
        # Shared boolean
        dcg.Text(C, value="Shared boolean value:")
        
        with dcg.HorizontalLayout(C):
            # Checkbox that controls the boolean
            dcg.Checkbox(C, label="Toggle", shareable_value=bool_value)
            
            # Text that shows the boolean state
            dcg.TextValue(C, shareable_value=bool_value, 
                          print_format="Current state: %d")
        
        # Shared color value
        dcg.Text(C, value="Shared color value:")
        
        # Color edit widget
        dcg.ColorEdit(C, label="Edit Color", shareable_value=color_value)
        
        # Color button using the same value
        dcg.ColorButton(C, label="Color Button", shareable_value=color_value)
        
        # Show color components as text
        dcg.TextValue(C, shareable_value=color_value, 
                     print_format="RGB: %f, %f, %f, Alpha: %f")


pop_group()  # End Styling and Theming


if __name__ == "__main__":
    launch_demo(title="Widgets Demo")
