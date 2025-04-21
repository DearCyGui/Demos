from demo_utils import documented, democode, push_group, pop_group, launch_demo, demosection
import dearcygui as dcg

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
    Note aach widget has its own set of properties and methods that allow you to control its behavior and appearance.
    """
    pass

push_group("Basic Widgets")

@demosection
@documented
@democode
def _text_widgets(C: dcg.Context):
    """
    ## Text Display Widgets
    
    DearCyGui offers various ways to display text:
    
    - `Text`: Simple text display with optional coloring and formatting
    - `TextValue`: Displays the value from a shared variable 
    - Text wrapping and formatting options
    
    Text widgets are the foundation for labels, descriptions, and displaying information.
    """
    ...

@demosection
@documented
@democode
def _button_widgets(C: dcg.Context):
    """
    ## Button Widgets
    
    Buttons are the primary interactive elements in a UI:
    
    - Standard buttons with text labels
    - Small buttons for compact layouts
    - Arrow buttons for navigation
    - Image buttons for visual interfaces
    - Repeat buttons that trigger continuously when held
    
    Buttons can trigger callbacks when clicked, allowing your application to respond to user actions.
    """
    ...

@demosection
@documented
@democode
def _checkbox_radio(C: dcg.Context):
    """
    ## Checkboxes and Radio Buttons
    
    Checkboxes and radio buttons allow users to toggle options or select from a set of choices:
    
    - `Checkbox`: Toggle boolean values on/off
    - `RadioButton`: Select one option from a group of related items
    
    These widgets provide visual feedback for binary and exclusive selection patterns.
    """
    ...

@demosection
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
    ...

@demosection
@documented
@democode
def _sliders(C: dcg.Context):
    """
    ## Sliders and Drag Controls
    
    Sliders and drag controls provide intuitive ways to adjust numeric values:
    
    - `Slider`: Adjust values by dragging along a track
    - Vertical and horizontal orientations
    - Integer, float, and multi-component options
    - Drag controls for precision adjustment
    
    These widgets are ideal for controlling parameters with visual feedback.
    """
    ...

pop_group()  # End Basic Widgets

push_group("Selection Widgets")

@demosection
@documented
@democode
def _combo_boxes(C: dcg.Context):
    """
    ## Combo Boxes (Dropdowns)
    
    Combo boxes (also known as dropdowns) allow selecting one item from a list:
    
    - Compact representation of selection options
    - Scrollable list when opened
    - Configurable size and appearance
    - Optional preview control
    
    Combo boxes are useful when you want to save screen space while offering multiple options.
    """
    ...

@demosection
@documented
@democode
def _list_boxes(C: dcg.Context):
    """
    ## List Boxes
    
    List boxes display a scrollable set of selectable items:
    
    - Always-visible list of options
    - Single or multi-selection modes
    - Customizable height and visible items
    
    List boxes are useful when you want to keep all options visible at once.
    """
    ...

@demosection
@documented
@democode
def _selectables(C: dcg.Context):
    """
    ## Selectables
    
    Selectables are flexible elements that can be clicked to toggle selection state:
    
    - Text items that can be selected/highlighted
    - Support for single and multi-selection patterns
    - Customizable appearance when selected
    
    Selectables can be arranged in various layouts to create custom selection interfaces.
    """
    ...

@demosection
@documented
@democode
def _trees_and_nodes(C: dcg.Context):
    """
    ## Trees and Tree Nodes
    
    Trees allow hierarchical organization of content:
    
    - `TreeNode`: Collapsible sections that can contain any widgets
    - `CollapsingHeader`: Similar to TreeNode, with a different visual style
    - Support for hierarchy, nesting, and organization
    
    Trees are excellent for organizing complex, hierarchical data and interfaces.
    """
    ...

pop_group()  # End Selection Widgets

push_group("Layout Containers")

@demosection
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
    ...

@demosection
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
    ...

@demosection
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
    ...

@demosection
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
    ...

pop_group()  # End Layout Containers

push_group("Advanced Widgets")

@demosection
@documented
@democode
def _tables(C: dcg.Context):
    """
    ## Tables
    
    Tables provide grid-based layout for structured data:
    
    - Row and column organization
    - Cell customization with any widget
    - Headers, borders, and styling options
    - Sorting, filtering, and selection capabilities
    
    Tables are ideal for displaying structured data that needs organization and interactivity.
    """
    ...

@demosection
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
    ...

@demosection
@documented
@democode
def _image_display(C: dcg.Context):
    """
    ## Images
    
    DearCyGui can display images and image-based controls:
    
    - `Image`: Simple display of image data
    - `ImageButton`: Clickable image that works like a button
    - Control scaling, tinting, and borders
    
    Images can be loaded from textures and customized with various display options.
    """
    ...

@demosection
@documented
@democode
def _progress_bars(C: dcg.Context):
    """
    ## Progress Bars and Simple Plots
    
    Visualize progress and simple data:
    
    - `ProgressBar`: Show completion status of operations
    - `SimplePlot`: Display simple data visualizations
    
    These widgets help provide visual feedback for processes and data trends.
    """
    ...

pop_group()  # End Advanced Widgets

push_group("Interactivity Features")

@demosection
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
    ...

@demosection
@documented
@democode
def _popups_and_modals(C: dcg.Context):
    """
    ## Popups and Modal Windows
    
    Create temporary UI elements that appear on demand:
    
    - Context menus and popup windows
    - Modal dialogs that block interaction with other windows
    - Customizable positioning and behavior
    
    Popups and modals help manage complex interfaces by showing content only when needed.
    """
    ...

@demosection
@documented
@democode
def _handlers(C: dcg.Context):
    """
    ## Handlers and Event Management
    
    DearCyGui's handler system provides rich interaction control:
    
    - Respond to hovering, clicking, focusing, and other events
    - Combine multiple conditions with handler lists
    - Create custom handlers for specialized behavior
    
    Handlers allow fine-grained control over how widgets respond to user interaction.
    """
    ...

@demosection
@documented
@democode
def _drag_and_drop(C: dcg.Context):
    """
    ## Drag and Drop
    
    Implement drag and drop interactions within your interface:
    
    - Make widgets draggable sources
    - Create drop targets for receiving dragged content
    - Work with drag payloads for data transfer
    
    Drag and drop provides intuitive interaction for moving and organizing data.
    """
    ...

pop_group()  # End Interactivity Features

push_group("Styling and Theming")

@demosection
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
    ...

@demosection
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
    ...

@demosection
@documented
@democode
def _shared_values(C: dcg.Context):
    """
    ## Shared Values
    
    Shared values provide a way to connect and synchronize widgets:
    
    - Link multiple widgets to the same data source
    - Update UI automatically when values change
    - Support various types: bool, int, float, string, etc.
    
    Shared values simplify state management and keep your interface consistent.
    """
    ...

pop_group()  # End Styling and Theming

push_group("Practical Examples")

@demosection
@documented
@democode
def _form_example(C: dcg.Context):
    """
    ## Form Input Example
    
    A complete form implementation demonstrating:
    
    - Input validation and feedback
    - Layout organization for form fields
    - Handling form submission
    - Error messaging and confirmation
    
    This example shows how to combine basic widgets into a practical interface.
    """
    ...

@demosection
@documented
@democode
def _calculator_example(C: dcg.Context):
    """
    ## Simple Calculator
    
    A working calculator that demonstrates:
    
    - Grid-based button layout
    - Input and display coordination
    - Event handling for numeric input
    - State management for calculations
    
    This example shows how to create an interactive application with state.
    """
    ...

@demosection
@documented
@democode
def _settings_panel(C: dcg.Context):
    """
    ## Settings Panel
    
    A complete settings interface that demonstrates:
    
    - Organized categories with tabs or tree nodes
    - Various input types for different settings
    - Real-time preview of setting changes
    - Settings persistence pattern
    
    This example shows how to create structured configuration interfaces.
    """
    ...

pop_group()  # End Practical Examples

if __name__ == "__main__":
    launch_demo(title="Widgets Demo")