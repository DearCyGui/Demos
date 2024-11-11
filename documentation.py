import dearcygui as dcg
from dearcygui.fonts import make_bold, make_bold_italic, make_italic
import pydoc

from utils import create_new_font

import marko
import os

def expand_or_restore_height(_, item):
    item.height = (50 if item.height == -1 else -1)

def display_docstring(C, object):
    """
    Retrieve the docstring of the target
    object and display the text in a box
    """
    docstring = pydoc.render_doc(object, renderer=pydoc.plaintext)
    keyword = dir(dcg) + dir(object)
    lines_of_text = docstring.split("\n")
    for text in lines_of_text:
        words = text.split(' ')
        # make words with '_' bold.
        words = [make_bold(w) if ('_' in w or w in keyword) else w for w in words]
        text = ' '.join(words)
        dcg.Text(C, wrap=0, value=text)

def display_docstring_in_child_window(C, object):
    """
    Retrieve the docstring of the target
    object and display the text in a box
    """
    with dcg.ChildWindow(C, width=-1, height=50) as cw:
        display_docstring(C, object)
    # show we can expand
    with dcg.ConditionalHandler(C) as display_mouse_when_hovered:
        dcg.MouseCursorHandler(C, cursor=dcg.mouse_cursor.Hand)
        dcg.HoverHandler(C)

    cw.handlers = [
        display_mouse_when_hovered,
        # React to click anywhere inside the window
        dcg.ClickedHandler(C, button=0, callback=expand_or_restore_height)
    ]
    # Reduce spacing between lines
    cw.theme = dcg.ThemeStyleImGui(C, FramePadding=(0,0), FrameBorderSize=0, ItemSpacing=(0, 0))

