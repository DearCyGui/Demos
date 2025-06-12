from demo_utils import documented, democode, push_group, pop_group, launch_demo, demosection
import dearcygui as dcg
import functools
import time
import math

# decorators:
# - documented: the description (markdown) is displayed
# - democode: the code is displayed and can edited (and run again)
# - demosection: the section is displayed in the table of contents,
#    the section name is extracted from the function name.

@demosection
@documented
def _subclassing_intro(C: dcg.Context):
    """
    # Introduction to Subclassing in DearCyGui

    Subclassing is a powerful technique in object-oriented programming that allows you to create new classes
    based on existing ones. In the context of DearCyGui, subclassing enables you to:

    - Create reusable custom widgets
    - Encapsulate complex UI elements in a single class
    - Keep related data and functionality together
    - Make your code more maintainable and easier to understand

    This tutorial will guide you through the process of subclassing in DearCyGui, explain best practices,
    and help you avoid common pitfalls. Even if you're new to object-oriented programming,
    you'll learn practical techniques for building better UI applications.

    ## Why Use Subclassing?

    Consider a situation where you need several buttons that each display a counter and can increment it.
    Without subclassing, you'd have to:

    1. Create variables to track each counter
    2. Create buttons for each counter
    3. Write separate callback functions for each button
    4. Keep track of which function belongs to which button

    With subclassing, you can:

    1. Create a `CounterButton` class that handles its own state
    2. Simply create instances of this class wherever needed
    3. Let each instance manage its own data and behavior

    Let's explore how to do this effectively!
    """
    pass

@demosection
@documented
@democode
def _simple_subclass_example(C: dcg.Context):
    """
    ## A Simple Subclass Example

    Let's start with a basic example. We'll create a custom button that counts how many times it's been clicked.
    
    This demonstrates the fundamental concept of subclassing: we're extending the functionality of 
    an existing class (`dcg.Button`) to create our own specialized version.

    ### Key Concepts:

    1. We define a new class that inherits from a DearCyGui class
    2. We customize its behavior in the `__init__` method
    3. We add our own methods to handle specific functionality
    """
    # A simple subclass of dcg.Button that counts clicks
    class CounterButton(dcg.Button):
        def __init__(self, context, **kwargs):
            # Initialize the parent class (dcg.Button)
            super().__init__(context, **kwargs)
            
            # Add our own attributes
            self.count = 0
            
            # Set up the callback to our own method
            self.callback = self.on_click
            
        def on_click(self, sender, target, data):
            # Increment counter when button is clicked
            self.count += 1
            # Update the button label to show the count
            self.label = f"Clicked {self.count} times"
    
    # Create an instance of our custom button
    dcg.Text(C, value="Click the button below to see the counter increase:")
    counter_btn = CounterButton(C, label="Click me (0 times)")
    
    # Explanation
    dcg.Text(C, value="The button above is an instance of our CounterButton class.")
    dcg.Text(C, value="It inherits all the properties of a regular button but adds counting functionality.")

