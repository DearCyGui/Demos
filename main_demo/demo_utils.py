import ast
from collections import OrderedDict
import colorsys
import dearcygui as dcg
import functools
import inspect
import re
import traceback
import textwrap
import numpy as np

from text_utils import MarkDownText

def democode(f):
    """
    Decorator that wraps a function in a DemoSection.
    Can be combined with @documented as:
    
    @documented
    @demo
    def my_demo_function(C: dcg.Context):
        # Demo code here
    """
    @functools.wraps(f)
    def wrapper(context):
        # Create a DemoSection with the original function
        with DemoSection(context, f):
            pass
    return wrapper


class DemoSection(dcg.Layout):
    """
    A layout component that displays a function's output and allows viewing/editing its source code.
    
    Features:
    - Displays the result of running a function
    - "Show Source" toggle displays the function's source code
    - Code can be edited and re-run to update the display
    - Changes are executed in the original function's context
    """
    
    def __init__(self, context: dcg.Context, function, **kwargs):
        super().__init__(context, **kwargs)
        
        # Store function references
        self.original_function = function
        self.source_function = inspect.unwrap(function)
        self.current_function = function
        self.func_name = function.__name__
        self.globals = function.__globals__
        
        # Set up UI components
        self._create_ui()
        self._run_function()
    
    def _create_ui(self):
        """Create all UI components for the demo section."""
        # Header with show source checkbox
        with dcg.HorizontalLayout(self.context, parent=self, alignment_mode=dcg.Alignment.RIGHT):
            self.show_source_checkbox = dcg.Checkbox(self.context, label="Show Source")
            self.show_source_checkbox.callbacks = self._toggle_source_view
        
        # Create source editor (initially hidden)
        self._create_source_editor()
        
        # Create content container for function output
        self.content_container = dcg.ChildWindow(self.context, parent=self, 
                                               width=-1e-3, 
                                               auto_resize_y=True,
                                               no_scrollbar=True)
    
    def _extract_function_code(self, func):
        """Extract the clean function definition and body without indentation or docstrings."""
        try:
            # Get source code
            source = inspect.getsource(func)
            source_lines = source.splitlines()
            
            # Find function definition line
            func_def_index = next((i for i, line in enumerate(source_lines) 
                                 if line.strip().startswith('def ')), 0)
            
            func_def_line = source_lines[func_def_index]
            original_indent = len(func_def_line) - len(func_def_line.lstrip())
            clean_func_def = func_def_line.lstrip()
            
            # Extract body and remove docstrings
            body_lines = source_lines[func_def_index + 1:]
            if not body_lines:
                return clean_func_def, ""
                
            # Find initial indentation level
            indent_level = next((len(line) - len(line.lstrip()) 
                              for line in body_lines if line.strip()), 4)
            
            # Check if first non-empty line starts a docstring
            first_non_empty = next((line.strip() for line in body_lines if line.strip()), "")
            if first_non_empty.startswith('"""') or first_non_empty.startswith("'''"):
                # Determine quote type
                quote_type = '"""' if first_non_empty.startswith('"""') else "'''"
                
                # Find the end of the docstring
                docstring_end = -1
                
                # Check if docstring ends on same line
                if first_non_empty.endswith(quote_type) and len(first_non_empty) > 3:
                    # Single-line docstring
                    docstring_end = next((i for i, line in enumerate(body_lines) 
                                    if line.strip() == first_non_empty), 0)
                else:
                    # Multi-line docstring - find the end quote
                    for i, line in enumerate(body_lines):
                        if i > 0 and quote_type in line:
                            docstring_end = i
                            break
                
                if docstring_end != -1:
                    # Skip all docstring lines including the closing quotes
                    body_lines = body_lines[docstring_end + 1:]
                
            # Remove indentation
            cleaned_body = "\n".join(
                line[indent_level:] if line.strip() else line 
                for line in body_lines
            )
            
            return clean_func_def, cleaned_body
            
        except Exception as e:
            return f"def {self.func_name}(context):", "# Could not retrieve source code\npass"
    
    def _create_source_editor(self):
        """Create the source code editor area."""
        # Get function code
        self.clean_func_def, body_source = self._extract_function_code(self.source_function)
        
        # Create source container (hidden by default)
        self.source_container = dcg.ChildWindow(self.context, parent=self, 
                                               show=False, height=300, width=-1e-3)
        
        with self.source_container:
            # Use monospace font if available
            font = self.globals.get('mono_font', None)
            
            # Add code editor with function body
            self.code_editor = dcg.InputText(self.context, 
                                            value=body_source,
                                            max_characters=len(body_source) * 2,
                                            multiline=True, 
                                            tab_input=True,
                                            font=font,
                                            width=-1e-3, 
                                            height=-30)
            
            # Add control buttons
            with dcg.HorizontalLayout(self.context, alignment_mode=dcg.Alignment.RIGHT):
                dcg.Button(self.context, label="Reset", callbacks=self._reset_code)
                dcg.Button(self.context, label="Run", callbacks=self._run_edited_code)
    
    def _toggle_source_view(self):
        """Show or hide the source code editor."""
        self.source_container.show = self.show_source_checkbox.value
    
    def _reset_code(self):
        """Reset the code to the original function."""
        try:
            _, body_source = self._extract_function_code(self.original_function)
            self.code_editor.value = body_source
            self.current_function = self.original_function
            self._run_function()
        except Exception as e:
            self._show_error(f"Error resetting code: {str(e)}")
    
    def _run_function(self):
        """Run the current function and display its output."""
        # Clear existing content
        self.content_container.children = []
        
        # Run the function with content_container as parent
        with self.content_container:
            try:
                self.current_function(self.context)
            except Exception as e:
                self._show_error(f"Error executing function: {str(e)}\n{traceback.format_exc()}")
    
    def _run_edited_code(self):
        """Execute the edited code and update the display."""
        body_code = self.code_editor.value
        
        try:
            # Construct complete function code
            complete_code = self.clean_func_def + "\n" + textwrap.indent(body_code, "    ")
            
            # Create namespace with the original function's globals
            namespace = {**self.globals, 'dcg': dcg}
            
            # Execute the code to define the updated function
            exec(complete_code, namespace)
            
            # Extract function name from definition
            func_name = re.search(r'def\s+(\w+)', self.clean_func_def).group(1)
            
            if func_name in namespace:
                self.current_function = namespace[func_name]
                self._run_function()
            else:
                self._show_error(f"Function '{func_name}' not found after execution")
                
        except Exception as e:
            self._show_error(f"Error in code: {str(e)}\n{traceback.format_exc()}")
    
    def _show_error(self, message):
        """Display an error message in the content container."""
        self.content_container.children = []
        with self.content_container:
            dcg.Text(self.context, value=message, color=(255, 0, 0))


