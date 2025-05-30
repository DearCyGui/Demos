import dearcygui as dcg
from dearcygui.font import make_bold, make_bold_italic, make_italic
from documentation import display_docstring, MarkDownText
import math
import time


def expand_or_restore_height(_, item : dcg.ChildWindow):
    item.height = (50 if item.height == -1 else -1)

class ItemNotExpanded(dcg.CustomHandler):
    def check_can_bind(self, item):
        return isinstance(item, dcg.ChildWindow)
    def check_status(self, item : dcg.ChildWindow):
        return item.height != -1

def display_docstring_in_child_window(C, object):
    """
    Retrieve the docstring of the target
    object and display the text in a box
    """
    with dcg.ChildWindow(C, width=-1, height=50) as cw:
        display_docstring(C, object)
    # show we can expand
    with dcg.ConditionalHandler(C) as display_mouse_when_hovered:
        dcg.MouseCursorHandler(C, cursor=dcg.MouseCursor.Hand)
        dcg.HoverHandler(C)

    # Tooltip to display hint, but only if not expanded
    with dcg.HandlerList(C, op=dcg.HandlerListOP.ALL) as hl:
        ItemNotExpanded(C)
        dcg.HoverHandler(C)

    with cw:
        with dcg.Tooltip(C, condition_from_handler=hl, target=cw) as to:
            dcg.Text(C, value=f"Click to see {dcg.font.make_bold_italic(object.__name__)} docstring")

    cw.handlers = [
        display_mouse_when_hovered,
        # React to click anywhere inside the window
        dcg.ClickedHandler(C, button=0, callback=expand_or_restore_height)
    ]
    # Reduce spacing between lines
    cw.theme = dcg.ThemeStyleImGui(C, FramePadding=(0,0), FrameBorderSize=0, ItemSpacing=(0, 0))

def create_demo_window(C : dcg.Context):
    huge_font = dcg.AutoFont(C, 51)
    big_font = dcg.AutoFont(C, 31)
    default_font = C.viewport.font
    # A strong or monochrome hinter helps fonts
    # being readable at small sizes
    small_font = dcg.AutoFont(C, 9, hinter="strong")

    with dcg.Window(C, width=1000, height=600, label="Demo window") as window:
        with dcg.CollapsingHeader(C, label="Buttons") as first_header:
            with dcg.Tooltip(C, target=first_header, parent=window):
                # Note we set the parent to the window as what is inside
                # a collapsing header is only run if opened.
                dcg.Text(C, value="Click to open this section")
            #display_docstring_in_child_window(C, dcg.Button)
        with dcg.CollapsingHeader(C, label="Draw items") as draw_items:
            # TODO: this looks very ugly, positions are not good
            dcg.Text(C, value="Some available shapes:")
            with dcg.DrawInWindow(C, width=600, height=600):
                dcg.DrawArrow(C, p1 = [80, 50], p2 = [50, 50])
                dcg.DrawBezierCubic(C, p1 = [150, 20], p2 = [110, 60], p3 = [120, 80], p4 = [130, 85])
                dcg.DrawBezierQuadratic(C, p1 = [200, 20], p2 = [160, 60], p3 = [180, 85])
                dcg.DrawEllipse(C, pmin=[250, 20], pmax=[300, 80], color = (0, 255, 0), fill=(0, 200, 0))
                dcg.DrawLine(C, p1=[50, 100], p2 = [300, 100], color = [0, 0, 255])
                dcg.DrawPolygon(C, points=[[50, 120], [30, 150], [50, 180], [80, 180], [80, 120]], fill=(80, 0, 125))
                dcg.DrawCircle(C, center=[100, 200], radius=40, color=(255, 0, 0), fill=(255, 200, 200))
                dcg.DrawRect(C, pmin=[150, 150], pmax=[200, 200], color=(0, 255, 0), fill=(200, 255, 200))
                dcg.DrawText(C, pos=[250, 250], text="Hello, DearCyGui!", color=(0, 0, 255))
                dcg.DrawTriangle(C, p1=[300, 300], p2=[350, 350], p3=[300, 350], color=(255, 255, 0), fill=(255, 255, 200))
                dcg.DrawPolyline(C, points=[[400, 400], [450, 450], [400, 450]], color=(0, 255, 255))
                dcg.DrawQuad(C, p1=[500, 500], p2=[550, 500], p3=[550, 550], p4=[500, 550], color=(255, 0, 255), fill=(255, 200, 255))
            with dcg.DrawInWindow(C, width=600, height=200) as diw:
                # Update loop
                def update_items(_, target):
                    direction = time.monotonic() * 0.1
                    direction -= int(direction)
                    direction *= 2 * 3.1415
                    inner_radius_factor = math.sin(time.monotonic() * 0.67)
                    for item in target.children:
                        if hasattr(item, 'direction'):
                            item.direction = direction
                        if hasattr(item, 'inner_radius'):
                            item.inner_radius = inner_radius_factor * item.radius
                    target.context.viewport.wake() # Do not stop rendering when visible
                diw.handlers = dcg.RenderHandler(C, callback=update_items)

                dcg.DrawRegularPolygon(C, center=[50, 80], radius=30, num_points=1, direction = 0.1, fill=(40, 40, 40))
                dcg.DrawRegularPolygon(C, center=[150, 80], radius=30, num_points=2, direction = 0.1, fill=(40, 40, 40))
                dcg.DrawRegularPolygon(C, center=[250, 80], radius=30, num_points=3, direction = 0.1, fill=(40, 40, 40))
                dcg.DrawRegularPolygon(C, center=[350, 80], radius=30, num_points=4, direction = 0.1, fill=(40, 40, 40))
                dcg.DrawRegularPolygon(C, center=[450, 80], radius=30, num_points=5, direction = 0.1, fill=(40, 40, 40))
                dcg.DrawRegularPolygon(C, center=[550, 80], radius=30, num_points=6, direction = 0.1, fill=(40, 40, 40))
                dcg.DrawStar(C, center=[100, 120], radius=30, num_points=3, direction = 0.1, inner_radius=10, fill=(40, 40, 40))
                dcg.DrawStar(C, center=[200, 120], radius=30, num_points=4, direction = 0.1, inner_radius=10, fill=(40, 40, 40))
                dcg.DrawStar(C, center=[300, 120], radius=30, num_points=5, direction = 0.1, inner_radius=10, fill=(40, 40, 40))
                dcg.DrawStar(C, center=[400, 120], radius=30, num_points=6, direction = 0.1, inner_radius=10, fill=(40, 40, 40))
                dcg.DrawStar(C, center=[500, 120], radius=30, num_points=7, direction = 0.1, inner_radius=10, fill=(40, 40, 40))

        # Add new section for ChildWindow demos
        with dcg.CollapsingHeader(C, label="Child Windows"):
            dcg.Text(C, value="Different types of child windows:")
            
            # Basic child window with border
            with dcg.ChildWindow(C, width=200, height=100, label="Basic Child"):
                dcg.Text(C, value="A basic child window with border")
            
            # Horizontal layout of child windows
            with dcg.HorizontalLayout(C):
                # Scrollable content
                with dcg.ChildWindow(C, width=200, height=100, label="Scrollable"):
                    for i in range(20):
                        dcg.Text(C, value=f"Scrollable content line {i}")
                
                # No scrollbar child
                with dcg.ChildWindow(C, width=200, height=100, label="No Scrollbar", no_scrollbar=True):
                    for i in range(20):
                        dcg.Text(C, value=f"No scroll content line {i}")
            
            # Child window with horizontal scrollbar
            with dcg.ChildWindow(C, width=200, height=100, label="H-Scroll", horizontal_scrollbar=True):
                dcg.Text(C, value="This is a very long text that will cause horizontal scrolling to appear in this child window")
            
            # Frameless child window
            with dcg.ChildWindow(C, width=200, height=100):
                dcg.Text(C, value="A frameless child window\nwithout borders")
            
            # Resizable child window
            with dcg.ChildWindow(C, width=200, height=100, label="Resizable", 
                               resizable_x=True, resizable_y=True):
                dcg.Text(C, value="Drag bottom-right corner to resize")

            # Auto-resizing child window
            with dcg.ChildWindow(C, width=0, height=0, label="Auto-size", 
                               auto_resize_x=True, auto_resize_y=True):
                dcg.Text(C, value="This child window auto-resizes\nto fit its content")