@demosection
@documented
@democode
def _python_naming_conventions(C: dcg.Context):
    """
    ## Python Naming Conventions and Access Control

    Python uses naming conventions to indicate the intended visibility of class members.
    Unlike some other languages that have strict access control keywords (`private`, `protected`),
    Python relies on naming conventions:

    - Variables with no special prefix are considered public
    - Variables starting with a single underscore (`_`) are considered "protected"
    - Variables starting with double underscores (`__`) are considered "private"

    These conventions are not enforced by the language but are widely followed in the Python community.
    
    ### Why This Matters

    Using these conventions helps other developers (and your future self) understand:
    - Which attributes are part of the public interface
    - Which attributes are intended for internal use only
    - Which attributes might change in future versions
    """
    # Example class with different variable naming conventions
    class TemperatureWidget(dcg.ChildWindow):
        def __init__(self, context, **kwargs):
            super().__init__(context, **kwargs)
            
            # Public attribute - intended to be accessed from outside
            self.current_temperature = 72
            
            # Protected attribute - intended to be used only within this class 
            # or by subclasses, but not from outside
            self._last_update_time = time.time()
            
            # Private attribute - intended to be used only within this class,
            # not even by subclasses
            self.__temperature_offset = 0
            
            # Set up the UI components inside the window
            self._create_ui(context)
        
        def _create_ui(self, context):
            # Protected method - internal implementation detail
            with self:
                dcg.Text(context, value=f"Temperature: {self.current_temperature}°F")
                dcg.Button(context, label="Refresh", callback=self._on_refresh)
        
        def _on_refresh(self, sender, target, data):
            # Protected method - internal implementation detail
            self._last_update_time = time.time()
            self.current_temperature = 70 + 5 * math.sin(time.time() / 10)
            self.refresh_ui(self.current_temperature)
        
        def refresh_ui(self, temperature):
            # Public method - part of the widget's interface
            self.children[0].value = f"Temperature: {temperature}°F"
            self.context.viewport.wake()
            
    # Create an instance of our custom widget
    temp_widget = TemperatureWidget(C, label="Temperature Monitor", width=300, height=100)
    
    # Explanation of naming conventions
    dcg.Text(C, value="\nNaming Convention Examples:")
    dcg.Text(C, marker="bullet", value="Public: temp_widget.current_temperature - intended for external use")
    dcg.Text(C, marker="bullet", value="Protected: temp_widget._last_update_time - intended for internal/subclass use")
    dcg.Text(C, marker="bullet", value="Private: temp_widget.__temperature_offset - intended for use only within the class")
    
    # Demonstrate accessing the attributes
    def check_temps():
        with temp_widget:
            # We can access public attributes normally
            public_val = temp_widget.current_temperature
            dcg.Text(C, value=f"Reading public attribute: current_temperature = {public_val}")
            
            # We can technically access protected attributes, but convention says we shouldn't
            protected_val = temp_widget._last_update_time
            dcg.Text(C, value=f"Reading protected attribute: _last_update_time = {protected_val:.2f} (not recommended)")
            
            # Private attributes are name-mangled and harder to access externally
            try:
                private_val = temp_widget.__temperature_offset
                dcg.Text(C, value=f"Private attribute: {private_val}")
            except AttributeError:
                dcg.Text(C, value="Cannot access private attribute __temperature_offset directly")
                # It's still possible to access it if you know the mangling scheme
                mangled_val = getattr(temp_widget, "_TemperatureWidget__temperature_offset", "Not found")
                dcg.Text(C, value=f"Access via name mangling: _TemperatureWidget__temperature_offset = {mangled_val}")
        C.viewport.wake()
        
    dcg.Button(C, label="Check Attributes", callback=check_temps)
    
    # Call a public method
    dcg.Button(C, label="Set Temperature", callback=lambda: temp_widget.refresh_ui(50))