def documented(f):
    """
    Decorator that adds the docstring
    of a function as markdown text before
    running the function
    """
    @functools.wraps(f)
    def wrapper(context):
        # Get the docstring of the function
        docstring = inspect.getdoc(f)
        if docstring:
            # Display the docstring as markdown text
            MarkDownText(context, value=docstring)
        # Run the function
        f(context)
    return wrapper

# Section hierarchy tracking
_demo_sections = OrderedDict()  # The full hierarchy of sections
_current_path = []  # The current path in the hierarchy

def push_group(name):
    """
    Start a new group of sections.
    
    Args:
        name: The name of the group to create
    """
    _current_path.append(name)
    
    # Ensure the path exists in our hierarchy
    current = _demo_sections
    for part in _current_path[:-1]:
        if part not in current:
            current[part] = OrderedDict()
        current = current[part]
    
    # Add the new group
    if _current_path[-1] not in current:
        current[_current_path[-1]] = OrderedDict()

def pop_group():
    """
    End the current group of sections.
    """
    if _current_path:
        _current_path.pop()

def demosection(func):
    """
    Mark a function as a section in the demo.
    The function will be added to the current group.
    """
    # Get the function name as title
    title = func.__name__
    
    # Add to the current path in our hierarchy
    current = _demo_sections
    for part in _current_path:
        if part not in current:
            current[part] = OrderedDict()
        current = current[part]
    
    # Store the function
    current[title] = func
    
    return func

class DemoContentContainer(dcg.ChildWindow):
    """
    A container specifically designed to hold demo content (documentation text or code).
    This container can be styled with different background colors and layout properties.
    """
    
    def __init__(self, context, content_type="doc", **kwargs):
        """
        Initialize a demo content container.
        
        Args:
            context: DearCyGui context
            content_type: Type of content ('doc' for documentation, 'code' for code)
            **kwargs: Additional arguments passed to dcg.ChildWindow
        """
        self.content_type = content_type
        self.no_scrollbar = True
        self.auto_resize_y = True
        self.border = False
        self.width = -1e-3
        
        # Apply any custom styling from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
            
        super().__init__(context, **kwargs)

    def set_background_color(self, color):
        """Set the background color of the container."""
        self.theme = \
            dcg.ThemeColorImGui(
                self.context,
                ChildBg=color
            )

