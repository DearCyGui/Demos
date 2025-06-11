import dearcygui as dcg
import numpy as np
from demo_utils import documented, democode, push_group, pop_group,\
    launch_demo, demosection, display_item_documentation

push_group("Introduction")

@demosection
@documented
def _themes_intro(C: dcg.Context):
    """
    # Introduction to Themes in DearCyGui

    Themes in DearCyGui provide a powerful way to customize the appearance of your application.
    They allow you to control colors, styles, fonts, and other visual aspects of your UI elements.

    ## Types of Themes

    DearCyGui offers several theme types:
    
    - **ThemeColorImGui**: Controls colors for ImGui elements (basic UI widgets)
    - **ThemeStyleImGui**: Controls sizes, spacing, and other non-color properties for ImGui elements
    - **ThemeColorImPlot**: Controls colors for ImPlot elements (plots and graphs)
    - **ThemeStyleImPlot**: Controls sizes, spacing, and other non-color properties for ImPlot elements
    - **ThemeList**: Combines multiple themes into one

    ## Theme Inheritance System

    DearCyGui uses a hierarchical theme system:
    
    1. **Item Themes**: Applied directly to individual items
    2. **Parent Themes**: If an item doesn't have a specific theme property, it inherits from its parent
    3. **Global Themes**: Applied to the entire application via Viewport.theme
    
    This hierarchy enables both consistent global styling and targeted customization.

    ## Key Theme Concepts

    - **Theme Properties**: Each theme type has specific properties that control different visual aspects
    - **Property Inheritance**: Child items inherit theme properties from their parents unless overridden
    - **Theme Scope**: Some theme properties only affect specific types of items
    - **Theme Composition**: Themes can be combined using ThemeList to create complex visual styles

    The sections that follow will demonstrate these concepts with practical examples.
    """
    pass

pop_group()  # End Introduction


push_group("Basic Theme Usage")

@demosection(dcg.ThemeColorImGui, dcg.ThemeStyleImGui)
@documented
@democode
def _applying_themes(C: dcg.Context):
    """
    ## Applying Themes to Items

    You can apply themes to UI elements in several ways:

    1. **Directly to individual items**: Pass the theme as a parameter when creating the item
    2. **To containers**: Apply a theme to a container to affect all its children
    3. **Globally**: Set a theme as the Viewport's theme to affect the entire application

    This example shows different ways to apply themes.
    """
    # Create some themes
    blue_theme = dcg.ThemeColorImGui(C, 
                                    button=(100, 130, 230),  # Button color
                                    button_hovered=(130, 160, 255),  # Button hover color
                                    button_active=(90, 120, 200))  # Button active color
    
    green_theme = dcg.ThemeColorImGui(C,
                                     button=(80, 170, 90),  # Button color
                                     button_hovered=(100, 200, 110),  # Button hover color
                                     button_active=(70, 150, 80))  # Button active color

    # Method 1: Apply theme directly to an individual item
    dcg.Text(C, value="1. Theme applied directly to an individual item:")
    dcg.Button(C, label="Blue Button", theme=blue_theme)
    dcg.Button(C, label="Green Button", theme=green_theme)
    dcg.Button(C, label="Default Button")  # No theme specified

    dcg.Separator(C)

    # Method 2: Apply theme to a container
    dcg.Text(C, value="2. Theme applied to a container (affects all children):")
    with dcg.ChildWindow(C, width=300, height=100, theme=blue_theme):
        dcg.Text(C, value="This container has the blue theme")
        dcg.Button(C, label="Inherits Blue Theme")  # Inherits theme from parent
        dcg.Button(C, label="Overridden Theme", theme=green_theme)  # Overrides parent's theme

