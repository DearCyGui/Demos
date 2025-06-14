import asyncio
from collections import OrderedDict
import colorsys
import dearcygui as dcg
from dearcygui.utils.asyncio_helpers import AsyncPoolExecutor, AsyncThreadPoolExecutor, run_viewport_loop
import functools
import inspect
import psutil
import re
import traceback
import textwrap
import numpy as np

from text_utils import MarkDownText
from dataclasses import dataclass
from typing import Any, Optional, Dict

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
            self.show_source_checkbox.callback = self._toggle_source_view
        
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

def demosection(*doc_classes):
    """
    Mark a function as a section in the demo.
    The function will be added to the current group.
    
    Args:
        doc_classes: Optional list of classes to show documentation for in the menu bar
    """
    if len(doc_classes) == 1 and callable(doc_classes[0]) and not doc_classes[0].__name__[0].isupper():
        # Called without arguments as @demosection
        func = doc_classes[0]
        title = func.__name__
        
        # Add to the current path in our hierarchy
        current = _demo_sections
        for part in _current_path:
            if part not in current:
                current[part] = OrderedDict()
            current = current[part]
        
        # Store the function with no documented classes
        current[title] = (func, [])
        return func
    else:
        # Called with arguments as @demosection(...)
        def wrapper(func):
            title = func.__name__
            
            # Add to the current path in our hierarchy
            current = _demo_sections
            for part in _current_path:
                if part not in current:
                    current[part] = OrderedDict()
                current = current[part]
            
            # Store the function with its documented classes
            current[title] = (func, doc_classes or [])
            return func
        return wrapper

