import dearcygui as dcg
from dearcygui.fonts import make_bold, make_bold_italic, make_italic
import pydoc

from utils import create_new_font

from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound
from stransi import Ansi, SetAttribute, SetColor
from stransi.attribute import Attribute as AnsiAttribute
from stransi.color import ColorRole as AnsiColorRole

import marko
import os
import inspect

class TextAnsi(dcg.HorizontalLayout):
    """
    Similar to dcg.Text, but has a limited support
    for ainsi escape sequences.
    Similar to dcg.Text, newlines are not supported.
    """
    def __init__(self, context, wrap=0, **kwargs):
        self.textline = ""
        self._bullet = False
        self.theme = dcg.ThemeStyleImGui(self.context, ItemSpacing=(0, 0))
        super().__init__(context, width=wrap, **kwargs)

    def render_text(self):
        self.children = [] # detach any previous text
        color = (255, 255, 255, 255) # Start with white
        bold_on = False
        italic_on = False
        with self:
            if self._bullet:
                dcg.Text(self.context, bullet=True, value="")
            for instr in Ansi(self.textline).instructions():
                if isinstance(instr, SetAttribute):
                    if instr.attribute == AnsiAttribute.NORMAL:
                        bold_on = False
                        italic_on = False
                    elif instr.attribute == AnsiAttribute.BOLD:
                        bold_on = True
                    elif instr.attribute == AnsiAttribute.ITALIC:
                        italic_on = True
                    else:
                        print("Unparsed Ainsi: ", instr)
                elif isinstance(instr, SetColor):
                    if instr.role == AnsiColorRole.BACKGROUND:
                        print(instr)
                        continue
                    if instr.color is None:
                        # reset color
                        color = (255, 255, 255, 255)
                        continue
                    color = instr.color.rgb
                    color = (color.red, color.green, color.blue)
                elif isinstance(instr, str):
                    text = instr
                    if bold_on and italic_on:
                        text = make_bold_italic(text)
                    elif italic_on:
                        text = make_italic(text)
                    elif bold_on:
                        text = make_bold(text)
                    if self.no_wrap:
                        dcg.Text(self.context, value=text, color=color)
                    else:
                        words = text.split(" ")
                        # add the spaces a the end of words
                        words = [w + " " for w in words[:-1]] + words[-1:]
                        for word in words:
                            dcg.Text(self.context, value=word, color=color)
                else:
                    print("Unparsed Ainsi: ", instr)

    @property
    def bullet(self):
        return self._bullet

    @bullet.setter
    def bullet(self, value):
        self._bullet = value
        self.render_text()

    @property
    def value(self):
        return self.textline

    @value.setter
    def value(self, value):
        self.textline = value
        self.render_text()


color_to_ansi = {
    "black": "90",
    "red": "91",
    "green": "92",
    "yellow": "93",
    "blue": "94",
    "magenta": "95",
    "cyan": "96",
    "white": "97"
}

def make_color(text : str, color : str | list = "white"):
    """
    Add ANSI escape codes to a text to render in color
    using TextAnsi.
    text: the text string to color
    color: the color name or color code
        Supported names are black, red, green, yellow, blue,
        magenta, cyan and white
        Else a color in any dcg color format is supported.
    """
    escape = "\u001b"
    if isinstance(color, str):
        transformed = f"{escape}[{color_to_ansi[color]}m{text}{escape}[39m"
    else:
        color = dcg.color_as_ints(color)
        (r, g, b, _) = color
        transformed = f"{escape}[38;2;{r};{g};{b}m{text}{escape}[39m"
    return transformed

