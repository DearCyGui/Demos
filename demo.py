import dearcygui as dcg
from dearcygui.fonts import make_bold, make_bold_italic, make_italic
from documentation import display_docstring, TextFormatter
import marko

from utils import create_new_font

def display_text(C, text):
    renderer = TextFormatter(C)
    parsed_text = marko.Markdown().parse(text)
    renderer.render(parsed_text)

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
            dcg.Text(C, value=f"Click to see {dcg.fonts.make_bold_italic(object.__name__)} docstring")

    cw.handlers = [
        display_mouse_when_hovered,
        # React to click anywhere inside the window
        dcg.ClickedHandler(C, button=0, callback=expand_or_restore_height)
    ]
    # Reduce spacing between lines
    cw.theme = dcg.ThemeStyleImGui(C, FramePadding=(0,0), FrameBorderSize=0, ItemSpacing=(0, 0))

def create_demo_window(C : dcg.Context):
    huge_font = create_new_font(C, 51)
    big_font = create_new_font(C, 31)
    default_font = C.viewport.font
    # A strong or monochrome hinter helps fonts
    # being readable at small sizes
    small_font = create_new_font(C, 9, hinter="strong")

    with dcg.Window(C, width=1000, height=600, label="Demo window") as window:
        with dcg.CollapsingHeader(C, label="Buttons") as first_header:
            with dcg.Tooltip(C, target=first_header, parent=window):
                # Note we set the parent to the window as what is inside
                # a collapsing header is only run if opened.
                dcg.Text(C, value="Click to open this section")
            display_docstring_in_child_window(C, dcg.Button)

def center_window(sender, item : dcg.Window):
    real_pixel_size = item.rect_size
    available_width = item.parent.width
    available_height = item.parent.height
    target_left = round(available_width / 2. - real_pixel_size[0] / 2.)
    target_top = round(available_height / 2. - real_pixel_size[1] / 2.)
    item.pos_to_viewport = [target_left, target_top]
    item.context.viewport.wake()

def make_welcome_window(C):
    huge_font = create_new_font(C, 51)
    # A strong or monochrome hinter helps fonts
    # being readable at small sizes
    small_font = create_new_font(C, 9, hinter="strong")
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
        C.viewport.render_frame(can_skip_presenting=False)

if __name__ == '__main__':
    launch_demo()