@demosection
@documented
@democode
def _attribute_name_conflicts(C: dcg.Context):
    """
    ## Avoiding Attribute Name Conflicts

    When subclassing, you need to be careful about attribute name conflicts. If you define 
    an attribute with the same name as one in the parent class, you might override important functionality.

    This is particularly important with DearCyGui widgets, which have many built-in properties
    like `width`, `height`, `label`, etc.

    ### Two Different Types of Conflicts:

    1. **Property Overrides**: If you define a property with the same name as a parent class property, 
       your property completely replaces the parent's functionality
       
    2. **Attribute Setting**: If you set an attribute with the same name as a property, 
       you're not overriding the property itself, just setting a value on your instance

    Let's see examples of both scenarios:
    """
    # Example 1: Attribute setting (safe but can be confusing)
    class MyButton1(dcg.Button):
        def __init__(self, context, **kwargs):
            super().__init__(context, **kwargs)
            
            # This sets the label property value, doesn't override the property itself
            self.label = "My Custom Label"
            
            # Custom attribute that doesn't conflict with any DearCyGui property
            self.click_count = 0
            
            self.callback = self.on_click
            
        def on_click(self, sender, target, data):
            self.click_count += 1
            self.label = f"Clicked {self.click_count} times"
    
    # Example 2: Property override (potentially dangerous)
    class MyButton2(dcg.Button):
        def __init__(self, context, **kwargs):
            super().__init__(context, **kwargs)
            self.click_count = 0
            self.callback = self.on_click
        
        def on_click(self, sender, target, data):
            self.click_count += 1
            self.label = f"Clicked {self.click_count} times"
        
        # This OVERRIDES the built-in label property
        @property
        def label(self):
            return f"CUSTOM: {self._my_label}"
            
        @label.setter
        def label(self, value):
            self._my_label = value
            # We forgot to actually update the button's displayed text!
            # This breaks the built-in functionality
    
    # Create instances of our buttons
    dcg.Text(C, value="Example 1: Safe attribute setting")
    btn1 = MyButton1(C, label="Button 1")
    
    dcg.Text(C, value="\nExample 2: Dangerous property override")
    btn2 = MyButton2(C, label="Button 2") 
    
    # Show the problem
    dcg.Text(C, value="\nThe second button's label isn't displaying properly because " +
                     "we overrode the 'label' property without correctly implementing it.")
    
    # Best practice example
    dcg.Text(C, value="\nBest Practice Example:")
    
    class SafeCustomButton(dcg.Button):
        def __init__(self, context, **kwargs):
            super().__init__(context, **kwargs)
            
            # Use protected attributes with distinct names to avoid conflicts
            self._click_count = 0
            self._last_click_time = 0
            
            # Set the callback to our method
            self.callback = self._on_click
        
        def _on_click(self, sender, target, data):
            self._click_count += 1
            self._last_click_time = time.time()
            # Use the built-in property correctly
            self.label = f"Clicked {self._click_count} times"
            
        def get_stats(self):
            return {
                "count": self._click_count,
                "last_click": self._last_click_time
            }
    
    safe_btn = SafeCustomButton(C, label="Safe Button")
    dcg.Text(C, value="This button uses protected attributes with distinct names to avoid conflicts.")

@demosection
@documented
@democode
def _memory_management(C: dcg.Context):
    """
    ## Memory Management and Object Lifecycle

    Understanding how Python manages memory is crucial when working with UI elements.
    
    ### Python's Memory Management

    Python uses reference counting and garbage collection:
    
    1. Objects are kept in memory as long as there are references to them
    2. When the reference count drops to zero, the object becomes eligible for cleanup
    3. The garbage collector periodically frees memory for objects that are no longer referenced

    ### DearCyGui and Memory Management

    In DearCyGui, UI elements exist in a parent-child tree structure:
    
    1. When an item is added to the UI tree, DearCyGui maintains an internal reference to it
    2. This means you don't need to keep your own reference to prevent garbage collection
    3. However, if you need to access an item later, you should keep a reference or retrieve it later

    Let's see examples of how this works:
    """
    # Example 1: Items in the tree stay alive even without external references
    class AutoDestroyExample(dcg.ChildWindow):
        def __init__(self, context, **kwargs):
            super().__init__(context, **kwargs)
            
            # These UI elements will be children of this window
            # We don't need to store references to them
            with self:
                dcg.Text(context, value="This text exists in the UI tree")
                dcg.Button(context, label="Create Temporary Text", 
                           callback=self._create_temp_item)
                
        def _create_temp_item(self, sender, target, data):
            # Create a new text element - we don't store a reference
            # It will still appear and stay visible because it's in the UI tree
            with self:
                new_text = dcg.Text(self.context, value=f"Temporary text created at {time.time():.2f}")
                
                # Button to remove its sibling text
                dcg.Button(self.context, label="Remove Text Above", 
                           callback=lambda s, t, d: new_text.delete_item())
    
    # Create the example window
    auto_example = AutoDestroyExample(C, label="Memory Management Example", 
                                      width=400, height=200)
    
    dcg.Text(C, value="\nExample of object lifecycle and cleanup:")
    
    # Example 2: Explicit cleanup with __del__
    class CleanupExample(dcg.ChildWindow):
        def __init__(self, context, **kwargs):
            super().__init__(context, **kwargs)
            
            # External resource simulation
            self._resource_id = id(self)
            print(f"Created resource: {self._resource_id}")
            
            # Set up UI
            with self:
                dcg.Text(context, value="Window with cleanup example")
                dcg.Button(context, label="Delete this window", 
                           callback=lambda s, t, d: self.delete_item())
        
        def __del__(self):
            # This gets called when the object is about to be destroyed
            print(f"Cleaning up resource: {self._resource_id}")
            # In a real app, you might close files, network connections, etc.
    
    # Function to create the cleanup example window
    def create_cleanup_window():
        window = CleanupExample(C, label="Cleanup Demo", width=300, height=100)
        dcg.Text(C, value=f"Window created with ID: {window._resource_id}")
        dcg.Text(C, value="Check console output when window is closed")
        C.viewport.wake()
    
    dcg.Button(C, label="Create Window with Cleanup", callback=lambda s, t, d: create_cleanup_window())
    
    dcg.Text(C, value="\nKey points about memory management:")
    dcg.Text(C, value="1. UI elements stay alive as long as they're in the UI tree")
    dcg.Text(C, value="2. You only need to keep references if you plan to modify items later")
    dcg.Text(C, value="3. The __del__ method can be used for cleanup when objects are destroyed")
    dcg.Text(C, value="4. Be careful with circular references as they can prevent cleanup")

