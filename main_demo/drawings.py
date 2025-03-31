import dearcygui as dcg
from demo_utils import documented, democode,\
    push_group, pop_group, launch_demo, demosection
import math

# decorators:
# - documented: the description (markdown) is displayed
# - democode: the code is displayed and can edited (and run again)
# - demosection: the section is displayed in the table of contents,
#    the section name is extracted from the function name.

push_group("Introduction")

@demosection
@documented
def _intro(C: dcg.Context):
    """
    ### Introduction to drawings

    Drawings are a powerful feature of DearCygui that allows you to create
    custom graphics and visuals.

    In this demo, we will explore various aspects of the drawing system,
    including how to create shapes, lines, and text, as well as how to
    customize their appearance.
    We will also look at how to use the drawing system to create
    interactive elements and animations.

    The drawing system is based on the concept of a "canvas", which is an
    infinite 2D surface where you can draw shapes, lines, and text.
    You can think of the canvas as a transparent sheet of paper where you can
    create your own graphics.

    To start drawing, you must first create a drawing container (canvas). Each
    container has its own coordinate system, so you can create multiple
    containers with different sizes and positions.
    You can also create multiple layers of drawings, which allows you to
    create complex graphics with multiple elements.
    """

@demosection
@documented
def _drawing_containers(C: dcg.Context):
    """
    ### Drawing containers

    To start drawing, you need to create a drawing container and
    attach drawing items to it.

    Available containers are:
    - `dcg.DrawInWindow`: A widget (subclass of uiItem). It defines a clickable surface
        of the target width/height (if you pass button=True). It can be used to create
        custom widgets. Inside
        a `DrawInWindow`, the coordinate system starts at (0, 0) in the top left corner
        of the widget and goes to (width, height) in the bottom right corner.
    - `dcg.DrawInPlot`: This container enables to draw inside a `dcg.Plot`. It can be
        used to draw custom plot series, but is also very useful to act as an interactive
        canvas. Indeed `DrawInPlot` benefits from the plot's zooming and panning features.
        Plot visuals can be completly removed, and make the canvas entirely empty.
        The coordinate system corresponds to the selected axes of the plot (by default X1/Y1).
    - `dcg.ViewportDrawList`: This container can be used to draw in pixel coordinates (top
        left origin) above or behind all items (depending on the `front` parameter).
        It is useful to draw custom backgrounds or overlays. The coordinate system
        corresponds to the viewport size (in pixels).
    - `dcg.DrawingList`: This simple container is a drawing item (and thus must be inside a
        drawing container). It is useful to group several drawing items together. On particular
        use case is creating custom drawing classes. Subclassing `DrawingList` allows to
        attach drawing items to the custom class instance. The coordinate system
        corresponds to the parent drawing container.
    - `dcg.DrawingScale`: This container enables to change the coordinate system for its
        children. It can be used for example in a `DrawInWindow` to change the origin
        and axes scales.
    - `dcg.DrawInvisibleButton`: This drawing container enables to have interactable area.
        For ease of use, it accepts drawing children. Its coordinate system is top left
        origin and (1, 1) for the bottom right corner.
    - `dcg.DrawingClip`: This container is reserved for advanced use-cases such as only displaying
        some items at specific zoom levels (e.g. in a `dcg.Plot`), or to skip rendering
        items outside the visible region of the canvas (in which case it is only useful
        when having more than 10K items).
        The coordinate system corresponds to the parent drawing container.

    In this demo we will only demonstrate the use of `DrawInWindow`, `ViewportDrawList`,
    `DrawingList` and `DrawingScales`. `DrawInPlot` is shown in the `Plot` demo.
    """
    pass