@demosection(dcg.ThemeColorImGui, dcg.ThemeStyleImGui)
@documented
@democode
def _theme_inheritance(C: dcg.Context):
    """
    ## Theme Inheritance

    Theme properties are inherited from parent items to child items. This creates a
    hierarchical styling system that allows for both global consistency and local customization.

    Key inheritance rules:
    1. If an item has a theme with a specific property set, that property is used
    2. If not, the property is inherited from the nearest parent that has it defined
    3. If no parent defines the property, the default value is used

    This example demonstrates how theme properties are inherited.
    """
    # Create parent theme with text and window background color
    parent_theme = dcg.ThemeColorImGui(C,
                                      text=(220, 220, 255),  # Light blue text
                                      window_bg=(40, 40, 60))  # Dark blue background
    
    # Create child theme with just button colors
    button_theme = dcg.ThemeColorImGui(C,
                                      button=(200, 100, 100),  # Red buttons
                                      button_hovered=(230, 120, 120))
    
    # Create a window with the parent theme
    with dcg.ChildWindow(C, width=450, height=300, label="Theme Inheritance Demo", 
                      border=True, theme=parent_theme):
        
        dcg.Text(C, value="This text inherits its color from the parent theme")
        dcg.Button(C, label="This button uses default colors")
        
        # Create a child window with just button theme
        with dcg.ChildWindow(C, width=400, height=200, label="Child Window", border=True, 
                          theme=button_theme):
            dcg.Text(C, value="This text still inherits from the parent window's theme")
            dcg.Button(C, label="This button uses the child theme's color")
            
            # Override specific property
            override_theme = dcg.ThemeColorImGui(C, text=(255, 255, 100))  # Yellow text
            dcg.Text(C, value="This text has its own color theme", theme=override_theme)
            
            # Button still uses the button_theme
            dcg.Button(C, label="Still using child window's button theme")
    
    dcg.Text(C, value="Key points about theme inheritance:", color=(255, 255, 0))
    dcg.Text(C, value="1. Properties cascade down from parents to children")
    dcg.Text(C, value="2. More specific themes (closer to the item) take precedence")
    dcg.Text(C, value="3. Individual properties can be overridden without affecting others")

@demosection(dcg.ThemeList, dcg.ThemeColorImGui, dcg.ThemeStyleImGui)
@documented
@democode
def _theme_composition(C: dcg.Context):
    """
    ## Theme Composition with ThemeList

    ThemeList allows you to combine multiple themes into a single theme. 
    This is particularly useful for:
    
    1. Separating color and style definitions
    2. Creating theme variations by combining base themes with override themes
    3. Organizing themes by category or purpose
    
    When combining themes, properties from themes defined later in the list will 
    override properties from earlier themes if they target the same attribute.
    """
    # Create base themes
    base_colors = dcg.ThemeColorImGui(C,
                                     window_bg=(35, 35, 45),  # Dark background
                                     text=(200, 200, 200),   # Light grey text
                                     border=(60, 60, 80))    # Border color
    
    base_styles = dcg.ThemeStyleImGui(C,
                                     window_padding=(10, 10),
                                     frame_padding=(8, 4),
                                     item_spacing=(10, 8),
                                     window_rounding=5.0,
                                     frame_rounding=4.0,
                                     scrollbar_size=14.0)
    
    # Create theme variations for buttons
    blue_buttons = dcg.ThemeColorImGui(C,
                                      button=(80, 100, 180),
                                      button_hovered=(100, 120, 210),
                                      button_active=(70, 90, 160))
    
    green_buttons = dcg.ThemeColorImGui(C,
                                       button=(80, 170, 90),
                                       button_hovered=(100, 200, 110),
                                       button_active=(70, 150, 80))
    
    # Combine base themes with button variations
    blue_theme = dcg.ThemeList(C)
    blue_theme.children = [
        base_colors,
        base_styles,
        blue_buttons
    ]
    green_theme = dcg.ThemeList(C)
    green_theme.children = [
        base_colors.copy(), # Copy because can only be in one child tree
        base_styles.copy(),
        green_buttons
    ]
    
    # Demonstrate the combined themes
    with dcg.HorizontalLayout(C):
        # Blue theme variation
        with dcg.ChildWindow(C, width=300, height=250, label="Blue Theme", theme=blue_theme):
            dcg.Text(C, value="This window uses the blue theme variation")
            dcg.Button(C, label="Blue Button")
            dcg.InputText(C, label="Input Field")
            dcg.Checkbox(C, label="Checkbox")
        
        # Green theme variation
        with dcg.ChildWindow(C, width=300, height=250, label="Green Theme", theme=green_theme):
            dcg.Text(C, value="This window uses the green theme variation")
            dcg.Button(C, label="Green Button")
            dcg.InputText(C, label="Input Field")
            dcg.Checkbox(C, label="Checkbox")
    
    dcg.Text(C, value="ThemeList benefits:", color=(255, 255, 0))
    dcg.Text(C, value="1. Create theme variations with minimal duplication")
    dcg.Text(C, value="2. Separate styles from colors for better organization")
    dcg.Text(C, value="3. Override specific properties while keeping a consistent base style")

