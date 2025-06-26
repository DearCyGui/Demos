import colorsys
import datetime
import dearcygui as dcg
import dearcygui.utils
from math import cos, sin
import os
import numpy as np
import time
import typing

# This file is a direct DearCyGui equivalent to the original DearPyGui demo.py

def hsv(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return r, g, b, 1.0

def _config(sender, target : dcg.uiItem):
    items = target.user_data

    if isinstance(sender, dcg.RadioButton):
        value = True
        keyword = target.value
    else:
        keyword = target.label
        value = target.value

    if isinstance(items, list):
        for item in items:
            setattr(item, keyword, value)
    else:
        item = items
        setattr(item, keyword, value)

def _table_flag_config(sender, target : dcg.baseItem, data):
    table : dcg.Table
    (table, flag) = target.user_data
    flags = table.flags
    if data:
        flags |= flag
    else:
        flags &= ~flag
    table.flags = flags

def _table_column_config(sender, target : dcg.baseItem, data):
    table : dcg.Table
    (table, column, attribute) = target.user_data
    setattr(table.col_config[column], attribute, data)

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

def add_help_symbol(target: dcg.uiItem, message: str):
    C = target.context
    with dcg.HorizontalLayout(C, parent=target.parent) as hl:
        target.parent = hl
        text_to_hover = dcg.Text(C, value="(?)", color=[0, 255, 0])
        with dcg.Tooltip(C, target=text_to_hover):
            dcg.Text(C, value=message)

def show_demo(C : dcg.Context):
    with dcg.Window(C, label="DearCyGui Demo",
                    width=800, height=800,
                    x=100, y=100) as __demo_id:
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

                    dcg.Slider(C, label="Slider Float")
                    dcg.InputValue(C, label="Input Int", print_format="%.0f", step=1)
                    dcg.Combo(C, items=("Yes", "No", "Maybe"), label="Combo")

            with dcg.Menu(C, label="Tools"):
                dcg.MenuItem(C, label="Show Metrics", callback=lambda: dcg.utils.MetricsWindow(C))
                dcg.MenuItem(C, label="Show Style editor", callback=lambda: dcg.utils.StyleEditor(C))
                dcg.MenuItem(C, label="Show Debug", callback=lambda: dcg.utils.ItemInspecter(C))

            with dcg.Menu(C, label="Settings"):
                dcg.MenuItem(C, label="Wait For Input", check=True, callback=lambda s, t, d: C.viewport.configure(wait_for_input=d))
                dcg.MenuItem(C, label="Vsync", check=True, callback=lambda s, t, d: C.viewport.configure(vsync=d))
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
                    dcg.Button(C, label="Arrow Button", callback=_log, arrow=dcg.ButtonDirection.UP)
                    for direction in [dcg.ButtonDirection.LEFT, dcg.ButtonDirection.RIGHT, dcg.ButtonDirection.DOWN]:
                        dcg.Button(C, callback=_log, arrow=direction)

                dcg.Button(C, label="Repeat Button", callback=_log, repeat=True)
                dcg.Checkbox(C, label="checkbox", callback=_log)
                dcg.RadioButton(C, items=["radio a", "radio b", "radio c"], horizontal=True, callback=_log)
                dcg.Selectable(C, label="selectable", callback=_log)

                with dcg.HorizontalLayout(C):
                    for i in range(7):
                        with dcg.ThemeList(C) as theme:
                            dcg.ThemeColorImGui(C,
                                                button=hsv(i/7.0, 0.6, 0.6),
                                                button_hovered=hsv(i/7.0, 0.7, 0.7),
                                                button_active=hsv(i/7.0, 0.8, 0.8))
                            dcg.ThemeStyleImGui(C,
                                                frame_rounding=i*5,
                                                frame_padding=(i*3, i*3))
                        dcg.Button(C, label="Click", callback=_log, theme=theme)

                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value="Counter: ")
                    counter = dcg.Text(C, value="0")
                    dcg.Button(C, arrow=dcg.ButtonDirection.LEFT, 
                             callback=lambda: counter.configure(value=str(int(counter.value)-1)))
                    dcg.Button(C, arrow=dcg.ButtonDirection.RIGHT,
                             callback=lambda: counter.configure(value=str(int(counter.value)+1)))

                dcg.Separator(C)
                
                text_to_hover = dcg.Text(C, value="hover me")
                with dcg.Tooltip(C, target=text_to_hover):
                    dcg.Text(C, value="I'm a tooltip!")

                dcg.Separator(C, label="This is a separator with text")

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
                dcg.InputValue(C, label="input int", print_format="%.0f", callback=_log, step=1)
                dcg.InputValue(C, label="input float", print_format="%.3f", callback=_log)
                dcg.InputValue(C, label="input scientific", print_format="%e", callback=_log)

                dcg.utils.InputValueN(C, label="input floatx", callback=_log, value=[1,2,3,4], width="fillx")
                dcg.InputValue(C, label="input double", print_format="%.14f", callback=_log)
                dcg.utils.InputValueN(C, label="input doublex", print_format="%.14f", callback=_log, values=[1,2,3,4], width="fillx")

                drag_int = dcg.Slider(C, label="drag int", print_format="%.0f", drag=True, callback=_log)
                add_help_symbol(drag_int, 
                    "Click and drag to edit value.\n"
                    "Hold SHIFT/ALT for faster/slower edit.\n"
                    "Double-click or CTRL+click to input value.")
                
                dcg.Slider(C, label="drag int 0..100", print_format="%.0f%%", drag=True, callback=_log)
                dcg.Slider(C, label="drag float", drag=True, callback=_log)
                dcg.Slider(C, label="drag small float",
                           print_format="%.06f ns", drag=True, value=0.0067, callback=_log)

                slider_int = dcg.Slider(C, label="slider int", print_format="%.0f", max_value=3, callback=_log)
                add_help_symbol(slider_int, "CTRL+click to enter value.")
                
                dcg.Slider(C, label="slider float", print_format="ratio = %.3f", max_value=1.0, callback=_log)
                dcg.Slider(C, label="slider double", print_format="ratio = %.14f", max_value=1.0, callback=_log)
                dcg.Slider(C, label="slider angle",  print_format="%.0f deg", min_value=-360, max_value=360, callback=_log)

                add_help_symbol(dcg.ColorEdit(C, label="color edit 4", value=(102, 179, 0, 128), callback=_log),
                    "Click on the colored square to open a color picker.\n"
                    "Click and hold to use drag and drop.\n"
                    "Right-click on the colored square to show options.\n"
                    "CTRL+click on individual component to input value.")

                dcg.ColorEdit(C, label="color edit floats", value=(.5, 1, .25, .1), callback=_log)
                
                dcg.ListBox(C, items=("Apple", "Banana", "Cherry", "Kiwi", "Mango", "Orange", "Pineapple", 
                                     "Strawberry", "Watermelon"), label="listbox", num_items_shown_when_open=4, callback=_log)
                dcg.ColorButton(C, value=(255, 0, 0, 255), label="color button", callback=_log)

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
                                label="Color Picker", alpha_preview="full",
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
                    dcg.RadioButton(C, items=("uint8",
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
                dcg.InputValue(C, print_format="%.0f", label="num_items", step=1,
                               callback=_config, user_data=[listbox_1, listbox_2], before = listbox_1)
                dcg.Slider(C, print_format="%.0f", label="width",
                           value=200, callback=_config, user_data=listbox_2,
                           before = listbox_1, max_value=500)

            with dcg.TreeNode(C, label="Selectables"):
                with dcg.TreeNode(C, label="Basic"):
                    dcg.Selectable(C, label="1. I am selectable")
                    dcg.Text(C, value="2. I am not selectable") 

                with dcg.TreeNode(C, label="Selection State: Single"):
                    selectables : list[dcg.Selectable] = []
                    # unselect the other selectables
                    def _selection(sender):
                        for item in selectables:
                            if item != sender:
                                item.value = False
                    
                    for i in range(5):
                        selectables.append(
                            dcg.Selectable(C, label=f"{i+1}. I am selectable", callback=_selection)
                        )
                    for sel in selectables:
                        sel.user_data = selectables

            with dcg.TreeNode(C, label="Bullets"):

                dcg.Text(C, value="Bullet point 1", marker="bullet")
                dcg.Text(C, value="Bullet point 2\nbullet text can be\nOn multiple lines", marker="bullet")
                with dcg.TreeNode(C, label="Tree node"):
                    dcg.Text(C, value="Another bullet point", marker="bullet")
                
                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value="1", marker="bullet")
                    dcg.Button(C, label="Button", small=True)

            with dcg.TreeNode(C, label="Text"):

                with dcg.TreeNode(C, label="Colored Text"):
                    dcg.Text(C, value="Pink", color=(255, 0, 255))
                    dcg.Text(C, value="Yellow", color=(255, 255, 0))

                with dcg.TreeNode(C, label="Word Wrapping"):
                    paragraph1 = 'This text should automatically wrap on the edge of the window.The current implementation for the text wrapping follows simple rules suited for English and possibly other languages'
                    paragraph2 = 'The lazy dong is a good dog. This paragraph should fit within the child. Testing a 1 character word. The quick brown fox jumps over the lazy dog.'

                    dcg.Text(C, value=paragraph1, wrap=0)
                    widget_id = dcg.Slider(C, print_format="%.0f", label="wrap width",
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
                    ConfigureOptions(C, text_input, 1, "readonly", "callback_on_enter")

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
                                  shareable_value=password.shareable_value, callback=_log)
                    dcg.InputText(C, label="password (clear)",
                                  shareable_value=password.shareable_value, callback=_log)

            with dcg.TreeNode(C, label="Simple Plots"):
                # Simple plots are simplified plotting widgets
                # that are core to imgui, while dcg.Plot is from
                # the advanced implot.
                data = (0.6, 0.1, 1.0, 0.5, 0.92, 0.1, 0.2)
                dcg.SimplePlot(C, label="Frame Times", value=data)
                dcg.SimplePlot(C, label="Histogram", value=data, height=80, 
                             histogram=True, scale_min=0.0)

                data1 = np.cos(np.pi/30 * np.arange(70))

                dcg.SimplePlot(C, label="Lines", value=data1, height=80)
                dcg.SimplePlot(C, label="Histogram", value=data1, height=80, histogram=True)
                
                with dcg.HorizontalLayout(C):
                    dcg.ProgressBar(C, label="Progress Bar", value=0.78, overlay="78%")
                    dcg.Text(C, value="Progress Bar")

                dcg.ProgressBar(C, value=0.78, overlay="1367/1753")

            with dcg.TreeNode(C, label="Multi-component Widgets"):

                for i in range(2, 5):
                    with dcg.VerticalLayout(C):
                        float_source = \
                            dcg.utils.InputValueN(
                                C,
                                label=f"input float {i}",
                                min_value=0.0, max_value=100.0,
                                value=[0.0] * i)
                        dcg.utils.SliderN(C, label=f"drag float {i}",
                                          shareable_values=float_source.shareable_values,
                                          drag=True)
                        dcg.utils.SliderN(C, label=f"slider float {i}",
                                          shareable_values=float_source.shareable_values)

                    with dcg.VerticalLayout(C):
                        int_source = \
                            dcg.utils.InputValueN(
                                C,
                                label=f"input int {i}", step=1,
                                min_value=0, max_value=100,
                                print_format="%.0f")
                        dcg.utils.SliderN(C, label=f"drag int {i}",
                                          shareable_values=int_source.shareable_values,
                                          print_format="%.0f", drag=True)
                        dcg.utils.SliderN(C, label=f"slider int {i}",
                                          shareable_values=int_source.shareable_values,
                                          print_format="%.0f")

                    dcg.Spacer(C, height=10)

            with dcg.TreeNode(C, label="Vertical Sliders"):
                with dcg.HorizontalLayout(C):
                    dcg.Slider(C, label=" ", value=1, vertical=True, width=20,
                               max_value=5, height=160, print_format="%.0f")
                    dcg.Slider(C, label=" ", value=1.0, vertical=True, width=20,
                               max_value=5.0, height=160)

                    with dcg.HorizontalLayout(C):
                        values = [0.0, 0.60, 0.35, 0.9, 0.70, 0.20, 0.0]

                        for i in range(7):
                            t = dcg.ThemeColorImGui(C,
                                    frame_bg=hsv(i/7.0, 0.5, 0.5),
                                    slider_grab=hsv(i/7.0, 0.9, 0.9),
                                    frame_bg_active=hsv(i/7.0, 0.7, 0.5),
                                    frame_bg_hovered=hsv(i/7.0, 0.6, 0.5))

                            dcg.Slider(C, label=" ", value=values[i], width=20,
                                       vertical=True, max_value=1.0, height=160,
                                       theme=t)

                        with dcg.VerticalLayout(C):
                            for i in range(3):
                                with dcg.HorizontalLayout(C):
                                    values = [0.20, 0.80, 0.40, 0.25]
                                    for j in range(4):
                                        dcg.Slider(C, label=" ", value=values[j], width=20,
                                                   vertical=True, max_value=1.0, height=50)

                        with dcg.HorizontalLayout(C):
                            dcg.Slider(C, label=" ", vertical=True, max_value=1.0,
                                       height=160, width=40)
                            dcg.Slider(C, label=" ", vertical=True, max_value=1.0,
                                       height=160, width=40) 
                            dcg.Slider(C, label=" ", vertical=True, max_value=1.0,
                                       height=160, width=40)
                            dcg.Slider(C, label=" ", vertical=True, max_value=1.0,
                                       height=160, width=40)
            with dcg.TreeNode(C, label="Time/Date widgets"):
                def _log_time(sender, target, value):
                    print(f"Time/Date changed: {value}")
                
                with dcg.TreeNode(C, label="Time Picker"):
                    with dcg.HorizontalLayout(C):
                        time_picker = dcg.utils.TimePicker(C, label="time", callback=_log_time)
                        with dcg.VerticalLayout(C):
                            ConfigureOptions(C, time_picker, 1, 
                                          "use_24hr", "show_seconds")

                with dcg.TreeNode(C, label="Date Picker"):
                    # Main date picker with options
                    with dcg.HorizontalLayout(C):
                        date_picker = dcg.utils.DatePicker(C, label="date", 
                                                             callback=_log_time,
                                                             layout="vertical")
                        '''
                        with dcg.VerticalLayout(C):
                            # Demonstration of various DatePicker options
                            dcg.Text(C, value="DatePicker Options:")
                            ConfigureOptions(C, date_picker, 1, 
                                          "no_header", "no_calendar",
                                          "no_year_nav", "no_scrollbar")
                        '''

                    # Create date range controls
                    with dcg.VerticalLayout(C):
                        dcg.Text(C, value="Date Range Controls:")
                        
                        def update_date_range(sender: dcg.InputText, target, value):
                            new_date = datetime.datetime.strptime(value, "%Y-%m-%d")
                            if sender.label == "min_date":
                                date_picker.min_date = new_date
                            else:
                                date_picker.max_date = new_date

                        dcg.InputText(C, label="min_date", value="1970-01-01",
                                    callback=update_date_range)
                        dcg.InputText(C, label="max_date", value="2999-12-31",
                                    callback=update_date_range)

            with dcg.TreeNode(C, label="Tree nodes"):

                dcg.TreeNode(C, label="Span text width", span_text_width=True)
                dcg.TreeNode(C, label="Span full width", span_full_width=True)

        with dcg.CollapsingHeader(C, label="Layout & Scrolling"):
            with dcg.TreeNode(C, label="Widgets Width"):
                
                dcg.Text(C, value="Width=100")
                dcg.Slider(C, label="float", width=100, drag=True)

                dcg.Text(C, value="Width=-100")
                dcg.Slider(C, label="float", width=-100, drag=True)

                dcg.Text(C, value="Width=-1")
                dcg.Slider(C, label="float", width=-1, drag=True)

                dcg.Text(C, value="group with width=75")
                with dcg.VerticalLayout(C, width=75):
                    dcg.Slider(C, label="float", drag=True) 
                    dcg.Slider(C, label="float", drag=True)
                    dcg.Slider(C, label="float", drag=True)

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
                window = __demo_id
                dcg.Button(C, label="Set Button 2 Pos", 
                           callback=lambda: B2.configure(x=window.x + "50 * dpi",
                                                         y=window.y + "125 * dpi"))
                dcg.Button(C, label="Reset Button 2 Pos",
                           callback=lambda: B2.configure(x=0, y=0))
                dcg.Button(C, label="Button 1", x="window.x1 + 50 * dpi",
                           y="window.y1 + 50 * dpi", width=75, height=75)
                B2 = dcg.Button(C, label="Button 2", width=75, height=75)
                dcg.Button(C, label="Button 3")

            with dcg.TreeNode(C, label="Grid Layout using Table API"):
                dcg.Text(C, value="Tables can be used to layout items in an equally spaced grid pattern.")
                dcg.Text(C, value="Layout items are preferred for simple use-cases")
                dcg.Text(C, value="See tables section for more detail on tables.")
                table_grid_layout_demo = \
                    dcg.Table(C,
                              flags=dcg.TableFlag.RESIZABLE | \
                                    dcg.TableFlag.BORDERS_INNER_H | \
                                    dcg.TableFlag.BORDERS_OUTER_H | \
                                    dcg.TableFlag.BORDERS_INNER_V | \
                                    dcg.TableFlag.BORDERS_OUTER_V)
                with table_grid_layout_demo.next_row:
                    dcg.Button(C, label="Button 1")
                    dcg.Button(C, label="Button 2")
                    dcg.Button(C, label="Button 3")
                with table_grid_layout_demo.next_row:
                    dcg.Spacer(C)
                    dcg.Button(C, label="Button 4")
                    dcg.Button(C, label="Button 5")
                
                dcg.Checkbox(C,
                             label="resizable",
                             value=True,
                             callback=_table_flag_config,
                             user_data=(table_grid_layout_demo, dcg.TableFlag.RESIZABLE))
                dcg.Checkbox(C,
                             label="borders_innerH",
                             value=True,
                             callback=_table_flag_config,
                             user_data=(table_grid_layout_demo, dcg.TableFlag.BORDERS_INNER_H))
                dcg.Checkbox(C,
                             label="borders_outerH",
                             value=True,
                             callback=_table_flag_config,
                             user_data=(table_grid_layout_demo, dcg.TableFlag.BORDERS_OUTER_H))
                dcg.Checkbox(C,
                             label="borders_innerV",
                             value=True,
                             callback=_table_flag_config,
                             user_data=(table_grid_layout_demo, dcg.TableFlag.BORDERS_INNER_V))
                dcg.Checkbox(C,
                             label="borders_outerV",
                             value=True,
                             callback=_table_flag_config,
                             user_data=(table_grid_layout_demo, dcg.TableFlag.BORDERS_OUTER_V))

            with dcg.TreeNode(C, label="Child Windows"):
                with dcg.ChildWindow(C, width=200, height=100, border=True):
                    for i in range(10):
                        dcg.Text(C, value=f"Scrolling Text {i}")
                with dcg.ChildWindow(C, width=200, height=100, border=True, horizontal_scrollbar=True):
                    for i in range(10):
                        dcg.Text(C, value=f"Scrolling Text {i}")

            with dcg.TreeNode(C, label="Containers"):
                with dcg.TreeNode(C, label="Tree Nodes"):
                    with dcg.TreeNode(C, label="Tree Node (selectable)", selectable=True):
                        dcg.Button(C, label="Button 1")
                        dcg.Button(C, label="Button 2") 
                        dcg.Button(C, label="Button 3")
                    with dcg.TreeNode(C, label="Tree Node (bullet)", bullet=True):
                        dcg.Button(C, label="Button 1")
                        dcg.Button(C, label="Button 2")
                        dcg.Button(C, label="Button 3")

                with dcg.TreeNode(C, label="Groups"):
                    dcg.Text(C, value="Groups are used to control child items placement, width, and provide a hit box for things like is the set of items are hovered, etc...")
                    with dcg.HorizontalLayout(C):
                        dcg.Button(C, label="Button 1")
                        dcg.Button(C, label="Button 2")
                        dcg.Button(C, label="Button 3") 
                    with dcg.VerticalLayout(C, width=150):
                        dcg.Button(C, label="Button 1")
                        dcg.Button(C, label="Button 2")
                        dcg.Button(C, label="Button 3")
                    with dcg.VerticalLayout(C):
                        dcg.Button(C, label="Button 1")
                        dcg.Button(C, label="Button 2")
                        dcg.Button(C, label="Button 3")

                with dcg.TreeNode(C, label="Child windows"):
                    dcg.Text(C, value="Child windows are basically embedded windows and provide much more structure and control of the containing items than groups.")
                    
                    demo_layout_child = dcg.ChildWindow(C, width=200, height=200, border=True)
                    with dcg.HorizontalLayout(C):
                        dcg.Checkbox(C, label="auto_resize_x", callback=_config, user_data=demo_layout_child)
                        dcg.Checkbox(C, label="auto_resize_y", callback=_config, user_data=demo_layout_child)
                        dcg.Checkbox(C, label="menubar", callback=_config, user_data=demo_layout_child)
                        dcg.Checkbox(C, label="no_scrollbar", callback=_config, user_data=demo_layout_child)
                        dcg.Checkbox(C, label="horizontal_scrollbar", callback=_config, user_data=demo_layout_child)
                        dcg.Checkbox(C, label="border", value=True, callback=_config, user_data=demo_layout_child)

                    with demo_layout_child:
                        with dcg.MenuBar(C):
                            with dcg.Menu(C, label="Menu"):
                                pass
                        for i in range(20):
                            dcg.Text(C, value="A pretty long sentence if you really think about it. It's also pointless. we need this to be even longer")

                    with dcg.ChildWindow(C, auto_resize_x=True, height=130, menubar=True):
                        with dcg.MenuBar(C):
                            dcg.Menu(C, label="Menu Options")
                        dcg.Button(C, label="Button 1")
                        dcg.Button(C, label="Button 2")
                        dcg.Button(C, label="Button 3")

                    with dcg.HorizontalLayout(C):
                        with dcg.ChildWindow(C, width=100, height=150, horizontal_scrollbar=True):
                            dcg.Button(C, label="Button 1")
                            dcg.Button(C, label="Button 2")
                            dcg.Button(C, label="Button 3")
                            dcg.Button(C, label="Button 4", width=150)
                            dcg.Button(C, label="Button 5")
                            dcg.Button(C, label="Button 6")
                        with dcg.ChildWindow(C, width=100, height=110):
                            dcg.Button(C, label="Button 1")
                            dcg.Button(C, label="Button 2")
                            dcg.Button(C, label="Button 3")

                with dcg.TreeNode(C, label="Collapsing Headers"):
                    with dcg.CollapsingHeader(C, label="Collapsing Header"):
                        dcg.Button(C, label="Button 1")
                        dcg.Button(C, label="Button 2")
                        dcg.Button(C, label="Button 3")
                    with dcg.CollapsingHeader(C, label="Collapsing Header (close)", closable=True):
                        dcg.Button(C, label="Button 1")
                        dcg.Button(C, label="Button 2")
                        dcg.Button(C, label="Button 3")
                    with dcg.CollapsingHeader(C, label="Collapsing Header (bullet)", bullet=True):
                        dcg.Button(C, label="Button 1")
                        dcg.Button(C, label="Button 2")
                        dcg.Button(C, label="Button 3")
                    with dcg.CollapsingHeader(C, label="Collapsing Header (leaf)", leaf=True):
                        dcg.Button(C, label="Button 1")
                        dcg.Button(C, label="Button 2")
                        dcg.Button(C, label="Button 3")

                with dcg.TreeNode(C, label="Tabs"):
                    with dcg.TreeNode(C, label="Basic"):
                        with dcg.TabBar(C):
                            with dcg.Tab(C, label="Avocado"):
                                dcg.Text(C, value="This is the avocado tab!")
                            with dcg.Tab(C, label="Broccoli"):
                                dcg.Text(C, value="This is the broccoli tab!")
                            with dcg.Tab(C, label="Cucumber"):
                                dcg.Text(C, value="This is the cucumber tab!")

                    with dcg.TreeNode(C, label="Advanced"):
                        tb = dcg.TabBar(C)
                        with tb:
                            with dcg.Tab(C, label="tab 1"):
                                dcg.Text(C, value="This is the tab 1!")
                            t2 = dcg.Tab(C, label="tab 2") 
                            with t2:
                                dcg.Text(C, value="This is the tab 2!")
                            with dcg.Tab(C, label="tab 3"):
                                dcg.Text(C, value="This is the tab 3!")
                            with dcg.Tab(C, label="tab 4"):
                                dcg.Text(C, value="This is the tab 4!")

                            tbb = dcg.TabButton(C, label="+")
                            dcg.TabButton(C, label="?")

                            # Controls before the tab bar
                            dcg.Checkbox(C, label="tab bar reorderable", callback=_config, user_data=tb, before=tb)
                            dcg.Checkbox(C, label="tab 2 no_reorder", callback=_config, user_data=t2, before=tb)
                            dcg.Checkbox(C, label="tab 2 leading", callback=_config, user_data=t2, before=tb) 
                            dcg.Checkbox(C, label="tab 2 trailing", callback=_config, user_data=t2, before=tb)
                            dcg.Checkbox(C, label="tab button trailing", callback=_config, user_data=tbb, before=tb)
                            dcg.Checkbox(C, label="tab button leading", callback=_config, user_data=tbb, before=tb)

            with dcg.TreeNode(C, label="Simple Layouts"):
                dcg.Text(C, value="Containers can be nested for advanced layout options")
                with dcg.ChildWindow(C, width=500, height=320, menubar=True):
                    with dcg.MenuBar(C):
                        dcg.Menu(C, label="Menu Options")
                    with dcg.ChildWindow(C, auto_resize_x=True, height=95):
                        with dcg.HorizontalLayout(C):
                            dcg.Button(C, label="Header 1", width=75, height=75)
                            dcg.Button(C, label="Header 2", width=75, height=75)
                            dcg.Button(C, label="Header 3", width=75, height=75)
                    with dcg.ChildWindow(C, auto_resize_x=True, height=175):
                        with dcg.HorizontalLayout(C, width=0):
                            with dcg.ChildWindow(C, width=102, height=150):
                                with dcg.TreeNode(C, label="Nav 1"):
                                    dcg.Button(C, label="Button 1")
                                with dcg.TreeNode(C, label="Nav 2"):
                                    dcg.Button(C, label="Button 2")
                                with dcg.TreeNode(C, label="Nav 3"):
                                    dcg.Button(C, label="Button 3")
                            with dcg.ChildWindow(C, width=300, height=150):
                                dcg.Button(C, label="Button 1")
                                dcg.Button(C, label="Button 2")
                                dcg.Button(C, label="Button 3")
                            with dcg.ChildWindow(C, width=50, height=150):
                                dcg.Button(C, label="B1", width=25, height=25)
                                dcg.Button(C, label="B2", width=25, height=25)
                                dcg.Button(C, label="B3", width=25, height=25)
                    with dcg.HorizontalLayout(C):
                        dcg.Button(C, label="Footer 1", width=175)
                        dcg.Text(C, value="Footer 2")
                        dcg.Button(C, label="Footer 3", width=175)

        with dcg.CollapsingHeader(C, label="Textures & Images"):
            with dcg.TreeNode(C, label="Help"):
                dcg.Separator(C)
                dcg.Text(C, value="ABOUT TEXTURES:")
                dcg.Text(C, value="Textures are buffers of RGBA data.", marker="bullet", x=20)
                dcg.Text(C, value="Textures are used by 'image based' widgets:", marker="bullet", x=20) 
                dcg.Text(C, value="Image", marker="bullet", x=50)
                dcg.Text(C, value="DrawImage", marker="bullet", x=50)
                dcg.Text(C, value="Textures can be assigned a dynamic hint", marker="bullet", x=20)
                dcg.Text(C, value="The dynamic hint helps GPU placement to optimize \n"
                                  "for fast upload (but possibly slower GPU access)", marker="bullet", x=20)
                dcg.Text(C, value="When their value are set, the content is uploaded right away to the GPU", marker="bullet", x=20)
                dcg.Text(C, value="Resizing is allowed but requires a sync, prefer allocating a new texture", marker="bullet", x=20)
                dcg.Text(C, value="Available format are R, RG, RGB, RGBA", marker="bullet", x=20)
                dcg.Text(C, value="They can be stored as uint8 or float32 (in that case data must be between 0 and 1)", marker="bullet", x=20)

                dcg.Separator(C)
                dcg.Text(C, value="PROGRAMMER GUIDE:")
                dcg.Text(C, value="'image based' widgets hold a reference to a texture widget.", marker="bullet", x=20)
                dcg.Text(C, value="Deleting the texture widget will not affect widget's using it.", marker="bullet", x=50)
                dcg.Text(C, value="Textures are only free'd from the GPU when the reference count reaches 0.", marker="bullet", x=50)
                dcg.Separator(C)

            with dcg.TreeNode(C, label="Textures"):

                # Creating RGB textures
                # Arrays are preferred as they can be easily copied
                # without conversion to the textures. Slices of arrays
                # can be used as well.
                texture_data1 = np.empty([100, 100, 3], dtype=np.uint8)
                texture_data2 = np.empty([50, 50, 3], dtype=np.uint8)
                texture_data3 = np.empty([100, 100, 3], dtype=np.uint8)
                texture_data1[:, :] = [255, 0, 255]
                texture_data2[:, :] = [255, 255, 0]
                texture_data3[:50, :50] = [255, 0, 0]
                texture_data3[:50, 50:] = [0, 255, 0]
                texture_data3[50:, :50] = [0, 0, 255]
                texture_data3[50:, 50:] = [255, 255, 0]

                __demo_static_texture_1 = dcg.Texture(C, texture_data1)
                __demo_static_texture_2 = dcg.Texture(C, texture_data2)
                __demo_static_texture_3 = dcg.Texture(C, texture_data3)
                # Note: we could pass dynamic=True, but it is optional
                __demo_dynamic_texture = dcg.Texture(C, texture_data1)
                # Textures are uploaded right away, thus modifying texture_data
                # will not affect the texture

                with dcg.HorizontalLayout(C):

                    with dcg.VerticalLayout(C):
                        dcg.Text(C, value="Image Button")
                        dcg.Image(C, button=True, texture=__demo_static_texture_1)

                    with dcg.VerticalLayout(C):
                        dcg.Text(C, value="Image")
                        dcg.Image(C, texture=__demo_static_texture_2)

                    with dcg.VerticalLayout(C):
                        dcg.Text(C, value="Image (texture size)")
                        dcg.Image(C, texture=__demo_static_texture_3)

                    with dcg.VerticalLayout(C):
                        dcg.Text(C, value="Image (2x texture size)")
                        dcg.Image(C, texture=__demo_static_texture_3, width=200, height=200)

                    with dcg.VerticalLayout(C):
                        dcg.Text(C, value="Dynamic Image")
                        # Note: RenderHandler will call the callback only when
                        # the texture is being rendered, that is when the
                        # Texture treenode is opened.
                        def update_dynamic_texture():
                            factor = (sin(time.time()) + 1) / 2.
                            texture_data = factor * np.float32(texture_data1) + (1 - factor) * np.float32(texture_data3)
                            texture_data = np.uint8(texture_data)
                            __demo_dynamic_texture.set_value(texture_data)
                            C.viewport.wake() # Prevent not refreshing
                        dcg.Image(C,
                                  texture=__demo_dynamic_texture,
                                  handlers = dcg.RenderHandler(C,
                                                callback=update_dynamic_texture))

                if C.viewport.font is not None:
                    # Note: C.viewport.font is filled during initialize()
                    # if you didn't set one.
                    dcg.Text(C, value="Current font Texture")
                    current_font = typing.cast(dcg.AutoFont, C.viewport.font)
                    one_font_level = current_font.fonts[0]
                    font_texture = one_font_level.texture
                    dcg.Image(C, texture=font_texture.texture)

                dcg.Text(C, value="Textures in a plot:")
                with dcg.Plot(C, width=500, height=300, equal_aspects=True) as plot_1:
                    plot_1.Y1.invert = True
                    # DearPyGui's image series are replaced by the more flexible
                    # DrawInPlot which enables to reuse DrawImage.
                    with dcg.DrawInPlot(C, no_legend=False, label="Images"): # no_legend is True by default for DrawInPlot
                        # DrawImage enables to set the corner positions using various ways
                        dcg.DrawImage(C, texture=__demo_static_texture_1, pmin=(0, 100), pmax=(100, 200))
                        # p1, p2, p3, p4: coordinates of the corners
                        # uv1, uv2, uv3, uv4: coordinates of the corresponding texture corners
                        # You will notice that the texture is not stretched uniformly
                        # but by pieces, this is due to the fact internally the rendering
                        # is performed using triangles.
                        dcg.DrawImage(C, texture=__demo_static_texture_3,
                                      p1=(200, 100), p2=(150, 150), p3=(200, 200), p4=(300, 150),
                                      uv1=(0.5, 0), uv2=(0, 0.5), uv3=(0.5, 1.), uv4=(1., 0.5))
                        # Note: rounding requires parallel to the axes
                        dcg.DrawImage(C, texture=__demo_dynamic_texture, pmin=(350, 100), pmax=(450, 200), rounding=10)

        with dcg.CollapsingHeader(C, label="Popups & Modal Windows"):
            with dcg.TreeNode(C, label="Popups"):

                popup_values = ["Bream", "Haddock", "Mackerel", "Pollock", "Tilefish"]

                dcg.Text(C, value="This is a light wrapper over a window.", marker="bullet")
                dcg.Text(C, value="By default a popup will shrink fit the items it contains. This is useful for context windows, and simple modal window popups.", marker="bullet")
                dcg.Text(C, value="When a popup is active, it inhibits interacting with windows that are behind the popup. Clicking outside the popup closes it.", marker="bullet")
            
                with dcg.HorizontalLayout(C):
                    def popup_open_callback(sender):
                        with dcg.Window(C, popup=True):
                            dcg.Text(C, value="Aquariam") 
                            dcg.Separator(C)
                            for i in popup_values:
                                dcg.Selectable(C,
                                               label=i,
                                               callback=lambda s: sender.user_data.configure(value=s.label))
                    b = dcg.Button(C, label="Click me", callback=popup_open_callback)
                    t = dcg.Text(C, value="<None>")
                    b.user_data = t

                dcg.Text(C, value="A Popup with minimum size and no_move", marker="bullet")
                with dcg.HorizontalLayout(C):
                    def popup_open_callback2(sender):
                        with dcg.Window(C, popup=True, no_move=True, min_size=(300,400)):
                            dcg.Text(C, value="Aquariam") 
                            dcg.Separator(C)
                            for i in popup_values:
                                dcg.Selectable(C,
                                               label=i,
                                               callback=lambda s: sender.user_data.configure(value=s.label))
                    b = dcg.Button(C, label="Click me", callback=popup_open_callback2)
                    t = dcg.Text(C, value="<None>")
                    b.user_data = t

            with dcg.TreeNode(C, label="Modals"):
                dcg.Text(C, value="Modal windows are like popups but the user cannot close them by clicking outside.")
                def modal_open_callback():
                    with dcg.Window(C, modal=True) as modal_popup:
                        dcg.Text(C, value="All those beautiful files will be deleted.\nThis operation cannot be undone!")
                        dcg.Separator(C)
                        dcg.Checkbox(C, label="Don't ask me next time")
                        with dcg.HorizontalLayout(C):
                            dcg.Button(C, label="OK", width=75, 
                                callback=lambda: modal_popup.configure(show=False))
                            dcg.Button(C, label="Cancel", width=75,
                                callback=lambda: modal_popup.configure(show=False))
                b = dcg.Button(C, label="Click me", callback=modal_open_callback)

            with dcg.TreeNode(C, label="File/Directory Selector"):
                dcg.Text(C, value="Demonstration of OS file dialogs")
                dcg.Text(C, value="Note: Paths are returned in a list passed to the callback", marker="bullet")

                def _log_paths(paths):
                    print(f"Selected paths: {paths}")

                dcg.Button(C, label="Show File Open Dialog", 
                             callback=lambda: dcg.os.show_open_file_dialog(C, _log_paths))
                dcg.Button(C, label="Show File Open Dialog (multiple files selectable)", 
                             callback=lambda: dcg.os.show_open_file_dialog(C, _log_paths, allow_multiple_files=True))
                dcg.Button(C, label="Show File Open Dialog (with filters, etc)", 
                             callback=lambda: dcg.os.show_open_file_dialog(C,
                                                                        _log_paths,
                                                                        allow_multiple_files=True,
                                                                        filters=[("Python", "py;pyw"), ("All Files", "*")],
                                                                        default_location=os.path.dirname(__file__),
                                                                        title="Please pick a file",
                                                                        accept="Yes",
                                                                        cancel="No"))
                dcg.Button(C, label="Show File Save Dialog",
                             callback=lambda: dcg.os.show_save_file_dialog(C, _log_paths))
                dcg.Button(C, label="Show Folder Dialog",
                             callback=lambda: dcg.os.show_open_folder_dialog(C, _log_paths))
                dcg.Button(C, label="Show Folder Dialog (multiple directories selectable)",
                             callback=lambda: dcg.os.show_open_folder_dialog(C, _log_paths, allow_multiple_files=True))

        with dcg.CollapsingHeader(C, label="Tooltips"):
            dcg.Text(C, value="Tooltips are floating windows that appear on hovering. Tooltips can be \n"
                        "attached to any item that is hovered. By default, a tooltip is attached to \n"
                        "the previously created item, but the target field enables to target \n"
                        "any item.")

            dcg.Separator(C)

            # Basic tooltips
            dcg.Text(C, value="Basic tooltip")
            with dcg.Tooltip(C):
                dcg.Text(C, value="I'm displayed when hovering the 'Basic tooltip' text")

            dcg.Separator(C)

            # You can add delay before showing
            dcg.Text(C, value="Tooltip with delay")
            with dcg.Tooltip(C, delay=0.5):
                dcg.Text(C, value="Takes 0.5s before showing")

            dcg.Separator(C)

            # Auto hide tooltip when moving the mouse
            dcg.Text(C, value="Hide on motion", no_newline=True)
            with dcg.Tooltip(C, hide_on_activity=True):
                dcg.Text(C, value="I disappear as soon as you move the mouse")
            dcg.Text(C, value="| And with a delay")
            with dcg.Tooltip(C, hide_on_activity=True, delay=0.25):
                dcg.Text(C, value="I disappear as soon as you move the mouse")

            dcg.Separator(C)

            # Using condition from handler
            text_with_custom_showing = dcg.Text(C, value="Custom condition")
            class EvenSecondsHandler(dcg.CustomHandler):
                """ A handler that is true every even second """
                def check_can_bind(self, item):
                    return True
                def check_status(self, item):
                    # Prevent the viewport from sleeping
                    # when we are checking the condition
                    # for the purpose of this demo
                    self.context.viewport.wake()
                    return int(time.time()) % 2 < 1
            complex_handler = dcg.HandlerList(C, op=dcg.HandlerListOP.ALL)
            # HandlerListOp.ALL: the condition holds if both 
            # HoverHandler and EvenSecondsHandler are true
            with complex_handler:
                dcg.HoverHandler(C)
                EvenSecondsHandler(C)
            # Note: when using condition_from_handler, the target field
            # must be set.
            with dcg.Tooltip(C,
                             condition_from_handler=complex_handler,
                             target=text_with_custom_showing):
                dcg.Text(C, value="I appear and disappear every second")

            dcg.Separator(C)

            # Target any item
            dcg.Text(C, value="Target specific item")
            # Note in general it is prefered to set the Tooltip after
            # its target in the rendering tree, because the handler condition
            # uses current item states which are only updated when the item
            # is rendered.
            with dcg.Tooltip(C):
                dcg.Text(C, value="This tooltip is for the text below")
            text_target2 = dcg.Text(C, value="I'm the target")
            text_target2.previous_sibling.target = text_target2 # type: ignore

            dcg.Separator(C)

            # Dynamic tooltips
            dcg.Text(C, value="\nDynamic tooltips:")
            text_dynamic = dcg.Text(C, value="Hover me for a dynamic tooltip")
            def create_tooltip(sender, target):
                # Temporary tooltip handles detaching and deleting the tooltip
                # when it is not shown anymore.
                with dcg.utils.TemporaryTooltip(C, target=target, parent=target.parent):
                    dcg.Text(C, value=f"Tooltip creation time: {datetime.datetime.now()}")
            text_dynamic.handlers += [dcg.GotHoverHandler(C, callback=create_tooltip)]

        with dcg.CollapsingHeader(C, label="Drag & Drop"):
           with dcg.TreeNode(C, label="Help"):
                dcg.Text(C, value="Use a DragDropSourceHandler to make a widget source.", marker="bullet")
                dcg.Text(C, value="Adding a DragDropTargetHandler to a widget makes it target.", marker="bullet")
                dcg.Text(C, value="Compatibility is determined by the 'drag_type'.", marker="bullet")
                dcg.Text(C, value="The 'drag_type' must be less than 30 characters.", marker="bullet")

           with dcg.TreeNode(C, label="Examples"):

                with dcg.HorizontalLayout(C, x=200):
                    with dcg.VerticalLayout(C):

                        dcg.Text(C, value="Int Sources:")
                        with dcg.ConditionalHandler(C) as on_press_int:
                            dcg.DragDropSourceHandler(C, drag_type="int")
                            dcg.ActivatedHandler(C)

                        source1 = dcg.Button(C, label="Source 1: 25", handlers=on_press_int, user_data=25)
                        source2 = dcg.Button(C, label="Source 2: 33", handlers=on_press_int, user_data=33)
                        source3 = dcg.Button(C, label="Source 3: 111", handlers=on_press_int, user_data=111)

                        with dcg.Tooltip(C, target=source1, condition_from_handler=dcg.DragDropActiveHandler(C)):
                            dcg.Text(C, value="25")
                        with dcg.Tooltip(C, target=source2, condition_from_handler=dcg.DragDropActiveHandler(C)):
                            dcg.Text(C, value="33")
                        with dcg.Tooltip(C, target=source3, condition_from_handler=dcg.DragDropActiveHandler(C)):
                            dcg.Text(C, value="111")

                    with dcg.VerticalLayout(C):
                        dcg.Text(C, value="Float Sources:")
                        with dcg.ConditionalHandler(C) as on_press_float:
                            dcg.DragDropSourceHandler(C, drag_type="float")
                            dcg.ActivatedHandler(C)

                        source1 = dcg.Button(C, label="Source 1: 43.7", handlers=on_press_float, user_data=43.7)
                        source2 = dcg.Button(C, label="Source 2: 99.8", handlers=on_press_float, user_data=99.8)
                        source3 = dcg.Button(C, label="Source 3: -23.4", handlers=on_press_float, user_data=-23.4)

                        with dcg.Tooltip(C, target=source1, condition_from_handler=dcg.DragDropActiveHandler(C)):
                            dcg.Text(C, value="43.7")
                        with dcg.Tooltip(C, target=source2, condition_from_handler=dcg.DragDropActiveHandler(C)):
                            dcg.Text(C, value="99.8")
                        with dcg.Tooltip(C, target=source3, condition_from_handler=dcg.DragDropActiveHandler(C)):
                            dcg.Text(C, value="-23.4")

                    with dcg.VerticalLayout(C):
                        dcg.Text(C, value="Targets:")

                        def on_drop(sender, target, data):
                            source = data[1]
                            target.value = source.user_data

                        #item_ is appended to all events from DragDropSourceHandler
                        dcg.InputValue(C, label="Int Target", width=100, print_format="%.0f", step=0,
                                       handlers=dcg.DragDropTargetHandler(C, accepted_types="item_int", callback=on_drop))
                        dcg.InputValue(C, label="Float Target", width=100, print_format="%f", step=0,
                                       handlers=dcg.DragDropTargetHandler(C, accepted_types="item_float", callback=on_drop))

        with dcg.CollapsingHeader(C, label="Tables"):
            with dcg.TreeNode(C, label="Basic"):
                # basic usage of the table api
                table = dcg.Table(C, header=False)
                for i in range(4):
                    with table.next_row:
                        for j in range(3):
                            dcg.Text(C, value=f"Row{i} Column{j}")
                dcg.Separator(C)
                dcg.Text(C, value="Tables can be declared in several ways for the same result.")
                dcg.Text(C, value="Example below are identical but with different syntax.")
                dcg.Separator(C)
                table = dcg.Table(C, header=False)
                for i in range(4):
                    for j in range(3):
                        # This syntax is more verbose but allows
                        # to skip cells more easily,
                        # and is the only syntax that
                        # enables to update a single cell.
                        table[i, j] = dcg.Text(C, value=f"Row{i} Column{j}")
                dcg.Separator(C)
                table = dcg.Table(C, header=False)
                for i in range(4):
                    for j in range(3):
                        # when not using the with syntax, it is possible
                        # to pass a string directly which will be 
                        # shown in the cell. If you only use
                        # text elements, it is recommended to use
                        # strings directly as it is more efficient.
                        table[i, j] = f"Row{i} Column{j}"
                dcg.Separator(C)
                table = dcg.Table(C, header=False)
                for j in range(3):
                    with table.next_col:
                        for i in range(4):
                            dcg.Text(C, value=f"Row{i} Column{j}")
                dcg.Separator(C)
                table = dcg.Table(C, header=False)
                for i in range(4):
                    with table.row(i): # Note this overwrite the row if it was previously set
                        for j in range(3):
                            dcg.Text(C, value=f"Row{i} Column{j}")
                dcg.Separator(C)
                table = dcg.Table(C, header=False)
                for j in range(3):
                    with table.col(j):
                        for i in range(4):
                            dcg.Text(C, value=f"Row{i} Column{j}")
                dcg.Separator(C)
                table = dcg.Table(C, header=False)
                for i in range(4):
                    items = []
                    for j in range(3):
                        # it is also possible to append dcg.Text/etc elements here
                        items.append(f"Row{i} Column{j}")
                    table.append_row(items)
                    # Same syntax exists for append_col,
                    # and set_row, set_col to overwrite a row or column.
                    # Finally remove_row, insert_row, etc enable
                    # to manipulate rows and columns and shift ranges
                    # of items.

            with dcg.TreeNode(C, label="Number of columns and rows"):
                dcg.Text(C, value=\
                    "By default the number of rows and columns is deduced\nfrom the indices of the items. "
                    "It is possible to force a\nnumber of visible columns/rows that is different\n"
                    "from the number of columns/rows in the table,\n"
                    "using the table.num_rows_visible and table.num_cols_visible attributes.\n"
                    "table.num_rows and table.num_cols hold the actual number.")
                # num_rows_visible and num_cols_visible defaults are None, which means
                # use num_rows and num_cols.
                table = dcg.Table(C, header=False, flags=dcg.TableFlag.BORDERS)
                table[1, 2] = "Row 1 Column 2"
                table.num_cols_visible = 4
                table.num_rows_visible = 3
                # For the purpose of this demo, increase the spacing between rows
                for i in range(3):
                    table.row_config[i].min_height = 50
                dcg.Text(C, value=f"This table has actually only {table.num_rows} rows and {table.num_cols} columns.")

            with dcg.TreeNode(C, label="Borders, background"):
                table = dcg.Table(C,
                                  header=False,
                                  flags = dcg.TableFlag.ROW_BG | \
                                          dcg.TableFlag.BORDERS_INNER_H | \
                                          dcg.TableFlag.BORDERS_OUTER_H | \
                                          dcg.TableFlag.BORDERS_INNER_V | \
                                          dcg.TableFlag.BORDERS_OUTER_V)
                for i in range(5):
                    with table.next_row:
                        for j in range(3):
                            dcg.Text(C, value=f"Row{i} Column{j}")
                with dcg.HorizontalLayout(C):
                    with dcg.VerticalLayout(C):
                        dcg.Checkbox(C, label="row_background", value=True, callback=_table_flag_config, user_data=(table, dcg.TableFlag.ROW_BG))
                        dcg.Checkbox(C, label="borders_innerH", value=True, callback=_table_flag_config, user_data=(table, dcg.TableFlag.BORDERS_INNER_H))
                        dcg.Checkbox(C, label="borders_innerV", value=True, callback=_table_flag_config, user_data=(table, dcg.TableFlag.BORDERS_INNER_V))
                    with dcg.VerticalLayout(C):
                        dcg.Checkbox(C, label="borders_outerH", value=True, callback=_table_flag_config, user_data=(table, dcg.TableFlag.BORDERS_OUTER_H))
                        dcg.Checkbox(C, label="borders_outerV", value=True, callback=_table_flag_config, user_data=(table, dcg.TableFlag.BORDERS_OUTER_V))
                        dcg.Checkbox(C, label="header", value=False, callback=_config, user_data=table)

            with dcg.TreeNode(C, label="Manipulating items"):
                dcg.Text(C, value="The following section shows how to manipulate table items and groups of items.")

                # Create a basic table with some content
                table = dcg.Table(C, header=False, flags=dcg.TableFlag.BORDERS)
                for i in range(3):
                    with table.next_row:
                        for j in range(3):
                            dcg.Text(C, value=f"Row{i} Column{j}")

                dcg.Separator(C)
                dcg.Text(C, value="Basic item manipulation:")

                def swap_cells(table=table):
                    table.swap((0, 0), (1, 1))
                dcg.Button(C, label="Swap (0,0) and (1,1)", callback=swap_cells)

                def delete_cell(table=table):
                    del table[0, 0]
                dcg.Button(C, label="Delete cell (0,0)", callback=delete_cell)

                def set_cell(table=table):
                    table[0, 0] = "New Value"
                dcg.Button(C, label="Set cell (0,0)", callback=set_cell)

                dcg.Separator(C)
                dcg.Text(C, value="Row manipulation:")

                def swap_rows(table=table):
                    table.swap_rows(0, 1)
                dcg.Button(C, label="Swap rows 0 and 1", callback=swap_rows)

                def remove_row(table=table):
                    table.remove_row(0)
                dcg.Button(C, label="Remove row 0", callback=remove_row)

                def insert_row(table=table):
                    table.insert_row(0, ["New", "Row", "Here"])
                dcg.Button(C, label="Insert row at 0", callback=insert_row)

                def append_row(table=table):
                    table.append_row(["Appended", "Row", "Here"])
                dcg.Button(C, label="Append row", callback=append_row)

                dcg.Separator(C)
                dcg.Text(C, value="Column manipulation:")

                def swap_cols(table=table):
                    table.swap_cols(0, 1)
                dcg.Button(C, label="Swap columns 0 and 1", callback=swap_cols)

                def remove_col(table=table):
                    table.remove_col(0)
                dcg.Button(C, label="Remove column 0", callback=remove_col)

                def insert_col(table=table):
                    table.insert_col(0, ["New", "Column", "Here"])
                dcg.Button(C, label="Insert column at 0", callback=insert_col)

                def append_col(table=table):
                    table.append_col(["Appended", "Column", "Here"])
                dcg.Button(C, label="Append column", callback=append_col)

                dcg.Separator(C)
                dcg.Text(C, value="Table iteration and clearing:")

                table_output: dcg.InputText | None = None
                def update_table_output(table=table):
                    nonlocal table_output
                    output = "Table contents:\n"
                    for (i, j) in table:
                        content = table[i,j].content
                        if content is None:
                            value = None
                        elif isinstance(content, dcg.uiItem):
                            value = (type(content), content.label, content.value)
                        else:
                            value = str(content)
                        output += f"({i},{j}): {value}\n"
                    assert table_output is not None
                    table_output.value = output

                dcg.Button(C, label="Show table contents", callback=update_table_output)
                table_output = dcg.InputText(C, readonly=True, height=200, multiline=True) 

                def clear_table(table=table):
                    table.clear()
                dcg.Button(C, label="Clear table", callback=clear_table)

            with dcg.TreeNode(C, label="Colors"):
                with dcg.TreeNode(C, label="Alternating row colors"):
                    dcg.Text(C, value="The TableFlag.ROW_BG flag enables to set alternating row colors.")
                    dcg.Text(C, value="The colors corresponds to the theme's TableRowBg and TableRowBgAlt.")
                    table = dcg.Table(C, header=False, flags=dcg.TableFlag.ROW_BG)
                    table.theme = \
                        dcg.ThemeColorImGui(C,
                            table_row_bg=(0, 255, 0),
                            table_row_bg_alt=(0, 0, 255))
                    for i in range(6):
                        with table.next_row:
                            for j in range(6):
                                dcg.Text(C, value=f"Row{i} Column{j}")

                with dcg.TreeNode(C, label="Manual row colors"):
                    dcg.Text(C, value="It is also possible to set the row/col colors manually.")
                    dcg.Text(C, value="The row_config attribute holds the configuration of each row.")
                    dcg.Text(C, value="The bg_color attribute of a row configuration enables to set the color.")
                    dcg.Text(C, value="Note that there is no equivalent bg_color for columns")
                    table = dcg.Table(C, header=False)
                    for i in range(6):
                        with table.next_row:
                            for j in range(6):
                                dcg.Text(C, value=f"Row{i} Column{j}")
                    for i in range(6):
                        table.row_config[i].bg_color = (255, 0, 0, i * 255 // 8)

                with dcg.TreeNode(C, label="Manual cell colors"):
                    dcg.Text(C, value="Cell colors can be set manually.")
                    dcg.Text(C, value="Table[i, j] returns a TableElement which enables to set a background color.")
                    dcg.Text(C, value="It is also possible to write a TableElement directly to Table[i, j].")
                    table = dcg.Table(C, header=False)
                    for i in range(6):
                        with table.next_row:
                            for j in range(6):
                                dcg.Text(C, value=f"Row{i} Column{j}")
                    table[1, 0].bg_color = (0, 255, 0, 100)# -> will have no effect because the table element is not set
                    # indeed table[1, 0] returns a copy of the configuration element,
                    # not a reference. To set the element, one must write it back.
                    table_element = table[1, 1]
                    table_element.bg_color = (0, 255, 0, 100)
                    table[1, 1] = table_element
                    # Alternative syntax:
                    table[2, 2] = {"content": "Row2 Column2", "bg_color": (0, 0, 255, 100)}
                    table[3, 3] = dcg.TableElement(content="Row3 Column3", bg_color=(255, 0, 0, 100))

                with dcg.TreeNode(C, label="Combining colors"):
                    dcg.Text(C, value="It is possible to combine the different color settings.")
                    dcg.Text(C, value="The color set at the cell level has precedence over the row color.")
                    dcg.Text(C, value="Which itself has precedence over the alternating row colors.")
                    table = dcg.Table(C, header=False, flags=dcg.TableFlag.ROW_BG)
                    table.theme = \
                        dcg.ThemeColorImGui(C,
                            table_row_bg=(0, 255, 0),
                            table_row_bg_alt=(0, 0, 255))
                    for i in range(6):
                        with table.next_row:
                            for j in range(6):
                                dcg.Text(C, value=f"Row{i} Column{j}")
                    # Note: if you set alpha != 255, blending will occur.
                    table_element = table[1, 1]
                    table_element.bg_color = (0, 0, 255)
                    table[1, 1] = table_element
                    table.row_config[1].bg_color = (255, 0, 0)

            with dcg.TreeNode(C, label="Resizing"):
                with dcg.TreeNode(C, label="Stretch columns"):
                    dcg.Text(C, value="Columns can be stretched to fill the remaining space.")
                    dcg.Text(C, value="The stretch attribute of a column configuration enables to stretch the column.")
                    table = dcg.Table(C, header=False, flags=dcg.TableFlag.BORDERS)
                    for i in range(3):
                        with table.next_row:
                            for j in range(3):
                                dcg.Text(C, value=f"Row{i} Column{j}")
                    # The table policy here defaults stretch = None to stretch = True,
                    # however it is needed to set manually if one wants to apply
                    # a non-default stretch weight.
                    table.col_config[1].stretch = True
                    table.col_config[1].stretch_weight = 2.
                    with dcg.HorizontalLayout(C):
                        dcg.Checkbox(C, label="stretch", value=True, callback=_table_column_config, user_data=(table, 1, "stretch"))
                        dcg.Checkbox(C, label="resizable", value=False, callback=_table_flag_config, user_data=(table, dcg.TableFlag.RESIZABLE))
                        dcg.Checkbox(C, label="borders", value=True, callback=_table_flag_config, user_data=(table, dcg.TableFlag.BORDERS))

                with dcg.TreeNode(C, label="Fixed columns"):
                    dcg.Text(C, value="Columns can be fixed to a specific width.")
                    dcg.Text(C, value="The width attribute of a column configuration enables to set the width.")
                    table = dcg.Table(C, header=False, flags=dcg.TableFlag.BORDERS | dcg.TableFlag.SIZING_FIXED_FIT)
                    for i in range(3):
                        with table.next_row:
                            for j in range(3):
                                dcg.Text(C, value=f"Row{i} Column{j}")
                    # Same as above. While the table policy would
                    # default stretch = None to stretch = False,
                    # it is needed to set manually if one wants to apply
                    # a non-default width.
                    table.col_config[1].stretch = False
                    table.col_config[1].width = 300
                    # SIZING_FIXED_FIT interpretes col_config.stretch = None as stretch = False for all columns
                    with dcg.HorizontalLayout(C):
                        dcg.Checkbox(C, label="stretch", value=False, callback=_table_column_config, user_data=(table, 1, "stretch"))
                        dcg.Checkbox(C, label="resizable", value=False, callback=_table_flag_config, user_data=(table, dcg.TableFlag.RESIZABLE))
                        dcg.Checkbox(C, label="borders", value=True, callback=_table_flag_config, user_data=(table, dcg.TableFlag.BORDERS))
                        dcg.Checkbox(C, label="no_host_extendX", value=False, callback=_table_flag_config, user_data=(table, dcg.TableFlag.NO_HOST_EXTEND_X))

            with dcg.TreeNode(C, label="Tooltips"):
                dcg.Text(C, value="Tooltips can be attributed to cells of a table.")
                table = dcg.Table(C, header=False)
                with table.next_row:
                    for j in range(3):
                        dcg.Text(C, value=f"Column{j}")
                        with dcg.Tooltip(C):
                            dcg.Text(C, value="Tables skip tooltip items when attributing cells.")

                table = dcg.Table(C, header=False)
                for j in range(3):
                    # Note it doesn't have to be strings with this syntax.
                    # It can be directly the inside of a dcg.Tooltip.
                    # The dcg.Tooltip syntax enables more control (such as
                    # hovering delay, etc).
                    # a TableElement can be used instead of a dict.
                    table[0, j] = {"content": f"Column{j}", "tooltip": f"item {j}"}

            with dcg.TreeNode(C, label="Columns Options"):
                # Create main table with all the features enabled
                table = dcg.Table(C, 
                            header=True,
                            flags=dcg.TableFlag.BORDERS_INNER_H | \
                                  dcg.TableFlag.BORDERS_OUTER_H | \
                                  dcg.TableFlag.BORDERS_INNER_V | \
                                  dcg.TableFlag.ROW_BG | \
                                  dcg.TableFlag.HIDEABLE | \
                                  dcg.TableFlag.REORDERABLE | \
                                  dcg.TableFlag.RESIZABLE | \
                                  dcg.TableFlag.SORTABLE | \
                                  dcg.TableFlag.SCROLL_X | \
                                  dcg.TableFlag.SCROLL_Y |
                                  dcg.TableFlag.NO_HOST_EXTEND_X)

                # Add columns with different configuration options
                # First column with default sort
                #table.col_config[0].default_sort = True
                table.col_config[0].label = "One"
                table.col_config[1].label = "Two"
                table.col_config[2].label = "Three"
                table.col_config[2].enabled = False # Start hidden

                # Add 8 rows of data with increasing indentation
                for i in range(8):
                    with table.next_row:
                        dcg.Text(C, value=(i * " ") + "Indented One")
                        dcg.Text(C, value="Hello Two")
                        dcg.Text(C, value="Hello Three")

                # Column configuration options 
                options = [
                    "default_sort", 
                    "stretch",
                    "no_resize",
                    "no_reorder",
                    "no_hide",
                    "no_clip",
                    "no_sort",
                    "no_sort_ascending",
                    "no_sort_descending", 
                    "no_header_width",
                    "prefer_sort_ascending",
                    "prefer_sort_descending"
                ]

                tb_config = dcg.Table(C, header=False)
                for i in range(3):
                    tb_config[0, i]=["One", "Two", "Three"][i]
                    for (j, opt) in enumerate(options):
                        tb_config[j+1, i] = dcg.Checkbox(C,
                            label=opt, callback=_table_column_config,
                            user_data=(table, i, opt))

            with dcg.TreeNode(C, label="Columns states"):
                # Create table with resizable columns
                table = dcg.Table(C, 
                            header=True, 
                            flags=dcg.TableFlag.BORDERS_OUTER_H | \
                                  dcg.TableFlag.BORDERS_INNER_H | \
                                  dcg.TableFlag.HIDEABLE | \
                                  dcg.TableFlag.SIZING_FIXED_SAME |
                                  dcg.TableFlag.RESIZABLE)

                # Add columns with different configuration options
                table.col_config[0].label = "One"
                table.col_config[1].label = "Two"
                table.col_config[2].label = "Three"
                table.col_config[3].label = "Four"
                column_visible_text = dcg.Text(C, value="Last column is not Visible")

                # color the columns when they are hovered:
                for i in range(4):
                    bg_color = (255, 0, 0, 100)
                    def update_color_on_hover(sender, table=table, i=i):
                        for j in range(3):
                            element = table[j, i]
                            element.bg_color = bg_color
                            table[j, i] = element
                    def update_color_on_unhover(sender, table=table, i=i):
                        for j in range(3):
                            element = table[j, i]
                            element.bg_color = 0
                            table[j, i] = element
                    def update_color(sender, table=table, i=i):
                        nonlocal bg_color
                        bg_color = np.random.randint(0, 255, 3).tolist() + [100]
                        if table.col_config[i].state.hovered:
                            for j in range(3):
                                element = table[j, i]
                                element.bg_color = bg_color
                                table[j, i] = element
                    def toggle_open(sender, table=table, i=i):
                        table.num_rows_visible = i
                    table.col_config[i].handlers += [
                        dcg.GotHoverHandler(C,
                                            callback=update_color_on_hover),
                        dcg.LostHoverHandler(C,
                                            callback=update_color_on_unhover),
                        dcg.ClickedHandler(C, callback=update_color),
                        dcg.ToggledOpenHandler(C, callback=toggle_open),
                        dcg.ToggledCloseHandler(C, callback=toggle_open)
                    ]
                    if i == 3:
                        # In the case of col_config, the render handler corresponds to
                        # the column being visible or not. Items are still rendered.
                        table.col_config[i].handlers += [
                            dcg.LostRenderHandler(C,
                                callback=lambda : column_visible_text.configure(value="Last column is not Visible")),
                            dcg.GotRenderHandler(C,
                                callback=lambda : column_visible_text.configure(value="Last column is Visible"))
                        ]
                        

                # Add 3 rows of data
                for i in range(3):
                    with table.next_row:
                        for j in range(3):
                            dcg.Text(C, value=f"Hello {i}, {j}                      ")
                        dcg.Button(C, label="Buttons do not block hover")

            with dcg.TreeNode(C, label="Columns widths"): # TODO
                # Create table with resizable columns
                table = dcg.Table(C, 
                            header=True,
                            flags=dcg.TableFlag.BORDERS_OUTER_H | \
                                  dcg.TableFlag.BORDERS_INNER_H | \
                                  dcg.TableFlag.BORDERS_OUTER_V | \
                                  dcg.TableFlag.BORDERS_INNER_V |
                                  dcg.TableFlag.NO_KEEP_COLUMNS_VISIBLE |
                                  dcg.TableFlag.RESIZABLE)

                # Add columns with different configuration options
                table.col_config[0].label = "One"
                table.col_config[1].label = "Two"
                table.col_config[2].label = "Three"

                # Add 3 rows of data
                for i in range(3):
                    for j in range(3):
                        table[i, j] = f"Hello {i}, {j}"

                # Add text to show column width
                with table.next_row:
                    for j in range(3):
                        text_id = dcg.TextValue(C, print_format="(w: %0.f)", value=0.)
                        text_id.handlers += [
                            dcg.RenderHandler(C,
                                user_data = (text_id, table, j),
                                callback=lambda s: s.user_data[0].configure(
                                    value=s.user_data[1].col_config[s.user_data[2]].width)
                                )
                        ]

                # Same but with content width
                with table.next_row:
                    for j in range(3):
                        text_id = dcg.TextValue(C, print_format="(w: %0.f)", value=0.)
                        text_id.handlers += [
                            dcg.RenderHandler(C,
                                user_data = (text_id, table, j),
                                callback=lambda s: s.user_data[0].configure(
                                    value=s.user_data[1].col_config[s.user_data[2]].content_area[0])
                                )
                        ]

                # Checkboxes for a few table options that affect sizing
                with dcg.HorizontalLayout(C):
                    for option in ["no_keep_columns_visible", "borders_inner_H", "borders_outer_H", "borders_inner_V", "borders_outer_V"]:
                        dcg.Checkbox(C, label=option, value=True, callback=_table_flag_config, user_data=(table, getattr(dcg.TableFlag, option.upper())))

            with dcg.TreeNode(C, label="Row heights"):
                # Create table with resizable columns
                table = dcg.Table(C, 
                            header=True,
                            flags=dcg.TableFlag.BORDERS_OUTER_H | \
                                  dcg.TableFlag.BORDERS_INNER_H | \
                                  dcg.TableFlag.BORDERS_OUTER_V | \
                                  dcg.TableFlag.BORDERS_INNER_V |
                                  dcg.TableFlag.RESIZABLE)

                # Add columns with different configuration options
                table.col_config[0].label = "One"
                table.col_config[1].label = "Two"
                table.col_config[2].label = "Three"

                # Add 3 rows of data
                for i in range(3):
                    # Force increasing min_height
                    table.row_config[i].min_height = 20 + 30 * i
                    for j in range(3):
                        table[i, j] = f"min height = {20 + 30 * i}"

            with dcg.TreeNode(C, label="Padding"):
                table = dcg.Table(C,
                                  header=False,
                                  flags=dcg.TableFlag.RESIZABLE | \
                                        dcg.TableFlag.HIDEABLE | \
                                        dcg.TableFlag.REORDERABLE | \
                                        dcg.TableFlag.BORDERS_OUTER_V | \
                                        dcg.TableFlag.BORDERS_INNER_H)

                table.col_config[0].label = "One"
                table.col_config[1].label = "Two"
                table.col_config[2].label = "three"

                for i in range(5):
                    with table.next_row:
                        for j in range(3):
                            dcg.Button(C, label=f"Hello {i}, {j}", width=-1)

                with dcg.HorizontalLayout(C):
                    for option in ["pad_outer_X", "no_pad_outer_X", "no_pad_inner_X", "borders_outer_V", "borders_inner_V"]:
                        dcg.Checkbox(C, label=option, value=True, callback=_table_flag_config, user_data=(table, getattr(dcg.TableFlag, option.upper())))

            with dcg.TreeNode(C, label="Reorderable, hideable, with headers"):
                table = dcg.Table(C,
                                  header=True,
                                  flags=dcg.TableFlag.BORDERS_OUTER_H | \
                                        dcg.TableFlag.BORDERS_INNER_H | \
                                        dcg.TableFlag.BORDERS_OUTER_V | \
                                        dcg.TableFlag.BORDERS_INNER_V | \
                                        dcg.TableFlag.HIDEABLE | \
                                        dcg.TableFlag.REORDERABLE | \
                                        dcg.TableFlag.RESIZABLE)

                table.col_config[0].label = "One"
                table.col_config[1].label = "Two"
                table.col_config[2].label = "three"

                for i in range(5):
                    with table.next_row:
                        for j in range(3):
                            dcg.Text(C, value=f"Hello {i}, {j}")

                with dcg.HorizontalLayout(C):
                    for option in ["hideable", "reorderable", "resizable"]:
                        dcg.Checkbox(C, label=option, value=True, callback=_table_flag_config, user_data=(table, getattr(dcg.TableFlag, option.upper())))

            with dcg.TreeNode(C, label="Outer Size"):
                table = dcg.Table(C, 
                                  header=False,
                                  flags=dcg.TableFlag.BORDERS_INNER_H | \
                                        dcg.TableFlag.BORDERS_OUTER_H | \
                                        dcg.TableFlag.BORDERS_INNER_V | \
                                        dcg.TableFlag.BORDERS_OUTER_V | \
                                        dcg.TableFlag.ROW_BG | \
                                        dcg.TableFlag.SIZING_FIXED_FIT |
                                        dcg.TableFlag.NO_HOST_EXTEND_X,
                                  height=150)

                table.col_config[0].label = "One"
                table.col_config[1].label = "Two" 
                table.col_config[2].label = "three"

                for i in range(10):
                    with table.next_row:
                        for j in range(3):
                            dcg.Text(C, value=f"Cell {i}, {j}")

                with dcg.HorizontalLayout(C):
                    for option in ["no_host_extend_X", "no_host_extend_Y", "resizable"]:
                        dcg.Checkbox(C, label=option, value=False, callback=_table_flag_config, user_data=(table, getattr(dcg.TableFlag, option.upper())))

                dcg.Text(C, value="Using explicit size:")
                table2 = dcg.Table(C,
                                     header=False, 
                                     flags=dcg.TableFlag.BORDERS_INNER_H | \
                                           dcg.TableFlag.BORDERS_OUTER_H | \
                                           dcg.TableFlag.BORDERS_INNER_V | \
                                           dcg.TableFlag.BORDERS_OUTER_V | \
                                           dcg.TableFlag.ROW_BG | \
                                           dcg.TableFlag.SIZING_FIXED_FIT |
                                           dcg.TableFlag.NO_HOST_EXTEND_X,
                                     height=300,
                                     width=300)

                table2.col_config[0].label = "One"
                table2.col_config[1].label = "Two"
                table2.col_config[2].label = "three"

                for i in range(6):
                    with table2.next_row:
                        for j in range(3):
                            dcg.Text(C, value=f"Cell {i}, {j}")

            with dcg.TreeNode(C, label="Scrolling"):
                table = dcg.Table(C, 
                                  header=True,
                                  height=150,
                                  width=150,
                                  flags=dcg.TableFlag.BORDERS | \
                                        dcg.TableFlag.CONTEXT_MENU_IN_BODY | \
                                        dcg.TableFlag.ROW_BG | \
                                        dcg.TableFlag.SIZING_FIXED_FIT | \
                                        dcg.TableFlag.SCROLL_X | \
                                        dcg.TableFlag.SCROLL_Y)

                table.col_config[0].label = "One"
                table.col_config[1].label = "Two"
                table.col_config[2].label = "three"

                for i in range(25):
                    with table.next_row:
                        dcg.InputValue(C, label=" ", print_format="%.0f", step=0)
                        dcg.Button(C, label=f"Cell {i}, 1")
                        dcg.Text(C, value=f"Cell {i}, 2")

                with dcg.HorizontalLayout(C):
                    for option in ["scroll_X", "scroll_Y", "resizable"]:
                        dcg.Checkbox(C, label=option, value=True, callback=_table_flag_config, user_data=(table, getattr(dcg.TableFlag, option.upper())))
                with dcg.HorizontalLayout(C):
                    def _table_frozen_rows(sender, target, value, table=table):
                        table.num_rows_frozen = int(value)
                    dcg.Slider(C, label="Number of frozen rows", print_format="%.0f", value=0, min_value=0, max_value=25, callback=_table_frozen_rows)
                    def _table_frozen_cols(sender, target, value, table=table):
                        table.num_cols_frozen = int(value)
                    dcg.Slider(C, label="Number of frozen columns", print_format="%.0f", value=0, min_value=0, max_value=3, callback=_table_frozen_cols)

            with dcg.TreeNode(C, label="Filtering"):
                dcg.Text(C, value="Using Filter (column 3)")
                table = dcg.Table(C,
                                  header=True,
                                  flags = \
                                    dcg.TableFlag.BORDERS | \
                                    dcg.TableFlag.NO_HOST_EXTEND_X | \
                                    dcg.TableFlag.CONTEXT_MENU_IN_BODY | \
                                    dcg.TableFlag.ROW_BG | \
                                    dcg.TableFlag.SIZING_FIXED_FIT | \
                                    dcg.TableFlag.SCROLL_Y,
                                   height=300)
                table.col_config[0].label = "One"
                table.col_config[1].label = "Two"
                table.col_config[2].label = "Three"

                for i in range(25):
                    with table.next_row:
                        dcg.InputValue(C, label=" ", print_format="%.0f", step=0)
                        dcg.Button(C, label=f"Cell {i}, 1")
                        dcg.Text(C, value=str(int(10000*np.random.randn())))

                def _filter_rows(sender, target, value, table=table):
                    if table is None:
                        return
                    for i in range(table.num_rows):
                        table.row_config[i].show = value in typing.cast(dcg.uiItem, table[i, 2].content).value
                dcg.InputText(C, label="Filter", decimal=True, before=table, callback=_filter_rows)

            with dcg.TreeNode(C, label="Sorting"):
                dcg.Text(C, value="Sorting")
                table = dcg.Table(C,
                                  header=True,
                                  flags = \
                                    dcg.TableFlag.BORDERS | \
                                    dcg.TableFlag.NO_HOST_EXTEND_X | \
                                    dcg.TableFlag.CONTEXT_MENU_IN_BODY | \
                                    dcg.TableFlag.ROW_BG | \
                                    dcg.TableFlag.SIZING_FIXED_FIT | \
                                    dcg.TableFlag.SCROLL_Y | \
                                    dcg.TableFlag.SORTABLE |
                                    dcg.TableFlag.SORT_MULTI |
                                    dcg.TableFlag.SORT_TRISTATE,
                                   height=300)
                table.col_config[0].label = "One"
                table.col_config[1].label = "Two"
                table.col_config[2].label = "Three"

                # When writing the content as a string, it uses
                # this value for the sorting.
                # When writing an item, it uses it's uuid (creation order)
                # to have a custom order, you can write to the
                # "ordering_value" field of table[i, j]

                for i in range(25):
                    # The content of the table is used to infer ordering_value
                    # here we pass an integer which will be used for sorting.
                    # The displayed element is a conversion of this integer to a string.
                    table[i, 0] = int(10000*np.random.randn())
                    # Alternative way of setting ordering value directly
                    # when passing a complex content
                    v1 = int(10000*np.random.randn())
                    table[i, 1] = {
                        "content": dcg.Text(C,
                                            value=str(v1),
                                            color = (255, 255, 0)),
                        "ordering_value": v1 # Any type is accepted. The sorting is done according to the type of the value.
                    }
                # Alternate way of setting ordering value using a different
                # syntax
                with table.next_col:
                    for i in range(25):
                        dcg.Text(C,
                                 value=str(int(10000*np.random.randn())),
                                 color = (0, 255, 255))
                for i in range(25):
                    # table[i, 2].ordering_value = ... won't work because
                    # it modified the table element but doesn't set it again.
                    table_element = table[i, 2]
                    table_element.ordering_value = int(typing.cast(dcg.uiItem, table_element.content).value)
                    table[i, 2] = table_element

                # Extend the table with interesting elements for sorting
                for i in range(25):
                    table[i+25, 0] = table[i, 0]
                    table[i+25, 1] = table[(i+12)%25, 1]
                    table[i+25, 2] = table[(i+6)%25, 2]

                def _change_sorting_type(sender, target, value, table=table):
                    for i in range(table.num_rows):
                        for j in range(table.num_cols):
                            table_element = table[i, j]
                            if value == "integer":
                                table_element.ordering_value = int(typing.cast(typing.SupportsInt, table_element.ordering_value))
                            else:
                                table_element.ordering_value = str(table_element.ordering_value)
                            table[i, j] = table_element
                dcg.RadioButton(C, label="Sort as ", items=["integer", "string (lexicographic)"],
                                horizontal=True,
                                value="integer", callback=_change_sorting_type)
                with dcg.HorizontalLayout(C):
                    for option in ["sortable", "sort_multi", "sort_tristate"]:
                        dcg.Checkbox(C, label=option, value=True, callback=_table_flag_config, user_data=(table, getattr(dcg.TableFlag, option.upper())))
                dcg.Text(C, wrap=0,
                         value="Multi: Hold shift to sort on multiple columns. "
                               "The array contains duplicated values to demonstrate this feature.")
                dcg.Text(C, value="Tristate: Adds a neutral sorting arrow")

            with dcg.TreeNode(C, label="Selecting rows"):
                #Create theme that hides table headers
                table_theme = \
                    dcg.ThemeColorImGui(C,
                        header_active=(0, 0, 0, 0),
                        header=(0, 0, 0, 0))

                table_sel_rows = dcg.Table(C, header=True, theme=table_theme)
                table_sel_rows.col_config[0].label = "First"
                table_sel_rows.col_config[1].label = "Second"
                table_sel_rows.col_config[2].label = "Third"

                def clb_selectable(sender, target, user_data):
                    print(f"Row {user_data}")

                for i in range(10):
                    with table_sel_rows.next_row:
                        for j in range(3):
                            dcg.Selectable(C,
                                label=f"Row{i} Column{j}",
                                callback=clb_selectable, 
                                span_columns=True,
                                user_data=i)

            with dcg.TreeNode(C, label="Selecting cells"):
                table_sel_cols = dcg.Table(C, header=True, theme=table_theme)
                table_sel_cols.col_config[0].label = "First"
                table_sel_cols.col_config[1].label = "Second"
                table_sel_cols.col_config[2].label = "Third"

                def clb_selectable(sender, target, user_data):
                    print(f"Row {user_data}")

                for i in range(10):
                    with table_sel_cols.next_row:
                        for j in range(3):
                            dcg.Selectable(C,
                                label=f"Row{i} Column{j}",
                                callback=clb_selectable,
                                user_data=(i, j))

            with dcg.TreeNode(C, label="Sizing Policy"):
                def create_table_set(size_policy: dcg.TableFlag):
                    """Create a pair of tables with given sizing policy"""
                    # First table with more rows
                    table1 = dcg.Table(C, header=False,
                                      flags=dcg.TableFlag.BORDERS_INNER_H | \
                                            dcg.TableFlag.BORDERS_OUTER_H | \
                                            dcg.TableFlag.BORDERS_INNER_V | \
                                            dcg.TableFlag.BORDERS_OUTER_V | \
                                            dcg.TableFlag.ROW_BG | size_policy)
                    for i in range(8):
                        with table1.next_row:
                            for j in range(3):
                                dcg.Text(C, value="Oh dear")

                    # Second table with varying width content
                    table2 = dcg.Table(C, header=False,
                                      flags=dcg.TableFlag.BORDERS_INNER_H | \
                                            dcg.TableFlag.BORDERS_OUTER_H | \
                                            dcg.TableFlag.BORDERS_OUTER_V | \
                                            dcg.TableFlag.ROW_BG | size_policy)
                    for i in range(3):
                        with table2.next_row:
                            dcg.Text(C, value="AAAA")
                            dcg.Text(C, value="BBBBBBBB")
                            dcg.Text(C, value="CCCCCCCCCCCC")
                    return table1, table2

                # Create tables with different policies
                tables_fixed_fit = create_table_set(dcg.TableFlag.SIZING_FIXED_FIT)
                tables_fixed_same = create_table_set(dcg.TableFlag.SIZING_FIXED_SAME)
                tables_stretch_prop = create_table_set(dcg.TableFlag.SIZING_STRETCH_PROP)
                tables_stretch_same = create_table_set(dcg.TableFlag.SIZING_STRETCH_SAME)

                all_tables = [*tables_fixed_fit, *tables_fixed_same, 
                            *tables_stretch_prop, *tables_stretch_same]
                SIZING_MASK = dcg.TableFlag.SIZING_FIXED_FIT | \
                              dcg.TableFlag.SIZING_FIXED_SAME | \
                              dcg.TableFlag.SIZING_STRETCH_PROP | \
                              dcg.TableFlag.SIZING_STRETCH_SAME

                # Controls
                policies = ["FIXED_FIT", "FIXED_SAME", "STRETCH_PROP", "STRETCH_SAME"]

                def update_policy(table_pair_idx, policy_name):
                    """Update sizing policy for a pair of tables"""
                    policy = getattr(dcg.TableFlag, "SIZING_"+policy_name)
                    start_idx = table_pair_idx * 2
                    all_tables[start_idx].flags &= ~SIZING_MASK
                    all_tables[start_idx].flags |= policy
                    all_tables[start_idx + 1].flags &= ~SIZING_MASK
                    all_tables[start_idx + 1].flags |= policy

                def update_flag(flag: dcg.TableFlag, value: bool):
                    """Update flag for all tables"""
                    for table in all_tables:
                        flags = table.flags
                        if value:
                            flags |= flag
                        else:
                            flags &= ~flag
                        table.flags = flags

                # Add controls at the top
                with dcg.HorizontalLayout(C, before=tables_fixed_fit[0]):
                    dcg.Checkbox(C, label="resizable",
                               callback=lambda s, t, d: update_flag(dcg.TableFlag.RESIZABLE, d))
                    dcg.Checkbox(C, label="no_host_extendX",
                               callback=lambda s, t, d: update_flag(dcg.TableFlag.NO_HOST_EXTEND_X, d))

                # Add policy selectors for each pair
                for i in range(4):
                    dcg.Combo(C, items=policies, label="Sizing Policy",
                             value=policies[i],
                             before=all_tables[2*i],
                             callback=lambda s, t, d, idx=i: update_policy(idx, d))


        with dcg.CollapsingHeader(C, label="Plots"):

            sindatax = np.linspace(0, 1, 101)
            sindatay = 0.5 + 0.5 * np.sin(50 * sindatax)
            cosdatay = 0.5 + 0.75 * np.cos(50 * sindatax)

            with dcg.TabBar(C):

                with dcg.Tab(C, label="Series"):

                    with dcg.TreeNode(C, label="Line Series"):                
                        # create plot
                        with dcg.Plot(C, label="Line Series", height=400, width=-1):
                            # By default plots are created with a legend.
                            # Three x axes and three y axes are available,
                            # and X1, Y1 are enabled by default and are the
                            # default axes for plot items.
                            dcg.PlotLine(C, X=sindatax, Y=sindatay, label="0.5 + 0.5 * sin(x)")

                    with dcg.TreeNode(C, label="Filled Line Series"):
                        fill_checkbox = dcg.Checkbox(C, label="fill", value=False)
                        segment_checkbox = dcg.Checkbox(C, label="segment", value=False)
                        with dcg.Plot(C, label="Filled Line Plot", height=400, width=-1):
                            filled_line_series = dcg.PlotLine(C, X=sindatax, Y=sindatay, label="0.5 + 0.5 * sin(x)")
                        
                        fill_checkbox.callback = lambda s, t, d: filled_line_series.configure(shaded=d)
                        segment_checkbox.callback = lambda s, t, d: filled_line_series.configure(segments=d)
                                
                    with dcg.TreeNode(C, label="Text"):                
                        # create plot
                        with dcg.Plot(C, label="Text", height=400, width=-1, equal_aspects=True):
                            with dcg.DrawInPlot(C, no_legend=False, label="Text"):
                                dcg.DrawText(C, text="This is just some text at the default size",
                                             pos=(0.5, 0.5),
                                             color=(255, 255, 0, 255))
                                dcg.DrawText(C, text="This text is at a custom fixed size",
                                             size=-20,
                                             pos=(0.5, 30.5),
                                             color=(255, 255, 0, 255))
                                dcg.DrawText(C, text="This text resizes with the plot",
                                             size=10,
                                             pos=(0.5, 60.5),
                                             color=(255, 255, 0, 255))
                            # The interest of text annotation over DrawText is that
                            # it can be clamped to the plot area, and can be put
                            # next to a target point.
                            dcg.PlotAnnotation(C, text="This is a text annotation",
                                               x=0.5, y=-20., clamp=True,
                                               bg_color=(255, 255, 0, 255))
                            dcg.PlotAnnotation(C, text="This is another text annotation",
                                               x=0.5, y=-40., clamp=True,
                                               theme=dcg.ThemeColorImPlot(C, inlay_text=(255, 255, 0, 255)))
                                
                    with dcg.TreeNode(C, label="Shade Series"):
                        std_alpha = 0.25

                        alpha_slider = dcg.Slider(C, min_value=0, max_value=1, 
                                                  speed=0.01, value=std_alpha)
                        
                        alpha_theme = dcg.ThemeStyleImPlot(C, fill_alpha=std_alpha)

                        with dcg.Plot(C, label="Shaded Plot", height=400, width=-1, theme=alpha_theme) as shaded_plot_1:
                            xs = np.linspace(0, 1, 1001)
                            np.random.seed(0)
                            ys = 0.25 + 0.25 * np.sin(25 * xs) * np.sin(5 * xs) + np.random.uniform(-0.01, 0.01, 1001)
                            ys1 = ys + np.random.uniform(0.1, 0.12, 1001)
                            ys2 = ys - np.random.uniform(0.1, 0.12, 1001)
                            ys3 = 0.75 + 0.2 * np.sin(25 * xs)
                            ys4 = 0.75 + 0.1 * np.cos(25 * xs)
                            dcg.PlotShadedLine(C, X=xs, Y1=ys1, Y2=ys2, label="Uncertain data")
                            dcg.PlotLine(C, X=xs, Y=ys, label="Uncertain data")
                            dcg.PlotShadedLine(C, X=xs, Y1=ys3, Y2=ys4, label="Overlapping")
                            dcg.PlotLine(C, X=xs, Y=ys3, label="Overlapping")
                            dcg.PlotLine(C, X=xs, Y=ys4, label="Overlapping")
                        def _cb_alpha(sender, target, value):
                            alpha_theme = dcg.ThemeStyleImPlot(C, fill_alpha=value)
                            shaded_plot_1.theme = alpha_theme

                        alpha_slider.callback = _cb_alpha

                        stock_datax = np.arange(100)
                        stock_data_y2 = np.zeros(100)
                        stock_data1 = 400 + 50 * np.abs(np.random.random(100))
                        stock_data2 = 275 + 75 * np.abs(np.random.random(100))
                        stock_data3 = 150 + 75 * np.abs(np.random.random(100))
                        stock_data4 = 500 + 75 * np.abs(np.random.random(100))
                        stock_data5 = 600 + 75 * np.abs(np.random.random(100))

                        stock_theme1 = dcg.ThemeColorImPlot(C,
                                                            line=(0, 0, 255),
                                                            fill=(0, 0, 255, 64))
                        stock_theme2 = dcg.ThemeColorImPlot(C,
                                                            line=(255, 0, 0),
                                                            fill=(255, 0, 0, 64))
                        stock_theme3 = dcg.ThemeColorImPlot(C,
                                                            line=(0, 255, 0),
                                                            fill=(0, 255, 0, 64))
                        stock_theme4 = dcg.ThemeColorImPlot(C,
                                                            fill=(255, 255, 100, 64))

                        with dcg.Plot(C, label="Stock Prices", height=400, width=-1) as stock_plot:
                            stock_plot.X1.label = "Days"
                            stock_plot.Y1.label = "Price"
                            dcg.PlotLine(C, X=stock_datax, Y=stock_data1, label="Stock 1", theme=stock_theme1)
                            dcg.PlotLine(C, X=stock_datax, Y=stock_data2, label="Stock 2", theme=stock_theme2)
                            dcg.PlotLine(C, X=stock_datax, Y=stock_data3, label="Stock 3", theme=stock_theme3)
                            dcg.PlotShadedLine(C, X=stock_datax, Y1=stock_data1, Y2=stock_data_y2, label="Stock 1", theme=stock_theme1)
                            dcg.PlotShadedLine(C, X=stock_datax, Y1=stock_data2, Y2=stock_data_y2, label="Stock 2", theme=stock_theme2)
                            dcg.PlotShadedLine(C, X=stock_datax, Y1=stock_data3, Y2=stock_data_y2, label="Stock 3", theme=stock_theme3)
                            dcg.PlotShadedLine(C, X=stock_datax, Y1=stock_data5, Y2=stock_data4, label="Shade between lines", theme=stock_theme4)

                    with dcg.TreeNode(C, label="Scatter Series"):
                        scatter_theme = dcg.ThemeStyleImPlot(C, marker=dcg.PlotMarker.CIRCLE)
                        def change_marker(sender, target, marker_name):
                            scatter_theme.marker = getattr(dcg.PlotMarker, marker_name.upper())

                        def change_size(sender, target, size):
                            scatter_theme.marker_size = size

                        with dcg.ChildWindow(C, width=-1, auto_resize_y=True, horizontal_scrollbar=True, no_scrollbar=True):
                            dcg.RadioButton(C, 
                                items=["Circle", "Square", "Diamond", "Up", "Down",
                                       "Left", "Right", "Cross", "Plus", "Asterisk"],
                                horizontal=True,
                                callback=change_marker
                            )

                        dcg.Slider(C, 
                            label="Marker Size",
                            min_value=2.0,
                            max_value=10.0,
                            value=scatter_theme.get_default("marker_size"),
                            callback=change_size
                        )

                        with dcg.Plot(C, label="Scatter Series", height=400, width=-1) as plot_scatter:
                            plot_scatter.X1.label = "X"
                            plot_scatter.Y1.label = "Y" 
                            dcg.PlotScatter(C, X=sindatax,
                                            Y=sindatay,
                                            label="0.5 + 0.5 * sin(x)",
                                            theme=scatter_theme)

                    with dcg.TreeNode(C, label="Stair Series"):
                        pre_step_cb = dcg.Checkbox(C, label="pre-step", value=False)
                        filled_stairs_cb = dcg.Checkbox(C, label="filled", value=False)
                        with dcg.Plot(C, label="Stair Plot", height=400, width=-1) as plot_stair:
                            plot_stair.X1.label = "X"
                            plot_stair.Y1.label = "Y"
                            stair_series = dcg.PlotStairs(C, X=sindatax, Y=sindatay, label="0.5 + 0.5 * sin(x)")
                        pre_step_cb.callback = lambda s, t, d: stair_series.configure(pre_step=d)
                        filled_stairs_cb.callback = lambda s, t, d: stair_series.configure(shaded=d)

                    with dcg.TreeNode(C, label="Bar Series"):
                        horizontal_bar_cb = dcg.Checkbox(C, label="horizontal", value=False)
                        with dcg.Plot(C, label="Bar Series", height=400, width=-1) as plot_bar:
                            plot_bar.X1.label = "Student"
                            plot_bar.X1.no_gridlines = True
                            plot_bar.X1.no_initial_fit = True
                            plot_bar.X1.min = 9
                            plot_bar.X1.max = 33
                            plot_bar.X1.labels = ("S1", "S2", "S3")
                            plot_bar.X1.labels_coord = (11, 21, 31)
                            plot_bar.X2.label = "hor_value"
                            plot_bar.X2.no_gridlines = True
                            plot_bar.X2.no_initial_fit = True
                            plot_bar.X2.min = 0
                            plot_bar.X2.max = 110
                            plot_bar.X2.enabled = True # Only X1/Y1 are enabled by default
                            plot_bar.Y1.label = "Score"
                            plot_bar.Y1.no_initial_fit = True
                            plot_bar.Y1.min = 0
                            plot_bar.Y1.max = 110

                            bar_series = dcg.PlotBars(C, X=[10, 20, 30], Y=[100, 75, 90], label="Final Exam", weight=1)
                            dcg.PlotBars(C, X=[11, 21, 31], Y=[83, 75, 72], label="Midterm Exam", weight=1)
                            dcg.PlotBars(C, X=[12, 22, 32], Y=[42, 68, 23], label="Course Grade", weight=1)
                        horizontal_bar_cb.callback = lambda s, t, d: bar_series.configure(horizontal=d)
                                

                    with dcg.TreeNode(C, label="Bar Group Series"):
                        horizontal_bar_group_cb = dcg.Checkbox(C, label="horizontal", value=False)
                        stacked_bar_group_cb = dcg.Checkbox(C, label="stacked", value=False)
                        slider_bar_group_width = dcg.Slider(C, min_value=0.1, max_value=1.0, value=0.67)
                        with dcg.Plot(C, label="Bar Group Series", height=400, width=-1) as plot_bar_group:
                            plot_bar_group.X1.label = "Student"
                            plot_bar_group.X1.no_gridlines = True
                            plot_bar_group.X1.no_initial_fit = True
                            plot_bar_group.X1.min = -0.5
                            plot_bar_group.X1.max = 9.5
            
                            values_group_series = [83, 67, 23, 89, 83, 78, 91, 82, 85, 90,
                                80, 62, 56, 99, 55, 78, 88, 78, 90, 100,
                                80, 69, 52, 92, 72, 78, 75, 76, 89, 95]
                            values_group_series = np.array(values_group_series).reshape(3, 10)
        
                            plot_bar_group.X1.labels = ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10")
                            plot_bar_group.X1.labels_coord = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
                            plot_bar_group.Y1.label = "Score"
                            plot_bar_group.Y1.no_initial_fit = True
                            plot_bar_group.Y1.min = 0
                            plot_bar_group.Y1.max = 110

                            bar_group_series = dcg.PlotBarGroups(C,
                                                                 values=values_group_series,
                                                                 labels=["Midterm Exam", "Final Exam", "Course Grade"])
                        
                        
                        def _set_horizontal(sender, target, data):
                            horizontal = bar_group_series.horizontal
                            if data == horizontal:
                                return
                            bar_group_series.horizontal = data
                            # swap configuration of Y1 and X1
                            config = plot_bar_group.X1
                            plot_bar_group.X1 = plot_bar_group.Y1
                            plot_bar_group.Y1 = config
                        
                        def _callback_stacked(sender, target, data):
                            bar_group_series.stacked = data

                        def _callback_width(sender, target, data):
                            bar_group_series.group_size = data

                        horizontal_bar_group_cb.callback = _set_horizontal
                        stacked_bar_group_cb.callback = _callback_stacked
                        slider_bar_group_width.callback = _callback_width

                    with dcg.TreeNode(C, label="Bar Stacks"):
                        politicians = (("Trump", 0), ("Bachman", 1), ("Cruz", 2), ("Gingrich", 3), ("Palin", 4), ("Santorum", 5),
                        ("Walker", 6), ("Perry", 7), ("Ryan", 8), ("McCain", 9), ("Rubio", 10), ("Romney", 11), ("Rand Paul", 12), ("Christie", 13),
                        ("Biden", 14), ("Kasich", 15), ("Sanders", 16), ("J Bush", 17), ("H Clinton", 18), ("Obama", 19))
                        data_reg = [18,26,7,14,10,8,6,11,4,4,3,8,6,8,6,5,0,3,1,2,  # Pants on Fire
                            43,36,30,21,30,27,25,17,11,22,15,16,16,17,12,12,14,6,13,12,  # False
                            16,13,28,22,15,21,15,18,30,17,24,18,13,10,14,15,17,22,14,12, # Mostly False
                            17,10,13,25,12,22,19,26,23,17,22,27,20,26,29,17,18,22,21,27, # Half True
                            5,7,16,10,10,12,23,13,17,20,22,16,23,19,20,26,36,29,27,26,   # Mostly True
                            1,8,6,8,23,10,12,15,15,20,14,15,22,20,19,25,15,18,24,21]    # True
                        labels_reg = ["Pants on Fire","False","Mostly False","Half True","Mostly True","True"]
                        data_reg = np.array(data_reg).reshape((len(labels_reg), -1))

                        data_div = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,                              # Pants on Fire (dummy, to order legend logically)
                            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,                                         # False         (dummy, to order legend logically)
                            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,                                         # Mostly False  (dummy, to order legend logically)
                            -16,-13,-28,-22,-15,-21,-15,-18,-30,-17,-24,-18,-13,-10,-14,-15,-17,-22,-14,-12, # Mostly False
                            -43,-36,-30,-21,-30,-27,-25,-17,-11,-22,-15,-16,-16,-17,-12,-12,-14,-6,-13,-12,  # False
                            -18,-26,-7,-14,-10,-8,-6,-11,-4,-4,-3,-8,-6,-8,-6,-5,0,-3,-1,-2,                 # Pants on Fire
                            17,10,13,25,12,22,19,26,23,17,22,27,20,26,29,17,18,22,21,27,                     # Half True
                            5,7,16,10,10,12,23,13,17,20,22,16,23,19,20,26,36,29,27,26,                       # Mostly True
                            1,8,6,8,23,10,12,15,15,20,14,15,22,20,19,25,15,18,24,21]                      # True
                        labels_div = ["Pants on Fire","False","Mostly False","Mostly False",
                        "False","Pants on Fire","Half True","Mostly True","True"]
                        data_div = np.array(data_div).reshape((len(labels_div), -1))
                        divergent_stack_checkbox = dcg.Checkbox(C, label="Divergent", value=True)
                        with dcg.Plot(C, label="PolitiFact: Who Lies More?", height=400, width=-1) as plot_bar_stacks:
                            plot_bar_stacks.X1.no_gridlines = True
                            plot_bar_stacks.Y1.no_gridlines = True
                            plot_bar_stacks.Y1.labels = [p[0] for p in politicians]
                            plot_bar_stacks.Y1.labels_coord = [p[1] for p in politicians]
                            plot_bar_stacks.Y1.min = -0.5
                            plot_bar_stacks.Y1.max = 19.5
                            plot_bar_stacks.Y1.no_initial_fit = True
                            bars_groups = dcg.PlotBarGroups(C, values=data_div, labels=labels_div, group_size=0.75, shift=0, stacked=True, horizontal=True)
                        
                        def divergent_stack_cb(sender, target, data):
                            if data:
                                bars_groups.configure(values=data_div, labels=labels_div)
                            else:
                                bars_groups.configure(values=data_reg, labels=labels_reg)
                        divergent_stack_checkbox.callback = divergent_stack_cb

                    with dcg.TreeNode(C, label="Error Series"):
                        error1_x = [1, 2, 3, 4, 5]
                        error1_y = [1, 2, 5, 3, 4]
                        error1_neg = [0.2, 0.4, 0.2, 0.6, 0.4]
                        error1_pos = [0.4, 0.2, 0.4, 0.8, 0.6]

                        error2_x = [1, 2, 3, 4, 5]
                        error2_y = [8, 8, 9, 7, 8]
                        error2_neg = [0.2, 0.4, 0.2, 0.6, 0.4]
                        error2_pos = [0.4, 0.2, 0.4, 0.8, 0.6]

                        with dcg.Plot(C, label="Error Series", height=400, width=-1) as plot_error_series:
                            plot_error_series.X1.label = "x"
                            plot_error_series.Y1.label = "y"
                            dcg.PlotBars(C, X=error1_x, Y=error1_y, label="Bar", weight=0.25)
                            dcg.PlotErrorBars(C, X=error1_x, Y=error1_y, negatives=error1_neg, positives=error1_pos, label="Bar")
                            dcg.PlotLine(C, X=error2_x, Y=error2_y, label="Line")
                            dcg.PlotErrorBars(C, X=error2_x, Y=error2_y, negatives=error2_neg, positives=error2_pos, label="Line")
                        
                    with dcg.TreeNode(C, label="Stem Series"):
                        with dcg.ThemeList(C) as stem_theme1:
                            dcg.ThemeColorImPlot(C, line=(0, 255, 0))
                            dcg.ThemeStyleImPlot(C, marker=dcg.PlotMarker.DIAMOND)
                        with dcg.Plot(C, label="Stem Series", height=400, width=-1) as plot_stem_series:
                            plot_stem_series.X1.label = "x"
                            plot_stem_series.Y1.label = "y"
                            dcg.PlotStems(C, X=sindatax, Y=sindatay, label="0.5 + 0.5 * sin(x)")
                            dcg.PlotStems(C, X=sindatax, Y=cosdatay, label="0.5 + 0.75 * cos(x)", theme=stem_theme1)

                    with dcg.TreeNode(C, label="Infinite Lines"):
                        infinite_x_data = (3, 5, 6, 7)
                        infinite_y_data = (3, 5, 6, 7)

                        with dcg.Plot(C, label="Infinite Lines", height=400, width=-1) as plot_inf_lines:
                            plot_inf_lines.X1.label = "x"
                            plot_inf_lines.Y1.label = "y"
                            dcg.PlotInfLines(C, X=infinite_x_data, label="vertical")
                            dcg.PlotInfLines(C, X=infinite_y_data, label="horizontal", horizontal=True)

                    with dcg.TreeNode(C, label="Pie Charts"):
                        with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.CENTER):
                            with dcg.Plot(C, label="Pie Series", height=250, width=250, no_mouse_pos=True) as plot_pie_series:
                                plot_pie_series.X1.no_gridlines = True
                                plot_pie_series.X1.no_tick_marks = True
                                plot_pie_series.X1.no_tick_labels = True
                                plot_pie_series.X1.no_initial_fit = True
                                plot_pie_series.X1.min = 0
                                plot_pie_series.X1.max = 1
                                plot_pie_series.Y1.no_gridlines = True
                                plot_pie_series.Y1.no_tick_marks = True
                                plot_pie_series.Y1.no_tick_labels = True
                                plot_pie_series.Y1.no_initial_fit = True
                                plot_pie_series.Y1.min = 0
                                plot_pie_series.Y1.max = 1
                                dcg.PlotPieChart(C, x=0.5, y=0.5, radius=0.5, values=[0.25, 0.30, 0.30], labels=["fish", "cow", "chicken"])

                            with dcg.Plot(C, label="Pie Series 2", height=250, width=250, no_mouse_pos=True) as plot_pie_series2:
                                plot_pie_series2.X1.no_gridlines = True
                                plot_pie_series2.X1.no_tick_marks = True
                                plot_pie_series2.X1.no_tick_labels = True
                                plot_pie_series2.X1.no_initial_fit = True
                                plot_pie_series2.X1.min = 0
                                plot_pie_series2.X1.max = 1
                                plot_pie_series2.Y1.no_gridlines = True
                                plot_pie_series2.Y1.no_tick_marks = True
                                plot_pie_series2.Y1.no_tick_labels = True
                                plot_pie_series2.Y1.no_initial_fit = True
                                plot_pie_series2.Y1.min = 0
                                plot_pie_series2.Y1.max = 1
                                dcg.PlotPieChart(C, x=0.5, y=0.5, radius=0.5, values=[1, 1, 2, 3, 5], labels=["A", "B", "C", "D", "E"], normalize=True, label_format="%.0f")

                    with dcg.TreeNode(C, label="Heatmaps"):
                        values = (0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0,
                                  2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0,
                                  1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0,
                                  0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0,
                                  0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0,
                                  1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1,
                                  0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3)
                        values = np.array(values).reshape((7, 7))
                        major_col_heat_cb = dcg.Checkbox(C, label="major col", value=False)
                        with dcg.Plot(C, label="Heat Series", height=400, width=-1) as plot_heat_series:
                            plot_heat_series.X1.label = "x"
                            plot_heat_series.X1.lock_min = True
                            plot_heat_series.X1.lock_max = True
                            plot_heat_series.X1.no_gridlines = True
                            plot_heat_series.X1.no_tick_marks = True
                            plot_heat_series.Y1.label = "y"
                            plot_heat_series.Y1.lock_min = True
                            plot_heat_series.Y1.lock_max = True
                            plot_heat_series.Y1.no_gridlines = True
                            plot_heat_series.Y1.no_tick_marks = True
                            # TODO colormap: dpg.add_colormap_scale(min_scale=0, max_scale=10, height=400)
                            heat_series = dcg.PlotHeatmap(C, values=values, label="heat_series", scale_min=0, scale_max=6.3)

                        major_col_heat_cb.callback = lambda s, t, d: heat_series.configure(col_major=d)

                    with dcg.TreeNode(C, label="Histogram Series"):
                        x_data = np.random.rand(10000) * 10 + 1
                        density_histograms_cb = dcg.Checkbox(C, label="density", value=False)
                        cumulative_histograms_cb = dcg.Checkbox(C, label="cumulative", value=False)
                        with dcg.Plot(C, label="Histogram Plot", height=400, width=-1) as plot_hist_series:
                            plot_hist_series.X1.label = "x"
                            plot_hist_series.X1.labels = ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10")
                            plot_hist_series.X1.labels_coord = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                            plot_hist_series.X1.no_initial_fit = True
                            plot_hist_series.X1.min = 1
                            plot_hist_series.X1.max = 10
                            plot_hist_series.Y1.label = "y"
                            plot_hist_series.Y1.auto_fit = True
                            hist_series = dcg.PlotHistogram(C, X=x_data, label="histogram")

                        density_histograms_cb.callback = lambda s, t, d: hist_series.configure(density=d)
                        cumulative_histograms_cb.callback = lambda s, t, d: hist_series.configure(cumulative=d)

                    with dcg.TreeNode(C, label="Histogram 2D Series"):
                        slider_hist_count = dcg.Slider(C, print_format="%.0f", width=300, min_value=100, max_value=100000, value=1000)
                        slider_hist_bins = dcg.utils.SliderN(C, print_format="%.0f", width=300, min_value=1, max_value=500, values=(50, 50))
                        checkbox_hist_density = dcg.Checkbox(C, label="density", value=False)

                        with dcg.Plot(C, label="Histogram 2D Plot", height=400, width=650) as plot_hist_2d:
                            plot_hist_2d.X1.label = "x"
                            plot_hist_2d.X1.auto_fit = True
                            plot_hist_2d.Y1.label = "y"
                            plot_hist_2d.Y1.auto_fit = True
                            hist_2d_series = dcg.PlotHistogram2D(C, label="histogram 2D")

                        with dcg.Plot(C, label="Histogram 2D Plot selection", height=400, width=650) as plot_hist_2d2:
                            plot_hist_2d2.X1.label = "x"
                            plot_hist_2d2.X1.auto_fit = True
                            plot_hist_2d2.Y1.label = "y"
                            plot_hist_2d2.Y1.auto_fit = True
                            hist_2d_series2 = dcg.PlotHistogram2D(C, label="histogram 2D")
                            hist_2d_series2.range_x = (-4, 4)
                            hist_2d_series2.range_y = (-4, 4)

                        def update_count(sender, target, data):
                            x_dist = np.random.normal(1, 2, data)
                            y_dist = np.random.normal(1, 1, data)
                            hist_2d_series.configure(X=x_dist, Y=y_dist)
                            hist_2d_series2.configure(X=x_dist, Y=y_dist)
                            # TODO dpg.configure_item("2d_hist_colormap_scale", max_scale=max_count)
                        def update_bins(sender, target, data):
                            hist_2d_series.configure(x_bins=data[0], y_bins=data[1])
                            hist_2d_series2.configure(x_bins=data[0], y_bins=data[1])
                        def update_density(sender, target, data):
                            # Note: doesn't have any visual effect due to scale/colormap
                            hist_2d_series.density=data
                            hist_2d_series2.density=data

                        # Initialize plot
                        update_count(None, None, 1000)
                        update_bins(None, None, (50, 50))

                        slider_hist_count.callback = update_count
                        slider_hist_bins.callback = update_bins
                        # TODO colormap scale
                        checkbox_hist_density.callback = update_density

                    with dcg.TreeNode(C, label="Digital Plots"):
                        dcg.Text(C, value="Digital plots do not respond to Y drag and zoom, so that", marker="bullet")
                        dcg.Text(C, value="you can drag analog plots over the rising/falling digital edge.", x=20)
                        with dcg.Plot(C, label="Digital Plot", height=400, width=-1) as plot_digital:
                            plot_digital.X1.label = "x"
                            plot_digital.X1.min = -10
                            plot_digital.X1.max = 0
                            plot_digital.X1.lock_min = True
                            plot_digital.X1.lock_max = True
                            plot_digital.Y1.label = "y"
                            plot_digital.Y1.min = -2
                            plot_digital.Y1.max = 1.5
                            digital_0 = dcg.PlotDigital(C, label="digital_0")
                            digital_1 = dcg.PlotDigital(C, label="digital_1")
                            analog_0 = dcg.PlotLine(C, label="analog_0")
                            analog_1 = dcg.PlotLine(C, label="analog_1")

                        def update_digital_plot():
                            t_digital_plot = plot_digital.user_data
                            if t_digital_plot is None:
                                t_digital_plot = 0
                            t_digital_plot += C.viewport.metrics.delta_whole_frame
                            plot_digital.X1.min = t_digital_plot - 10
                            plot_digital.X1.max = t_digital_plot
                            digital_0.X = np.concatenate([digital_0.X, [t_digital_plot]], axis=None)
                            digital_0.Y = np.concatenate([digital_0.Y, [1. if sin(t_digital_plot) > 0.45 else 0.]], axis=None)
                            digital_1.X = np.concatenate([digital_1.X, [t_digital_plot]], axis=None)
                            digital_1.Y = np.concatenate([digital_1.Y, [1. if sin(t_digital_plot) < 0.45 else 0.]], axis=None)
                            analog_0.X = np.concatenate([analog_0.X, [t_digital_plot]], axis=None)
                            analog_0.Y = np.concatenate([analog_0.Y, [sin(t_digital_plot)]], axis=None)
                            analog_1.X = np.concatenate([analog_1.X, [t_digital_plot]], axis=None)
                            analog_1.Y = np.concatenate([analog_1.Y, [cos(t_digital_plot)]], axis=None)
                            plot_digital.user_data = t_digital_plot

                        plot_digital.handlers = [dcg.RenderHandler(C, callback=update_digital_plot)]

                    with dcg.TreeNode(C, label="Candle Stick Series"):
                        dates = [1546300800,1546387200,1546473600,1546560000,1546819200,1546905600,1546992000,1547078400,1547164800,1547424000,1547510400,1547596800,1547683200,1547769600,1547942400,1548028800,1548115200,1548201600,1548288000,1548374400,1548633600,1548720000,1548806400,1548892800,1548979200,1549238400,1549324800,1549411200,1549497600,1549584000,1549843200,1549929600,1550016000,1550102400,1550188800,1550361600,1550448000,1550534400,1550620800,1550707200,1550793600,1551052800,1551139200,1551225600,1551312000,1551398400,1551657600,1551744000,1551830400,1551916800,1552003200,1552262400,1552348800,1552435200,1552521600,1552608000,1552867200,1552953600,1553040000,1553126400,1553212800,1553472000,1553558400,1553644800,1553731200,1553817600,1554076800,1554163200,1554249600,1554336000,1554422400,1554681600,1554768000,1554854400,1554940800,1555027200,1555286400,1555372800,1555459200,1555545600,1555632000,1555891200,1555977600,1556064000,1556150400,1556236800,1556496000,1556582400,1556668800,1556755200,1556841600,1557100800,1557187200,1557273600,1557360000,1557446400,1557705600,1557792000,1557878400,1557964800,1558051200,1558310400,1558396800,1558483200,1558569600,1558656000,1558828800,1558915200,1559001600,1559088000,1559174400,1559260800,1559520000,1559606400,1559692800,1559779200,1559865600,1560124800,1560211200,1560297600,1560384000,1560470400,1560729600,1560816000,1560902400,1560988800,1561075200,1561334400,1561420800,1561507200,1561593600,1561680000,1561939200,1562025600,1562112000,1562198400,1562284800,1562544000,1562630400,1562716800,1562803200,1562889600,1563148800,1563235200,1563321600,1563408000,1563494400,1563753600,1563840000,1563926400,1564012800,1564099200,1564358400,1564444800,1564531200,1564617600,1564704000,1564963200,1565049600,1565136000,1565222400,1565308800,1565568000,1565654400,1565740800,1565827200,1565913600,1566172800,1566259200,1566345600,1566432000,1566518400,1566777600,1566864000,1566950400,1567036800,1567123200,1567296000,1567382400,1567468800,1567555200,1567641600,1567728000,1567987200,1568073600,1568160000,1568246400,1568332800,1568592000,1568678400,1568764800,1568851200,1568937600,1569196800,1569283200,1569369600,1569456000,1569542400,1569801600,1569888000,1569974400,1570060800,1570147200,1570406400,1570492800,1570579200,1570665600,1570752000,1571011200,1571097600,1571184000,1571270400,1571356800,1571616000,1571702400,1571788800,1571875200,1571961600]
                        opens = [1284.7,1319.9,1318.7,1328,1317.6,1321.6,1314.3,1325,1319.3,1323.1,1324.7,1321.3,1323.5,1322,1281.3,1281.95,1311.1,1315,1314,1313.1,1331.9,1334.2,1341.3,1350.6,1349.8,1346.4,1343.4,1344.9,1335.6,1337.9,1342.5,1337,1338.6,1337,1340.4,1324.65,1324.35,1349.5,1371.3,1367.9,1351.3,1357.8,1356.1,1356,1347.6,1339.1,1320.6,1311.8,1314,1312.4,1312.3,1323.5,1319.1,1327.2,1332.1,1320.3,1323.1,1328,1330.9,1338,1333,1335.3,1345.2,1341.1,1332.5,1314,1314.4,1310.7,1314,1313.1,1315,1313.7,1320,1326.5,1329.2,1314.2,1312.3,1309.5,1297.4,1293.7,1277.9,1295.8,1295.2,1290.3,1294.2,1298,1306.4,1299.8,1302.3,1297,1289.6,1302,1300.7,1303.5,1300.5,1303.2,1306,1318.7,1315,1314.5,1304.1,1294.7,1293.7,1291.2,1290.2,1300.4,1284.2,1284.25,1301.8,1295.9,1296.2,1304.4,1323.1,1340.9,1341,1348,1351.4,1351.4,1343.5,1342.3,1349,1357.6,1357.1,1354.7,1361.4,1375.2,1403.5,1414.7,1433.2,1438,1423.6,1424.4,1418,1399.5,1435.5,1421.25,1434.1,1412.4,1409.8,1412.2,1433.4,1418.4,1429,1428.8,1420.6,1441,1460.4,1441.7,1438.4,1431,1439.3,1427.4,1431.9,1439.5,1443.7,1425.6,1457.5,1451.2,1481.1,1486.7,1512.1,1515.9,1509.2,1522.3,1513,1526.6,1533.9,1523,1506.3,1518.4,1512.4,1508.8,1545.4,1537.3,1551.8,1549.4,1536.9,1535.25,1537.95,1535.2,1556,1561.4,1525.6,1516.4,1507,1493.9,1504.9,1506.5,1513.1,1506.5,1509.7,1502,1506.8,1521.5,1529.8,1539.8,1510.9,1511.8,1501.7,1478,1485.4,1505.6,1511.6,1518.6,1498.7,1510.9,1510.8,1498.3,1492,1497.7,1484.8,1494.2,1495.6,1495.6,1487.5,1491.1,1495.1,1506.4]
                        highs = [1284.75,1320.6,1327,1330.8,1326.8,1321.6,1326,1328,1325.8,1327.1,1326,1326,1323.5,1322.1,1282.7,1282.95,1315.8,1316.3,1314,1333.2,1334.7,1341.7,1353.2,1354.6,1352.2,1346.4,1345.7,1344.9,1340.7,1344.2,1342.7,1342.1,1345.2,1342,1350,1324.95,1330.75,1369.6,1374.3,1368.4,1359.8,1359,1357,1356,1353.4,1340.6,1322.3,1314.1,1316.1,1312.9,1325.7,1323.5,1326.3,1336,1332.1,1330.1,1330.4,1334.7,1341.1,1344.2,1338.8,1348.4,1345.6,1342.8,1334.7,1322.3,1319.3,1314.7,1316.6,1316.4,1315,1325.4,1328.3,1332.2,1329.2,1316.9,1312.3,1309.5,1299.6,1296.9,1277.9,1299.5,1296.2,1298.4,1302.5,1308.7,1306.4,1305.9,1307,1297.2,1301.7,1305,1305.3,1310.2,1307,1308,1319.8,1321.7,1318.7,1316.2,1305.9,1295.8,1293.8,1293.7,1304.2,1302,1285.15,1286.85,1304,1302,1305.2,1323,1344.1,1345.2,1360.1,1355.3,1363.8,1353,1344.7,1353.6,1358,1373.6,1358.2,1369.6,1377.6,1408.9,1425.5,1435.9,1453.7,1438,1426,1439.1,1418,1435,1452.6,1426.65,1437.5,1421.5,1414.1,1433.3,1441.3,1431.4,1433.9,1432.4,1440.8,1462.3,1467,1443.5,1444,1442.9,1447,1437.6,1440.8,1445.7,1447.8,1458.2,1461.9,1481.8,1486.8,1522.7,1521.3,1521.1,1531.5,1546.1,1534.9,1537.7,1538.6,1523.6,1518.8,1518.4,1514.6,1540.3,1565,1554.5,1556.6,1559.8,1541.9,1542.9,1540.05,1558.9,1566.2,1561.9,1536.2,1523.8,1509.1,1506.2,1532.2,1516.6,1519.7,1515,1519.5,1512.1,1524.5,1534.4,1543.3,1543.3,1542.8,1519.5,1507.2,1493.5,1511.4,1525.8,1522.2,1518.8,1515.3,1518,1522.3,1508,1501.5,1503,1495.5,1501.1,1497.9,1498.7,1492.1,1499.4,1506.9,1520.9]
                        lows = [1282.85,1315,1318.7,1309.6,1317.6,1312.9,1312.4,1319.1,1319,1321,1318.1,1321.3,1319.9,1312,1280.5,1276.15,1308,1309.9,1308.5,1312.3,1329.3,1333.1,1340.2,1347,1345.9,1338,1340.8,1335,1332,1337.9,1333,1336.8,1333.2,1329.9,1340.4,1323.85,1324.05,1349,1366.3,1351.2,1349.1,1352.4,1350.7,1344.3,1338.9,1316.3,1308.4,1306.9,1309.6,1306.7,1312.3,1315.4,1319,1327.2,1317.2,1320,1323,1328,1323,1327.8,1331.7,1335.3,1336.6,1331.8,1311.4,1310,1309.5,1308,1310.6,1302.8,1306.6,1313.7,1320,1322.8,1311,1312.1,1303.6,1293.9,1293.5,1291,1277.9,1294.1,1286,1289.1,1293.5,1296.9,1298,1299.6,1292.9,1285.1,1288.5,1296.3,1297.2,1298.4,1298.6,1302,1300.3,1312,1310.8,1301.9,1292,1291.1,1286.3,1289.2,1289.9,1297.4,1283.65,1283.25,1292.9,1295.9,1290.8,1304.2,1322.7,1336.1,1341,1343.5,1345.8,1340.3,1335.1,1341.5,1347.6,1352.8,1348.2,1353.7,1356.5,1373.3,1398,1414.7,1427,1416.4,1412.7,1420.1,1396.4,1398.8,1426.6,1412.85,1400.7,1406,1399.8,1404.4,1415.5,1417.2,1421.9,1415,1413.7,1428.1,1434,1435.7,1427.5,1429.4,1423.9,1425.6,1427.5,1434.8,1422.3,1412.1,1442.5,1448.8,1468.2,1484.3,1501.6,1506.2,1498.6,1488.9,1504.5,1518.3,1513.9,1503.3,1503,1506.5,1502.1,1503,1534.8,1535.3,1541.4,1528.6,1525.6,1535.25,1528.15,1528,1542.6,1514.3,1510.7,1505.5,1492.1,1492.9,1496.8,1493.1,1503.4,1500.9,1490.7,1496.3,1505.3,1505.3,1517.9,1507.4,1507.1,1493.3,1470.5,1465,1480.5,1501.7,1501.4,1493.3,1492.1,1505.1,1495.7,1478,1487.1,1480.8,1480.6,1487,1488.3,1484.8,1484,1490.7,1490.4,1503.1]
                        closes = [1283.35,1315.3,1326.1,1317.4,1321.5,1317.4,1323.5,1319.2,1321.3,1323.3,1319.7,1325.1,1323.6,1313.8,1282.05,1279.05,1314.2,1315.2,1310.8,1329.1,1334.5,1340.2,1340.5,1350,1347.1,1344.3,1344.6,1339.7,1339.4,1343.7,1337,1338.9,1340.1,1338.7,1346.8,1324.25,1329.55,1369.6,1372.5,1352.4,1357.6,1354.2,1353.4,1346,1341,1323.8,1311.9,1309.1,1312.2,1310.7,1324.3,1315.7,1322.4,1333.8,1319.4,1327.1,1325.8,1330.9,1325.8,1331.6,1336.5,1346.7,1339.2,1334.7,1313.3,1316.5,1312.4,1313.4,1313.3,1312.2,1313.7,1319.9,1326.3,1331.9,1311.3,1313.4,1309.4,1295.2,1294.7,1294.1,1277.9,1295.8,1291.2,1297.4,1297.7,1306.8,1299.4,1303.6,1302.2,1289.9,1299.2,1301.8,1303.6,1299.5,1303.2,1305.3,1319.5,1313.6,1315.1,1303.5,1293,1294.6,1290.4,1291.4,1302.7,1301,1284.15,1284.95,1294.3,1297.9,1304.1,1322.6,1339.3,1340.1,1344.9,1354,1357.4,1340.7,1342.7,1348.2,1355.1,1355.9,1354.2,1362.1,1360.1,1408.3,1411.2,1429.5,1430.1,1426.8,1423.4,1425.1,1400.8,1419.8,1432.9,1423.55,1412.1,1412.2,1412.8,1424.9,1419.3,1424.8,1426.1,1423.6,1435.9,1440.8,1439.4,1439.7,1434.5,1436.5,1427.5,1432.2,1433.3,1441.8,1437.8,1432.4,1457.5,1476.5,1484.2,1519.6,1509.5,1508.5,1517.2,1514.1,1527.8,1531.2,1523.6,1511.6,1515.7,1515.7,1508.5,1537.6,1537.2,1551.8,1549.1,1536.9,1529.4,1538.05,1535.15,1555.9,1560.4,1525.5,1515.5,1511.1,1499.2,1503.2,1507.4,1499.5,1511.5,1513.4,1515.8,1506.2,1515.1,1531.5,1540.2,1512.3,1515.2,1506.4,1472.9,1489,1507.9,1513.8,1512.9,1504.4,1503.9,1512.8,1500.9,1488.7,1497.6,1483.5,1494,1498.3,1494.1,1488.1,1487.5,1495.7,1504.7,1505.3]
                        # convert to numpy arrays
                        dates = np.array(dates, dtype=np.float64)
                        opens = np.array(opens, dtype=np.float64)
                        closes = np.array(closes, dtype=np.float64)
                        lows = np.array(lows, dtype=np.float64)
                        highs = np.array(highs, dtype=np.float64)

                        with dcg.Plot(C, label="Candle Stick Plot", height=400, width=-1) as plot_candle:
                            plot_candle.X1.label = "Date"
                            plot_candle.X1.scale = dcg.AxisScale.TIME
                            plot_candle.Y1.label = "USD"
                            dcg.utils.PlotCandleStick(C,
                                                      dates=dates,
                                                      opens=opens,
                                                      closes=closes,
                                                      lows=lows,
                                                      highs=highs,
                                                      label="GOOGL",
                                                      time_formatter = lambda x: f"Days: {datetime.datetime.fromtimestamp(x).day}"
                                                      )

                with dcg.Tab(C, label="Subplots"):
                    with dcg.TreeNode(C, label="Basic"):
                        with dcg.Subplots(C, cols=3, rows=3, label="My Subplots", width=-1, height=600, row_ratios=[5.0, 1.0, 1.0], col_ratios=[5.0, 1.0, 1.0]) as subplot:
                            for i in range(9):
                                with dcg.Plot(C, no_title=True) as plot:
                                    plot.X1.no_tick_labels = True
                                    plot.Y1.no_tick_labels = True
                                    dcg.PlotLine(C, X=sindatax, Y=sindatay, label="0.5 + 0.5 * sin(x)")
                        ConfigureOptions(C, subplot, 1, "no_resize", "no_title", before=subplot)

                    with dcg.TreeNode(C, label="Item Sharing"):
                        with dcg.Subplots(C, cols=3, rows=2, label="My Subplots", width=-1, height=600, row_ratios=[5.0, 1.0, 1.0], col_ratios=[5.0, 1.0, 1.0]) as subplot:
                            for i in range(6):
                                with dcg.Plot(C, no_title=True) as plot:
                                    plot.X1.no_tick_labels = True
                                    plot.Y1.no_tick_labels = True
                                    dcg.PlotLine(C, X=sindatax, Y=sindatay, label="data" + str(i))
                        ConfigureOptions(C, subplot, 1, "col_major", before=subplot)

                    with dcg.TreeNode(C, label="Linked Axes"):
                        with dcg.Subplots(C, cols=2, rows=2, label="My Subplots", width=-1, height=600, row_ratios=[5.0, 1.0, 1.0], col_ratios=[5.0, 1.0, 1.0]) as subplot:
                            for i in range(4):
                                with dcg.Plot(C, no_title=True) as plot:
                                    plot.X1.no_tick_labels = True
                                    plot.Y1.no_tick_labels = True
                                    dcg.PlotLine(C, X=sindatax, Y=sindatay, label="data" + str(i))
                        ConfigureOptions(C, subplot, 2, "no_align", "share_legends", before=subplot)

                with dcg.Tab(C, label="Axes"):
                    with dcg.TreeNode(C, label="Time Axes"):
                        timedatax = np.arange(0, 739497600, 60*60*24*7)
                        timedatay = timedatax / (60*60*24)
                
                        dcg.Text(C, value="When time is enabled, x-axis values are interpreted as UNIX timestamps in seconds (e.g. 1599243545).", marker="bullet")
                        dcg.Text(C, value="UNIX timestamps are seconds since 00:00:00 UTC on 1 January 1970", marker="bullet")
                        with dcg.Plot(C, label="Time Plot", height=400, width=-1) as plot:
                            plot.X1.label = "Date"
                            plot.X1.scale = dcg.AxisScale.TIME
                            plot.Y1.label = "Days since 1970"
                            dcg.PlotLine(C, X=timedatax, Y=timedatay, label="Days")

                    with dcg.TreeNode(C, label="Multi Axes Plot"):                        
                        show_y1 = dcg.Checkbox(C, label="Show Y1", value=True)
                        show_y2 = dcg.Checkbox(C, label="Show Y2", value=True)
                        show_y3 = dcg.Checkbox(C, label="Show Y3", value=True)
                        show_x1 = dcg.Checkbox(C, label="Show X1", value=True)
                        show_x2 = dcg.Checkbox(C, label="Show X2", value=True)
                        show_x3 = dcg.Checkbox(C, label="Show X3", value=True)

                        with dcg.Plot(C, label="Multi Axes Plot", height=400, width=-1) as multi_axes_plot:
                            multi_axes_plot.X1.label = "x1"
                            multi_axes_plot.Y1.label = "y1"
                            dcg.PlotLine(C, X=sindatax, Y=sindatay, label="y1")
                            multi_axes_plot.X2.label = "x2"
                            multi_axes_plot.X2.opposite = True
                            multi_axes_plot.X2.enabled = True # by default only X1/Y1 are enabled
                            multi_axes_plot.Y2.label = "y2"
                            multi_axes_plot.Y2.opposite = True
                            multi_axes_plot.Y2.enabled = True
                            dcg.PlotLine(C, X=sindatax, Y=cosdatay, label="y2")
                            multi_axes_plot.X3.label = "x3"
                            multi_axes_plot.X3.enabled = True
                            multi_axes_plot.Y3.label = "y3"
                            multi_axes_plot.Y3.enabled = True
                            dcg.PlotLine(C, X=sindatax, Y=sindatay, label="0.5 + 0.5 * sin(x)")
                        show_y1.callback = lambda s, t, d: multi_axes_plot.Y1.configure(enabled=d)
                        show_y2.callback = lambda s, t, d: multi_axes_plot.Y2.configure(enabled=d)
                        show_y3.callback = lambda s, t, d: multi_axes_plot.Y3.configure(enabled=d)
                        show_x1.callback = lambda s, t, d: multi_axes_plot.X1.configure(enabled=d)
                        show_x2.callback = lambda s, t, d: multi_axes_plot.X2.configure(enabled=d)
                        show_x3.callback = lambda s, t, d: multi_axes_plot.X3.configure(enabled=d)

                    with dcg.TreeNode(C, label="Ordering Axes Plot"):
                        opposite_x = dcg.Checkbox(C, label="Opposite X", value=False)
                        invert_x = dcg.Checkbox(C, label="Invert X", value=False)
                        opposite_y = dcg.Checkbox(C, label="Opposite Y", value=False)
                        invert_y = dcg.Checkbox(C, label="Invert Y", value=False)

                        with dcg.Plot(C, label="Ordering Axes Plot", height=400, width=-1) as ordering_axes_plot:
                            ordering_axes_plot.X1.label = "x"
                            ordering_axes_plot.Y1.label = "y"
                            dcg.PlotLine(C, X=sindatax, Y=sindatay)

                        opposite_x.callback = lambda s, t, d: ordering_axes_plot.X1.configure(opposite=d)
                        invert_x.callback = lambda s, t, d: ordering_axes_plot.X1.configure(invert=d)
                        opposite_y.callback = lambda s, t, d: ordering_axes_plot.Y1.configure(opposite=d)
                        invert_y.callback = lambda s, t, d: ordering_axes_plot.Y1.configure(invert=d)

                    with dcg.TreeNode(C, label="Log Axis Scale"):
                        xs = np.linspace(0.1, 100, 1000)
                        ys1 = np.sin(xs) + 1
                        ys2 = np.log10(1+xs)
                        ys3 = np.power(10.0, xs)

                        with dcg.Plot(C, label="Log Axes Plot", height=400, width=-1) as log_axis_plot:
                            log_axis_plot.X1.label = "x1"
                            log_axis_plot.X1.min = 0.1
                            log_axis_plot.X1.max = 100
                            log_axis_plot.Y1.label = "y1"
                            log_axis_plot.Y1.scale = dcg.AxisScale.LOG10
                            log_axis_plot.Y1.min = 0
                            log_axis_plot.Y1.max = 10
                            dcg.PlotLine(C, X=xs, Y=xs, label="x")
                            dcg.PlotLine(C, X=xs, Y=ys1, label="sin(x)+1")
                            dcg.PlotLine(C, X=xs, Y=ys2, label="log(1+x)")
                            dcg.PlotLine(C, X=xs, Y=ys3, label="10^x")
                    
                    with dcg.TreeNode(C, label="Time Axis"):
                        t_min = 1609459200 # 01/01/2021 @ 12:00:00am (UTC)
                        t_max = 1640995200 # 01/01/2022 @ 12:00:00am (UTC)
                        xs = np.arange(t_min, t_max, 86400)
                        ys1 = np.sin(xs)
                        ys2 = np.cos(xs)

                        with dcg.Plot(C, label="Time Plot", height=400, width=-1) as time_axis_plot:
                            time_axis_plot.X1.label = "Time"
                            time_axis_plot.X1.scale = dcg.AxisScale.TIME
                            time_axis_plot.X1.min = t_min
                            time_axis_plot.X1.max = t_max
                            dcg.PlotLine(C, X=xs, Y=ys1, label="sin(x)")
                            dcg.PlotLine(C, X=xs, Y=ys2, label="cos(x)")

                    with dcg.TreeNode(C, label="Symmetric Log Axis Scale"):
                        indices = np.arange(1000)
                        xs = indices * 0.1 - 50
                        ys1 = np.sin(xs)
                        ys2 = indices * 0.002 - 1

                        with dcg.Plot(C, label="Symmetric Log Axes Plot", height=400, width=-1) as symmetric_log_axes_plot:
                            symmetric_log_axes_plot.X1.label = "x1"
                            symmetric_log_axes_plot.X1.scale = dcg.AxisScale.SYMLOG
                            symmetric_log_axes_plot.Y1.label = "y1"
                            dcg.PlotLine(C, X=xs, Y=ys1, label="y1")
                            dcg.PlotLine(C, X=xs, Y=ys2, label="y2")

                with dcg.Tab(C, label="Tools"):
                    with dcg.TreeNode(C, label="Interactables and dragging items"):
                        with dcg.Plot(C, label="Dragging elements", height=400, width=-1) as plot:
                            plot.X1.label = "x"
                            plot.Y1.label = "y"
                            with dcg.DrawInPlot(C):
                                interactable_area = dcg.DrawInvisibleButton(C, p1=(-1, 0), p2=(-0.5, 0.5), min_side=50)
                                interactable_rect = dcg.DrawRect(C, pmin=(-1, 0), pmax=(-0.5, 0.5), fill=(220, 170, 170), thickness=-1)
                                dcg.DrawTextQuad(C, text="Hover me!",
                                                 p1=(-0.95, 0.05), p2=(-0.55, 0.05),
                                                 p3=(-0.55, 0.45), p4=(-0.95, 0.45),
                                                 color=(0, 0, 0),
                                                 preserve_ratio=True)

                                d1 = dcg.utils.DragPoint(C, color=(255, 0, 255), x=0.25, y=0.25)
                                d2 = dcg.utils.DragPoint(C, color=(255, 0, 255), clamp_inside=True, x=0.75, y=0.75)
                                l1 = dcg.utils.DragHLine(C, color=(0, 255, 0), y=0.5)
                                l2 = dcg.utils.DragVLine(C, color=(0, 255, 0), x=0.5)
                                r1 = dcg.utils.DragRect(C, color=(0, 0, 255), rect=(0.1, 0.1, 0.4, 0.4), on_dragged=lambda s, t, d: print(f"DragRect was dragged at {d}"))
                        drag_text = dcg.Text(C, value="")
                        d1.on_dragging = lambda s, t, d: drag_text.configure(value=f"dpoint1 is being dragged at {d}")
                        d1.on_dragged = lambda s, t, d: drag_text.configure(value=f"dpoint1 was dragged at {d}")
                        d1.handlers += [dcg.LostHoverHandler(C, callback=lambda: drag_text.configure(value="dpoint1 lost hover"))]
                        d2.on_dragging = lambda s, t, d: drag_text.configure(value=f"dpoint2 is being dragged at {d}")
                        d2.on_dragged = lambda s, t, d: drag_text.configure(value=f"dpoint2 was dragged at {d}")
                        d2.handlers += [dcg.LostHoverHandler(C, callback=lambda: drag_text.configure(value="dpoint2 lost hover"))]
                        interactable_area.handlers += [
                            dcg.GotHoverHandler(C, callback=lambda: interactable_rect.configure(fill=(170, 220, 220))),
                            dcg.LostHoverHandler(C, callback=lambda: interactable_rect.configure(fill=(220, 170, 170))),
                        ]
                    with dcg.TreeNode(C, label="Querying"):
                        dcg.Text(C, value="Make your custom query behaviour out of interactable items")
                        dcg.Text(C, value="In this example the commands are:")
                        # If you need another button than left click you should copy paste the
                        # DragRect implementation and change the button parameter for the Dragging handlers
                        dcg.Text(C, marker=dcg.TextMarker.BULLET, value="Left click to box select and then double click on the item to delete")

                        with dcg.Plot(C, label="Query Plot", height=400, width=-1, no_menus=True, pan_button=dcg.MouseButton.RIGHT) as query_plot:
                            query_plot.X1.label = "x"
                            query_plot.Y1.label = "y"
                            # add a line series to the plot
                            dcg.PlotLine(C, X=sindatax, Y=sindatay, label="0.5 + 0.5 * sin(x)")

                        with dcg.Plot(C, label="Zoom view", height=400, width=-1, no_menus=True) as query_plot_2:
                            query_plot_2.X1.label = "x"
                            query_plot_2.Y1.label = "y"
                            # add a line series to the plot
                            dcg.PlotLine(C, X=sindatax, Y=sindatay, label="0.5 + 0.5 * sin(x)")

                        # Define commands:
                        def set_zoom_limits(sender, target, data):
                            rect = target.rect
                            x1, y1, x2, y2 = rect
                            # Set the axis limits based on the rectangle coordinates
                            query_plot_2.X1.min = min(x1, x2)
                            query_plot_2.X1.max = max(x1, x2)
                            query_plot_2.Y1.min = min(y1, y2)
                            query_plot_2.Y1.max = max(y1, y2)

                        def create_query_rect(sender, target, data):
                            x = query_plot.X1.mouse_coord
                            y = query_plot.Y1.mouse_coord
                            drag_container = dcg.DrawInPlot(C, parent=query_plot, ignore_fit=True)
                            drag_rect = dcg.utils.DragRect(C, color=(255, 0, 255), rect=(x, y, x, y),
                                                           on_dragging=set_zoom_limits,
                                                           capture_mouse=True,
                                                           parent=drag_container)
                            drag_rect.handlers += [
                                dcg.DoubleClickedHandler(C, button=dcg.MouseButton.LEFT, callback=lambda s, t, d: drag_container.delete_item()),
                            ]

                        query_plot.handlers += [dcg.ClickedHandler(C, button=dcg.MouseButton.LEFT, callback=create_query_rect)]

                    with dcg.TreeNode(C, label="Annotations"):
                        with dcg.Plot(C, label="Annotations", height=400, width=-1) as plot:
                            plot.X1.label = "x"
                            plot.Y1.label = "y"
                            dcg.PlotLine(C, X=sindatax, Y=sindatay, label="0.5 + 0.5 * sin(x)")
                            dcg.PlotAnnotation(C, text="BL", x=0.25, y=0.25, offset=(-15, 15), bg_color=[255, 255, 0, 255])
                            dcg.PlotAnnotation(C, text="BR", x=0.75, y=0.25, offset=(15, 15), bg_color=[255, 255, 0, 255])
                            dcg.PlotAnnotation(C, text="TR clampled", x=0.75, y=0.75, offset=(-15, -15), bg_color=[255, 255, 0, 255], clamp=True)
                            dcg.PlotAnnotation(C, text="TL", x=0.25, y=0.75, offset=(-15, -15), bg_color=[255, 255, 0, 255])
                            dcg.PlotAnnotation(C, text="Center", x=0.5, y=0.5, bg_color=[255, 255, 0, 255])

                    with dcg.TreeNode(C, label="Tags"):
                        with dcg.Plot(C, label="Tags", height=400, width=-1) as plot:
                            plot.X1.label = "x"
                            plot.Y1.label = "y"
                            dcg.PlotLine(C, X=sindatax, Y=sindatay, label="0.5 + 0.5 * sin(x)")
                            with plot.X1:
                                # Axes tags are the only accepted children of axes
                                dcg.AxisTag(C, coord=0.25, bg_color=(255, 255, 0, 255), text="0.25")
                            with plot.Y1:
                                # Contrary to Dear PyGui, text must always be provided
                                # (DPG will automatically set it to the coord if not provided)
                                dcg.AxisTag(C, coord=0.75, bg_color=(255, 255, 0, 255), text="0.75")
                            plot.X2.enabled = True
                            plot.Y2.enabled = True
                            with plot.X2:
                                dcg.AxisTag(C, coord=0.5, bg_color=(0, 255, 255, 255), text="MyTag")
                            with plot.Y2:
                                dcg.AxisTag(C, coord=0.5, bg_color=(0, 255, 255, 255), text="Tag: 42")

                    with dcg.TreeNode(C, label="Legend Options"):

                        with dcg.HorizontalLayout(C):
                            north_legend = dcg.Checkbox(C, label="North", value=False)
                            east_legend = dcg.Checkbox(C, label="East", value=False)
                            west_legend = dcg.Checkbox(C, label="West", value=False)
                            south_legend = dcg.Checkbox(C, label="South", value=False)
                        horizontal_legend = dcg.Checkbox(C, label="Horizontal", value=False)
                        outside_legend = dcg.Checkbox(C, label="Outside", value=False)
                        sort_legend = dcg.Checkbox(C, label="Sort", value=False)

                        with dcg.Plot(C, height=400, width=-1) as plot_with_legend:
                            plot_with_legend.legend_config.configure(location=0, outside=False, sorted=False, horizontal=False)
                            dcg.PlotLine(C, X=sindatax, Y=sindatay, label="2")
                            dcg.PlotLine(C, X=sindatax, Y=sindatay, label="1")
                            dcg.PlotLine(C, X=sindatax, Y=sindatay, label="3")
                        
                        def add_remove_location(element, add):
                            cur_location = plot_with_legend.legend_config.location
                            try:
                                if add:
                                    plot_with_legend.legend_config.location = cur_location | element
                                else:
                                    plot_with_legend.legend_config.location = cur_location & (~element)
                            except ValueError:
                                # West | East will raise this and will be ignored
                                pass

                        north_legend.callback = lambda s, t, d: add_remove_location(dcg.LegendLocation.NORTH, d)
                        east_legend.callback = lambda s, t, d: add_remove_location(dcg.LegendLocation.EAST, d)
                        west_legend.callback = lambda s, t, d: add_remove_location(dcg.LegendLocation.WEST, d)
                        south_legend.callback = lambda s, t, d: add_remove_location(dcg.LegendLocation.SOUTH, d)
                        horizontal_legend.callback = lambda s, t, d: plot_with_legend.legend_config.configure(horizontal=d)
                        outside_legend.callback = lambda s, t, d: plot_with_legend.legend_config.configure(outside=d)
                        sort_legend.callback = lambda s, t, d: plot_with_legend.legend_config.configure(sorted=d)

                    with dcg.TreeNode(C, label="Legend Popups"):
                        x = np.linspace(0, 100, 101)
                        frequency = 0.1
                        amplitude = 0.5
                        vals = amplitude * np.sin(frequency * x)

                        with dcg.Plot(C, label="Line Series", height=400, width=-1) as plot:
                            plot.X1.label = "x"
                            plot.Y1.label = "y"
                            with dcg.PlotBars(C, X=x, Y=vals, label="Right Click Me!") as plot_bars_with_legend:
                                # Children of series correspond to the context menu.
                                # They must be uiItems.
                                # In addition, DrawInPlot accepts drawing items, but these
                                # are not part of the context menu.
                                frequency_slider = dcg.Slider(C, label="Frequency",
                                                              value=frequency, min_value=0.01, max_value=5.0)
                                amplitude_slider = dcg.Slider(C, label="Amplitude",
                                                              value=amplitude, min_value=0.01, max_value=5.0)
                                dcg.Separator(C)
                        frequency_slider.callback = \
                            lambda: plot_bars_with_legend.configure(Y=amplitude_slider.value * np.sin(frequency_slider.value * x))
                        amplitude_slider.callbacks = frequency_slider.callbacks

                with dcg.Tab(C, label="Drawing"):
                    with dcg.TreeNode(C, label="Drawing in a window or a plot"):
                        with dcg.Plot(C, label="Drawing in a plot", height=400, width=-1) as plot:
                            plot.X1.label = "x"
                            plot.Y1.label = "y"
                            with dcg.DrawInPlot(C):
                                dcg.DrawCircle(C, center=(0.5, 0.5), radius=0.1, color=[255, 0, 0, 255], thickness=-2)
                                dcg.DrawTriangle(C, p1=(0.25, 0.75), p2=(0.75, 0.75), p3=(0.5, 0.25), color=[0, 255, 0, 255], thickness=-2)
                                dcg.DrawQuad(C, p1=(0.25, 0.25), p2=(0.75, 0.25), p3=(0.75, 0.75), p4=(0.25, 0.75), color=[0, 0, 255, 255], thickness=-2)
                                dcg.DrawText(C, pos=(0.5, 0.5), text="Hello, world!", color=[255, 255, 255, 255], size=-20)
                                dcg.DrawStar(C, center=(0.75, 0.25), color=[255, 0, 255, 255], radius=0.1, inner_radius=0.05, thickness=-2, num_points=5)
                        dcg.Text(C, value="Drawing in a window is similar to drawing in a plot, but plot features are unavailable.")
                        with dcg.DrawInWindow(C, relative=True, invert_y=True, orig_x = 0., orig_y = 0., scale_x=1., scale_y=1., width=-1, height=400):
                            dcg.DrawCircle(C, center=(0.5, 0.5), radius=0.1, color=[255, 0, 0, 255], thickness=-2)
                            dcg.DrawTriangle(C, p1=(0.25, 0.75), p2=(0.75, 0.75), p3=(0.5, 0.25), color=[0, 255, 0, 255], thickness=-2)
                            dcg.DrawQuad(C, p1=(0.25, 0.25), p2=(0.75, 0.25), p3=(0.75, 0.75), p4=(0.25, 0.75), color=[0, 0, 255, 255], thickness=-2)
                            dcg.DrawText(C, pos=(0.5, 0.5), text="Hello, world!", color=[255, 255, 255, 255], size=-20)
                            dcg.DrawStar(C, center=(0.75, 0.25), color=[255, 0, 255, 255], radius=0.1, inner_radius=0.05, thickness=-2, num_points=5)
                    with dcg.TreeNode(C, label="Controling line thickness"):
                        dcg.Text(C, value="Line thickness can be specified in pixels or plot space.")
                        with dcg.Plot(C, label="pixel space", height=400, width=-1) as plot:
                            plot.X1.label = "x"
                            plot.Y1.label = "y"
                            with dcg.DrawInPlot(C):
                                # Negatives for size, radius and thickness mean "screen space", that is not in plot coordinates
                                dcg.DrawLine(C, p1=(0.25, 0.25), p2=(0.75, 0.75), color=[255, 0, 0, 255], thickness=-2)
                                dcg.DrawCircle(C, center=(0.5, 0.5), radius=0.1, color=[0, 255, 0, 255], thickness=-2)
                                dcg.DrawTriangle(C, p1=(0.25, 0.75), p2=(0.75, 0.75), p3=(0.5, 0.25), color=[0, 0, 255, 255], thickness=-2)
                                dcg.DrawQuad(C, p1=(0.25, 0.25), p2=(0.75, 0.25), p3=(0.75, 0.75), p4=(0.25, 0.75), color=[255, 255, 0, 255], thickness=-2)
                                dcg.DrawText(C, pos=(0.5, 0.5), text="Hello, world!", color=[255, 255, 255, 255], size=-20)
                                dcg.DrawStar(C, center=(0.75, 0.25), color=[255, 0, 255, 255], radius=0.1, inner_radius=0.05, thickness=-2, num_points=5)
                        with dcg.Plot(C, label="plot space", height=400, width=-1) as plot:
                            plot.X1.label = "x"
                            plot.Y1.label = "y"
                            with dcg.DrawInPlot(C):
                                dcg.DrawLine(C, p1=(0.25, 0.25), p2=(0.75, 0.75), color=[255, 0, 0, 255], thickness=0.001)
                                dcg.DrawCircle(C, center=(0.5, 0.5), radius=0.1, color=[0, 255, 0, 255], thickness=0.001)
                                dcg.DrawTriangle(C, p1=(0.25, 0.75), p2=(0.75, 0.75), p3=(0.5, 0.25), color=[0, 0, 255, 255], thickness=0.001)
                                dcg.DrawQuad(C, p1=(0.25, 0.25), p2=(0.75, 0.25), p3=(0.75, 0.75), p4=(0.25, 0.75), color=[255, 255, 0, 255], thickness=0.001)
                                dcg.DrawText(C, pos=(0.5, 0.5), text="Hello, world!", color=[255, 255, 255, 255], size=0.01)
                                dcg.DrawStar(C, center=(0.75, 0.25), color=[255, 0, 255, 255], radius=0.1, inner_radius=0.05, thickness=0.001, num_points=5)

                    with dcg.TreeNode(C, label="Animation with DrawStream"):
                        dcg.Text(C, value="DrawStream allows you to create animations by showing items sequentially.")
                        dcg.Text(C, value="Each item is associated with an expiration time.", marker="bullet")
                        dcg.Text(C, value="When time_modulus is set, the animation loops.", marker="bullet")
                        
                        with dcg.Plot(C, label="Animated Shapes", height=400, width=-1) as plot:
                            plot.X1.label = "x"
                            plot.Y1.label = "y"
                            plot.X1.min = 0
                            plot.X1.max = 1
                            plot.Y1.min = 0
                            plot.Y1.max = 1
                            
                            # Add shapes that will appear in sequence
                            with dcg.DrawInPlot(C):
                                # Create a DrawStream with a 4 second loop
                                stream = dcg.utils.DrawStream(C)
                                stream.time_modulus = 4.0  # Loop every 4 seconds
                                # Red circle at t=0s, expires at t=1s
                                item1 = dcg.DrawCircle(C, center=(0.5, 0.5), radius=0.2, 
                                             color=(255, 0, 0, 255), thickness=-3)
                                stream.push(item1, 1.0)
                                
                                # Green triangle at t=1s, expires at t=2s
                                item2 = \
                                    dcg.DrawTriangle(C, p1=(0.2, 0.2), p2=(0.8, 0.2), p3=(0.5, 0.8),
                                               color=(0, 255, 0, 255), thickness=-3)
                                stream.push(item2, 2.0)
                                
                                # Blue rectangle at t=2s, expires at t=3s
                                item3 = \
                                    dcg.DrawQuad(C, p1=(0.2, 0.2), p2=(0.8, 0.2), 
                                           p3=(0.8, 0.8), p4=(0.2, 0.8),
                                           color=(0, 0, 255, 255), thickness=-3)
                                stream.push(item3, 3.0)
                                
                                # Yellow star at t=3s, expires at t=4s
                                item4 = \
                                    dcg.DrawStar(C, center=(0.5, 0.5), radius=0.3, 
                                           inner_radius=0.15, num_points=5,
                                           color=(255, 255, 0, 255), thickness=-3)
                                stream.push(item4, 4.0)

                with dcg.Tab(C, label="Help"):
                    dcg.Text(C, value="Plotting User Guide")
                    dcg.Text(C, value="Left click and drag within the plot area to pan X and Y axes.", marker="bullet")
                    dcg.Text(C, value="Left click and drag on an axis to pan an individual axis.", marker="bullet", x=20)
                    dcg.Text(C, value="Scoll in the plot area to zoom both X and Y axes.", marker="bullet")
                    dcg.Text(C, value="Scroll on an axis to zoom an individual axis.", marker="bullet", x=20)
                    dcg.Text(C, value="Double left click to fit all visible data.", marker="bullet")
                    dcg.Text(C, value="Double left click on an axis to fit the individual axis", marker="bullet", x=20)
                    dcg.Text(C, value="Double right click to open the plot context menu.", marker="bullet")
                    dcg.Text(C, value="Click legend label icons to show/hide plot items.", marker="bullet")

if __name__ == "__main__":
    C = dcg.Context()
    C.viewport.initialize(title="DearCyGui Demo")
    show_demo(C)
    while C.running:
        C.viewport.render_frame()