class DemoContentContainer(dcg.ChildWindow):
    """
    A container specifically designed to hold demo content (documentation text or code).
    This container can be styled with different background colors and layout properties.
    """
    
    def __init__(self, context, content_type="doc", doc_links=(), **kwargs):
        """
        Initialize a demo content container.
        
        Args:
            context: DearCyGui context
            content_type: Type of content ('doc' for documentation, 'code' for code)
            doc_links: documentation links
            **kwargs: Additional arguments passed to dcg.ChildWindow
        """
        self.content_type = content_type
        self.doc_links = doc_links
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
                child_bg=color
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
        self._setup_controls_and_status()
        
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
    
    def _setup_controls_and_status(self):
        """Set up the controls bar for visual parameters, etc"""
        C = self.context
        with dcg.MenuBar(C, parent=self) as bar:
            self.doc_bar = dcg.Layout(C) # This will hold the documentation links
            # status widgets
            with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.RIGHT, no_wrap=True):
                async def update_cpu_usage(target: dcg.ProgressBar):
                    process = psutil.Process()
                    while C.running:
                        # Update CPU usage
                        cpu_percent = process.cpu_percent()
                        target.value = cpu_percent / 100.
                        prev_overlay = target.overlay
                        target.overlay = f"{int(cpu_percent)}%"
                        if prev_overlay != target.overlay:
                            C.viewport.wake()
                        await asyncio.sleep(5.)  # Update every five seconds

                async def update_fps_usage(target: dcg.ProgressBar):
                    last_frame_count = C.viewport.metrics.frame_count
                    last_frame_time = C.viewport.metrics.last_time_after_swapping
                    while C.running:
                        # Update FPS
                        current_frame_count = C.viewport.metrics.frame_count
                        current_frame_time = C.viewport.metrics.last_time_after_swapping
                        fps = (current_frame_count - last_frame_count) / max(0.0001, (current_frame_time - last_frame_time))
                        target.value = min(fps / 120., 1.0)  # Normalize to 120fps max
                        target.overlay = f"{int(fps)}"
                        last_frame_count = current_frame_count
                        last_frame_time = current_frame_time
                        if current_frame_count <= last_frame_count + 5:
                            # Do not cause rendering when it is not needed
                            C.viewport.wake()
                        await asyncio.sleep(0.5)  # Update every half-second

                async def update_max_fps(target: dcg.ProgressBar):
                    last_frame_count = C.viewport.metrics.frame_count
                    while C.running:
                        acc_deltas = 0.
                        acc_count = 0
                        while acc_count < 30 and C.running:
                            current_frame_count = C.viewport.metrics.frame_count
                            if last_frame_count == current_frame_count:
                                # No new frames rendered, skip this iteration
                                await asyncio.sleep(0.05)
                                continue
                            last_frame_count = current_frame_count
                            metrics = C.viewport.metrics
                            current_start_frame_time = metrics.last_time_before_event_handling
                            current_end_frame_time = metrics.last_time_after_swapping
                            acc_deltas += current_end_frame_time - current_start_frame_time
                            acc_count += 1
                            await asyncio.sleep(0.05)  # Wait for a short time to get a good average
                        avg_delta = acc_deltas / max(1, acc_count)
                        max_fps = 1.0 / max(0.0001, avg_delta)
                        target.value = min(max_fps / 120., 1.0)  # Normalize to 120fps max
                        target.overlay = f"{int(max_fps)}"


                cpu_stat = dcg.ProgressBar(C, value=0.0, overlay="0%", width="0.05*bar.width")
                with dcg.Tooltip(C):
                    dcg.Text(C, value="CPU Usage")
                    dcg.Text(C, value="This shows the CPU usage of the current process.")
                dcg.Spacer(C, width="0.01*bar.width")
                fps_stat = dcg.ProgressBar(C, value=0.0, overlay="0", width="0.05*bar.width")
                with dcg.Tooltip(C):
                    dcg.Text(C, value="Actual FPS")
                    dcg.Text(C, value="This shows the current frames per second (FPS) of the viewport.")
                    dcg.Text(C, value="A small value indicates frame rendering was skipped to save CPU/GPU time,")
                    dcg.Text(C, value="or that other tasks are using a lot of CPU/GPU time.")
                dcg.Spacer(C, width="0.01*bar.width")
                max_fps_stat = dcg.ProgressBar(C, value=0.0, overlay="0", width="0.05*bar.width")
                with dcg.Tooltip(C):
                    dcg.Text(C, value="Max FPS")
                    dcg.Text(C, value="This shows the maximum frames per second (FPS) that can be achieved (window rendering only).")
                    dcg.Text(C, value="It is calculated based on the time taken to render recent frames.")
                    dcg.Text(C, value="It is higher than the actual FPS if the viewport is not rendering frames at full speed.")
                    dcg.Text(C, value="The value can appear lower temporarily if the CPU is an idle state.")
                C.queue.submit(update_cpu_usage, cpu_stat)
                C.queue.submit(update_fps_usage, fps_stat)
                C.queue.submit(update_max_fps, max_fps_stat)


    def _build_item_tree(self, section_tree: OrderedDict):
        """Run the demo sections and put them in containers"""
        text_dict = OrderedDict()
        code_dict = OrderedDict()

        for key, value in section_tree.items():
            if isinstance(value, OrderedDict):
                # Recursively build the tree
                text_dict[key], code_dict[key] = self._build_item_tree(value)
            elif isinstance(value, tuple) and len(value) == 2:
                # Unpack the function and doc_classes
                func, doc_classes = value
                placeholder = dcg.Layout(self.context)
                with placeholder:
                    func(self.context)
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
                    container = DemoContentContainer(self.context,
                                                     content_type="doc",
                                                     doc_links=doc_classes)
                    container.set_background_color(self._doc_bg_color)
                    text.parent = container
                    text_dict[key] = container
                else:
                    text_dict[key] = None
                if code is not None:
                    container = DemoContentContainer(self.context,
                                                     content_type="code",
                                                     doc_links=doc_classes if text is None else ())
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

    def _on_show_item(self, sender, target):
        if not target.value: # opened tab
            return
        self.doc_bar.children = []
        with self.doc_bar:
            # Get the text and code sections from the sender's user data
            text_section, code_section = target.user_data
            # Retrieve the documentation links to show
            doc_links = ()
            if text_section is not None and hasattr(text_section, "doc_links"):
                doc_links = text_section.doc_links
            if code_section is not None and hasattr(code_section, "doc_links"):
                doc_links += code_section.doc_links

            # Add them to the menu bar
            def _show_documentation(sender, target, value):
                # Show the documentation for the selected item
                ItemDocumentation(self.context, target.user_data, modal=True)
            for link in doc_links:
                dcg.Button(self.context, label=link.__name__, small=True,
                           callback=_show_documentation, user_data=link)
        self.context.viewport.wake() # Wake the viewport to refresh the display

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
            text_content = _text_sections[group_name]
            code_content = _code_sections[group_name]
            with dcg.Tab(self.context,
                         label=formatted_group_name,
                         user_data=(text_content, code_content)) as parent_tab:
                if isinstance(text_content, OrderedDict):
                    assert isinstance(code_content, OrderedDict)
                    with dcg.TabBar(self.context):
                        self._create_tabs_from_hierarchy(text_content, code_content, level + 1)
                else:
                    # When clicked
                    parent_tab.callbacks = [self._on_show_item]
                    # When switching from a parent tab to another (will trigger for all tabs)
                    parent_tab.handlers = [dcg.GotRenderHandler(self.context, callback=self._on_show_item)]
                    if text_content is not None:
                        text_content.parent = self.context.fetch_parent_queue_back()
                    if code_content is not None:
                        code_content.parent = self.context.fetch_parent_queue_back()