@demosection
@documented
@democode
def _class_method_callbacks(C: dcg.Context):
    """
    ## Using Class Methods for Callbacks

    One of the most powerful aspects of subclassing is the ability to use class methods as callbacks.
    This approach has several advantages:

    1. Methods have access to the instance's attributes
    2. Related functionality stays organized within the class
    3. Each instance maintains its own state independently

    ### Best Practices:

    1. Use instance methods for callbacks that need to access or modify instance state
    2. Prefix protected methods with underscore (`_`) to indicate they're internal
    3. Use descriptive method names that indicate their purpose

    Let's see an example of a well-structured class with proper callbacks:
    """
    class ColorPicker(dcg.ChildWindow):
        """A custom color picker widget with preview and history."""
        
        def __init__(self, context, **kwargs):
            super().__init__(context, **kwargs)
            
            # Initialize instance variables
            self._color_history = []
            self._current_color = (255, 0, 0, 255)  # Start with red
            
            # Build the UI
            self._create_ui(context)
        
        def _create_ui(self, context):
            """Creates the internal UI elements."""
            with self:
                # Main row with color editor and preview
                with dcg.HorizontalLayout(context, width=-1):
                    # Color editor
                    self._color_editor = dcg.ColorEdit(
                        context, 
                        label="Select Color",
                        value=self._current_color,
                        callback=self._on_color_changed
                    )
                    
                    # Color preview
                    self._preview = dcg.ColorButton(
                        context,
                        value=self._current_color,
                        width=40,
                        height=40,
                        no_border=True
                    )
                
                # History section
                with dcg.CollapsingHeader(context, label="Color History", value=True):
                    self._history_container = dcg.ChildWindow(
                        context, 
                        width=-1, 
                        height=80,
                        no_scrollbar=False
                    )
                
                # Buttons row
                with dcg.HorizontalLayout(context, width=-1):
                    dcg.Button(context, label="Add to History", callback=self._on_add_to_history)
                    dcg.Button(context, label="Clear History", callback=self._on_clear_history)
        
        def _on_color_changed(self, sender, target, color):
            """Called when the color editor value changes."""
            self._current_color = color
            self._preview.value = color
            self.context.viewport.wake()
        
        def _on_add_to_history(self, sender, target, data):
            """Adds the current color to history."""
            # Add to our internal list
            self._color_history.append(self._current_color)
            
            # Add a color button to the history container
            with self._history_container:
                new_color_btn = dcg.ColorButton(
                    self.context,
                    value=self._current_color, 
                    width=30, 
                    height=30,
                    no_border=False,
                    no_newline=True
                )
                
                # Using a method as callback and passing the color as data
                new_color_btn.callback = self._on_history_color_selected
            self.context.viewport.wake()
        
        def _on_history_color_selected(self, sender, target, data):
            """Called when a color from history is selected."""
            selected_color = sender.value
            self._current_color = selected_color
            
            # Update the color editor and preview
            self._color_editor.value = selected_color
            self._preview.value = selected_color
            self.context.viewport.wake()
        
        def _on_clear_history(self, sender, target, data):
            """Clears the color history."""
            self._color_history = []
            
            # Remove all children from the history container
            for child in list(self._history_container.children):
                child.delete_item()
            self.context.viewport.wake()
        
        # Public methods that form our class interface
        def get_color(self):
            """Returns the currently selected color."""
            return self._current_color
        
        def set_color(self, color):
            """Sets the current color."""
            self._current_color = color
            self._color_editor.value = color
            self._preview.value = color
    
    # Create an instance of our custom color picker
    dcg.Text(C, value="Custom Color Picker Widget Example:")
    color_picker = ColorPicker(C, label="Color Picker", width=400, height=250)
    
    # Add some buttons to demonstrate the public interface
    dcg.Text(C, value="\nInteracting with the widget through its public interface:")
    with dcg.HorizontalLayout(C):
        dcg.Button(C, label="Set to Blue", 
                   callback=lambda s, t, d: color_picker.set_color((0, 0, 255, 255)))
        
        dcg.Button(C, label="Set to Green", 
                   callback=lambda s, t, d: color_picker.set_color((0, 255, 0, 255)))
        
        dcg.Button(C, label="Get Current Color", 
                   callback=lambda s, t, d: dcg.Text(
                       C, value=f"Current color: {color_picker.get_color()}"
                   ))