@demosection
@documented
@democode
def _thickness_considerations(C: dcg.Context):
    """
    ### Thickness Considerations
    
    When drawing shapes, the `thickness` parameter is crucial but can be tricky when
    working with different coordinate systems:
    
    - **Positive thickness values** are in coordinate units. This means their visual size
      changes with the coordinate system's scale.
    - **Negative thickness values** are in screen pixels. This gives consistent visual 
      appearance regardless of the coordinate scale.
    - **Default thickness** (1.0) can cause unexpectedly thick lines when coordinates
      span a small range (like 0 to 1).
    
    #### Rules of thumb:
    
    1. For fixed pixel thickness (like UI elements): Use negative values like `-1`, `-2`
    2. For coordinate-scaled thickness: Use small positive values appropriate to your
       coordinate range (e.g., `0.01` in a 0-1 plot)
    3. For filled shapes: Set the outline color to 0 to draw only the fill
    
    The example below shows three stars with different thickness settings in a 0-1
    coordinate system:
    """
    with dcg.DrawInWindow(C, width=500, height=200):
        # Using pixel-based thickness (looks consistent regardless of scale)
        dcg.DrawStar(C, center=(100, 100), radius=50, num_points=5, 
                    color=(255, 0, 0), thickness=-2,
                    direction=0.3, inner_radius=25)
        
        # Using appropriate coordinate-based thickness (would scale with coordinates)
        # This would be good in a Plot with small coordinate range
        dcg.DrawText(C, pos=(100, 170), text="Pixel thickness (-2)", 
                    color=(255, 255, 255), size=-16)
        
        # Using default thickness - far too thick in small coordinate ranges
        dcg.DrawStar(C, center=(250, 100), radius=50, num_points=5, 
                    color=(0, 255, 0), thickness=5,
                    direction=0.3, inner_radius=25)
        dcg.DrawText(C, pos=(250, 170), text="Large thickness (5)", 
                    color=(255, 255, 255), size=-16)
        
        # Using default thickness - far too thick in small coordinate ranges  
        dcg.DrawStar(C, center=(400, 100), radius=50, num_points=5, 
                    color=(255, 255, 0), thickness=1,
                    direction=0.3, inner_radius=25)
        dcg.DrawText(C, pos=(400, 170), text="Default thickness (1)", 
                    color=(255, 255, 255), size=-16)
    
    # Example in a plot (0-1 coordinate range) to show how thickness behaves
    with dcg.Plot(C, label="Thickness in small coordinate ranges", height=300, width=-1) as plot:
        plot.X1.min = 0
        plot.X1.max = 1
        plot.Y1.min = 0
        plot.Y1.max = 1
        
        with dcg.DrawInPlot(C):
            # Good: Pixel thickness (constant visual size)
            dcg.DrawStar(C, center=(0.25, 0.5), radius=0.1, num_points=5, 
                        color=(255, 0, 0), thickness=-2,
                        direction=0.3, inner_radius=0.05)
            
            # Good: Small appropriate coordinate thickness
            dcg.DrawStar(C, center=(0.5, 0.5), radius=0.1, num_points=5, 
                        color=(0, 255, 0), thickness=0.01,
                        direction=0.3, inner_radius=0.05)
            
            # Bad: Default thickness (way too thick for this coordinate system)
            dcg.DrawStar(C, center=(0.75, 0.5), radius=0.1, num_points=5, 
                        color=(255, 255, 0), thickness=1,
                        direction=0.3, inner_radius=0.05)
            
            # Add labels
            dcg.DrawText(C, pos=(0.25, 0.7), text="Pixel (-2)", 
                        color=(255, 255, 255), size=-12)
            dcg.DrawText(C, pos=(0.5, 0.7), text="Coord (0.01)", 
                        color=(255, 255, 255), size=-12)
            dcg.DrawText(C, pos=(0.75, 0.7), text="Default (1)", 
                        color=(255, 255, 255), size=-12)

