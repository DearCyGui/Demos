import dearcygui as dcg
from dearcygui.fonts import make_bold, make_bold_italic, make_italic

def create_new_font(C, size, **kwargs):
    # Manual DPI handling (method 2 described in Font texture)
    # This is needed for sharp fonts even for small sizes.
    current_scale = C.viewport.dpi * C.viewport.scale
    size = round(size*current_scale)
    # Load the default texture at the target size
    font_texture = dcg.FontTexture(C)
    font_texture.add_custom_font(*dcg.fonts.make_extended_latin_font(size, **kwargs))
    font = font_texture[0]
    # end of method 2 of manual DPI handling
    font.scale = 1./current_scale
    return font_texture[0]

def create_demo_window(C):
    huge_font = create_new_font(C, 51)
    big_font = create_new_font(C, 31)
    default_font = C.viewport.font
    # A strong or monochrome hinter helps fonts
    # being readable at small sizes
    small_font = create_new_font(C, 9, hinter="strong")

    with dcg.Window(C, width=1000, height=600, label="Demo window"):
        with dcg.CollapsingHeader(C, label="Basics") as first_header:
            with dcg.Tooltip(C, target=first_header):
                dcg.Text(C, value="Click to open this section")

            dcg.Text(C, wrap=0, value=f"{make_bold_italic("DearCyGui")} is a tool "
                     f"to write {make_bold("GUI")} applications in {make_bold_italic("Python")}. "
                     f"It is mainly written in {make_bold_italic("Cython")}, thus the name. "
                     f"{make_bold_italic("Cython")} knowledge is not required and 99% of your "
                     f"needs should be met using {make_bold_italic("Python")} only."
            )
            dcg.Spacer(C)
            dcg.Text(C, wrap=0, value=f"{make_bold_italic("Python")} is quite handy, "
                     f"but is not performant enough to render at full frame-rate "
                     f"complex UIs. The main idea of this library is to create items "
                     f"and declare how they should behave, and let the library handle "
                     f"rendering the items and check the conditions you registered for. "
                     f"The library is written mostly using {make_bold_italic("Cython")} code, "
                     f"which is converted into efficient {make_bold_italic("C ++")} code and "
                     f"compiled."
            )
            dcg.Spacer(C)
            dcg.Text(C, wrap=0, value=f"The first item you need to create is a "
                     f"{make_italic("Context")}."
            )
            dcg.Text(C, wrap=0, indent=-1, value=make_bold("C = dcg.Context()"))
            dcg.Text(C, wrap=0, value=f"The Context manages the state "
                     f"of your UI items."
            )
            dcg.Spacer(C)
            dcg.Text(C, wrap=0, value=f"With the Context is attached a single {make_italic("Viewport")}. "
                     f"The Viewport basically corresponds to your application window as seen "
                     f"by the operating system. It has a title, decoration, etc (this is configurable). "
                     f"Every frame, rendering starts from the viewport and, in a tree traversal fashion, "
                     f"all children of the viewport, their children, the children of their children, "
                     f"etc will be rendered. An item outside of this {make_italic("rendering")} tree can "
                     f"exist, but will not be rendered. In addition items attached in the rendering tree "
                     f"can prevent being rendered using the {make_bold("show")} attribute."
            )
            dcg.Text(C, wrap=0, value=f"Items can be created as soon as the Context is created, "
                     f"but for anything to be displayed, you need to initialize the viewport."
            )
            dcg.Text(C, wrap=0, indent=-1, value=make_bold("C.viewport.initialize()"))
            dcg.Spacer(C)
            dcg.Text(C, wrap=0, value=f"Once attached to the rendering tree, you do not need "
                     f"to retain a reference to the item for it to remain alive. You can "
                     f"retain a reference if you want to access later the object, or you "
                     f"can assign the {make_bold("tag")} field in order to give a name "
                     f"to your object and later reaccess it by indexing the Context with "
                     f"the assigned tag."
            )
            dcg.Text(C, wrap=0, value=f"To attach an item to another, several options are available")
            dcg.Text(C, wrap=0, bullet=True, value=f"You can set the {make_bold("parent")} attribute of your "
                     f"item to a reference to the parent or its {make_bold("tag")}.")
            dcg.Text(C, wrap=0, bullet=True, value=f"You can append the item to the {make_bold("children")} "
                     f"attribute of the target parent.")
            dcg.Text(C, wrap=0, bullet=True, value=f"Using the {make_bold("with")} syntax on the parent "
                     f"will attach all items inside the {make_bold("with")} to that parent")
            dcg.Text(C, indent=-1, value=f"with my_parent_item:")
            dcg.Text(C, indent=-1, value=f"    item = create_my_new_item()")
            dcg.Text(C, wrap=0, value=f"By default items try to attach to a parent unless "
                     f"{make_bold("attach=False")} is set during item creation.")



    with dcg.Window(C, popup=True, autosize=True):
        with dcg.HorizontalLayout(C, alignment_mode = dcg.alignment.CENTER):
            dcg.Text(C, value="Welcome", font=huge_font)
        dcg.Spacer(C)
        with dcg.HorizontalLayout(C, alignment_mode = dcg.alignment.CENTER):
            dcg.Text(C, value=f"We are pleased to welcome you to {make_bold_italic("DearCyGui")}.")
        dcg.Spacer(C)
        dcg.Text(C, value=f"In this demo, we will demonstrate several features of"
                 f" {make_bold_italic("DearCyGui")} and how to start writing your program.")
        dcg.Spacer(C)
        dcg.Spacer(C)
        with dcg.HorizontalLayout(C, alignment_mode = dcg.alignment.CENTER):
            dcg.Text(C, value="Click anywhere outside this window to start", font=small_font)
        

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

    create_demo_window(C)
    while C.running:
        # can_skip_presenting: no GPU re-rendering on input that has no impact (such as mouse motion) 
        C.viewport.render_frame(can_skip_presenting=True)

if __name__ == '__main__':
    launch_demo()