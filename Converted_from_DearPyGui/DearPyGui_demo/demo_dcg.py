import colorsys
import dearcygui as dcg

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

if __name__ == "__main__":
    C = dcg.Context()
    show_demo(C)
    C.viewport.initialize(title="DearCyGui Demo")
    while C.running:
        C.viewport.render_frame()