pop_group()  # End Basic Theme Usage


push_group("Theme Properties")

@demosection(dcg.ThemeColorImGui, dcg.color_as_ints, dcg.color_as_floats, dcg.color_as_int)
@documented
@democode
def _theme_color_imgui(C: dcg.Context):
    """
    ## ThemeColorImGui Properties

    `ThemeColorImGui` controls the colors of ImGui elements (standard UI widgets).
    Colors can be specified as:
    
    - RGB tuples: (255, 0, 0) for red
    - RGBA tuples: (255, 0, 0, 128) for semi-transparent red
    - Values are either floats in range [0, 1] or integers in range [0, 255].
    - A single integer (compressed RGBA tuple) is also accepted.

    Conversion can be performed using `dcg.color_as_ints`, `dcg.color_as_floats`
    or `dcg.color_as_int` functions.

    This example demonstrates the most commonly used ThemeColorImGui properties
    and their effects on different UI elements.
    """
    # Create a demonstration window for each theme category
    with dcg.HorizontalLayout(C):
        # Window and backgrounds
        with dcg.ChildWindow(C, width=200, height=400, label="Window & Backgrounds"):
            dcg.Text(C, value="Window themes control backgrounds and borders")
            
            # Demonstrate window background
            with dcg.ChildWindow(C, width=180, height=80, label="window_bg", 
                              theme=dcg.ThemeColorImGui(C, window_bg=(60, 50, 80))):
                dcg.Text(C, value="Window background")
            
            # Demonstrate popup background
            popup_bg_btn = dcg.Button(C, label="Show popup_bg")
            def show_popup_bg():
                popup = dcg.Window(C, label="popup_bg Demo", width=150, height=80, popup=True,
                                   x=400, y=300,
                                   theme=dcg.ThemeColorImGui(C, popup_bg=(80, 60, 60)))
                with popup:
                    dcg.Text(C, value="Popup background")
                    dcg.Button(C, label="Close", callback=popup.delete_item)
                C.viewport.wake()
            popup_bg_btn.callback = show_popup_bg
            
            # Demonstrate child background
            with dcg.ChildWindow(C, width=180, height=80, label="child_bg",
                              theme=dcg.ThemeColorImGui(C, child_bg=(50, 80, 50))):
                dcg.Text(C, value="Child window background")
            
            # Demonstrate frame background
            dcg.InputText(C, label="frame_bg", hint="Frame background",
                          theme=dcg.ThemeColorImGui(C, frame_bg=(80, 50, 50)))
            
            # Demonstrate border colors
            with dcg.ChildWindow(C, width=180, height=50, border=True, label="border",
                                 theme=dcg.ThemeColorImGui(C, border=(200, 150, 50))):
                dcg.Text(C, value="Border color")
        
        # Text colors
        with dcg.ChildWindow(C, width=200, height=400, label="Text Colors"):
            dcg.Text(C, value="Text color themes")
            
            # Standard text
            dcg.Text(C, value="Default text")
            dcg.Text(C, value="Custom text", theme=dcg.ThemeColorImGui(C, text=(255, 200, 0)))
            
            # Disabled text
            dcg.Text(C, value="text_disabled", theme=dcg.ThemeColorImGui(C, text_disabled=(150, 150, 200)))
            
            # Button text
            dcg.Button(C, label="Button text color",
                       theme=dcg.ThemeColorImGui(C, text=(255, 255, 255), button=(100, 50, 150)))
            
            # Text selection
            dcg.InputText(C, label="text_selected_bg", 
                          value="Select this text",
                          hint="Selection highlight color",
                          theme=dcg.ThemeColorImGui(C, 
                                    text_selected_bg=(100, 150, 200),
                                    frame_bg=(50, 50, 50)))
            
            # Header text
            with dcg.TreeNode(C, label="Header text colors",
                              theme=dcg.ThemeColorImGui(C, 
                                    header=(100, 100, 170),
                                    header_hovered=(120, 120, 190),
                                    header_active=(140, 140, 210))):
                dcg.Text(C, value="Header text in tree node")
        
        # Interactive elements
        with dcg.ChildWindow(C, width=200, height=400, label="Interactive Elements"):
            dcg.Text(C, value="Interactive element colors")
            
            # Button colors
            dcg.Button(C, label="Button colors",
                       theme=dcg.ThemeColorImGui(C, 
                                    button=(100, 150, 200),
                                    button_hovered=(120, 170, 220),
                                    button_active=(80, 130, 180)))
            
            # Checkbox colors
            dcg.Checkbox(C, label="check_mark color", value=True,
                         theme=dcg.ThemeColorImGui(C, 
                                    frame_bg=(60, 60, 80),
                                    check_mark=(255, 200, 100)))
            
            # Slider colors
            dcg.Slider(C, label="Slider colors", format="float",
                       theme=dcg.ThemeColorImGui(C, 
                                    frame_bg=(50, 50, 70),
                                    slider_grab=(100, 200, 150),
                                    slider_grab_active=(120, 220, 170)),
                       min_value=0, max_value=1, value=0.5)
            
            # Tab colors
            with dcg.TabBar(C, theme=dcg.ThemeColorImGui(C, 
                                    tab=(80, 100, 140),
                                    tab_hovered=(100, 120, 160),
                                    tab_selected=(140, 160, 200),
                                    tab_dimmed=(60, 80, 120),
                                    tab_dimmed_selected=(80, 100, 140),
                                    tab_dimmed_selected_overline=(100, 120, 160))):
                with dcg.Tab(C, label="Tab 1"):
                    dcg.Text(C, value="Tab colors")
                with dcg.Tab(C, label="Tab 2"):
                    dcg.Text(C, value="Tab 2 content")

    with dcg.TreeNode(C, label="View all ThemeColorImGui properties", value=True):
        display_item_documentation(C, dcg.ThemeColorImGui)