@demosection
@documented
def _drawing_trivia(C: dcg.Context):
    """
    ### Drawing good to know facts

    - The `show` property of a `DrawingList` can be useful to hide/show a group of items
        without having to change the visibility of each item individually.
    - `DrawingList` can be useful to implement "double buffering". You draw items in
        a hidden `DrawingList`, while you show another `DrawingList`. When you are done
        drawing, you can swap the two lists. This is useful when creating your drawings
        take time.
    - DearCyGui attemps to be as fast as possible for item creation. This enables to
        create >100K drawing items per frame before losing real time updates. Creating
        a DearCyGui drawing item is only slightly slower than creating a builtin
        Python object.
    - All rendering in DearCyGui uses ImGui's rendering system. During rendering,
        all items are converted into vertex coordinates and compacted in a few draw calls.
        Everything is rendering using OpenGL. The overhead of OpenGL is negligible for
        that few draw calls. The main CPU overhead is the conversion of the items. In
        particular ImGui renders all items in such a way they appear antialiased.
    - If you need to prevent two items to be in same draw calls (to force ordering),
        you can use the `dcg.DrawSplitBatch` item which will force the creation
        of a new draw calls for items rendered after it. Note that this is only needed
        in seldom cases as ImGui already splits the draw calls in many needed cases,
        such as when drawing an image.
    - In order to compact draw calls, ImGui uses a font texture atlas. It attemps
        for all items to read from the same texture atlas. Even when the items
        just has a single color, it will read from the texture (a white pixel).
    - Due to the above, while DearCyGui's drawing items can be numerous and enable
        various use-cases, for heavy rendering you may need to mix DearCyGui with
        custom OpenGL rendering (see related section).
    """

pop_group()  # end of Introduction

push_group("Available shapes")

@demosection
@documented
@democode
def _basic_shapes(C: dcg.Context):
    """
    ### Basic Shapes
    
    DearCyGui provides several basic shapes that can be used to create complex
    visualizations. Each shape can have an outline color (via `color` parameter)
    and a fill color (via `fill` parameter).
    
    Basic shapes include:
    - `DrawCircle`: Draws a circle specified by center and radius
    - `DrawRect`: Draws a rectangle specified by min/max points
    - `DrawTriangle`: Draws a triangle specified by three points
    - `DrawQuad`: Draws a quadrilateral specified by four points
    - `DrawEllipse`: Draws an ellipse specified by min/max points
    - `DrawArc`: Draws an ellipse/circle arc specified by center, radius, and angles
    - `DrawRegularPolygon`: Draws a regular polygon specified by center, radius, and number of points
    - `DrawStar`: Draws a star specified by center, radius, number of points, and inner radius
    
    Each shape can be filled and/or outlined. Set `color=0` for filled shapes
    with no outline.
    """
    with dcg.DrawInWindow(C, width=600, height=300):
        # Circle
        dcg.DrawCircle(C, center=(100, 100), radius=50, 
                      color=(255, 0, 0), fill=(255, 200, 200), thickness=-2)
        dcg.DrawText(C, pos=(100, 170), text="Circle", 
                    color=(255, 255, 255), size=-16)
        
        # Rectangle
        dcg.DrawRect(C, pmin=(200, 50), pmax=(300, 150), 
                    color=(0, 255, 0), fill=(200, 255, 200), thickness=-2)
        dcg.DrawText(C, pos=(250, 170), text="Rectangle", 
                    color=(255, 255, 255), size=-16)
        
        # Triangle
        dcg.DrawTriangle(C, p1=(350, 50), p2=(400, 150), p3=(450, 50),
                        color=(0, 0, 255), fill=(200, 200, 255), thickness=-2)
        dcg.DrawText(C, pos=(400, 170), text="Triangle", 
                    color=(255, 255, 255), size=-16)
        
        # Quadrilateral
        dcg.DrawQuad(C, p1=(500, 50), p2=(550, 75), p3=(550, 125), p4=(500, 150),
                    color=(255, 0, 255), fill=(255, 200, 255), thickness=-2)
        dcg.DrawText(C, pos=(525, 170), text="Quad", 
                    color=(255, 255, 255), size=-16)
        
        # Ellipse
        dcg.DrawEllipse(C, pmin=(150, 200), pmax=(250, 250),
                       color=(255, 255, 0), fill=(255, 255, 200), thickness=-2)
        dcg.DrawText(C, pos=(200, 270), text="Ellipse", 
                    color=(255, 255, 255), size=-16)
        
        # Fill-only shape (no outline)
        dcg.DrawCircle(C, center=(350, 225), radius=40,
                      color=(0, 0, 0, 0), fill=(0, 255, 255))
        dcg.DrawText(C, pos=(350, 270), text="Fill only", 
                    color=(255, 255, 255), size=-16)
        
        # Outline-only shape (no fill)
        dcg.DrawRect(C, pmin=(450, 200), pmax=(550, 250),
                    color=(255, 150, 0), thickness=-2)
        dcg.DrawText(C, pos=(500, 270), text="Outline only", 
                    color=(255, 255, 255), size=-16)


