


import dearcygui as dcg
from dearcygui.font import make_bold, make_bold_italic, make_italic

from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound
from stransi import Ansi, SetAttribute, SetColor
from stransi.attribute import Attribute as AnsiAttribute
from stransi.color import ColorRole as AnsiColorRole

import marko
import os
import time
import imageio

##### Set of utilities that will probably one day
##### end up in dearcygui.utils


def blinking_callback(sender, item):
    t = int(time.time())
    text_color = item.theme.children[0].Text
    c = dcg.color_as_floats(text_color)
    # Alternate between transparent and full
    if t % 2 == 0:
        c = (c[0], c[1], c[2], 0)
    else:
        c = (c[0], c[1], c[2], 1.)
    item.theme.children[0].Text = c
    item.context.viewport.wake()

class TextAnsi(dcg.HorizontalLayout):
    """
    Similar to dcg.Text, but has a limited support
    for ANSI escape sequences.
    Unlike dcg.Text, newlines are not supported.
    """
    def __init__(self, context, wrap=0, **kwargs):
        self.textline = ""
        self._bullet = False
        self.theme = dcg.ThemeStyleImGui(self.context, item_spacing=(0, 0))
        super().__init__(context, width=wrap, **kwargs)

    def render_text(self):
        self.children = [] # detach any previous text
        color = (255, 255, 255, 255) # Start with white
        bold = False
        italic = False
        background_color = None
        blinking = False
        underline = False # TODO
        strikethrough = False # TODO
        with self:
            if self._bullet:
                dcg.Text(self.context, bullet=True, value="")
            for instr in Ansi(self.textline).instructions():
                if isinstance(instr, SetAttribute):
                    if instr.attribute == AnsiAttribute.NORMAL:
                        bold = False
                        italic = False
                        background_color = None
                        blinking = False
                        underline = False
                        strikethrough = False
                    elif instr.attribute == AnsiAttribute.BOLD:
                        bold = True
                    elif instr.attribute == AnsiAttribute.ITALIC:
                        italic = True
                    elif instr.attribute == AnsiAttribute.UNDERLINE:
                        underline = True
                    elif instr.attribute == AnsiAttribute.BLINK:
                        blinking = True
                    elif instr.attribute == AnsiAttribute.NEITHER_BOLD_NOR_DIM:
                        bold = False
                    elif instr.attribute == AnsiAttribute.NOT_ITALIC:
                        italic = False
                    elif instr.attribute == AnsiAttribute.NOT_UNDERLINE:
                        underline = False
                    elif instr.attribute == AnsiAttribute.NOT_BLINK:
                        blinking = False
                    else:
                        raise RuntimeWarning("Unparsed Ansi: ", instr)
                elif isinstance(instr, SetColor):
                    if instr.role == AnsiColorRole.BACKGROUND:
                        if instr.color is None:
                            background_color = None
                        else:
                            background_color = instr.color.rgb
                            background_color = (background_color.red, background_color.green, background_color.blue)
                        continue
                    if instr.color is None:
                        # reset color
                        color = (255, 255, 255, 255)
                        continue
                    color = instr.color.rgb
                    color = (color.red, color.green, color.blue)
                elif isinstance(instr, str):
                    text = instr
                    if bold and italic:
                        text = make_bold_italic(text)
                    elif italic:
                        text = make_italic(text)
                    elif bold:
                        text = make_bold(text)
                    words = text.split(" ")
                    if background_color is None and not(blinking):
                        # add a space at the end of each words,
                        # except the last one.
                        words = [w + " " for w in words[:-1]] + words[-1:]
                        for word in words:
                            dcg.Text(self.context, value=word, color=color)
                    else:
                        current_theme = dcg.ThemeList(self.context)
                        current_theme_style = dcg.ThemeStyleImGui(self.context,
                                                  item_spacing=(0, 0),
                                                  frame_borderSize=0,
                                                  frame_padding=(0, 0),
                                                  frame_rounding=0,
                                                  item_inner_spacing=(0, 0))
                        current_theme_color = dcg.ThemeColorImGui(self.context)
                        current_theme.children = [current_theme_color, current_theme_style]
                        bg_color = background_color if background_color is not None else (0, 0, 0, 0)
                        current_theme_color.button = bg_color
                        current_theme_color.button_hovered = bg_color
                        current_theme_color.button_active = bg_color
                        current_theme_color.text = color
                        words = [w + " " for w in words[:-1]] + words[-1:]
                        # Wrapping the text within a button window.
                        for word in words:
                            dcg.Button(self.context,
                                       label=word,
                                       small=True,
                                       theme=current_theme,
                                       handlers=dcg.RenderHandler(self.context, callback=blinking_callback) if blinking else [])

                else:
                    raise RuntimeWarning("Unparsed Ansi: ", instr)

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