class TextFormatter(marko.Renderer):
    """
    A markdown renderer to use with marko
    """
    def __init__(self, C : dcg.Context, wrap : int = 0):
        """
        C: the context
        wrap: Text() wrap attribute. 0 means
            wrap at the end of the window. > 0 means
            a specified size.
        """
        self.C = C
        self.huge_font = create_new_font(C, 31)
        self.big_font = create_new_font(C, 25)
        self.default_font = C.viewport.font
        self.wrap = wrap
        self.no_spacing = dcg.ThemeStyleImGui(C, FramePadding=(0,0), FrameBorderSize=0, ItemSpacing=(0, 0))
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
            TextAnsi(self.C, wrap=self.wrap, value=text)
        return ""

    def render_paragraph(self, element):
        with dcg.VerticalLayout(self.C):
            text = self.render_children_if_not_str(element)
            if text != "":
                TextAnsi(self.C, wrap=self.wrap, value=text)
        dcg.Spacer(self.C)
        return ""

    def render_list(self, element):
        with dcg.VerticalLayout(self.C, indent=-1):
            self.render_children_if_not_str(element)
        return ""

    def render_list_item(self, element):
        with dcg.Layout(self.C, theme=self.no_spacing) as l:
            with dcg.VerticalLayout(self.C) as vl:
                text = self.render_children_if_not_str(element)
                if text != "":
                    TextAnsi(self.C, bullet=True, value="text")
                else:
                    # text rendered inside render_children_if_not_str
                    # insert the bullet
                    l.children = [TextAnsi(self.C, wrap=self.wrap, bullet=True, no_newline=True, value="", attach=False), vl]
        dcg.Spacer(self.C) # TODO: somehow the no_spacing theme affects the spacer !
        dcg.Spacer(self.C)
        dcg.Spacer(self.C)
        return ""

    def render_quote(self, element):
        with dcg.ChildWindow(self.C, width=0, height=0):
            text = self.render_children_if_not_str(element)
            if text != "":
                TextAnsi(self.C, bullet=True, value=make_italic(text))
        return ""

    def render_fenced_code(self, element):
        code = element.children[0].children
        if element.lang:
            try:
                lexer = get_lexer_by_name(element.lang, stripall=True, encoding='utf-8')
            except ClassNotFound:
                lexer = guess_lexer(code, encoding='utf-8')
        else:
            lexer = guess_lexer(code, encoding='utf-8')

        formatter = Terminal256Formatter(bg='dark', style='monokai')
        text = highlight(code, lexer, formatter)
        with dcg.ChildWindow(self.C, indent=-1, auto_resize_y=True, theme=self.no_spacing):
            lines = text.split("\n")
            for line in lines:
                if line == "":
                    dcg.Spacer(self.C)
                    continue
                TextAnsi(self.C, value=line, no_wrap=True)
        return ""

    def render_thematic_break(self, element):
        with dcg.DrawInWindow(self.C, height=8, width=10000): # TODO: fix height=1 not working
            dcg.DrawLine(self.C, p1 = (-100, 0), p2 = (10000, 0), color=(255, 255, 255))
        #dcg.Spacer(self.C)
        return ""

    def render_heading(self, element):
        level = element.level
        font = self.huge_font if level <= 1 else self.big_font
        with dcg.Layout(self.C, font=font):
            text = self.render_children_if_not_str(element)
            if text != "":
                TextAnsi(self.C, wrap=self.wrap, value=text)
        return ""

    def render_blank_line(self, element):
        dcg.Spacer(self.C)
        return ""

    def render_emphasis(self, element) -> str:
        return make_color(make_italic(self.render_children_if_not_str(element)), color="green")

    def render_strong_emphasis(self, element) -> str:
        return make_color(make_bold_italic(self.render_children_if_not_str(element)), color="red")

    def render_plain_text(self, element):
        return self.render_children_if_not_str(element)

    def render_raw_text(self, element):
        # Trim spaces after a "\n"
        text = self.render_children_if_not_str(element)
        subtexts = text.split('\n')
        new_subtexts = subtexts[0:1]
        for subtext in subtexts[1:]:
            i = 0
            while i < len(subtext) and text[i] == ' ':
                i = i + 1
            new_subtexts.append(subtext[i:]) 
        # convert newline into spaces
        return " ".join(new_subtexts)

    def render_image(self, element) -> str:
        print("TODO image: ", element) # TODO
        return ""

    def render_line_break(self, element):
        if element.soft:
            return " "
        return "\n"

    def render_code_span(self, element) -> str:
        text = make_bold(self.render_children_if_not_str(element))
        if True:#hasattr(dcg, text) or '_' in text:
            text = make_color(text, color="cyan")
        return text

class DocStringRenderer(pydoc.TextDoc):
    def __init__(self, context):
        self.context = context
        super().__init__()

    def bold(self, text):
        print(text)
        return make_color(make_bold(text), color="cyan")
    def indent(self, text, prefix='    '):
        if '|' in prefix and text[0] == ' ':
            return text
        return super().indent(text, prefix=prefix)

    def docdata(self, object, name=None, mod=None, cl=None, *ignored):
        results = []
        push = results.append

        if name:
            push(self.bold(name))
            push('\n')
        doc = pydoc.getdoc(object) or ''
        if doc:
            push("MARKDOWNSTART")
            push(doc)
            push("MARKDOWNSTOP")
            push('\n')
        return ''.join(results)

    docproperty = docdata