@demosection
@documented
@democode
def _line_based_drawings(C: dcg.Context):
    """
    ### Line-Based Drawings
    
    DearCyGui offers several drawing primitives for lines and curves:
    
    - `DrawLine`: Draws a straight line between two points
    - `DrawPolyline`: Connects multiple points with line segments
    - `DrawArrow`: Draws a line with an arrow at one end
    - `DrawBezierCubic`: Draws a cubic Bezier curve defined by 4 control points
    - `DrawBezierQuadratic`: Draws a quadratic Bezier curve defined by 3 control points
    
    Line thickness works the same as with shapes - use negative values for pixel-space
    thickness and positive values for coordinate-space thickness.
    """
    with dcg.DrawInWindow(C, width=600, height=400):
        # Simple line
        dcg.DrawLine(C, p1=(50, 50), p2=(200, 50), 
                    color=(255, 255, 255), thickness=-2)
        dcg.DrawText(C, pos=(125, 70), text="Line", 
                    color=(255, 255, 255), size=-16)
        
        # Arrow
        dcg.DrawArrow(C, p1=(50, 120), p2=(200, 120), 
                     color=(255, 100, 100), thickness=-2)
        dcg.DrawText(C, pos=(125, 140), text="Arrow", 
                    color=(255, 255, 255), size=-16)
        
        # Polyline
        points = [(50, 200), (100, 180), (150, 220), (200, 180)]
        dcg.DrawPolyline(C, points=points, 
                        color=(100, 255, 100), thickness=-2)
        dcg.DrawText(C, pos=(125, 240), text="Polyline", 
                    color=(255, 255, 255), size=-16)
        
        # Cubic Bezier curve
        dcg.DrawBezierCubic(C, p1=(300, 50), p2=(350, 25), 
                           p3=(450, 25), p4=(500, 50), 
                           color=(100, 100, 255), thickness=-2)
        # Draw control points for clarity
        dcg.DrawCircle(C, center=(300, 50), radius=4, color=(100, 100, 255), thickness=-1)
        dcg.DrawCircle(C, center=(350, 25), radius=4, color=(255, 100, 100), thickness=-1)
        dcg.DrawCircle(C, center=(450, 25), radius=4, color=(255, 100, 100), thickness=-1)
        dcg.DrawCircle(C, center=(500, 50), radius=4, color=(100, 100, 255), thickness=-1)
        # Draw dotted lines to control points
        dcg.DrawLine(C, p1=(300, 50), p2=(350, 25), color=(255, 255, 255, 100), thickness=-1)
        dcg.DrawLine(C, p1=(500, 50), p2=(450, 25), color=(255, 255, 255, 100), thickness=-1)
        
        dcg.DrawText(C, pos=(400, 70), text="Cubic Bezier", 
                    color=(255, 255, 255), size=-16)
        
        # Quadratic Bezier curve
        dcg.DrawBezierQuadratic(C, p1=(300, 120), p2=(400, 70), p3=(500, 120), 
                               color=(255, 100, 255), thickness=-2)
        # Draw control points for clarity
        dcg.DrawCircle(C, center=(300, 120), radius=4, color=(255, 100, 255), thickness=-1)
        dcg.DrawCircle(C, center=(400, 70), radius=4, color=(255, 100, 100), thickness=-1)
        dcg.DrawCircle(C, center=(500, 120), radius=4, color=(255, 100, 255), thickness=-1)
        # Draw dotted lines to control point
        dcg.DrawLine(C, p1=(300, 120), p2=(400, 70), color=(255, 255, 255, 100), thickness=-1)
        dcg.DrawLine(C, p1=(500, 120), p2=(400, 70), color=(255, 255, 255, 100), thickness=-1)
        
        dcg.DrawText(C, pos=(400, 140), text="Quadratic Bezier", 
                    color=(255, 255, 255), size=-16)
        
        # Line styles demonstration
        dcg.DrawText(C, pos=(400, 200), text="Line Thickness Examples:", 
                    color=(255, 255, 255), size=-16)
        
        dcg.DrawLine(C, p1=(300, 230), p2=(500, 230), 
                    color=(255, 255, 255), thickness=-1)
        dcg.DrawText(C, pos=(520, 230), text="-1px", 
                    color=(255, 255, 255), size=-14)
        
        dcg.DrawLine(C, p1=(300, 260), p2=(500, 260), 
                    color=(255, 255, 255), thickness=-3)
        dcg.DrawText(C, pos=(520, 260), text="-3px", 
                    color=(255, 255, 255), size=-14)
        
        dcg.DrawLine(C, p1=(300, 290), p2=(500, 290), 
                    color=(255, 255, 255), thickness=-5)
        dcg.DrawText(C, pos=(520, 290), text="-5px", 
                    color=(255, 255, 255), size=-14)