@demosection
@documented
@democode
def _closure_pitfalls(C: dcg.Context):
    """
    ## The Dangers of Closures in Callbacks

    When creating callbacks in DearCyGui, a common pitfall is using closures incorrectly.
    A **closure** is a function that remembers the environment where it was created, including
    variables from the outer scope.

    ### The Problem:

    When you define a function inside a method and reference variables from that method,
    the function captures references to these variables, not their values at the time of creation.
    If those variables change, the function will use the new values.

    This can lead to unexpected behavior when:
    1. The callback is triggered later, after the variable values have changed
    2. Multiple callbacks are created in a loop or iteration

    Let's see an example of this problem and how to fix it:
    """
    class ProblematicCounter(dcg.ChildWindow):
        def __init__(self, context, **kwargs):
            super().__init__(context, **kwargs)
            
            with self:
                dcg.Text(context, value="Problematic Buttons - They'll ALL show the SAME number")
                
                # Problem: Creating buttons with closures in a loop
                for i in range(5):
                    # Wrong way: The callback references 'i', which changes with each iteration
                    def problematic_callback(sender, target, data):
                        dcg.Text(context, value=f"You clicked button with index: {i}", next_sibling=self.children[0])
                        self.context.viewport.wake()
                    dcg.Button(
                        context, 
                        label=f"Button {i}",
                        callback=problematic_callback
                    )
                
                dcg.Separator(context)
                dcg.Text(context, value="Fixed Buttons - Each shows its correct number")
                
                # Solution 1: Using default parameters to capture the current value
                for i in range(5):
                    # Right way: Pass 'i' as a default parameter to capture its current value
                    def fixed_callback(sender, target, data, i=i):
                        dcg.Text(context, value=f"You clicked button with index: {i}", next_sibling=self.children[0])
                        self.context.viewport.wake()
                    dcg.Button(
                        context, 
                        label=f"Button {i} (Fix 1)",
                        callback=fixed_callback
                    )
                
                dcg.Separator(context)
                
                # Solution 2: Using partial function application
                for i in range(5):
                    # Right way: Use functools.partial to bind the current value of 'i'
                    def fixed_callback_2(sender, target, data, index):
                        dcg.Text(context, value=f"You clicked button with index: {index}", next_sibling=self.children[0])
                        self.context.viewport.wake()
                    dcg.Button(
                        context, 
                        label=f"Button {i} (Fix 2)",
                        callback=functools.partial(fixed_callback_2, index=i)
                    )
    
    # Create an instance of our problematic counter
    dcg.Text(C, value="Example of Closure Problems and Solutions:")
    ProblematicCounter(C, label="Closure Problems and Solutions", 
                       width=500, height=400)
    
    # Additional explanation
    dcg.Text(C, value="\nExplanation of the Problem and Solutions:")
    
    with dcg.ChildWindow(C, width=-1, height=200):
        dcg.Text(C, value="The Problem:")
        dcg.Text(C, value="When you define a function inside a loop that references a loop variable,")
        dcg.Text(C, value="all functions end up referring to the FINAL value of that variable.")
        dcg.Text(C, value="This happens because the functions capture a REFERENCE to the variable,")
        dcg.Text(C, value="not its value at the time the function was created.")
        
        dcg.Separator(C)
        
        dcg.Text(C, value="Solutions:")
        dcg.Text(C, value="1. Use default parameters to capture the current value")
        dcg.Text(C, value="2. Use partial function application (functools.partial)")
        dcg.Text(C, value="3. Create a factory function that returns a callback with the value bound")
        dcg.Text(C, value="Always be careful when callbacks reference variables from their enclosing scope!")