def display_docstring(C, object):
    """
    Retrieve the docstring of the target
    object and display the text in a box
    """
    docstring = pydoc.render_doc(object, renderer=DocStringRenderer(C))
    keyword = dir(dcg) + dir(object)
    markdown_starts = docstring.split("MARKDOWNSTART")
    in_markdown = False
    for markdown in markdown_starts:
        if not(in_markdown):
            assert(not("MARKDOWNSTOP" in markdown))
            lines_of_text = markdown.split("\n")
            for text in lines_of_text:
                TextAnsi(C, value=text)
            in_markdown = True
        else:
            markdown_end = markdown.split("MARKDOWNSTOP")
            assert(len(markdown_end) <= 2)
            parsed_text = marko.Markdown().parse(markdown_end[0])
            with dcg.Layout(C):
                renderer = TextFormatter(C)
                renderer.render(parsed_text)
            in_markdown = False
            if len(markdown_end) == 2:
                lines_of_text = markdown_end[1].split("\n")
                for text in lines_of_text:
                    TextAnsi(C, value=text)
            in_markdown = True




class TextWithDocstring(dcg.Text):
    def __init__(self, C, target, **kwargs):
        super().__init__(C, **kwargs)
        self.target = target
        self.value = target.__name__
        self.handlers = [
            dcg.GotHoverHandler(C, callback=self.display_tooltip)
        ]

    def display_tooltip(self):
        # Using a normal tooltip would have been fine,
        # but this is the occasion to show one use of
        # TemporaryTooltip
        docstring = getattr(self.target, '__doc__', None)
        if docstring is None:
            return
        window = self
        while window is not None and not(isinstance(window, dcg.Window)):
            window = window.parent

        # prerender else it appears not smooth
        # to have the tooltip render first empty
        parsed_text = marko.Markdown().parse(docstring)
        with dcg.Layout(self.context, attach=False) as temporary_layout:
            renderer = TextFormatter(self.context, wrap=1200)
            renderer.render(parsed_text)

        with dcg.utils.TemporaryTooltip(self.context, target=self, parent=window) as tt:
            for child in temporary_layout.children:
                child.parent = tt
            
        # Indicate we have updated content
        self.context.viewport.wake()

class InteractiveDocstring(dcg.ChildWindow):
    def __init__(self, C, object_class, **kwargs):
        super().__init__(C, **kwargs)

        class_attributes = [v[0] for v in inspect.getmembers_static(object_class)]
        instance = object_class(C, attach=False)
        attributes = dir(instance)
        dynamic_attributes = set(attributes).difference(set(class_attributes))
        disabled_properties = []
        read_only_properties = []
        writable_properties = []
        dynamic_properties = []
        methods = []
        for attr in sorted(attributes):
            if attr[:2] == "__":
                continue
            attr_inst = getattr(object_class, attr, None)
            if attr_inst is not None and inspect.isbuiltin(attr_inst):
                continue
            is_dynamic = attr in dynamic_attributes
            default_value = None
            is_accessible = False
            is_writable = False
            is_property = inspect.isdatadescriptor(attr_inst)
            is_class_method = inspect.ismethoddescriptor(attr_inst)
            try:
                default_value = getattr(instance, attr)
                is_accessible = True
                setattr(instance, attr, default_value)
                is_writable = True
            except AttributeError:
                pass
            except (TypeError, ValueError):
                is_writable = True
                pass
            if is_property:
                if is_writable:
                    writable_properties.append(attr)
                elif is_accessible:
                    read_only_properties.append(attr)
                else:
                    disabled_properties.append(attr)
            elif is_dynamic and is_accessible:
                dynamic_properties.append(attr)
            elif is_class_method:
                methods.append(attr)

        with self:
            if len(writable_properties) > 0:
                dcg.Text(C, value="Read-Write properties:")
                with dcg.HorizontalLayout(C, indent=-1, alignment_mode=dcg.Alignment.JUSTIFIED):
                    for attr in writable_properties:
                        TextWithDocstring(C, getattr(object_class, attr))
            if len(read_only_properties) > 0:
                dcg.Text(C, value="Read-only properties:")
                with dcg.HorizontalLayout(C, indent=-1):
                    for attr in read_only_properties:
                        TextWithDocstring(C, getattr(object_class, attr))
            if len(dynamic_properties) > 0:
                dcg.Text(C, value="Dynamic properties:")
                with dcg.HorizontalLayout(C, indent=-1):
                    for attr in dynamic_properties:
                        dcg.Text(C, value=attr)
            if len(methods) > 0:
                dcg.Text(C, value="Methods:")
                with dcg.HorizontalLayout(C, indent=-1):
                    for attr in methods:
                        TextWithDocstring(C, getattr(object_class, attr))


        

