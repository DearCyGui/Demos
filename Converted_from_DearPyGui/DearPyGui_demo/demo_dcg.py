import colorsys
import dearcygui as dcg
from math import cos

# This file is a direct DearCyGui equivalent to the original DearPyGui demo.py

def hsv(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return r, g, b, 1.0

def _config(sender, target : dcg.uiItem):
    items = target.user_data

    if isinstance(sender, dcg.RadioButton):
        value = True
    else:
        keyword = target.label
        value = target.value

    if isinstance(items, list):
        for item in items:
            setattr(item, keyword, value)
    else:
        item = items
        setattr(item, keyword, value)

def _log(sender, target, data):
    print(f"Event from sender: {sender}, for target: {target}, with data: {data}")

class ConfigureOptions(dcg.Layout):
    def __init__(self, C, item, columns, *names, **kwargs):
        super().__init__(C, **kwargs)
        if columns == 1:
            for name in names:
                dcg.Checkbox(C,
                             label=name,
                             callback=_config,
                             user_data=item,
                             parent=self,
                             value=getattr(item, name))
        else:
            with dcg.VerticalLayout(C, parent=self):
                for i in range((len(names)+(columns - 1))//columns):
                    with dcg.HorizontalLayout(C):
                        for j in range(columns):
                            if (i*columns + j) >= len(names): 
                                break
                            dcg.Checkbox(C,
                                         label=names[i*columns + j], 
                                         callback=_config, 
                                         user_data=item, 
                                         value=getattr(item, names[i*columns + j]))

def add_help_symbol(target, message):
    C = target.context
    with dcg.HorizontalLayout(C, parent=target.parent) as hl:
        target.parent = hl
        text_to_hover = dcg.Text(C, value="(?)", color=[0, 255, 0])
        with dcg.Tooltip(C, target=text_to_hover):
            dcg.Text(C, value=message)

def show_demo(C : dcg.Context):
    with dcg.Window(C, label="DearCyGui Demo",
                    width=800, height=800,
                    pos_to_viewport=(100, 100)) as __demo_id:
        with dcg.MenuBar(C):
            with dcg.Menu(C, label="Menu"):
                dcg.Text(C, value="This menu is just for show!")
                dcg.MenuItem(C, label="New")
                dcg.MenuItem(C, label="Open")

                with dcg.Menu(C, label="Open Recent"):
                    dcg.MenuItem(C, label="harrel.c")
                    dcg.MenuItem(C, label="patty.h")
                    dcg.MenuItem(C, label="nick.py")

                dcg.MenuItem(C, label="Save")
                dcg.MenuItem(C, label="Save As...")

                with dcg.Menu(C, label="Settings"):
                    dcg.MenuItem(C, label="Option 1", callback=_log)
                    dcg.MenuItem(C, label="Option 2", check=True, callback=_log)
                    dcg.MenuItem(C, label="Option 3", check=True, value=True, callback=_log)

                    with dcg.ChildWindow(C, height=60, auto_resize_x=True):
                        for i in range(10):
                            dcg.Text(C, value=f"Scolling Text{i}")

                    dcg.Slider(C, label="Slider Float", format="float")
                    dcg.InputValue(C, label="Input Int", format="int")
                    dcg.Combo(C, items=("Yes", "No", "Maybe"), label="Combo")

            with dcg.Menu(C, label="Tools"):
                dcg.MenuItem(C, label="Show Metrics", callback=lambda: dcg.utils.MetricsWindow(C))
                dcg.MenuItem(C, label="Show Debug", callback=lambda: dcg.utils.ItemInspecter(C))

            with dcg.Menu(C, label="Settings"):
                dcg.MenuItem(C, label="Wait For Input", check=True, callback=lambda s, t, d: C.viewport.configure(wait_for_input=d))
                dcg.MenuItem(C, label="Toggle Fullscreen", callback=lambda: C.viewport.configure(fullscreen=not C.viewport.fullscreen))

        with dcg.CollapsingHeader(C, label="Window Options"):
            ConfigureOptions(C, __demo_id, 3, 
                             "no_title_bar", "no_scrollbar", "menubar", 
                             "no_move", "no_resize", "no_collapse",
                             "has_close_button", "no_background", "no_bring_to_front_on_focus",
                             "unsaved_document"
                             )


        with dcg.CollapsingHeader(C, label="Widgets"):
            with dcg.TreeNode(C, label="Basic"):
                with dcg.HorizontalLayout(C):
                    dcg.Button(C, label="Button", callback=_log)
                    dcg.Button(C, label="Small Button", callback=_log, small=True)
                    dcg.Button(C, label="Arrow Button", callback=_log, arrow=True)
                    for direction in [dcg.ButtonDirection.LEFT, dcg.ButtonDirection.RIGHT, dcg.ButtonDirection.DOWN]:
                        dcg.Button(C, callback=_log, arrow=True, direction=direction)

                dcg.Button(C, label="Repeat Button", callback=_log, repeat=True)
                dcg.Checkbox(C, label="checkbox", callback=_log)
                dcg.RadioButton(C, items=["radio a", "radio b", "radio c"], horizontal=True, callback=_log)
                dcg.Selectable(C, label="selectable", callback=_log)

                with dcg.HorizontalLayout(C):
                    for i in range(7):
                        with dcg.ThemeList(C) as theme:
                            dcg.ThemeColorImGui(C,
                                                Button=hsv(i/7.0, 0.6, 0.6),
                                                ButtonHovered=hsv(i/7.0, 0.7, 0.7),
                                                ButtonActive=hsv(i/7.0, 0.8, 0.8))
                            dcg.ThemeStyleImGui(C,
                                                FrameRounding=i*5,
                                                FramePadding=(i*3, i*3))
                        dcg.Button(C, label="Click", callback=_log, theme=theme)

                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value="Counter: ")
                    counter = dcg.Text(C, value="0")
                    dcg.Button(C, arrow=True, direction=dcg.ButtonDirection.LEFT, 
                             callback=lambda: counter.configure(value=str(int(counter.value)-1)))
                    dcg.Button(C, arrow=True, direction=dcg.ButtonDirection.RIGHT,
                             callback=lambda: counter.configure(value=str(int(counter.value)+1)))

                dcg.Separator(C)
                
                text_to_hover = dcg.Text(C, value="hover me")
                with dcg.Tooltip(C, target=text_to_hover):
                    dcg.Text(C, value="I'm a tooltip!")

                dcg.Separator(C, label="This is a separator with text")

                dcg.Text(C, value="With Label", show_label=True, label="Label")
                combo = dcg.Combo(C, items=["AAAA", "BBBB", "CCCC", "DDDD"], 
                                label="combo", value="AAAA", callback=_log)
                input_text_hello = dcg.InputText(C, label="input text", value="Hello, world!", callback=_log)

                help_text = """Hover me for help: 
                - Hold SHIFT for text selection
                - CTRL+Left/Right to word jump
                - CTRL+A or double-click to select all
                - CTRL+X,C,V for clipboard
                - CTRL+Z,Y for undo/redo
                - ESCAPE to revert
                """
                add_help_symbol(input_text_hello, help_text)
                dcg.InputText(C, label="input text (w/ hint)", hint="enter text here", callback=_log)
                dcg.InputValue(C, label="input int", format="int", callback=_log)
                dcg.InputValue(C, label="input float", format="float", print_format="%.3f", callback=_log)
                dcg.InputValue(C, label="input scientific", format="float", print_format="%e", callback=_log)

                dcg.InputValue(C, label="input floatx", format="float", array_size=4, callback=_log, value=[1,2,3,4])
                dcg.InputValue(C, label="input double", format="double", print_format="%.14f", callback=_log)
                dcg.InputValue(C, label="input doublex", format="double", print_format="%.14f", array_size=4, callback=_log, value=[1,2,3,4])

                drag_int = dcg.Slider(C, label="drag int", format="int", drag=True, callback=_log)
                add_help_symbol(drag_int, 
                    "Click and drag to edit value.\n"
                    "Hold SHIFT/ALT for faster/slower edit.\n"
                    "Double-click or CTRL+click to input value.")
                
                dcg.Slider(C, label="drag int 0..100", format="int", print_format="%d%%", drag=True, callback=_log)
                dcg.Slider(C, label="drag float", format="float", drag=True, callback=_log)
                dcg.Slider(C, label="drag small float", format="float",
                           print_format="%.06f ns", drag=True, value=0.0067, callback=_log)

                slider_int = dcg.Slider(C, label="slider int", format="int", max_value=3, callback=_log)
                add_help_symbol(slider_int, "CTRL+click to enter value.")
                
                dcg.Slider(C, label="slider float", format="float", print_format="ratio = %.3f", max_value=1.0, callback=_log)
                dcg.Slider(C, label="slider double", format="double", print_format="ratio = %.14f", max_value=1.0, callback=_log)
                dcg.Slider(C, label="slider angle", format="int", print_format="%d deg", min_value=-360, max_value=360, callback=_log)

                add_help_symbol(dcg.ColorEdit(C, label="color edit 4", value=(102, 179, 0, 128), callback=_log),
                    "Click on the colored square to open a color picker.\n"
                    "Click and hold to use drag and drop.\n"
                    "Right-click on the colored square to show options.\n"
                    "CTRL+click on individual component to input value.")

                dcg.ColorEdit(C, label="color edit floats", value=(.5, 1, .25, .1), callback=_log)
                
                dcg.ListBox(C, items=("Apple", "Banana", "Cherry", "Kiwi", "Mango", "Orange", "Pineapple", 
                                     "Strawberry", "Watermelon"), label="listbox", num_items=4, callback=_log)
                dcg.ColorButton(C, color=(255, 0, 0, 255), label="color button", callback=_log)

            with dcg.TreeNode(C, label="Combo"):
                items = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                combo_demo = dcg.Combo(C, items=items, label="combo", height_mode="small")

                def change_combo_height(sender, target, mode):
                    combo_demo.configure(height_mode=mode)

                dcg.RadioButton(C, items=("small", "regular", "large", "largest"),
                              callback=change_combo_height, horizontal=True)

                ConfigureOptions(C, combo_demo, 1, 
                               "popup_align_left", "no_arrow_button", 
                               "no_preview", "fit_width")

            with dcg.TreeNode(C, label="Color Picker & Edit"):

                def _color_picker_configs(sender, target, value):
                    target = target.user_data

                    # picker_mode
                    if value == "bar":
                        target.picker_mode = "bar"
                    elif value == "wheel":
                        target.picker_mode = "wheel"

                    # alpha_preview
                    elif value == "AlphaPreviewNone":
                        target.alpha_preview = "none"
                    elif value == "AlphaPreview":
                        target.alpha_preview = "full"
                    elif value == "AlphaPreviewHalf":
                        target.alpha_preview = "half"

                    # display_type
                    elif value == "uint8":
                        target.data_type = "uint8"
                    elif value == "float":
                        target.data_type = "float"

                    # display_mode
                    elif value == "rgb":
                        target.display_mode = "rgb"
                    elif value == "hsv":
                        target.display_mode = "hsv"
                    elif value == "hex":
                        target.display_mode = "hex"

                    # input mode
                    elif value == "input_rgb":
                        target.input_mode = "rgb"
                    elif value == "input_rhsv":
                        target.input_mode = "hsv"
                    elif value == "input_rhex":
                        target.input_mode = "hex"

                dcg.Text(C, value="Color Picker")


                # The equivalent DPG code used to allocate the ID
                # in advance. This is not possible in DearCyGui.
                # Instead we create the item, and append it later
                # at the equivalent location as the DPG code.
                color_picker = dcg.ColorPicker(C, value=(255, 0, 255, 200),
                                label="Color Picker", alpha_preview=True,
                                no_alpha=False, alpha_bar=True, 
                                width=200)
                
                with dcg.HorizontalLayout(C) as _before_id:
                    dcg.Text(C, value="picker_mode:")
                    dcg.RadioButton(C, items=("bar", "wheel"),
                                    callback=_color_picker_configs, 
                                    user_data=color_picker, horizontal=True)
                
                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value="alpha_preview:")
                    dcg.RadioButton(C, items=("AlphaPreviewNone",
                                              "AlphaPreview",
                                              "AlphaPreviewHalf"),
                                    callback=_color_picker_configs, 
                                    user_data=color_picker, horizontal=True)

                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value="display_type:")
                    dcg.RadioButton(C, value=("uint8",
                                              "float"),
                                    callback=_color_picker_configs, 
                                    user_data=color_picker, horizontal=True)

                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value="input_mode:")
                    dcg.RadioButton(C, items=("input_rgb",
                                              "input_hsv"),
                                    callback=_color_picker_configs, 
                                    user_data=color_picker, horizontal=True)

                color_picker.parent = color_picker.parent # reattach (thus appending)

                ConfigureOptions(C, color_picker, 3, 
                                 "no_alpha", "no_side_preview", 
                                 "no_small_preview", "no_inputs", "no_tooltip",
                                 "no_label", before=_before_id)

                dcg.Separator(C)

                dcg.Text(C, value="Color Edit")

                # Color Edit
                color_edit = dcg.ColorEdit(C, value=(255, 0, 255, 255), 
                                         label="Color Edit", width=200)

                with dcg.HorizontalLayout(C) as _before_id:
                    dcg.Text(C, value="alpha_preview:")
                    dcg.RadioButton(C, items=("AlphaPreviewNone",
                                          "AlphaPreview", 
                                          "AlphaPreviewHalf"),
                                callback=_color_picker_configs,
                                user_data=color_edit, horizontal=True)

                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value="display_type:")
                    dcg.RadioButton(C, items=("uint8", "float"),
                                callback=_color_picker_configs,
                                user_data=color_edit, horizontal=True)

                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value="display_mode:")
                    dcg.RadioButton(C, items=("rgb", "hsv", "hex"),
                                callback=_color_picker_configs,
                                user_data=color_edit, horizontal=True)

                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value="input_mode:")
                    dcg.RadioButton(C, items=("input_rgb", "input_hsv"),
                                callback=_color_picker_configs,
                                user_data=color_edit, horizontal=True)

                color_edit.parent = color_edit.parent # reattach (thus appending)

                ConfigureOptions(C, color_edit, 3,
                             "no_alpha", "no_picker", "no_options", 
                             "no_inputs", "no_small_preview", "no_tooltip",
                             "no_label", "no_drag_drop", "alpha_bar",
                             before=_before_id)

            with dcg.TreeNode(C, label="List Boxes"):
                items = ("A","B","C","D","E","F","G","H","I","J","K","L","M" "O","P","Q","R","S","T","U","V","W","X","Y","Z")
                listbox_1 = dcg.ListBox(C, items=items, label="listbox 1 (full)")
                listbox_2 = dcg.ListBox(C, items=items, label="listbox 2", width=200)
                dcg.InputValue(C, format="int", label="num_items",
                               callback=_config, user_data=[listbox_1, listbox_2], before = listbox_1)
                dcg.Slider(C, format="int", label="width",
                           value=200, callback=_config, user_data=listbox_2,
                           before = listbox_1, max_value=500)

            with dcg.TreeNode(C, label="Selectables"):
                with dcg.TreeNode(C, label="Basic"):
                    dcg.Selectable(C, label="1. I am selectable")
                    dcg.Text(C, value="2. I am not selectable") 

                with dcg.TreeNode(C, label="Selection State: Single"):
                    items = []
                    def _selection(sender, target, _):
                        for item in items:
                            if item != sender:
                                item.value = False
                    
                    for i in range(5):
                        items.append(
                            dcg.Selectable(C, label=f"{i+1}. I am selectable", callback=_selection)
                        )
                    for sel in items:
                        sel.user_data = items

            with dcg.TreeNode(C, label="Bullets"):

                dcg.Text(C, value="Bullet point 1", bullet=True)
                dcg.Text(C, value="Bullet point 2\nbullet text can be\nOn multiple lines", bullet=True)
                with dcg.TreeNode(C, label="Tree node"):
                    dcg.Text(C, value="Another bullet point", bullet=True)
                
                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value="1", bullet=True)
                    dcg.Button(C, label="Button", small=True)

            with dcg.TreeNode(C, label="Text"):

                with dcg.TreeNode(C, label="Colored Text"):
                    dcg.Text(C, value="Pink", color=(255, 0, 255))
                    dcg.Text(C, value="Yellow", color=(255, 255, 0))

                with dcg.TreeNode(C, label="Word Wrapping"):
                    paragraph1 = 'This text should automatically wrap on the edge of the window.The current implementation for the text wrapping follows simple rules suited for English and possibly other languages'
                    paragraph2 = 'The lazy dong is a good dog. This paragraph should fit within the child. Testing a 1 character word. The quick brown fox jumps over the lazy dog.'

                    dcg.Text(C, value=paragraph1, wrap=0)
                    widget_id = dcg.Slider(C, format="int", label="wrap width",
                                           value=500, max_value=1000, 
                                           callback=lambda s, t, d: t.user_data.configure(wrap=d))
                    widget_id.user_data = dcg.Text(C, value=paragraph2, wrap=500)

            with dcg.TreeNode(C, label="Text Input"):
                
                with dcg.TreeNode(C, label="Multi-line Text Input"):
                    paragraph = """/*\n
                        The Pentium F00F bug, shorthand for F0 0F C7 C8,\n
                        the hexadecimal encoding of one offending instruction,\n
                        more formally, the invalid operand with locked CMPXCHG8B\n
                        instruction bug, is a design flaw in the majority of\n
                        Intel Pentium, Pentium MMX, and Pentium OverDrive\n
                        processors (all in the P5 microarchitecture).\n
                        */\n\n
                        label:\n
                        \tlock cmpxchg8b eax\n"""

                    text_input = dcg.InputText(C, label="input text", multiline=True, value=paragraph, 
                                             height=300, callback=_log, tab_input=True)
                    ConfigureOptions(C, text_input, 1, "readonly", "on_enter")

                with dcg.TreeNode(C, label="Filtered Text Input"):
                    dcg.InputText(C, callback=_log, label="default")
                    dcg.InputText(C, callback=_log, label="decimal", decimal=True)
                    dcg.InputText(C, callback=_log, label="no blank", no_spaces=True)
                    dcg.InputText(C, callback=_log, label="uppercase", uppercase=True)
                    dcg.InputText(C, callback=_log, label="scientific", scientific=True)
                    dcg.InputText(C, callback=_log, label="hexdecimal", hexadecimal=True)

                with dcg.TreeNode(C, label="Password Input"):
                    password = dcg.InputText(C, label="password", password=True, callback=_log)
                    dcg.InputText(C, label="password (w/ hint)", password=True, hint="<password>", 
                                source=password, callback=_log)
                    dcg.InputText(C, label="password (clear)", source=password, callback=_log)

            with dcg.TreeNode(C, label="Simple Plots"):
                data = (0.6, 0.1, 1.0, 0.5, 0.92, 0.1, 0.2)
                dcg.SimplePlot(C, label="Frame Times", value=data)
                dcg.SimplePlot(C, label="Histogram", value=data, height=80, 
                             histogram=True, min_scale=0.0)

                data1 = []
                for i in range(70):
                    data1.append(cos(3.14*6*i/180))

                dcg.SimplePlot(C, label="Lines", value=data1, height=80)
                dcg.SimplePlot(C, label="Histogram", value=data1, height=80, histogram=True)
                
                with dcg.HorizontalLayout(C):
                    dcg.ProgressBar(C, label="Progress Bar", value=0.78, overlay="78%")
                    dcg.Text(C, value="Progress Bar")

                theme = dcg.ThemeColorImPlot(C, PlotHistogram=(255,0,0,255))
                dcg.ProgressBar(C, value=0.78, overlay="1367/1753", theme=theme)

            with dcg.TreeNode(C, label="Multi-component Widgets"):

                for i in range(2, 5):
                    with dcg.VerticalLayout(C):
                        float_source = dcg.InputValue(C, label=f"input float {i}",
                                                      min_value=0.0, max_value=100.0,
                                                      format="float", array_size=i)
                        dcg.Slider(C, label=f"drag float {i}", source=float_source,
                                   format="float", array_size=i, drag=True)
                        dcg.Slider(C, label=f"slider float {i}", source=float_source,
                                   format="float", array_size=i)

                    with dcg.VerticalLayout(C):
                        double_source = dcg.InputValue(C, label=f"input double {i}",
                                                       min_value=0.0, max_value=100.0,
                                                       format="double", array_size=i)
                        dcg.Slider(C, label=f"drag double {i}", source=double_source,
                                   format="double", array_size=i, drag=True)
                        dcg.Slider(C, label=f"slider double {i}", source=double_source,
                                   format="double", array_size=i)

                    with dcg.VerticalLayout(C):
                        int_source = dcg.InputValue(C, label=f"input int {i}",
                                                    min_value=0, max_value=100,
                                                    format="int", array_size=i)
                        dcg.Slider(C, label=f"drag int {i}", source=int_source,
                                   format="int", array_size=i, drag=True)
                        dcg.Slider(C, label=f"slider int {i}", source=int_source,
                                   format="int", array_size=i)

                    dcg.Spacer(C, height=10)

            with dcg.TreeNode(C, label="Vertical Sliders"):
                with dcg.HorizontalLayout(C):
                    dcg.Slider(C, label=" ", value=1, vertical=True,
                               max_value=5, height=160, format="int")
                    dcg.Slider(C, label=" ", value=1.0, vertical=True,
                               max_value=5.0, height=160, format="float")

                    with dcg.HorizontalLayout(C):
                        values = [0.0, 0.60, 0.35, 0.9, 0.70, 0.20, 0.0]

                        for i in range(7):
                            t = dcg.ThemeColorImGui(C,
                                    FrameBg=hsv(i/7.0, 0.5, 0.5),
                                    SliderGrab=hsv(i/7.0, 0.9, 0.9),
                                    FrameBgActive=hsv(i/7.0, 0.7, 0.5),
                                    FrameBgHovered=hsv(i/7.0, 0.6, 0.5))

                            dcg.Slider(C, label=" ", value=values[i],
                                       vertical=True, max_value=1.0, height=160,
                                       format="float", theme=t)

                        with dcg.VerticalLayout(C):
                            for i in range(3):
                                with dcg.HorizontalLayout(C):
                                    values = [0.20, 0.80, 0.40, 0.25]
                                    for j in range(4):
                                        dcg.Slider(C, label=" ", value=values[j],
                                                   vertical=True, max_value=1.0, height=50,
                                                   format="float")

                        with dcg.HorizontalLayout(C):
                            dcg.Slider(C, label=" ", vertical=True, max_value=1.0,
                                       height=160, width=40, format="float")
                            dcg.Slider(C, label=" ", vertical=True, max_value=1.0,
                                       height=160, width=40, format="float") 
                            dcg.Slider(C, label=" ", vertical=True, max_value=1.0,
                                       height=160, width=40, format="float")
                            dcg.Slider(C, label=" ", vertical=True, max_value=1.0,
                                       height=160, width=40, format="float")

            with dcg.TreeNode(C, label="Tree nodes"):

                dcg.TreeNode(C, label="Span text width", span_text_width=True)
                dcg.TreeNode(C, label="Span full width", span_full_width=True)

        with dcg.CollapsingHeader(C, label="Layout & Scrolling"):
            with dcg.TreeNode(C, label="Widgets Width"):
                
                dcg.Text(C, value="Width=100")
                dcg.Slider(C, label="float", width=100, format="float", drag=True)

                dcg.Text(C, value="Width=-100")
                dcg.Slider(C, label="float", width=-100, format="float", drag=True)

                dcg.Text(C, value="Width=-1")
                dcg.Slider(C, label="float", width=-1, format="float", drag=True)

                dcg.Text(C, value="group with width=75")
                with dcg.VerticalLayout(C, width=75):
                    dcg.Slider(C, label="float", format="float", drag=True) 
                    dcg.Slider(C, label="float", format="float", drag=True)
                    dcg.Slider(C, label="float", format="float", drag=True)

            with dcg.TreeNode(C, label="Basic Horizontal Layout"):

                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value="Normal buttons")
                    dcg.Button(C, label="Banana")
                    dcg.Button(C, label="Apple") 
                    dcg.Button(C, label="Corniflower")

                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value="Small buttons")
                    dcg.Button(C, label="Like this one", small=True)
                    dcg.Text(C, value="can fit within a text block")

                with dcg.HorizontalLayout(C, positions=(0, 150, 300)):
                    dcg.Text(C, value="Aligned")
                    dcg.Text(C, value="x=150")
                    dcg.Text(C, value="x=300")

                with dcg.HorizontalLayout(C, positions=(0, 150, 300)):
                    dcg.Text(C, value="Aligned")
                    dcg.Button(C, label="x=150", small=True)
                    dcg.Button(C, label="x=300", small=True)

                with dcg.HorizontalLayout(C):
                    dcg.Checkbox(C, label="My")
                    dcg.Checkbox(C, label="Tailor")
                    dcg.Checkbox(C, label="is")
                    dcg.Checkbox(C, label="rich")

                dcg.Text(C, value="Lists:")
                with dcg.HorizontalLayout(C):
                    dcg.ListBox(C, items=("AAAA", "BBBB", "CCCC", "DDDD"), value="AAAA", width=100, label="")
                    dcg.ListBox(C, items=("AAAA", "BBBB", "CCCC", "DDDD"), value="BBBB", width=100, label="")
                    dcg.ListBox(C, items=("AAAA", "BBBB", "CCCC", "DDDD"), value="CCCC", width=100, label="")
                    dcg.ListBox(C, items=("AAAA", "BBBB", "CCCC", "DDDD"), value="DDDD", width=100, label="")
                
                dcg.Text(C, value="Spacing(100):")
                with dcg.HorizontalLayout(C):
                    dcg.Button(C, label="A", width=50, height=50)
                    dcg.Spacer(C, width=100)
                    dcg.Button(C, label="B", width=50, height=50)

                dcg.Text(C, value="Right alignment:")
                with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.RIGHT):
                    dcg.Text(C, value="My")
                    dcg.Button(C, label="Tailor", small=True)
                    dcg.Text(C, value="is")
                    dcg.Button(C, label="rich", small=True)

                dcg.Text(C, value="Right alignment with fixed width:")
                with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.RIGHT, width=400):
                    dcg.Text(C, value="My")
                    dcg.Button(C, label="Tailor", small=True)
                    dcg.Text(C, value="is")
                    dcg.Button(C, label="rich", small=True)

                dcg.Text(C, value="Center alignment:")
                with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.CENTER):
                    dcg.Text(C, value="My")
                    dcg.Button(C, label="Tailor", small=True)
                    dcg.Text(C, value="is")
                    dcg.Button(C, label="rich", small=True)

                dcg.Text(C, value="Justified alignment:")
                with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.JUSTIFIED):
                    dcg.Text(C, value="My")
                    dcg.Button(C, label="Tailor", small=True)
                    dcg.Text(C, value="is")
                    dcg.Button(C, label="rich", small=True)

                dcg.Text(C, value="Wrapping:")
                with dcg.HorizontalLayout(C) as hl_wrapping:
                    for i in range(10):
                        dcg.Text(C, value="My")
                        dcg.Button(C, label="Tailor", small=True)
                        dcg.Text(C, value="is")
                        dcg.Button(C, label="rich", small=True)
                
                dcg.Checkbox(C, label="Wrapping", value=True, callback=lambda sender, target, data: hl_wrapping.configure(no_wrap=not(data)))

            with dcg.TreeNode(C, label="Ordered pack style"):
                dcg.Button(C, label="Button 1")
                dcg.Button(C, label="Button 2")
                dcg.Button(C, label="Button 3")

            with dcg.TreeNode(C, label="Absolute Position Placement"):
                dcg.Button(C, label="Set Button 2 Pos", 
                          callback=lambda: B2.configure(pos_to_window=(50, 125)))
                dcg.Button(C, label="Reset Button 2 Pos",
                          callback=lambda: B2.configure(pos_to_window=None))
                dcg.Button(C, label="Button 1", pos_to_window=(50,50), width=75, height=75)
                B2 = dcg.Button(C, label="Button 2", width=75, height=75)
                dcg.Button(C, label="Button 3")

            with dcg.TreeNode(C, label="Child Windows"):
                with dcg.ChildWindow(C, width=200, height=100, border=True):
                    for i in range(10):
                        dcg.Text(C, value=f"Scrolling Text {i}")
                with dcg.ChildWindow(C, width=200, height=100, border=True, horizontal_scrollbar=True):
                    for i in range(10):
                        dcg.Text(C, value=f"Scrolling Text {i}")

if __name__ == "__main__":
    C = dcg.Context()
    show_demo(C)
    C.viewport.initialize(title="DearCyGui Demo")
    while C.running:
        C.viewport.render_frame()