@demosection(dcg.ThemeStyleImGui)
@documented
@democode
def _theme_style_imgui(C: dcg.Context):
    """
    ## ThemeStyleImGui Properties

    `ThemeStyleImGui` controls the non-color style properties of ImGui elements,
    such as sizes, spacing, rounding, and other visual parameters.
    
    These properties affect the layout, dimensions, and shape of UI elements.
    Style properties are specified as:
    
    - Single float values: For sizes, radii, etc.
    - Tuples of two floats: For X,Y dimensions like padding and spacing
    
    This example demonstrates the most commonly used ThemeStyleImGui properties.
    """
    # Window padding
    window_padding_theme = dcg.ThemeStyleImGui(C, window_padding=(20, 20))
    with dcg.ChildWindow(C, label="window_padding: (20, 20)", 
                      width=250, height=100, theme=window_padding_theme):
        dcg.Text(C, value="Note the extra space around this text")
    
    # Frame padding
    frame_padding_theme = dcg.ThemeStyleImGui(C, frame_padding=(12, 8))
    with dcg.HorizontalLayout(C):
        dcg.Text(C, value="frame_padding: (12, 8)")
        dcg.Button(C, label="Normal Button")
        dcg.Button(C, label="Padded Button", theme=frame_padding_theme)
    
    # Item spacing
    item_spacing_theme = dcg.ThemeStyleImGui(C, item_spacing=(20, 15))
    with dcg.ChildWindow(C, label="item_spacing: (20, 15)", 
                      width=250, height=150, theme=item_spacing_theme):
        dcg.Text(C, value="These items have")
        dcg.Text(C, value="extra space")
        dcg.Text(C, value="between them")
    
    # Rounding
    with dcg.HorizontalLayout(C):
        # Window rounding
        window_rounding_theme = dcg.ThemeStyleImGui(C, window_rounding=10.0)
        with dcg.ChildWindow(C, label="window_rounding: 10.0", 
                          width=200, height=80, theme=window_rounding_theme):
            dcg.Text(C, value="Rounded window corners")
        
        # Frame rounding
        frame_rounding_theme = dcg.ThemeStyleImGui(C, frame_rounding=8.0)
        with dcg.ChildWindow(C, width=200, height=80, label="frame_rounding: 8.0", theme=frame_rounding_theme):
            dcg.Button(C, label="Rounded Button")
            dcg.InputText(C, label="Rounded Input", hint="Rounded corners")
    
    # Button text alignment
    button_align_theme = dcg.ThemeStyleImGui(C, button_text_align=(1.0, 0.5))  # Right-aligned
    with dcg.HorizontalLayout(C):
        dcg.Text(C, value="button_text_align:")
        dcg.Button(C, label="Default Aligned", width=150)
        dcg.Button(C, label="Right Aligned", width=150, theme=button_align_theme)
    
    # Combined style example
    with dcg.ThemeList(C) as combined_style:
        dcg.ThemeStyleImGui(C, 
                          window_rounding=8.0,
                          frame_rounding=4.0,
                          window_padding=(16, 16),
                          frame_padding=(10, 6),
                          item_spacing=(12, 8))
        dcg.ThemeColorImGui(C,
                          window_bg=(40, 42, 54),
                          frame_bg=(52, 55, 70),
                          button=(85, 95, 175))
    
    with dcg.ChildWindow(C, label="Combined Styles", width=350, height=150, theme=combined_style):
        dcg.Text(C, value="This demonstrates combining style and color themes")
        dcg.Button(C, label="Styled Button")
        dcg.InputText(C, label="Styled Input", hint="With combined styles")

    with dcg.TreeNode(C, label="View all ThemeStyleImGui properties", value=True):
        display_item_documentation(C, dcg.ThemeStyleImGui)