class AvailableItems(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(C, **kwargs)

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
                    object_class = getattr(dcg, item.label)
                    try:
                        InteractiveDocstring(C, object_class, width=0, auto_resize_y=True,
                                             theme=dcg.ThemeStyleImGui(C, FramePadding=(4,3), FrameBorderSize=1, ItemSpacing=(8, 4)))
                    except: # Shared*
                        pass
                    display_docstring(C, object_class)
                C.viewport.wake()
            update_item_list(filter, filter, filter.value)
            filter.callbacks = [update_item_list]

"""
class Basics(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(C, **kwargs)

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
"""


class Basics(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(C, **kwargs)

        base_dir = dcg.__path__[0]
        doc_dir = os.path.join(base_dir, 'docs')
        with open(os.path.join(doc_dir, "basics.md"), 'r') as fp:
            text = fp.read()
        renderer = TextFormatter(C)
        parsed_text = marko.Markdown().parse(text)
        with self:
            renderer.render(parsed_text)

class Callbacks(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(C, **kwargs)

        base_dir = dcg.__path__[0]
        doc_dir = os.path.join(base_dir, 'docs')
        with open(os.path.join(doc_dir, "callbacks.md"), 'r') as fp:
            text = fp.read()
        renderer = TextFormatter(C)
        parsed_text = marko.Markdown().parse(text)
        with self:
            renderer.render(parsed_text)

class Drawing(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(C, **kwargs)

        base_dir = dcg.__path__[0]
        doc_dir = os.path.join(base_dir, 'docs')
        with open(os.path.join(doc_dir, "drawings.md"), 'r') as fp:
            text = fp.read()
        renderer = TextFormatter(C)
        parsed_text = marko.Markdown().parse(text)
        with self:
            renderer.render(parsed_text)

class UI(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(C, **kwargs)

        base_dir = dcg.__path__[0]
        doc_dir = os.path.join(base_dir, 'docs')
        with open(os.path.join(doc_dir, "UI.md"), 'r') as fp:
            text = fp.read()
        renderer = TextFormatter(C)
        parsed_text = marko.Markdown().parse(text)
        with self:
            renderer.render(parsed_text)

class Plot(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(C, **kwargs)

        base_dir = dcg.__path__[0]
        doc_dir = os.path.join(base_dir, 'docs')
        with open(os.path.join(doc_dir, "plots.md"), 'r') as fp:
            text = fp.read()
        renderer = TextFormatter(C)
        parsed_text = marko.Markdown().parse(text)
        with self:
            renderer.render(parsed_text)

class Themes(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(C, **kwargs)

        base_dir = dcg.__path__[0]
        doc_dir = os.path.join(base_dir, 'docs')
        with open(os.path.join(doc_dir, "themes.md"), 'r') as fp:
            text = fp.read()
        renderer = TextFormatter(C)
        parsed_text = marko.Markdown().parse(text)
        with self:
            renderer.render(parsed_text)

class Advanced(dcg.Layout):
    def __init__(self, C, **kwargs):
        super().__init__(C, **kwargs)

        base_dir = dcg.__path__[0]
        doc_dir = os.path.join(base_dir, 'docs')
        with open(os.path.join(doc_dir, "advanced.md"), 'r') as fp:
            text = fp.read()
        renderer = TextFormatter(C)
        parsed_text = marko.Markdown().parse(text)
        with self:
            renderer.render(parsed_text)

class DocumentationWindow(dcg.Window):
    def __init__(self, C, width=1000, height=600, label="Documentation", **kwargs):
        super().__init__(C, width=width, height=height, label=label, **kwargs)

        with self:
            radio_button = dcg.RadioButton(C)
            selection = {
                "Available items": AvailableItems(C, show=False),
                "Basics": Basics(C, show=False),
                "Callbacks": Callbacks(C, show=False),
                "Drawings": Drawing(C, show=False),
                "User-Interfaces": UI(C, show=False),
                "Plots": Plot(C, show=False),
                "Themes": Themes(C, show=False),
                "Advanced": Advanced(C, show=False)
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