@demosection
@documented
@democode
def _regular_shapes(C: dcg.Context):
    """
    ### Regular and Star Shapes
    
    DearCyGui provides specialized functions for drawing regular polygons and stars:
    
    - `DrawRegularPolygon`: Draws a regular polygon with a specified number of sides
    - `DrawStar`: Draws a star with a specified number of points
    
    Parameters:
    - `center`: Center position of the shape
    - `radius`: Outer radius of the shape
    - `num_points`: Number of vertices/points
    - `direction`: Rotation angle in radians
    - `inner_radius`: For stars, the radius of inner points
    
    These shapes are great for creating markers, icons, and decorative elements.
    """
    with dcg.DrawInWindow(C, width=600, height=400):
        # Regular polygons row
        shapes = [
            {"num": 3, "name": "Triangle"},
            {"num": 4, "name": "Square"},
            {"num": 5, "name": "Pentagon"},
            {"num": 6, "name": "Hexagon"},
            {"num": 8, "name": "Octagon"}
        ]
        
        for i, shape in enumerate(shapes):
            x = 75 + i * 110
            dcg.DrawRegularPolygon(C, center=(x, 100), radius=40, 
                                  num_points=shape["num"], 
                                  color=(255, 200, 0), 
                                  fill=(255, 255, 100, 100), 
                                  thickness=-2)
            dcg.DrawText(C, pos=(x, 160), text=shape["name"], 
                        color=(255, 255, 255), size=-16)
        
        # Stars row
        stars = [
            {"num": 3, "name": "3-point"},
            {"num": 4, "name": "4-point"},
            {"num": 5, "name": "5-point"},
            {"num": 6, "name": "6-point"},
            {"num": 8, "name": "8-point"}
        ]
        
        for i, star in enumerate(stars):
            x = 75 + i * 110
            dcg.DrawStar(C, center=(x, 250), radius=40, 
                        num_points=star["num"], 
                        inner_radius=15,
                        color=(0, 150, 255), 
                        fill=(100, 200, 255, 100), 
                        thickness=-2)
            dcg.DrawText(C, pos=(x, 310), text=star["name"], 
                        color=(255, 255, 255), size=-16)
        
        # Direction demonstration
        dcg.DrawText(C, pos=(300, 350), text="Direction changes orientation:", 
                    color=(255, 255, 255), size=-16)
        
        directions = [0, 0.2, 0.4, 0.6, 0.8]
        for i, dir in enumerate(directions):
            x = 100 + i * 100
            dcg.DrawStar(C, center=(x, 380), radius=25, 
                        num_points=5, 
                        inner_radius=10,
                        direction=dir,
                        color=(255, 150, 0), 
                        fill=(255, 200, 100, 100), 
                        thickness=-2)
            dcg.DrawText(C, pos=(x, 420), text=f"{dir:.1f}π", 
                        color=(255, 255, 255), size=-14)