@demosection(dcg.ThemeColorImPlot, dcg.ThemeStyleImPlot)
@documented
@democode
def _theme_implot(C: dcg.Context):
    """
    ## ImPlot Themes

    DearCyGui provides specialized themes for plot elements:
    
    - `ThemeColorImPlot`: Controls colors of plot elements
    - `ThemeStyleImPlot`: Controls non-color properties of plot elements
    
    These themes work similarly to their ImGui counterparts but are specifically
    designed for customizing plots and visualizations.
    
    This example demonstrates some common ImPlot theme properties.
    """
    import numpy as np
    
    # Generate sample data for plots
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    # Basic default plot for comparison
    with dcg.Plot(C, label="Default Plot Style", height=300, width=-1):
        dcg.PlotLine(C, label="Sin(x)", X=x, Y=y1)
        dcg.PlotLine(C, label="Cos(x)", X=x, Y=y2)
        dcg.PlotScatter(C, label="Points", X=x[::10], Y=y1[::10])
    
    # Create custom plot colors
    plot_colors = dcg.ThemeColorImPlot(C,
                                      plot_bg=(30, 30, 40),           # Plot background
                                      plot_border=(70, 70, 100),      # Plot border
                                      line=(255, 160, 50),           # Default line color  
                                      axis_text=(200, 200, 220),      # Axis text
                                      axis_grid=(70, 70, 90),         # Grid lines
                                      legend_bg=(40, 40, 60, 230),    # Legend background
                                      legend_border=(70, 70, 100),    # Legend border
                                      legend_text=(220, 220, 240),    # Legend text
                                      title_text=(255, 200, 60))      # Title text
    
    # Create custom plot styles
    plot_styles = dcg.ThemeStyleImPlot(C,
                                      line_weight=2.0,               # Line thickness
                                      marker_size=5.0,               # Marker size
                                      marker_weight=1.5,             # Marker outline weight
                                      fill_alpha=0.25,               # Fill transparency
                                      legend_padding=(12, 12),       # Legend padding
                                      plot_padding=(10, 10),         # Plot padding
                                      minor_alpha=0.25)              # Minor grid alpha
    
    # Combine plot colors and styles
    with dcg.ThemeList(C) as plot_theme:
        plot_colors
        plot_styles
    
    # Apply custom theme to plot
    with dcg.Plot(C, label="Custom Plot Style", height=300, width=-1, theme=plot_theme):
        dcg.PlotLine(C, label="Sin(x)", X=x, Y=y1)
        dcg.PlotLine(C, label="Cos(x)", X=x, Y=y2)
        dcg.PlotScatter(C, label="Points", X=x[::10], Y=y1[::10])
    
    # Series-specific themes
    with dcg.Plot(C, label="Series-Specific Themes", height=300, width=-1):
        # Global plot theme
        plot_base_theme = dcg.ThemeColorImPlot(C,
                                             plot_bg=(25, 25, 35),
                                             axis_text=(200, 200, 220),
                                             axis_grid=(60, 60, 80))
        
        # Apply themes to specific series
        sin_theme = dcg.ThemeList(C)
        with sin_theme:
            dcg.ThemeColorImPlot(C, line=(220, 100, 100))
            dcg.ThemeStyleImPlot(C, line_weight=3.0)
        
        cos_theme = dcg.ThemeList(C)
        with cos_theme:
            dcg.ThemeColorImPlot(C, line=(100, 180, 250))
            dcg.ThemeStyleImPlot(C, line_weight=2.0)
        
        points_theme = dcg.ThemeList(C)
        with points_theme:
            dcg.ThemeColorImPlot(C, marker_fill=(220, 180, 80), marker_outline=(0, 0, 0))
            dcg.ThemeStyleImPlot(C, marker_size=7.0, marker_weight=1.5)
        
        # Apply plot theme and add series with their specific themes
        dcg.PlotLine(C, label="Sin(x)", X=x, Y=y1, theme=sin_theme)
        dcg.PlotLine(C, label="Cos(x)", X=x, Y=y2, theme=cos_theme)
        dcg.PlotScatter(C, label="Points", X=x[::10], Y=y1[::10], theme=points_theme)

    with dcg.HorizontalLayout(C):
        with dcg.TreeNode(C, label="View all ThemeColorImPlot properties", value=True, width=300):
            display_item_documentation(C, dcg.ThemeColorImPlot)
        
        with dcg.TreeNode(C, label="View all ThemeStyleImPlot properties", value=True, width=300):
            display_item_documentation(C, dcg.ThemeStyleImPlot)