def center_window(sender, item : dcg.Window):
    real_pixel_size = item.rect_size
    available_width = item.parent.width
    available_height = item.parent.height
    target_left = round(available_width / 2. - real_pixel_size[0] / 2.)
    target_top = round(available_height / 2. - real_pixel_size[1] / 2.)
    item.pos_to_viewport = [target_left, target_top]
    item.context.viewport.wake()

def make_welcome_window(C):
    huge_font = dcg.AutoFont(C, 51)
    # A strong or monochrome hinter helps fonts
    # being readable at small sizes
    small_font = dcg.AutoFont(C, 9, hinter="strong")
    with dcg.Window(C, popup=True, autosize=True) as welcome_window:
        with dcg.HorizontalLayout(C, alignment_mode = dcg.Alignment.CENTER):
            dcg.Text(C, value="Welcome", font=huge_font)
        dcg.Spacer(C)
        with dcg.HorizontalLayout(C, alignment_mode = dcg.Alignment.CENTER):
            dcg.Text(C, value=f"We are pleased to welcome you to {make_bold_italic('DearCyGui')}.")
        dcg.Spacer(C)
        dcg.Text(C, value=f"In this demo, we will demonstrate several features of"
                 f" {make_bold_italic('DearCyGui')} and how to start writing your program.")
        dcg.Spacer(C)
        with dcg.HorizontalLayout(C, alignment_mode = dcg.Alignment.CENTER):
            dcg.Text(C, value=f"Use the {make_bold('documentation.py')} script for documentation.")
        dcg.Spacer(C)
        with dcg.HorizontalLayout(C, alignment_mode = dcg.Alignment.CENTER):
            dcg.Text(C, value="Click anywhere outside this window to start", font=small_font)
        welcome_window.handlers = [
            # The window doesn't have its final size right away, thus why we
            # use ResizeHandler and not GotRenderHandler
            dcg.ResizeHandler(C, callback=center_window)
        ]
        

def launch_demo():
    C = dcg.Context()
    # vsync: limit to screen refresh rate and have no tearing
    # wait_for_input: Do not refresh until a change is detected (C.viewport.wake() to help)
    C.viewport.initialize(vsync=True,
                          wait_for_input=True,
                          title="Welcome to DearCyGui")
    # primary: use the whole window area
    # no_bring_to_front_on_focus: enables to have windows on top to
    # add your custom UI, and not have them hidden when clicking on the image.

    # Declarative way of creating items
    create_demo_window(C)

    make_welcome_window(C)
    while C.running:
        # can_skip_presenting: no GPU re-rendering on input that has no impact (such as mouse motion) 
        C.viewport.render_frame()

if __name__ == '__main__':
    launch_demo()