@demosection
@documented
@democode
def _text_and_values(C: dcg.Context):
    """
    ### Text and Value Drawing
    
    DearCyGui offers ways to draw text directly in drawing areas:
    
    - `DrawText`: Draws static text at a specified position
    - `DrawValue`: Displays a SharedValue (like SharedStr)
    
    Text size can be specified in pixels (negative values) or in drawing coordinates
    (positive values). Colors can be specified as RGB or RGBA tuples.
    """
    with dcg.DrawInWindow(C, width=600, height=300):
        # Basic text
        dcg.DrawText(C, pos=(50, 50), text="Hello, DearCyGui!", 
                    color=(255, 255, 255), size=-24)
        
        # Colored text
        dcg.DrawText(C, pos=(50, 100), text="Colored Text", 
                    color=(255, 100, 100), size=-20)
        
        # Small text
        dcg.DrawText(C, pos=(50, 150), text="Small pixel-size text", 
                    color=(100, 255, 100), size=-12)
        
        # Text with coordinate-based size (useful in plots)
        dcg.DrawText(C, pos=(50, 200), text="Coordinate-size text (20)", 
                    color=(100, 100, 255), size=20)
        
        # SharedValue example
        dcg.Text(C, value="The text below uses a SharedStr that can be updated dynamically:")
        
        # Create a shared string value
        shared_text = dcg.SharedStr(C, value="Hello, World!")
        
        # Draw the shared value
        dcg.DrawValue(C, pos=(300, 80), 
                     color=(255, 255, 0), 
                     size=-18,
                     print_format="This is a dynamic value: %s", # Same as C's printf
                     shareable_value=shared_text)
        
    # Add a slider to control the shared value
    with dcg.HorizontalLayout(C, width=250):
        dcg.Text(C, value="Try changing this text:")
        dcg.InputText(C, shareable_value=shared_text, width=-1)