pop_group()  # End Theme Properties

@demosection(dcg.ThemeColorImGui, dcg.ThemeStyleImGui)
@documented
@democode
def _theme_management(C: dcg.Context):
    """
    ## Managing Themes

    Themes enable a design approach where visual appearance is centralized and 
    separated from component logic. Attaching to each item the theme is not
    practical for large applications. Instead, we can use a theme manager to
    handle theme management.

    ### Demonstrated Pattern:

    - Creating a shared theme and applying it to several items
    - Switching between variants of the theme
    """
    # Theme manager class that inherits from ThemeList
    class ThemeManager(dcg.ThemeList):
        def __init__(self, context):
            super().__init__(context)
            self.current_theme_name = "Gray"
            self._theme_items = {}
            self._initialize_themes()
        
        def _initialize_themes(self):
            # Create default theme
            default_theme = dcg.ThemeList(self.context, parent=self)
            with default_theme:
                dcg.ThemeColorImGui(self.context,
                    text=(220, 220, 220),
                    window_bg=(45, 45, 48),
                    button=(70, 70, 75),
                    button_hovered=(90, 90, 95),
                    button_active=(110, 110, 120),
                    frame_bg=(60, 60, 65))
                
                dcg.ThemeStyleImGui(self.context,
                    window_rounding=3.0,
                    frame_rounding=3.0,
                    window_padding=(8, 8),
                    frame_padding=(6, 3),
                    item_spacing=(8, 4))
            
            # Create dark blue theme
            dark_blue_theme = dcg.ThemeList(self.context, parent=self)
            with dark_blue_theme:
                dcg.ThemeColorImGui(self.context,
                    text=(220, 220, 255),
                    window_bg=(35, 35, 55),
                    button=(60, 70, 120),
                    button_hovered=(80, 90, 150),
                    button_active=(100, 110, 180),
                    frame_bg=(50, 50, 80))
                
                dcg.ThemeStyleImGui(self.context,
                    window_rounding=4.0,
                    frame_rounding=4.0,
                    window_padding=(10, 10),
                    frame_padding=(8, 4),
                    item_spacing=(10, 5))
            
            # Create dark green theme
            dark_green_theme = dcg.ThemeList(self.context, parent=self)
            with dark_green_theme:
                dcg.ThemeColorImGui(self.context,
                    text=(220, 255, 220),
                    window_bg=(35, 45, 35),
                    button=(60, 110, 70),
                    button_hovered=(80, 140, 90),
                    button_active=(100, 170, 110),
                    frame_bg=(50, 70, 50))
                
                dcg.ThemeStyleImGui(self.context,
                    window_rounding=2.0,
                    frame_rounding=2.0,
                    window_padding=(8, 8),
                    frame_padding=(6, 3),
                    item_spacing=(8, 4))
            
            # Add themes to the ThemeManager (which is itself a ThemeList)
            self.add_theme("Gray", default_theme)
            self.add_theme("Dark Blue", dark_blue_theme)
            self.add_theme("Dark Green", dark_green_theme)
            
            # Set the default theme as active
            self.set_current_theme("Gray")
        
        def add_theme(self, name, theme):
            """Add a theme to the manager"""
            self._theme_items[name] = theme
            theme.enabled = False  # Initially hide all themes
        
        def set_current_theme(self, name):
            """Set the current theme by name by showing only that theme"""
            if name not in self._theme_items:
                return
            # Hide all themes
            for theme_name, theme in self._theme_items.items():
                theme.enabled = False

            # Show only the selected theme
            self._theme_items[name].enabled = True
            self.current_theme_name = name
            C.viewport.wake() # Refresh the viewport to apply the theme change
    
    # Create a theme manager instance
    theme_mgr = ThemeManager(C)
    
    # Create theme selector
    dcg.Text(C, value="Select Application Theme:")
    theme_names = list(theme_mgr._theme_items.keys())
    theme_selector = dcg.Combo(C, items=theme_names, 
                               value=theme_mgr.current_theme_name,
                               width=200)
    
    # Create a window that uses the theme manager
    demo_window = dcg.ChildWindow(C, label=f"Theme Manager Demo", 
                                  width="0.33*fillx", height=300,
                                  border=True, 
                                  theme=theme_mgr)  # Set theme manager as the theme
    
    # Populate the window with UI elements
    with demo_window:
        dcg.Button(C, label="Button")
        dcg.InputText(C, label="Input Field", hint="Enter text")
        dcg.Checkbox(C, label="Checkbox")
        dcg.Slider(C, label="Slider", format="float", min_value=0, max_value=1, value=0.5)
        with dcg.TreeNode(C, label="Tree Node"):
            dcg.Text(C, value="Tree content")
    
    # Handle theme selection changes
    def on_theme_change(sender, target, selected_theme):
        theme_mgr.set_current_theme(selected_theme)
        # Update the window title to reflect the current theme
        demo_window.label = f"{selected_theme} Theme Demo"
        C.viewport.wake()
    
    theme_selector.callback = on_theme_change