def make_bg_color(text : str, color : str | list = "white"):
    """
    Add ANSI escape codes to add a colored background to text
    using TextAnsi.
    text: the text string to color
    color: the color name or color code
        Supported names are black, red, green, yellow, blue,
        magenta, cyan and white
        Else a color in any dcg color format is supported.
    """
    escape = "\u001b"
    if isinstance(color, str):
        transformed = f"{escape}[{str(int(color_to_ansi[color])+10)}m{text}{escape}[49m"
    else:
        color = dcg.color_as_ints(color)
        (r, g, b, _) = color
        transformed = f"{escape}[48;2;{r};{g};{b}m{text}{escape}[49m"
    return transformed

def make_blinking(text : str):
    """
    Add ANSI escape codes to make a text blinking
    using TextAnsi.
    text: the text string to blink
    """
    escape = "\u001b"
    transformed = f"{escape}[5m{text}{escape}[25m"
    return transformed

class MarkDownText(dcg.Layout, marko.Renderer):
    """
    Text displayed in DearCyGui using Marko to render

    Will use the viewport font or the font passed in the 
    initialization arguments.
    """
    def __init__(self, C : dcg.Context, wrap : int = 0, **kwargs):
        """
        C: the context
        wrap: Text() wrap attribute. 0 means
            wrap at the end of the window. > 0 means
            a specified size.
        """
        self.C = C

        self.font = kwargs.pop("font", self.context.viewport.font)
        if isinstance(self.font, dcg.AutoFont):
            # We will cheat by using the AutoFont feature
            # to build various scales for us.
            # This enables to avoid duplicating fonts if we
            # have several MarkDownText instances.
            self.huge_font_scale = 2.
            self.big_font_scale = 1.5
            self.use_auto_scale = True
        else:
            self.huge_font = dcg.AutoFont(C, 34)
            self.big_font = dcg.AutoFont(C, 25)
            self.use_auto_scale = False
        self.default_font = C.viewport.font
        self.wrap = wrap
        self.no_spacing = dcg.ThemeStyleImGui(C, frame_padding=(0,0), frame_border_size=0, item_spacing=(0, 0))
        self._text = None
        marko.Renderer.__init__(self)
        dcg.Layout.__init__(self, C, **kwargs)

    @property
    def value(self):
        """Content text"""
        return self._text

    @value.setter
    def value(self, text):
        if not(isinstance(text, str)):
            raise ValueError("Expected a string as text")
        self._text = text
        parsed_text = marko.Markdown().parse(text)
        with self:
            self.render(parsed_text)

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
        with dcg.VerticalLayout(self.C, x="parent.x1 + theme.item_spacing.x"):
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
        with dcg.ChildWindow(self.C, auto_resize_y=True):
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
            lexer = None

        formatter = Terminal256Formatter(bg='dark', style='monokai')
        text = code if lexer is None else highlight(code, lexer, formatter)
        with dcg.ChildWindow(self.C, x="parent.x1 + theme.item_spacing.x", auto_resize_y=True, theme=self.no_spacing):
            lines = text.split("\n")
            for line in lines:
                if line == "":
                    dcg.Spacer(self.C)
                    continue
                TextAnsi(self.C, value=line, no_wrap=True)
        return ""

    def render_thematic_break(self, element):
        #with dcg.DrawInWindow(self.C, height=8, width=10000): # TODO: fix height=1 not working
        #    dcg.DrawLine(self.C, p1 = (-100, 0), p2 = (10000, 0), color=(255, 255, 255))
        #dcg.Spacer(self.C)
        dcg.Separator(self.C)
        return ""

    def render_heading(self, element):
        level = element.level
        if self.use_auto_scale:
            # Cheat by applying a global scale only on the AutoFont attached
            scaling = self.huge_font_scale if level <= 1 else self.big_font_scale
            with dcg.Layout(self.C, font=self.default_font, scaling_factor=scaling):
                with dcg.Layout(self.C, scaling_factor=1./scaling):
                    text = self.render_children_if_not_str(element)
                    if text != "":
                        TextAnsi(self.C, wrap=self.wrap, value=text)
        else:
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
        with dcg.ChildWindow(self.context, auto_resize_x=True, auto_resize_y=True):
            image_path = element.dest
            if not(os.path.exists(image_path)):
                alternate_text = self.render_children_if_not_str(element)
                dcg.Text(self.context, alternate_text)
            else:
                image_content = imageio.v3.imread(image_path)
                image_texture = dcg.Texture(self.context)
                image_texture.set_value(image_content)
                dcg.Image(self.context, texture=image_texture)
            if element.title:
                with dcg.HorizontalLayout(self.context, alignment_mode=dcg.Alignment.CENTER):
                    dcg.Text(self.context, value=element.title)
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