@demosection
@documented
@democode
def _interactive_elements(C: dcg.Context):
    """
    ### Interactive Drawing Elements
    
    DearCyGui allows you to create interactive elements in drawing areas:
    
    - `DrawInvisibleButton`: Creates an invisible clickable area
    
    These elements can respond to hover events, clicks, and drags, allowing
    you to build custom interactive widgets and tools.
    
    The example below demonstrates an invisible button that:
    1. Changes color when hovered
    2. Can be clicked and dragged
    3. Reports its state and position

    A noticeable difference with other DearCyGui buttons is that it has
    additional features to handle button overlaps. For more details,
    refer to the item documentation (e.g. `help(dcg.DrawInvisibleButton)`).
    """
    with dcg.VerticalLayout(C, width=-1):
        info_text = dcg.Text(C, value="Hover, click, and drag in the area below")
        
        # Create drawing area with interactive elements
        with dcg.DrawInWindow(C, width=600, height=300) as draw_area:
            # Create a rectangle that will be our visible button representation
            button_rect = dcg.DrawRect(C, pmin=(100, 100), pmax=(300, 200), 
                                     color=(0, 120, 255), 
                                     fill=(100, 150, 255, 150), 
                                     thickness=-2)
            
            # Create an invisible button at the same position
            invisible_btn = dcg.DrawInvisibleButton(C, p1=(100, 100), p2=(300, 200),
                                                  button=dcg.MouseButtonMask.ANY,
                                                  capture_mouse=True)
            
            # Add text to the button
            with invisible_btn:
                dcg.DrawText(C, pos=(0.5, 0.5), 
                            text="Drag Me!",
                            color=(255, 255, 255), 
                            size=-20)
            
            # Event tracking variables
            start_pos = [100, 100]
            current_pos = [100, 100]
            
            # Event handlers
            def on_hover_enter():
                button_rect.color = (255, 120, 0)  # Change outline color when hovered
                info_text.value = "Button is hovered!"
            
            def on_hover_exit():
                button_rect.color = (0, 120, 255)  # Reset color
                info_text.value = "Hover, click, and drag in the area below"
            
            def on_clicked():
                nonlocal start_pos
                start_pos = [button_rect.pmin[0], button_rect.pmin[1]]
                info_text.value = "Button clicked! Drag to move."
            
            def on_released():
                info_text.value = f"Button released at: ({button_rect.pmin[0]:.1f}, {button_rect.pmin[1]:.1f})"
            
            def on_dragging(_, __, delta):
                nonlocal current_pos
                # Update button position
                new_pmin = (start_pos[0] + delta[0], start_pos[1] + delta[1])
                new_pmax = (new_pmin[0] + 200, new_pmin[1] + 100)

                # Update button rectangle position
                button_rect.pmin = new_pmin
                button_rect.pmax = new_pmax
                    
                # Update invisible button position
                invisible_btn.p1 = new_pmin
                invisible_btn.p2 = new_pmax
                    
                current_pos = new_pmin
                info_text.value = f"Dragging to: ({current_pos[0]:.1f}, {current_pos[1]:.1f})"
            
            # Connect event handlers
            invisible_btn.handlers = [
                dcg.GotHoverHandler(C, callback=on_hover_enter),
                dcg.LostHoverHandler(C, callback=on_hover_exit),
                dcg.ClickedHandler(C, callback=on_clicked),
                dcg.DraggingHandler(C, callback=on_dragging),
                dcg.DraggedHandler(C, callback=on_released)
            ]
            
        dcg.Text(C, value="The DrawInvisibleButton component allows you to create custom interactive elements.")
        dcg.Text(C, value="It can be used to implement draggable items, custom buttons, and more.")