@dataclass
class PropertyInfo:
    """Information about a class property."""
    # The name of the property
    name: str
    
    # Documentation string describing the property
    docstring: str
    
    # Whether the property can be modified
    writable: bool
    
    # Whether the property can be accessed
    accessible: bool
    
    # Default value of the property when initialized
    default_value: Any

    # Whether this property is dynamic (implemented in getattr/setattr)
    dynamic: bool = False
    
    # Whether this property is inherited from a parent class
    inherited: bool = False
    
    # Name of the parent class this property is inherited from (if any)
    inherited_from: Optional[str] = None
    
    @property
    def readonly(self) -> bool:
        """Whether the property is read-only."""
        return self.accessible and not self.writable
    
    @property
    def disabled(self) -> bool:
        """Whether the property is disabled (not accessible)."""
        return not self.accessible

@dataclass
class MethodInfo:
    """Information about a class method."""
    # The name of the method
    name: str
    
    # Documentation string describing the method
    docstring: str | None
    
    # String representation of the method signature
    signature: str
    
    # Whether this method is inherited from a parent class
    inherited: bool = False
    
    # Name of the parent class this method is inherited from (if any)
    inherited_from: Optional[str] = None

class ItemParser:
    """
    Parses class docstrings and organizes class attributes for documentation purposes.
    
    This utility class extracts and processes documentation information from a class,
    including its properties, methods, and their docstrings, without implementing
    any visual components.
    """
    
    def __init__(self, C: dcg.Context, object_class):
        """
        Initialize the docstring parser for a given class.
        
        Args:
            object_class: The class to parse documentation from
        """
        self._context = C
        self._object_class = object_class
        self._class_name = object_class.__name__
        self._class_docstring = inspect.getdoc(object_class) or ""
        
        # Properties and methods collections
        self._property_dict: Dict[str, PropertyInfo] = {}
        self._method_dict: Dict[str, MethodInfo] = {}
        
        # Parse the class attributes and properties
        self._parse_class_attributes()
    
    @property
    def docstring(self) -> str:
        """The documentation string of the class."""
        return self._class_docstring
    
    @property
    def parent(self):
        """The class being documented."""
        return self._object_class
    
    @property
    def properties(self) -> list[PropertyInfo]:
        """List of all properties in the class."""
        return list(self._property_dict.values())
    
    @property
    def methods(self) -> list[MethodInfo]:
        """List of all methods in the class."""
        return list(self._method_dict.values())
    
    def _parse_class_attributes(self):
        """Parse all attributes and organize them by type."""
        if not isinstance(self._object_class, type):
            return
        # Get class attributes (static)
        class_attributes = [v[0] for v in inspect.getmembers_static(self._object_class)]
        
        # Get base classes (for inheritance tracking)
        base_classes = self._object_class.__mro__[1:]  # Skip self
        
        # Create a temporary instance to inspect dynamic attributes
        try:
            instance = self._object_class(self._context, attach=False)
            attributes = dir(instance)
            dynamic_attributes = set(attributes).difference(set(class_attributes))
        except:
            # If we can't create an instance, fallback to class attributes
            instance = None
            attributes = dir(self._object_class)
            dynamic_attributes = set()
        
        # Process each attribute
        for attr in sorted(attributes):
            if attr.startswith("__"):  # Skip dunder methods
                continue
                
            attr_inst = getattr(self._object_class, attr, None)
            if attr_inst is not None and inspect.isbuiltin(attr_inst):
                continue
                
            is_dynamic = attr in dynamic_attributes
            is_property = inspect.isdatadescriptor(attr_inst)
            is_class_method = inspect.ismethoddescriptor(attr_inst)
            
            # Check inheritance
            inherited = False
            inherited_from = None
            for base in base_classes:
                if hasattr(base, attr):
                    base_attr = getattr(base, attr, None)
                    if base_attr is attr_inst:
                        inherited = True
                        inherited_from = base.__name__
                        break
            
            # Store docstring if available
            doc = inspect.getdoc(attr_inst) if attr_inst else None
            
            # Check if property is accessible/writable
            default_value = None
            is_accessible = False
            is_writable = False
            
            try:
                if hasattr(instance, attr):
                    default_value = getattr(instance, attr)
                    is_accessible = True
                    setattr(instance, attr, default_value)
                    is_writable = True
            except AttributeError:
                pass
            except (TypeError, ValueError, OverflowError):
                is_writable = True
                pass
            
            # Categorize the attribute
            if is_property or (is_dynamic and is_accessible):
                # Create PropertyInfo object
                prop_info = PropertyInfo(
                    name=attr,
                    docstring=doc,
                    writable=is_writable,
                    accessible=is_accessible,
                    default_value=default_value,
                    dynamic=is_dynamic,
                    inherited=inherited,
                    inherited_from=inherited_from
                )
                
                # Store and categorize
                self._property_dict[attr] = prop_info
                    
            elif is_class_method:
                # Get method signature
                try:
                    signature = str(inspect.signature(attr_inst))
                except (ValueError, TypeError):
                    signature = "()"
                
                # Create MethodInfo object
                method_info = MethodInfo(
                    name=attr,
                    docstring=doc or "",
                    signature=signature,
                    inherited=inherited,
                    inherited_from=inherited_from
                )
                
                # Store method
                self._method_dict[attr] = method_info