@demosection
@documented
@democode
def _practical_custom_widget(C: dcg.Context):
    """
    ## A Practical Custom Widget Example

    Now that we've covered the key concepts and best practices, let's build a practical
    custom widget that incorporates everything we've learned.
    
    We'll create a `GraphWidget` that:
    1. Displays a line graph of values
    2. Has controls to add and clear data points
    3. Properly handles internal state and callbacks
    4. Follows proper naming conventions and avoids memory leaks
    
    This example demonstrates how subclassing helps create reusable, maintainable components.
    """
    import random
    
    class GraphWidget(dcg.ChildWindow):
        """A custom graph widget that displays a line of values."""
        
        def __init__(self, context, 
                     title="Graph Widget",
                     max_points=100, 
                     y_min=0, 
                     y_max=100, 
                     line_color=(0, 150, 255, 255),
                     **kwargs):
            """Initialize a new graph widget.
            
            Args:
                context: DearCyGui context
                title: Title for the graph
                max_points: Maximum number of points to show
                y_min: Minimum y-axis value
                y_max: Maximum y-axis value
                line_color: Color of the graph line
                **kwargs: Additional arguments for the ChildWindow
            """
            super().__init__(context, **kwargs)
            
            # Store configuration as protected attributes
            self._title = title
            self._max_points = max_points
            self._y_min = y_min
            self._y_max = y_max
            self._line_color = line_color
            
            # Initialize data with empty list
            self._data_points = []
            
            # Build the UI
            self._create_ui(context)
        
        def _create_ui(self, context):
            """Creates the internal UI components."""
            with self:
                # Graph title
                dcg.Text(context, value=self._title)
                
                # Graph with data
                self._plot = dcg.Plot(
                    context,
                    height=200,
                    width=-1,
                    no_mouse_pos=True,
                    no_legend=True
                )
                
                # Configure axis limits
                self._plot.Y1.min = self._y_min
                self._plot.Y1.max = self._y_max
                
                # Controls section
                with dcg.HorizontalLayout(context, width=-1):
                    # Add random point button
                    dcg.Button(
                        context,
                        label="Add Point",
                        callback=self._on_add_point
                    )
                    
                    # Clear button
                    dcg.Button(
                        context,
                        label="Clear",
                        callback=self._on_clear_graph
                    )
                    
                    # Last value display
                    self._value_display = dcg.Text(
                        context,
                        value="No data"
                    )
                
                # Update the graph initially
                self._update_graph()
        
        def _on_add_point(self, sender, target, data):
            """Adds a random data point to the graph."""
            # Generate a random value within our y-axis range
            new_value = random.uniform(self._y_min, self._y_max)
            
            # Add to our data points
            self._data_points.append(new_value)
            
            # Maintain maximum number of points
            if len(self._data_points) > self._max_points:
                self._data_points.pop(0)  # Remove oldest point
            
            # Update the display
            self._value_display.value = f"Last value: {new_value:.2f}"
            
            # Refresh the graph
            self._update_graph()
        
        def _on_clear_graph(self, sender, target, data):
            """Clears all data points from the graph."""
            self._data_points = []
            self._value_display.value = "No data"
            self._update_graph()
        
        def _update_graph(self):
            """Updates the graph with current data."""
            # Delete existing plot children
            for child in list(self._plot.children):
                child.delete_item()
            
            # If we have data, plot it
            if self._data_points:
                # Generate x-coordinates (0, 1, 2, ...)
                x_values = list(range(len(self._data_points)))
                
                # Create the line plot
                dcg.PlotLine(
                    self.context,
                    X=x_values,
                    Y=self._data_points,
                    theme=dcg.ThemeColorImPlot(C, line=self._line_color),
                    parent=self._plot
                )
                
                # Auto-fit x-axis to the data
                self._plot.X1.min = 0
                self._plot.X1.max = len(self._data_points) - 1
            else:
                # No data case
                self._plot.X1.min = 0
                self._plot.X1.max = 10
            self.context.viewport.wake()
        
        # Public methods
        
        def add_value(self, value):
            """Adds a specific value to the graph.
            
            Args:
                value: The value to add (should be within y_min and y_max)
            """
            # Ensure value is within range
            value = max(self._y_min, min(self._y_max, value))
            
            # Add to our data points
            self._data_points.append(value)
            
            # Maintain maximum number of points
            if len(self._data_points) > self._max_points:
                self._data_points.pop(0)
            
            # Update the display
            self._value_display.value = f"Last value: {value:.2f}"
            
            # Refresh the graph
            self._update_graph()
        
        def clear(self):
            """Clears all data points from the graph."""
            self._data_points = []
            self._value_display.value = "No data"
            self._update_graph()
        
        def get_data(self):
            """Returns a copy of the current data points."""
            return self._data_points.copy()
    
    # Create instances of our graph widget to demonstrate reusability
    dcg.Text(C, value="Example Custom Graph Widgets:")
    
    with dcg.HorizontalLayout(C, width=-1):
        # Temperature graph
        temp_graph = GraphWidget(
            C,
            title="Temperature Over Time",
            max_points=50,
            y_min=0,
            y_max=100,
            line_color=(255, 100, 50, 255),
            label="Temperature",
            width=300,
            height=300
        )
        
        # Revenue graph with different settings
        revenue_graph = GraphWidget(
            C,
            title="Revenue ($1000s)",
            max_points=30,
            y_min=0,
            y_max=1000,
            line_color=(50, 200, 50, 255),
            label="Revenue",
            width=300,
            height=300
        )
    
    # Add some sample data
    for _ in range(15):
        temp_graph.add_value(random.uniform(30, 90))
        revenue_graph.add_value(random.uniform(100, 800))
    
    # Demonstrate accessing instance methods
    dcg.Text(C, value="\nInteracting with these widgets through their public interfaces:")
    
    with dcg.HorizontalLayout(C):
        dcg.Button(
            C,
            label="Add Temperature",
            callback=lambda s, t, d: temp_graph.add_value(random.uniform(30, 90))
        )
        
        dcg.Button(
            C,
            label="Add Revenue",
            callback=lambda s, t, d: revenue_graph.add_value(random.uniform(100, 800))
        )
        
        dcg.Button(
            C,
            label="Clear Both",
            callback=lambda s, t, d: [temp_graph.clear(), revenue_graph.clear()]
        )