@demosection
@documented
@democode
def _advanced_combinations(C: dcg.Context):
    """
    ### Advanced Drawing Combinations
    
    By combining basic drawing primitives, you can create complex visualizations.
    This example demonstrates how to create a simple interactive gauge using
    multiple drawing elements working together.
    
    Techniques shown:
    - Using multiple shapes to build a composite object
    - Using transformations to position elements
    - Responding to user interaction
    """
    class Gauge(dcg.DrawInWindow):
        def __init__(self, context, width=400, height=300, value=25.0, **kwargs):
            super().__init__(context, width=width, height=height, **kwargs)
            
            # Gauge properties
            self._value = value
            self._radius = 100
            self._center_x = width // 2
            self._center_y = height // 2
            self._start_angle = -0.75 * math.pi  # -135 degrees in radians
            self._end_angle = 0.75 * math.pi     # 135 degrees in radians
            
            # Create drawing elements
            with self:
                self._create_gauge_elements(context)
        
        @property
        def value(self):
            return self._value
        
        @value.setter
        def value(self, new_value):
            # Update the value with validation
            self._value = max(0.0, min(100.0, new_value))
            # Update the visual elements
            self._update_gauge_elements()
        
        def _create_gauge_elements(self, context):
            # Draw gauge background
            self.background_arc = dcg.DrawArc(
                context, 
                center=(self._center_x, self._center_y), 
                radius=(self._radius, self._radius),
                start_angle=self._start_angle, 
                end_angle=self._end_angle,
                color=(100, 100, 100), 
                thickness=-8
            )
            
            # Draw gauge value arc (colored portion)
            value_angle = self._start_angle + (self._end_angle - self._start_angle) * (self._value / 100.0)
            self.value_arc = dcg.DrawArc(
                context, 
                center=(self._center_x, self._center_y), 
                radius=(self._radius, self._radius),
                start_angle=self._start_angle, 
                end_angle=value_angle,
                color=(0, 200, 100), 
                thickness=-8
            )
            
            # Draw gauge center
            self.center_circle = dcg.DrawCircle(
                context, 
                center=(self._center_x, self._center_y), 
                radius=10,
                color=(50, 50, 50), 
                fill=(200, 200, 200)
            )
            
            # Draw gauge needle
            needle_length = self._radius - 10
            needle_angle = self._start_angle + (self._end_angle - self._start_angle) * (self._value / 100.0)
            needle_x = self._center_x + needle_length * math.cos(needle_angle)
            needle_y = self._center_y + needle_length * math.sin(needle_angle)
            
            self.needle = dcg.DrawLine(
                context, 
                p1=(self._center_x, self._center_y), 
                p2=(needle_x, needle_y),
                color=(255, 50, 50), 
                thickness=-3
            )
            
            # Draw tick marks
            self.ticks = []
            self.tick_labels = []
            num_ticks = 11  # 0 to 100 by 10s
            
            for i in range(num_ticks):
                tick_percent = i / (num_ticks - 1)
                tick_angle = self._start_angle + (self._end_angle - self._start_angle) * tick_percent
                
                # Outer point
                outer_x = self._center_x + self._radius * math.cos(tick_angle)
                outer_y = self._center_y + self._radius * math.sin(tick_angle)
                
                # Inner point
                inner_x = self._center_x + (self._radius - 15) * math.cos(tick_angle)
                inner_y = self._center_y + (self._radius - 15) * math.sin(tick_angle)
                
                # Draw tick
                tick = dcg.DrawLine(
                    context, 
                    p1=(inner_x, inner_y), 
                    p2=(outer_x, outer_y),
                    color=(200, 200, 200), 
                    thickness=-2
                )
                self.ticks.append(tick)
                
                # Draw label for each major tick
                label_x = self._center_x + (self._radius - 30) * math.cos(tick_angle)
                label_y = self._center_y + (self._radius - 30) * math.sin(tick_angle)
                
                value_text = int(100 * tick_percent)
                label = dcg.DrawText(
                    context, 
                    pos=(label_x, label_y), 
                    text=f"{value_text}", 
                    color=(255, 255, 255), 
                    size=-12
                )
                self.tick_labels.append(label)
            
            # Draw value text
            self.value_text = dcg.DrawText(
                context, 
                pos=(self._center_x, self._center_y + 50), 
                text=f"{self._value:.1f}", 
                color=(255, 255, 255), 
                size=-24
            )
        
        def _update_gauge_elements(self):
            # Update value arc
            value_angle = self._start_angle + (self._end_angle - self._start_angle) * (self._value / 100.0)
            self.value_arc.end_angle = value_angle
            
            # Update needle position
            needle_length = self._radius - 10
            needle_angle = self._start_angle + (self._end_angle - self._start_angle) * (self._value / 100.0)
            needle_x = self._center_x + needle_length * math.cos(needle_angle)
            needle_y = self._center_y + needle_length * math.sin(needle_angle)
            self.needle.p2 = (needle_x, needle_y)
            
            # Update value text
            self.value_text.text = f"{self._value:.1f}"


        # Demo usage of the Gauge class
    with dcg.HorizontalLayout(C, width=-1):
        # Create the gauge
        gauge = Gauge(C, value=25.0)

        gauge_value = dcg.Slider(C, label="Gauge Value", format="float",
                                 min_value=0.0, max_value=100.0,
                                 value=25.0, print_format="%.1f")     

        # Update gauge when slider changes
        def update_gauge(sender, target, value):
            gauge.value = value

        gauge_value.callback = update_gauge



if __name__ == "__main__":
    launch_demo(title="Drawing Demo")