class PropertyDocNode(dcg.TreeNode):
    """
    A button about a property. When clicked, it opens a documentation window
    for the property.
    """
    def __init__(self, context, property_info: PropertyInfo, **kwargs):
        """
        Initialize the button with the property information.
        
        Args:
            context: DearCyGui context
            property_info: The property information to document
            **kwargs: Additional arguments passed to dcg.Button
        """
        super().__init__(context, label=property_info.name, **kwargs)
        self.property_info = property_info
        docstring = self.property_info.docstring
        
        with self:
            if docstring is not None:
                MarkDownText(self.context, value=docstring.strip())

class MethodDocNode(dcg.TreeNode):
    """
    A button about a method. When clicked, it opens a documentation window
    for the method.
    """
    def __init__(self, context, method_info: MethodInfo, **kwargs):
        """
        Initialize the button with the method information.
        
        Args:
            context: DearCyGui context
            method_info: The method information to document
            **kwargs: Additional arguments passed to dcg.Button
        """
        super().__init__(context, label=method_info.name, **kwargs)
        self.method_info = method_info
        docstring = self.method_info.docstring
        
        with self:
            if docstring is not None:
                MarkDownText(self.context, value=docstring.strip())
            # Add method signature
            signature = f"Signature: {self.method_info.signature}"
            MarkDownText(self.context, value=signature)