@demosection
@documented
def _subclassing_summary(C: dcg.Context):
    """
    ## Summary: Best Practices for Subclassing in DearCyGui

    Here's a summary of the key points we've covered in this tutorial:

    ### Naming Conventions:
    - Use `_variable_name` (single underscore) for protected attributes
    - Use `__variable_name` (double underscore) for private attributes
    - Use clear, descriptive names for public methods and attributes

    ### Avoiding Conflicts:
    - Be careful not to override built-in properties with your own properties
    - Use distinct names for your attributes to avoid conflicts
    - Consider the parent class's interface when designing your subclass

    ### Memory Management:
    - UI elements stay alive as long as they're in the UI tree
    - Use `__del__` for cleanup when needed
    - Be aware of reference counting and how it affects object lifecycle

    ### Callbacks:
    - Use instance methods as callbacks for better organization
    - When using closures in callbacks, be careful with variable capture
    - Use default parameters or partial functions to capture values in loops

    ### Structure and Design:
    - Keep related data and functionality together in a class
    - Use protected methods for internal implementation details
    - Provide a clean public interface for your widgets
    - Document your classes with docstrings

    By following these practices, you can create reusable, maintainable custom widgets
    that enhance your DearCyGui applications and make your code easier to understand
    and modify.
    """
    pass

if __name__ == "__main__":
    launch_demo(title="Subclassing Tutorial")