@demosection(dcg.ThemeColorImGui, dcg.ThemeList, dcg.utils.StyleEditor)
@documented
@democode
def _style_editor(C: dcg.Context):
    """
    ## Using the Style Editor

    DearCyGui includes a built-in style editor to help you create and customize themes.
    The style editor provides a visual interface for adjusting theme properties and
    seeing the results in real time.
    
    Key features of the style editor:
    
    1. Interactive preview of theme changes
    2. Settings for all color and style properties
    3. Export theme code for use in your application
    
    This example demonstrates how to use the style editor to create custom themes.
    """
    # Create a button to open the style editor
    dcg.Button(C, label="Open Style Editor", 
             callback=lambda: dcg.utils.StyleEditor(C))
    
    # Create a theme that can be edited
    editable_theme = dcg.ThemeList(C)
    with editable_theme:
        dcg.ThemeColorImGui(C,
            # Default dark theme
            text=(220, 220, 220),
            window_bg=(40, 40, 45),
            button=(70, 70, 85),
            button_hovered=(85, 85, 100),
            button_active=(60, 60, 75))
    
    # Sample UI with the theme applied
    with dcg.ChildWindow(C, label="Theme Preview", width=400, height=300, 
                      theme=editable_theme, border=True):
        dcg.Text(C, value="This is a preview of the editable theme")
        dcg.Button(C, label="Sample Button")
        dcg.InputText(C, label="Sample Input", hint="Type here")
        dcg.Checkbox(C, label="Sample Checkbox")
        dcg.Slider(C, label="Sample Slider", format="float", 
                 min_value=0, max_value=1, value=0.5)
        
        with dcg.TreeNode(C, label="Tree Node"):
            dcg.Text(C, value="Tree content")


pop_group()  # End Global Theme Management


if __name__ == "__main__":
    launch_demo(title="Styles and Themes Demo")