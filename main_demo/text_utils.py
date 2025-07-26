


import dearcygui as dcg
from dearcygui import make_bold, make_bold_italic, make_italic

import os

try:
    import imageio
except ImportError as e:
    raise ImportError("This module requires imageio to be installed. "
                      "Please install them using 'pip install imageio'") from e
import typing

##### Set of utilities that will probably one day
##### end up in dearcygui.utils


def import_md4c():
    """Import pymd4c if not already imported"""
    global md4c, BlockType, SpanType, TextType
    if 'md4c' in globals():
        return
    try:
        import md4c
        from md4c import BlockType, SpanType, TextType
    except ImportError as e:
        raise ImportError("This module requires pymd4c to be installed. "
                          "Please install it using 'pip install pymd4c'") from e

class MarkDownText_(dcg.Layout):
    """
    Text displayed in DearCyGui using pymd4c to render

    Will use the viewport font or the font passed in the 
    initialization arguments.
    """
    def __init__(self, C : dcg.Context, x=5, **kwargs):
        """
        C: the context
        """
        import_md4c()
        self.C = C

        self.font = kwargs.pop("font", C.viewport.font)
        # We will cheat by using the AutoFont feature
        # to build various scales for us.
        # This enables to avoid duplicating fonts if we
        # have several MarkDownText instances.
        self.huge_font_scale = 2.
        self.big_font_scale = 1.5
        self.no_spacing = dcg.ThemeStyleImGui(C,
                                              frame_padding=(0,0),
                                              frame_border_size=0,
                                              item_spacing=(0, 0))
        self._text = None

        # State for pymd4c parsing
        self._reset_state()

        dcg.Layout.__init__(self, C, x=x, **kwargs)
    
    def _reset_state(self):
        """Reset parsing state variables"""
        self._container_stack = []
        self._current_container = self
        self._text_buffer = []
        self._strikethrough = False
        self._underline = False
        self._text_processor : list[typing.Callable[[str], tuple[str, dcg.Color]]] = [self._process_text_normal]
        self._in_code_block = False
        self._code_buffer = []
        self._code_lang = None
        self._list_item_layout = None
        self._bullet_added = False
        self._list_enum = []
        self._list_is_enum = []
    
    @property
    def value(self):
        """Content text"""
        return self._text

    @value.setter
    def value(self, value):
        if not(isinstance(value, str)):
            raise ValueError("Expected a string as text")
        self._text = value
        
        # Clear children and reset state
        self.children = []
        self._reset_state()
        
        # Parse markdown using pymd4c
        with self:
            parser = md4c.GenericParser(
                collapse_whitespace=True,
                permissive_atx_headers=True,
                no_html_blocks=True,
                no_html_spans=True)
            parser.parse(
                value, 
                self._enter_block,
                self._leave_block,
                self._enter_span,
                self._leave_span,
                self._handle_text
            )
    
    def _push_container(self, container):
        """Helper to push a container onto the stack"""
        container.parent = self._current_container
        self._container_stack.append(self._current_container)
        self._current_container = container
    
    def _pop_container(self):
        """Helper to pop a container from the stack"""
        if len(self._current_container.children) == 0 and \
           self._current_container is not self:
            # If the current container is empty, remove it
            self._current_container.delete_item()
        if self._container_stack:
            self._current_container = self._container_stack.pop()
        else:
            self._current_container = self
    
    def _flush_text(self):
        """Render accumulated text with current styling"""
        if not self._text_buffer:
            return

        # Check for bullet in list items
        if self._list_item_layout is not None and not self._bullet_added:
            if not self._list_is_enum[-1]:
                dcg.Text(self.C, marker="bullet", no_newline=True, value="",
                         before=self._list_item_layout.children[0], theme=self.no_spacing)
            else:
                index = self._list_enum[-1]
                self._list_enum[-1] += 1
                dcg.Text(self.C, no_newline=True, value=f"- {index}. ",
                         before=self._list_item_layout.children[0], theme=self.no_spacing)
            self._bullet_added = True

        while len(self._text_buffer) > 0:
            with dcg.HorizontalLayout(self.C,
                                      parent=self._current_container,
                                      theme=self.no_spacing):
                for i, item in enumerate(self._text_buffer):
                    if item == "\n":
                        # Break line
                        self._text_buffer = self._text_buffer[i+1:]
                        break
                    (text, color) = item
                    # Remove trailing line breaks
                    text = text.rstrip("\n")

                    # Create a Text widget for each word
                    words = text.split(" ")
                    # add a space after each word except the last
                    # Note: could be done instead with appropriate itemspacing
                    words = [word + " " for word in words[:-1]] + [words[-1]]
                    for word in words:
                        dcg.Text(self.C, value=word,
                                 color=color)
                else:
                    # If we didn't break, clear the buffer
                    self._text_buffer = []

    def _enter_block(self, block_type, details):
        """Handle entering a block element"""
        if block_type == BlockType.DOC:
            # Document start - already in the main layout
            pass
            
        elif block_type == BlockType.P:
            # Paragraph
            vl = dcg.VerticalLayout(self.C)
            self._push_container(vl)
            
        elif block_type == BlockType.H:
            # Heading
            level = details.get('level', 1)
            # Cheat by applying a global scale and reapplying the font
            scaling = self.huge_font_scale if level <= 1 else self.big_font_scale
            outer = dcg.Layout(self.C, font=self.font, parent=self._current_container,
                               scaling_factor=scaling)
            self._push_container(outer)
            inner = dcg.VerticalLayout(self.C, scaling_factor=1./scaling)
            self._push_container(inner)
                
        elif block_type == BlockType.UL or block_type == BlockType.OL:
            # Lists
            vl = dcg.VerticalLayout(self.C,
                                    x="parent.x1 + theme.indent_spacing.x")
            self._push_container(vl)
            if block_type == BlockType.OL:
                # Ordered list
                self._list_is_enum.append(True)
                if 'start' in details:
                    self._list_enum.append(details['start'])
                else:
                    self._list_enum.append([1])
            else:
                self._list_is_enum.append(False)
            
        elif block_type == BlockType.LI:
            # List item
            outer = dcg.Layout(self.C)
            self._push_container(outer)
            inner = dcg.VerticalLayout(self.C)
            self._list_item_layout = outer
            self._bullet_added = False
            self._push_container(inner)
            
        elif block_type == BlockType.QUOTE:
            # Block quote
            window = dcg.ChildWindow(self.C,
                                     auto_resize_y=True)
            self._push_container(window)
            
        elif block_type == BlockType.CODE:
            # Code block
            self._in_code_block = True
            self._code_buffer = []
            
            # Get language if available
            if 'lang' in details and details['lang']:
                self._code_lang = ''.join(text for _, text in details['lang'])
            else:
                self._code_lang = None
            
            window = dcg.ChildWindow(
                self.C,
                x="parent.x1 + theme.indent_spacing.x", 
                auto_resize_y=True, 
                theme=self.no_spacing
            )
            self._push_container(window)
            
        elif block_type == BlockType.HR:
            # Horizontal rule
            dcg.Separator(self.C, parent=self._current_container)
    
    def _leave_block(self, block_type, details):
        """Handle leaving a block element"""
        if block_type == BlockType.DOC:
            # Document start - already in the main layout
            self._flush_text()
        elif block_type == BlockType.P:
            # End paragraph
            self._flush_text()
            self._pop_container()
            if len(self._list_is_enum) > 0:
                # loose list item, use a medium space.
                dcg.Spacer(self.C, parent=self._current_container, theme=self.no_spacing)
            else:
                # Jump a line after paragraphs
                dcg.Text(self.C, value=" ", parent=self._current_container, theme=self.no_spacing)
            
        elif block_type == BlockType.H:
            # End heading
            self._flush_text()
            self._pop_container()
            self._pop_container()
            level = details.get('level', 1)
            # Add a double spacer after main headings
            if level <= 1:
                dcg.Text(self.C, value=" \n ", parent=self._current_container, theme=self.no_spacing)
            else:
                # For subheadings, just a single spacer
                dcg.Text(self.C, value=" ", parent=self._current_container, theme=self.no_spacing)
            
        elif block_type == BlockType.UL or block_type == BlockType.OL:
            # End list
            self._pop_container()
            if self._list_is_enum[-1]: # should be block_type == BlockType.OL
                # If it was an ordered list, pop the enum stack
                self._list_enum.pop()
            self._list_is_enum.pop()
            dcg.Text(self.C, value=" ", parent=self._current_container, theme=self.no_spacing)
            
        elif block_type == BlockType.LI:
            # End list item
            self._flush_text()
            self._pop_container()
            self._pop_container()
            self._list_item_layout = None
            
        elif block_type == BlockType.QUOTE:
            # End quote
            self._flush_text()
            self._pop_container()
            
        elif block_type == BlockType.CODE:
            # End code block - render the code
            if self._code_buffer:
                code = "".join(self._code_buffer)
                text = code

                # Remove leading/trailing whitespace and newlines
                text = text.strip()

                # Render each line
                lines = text.split("\n")
                for line in lines:
                    if line == "":
                        dcg.Text(self.C, value=" ", parent=self._current_container, theme=self.no_spacing)
                        continue
                    dcg.Text(self.C, value=line, parent=self._current_container)
            
            self._in_code_block = False
            self._code_buffer = []
            self._code_lang = None
            self._pop_container()

    def _process_text_normal(self, text):
        return (text, 0)  # Normal text with no color

    def _process_text_emphasized(self, text):
        return (make_italic(text), (0, 255, 0))  # Italic text in green

    def _process_text_strong(self, text):
        return (make_bold_italic(text), (255, 0, 0))

    def _process_text_code(self, text):
        return (make_bold(text), (0, 255, 255))

    def _enter_span(self, span_type, details):
        """Handle entering a span/inline element"""
        if span_type == SpanType.EM:
            # Emphasis
            self._text_processor.append(self._process_text_emphasized)
            
        elif span_type == SpanType.STRONG:
            # Strong emphasis
            self._text_processor.append(self._process_text_strong)

        elif span_type == SpanType.A:
            # Link - store href for later use
            if 'href' in details:
                self._link_href = ''.join(text for _, text in details['href'])
            
        elif span_type == SpanType.CODE:
            # Inline code
            self._text_processor.append(self._process_text_code)
            self._code = True

        elif span_type == SpanType.DEL:
            # Strikethrough
            self._strikethrough = True
            
        elif span_type == SpanType.IMG:
            self._flush_text()
            # Image
            if 'src' in details:
                src = ''.join(text for _, text in details['src'])
                title = None
                if 'title' in details:
                    title = ''.join(text for _, text in details['title'])
                
                with dcg.ChildWindow(self.C, 
                                     parent=self._current_container,
                                     auto_resize_x=True, auto_resize_y=True):
                    if not(os.path.exists(src)):
                        # Will capture alt text in text handler
                        self._img_alt_pending = True
                    else:
                        image_content = imageio.v3.imread(src)
                        image_texture = dcg.Texture(self.C)
                        image_texture.set_value(image_content)
                        dcg.Image(self.C, texture=image_texture)
                    
                    if title:
                        with dcg.HorizontalLayout(self.C, alignment_mode=dcg.Alignment.CENTER):
                            dcg.Text(self.C, value=title)

        elif span_type == SpanType.U:
            # Underline
            self._underline = True

    def _leave_span(self, span_type, details):
        """Handle leaving a span/inline element"""
        if span_type == SpanType.EM:
            self._text_processor.pop()
            
        elif span_type == SpanType.STRONG:
            # End strong emphasis
            self._text_processor.pop()
            
        elif span_type == SpanType.A:
            # End link
            if hasattr(self, '_link_href'):
                delattr(self, '_link_href')

        elif span_type == SpanType.CODE:
            # End inline code
            self._text_processor.pop()

        elif span_type == SpanType.DEL:
            # End strikethrough
            self._strikethrough = False
            
        elif span_type == SpanType.IMG:
            # End image
            if hasattr(self, '_img_alt_pending'):
                delattr(self, '_img_alt_pending')

        elif span_type == SpanType.U:
            # End underline
            self._underline = False
    
    def _handle_text(self, text_type, text):
        """Handle text content"""
        if self._in_code_block:
            # Accumulate text for code blocks
            self._code_buffer.append(text)
            return
        
        if hasattr(self, '_img_alt_pending'):
            # Use text as image alt text
            dcg.Text(self.C, value=text)
            delattr(self, '_img_alt_pending')
            return
        
        if text_type == TextType.NORMAL:
            self._text_buffer.append(
                self._text_processor[-1](text)
            )

        elif text_type == TextType.BR:
            if len(self._text_buffer) == 0 or self._text_buffer[-1] != "\n":
                self._text_buffer.append("\n")
            
        elif text_type == TextType.SOFTBR:
            self._text_buffer.append((" ", 0))
            
        elif text_type == TextType.ENTITY:
            self._text_buffer.append((md4c.lookup_entity(text), 0))
            
        elif text_type == TextType.CODE:
            # Code text
            self._text_buffer.append(self._process_text_code(text))
            
        elif text_type == TextType.HTML:
            # Raw HTML
            self._text_buffer.append((text, 0))

        elif text_type == TextType.LATEXMATH:
            # LaTeX math
            self._text_buffer.append((text, 0))

try:
    MarkDownText = dcg.MarkDownText
except:
    MarkDownText = MarkDownText_
