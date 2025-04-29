import dearcygui as dcg
from demo_utils import documented, democode,\
    push_group, pop_group, launch_demo, demosection,\
    display_item_documentation
import math
import numpy as np
import os
from PIL import Image
import time

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
    - `dcg.utils.DrawStream`: This container is a timed DrawingList. It enables to draw a different
        item every frame depending on timing constraints. It can be used to create
        animations. The coordinate system corresponds to the parent drawing container.
    - `dcg.DrawingClip`: This container is reserved for advanced use-cases such as only displaying
        some items at specific zoom levels (e.g. in a `dcg.Plot`), or to skip rendering
        items outside the visible region of the canvas (in which case it is only useful
        when having more than 10K items).
        The coordinate system corresponds to the parent drawing container.

    In this demo we will only demonstrate the use of `DrawInWindow`, `ViewportDrawList`,
    `DrawingList` and `DrawingScales`. `DrawInPlot` is shown in the `Plot` demo.
    """
    with dcg.TreeNode(C, label="DrawInWindow"):
        display_item_documentation(C, dcg.DrawInWindow)
    with dcg.TreeNode(C, label="ViewportDrawList"):
        display_item_documentation(C, dcg.ViewportDrawList)
    with dcg.TreeNode(C, label="DrawingList"):
        display_item_documentation(C, dcg.DrawingList)
    with dcg.TreeNode(C, label="DrawingScale"):
        display_item_documentation(C, dcg.DrawingScale)
    with dcg.TreeNode(C, label="DrawInvisibleButton"):
        display_item_documentation(C, dcg.DrawInvisibleButton)
    with dcg.TreeNode(C, label="DrawStream"):
        display_item_documentation(C, dcg.utils.DrawStream)
    with dcg.TreeNode(C, label="DrawingClip"):
        display_item_documentation(C, dcg.DrawingClip)

@demosection(dcg.DrawInWindow, dcg.DrawInPlot, dcg.DrawStar, dcg.DrawText)
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

@demosection(dcg.DrawingList, dcg.DrawingClip, dcg.DrawSplitBatch)
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

@demosection(dcg.DrawInWindow, dcg.DrawCircle, dcg.DrawRect, dcg.DrawQuad)
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
    with dcg.TreeNode(C, label="DrawCircle"):
        display_item_documentation(C, dcg.DrawCircle)
    with dcg.TreeNode(C, label="DrawRect"):
        display_item_documentation(C, dcg.DrawRect)
    with dcg.TreeNode(C, label="DrawTriangle"):
        display_item_documentation(C, dcg.DrawTriangle)
    with dcg.TreeNode(C, label="DrawQuad"):
        display_item_documentation(C, dcg.DrawQuad)
    with dcg.TreeNode(C, label="DrawEllipse"):
        display_item_documentation(C, dcg.DrawEllipse)
    with dcg.TreeNode(C, label="DrawArc"):
        display_item_documentation(C, dcg.DrawArc)
    with dcg.TreeNode(C, label="DrawRegularPolygon"):
        display_item_documentation(C, dcg.DrawRegularPolygon)
    with dcg.TreeNode(C, label="DrawStar"):
        display_item_documentation(C, dcg.DrawStar)
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


@demosection(dcg.DrawArrow, dcg.DrawLine, dcg.DrawBezierCubic, 
             dcg.DrawBezierQuadratic, dcg.DrawPolyline)
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


@demosection(dcg.DrawRegularPolygon, dcg.DrawStar)
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
            dcg.DrawText(C, pos=(x, 420), text=f"{dir:.1f}pi", 
                        color=(255, 255, 255), size=-14)


@demosection(dcg.DrawText, dcg.DrawValue)
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


@demosection(dcg.DrawInvisibleButton, dcg.GotHoverHandler,
             dcg.LostHoverHandler, dcg.ClickedHandler,
             dcg.DraggingHandler, dcg.DraggedHandler)
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

@demosection(dcg.DrawInWindow, dcg.DrawArc, dcg.DrawCircle,
             dcg.DrawLine, dcg.DrawText, dcg.HorizontalLayout)
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

@demosection(dcg.DrawImage)
@documented
def _draw_images(C: dcg.Context):
    """
    ### Drawing Images
    
    `dcg.DrawImage` enables to draw a static image at a specified position.
    It supports three ways to express its position in space:
    - p1, p2, p3, p4, the positions of the corners of the image, in
       a clockwise order
    - pmin and pmax, where pmin = p1, and pmax = p3, and p2/p4
        are automatically set such that the image is parallel
        to the axes.
    - center, direction, width, height for the coordinate of the center,
        the angle of (center, middle of p2 and p3) against the x horizontal axis,
        and the width/height of the image at direction 0.

    The systems are similar, but writing to p1/p2/p3/p4 is more expressive
    as it allows to have non-rectangular shapes.
    The last system enables to indicate a size in screen space rather
    than in coordinate space by passing negative values to width and height.

    Finally, it takes uv1/uv2/uv3/uv4 parameters. They are the normalized
    texture coordinates at p1/p2/p3/p4. uv1 = (0, 0) means that the top
    left of the texture is at p1, and uv3 = (1, 1) means that the bottom
    right of the texture is at p3.

    It can be useful to use uv1/uv2/uv3/uv4 to display only a portion of a texture,
    for instance when combining a lot of small images in a texture (which is a common
    practice in game development for performance reasons).

    The texture passed must be a `dcg.Texture` object (see next section).

    `DrawImage` take also as input:
    - color_multiplier: a color multiplier applied to the whole image
    - rounding: if set, the borders will be rounded (useful for custom buttons).
        The image requires to be parallel to the axes with this setting.

    """


@demosection(dcg.Texture)
@documented
def _draw_texture(C: dcg.Context):
    """
    Textures are a representation of an image content in GPU memory.
    They are required for dcg.DrawImage.

    DearCyGui supports displaying two types of textures:
    - uint8 textures, which are 8-bit unsigned integer textures
        (i.e. 0-255 for each channel).
    - float textures, which are 32-bit floating point textures
        (i.e. 0.0-1.0 for each channel).

    The textures can have 1 (gray), 2 (red, green), 3 (red, green, blue),
    or 4 (red, green, blue, alpha) channels.

    To create a texture, you need to pass an array (for instance a numpy array)
    to dcg.Texture's set_value method. Alternatively it can be passed at
    texture creation as secondary positional parameter (after the context).

    Textures can be created at any moment and are uploaded to the GPU right away.
    The upload does not block rendering and is not instantaneous. It can be
    performed in a background thread. The texture content can be resized, and
    DearCyGui implements a pool of released textures, thus it is close in performance
    between creating a new dcg.Texture and reusing an existing one.

    Additional parameters are:
    - hint_dynamic: This parameter affects GPU texture placement and
        indicates that the texture may be very frequently updated (e.g. every frame).
    - nearest_neighbor_upsampling: If set, when the texture is zoomed in, it will
        use nearest neighbor interpolation instead of bilinear interpolation.

    """


@demosection(dcg.DrawInWindow, dcg.utils.DrawStream)
@documented
@democode
def _draw_animation(C: dcg.Context):
    """
    ### Animated Drawing Elements
    
    DearCyGui supports creating animations with these key components:
    
    - `DrawStream`: A container for time-based drawing elements
    - Timing control for frame-by-frame animation
    - Integration with `DrawInWindow` for interactive animated widgets
    
    This example shows:
    1. Basic animation using `DrawStream`
    2. Creating a custom animated button with GIF support 
    3. Programmatic shape animation
    
    Animations are great for providing visual feedback and creating engaging interfaces.
    """
    class GifButton(dcg.DrawInWindow):
        """A button that displays an animated GIF using DrawInWindow and DrawStream"""
        
        def __init__(self, context, gif_path, width=0, height=0, **kwargs):
            """Initialize the GIF button
            
            Args:
                context: DearCyGui context
                gif_path: Path to GIF file
                width: Width of button (0 = autosize)
                height: Height of button (0 = autosize) 
                **kwargs: Additional arguments passed to DrawInWindow
            """
            # Create button behavior and prepare container
            super().__init__(context, button=True, width=width, height=height, **kwargs)
            
            # Load GIF and convert frames to textures
            self._frames = []
            self._frame_durations = []
            self._total_duration = 0
            
            gif = Image.open(gif_path)
            try:
                while True:
                    # Convert frame to RGBA
                    frame = np.array(gif.convert('RGBA'))
                    
                    # Create texture from frame
                    texture = dcg.Texture(context)
                    texture.set_value(frame)
                    self._frames.append(texture)
                    
                    # Get frame duration in seconds
                    duration = gif.info.get('duration', 100) / 1000.0  # Default 100ms if not specified
                    self._frame_durations.append(duration)
                    self._total_duration += duration
                    
                    # Try to move to next frame
                    gif.seek(gif.tell() + 1)
            except EOFError:
                pass  # End of frames reached

            # Create draw stream for animation
            self._stream = dcg.utils.DrawStream(context, parent=self)
            self._stream.time_modulus = self._total_duration
            
            # Setup initial frame display and animation
            elapsed_time = 0
            for i, texture in enumerate(self._frames):
                # Add frame to stream with its duration
                expiry = elapsed_time + self._frame_durations[i]
                image = dcg.DrawImage(context, texture=texture)
                if width > 0 and height > 0:
                    # Use explicit dimensions if provided
                    image.pmin = (0, 0)
                    image.pmax = (width, height)
                self._stream.push(image, expiry)
                elapsed_time = expiry
    
    class AnimatedSpinner(dcg.DrawInWindow):
        """A spinning loader animation using programmatic drawing"""
        
        def __init__(self, context, radius=30, color=(0, 119, 255), **kwargs):
            """Initialize the spinner
            
            Args:
                context: DearCyGui context
                radius: Radius of the spinner
                color: Base color of the spinner
                **kwargs: Additional arguments passed to DrawInWindow
            """
            size = radius * 2 + 10  # Add padding
            super().__init__(context, width=size, height=size, **kwargs)
            
            self._radius = radius
            self._center_x = size // 2
            self._center_y = size // 2
            self._base_color = color
            self._start_time = time.time()
            
            # Create draw stream
            self._stream = dcg.utils.DrawStream(context, parent=self)
            self._stream.time_modulus = 2.0  # 2 second animation cycle
            
            # Create animation frames
            self._create_animation(context)
        
        def _create_animation(self, context):
            # Create 20 frames for smooth animation
            num_segments = 8
            segments_per_frame = 1
            rotation_per_frame = 2 * math.pi / 20  # Full rotation in 20 frames
            
            for frame in range(20):
                # Calculate rotation for this frame
                rotation = frame * rotation_per_frame
                
                # Create a drawing list for this frame
                elapsed_time = frame / 10.0  # 10 frames per second
                expiry_time = elapsed_time + 0.1  # Each frame lasts 0.1 seconds
                
                with dcg.DrawingList(context) as drawing:
                    # Draw segments with varying opacity
                    for i in range(num_segments):
                        angle = rotation + (i * 2 * math.pi / num_segments)
                        
                        # Calculate position
                        x1 = self._center_x + self._radius * 0.5 * math.cos(angle)
                        y1 = self._center_y + self._radius * 0.5 * math.sin(angle)
                        x2 = self._center_x + self._radius * math.cos(angle)
                        y2 = self._center_y + self._radius * math.sin(angle)
                        
                        # Calculate opacity (fade based on position in rotation)
                        opacity = 55 + 200 * (i / num_segments)
                        color = (self._base_color[0], self._base_color[1], self._base_color[2], int(opacity))
                        
                        # Draw the segment
                        dcg.DrawLine(context, p1=(x1, y1), p2=(x2, y2), color=color, thickness=-3)
                
                # Add to stream
                self._stream.push(drawing, expiry_time)
    
    class PulsingCircle(dcg.DrawInWindow):
        """A circle that pulses in and out with color changes"""
        
        def __init__(self, context, radius=40, **kwargs):
            """Initialize the pulsing circle
            
            Args:
                context: DearCyGui context
                radius: Maximum radius of the circle
                **kwargs: Additional arguments passed to DrawInWindow
            """
            size = radius * 2 + 20  # Add padding
            super().__init__(context, width=size, height=size, **kwargs)
            
            self._max_radius = radius
            self._center_x = size // 2
            self._center_y = size // 2
            
            # Create draw stream with 3-second cycle
            self._stream = dcg.utils.DrawStream(context, parent=self)
            self._stream.time_modulus = 3.0
            
            # Create animation frames
            self._create_animation(context)
        
        def _create_animation(self, context):
            # Create 60 frames for a smooth 3-second animation (20fps)
            num_frames = 60
            
            for frame in range(num_frames):
                # Calculate progress through animation (0.0 to 1.0)
                progress = frame / num_frames
                t = progress * 2 * math.pi  # Convert to radians for sin/cos
                
                # Calculate radius and color for this frame
                radius_factor = 0.5 + 0.5 * math.sin(t)  # Oscillate between 0.5 and 1.0
                radius = self._max_radius * radius_factor
                
                # Create oscillating colors
                r = int(127 + 127 * math.sin(t))
                g = int(127 + 127 * math.sin(t + 2*math.pi/3))
                b = int(127 + 127 * math.sin(t + 4*math.pi/3))
                
                # Create a drawing for this frame
                elapsed_time = 3.0 * progress
                expiry_time = elapsed_time + 0.05  # Each frame lasts 0.05 seconds
                
                with dcg.DrawingList(context) as drawing:
                    # Draw the circle
                    dcg.DrawCircle(context, 
                                  center=(self._center_x, self._center_y),
                                  radius=radius,
                                  color=(r, g, b, 255),
                                  fill=(r, g, b, 100),
                                  thickness=-2)
                
                # Add to stream
                self._stream.push(drawing, expiry_time)
    
    # Display the examples
    with dcg.VerticalLayout(C, width=-1):
        dcg.Text(C, value="Animation Examples")
        
        # For GIF example, we should check if the demo gif exists
        current_dir = os.path.dirname(os.path.abspath(__file__))
        demo_gif_path = os.path.join(current_dir, "..", "demo_cython_subclassing", "demo.gif")
        try:
            dcg.Text(C, value="1. Animated GIF Button")
            gif_button = GifButton(C, gif_path=demo_gif_path, width=150, height=100)
            click_animation = dcg.Text(C, value="Click the animation!")
            
            # Add click handler to demonstrate interactivity
            def on_button_click():
                dcg.Text(C,
                         previous_sibling=click_animation,
                         value=f"Button clicked at {time.strftime('%H:%M:%S')}")
            
            gif_button.callback = on_button_click
        except Exception as e:
            dcg.Text(C, value=f"Could not load GIF example: {str(e)}")
        
        dcg.Separator(C)
        
        # Programmatic animations
        with dcg.HorizontalLayout(C, width=-1):
            # Spinner example
            with dcg.VerticalLayout(C):
                dcg.Text(C, value="2. Loading Spinner")
                AnimatedSpinner(C, radius=30)
            
            # Pulsing circle example
            with dcg.VerticalLayout(C):
                dcg.Text(C, value="3. Pulsing Circle")
                PulsingCircle(C, radius=35)
        
        dcg.Separator(C)
        
        # Explanation of DrawStream
        dcg.Text(C, value="How DrawStream Works:", color=(255, 255, 0))
        dcg.Text(C, value="1. Create a DrawStream container and set its time_modulus (cycle length)")
        dcg.Text(C, value="2. Push drawing items with expiry times (when to switch to the next item)")
        dcg.Text(C, value="3. The stream automatically displays the correct item based on elapsed time")
        dcg.Text(C, value="4. The viewport is woken up at the end of each cycle to render the next item")
        dcg.Text(C, value="5. For smooth animation, create many frames with short display durations")


@demosection(dcg.Context, dcg.Texture)
@documented
def _draw_texture_advanced(C: dcg.Context):
    """
    ### Advanced Texture Usage

    dcg.Texture allows various advanced features:
    - The `read` method allows to read the texture content back to a numpy array.
        It is possible to only read a portion of the texture.
    - The content of DearCyGui can be retrieved as a Texture. For this
        purpose the Viewport's `retrieve_framebuffer` parameter must be set
        to True. This will create a framebuffer object every frame, which
        can be accessed through the Viewport's `framebuffer` attribute.
    - The `allocate` method allows to allocate a texture without uploading
        data. This is useful when you can to create a texture that will be
        shared with another OpenGL context, and do not want to initialize
        it with `set_value`.
    - The `texture_id` attribute allows to access the OpenGL texture ID. This
        can be used to share the texture with another OpenGL context.

    #### OpenGL sharing

    There are several ways to retrieve an OpenGL context in DearCyGui:
    - The easiest one is through the context's `create_new_shared_gl_context`.
        This will create a new OpenGL context that shares access to DearCyGui's
        resources. It returns a `SharedGLContext` object, which has the methods
        `make_current` to make the context current, and `release` to release
        it. `destroy` terminates the context. It supports the `with` statement.
    - The context's `rendering_context` attribute returns a `BackendRenderingContext`
        object, which only supports the `with` syntax and locks texture uploads. It should
        not be used directly for rendering, but can be used to create a shared GL
        context with external tools (such as OpenCL, CUDA, etc.).

    Note a context must not be current when creating and allocating a new dcg.Texture.

    #### Importing an external texture

    It is not possible to import an external texture directly in DearCyGui. It must
    be created through dcg.Texture.

    #### OpenGL to DearCyGui - DearCyGui to OpenGL

    When rendering in separate OpenGL contexts, it is important both for performance
    and to avoid glitches to properly synchronize rendering to textures and using
    texture contents.

    For the purpose of DearCyGui using a texture rendered in an external GL context,
    `dcg.Texture` provides the following methods:
    - `gl_begin_write`: Locks a texture for a write operation for an external GL context.

        The target GL context MUST be current.

        The call inserts a GPU fence to ensure any previous
        DearCyGui rendering reading from the texture finishes
        before the texture is written to.
    - `gl_end_write`: Unlocks a texture after a write operation for an external GL context.

        The target GL context MUST be current.

        The call issues a GPU fence that will be used by
        DearCyGui to ensure the texture is not read from
        before the write operation has finished.

    Note if you render only once to the texture and do not update it (and uses glFinish),
    there is no need to synchronize.

    For the purpose of external OpenGL using DearCyGui's framebuffer,
    `dcg.Texture` provides the following methods:
    - `gl_begin_read`: Locks a texture for a read operation for an external GL context.

        The target GL context MUST be current.

        The call inserts a GPU fence to ensure any previous
        DearCyGui rendering or upload finishes before the texture
        is read.
    - `gl_end_read`: Unlocks a texture after a read operation for an external GL context.

        The target GL context MUST be current.

        The call issues a GPU fence that will be used by
        DearCyGui to ensure the texture is not written to
        before the read operation has finished.

    Note that DearCyGui does not need to have a visible window to render !
    It is entirely possible to render only to a framebuffer and display the
    result in another OpenGL context.

    For this purpose, the viewport can be initialized with `visible=False`
    and `retrieve_framebuffer=True`.

    As the viewport will not have any window, it will need to receive keyboard
    and mouse events manually. You can inform DearCyGui of these events using
    the context methods `inject_key_down`, `inject_key_up`, `inject_mouse_pos`,
    `inject_mouse_button_down`, `inject_mouse_button_up`, and `inject_mouse_wheel`.

    Note due to SDL constraints, it is not possible to create DearCyGui contexts
    in separate threads, nor it is possible to call `render_frame` in a separate thread.
    """
    pass

@demosection(dcg.ChildWindow, dcg.Texture, dcg.CustomHandler, dcg.RenderHandler)
@documented
@democode
def _draw_texture_advanced_example(C: dcg.Context):
    """
    ### Advanced Texture Usage with OpenGL Integration
    
    This example demonstrates most of the advanced texture usage features
    presented in the previous section. It shows how to create a shared OpenGL
    context, render a cube in that context, and then use the rendered texture
    in the main DearCyGui context. It also demonstrates how to synchronize
    rendering between the two contexts.
    """
    try:
        import moderngl
        import pyrr
    except ImportError:
        dcg.Text(C, value="This example requires the moderngl and pyrr packages.\n"
                          "Please install them using 'pip install moderngl pyrr'.",
                          color=(255, 255, 255), size=-16)
        return
    
    class CubeDemo(dcg.ChildWindow):
        def __init__(self, main_context, **kwargs):
            super().__init__(main_context, **kwargs)
            self.start_time = time.time()
            
            # Create OpenGL shared context
            self.shared_context = main_context.create_new_shared_gl_context(3, 3)
            if self.shared_context is None:
                raise ValueError("Failed to create shared context")
            
            # Setup ModernGL and create resources
            self.shared_context.make_current()
            self.ctx = moderngl.create_context()
            
            # Define shaders
            self.program = self.ctx.program(
                vertex_shader="""
                #version 330 core
                in vec3 position;
                in vec2 texCoord;
                out vec2 vTexCoord;
                uniform mat4 model;
                uniform mat4 view;
                uniform mat4 projection;
                
                void main() {
                    gl_Position = projection * view * model * vec4(position, 1.0);
                    vTexCoord = texCoord;
                }
                """,
                fragment_shader="""
                #version 330 core
                in vec2 vTexCoord;
                out vec4 fragColor;
                uniform sampler2D tex;
                
                void main() {
                    fragColor = texture(tex, vTexCoord);
                }
                """
            )
            
            # Create cube vertices and indices
            cube_vertices = np.array([
                # front face
                -1.0, -1.0, -1.0,  0.0, 1.0,
                -1.0,  1.0, -1.0,  0.0, 0.0,
                 1.0,  1.0, -1.0,  1.0, 0.0,
                 1.0, -1.0, -1.0,  1.0, 1.0,
                
                # back face
                 1.0, -1.0,  1.0,  0.0, 1.0,
                 1.0,  1.0,  1.0,  0.0, 0.0,
                -1.0,  1.0,  1.0,  1.0, 0.0,
                -1.0, -1.0,  1.0,  1.0, 1.0,
                
                # left face
                -1.0, -1.0,  1.0,  0.0, 1.0,
                -1.0,  1.0,  1.0,  0.0, 0.0,
                -1.0,  1.0, -1.0,  1.0, 0.0,
                -1.0, -1.0, -1.0,  1.0, 1.0,
                
                # right face
                 1.0, -1.0, -1.0,  0.0, 1.0,
                 1.0,  1.0, -1.0,  0.0, 0.0,
                 1.0,  1.0,  1.0,  1.0, 0.0,
                 1.0, -1.0,  1.0,  1.0, 1.0,
                
                # top face
                -1.0,  1.0, -1.0,  0.0, 1.0,
                -1.0,  1.0,  1.0,  0.0, 0.0,
                 1.0,  1.0,  1.0,  1.0, 0.0,
                 1.0,  1.0, -1.0,  1.0, 1.0,
                
                # bottom face
                -1.0, -1.0,  1.0,  0.0, 1.0,
                -1.0, -1.0, -1.0,  0.0, 0.0,
                 1.0, -1.0, -1.0,  1.0, 0.0,
                 1.0, -1.0,  1.0,  1.0, 1.0
            ], dtype='f4')

            cube_indices = np.array([
                # front
                0, 1, 2, 2, 3, 0,
                # back
                4, 5, 6, 6, 7, 4,
                # left
                8, 9, 10, 10, 11, 8,
                # right
                12, 13, 14, 14, 15, 12,
                # top
                16, 17, 18, 18, 19, 16,
                # bottom
                20, 21, 22, 22, 23, 20
            ], dtype='i4')
            
            # Create vertex buffer, index buffer, and vertex array
            self.vbo = self.ctx.buffer(cube_vertices.tobytes())
            self.ibo = self.ctx.buffer(cube_indices.tobytes())
            self.vao = self.ctx.vertex_array(
                self.program,
                [(self.vbo, '3f 2f', 'position', 'texCoord')],
                self.ibo
            )
            
            # Create output texture for the main context
            self.shared_context.release() # Important to release the context before creating the texture
            self.output_texture = dcg.Texture(main_context)
            self.output_texture.allocate(width=1024, height=1024, num_chans=4, uint8=True)
            self.shared_context.make_current()
            
            # Create OpenGL resources for rendering
            dcg_texture = self.ctx.external_texture(
                self.output_texture.texture_id, 
                (self.output_texture.width, self.output_texture.height), 
                4, 0, "f1"
            )
            
            depth_rb = self.ctx.depth_renderbuffer(
                (self.output_texture.width, self.output_texture.height)
            )
            
            self.fbo = self.ctx.framebuffer(
                color_attachments=[dcg_texture],
                depth_attachment=depth_rb
            )
            
            self.shared_context.release()

            with self:
                with dcg.VerticalLayout(C, alignment_mode=dcg.Alignment.CENTER):
                    with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.CENTER):
                        # Create a DearCyGui window to display the cube
                        dcg.Image(main_context, texture=self.output_texture)

        def render(self, invisible_context):
            # Get the DearCyGui framebuffer from invisible context
            ui_texture = invisible_context.viewport.framebuffer
            
            # Make our OpenGL context current
            self.shared_context.make_current()
            
            # Get the UI texture as ModernGL texture
            moderngl_ui_texture = self.ctx.external_texture(
                ui_texture.texture_id,
                (ui_texture.width, ui_texture.height),
                4, 0, "f1"
            )
            
            # Set texture parameters
            moderngl_ui_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
            moderngl_ui_texture.repeat_x = False
            moderngl_ui_texture.repeat_y = False
            moderngl_ui_texture.use(0)
            
            # Begin synchronization for textures
            ui_texture.gl_begin_read()
            self.output_texture.gl_begin_write()
            
            # prepare rendering to our framebuffer
            self.fbo.use()
            
            # Enable OpenGL features
            self.ctx.enable(moderngl.DEPTH_TEST)
            self.ctx.enable(moderngl.CULL_FACE)
            self.ctx.front_face = 'ccw'
            
            # Calculate rotation based on time (slow rotation)
            elapsed = time.time() - self.start_time
            angle_x = 20.0 * math.sin(elapsed * 0.2)
            angle_y = 30.0 * math.sin(elapsed * 0.1)
            angle_z = 15.0 * math.sin(elapsed * 0.15)
            
            # Create model matrix with rotation
            rotation = pyrr.matrix44.create_from_eulers([
                math.radians(angle_x), 
                math.radians(angle_y), 
                math.radians(angle_z)
            ])
            model_matrix = pyrr.matrix44.create_identity()
            model_matrix = pyrr.matrix44.multiply(model_matrix, rotation)
            
            # Set uniform values
            self.program['model'].write(model_matrix.astype('f4').tobytes())
            self.program['view'].write(pyrr.matrix44.create_look_at(
                eye=[3.0, 3.0, 3.0],
                target=[0.0, 0.0, 0.0],
                up=[0.0, 1.0, 0.0]
            ).astype('f4').tobytes())
            self.program['projection'].write(pyrr.matrix44.create_perspective_projection(
                fovy=45.0, aspect=1.0, near=0.1, far=100.0
            ).astype('f4').tobytes())
            
            # Clear framebuffer
            self.ctx.clear(0.1, 0.1, 0.1, 1.0)
            
            # Render the cube
            self.vao.render(moderngl.TRIANGLES)
            
            # End synchronization
            ui_texture.gl_end_read()
            self.output_texture.gl_end_write()
            
            # Release the ModernGL texture and shared context
            moderngl_ui_texture.release()
            self.shared_context.release()
            
            # Inform main context of updated content
            self.context.viewport.wake()
            
            return self.output_texture
        
        def __del__(self):
            try:
                self.shared_context.make_current()
                self.vao.release()
                self.vbo.release()
                self.ibo.release()
                self.program.release()
                self.fbo.release()
                self.ctx.release()
                self.shared_context.release()
            except:
                pass

    class InvisibleUI(dcg.Window):
        def __init__(self, invisible_context: dcg.Context):
            super().__init__(invisible_context,
                             parent=invisible_context.viewport,
                             primary=True)
            self.no_scrollbar = True
            # Create UI elements that will appear on the cube
            with self:
                dcg.Text(invisible_context, value=f"DearCyGui + OpenGL Integration", 
                        color=(255, 255, 255), scaling_factor=2.)
                
                dcg.Separator(invisible_context)
                
                # Add some dynamic content
                self.current_time = dcg.TextValue(
                    invisible_context, 
                    print_format="Current time: %.1f s",
                    shareable_value=dcg.SharedDouble(invisible_context, 0.0),
                    scaling_factor=1.3
                )
                
                # Add rotating star shape
                with dcg.DrawInWindow(invisible_context, width=-1, height=-1) as self.diw:                
                    # Add some animated shapes
                    dcg.DrawStar(invisible_context, center=(175, 175), 
                            radius=150, num_points=5,
                            color=(255, 255, 0), fill=(255, 255, 0, 150),
                            inner_radius=70, thickness=-2)
                    
                    # Add text in the center
                    dcg.DrawText(invisible_context, pos=(175, 175), 
                            text="3D CUBE", size=-48, 
                            color=(255, 255, 255))
                # Draw at the corners to indicate cube borders
                with dcg.ViewportDrawList(invisible_context, front=True,
                                          parent=invisible_context.viewport):
                    dcg.DrawRect(invisible_context,
                                 pmin=(0, 0),
                                 pmax=(invisible_context.viewport.pixel_width,
                                       invisible_context.viewport.pixel_height),
                                 color=(255, 255, 255),
                                 fill=(0, 0, 0, 0),
                                 thickness=-30)

        def update(self):
            t = time.time()
            # Update rotation and colors
            for item in self.diw.children:
                if hasattr(item, 'direction'):
                    item.direction = (t%100) * 0.3
                if hasattr(item, 'color'):
                    r = int(127 + 127 * math.sin(t * 0.7))
                    g = int(127 + 127 * math.sin(t * 0.5))
                    b = int(127 + 127 * math.sin(t * 0.3))
                    item.color = (r, g, b)
                if hasattr(item, 'fill'):
                    item.fill = (r//2, g//2, b//2, 150)
                 
                # Update time display
                self.current_time.value = t

    with C.rendering_context:
        invisible_context = dcg.Context()
    invisible_context.viewport.initialize(
        visible=False, retrieve_framebuffer=True, 
        width=512, height=512,
        title="Invisible")
    invisible_context.viewport.theme = \
        dcg.ThemeColorImGui(invisible_context,
                            Text=(30, 0, 30),
                            WindowBg=(180, 180, 180))

    invisible_ui = InvisibleUI(invisible_context)
    cube_demo = CubeDemo(C, width=-1, auto_resize_y=True)

    # update loop:
    # We cheat around the limitation that render_frame
    # must be called from the main thread by using
    # a CustomHandler.
    class MainThreadCallbackHandler(dcg.CustomHandler):
        def __init__(self, context, callback):
            super().__init__(context)
            self.mt_callback = callback

        def check_can_bind(self, target):
            return True

        def check_status(self):
            return True

        def run(self, target):
            self.mt_callback()

    def render_invisible_ui():
        # Update the invisible UI
        # Okay to render in the main thread
        # because we do not use the main context
        # at all.
        invisible_ui.update()
        invisible_context.viewport.render_frame()

    def render_cube():
        # Render the cube (NOT in the main thread!!!),
        cube_demo.render(invisible_context)

    cube_demo.handlers += [
        MainThreadCallbackHandler(C, callback=render_invisible_ui),
        dcg.RenderHandler(C, callback=render_cube)
    ]

pop_group()          

if __name__ == "__main__":
    launch_demo(title="Drawing Demo")