class AvailableItems(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(self, **kwargs)

        with self:
            with dcg.HorizontalLayout(C, theme=dcg.ThemeStyleImGui(C, FramePadding=(0,0), FrameBorderSize=0, ItemSpacing=(0, 0))):
                with dcg.VerticalLayout(C):
                    filter = dcg.Combo(C, width=200)
                    left = dcg.ChildWindow(C, height=-1, width=200)
                right = dcg.ChildWindow(C, height=-1, width=-1)

            def is_item_sub_class(name, targets):
                try:
                    item = getattr(dcg, name)
                    for target in targets:
                        if issubclass(item, target):
                            return True
                except Exception:
                    return False
            filter_names = {
                "All": [dcg.baseItem, dcg.SharedValue],
                "Ui items": [dcg.uiItem, dcg.Texture, dcg.Font],
                "Handlers": [dcg.baseHandler],
                "Drawings": [dcg.drawingItem, dcg.Texture],
                "Plots": [dcg.plotElement, dcg.Plot, dcg.PlotAxisConfig, dcg.PlotLegendConfig],
                "Themes": [dcg.baseTheme],
                "Values": [dcg.SharedValue]
            }
            filter.items=filter_names.keys()
            filter.value="All"

            def update_item_list(sender, item, value):
                parent_classes = filter_names[value]
                dcg_items = dir(dcg)
                # remove items not starting with an upper case,
                # which are mainly for internal use, or items finishing by _
                dcg_items = [i for i in dcg_items if i[0].isupper() and i[-1] != '_']
                # remove items that are not subclasses of the target.
                dcg_items = [i for i in dcg_items if is_item_sub_class(i, parent_classes)]
                # Clear the previous list
                left.children = []
                with left:
                    for item_name in dcg_items:
                        dcg.Selectable(C, label=item_name, callback=handle_selection)
                C.viewport.wake()
            def handle_selection(item):
                # Unselect the other items
                for other_item in item.parent.children:
                    if other_item is item:
                        continue
                    if not(isinstance(other_item, dcg.Selectable)):
                        continue
                    other_item.value = False
                # Clear previous text
                right.children = []
                # Display text
                with right:
                    display_docstring(C, getattr(dcg, item.label))
                C.viewport.wake()
            update_item_list(filter, filter, filter.value)
            filter.callbacks = [update_item_list]

class Basics(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(self, **kwargs)

        with self:
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

class TextFormatter(marko.Renderer):
    def __init__(self, C):
        self.C = C
        self.huge_font = create_new_font(C, 51)
        self.big_font = create_new_font(C, 31)
        self.default_font = C.viewport.font
        self.raw_font = create_new_font(C, 17, hinter="monochrome")
        # A strong or monochrome hinter helps fonts
        # being readable at small sizes
        self.small_font = create_new_font(C, 9, hinter="strong")
        super().__init__()

    def render_children_if_not_str(self, element):
        if isinstance(element, str):
            return element
        elif isinstance(element.children, str):
            return element.children
        else:
            return self.render_children(element)

    def render_document(self, element):
        text = self.render_children_if_not_str(element)
        if text != "":
            dcg.Text(self.C, wrap=0, value=text)
        return ""

    def render_paragraph(self, element):
        print("render_paragraph", element)
        with dcg.VerticalLayout(self.C):
            text = self.render_children_if_not_str(element)
            if text != "":
                dcg.Text(self.C, wrap=0, value=text)
        dcg.Spacer(self.C)
        return ""

    def render_list(self, element):
        print("render_list", element)
        with dcg.VerticalLayout(self.C, indent=-1):
            self.render_children_if_not_str(element)
        return ""

    def render_list_item(self, element):
        print("render_list_item", element)
        with dcg.VerticalLayout(self.C):
            text = self.render_children_if_not_str(element)
            if text != "":
                dcg.Text(self.C, value=text)
        return ""

    def render_quote(self, element):
        print("render_quote", element)
        return make_italic(self.render_children_if_not_str(element))

    def render_fenced_code(self, element):
        print("render_fc", element)
        with dcg.VerticalLayout(self.C, indent=-1):
            text = self.render_children_if_not_str(element)#element.children[0].children
            lines = text.split("\n")
            for line in lines:
                if line == "":
                    dcg.Spacer(self.C)
                else:
                    dcg.Text(self.C, wrap=0, value=make_bold(line))
        return ""

    def render_thematic_break(self, element):
        print("render_tb", element)
        with dcg.DrawInWindow(self.C, height=8, width=10000):
            dcg.DrawLine(self.C, p1 = (-100, 0), p2 = (10000, 0), color=(255, 255, 255))
        #dcg.Spacer(self.C)
        return ""

    def render_heading(self, element):
        print("render_heading", element)
        level = element.level
        font = self.huge_font if level > 1 else self.big_font
        with dcg.Layout(self.C, font=font):
            text = self.render_children_if_not_str(element)
            if text != "":
                dcg.Text(self.C, wrap=0, value=text)
        return ""

    def render_blank_line(self, element):
        print("render_blank_line", element)
        dcg.Spacer(self.C)
        return ""

    def render_emphasis(self, element) -> str:
        print("render_emphasis", element)
        return make_italic(self.render_children_if_not_str(element))

    def render_strong_emphasis(self, element) -> str:
        print("render_strong_emphasis", element)
        return make_bold_italic(self.render_children_if_not_str(element))

    def render_plain_text(self, element):
        print("render_plain", element)
        return self.render_children_if_not_str(element)

    def render_raw_text(self, element):
        print("render_raw", element)
        return " ".join(self.render_children_if_not_str(element).split("\n"))

    def render_image(self, element) -> str:
        print("TODO image: ", element) # TODO
        return ""

    def render_line_break(self, element):
        print("render_lb", element)
        if element.soft:
            return " "
        return "\n"

    def render_code_span(self, element) -> str:
        print("render_code_span", element)
        return make_bold(self.render_children_if_not_str(element))


class Callbacks(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(self, **kwargs)

        base_dir = os.path.dirname(__file__)
        doc_dir = os.path.join(base_dir, 'docs')
        with open(os.path.join(doc_dir, "callbacks.md"), 'r') as fp:
            text = fp.read()
        renderer = TextFormatter(C)
        parsed_text = marko.Markdown().parse(text)
        with self:
            renderer.render(parsed_text)

class Drawing(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(self, **kwargs)

        with self:
            """
            
            """

class UI(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(self, **kwargs)

        with self:
            """
            
            """

class Plot(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(self, **kwargs)

        with self:
            """
            
            """

class Themes(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(self, **kwargs)

        with self:
            """
            
            """

class DocumentationWindow(dcg.Window):
    def __init__(self, C, width=1000, height=600, label="Documentation", **kwargs):
        super().__init__(self, width=width, height=height, label=label, **kwargs)

        with self:
            radio_button = dcg.RadioButton(C)
            selection = {
                "Available items": AvailableItems(C, show=False),
                "Basics": Basics(C, show=False),
                "Callbacks": Callbacks(C, show=False),
                "Drawing": Drawing(C, show=False),
                "User-Interface": UI(C, show=False),
                "Plot": Plot(C, show=False),
                "Themes": Themes(C, show=False),
            }
            radio_button.items = selection.keys()
            def pick_selection(sender, target, value):
                # Unselect previous items:
                for item in selection.values():
                    item.show = False
                # Display selected item
                selection[value].show = True
            radio_button.value = "Available items"
            radio_button.callbacks = [pick_selection]
            radio_button.horizontal = True
            pick_selection(radio_button, radio_button, radio_button.value)
            
                


def launch_documentation():
    C = dcg.Context()
    # vsync: limit to screen refresh rate and have no tearing
    # wait_for_input: Do not refresh until a change is detected (C.viewport.wake() to help)
    C.viewport.initialize(vsync=True,
                          wait_for_input=True,
                          maximized=True,
                          title="DearCyGui documentation")
    # primary: use the whole window area
    DocumentationWindow(C, primary=True, width=0, height=0)

    while C.running:
        # can_skip_presenting: no GPU re-rendering on input that has no impact (such as mouse motion) 
        C.viewport.render_frame(can_skip_presenting=True)
        

if __name__ == '__main__':
    launch_documentation()