def display_item_documentation(context: dcg.Context, item_class, show_inherited=False):
    """
    Display the documentation for the given item class inside the
    current container.
    """
    #current_parent = context.fetch_parent_queue_back()
    #cache = getattr(display_item_documentation, "_cache", {})
    #if item_class in cache:
    #    # If we have already displayed this class, reuse the cached content
    #    items = [item.copy() for item in cache[item_class]] -> doesn't work yet completly
    #    for item in items:
    #        item.parent = current_parent
    #    return
    #prev_children = current_parent.children

    # Display docstring, class inheritance, properties, methods as a treenode
    item_info = ItemParser(context, item_class)
    docstring = item_info.docstring
    if docstring:
        with dcg.TreeNode(context, label="Class Docstring"):
            MarkDownText(context, value=docstring)

    # Display non-inherited properties
    if len([p for p in item_info.properties if not p.inherited or show_inherited]) > 0:
        with dcg.TreeNode(context, label="Properties"):
            for prop in item_info.properties:
                if not prop.inherited or show_inherited:
                    PropertyDocNode(context, prop)
    # Display non-inherited methods
    if len([m for m in item_info.methods if not m.inherited or show_inherited]) > 0:
        with dcg.TreeNode(context, label="Methods"):
            for method in item_info.methods:
                if not method.inherited or show_inherited:
                    MethodDocNode(context, method)

    if isinstance(item_class, type) and len(item_class.__mro__) > 1 and item_class.__mro__[1].__name__ != "object":
        # Display inheritance tree
        with dcg.TreeNode(context, label="Inheritance"):
            for base in item_class.__mro__[1:]:
                if base.__name__ != item_class.__name__ and base.__name__ != "object":
                    with dcg.TreeNode(context, label=base.__name__):
                        display_item_documentation(context, base)

    #added_children = current_parent.children[len(prev_children):]
    ## Cache the added children for future reuse
    #cache[item_class] = added_children
    ## Store the cache in the function itself
    #display_item_documentation._cache = cache

class ItemDocumentation(dcg.Window):
    """
    Represents a window that displays documentation for a specific item class.
    """
    def __init__(self, context, item_class, **kwargs):
        """
        Initialize the documentation window.
        
        Args:
            context: DearCyGui context
            item_class: The class of the item to document
            **kwargs: Additional arguments passed to dcg.Window
        """
        super().__init__(context,
                         label=f"{item_class.__name__} Documentation",
                         width="0.9*fullx",
                         height="0.9*fully")
        self.configure(**kwargs)
        self._object_class = item_class
        with self:
            dcg.Checkbox(self.context, label="Show all inherited properties", callback=self._toggle_inherited)
            display_item_documentation(self.context, item_class)

    def _toggle_inherited(self, sender, target, value):
        """
        Toggle the display of inherited properties and methods.
        """
        self.children = [target]  # Erase all but keep the button
        with self:
            display_item_documentation(self.context, self._object_class, show_inherited=value)