class DemoWindow(dcg.Window):
    """
    A customizable window for displaying demonstrations with various layout options.
    
    Features:
    - Fills the entire viewport (primary window)
    - Provides controls for visual parameters
    - Supports multiple layout modes for displaying demo sections
    - Can use tabs or collapsing headers for section navigation
    - Optional background colors for text and code sections
    """
    
    class Layout:
        """Layout options for demo content display"""
        SINGLE = "single"  # Text above, code below
        TWO_COL_TEXT_LEFT = "two_col_text_left"  # Text left, code right
        TWO_COL_CODE_LEFT = "two_col_code_left"  # Code left, text right
    
    def __init__(self, context, title="Demo", **kwargs):
        # Set default properties
        self.width = -1e-3  # Fill available width
        self.height = -1e-3  # Fill available height
        
        # Default settings
        self._layout_mode = self.Layout.SINGLE
        self._use_colored_backgrounds = False
        self._use_tabs = True  # True for tabs, False for collapsing headers
        
        # Initialize colors for backgrounds
        self._doc_bg_color = (60, 70, 80, 25)  # Semi-transparent dark blue
        self._code_bg_color = (80, 60, 60, 25)  # Semi-transparent dark red
        
        super().__init__(context, label=title, primary=True, **kwargs)
        
        # Create the main controls bar
        self._setup_controls()
        
        # Create main tab bar
        self.main_tab_bar = dcg.TabBar(context, parent=self)

        # Build the tree
        self._text_sections, self._code_sections = self._build_item_tree(_demo_sections)

        # Create tabs from our hierarchy
        with self.main_tab_bar:
            self._create_tabs_from_hierarchy(
                self._text_sections,
                self._code_sections
            )
    
    def _setup_controls(self):
        """Set up the controls bar for visual parameters"""
        with dcg.MenuBar(self.context, parent=self):
            # These will be implemented later
            pass

    def _build_item_tree(self, section_tree: OrderedDict):
        """Run the demo sections and put them in containers"""
        text_dict = OrderedDict()
        code_dict = OrderedDict()

        for key, value in section_tree.items():
            if isinstance(value, OrderedDict):
                # Recursively build the tree
                text_dict[key], code_dict[key] = self._build_item_tree(value)
            elif callable(value):
                placeholder = dcg.Layout(self.context)
                with placeholder:
                    value(self.context)
                items = placeholder.children
                if len(items) == 0:
                    return
                text = None
                if isinstance(items[0], MarkDownText):
                    text = items[0]
                    code = items[1:]
                else:
                    code = items
                if text is not None:
                    container = DemoContentContainer(self.context, content_type="doc")
                    container.set_background_color(self._doc_bg_color)
                    text.parent = container
                    text_dict[key] = container
                else:
                    text_dict[key] = None
                if code is not None:
                    container = DemoContentContainer(self.context, content_type="code")
                    container.set_background_color(self._code_bg_color)
                    for element in code:
                        element.parent = container
                    code_dict[key] = container
                else:
                    code_dict[key] = None
            else:
                raise ValueError(f"Invalid section type: {type(value)}")

        return text_dict, code_dict
            
    @property
    def layout_mode(self):
        """Get the current layout mode"""
        return self._layout_mode
    
    @layout_mode.setter
    def layout_mode(self, value):
        """Set the layout mode and refresh the display"""
        if value in [self.Layout.SINGLE, self.Layout.TWO_COL_TEXT_LEFT, self.Layout.TWO_COL_CODE_LEFT]:
            self._layout_mode = value
            # Will need to refresh the display here
            
    @property
    def use_colored_backgrounds(self):
        """Get whether colored backgrounds are enabled"""
        return self._use_colored_backgrounds
    
    @use_colored_backgrounds.setter
    def use_colored_backgrounds(self, value):
        """Set whether to use colored backgrounds"""
        self._use_colored_backgrounds = bool(value)
        # Will need to refresh the display here
            
    @property
    def use_tabs(self):
        """Get whether tabs are used for section navigation"""
        return self._use_tabs
    
    @use_tabs.setter
    def use_tabs(self, value):
        """Set whether to use tabs for section navigation"""
        self._use_tabs = bool(value)
        # Will need to refresh the display here
    
    def generate_random_bg_color(self):
        """Generate a random semi-transparent background color"""
        hue = np.random.random()  # Random hue
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.3, 0.7)]  # Low saturation, moderate value
        return (r, g, b, 25)  # 25 alpha for semi-transparency
    
    def setup_layout(self):
        """
        Configure the layout based on the current settings.
        This will be implemented in a future update.
        """
        pass

    def _create_tabs_from_hierarchy(self,
                                    _text_sections: OrderedDict,
                                    _code_sections: OrderedDict,
                                    level: int = 0):
        """
        Recursively create tabs from the hierarchy.
        """
        for group_name in _text_sections.keys():
            if group_name.startswith("_"):
                formatted_group_name = group_name[1:].split("_")
                formatted_group_name = " ".join(formatted_group_name).title()
            else:
                formatted_group_name = group_name
            with dcg.Tab(self.context, label=formatted_group_name):
                text_content = _text_sections[group_name]
                code_content = _code_sections[group_name]
                if isinstance(text_content, OrderedDict):
                    assert isinstance(code_content, OrderedDict)
                    with dcg.TabBar(self.context):
                        self._create_tabs_from_hierarchy(text_content, code_content, level + 1)
                else:
                    if text_content is not None:
                        text_content.parent = self.context.fetch_parent_queue_back()
                    if code_content is not None:
                        code_content.parent = self.context.fetch_parent_queue_back()


def launch_demo(title="DearCyGui Demo"):
    """
    Create a window displaying all the defined sections.
    """
    # Main function to run the demo
    context = dcg.Context()
    context.viewport.initialize(title=title, width=950, height=750, vsync=True)
    window = DemoWindow(context)
    
    while context.running:
        context.viewport.render_frame(can_skip_presenting=False)
    