def create_demo_icon():
    """
    Create a set of icon images for the DearCyGui Demo.
    
    This code has been generated by an AI and is not
    the official DearCyGui icon :-)
    """
    # Create icons in different sizes for OS to choose from
    sizes = [128, 64, 32, 16]
    icons = []
    
    for size in sizes:
        # Create RGBA image (height, width, 4)
        icon = np.zeros((size, size, 4), dtype=np.uint8)
        
        # Set background to transparent
        icon[:, :, 3] = 0
        
        # Create a gradient background with rounded corners
        center = size // 2
        for y in range(size):
            for x in range(size):
                # Calculate distance from center (for rounded corners)
                dx, dy = x - center, y - center
                dist = np.sqrt(dx*dx + dy*dy)
                
                # Create rounded corners by adjusting alpha
                if dist <= center:
                    # Gradient from blue to purple
                    ratio = dist / center
                    r = int(60 + 100 * ratio)  # Increase red with distance
                    g = int(70 - 50 * ratio)   # Decrease green with distance
                    b = int(200)               # Keep blue high
                    
                    # Set colors and full opacity
                    icon[y, x, 0] = r
                    icon[y, x, 1] = g 
                    icon[y, x, 2] = b
                    icon[y, x, 3] = 255
        
        # Add a distinctive 'DCG' marking in the center
        # For smaller icons, make simpler designs
        if size >= 32:
            # Draw 'D' shape
            thick = max(1, size // 16)
            radius = size // 3
            d_center_x = center - radius // 2
            
            for y in range(center - radius, center + radius):
                for x in range(d_center_x - thick, d_center_x + thick):
                    if x >= 0 and x < size and y >= 0 and y < size:
                        icon[y, x, 0:3] = [255, 255, 255]  # White
            
            # Vertical line for 'D'
            for y in range(center - radius, center + radius):
                for x in range(d_center_x - radius, d_center_x - radius + thick):
                    if x >= 0 and x < size and y >= 0 and y < size:
                        icon[y, x, 0:3] = [255, 255, 255]  # White
            
            # Draw 'C' shape
            c_center_x = center + radius // 3
            for angle in range(-60, 61):
                rad = np.radians(angle)
                x = int(c_center_x + radius//2 * np.cos(rad))
                y = int(center + radius//2 * np.sin(rad))
                
                for i in range(-thick//2, thick//2+1):
                    for j in range(-thick//2, thick//2+1):
                        px, py = x+i, y+j
                        if 0 <= px < size and 0 <= py < size:
                            icon[py, px, 0:3] = [255, 255, 255]
        
        # For small icons, just draw a simpler shape
        else:
            # Draw a simple circle
            for y in range(size):
                for x in range(size):
                    dx, dy = x - center, y - center
                    dist = np.sqrt(dx*dx + dy*dy)
                    if dist <= size//4:
                        icon[y, x, 0:3] = [255, 255, 255]  # White center
        
        icons.append(icon)
    
    return icons

"""
Version without asyncio:
"""
def launch_demo_noasyncio(title="DearCyGui Demo"):
    # Main function to run the demo
    context = dcg.Context()
    context.viewport.wait_for_input = True
    context.viewport.initialize(title=title, width=950, height=750, vsync=True)
    DemoWindow(context)

    while context.running:
        context.viewport.render_frame()


        
def launch_demo(title="DearCyGui Demo"):
    """
    Create a window displaying all the defined sections.
    """
    # Main function to run the demo
    context = dcg.Context()
    loop = asyncio.get_event_loop()
    context.queue = AsyncPoolExecutor()
    # refresh only when needed
    context.viewport.wait_for_input = True
    # Set an icon for the viewport (must be set before initializing the viewport)
    context.viewport.icon = create_demo_icon()
    # Set some app metadata (completly optional)
    dcg.os.set_application_metadata(
        name="DearCyGui Demo",
        version="0.1.0",
        identifier="dearcygui.demo",
        creator="DearCyGui Team",
        copyright="MIT",
        url="https://github.com/DearCyGui/Demos",
        type="application")
    # Initialize the viewport
    context.viewport.initialize(title=title, width=950, height=750)

    # Show a temporary centered window while the demo is loading
    with dcg.Window(context, x="viewport.width/2 - self.width/2",
                    y="viewport.height/2 - self.height/2",
                    width="0.9*viewport.width",
                    height="0.9*viewport.height") as temp_window:
        with dcg.VerticalLayout(context, alignment_mode=dcg.Alignment.CENTER):
            with dcg.HorizontalLayout(context, alignment_mode=dcg.Alignment.CENTER):
                dcg.Text(context, value="Please wait while the demo is loading...", color=(255, 255, 0))
    # Render two full frames for size convergence
    for _ in range(2):
        while not context.viewport.render_frame():
            pass

    DemoWindow(context)

    # Remove the temporary window
    temp_window.delete_item()

    loop.run_until_complete(run_viewport_loop(context.viewport))
    

