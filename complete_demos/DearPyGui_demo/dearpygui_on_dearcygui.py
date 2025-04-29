##########################################################
# Compatibility file for DearPyGui
#
#   Resources:
#     * FAQ:         https://github.com/hoffstadt/DearPyGui/discussions/categories/frequently-asked-questions-faq 
#     * Homepage:    https://github.com/hoffstadt/DearPyGui 
#     * Wiki:        https://github.com/hoffstadt/DearPyGui/wiki 
#     * Issues:      https://github.com/hoffstadt/DearPyGui/issues
#     * Discussions: https://github.com/hoffstadt/DearPyGui/discussions
#
# Note not everything is implemented and this file is more
# intended as a demonstration than a production tool.
##########################################################

import inspect
import math
import random
import string
from contextlib import contextmanager

import dearcygui as dcg

from dearcygui import Key, KeyMod, MouseButton

from typing import List, Any, Callable, Union, Tuple
import numpy as np
import threading
import weakref

CONTEXT = None

DEFAULTS = {
    'payload_type': '$$DPG_PAYLOAD',
    'drag_callback': None,
    'drop_callback': None,
    'filter_key': '',
    'tracked': False,
    'track_offset': 0.5,
    'show': True,
    'uv_min': (0.0, 0.0),
    'uv_max': (1.0, 1.0),
    'color': -1,
    'min_scale': 0.0,
    'max_scale': 0.0,
    'order_mode': 0,
    'autosize_x': False,
    'autosize_y': False,
    'alpha_bar': False,
    'alpha_preview': 0,
    'corner_colors': None,
    'sort': False,
    'label': None
}

# Wrapping DearCyGui to inject some additional features

dcg_base = dcg

class DPGWrapper:
    """
    Wrapper class around DCG items to implemented DPG
    specific features:
    - tag: string identifier for the item
        This is implemented by catching the parameter
        and registering the association in the context
    - before/source/parent: Adding support for tags by
        letting the context handle the parent reference
    - pos: position of the item in the window, matching
        the DPG behavior
    - callback: DPG specific callback
    
    """
    def _clean_kwargs(self, kwargs: dict) -> dict:
        """Clean kwargs according to DPG rules"""
        # Handle tag
        if "tag" in kwargs:
            tag = kwargs.pop("tag")
            if tag is not None and hasattr(self, "uuid"):
                CONTEXT.register_tag_for_uuid(self.uuid, tag)

        # Handle parent reference
        if "parent" in kwargs:
            parent = kwargs.pop("parent")
            if parent is not None and parent != 0:
                kwargs["parent"] = CONTEXT.get(parent)

        # Handle before reference 
        if "before" in kwargs:
            before = kwargs.pop("before")
            if before is not None and before != 0:
                kwargs["before"] = CONTEXT.get(before)

        # Handle source reference
        if "source" in kwargs:
            source = kwargs.pop("source")
            if source is not None and (not(isinstance(source, int)) or source > 0):
                kwargs["shareable_value"] = CONTEXT.get(source).shareable_value

        # Handle pos
        if "pos" in kwargs:
            pos = kwargs.pop("pos")
            if pos is not None and len(pos) == 2:
                if isinstance(self, dcg_base.Window):
                    kwargs["pos_to_viewport"] = pos
                else:
                    kwargs["pos_to_window"] = pos

        # Handle callback
        if "callback" in kwargs:
            callback = kwargs.pop("callback")
            if callback is not None:
                kwargs["callbacks"] = callback
  
        return kwargs

    def __init__(self, *args, **kwargs):
        # Register with context
        if hasattr(self, "uuid"):
            CONTEXT.register_uuid(self, self.uuid)

        # Handle DPG specifics
        configure_args = self._clean_kwargs(kwargs)
        
        # Extract init kwargs vs configure kwargs
        init_args = {}
        
        # Only pass before and parent to init if set
        if "before" in configure_args:
            init_args["before"] = configure_args.pop("before")
        if "parent" in configure_args:
            init_args["parent"] = configure_args.pop("parent")
                
        # Call parent init
        super().__init__(*args, **init_args)
                
        # Configure remaining args
        if configure_args:
            self.configure(**configure_args)

    def configure(self, **kwargs):
        # Clean kwargs
        configure_args = self._clean_kwargs(kwargs)

        # These must be set first
        if "format" in configure_args:
            self.format = configure_args.pop("format")
        if "size" in configure_args:
            self.size = configure_args.pop("size")
        
        # Try to set each attribute
        non_defaults = {}
        for key, value in configure_args.items():
            try:
                setattr(self, key, value)
            except AttributeError:
                if value == DEFAULTS[key]:
                    continue
                non_defaults[key] = value

        if non_defaults:
            print(f'Unhandled configure args for {self}: {non_defaults}')

    def __del__(self):
        """
        Free the weak reference
        """
        try:
            CONTEXT.release_tag_and_uuid(self.uuid)
        except Exception:
            pass
        try:
            super().__del__()
        except AttributeError:
            pass

def create_dpg_class(cls: type) -> type:
    """Create a DPG-compatible version of the given class with wrapped methods
    
    Args:
        cls: The class to create a DPG version of
        
    Returns:
        A new class that handles DPG-specific behaviors
    """
    # Avoid creating duplicate DPG classes
    if cls.__name__.startswith('DPG'):
        return cls

    # Create the wrapped class
    wrapped_cls = type(
        f"DPG{cls.__name__}",
        (DPGWrapper, cls),
        {
            '__module__': cls.__module__,
            '__doc__': cls.__doc__,
            '__qualname__': cls.__qualname__
        }
    )
    
    return wrapped_cls

# Create DPG versions of all item classes
# Using the dcg_dpg. prefix instead of dcg.
# to avoid conflicts with the original
# dearcygui module

class _WrapperHolder:
    pass
dcg_dpg = _WrapperHolder()

for name, cls in list(vars(dcg).items()):
    if isinstance(cls, type) and \
       (issubclass(cls, dcg.baseItem) or issubclass(cls, dcg.SharedValue)):
        try:
            setattr(dcg_dpg, name, create_dpg_class(cls))
        except TypeError:
            # Some items cannot be subclassed
            setattr(dcg_dpg, name, cls)
    else:
        setattr(dcg_dpg, name, cls)

# Use the wrapper version of each item
dcg = dcg_dpg

# Adapted context to support DPG features

class DPGContext(dcg_base.Context):
    """
    A custom DCG context with extended functionalities
    to emulate DPG. In particular:
    - Support for tags and uuid retrieval
       Each wrapped item is registered with a tag and uuid
       to the context. The get method can be used to retrieve
       the item associated with a tag or uuid. Wrapped items
       do use get() for the parent, before and source
       parameters.

    """
    items : weakref.WeakValueDictionary
    tag_to_uuid : dict[str, int]
    uuid_to_tag : dict[int, str]
    def __init__(self):
        super().__init__()
        self.items = weakref.WeakValueDictionary()
        self.uuid_to_tag = dict()
        self.tag_to_uuid = dict()
        self.threadlocal_data = threading.local()

    def register_uuid(self, item, uuid: int) -> None:
        """Register an item with a uuid"""
        self.items[uuid] = item
        self.threadlocal_data.last_item_uuid = uuid
        try:
            if item.children_types != dcg_base.ChildType.NOCHILD:
                self.threadlocal_data.last_container_uuid = uuid
        except:
            pass

    def register_tag_for_uuid(self, uuid: int, tag: str) -> None:
        """Register a tag for an uuid"""
        old_tag = self.uuid_to_tag.get(uuid, None)
        
        if old_tag != tag:
            if tag in self.tag_to_uuid:
                raise KeyError(f"Tag {tag} already in use")
            if old_tag is not None:
                del self.tag_to_uuid[old_tag]
                del self.uuid_to_tag[uuid]
            if tag is not None:
                self.uuid_to_tag[uuid] = tag
                self.tag_to_uuid[tag] = uuid

    def release_tag_and_uuid(self, uuid: int) -> None:
        """Release the tag and uuid of an object"""
        if self.uuid_to_tag is None or self.items is None:
            # Can occur during gc collect at
            # the end of the program
            return
        if uuid in self.items:
            del self.items[uuid]
        if uuid in self.uuid_to_tag:
            tag = self.uuid_to_tag[uuid]
            del self.uuid_to_tag[uuid]
            del self.tag_to_uuid[tag]

    def get(self, key) -> Union[dcg_base.baseItem, None]:
        """
        Retrieves the object associated to
        a tag or an uuid
        """
        if isinstance(key, dcg_base.baseItem) or \
           isinstance(key, dcg_base.SharedValue):
            return key
        if isinstance(key, str):
            if key not in self.tag_to_uuid:
                raise KeyError(f"Item not found with index {key}.")
            uuid = self.tag_to_uuid[key]
        elif isinstance(key, int):
            uuid = key
        else:
            raise TypeError(f"{type(key)} is an invalid index type")
        item = self.items.get(uuid, None)
        if item is None:
            raise KeyError(f"Item not found with index {key}.")
        return item

    def get_item_tag(self, item) -> Union[str, None]:
        """Get the tag associated with an item"""
        return self.uuid_to_tag.get(item.uuid, None)

    def fetch_last_created_item(self)  -> Union[dcg_base.baseItem, None]:
        """
        Return the last item created in this thread.
        Returns None if the last item created has been
        deleted.
        """
        last_uuid = getattr(self.threadlocal_data, 'last_item_uuid', -1)
        return self.items.get(last_uuid, None)

    def fetch_last_created_container(self) -> Union[dcg_base.baseItem, None]:
        """
        Return the last item which can have children
        created in this thread.
        Returns None if the last such item has been
        deleted.
        """
        last_uuid = getattr(self.threadlocal_data, 'last_container_uuid', -1)
        return self.items.get(last_uuid, None)

    def override_last_item(self, item: dcg_base.baseItem) -> None:
        """Override the last created item/container"""
        uuid = item.uuid
        self.threadlocal_data.last_item_uuid = uuid
        if item.children_types != dcg_base.ChildType.NOCHILD:
            self.threadlocal_data.last_container_uuid = uuid

# Helper classes to implement DPG specific features

LOCAL_STORAGE = threading.local()
LOCAL_STORAGE.Y_AXIS = dcg.Axis.Y1

class PlotAxisY(dcg.PlotAxisConfig):
    """
    Context manager to help track
    the Y axis to bind to with
    DPG syntax.
    """
    def __init__(self, context : dcg_base.Context, axis_hint, plot : dcg_base.Plot, **kwargs):
        # In the case of Y axis there seems to be in dpg various ways
        # of adding y axes
        self.axis = LOCAL_STORAGE.Y_AXIS if axis_hint == mvYAxis else axis_hint
        if self.axis == dcg.Axis.Y1:
            plot.Y1 = self
            LOCAL_STORAGE.Y_AXIS = dcg.Axis.Y2
        elif self.axis == dcg.Axis.Y2:
            plot.Y2 = self
            LOCAL_STORAGE.Y_AXIS = dcg.Axis.Y3
        else:
            plot.Y3 = self
        self.plot = plot

    def __enter__(self):
        LOCAL_STORAGE.CURRENT_Y_AXIS = self
    def __exit__(self, exc_type, exc_value, traceback):
        del LOCAL_STORAGE.CURRENT_Y_AXIS

class PlotAxisX(dcg.PlotAxisConfig):
    """
    Context manager to help track
    the X axis to bind to with
    DPG syntax.
    """
    def __init__(self, context : dcg_base.Context, axis_hint, plot : dcg_base.Plot, **kwargs):
        super().__init__(context, **kwargs)
        self.axis = axis_hint
        if self.axis == dcg.Axis.X1:
            plot.X1 = self
        elif self.axis == dcg.Axis.X2:
            plot.X2 = self
        else:
            plot.X3 = self

class FrameBufferCallback:
    """
    A callback that is called the next frame only once to retrieve the
    framebuffer.
    """
    def __init__(self, C : dcg_base.Context, callback : Callable, *, user_data: Any =None, **kwargs):
        self.context = C
        assert(callback is not None) # TODO
        self.callback = callback
        self.handler = dcg.RenderHandler(C, callback=self.check_frame, user_data=user_data)
        with C.viewport.mutex:
            C.viewport.handlers += [
                self.handler
            ]
        self.run = False

    def check_frame(self) -> None:
        """
        Check if the frame buffer is ready and call the callback
        """
        if self.run:
            return
        if self.context.viewport.framebuffer is None:
            return
        # Technically there is an issue here if the frame
        # buffer is not updated. TODO
        self.callback(self.context.viewport, self.context.viewport.framebuffer)
        with self.context.viewport.mutex:
            self.context.viewport.handlers = \
            [
                h for h in self.context.viewport.handlers if h is not self.handler
            ]
        self.run = True

class FrameCallback:
    """
    A callback that is called once when the target frame index is reached.
    """
    def __init__(self, C : dcg_base.Context, frame : int, callback : Callable, *, user_data: Any =None, **kwargs):
        self.context = C
        self.frame = frame
        self.callback = dcg.DPGCallback(callback)
        self.handler = dcg.RenderHandler(C, callback=self.check_frame, user_data=user_data)
        with C.viewport.mutex:
            C.viewport.handlers += [
                self.handler
            ]
        self.run = False

    def check_frame(self) -> None:
        """
        Check if the target frame count is reached and call the callback
        """
        if self.run:
            return
        if self.context.viewport.metrics["frame_count"] < self.frame:
            return
        self.callback(self, self, None)
        with self.context.viewport.mutex:
            self.context.viewport.handlers = \
            [
                h for h in self.context.viewport.handlers if h is not self.handler
            ]
        self.run = True


#############################################################################################################################

# Constants

# reserved fields:
mvReservedUUID_0 = 10
mvReservedUUID_1 = 11
mvReservedUUID_2 = 12
mvReservedUUID_3 = 13
mvReservedUUID_4 = 14
mvReservedUUID_5 = 15
mvReservedUUID_6 = 16
mvReservedUUID_7 = 17
mvReservedUUID_8 = 18
mvReservedUUID_9 = 19
mvReservedUUID_10 = 20

# Key codes
mvKey_ModDisabled = None
mvKey_None = KeyMod.NOMOD
mvKey_0 = Key.ZERO
mvKey_1 = Key.ONE
mvKey_2 = Key.TWO
mvKey_3 = Key.THREE
mvKey_4 = Key.FOUR
mvKey_5 = Key.FIVE
mvKey_6 = Key.SIX
mvKey_7 = Key.SEVEN
mvKey_8 = Key.EIGHT
mvKey_9 = Key.NINE
mvKey_A = Key.A
mvKey_B = Key.B
mvKey_C = Key.C
mvKey_D = Key.D
mvKey_E = Key.E
mvKey_F = Key.F
mvKey_G = Key.G
mvKey_H = Key.H
mvKey_I = Key.I
mvKey_J = Key.J
mvKey_K = Key.K
mvKey_L = Key.L
mvKey_M = Key.M
mvKey_N = Key.N
mvKey_O = Key.O
mvKey_P = Key.P
mvKey_Q = Key.Q
mvKey_R = Key.R
mvKey_S = Key.S
mvKey_T = Key.T
mvKey_U = Key.U
mvKey_V = Key.V
mvKey_W = Key.W
mvKey_X = Key.X
mvKey_Y = Key.Y
mvKey_Z = Key.Z
mvKey_Back = Key.BACKSPACE
mvKey_Tab = Key.TAB
mvKey_Return = Key.ENTER
mvKey_LShift = Key.LEFTSHIFT
mvKey_RShift = Key.RIGHTSHIFT
mvKey_LControl = Key.LEFTCTRL
mvKey_RControl = Key.RIGHTCTRL
mvKey_LAlt = Key.LEFTALT
mvKey_RAlt = Key.RIGHTALT
mvKey_Pause = Key.PAUSE
mvKey_CapsLock = Key.CAPSLOCK
mvKey_Escape = Key.ESCAPE
mvKey_Spacebar = Key.SPACE
mvKey_End = Key.END
mvKey_Home = Key.HOME
mvKey_Left = Key.LEFTARROW
mvKey_Up = Key.UPARROW
mvKey_Right = Key.RIGHTARROW
mvKey_Down = Key.DOWNARROW
mvKey_Print = Key.PRINTSCREEN
mvKey_Insert = Key.INSERT
mvKey_Delete = Key.DELETE
mvKey_NumPad0 = Key.KEYPAD0
mvKey_NumPad1 = Key.KEYPAD1
mvKey_NumPad2 = Key.KEYPAD2
mvKey_NumPad3 = Key.KEYPAD3
mvKey_NumPad4 = Key.KEYPAD4
mvKey_NumPad5 = Key.KEYPAD5
mvKey_NumPad6 = Key.KEYPAD6
mvKey_NumPad7 = Key.KEYPAD7
mvKey_NumPad8 = Key.KEYPAD8
mvKey_NumPad9 = Key.KEYPAD9
mvKey_Subtract = Key.KEYPADSUBTRACT
mvKey_Decimal = Key.KEYPADDECIMAL
mvKey_Divide = Key.KEYPADDIVIDE
mvKey_Multiply = Key.KEYPADMULTIPLY
mvKey_Add = Key.KEYPADADD
mvKey_F1 = Key.F1
mvKey_F2 = Key.F2
mvKey_F3 = Key.F3
mvKey_F4 = Key.F4
mvKey_F5 = Key.F5
mvKey_F6 = Key.F6
mvKey_F7 = Key.F7
mvKey_F8 = Key.F8
mvKey_F9 = Key.F9
mvKey_F10 = Key.F10
mvKey_F11 = Key.F11
mvKey_F12 = Key.F12
mvKey_F13 = Key.F13
mvKey_F14 = Key.F14
mvKey_F15 = Key.F15
mvKey_F16 = Key.F16
mvKey_F17 = Key.F17
mvKey_F18 = Key.F18
mvKey_F19 = Key.F19
mvKey_F20 = Key.F20
mvKey_F21 = Key.F21
mvKey_F22 = Key.F22
mvKey_F23 = Key.F23
mvKey_F24 = Key.F24
mvKey_NumLock = Key.NUMLOCK
mvKey_ScrollLock = Key.SCROLLLOCK
mvKey_Period = Key.PERIOD
mvKey_Slash = Key.SLASH
mvKey_Backslash = Key.BACKSLASH
mvKey_Open_Brace = Key.LEFTBRACKET
mvKey_Close_Brace = Key.RIGHTBRACKET
mvKey_Browser_Back = Key.APPBACK
mvKey_Browser_Forward = Key.APPFORWARD
mvKey_Comma = Key.COMMA # -> it seems to be the old mvKey_Separator
mvKey_Minus = Key.MINUS
mvKey_Menu = Key.MENU
mvKey_ModSuper = KeyMod.SUPER # Cmd/Super/Windows
mvKey_ModShift = KeyMod.SHIFT
mvKey_ModAlt = KeyMod.ALT
mvKey_ModCtrl = KeyMod.CTRL


#-----------------------------------------------------------------------------
# Mouse Codes
#-----------------------------------------------------------------------------
mvMouseButton_Left = MouseButton.LEFT
mvMouseButton_Right = MouseButton.RIGHT
mvMouseButton_Middle = MouseButton.MIDDLE
mvMouseButton_X1 = MouseButton.X1
mvMouseButton_X2 = MouseButton.X2

mvGraphicsBackend_D3D11 = 0
mvGraphicsBackend_D3D12 = 1
mvGraphicsBackend_VULKAN = 2
mvGraphicsBackend_METAL = 3
mvGraphicsBackend_OPENGL = 4


mvAll = 0
mvTool_About = 3 # MV_TOOL_ABOUT_UUID
mvTool_Debug = 4 # MV_TOOL_DEBUG_UUID
mvTool_Doc = 5 # MV_TOOL_DOC_UUID
mvTool_ItemRegistry = 6 # MV_TOOL_ITEM_REGISTRY_UUID
mvTool_Metrics = 7 # MV_TOOL_METRICS_UUID
mvTool_Stack = 10 # MV_TOOL_STACK_UUID
mvTool_Style = 8 # MV_TOOL_STYLE_UUID
mvTool_Font = 9 # MV_TOOL_FONT_UUID
mvFontAtlas = 2 # MV_ATLAS_UUID
mvAppUUID = 1 # MV_APP_UUID
mvInvalidUUID = 0 # MV_INVALID_UUID

mvComboHeight_Small = "small"
mvComboHeight_Regular = "regular"
mvComboHeight_Large = "large"
mvComboHeight_Largest = "largest"

mvPlatform_Windows = 0
mvPlatform_Apple = 1
mvPlatform_Linux = 2

mvTabOrder_Reorderable = 0
mvTabOrder_Fixed = 1
mvTabOrder_Leading = 2
mvTabOrder_Trailing = 3

mvTimeUnit_Us = 0
mvTimeUnit_Ms = 1
mvTimeUnit_S = 2
mvTimeUnit_Min = 3
mvTimeUnit_Hr = 4
mvTimeUnit_Day = 5
mvTimeUnit_Mo = 6
mvTimeUnit_Yr = 7

mvDatePickerLevel_Day = 0
mvDatePickerLevel_Month = 1
mvDatePickerLevel_Year = 2

mvCullMode_None = 0
mvCullMode_Back = 1
mvCullMode_Front = 2

mvFontRangeHint_Default = 0
mvFontRangeHint_Japanese = 1
mvFontRangeHint_Korean = 2
mvFontRangeHint_Chinese_Full = 3
mvFontRangeHint_Chinese_Simplified_Common = 4
mvFontRangeHint_Cyrillic = 5
mvFontRangeHint_Thai = 6
mvFontRangeHint_Vietnamese = 7

mvNode_Attr_Input = 0
mvNode_Attr_Output = 1
mvNode_Attr_Static = 2

mvPlotBin_Sqrt = -1
mvPlotBin_Sturges = -2
mvPlotBin_Rice = -3
mvPlotBin_Scott = -4


mvFormat_Float_rgba = 0
mvFormat_Float_rgb = 1

mvThemeCat_Core = 0
mvThemeCat_Plots = 1
mvThemeCat_Nodes = 2

mvThemeCol_Text = "Text"
mvThemeCol_TextDisabled = "TextDisabled"
mvThemeCol_WindowBg = "WindowBg"
mvThemeCol_ChildBg = "ChildBg"
mvThemeCol_Border = "Border"
mvThemeCol_PopupBg = "PopupBg"
mvThemeCol_BorderShadow = "BorderShadow"
mvThemeCol_FrameBg = "FrameBg"
mvThemeCol_FrameBgHovered = "FrameBgHovered"
mvThemeCol_FrameBgActive = "FrameBgActive"
mvThemeCol_TitleBg = "TitleBg"
mvThemeCol_TitleBgActive = "TitleBgActive"
mvThemeCol_TitleBgCollapsed = "TitleBgCollapsed"
mvThemeCol_MenuBarBg = "MenuBarBg"
mvThemeCol_ScrollbarBg = "ScrollbarBg"
mvThemeCol_ScrollbarGrab = "ScrollbarGrab"
mvThemeCol_ScrollbarGrabHovered = "ScrollbarGrabHovered"
mvThemeCol_ScrollbarGrabActive = "ScrollbarGrabActive"
mvThemeCol_CheckMark = "CheckMark"
mvThemeCol_SliderGrab = "SliderGrab"
mvThemeCol_SliderGrabActive = "SliderGrabActive"
mvThemeCol_Button = "Button"
mvThemeCol_ButtonHovered = "ButtonHovered"
mvThemeCol_ButtonActive = "ButtonActive"
mvThemeCol_Header = "Header"
mvThemeCol_HeaderHovered = "HeaderHovered"
mvThemeCol_HeaderActive = "HeaderActive"
mvThemeCol_Separator = "Separator"
mvThemeCol_SeparatorHovered = "SeparatorHovered"
mvThemeCol_SeparatorActive = "SeparatorActive"
mvThemeCol_ResizeGrip = "ResizeGrip"
mvThemeCol_ResizeGripHovered = "ResizeGripHovered"
mvThemeCol_ResizeGripActive = "ResizeGripActive"
mvThemeCol_Tab = "Tab"
mvThemeCol_TabHovered = "TabHovered"
mvThemeCol_TabActive = "TabSelected"
mvThemeCol_TabUnfocused = "TabDimmed"
mvThemeCol_TabUnfocusedActive = "TabDimmedSelected"
mvThemeCol_PlotLines = "PlotLines"
mvThemeCol_PlotLinesHovered = "PlotLinesHovered"
mvThemeCol_PlotHistogram = "PlotHistogram"
mvThemeCol_PlotHistogramHovered = "PlotHistogramHovered"
mvThemeCol_TableHeaderBg = "TableHeaderBg"
mvThemeCol_TableBorderStrong = "TableBorderStrong"
mvThemeCol_TableBorderLight = "TableBorderLight"
mvThemeCol_TableRowBg = "TableRowBg"
mvThemeCol_TableRowBgAlt = "TableRowBgAlt"
mvThemeCol_TextSelectedBg = "TextSelectedBg"
mvThemeCol_DragDropTarget = "DragDropTarget"
mvThemeCol_NavHighlight = "NavCursor"
mvThemeCol_NavWindowingHighlight = "NavWindowingHighlight"
mvThemeCol_NavWindowingDimBg = "NavWindowingDimBg"
mvThemeCol_ModalWindowDimBg = "ModalWindowDimBg"

mvPlotCol_Line = "Line"
mvPlotCol_Fill = "Fill"
mvPlotCol_MarkerOutline = "MarkerOutline"
mvPlotCol_MarkerFill = "MarkerFill"
mvPlotCol_ErrorBar = "ErrorBar"
mvPlotCol_FrameBg = "FrameBg"
mvPlotCol_PlotBg = "PlotBg"
mvPlotCol_PlotBorder = "PlotBorder"
mvPlotCol_LegendBg = "LegendBg"
mvPlotCol_LegendBorder = "LegendBorder"
mvPlotCol_LegendText = "LegendText"
mvPlotCol_TitleText = "TitleText"
mvPlotCol_InlayText = "InlayText"
mvPlotCol_AxisBg = "AxisBg"
mvPlotCol_AxisBgActive = "AxisBgActive"
mvPlotCol_AxisBgHovered = "AxisBgHovered"
mvPlotCol_AxisGrid = "AxisGrid"
mvPlotCol_AxisText = "AxisText"
mvPlotCol_Selection = "Selection"
mvPlotCol_Crosshairs = "Crosshairs"


mvStyleVar_Alpha = "Alpha" #float Alpha
mvStyleVar_DisabledAlpha = "DisabledAlpha" #float DisabledAlpha
mvStyleVar_WindowPadding = "WindowPadding" #ImVec2WindowPadding
mvStyleVar_WindowRounding = "WindowRounding"#float WindowRounding
mvStyleVar_WindowBorderSize = "WindowBorderSize"#float WindowBorderSize
mvStyleVar_WindowMinSize = "WindowMinSize" #ImVec2WindowMinSize
mvStyleVar_WindowTitleAlign = "WindowTitleAlign"#ImVec2WindowTitleAlign
mvStyleVar_ChildRounding = "ChildRounding" #float ChildRounding
mvStyleVar_ChildBorderSize = "ChildBorderSize" #float ChildBorderSize
mvStyleVar_PopupRounding = "PopupRounding" #float PopupRounding
mvStyleVar_PopupBorderSize = "PopupBorderSize" #float PopupBorderSize
mvStyleVar_FramePadding = "FramePadding"#ImVec2FramePadding
mvStyleVar_FrameRounding = "FrameRounding" #float FrameRounding
mvStyleVar_FrameBorderSize = "FrameBorderSize" #float FrameBorderSize
mvStyleVar_ItemSpacing = "ItemSpacing" #ImVec2ItemSpacing
mvStyleVar_ItemInnerSpacing = "ItemInnerSpacing"#ImVec2ItemInnerSpacing
mvStyleVar_IndentSpacing = "IndentSpacing" #float IndentSpacing
mvStyleVar_CellPadding = "CellPadding" #ImVec2CellPadding
mvStyleVar_ScrollbarSize = "ScrollbarSize" #float ScrollbarSize
mvStyleVar_ScrollbarRounding = "ScrollbarRounding" #float ScrollbarRounding
mvStyleVar_GrabMinSize = "GrabMinSize" #float GrabMinSize
mvStyleVar_GrabRounding = "GrabRounding" #float GrabRounding
mvStyleVar_TabRounding = "TabRounding" #float TabRounding
mvStyleVar_TabBorderSize = "TabBorderSize"	# float TabBorderSize
mvStyleVar_TabBarBorderSize = "TabBarBorderSize"	# float TabBarBorderSize
mvStyleVar_TableAngledHeadersAngle = "TableAngledHeadersAngle" # float TableAngledHeadersAngle
mvStyleVar_TableAngledHeadersTextAlign = "TableAngledHeadersTextAlign" #ImVec2 TableAngledHeadersTextAlign
mvStyleVar_ButtonTextAlign = "ButtonTextAlign" #ImVec2ButtonTextAlign
mvStyleVar_SelectableTextAlign = "SelectableTextAlign" #ImVec2SelectableTextAlign
mvStyleVar_SeparatorTextBorderSize = "SeparatorTextBorderSize"	# float SeparatorTextBorderSize
mvStyleVar_SeparatorTextAlign = "SeparatorTextAlign"# ImVec2SeparatorTextAlign
mvStyleVar_SeparatorTextPadding = "SeparatorTextPadding"	# ImVec2SeparatorTextPadding

# item styling variables
mvPlotStyleVar_LineWeight = "LineWeight" #float,  plot item line weight in pixels
mvPlotStyleVar_Marker = "Marker" #int,marker specification
mvPlotStyleVar_MarkerSize = "MarkerSize" #float,  marker size in pixels (roughly the marker's "radius")
mvPlotStyleVar_MarkerWeight =   "MarkerWeight"#float,  plot outline weight of markers in pixels
mvPlotStyleVar_FillAlpha =  "FillAlpha"#float,  alpha modifier applied to all plot item fills
mvPlotStyleVar_ErrorBarSize =   "ErrorBarSize"#float,  error bar whisker width in pixels
mvPlotStyleVar_ErrorBarWeight = "ErrorBarWeight" #float,  error bar whisker weight in pixels
mvPlotStyleVar_DigitalBitHeight =   "DigitalBitHeight"#float,  digital channels bit height (at 1) in pixels
mvPlotStyleVar_DigitalBitGap =  "DigitalBitGap"#float,  digital channels bit padding gap in pixels

# plot styling variables
mvPlotStyleVar_PlotBorderSize = "PlotBorderSize" #float,  thickness of border around plot area
mvPlotStyleVar_MinorAlpha = "MinorAlpha" #float,  alpha multiplier applied to minor axis grid lines
mvPlotStyleVar_MajorTickLen = "MajorTickLen" #ImVec2, major tick lengths for X and Y axes
mvPlotStyleVar_MinorTickLen = "MinorTickLen" #ImVec2, minor tick lengths for X and Y axes
mvPlotStyleVar_MajorTickSize = "MajorTickSize"#ImVec2, line thickness of major ticks
mvPlotStyleVar_MinorTickSize = "MinorTickSize"#ImVec2, line thickness of minor ticks
mvPlotStyleVar_MajorGridSize = "MajorGridSize"#ImVec2, line thickness of major grid lines
mvPlotStyleVar_MinorGridSize = "MinorGridSize"#ImVec2, line thickness of minor grid lines
mvPlotStyleVar_PlotPadding = "PlotPadding"#ImVec2, padding between widget frame and plot area, labels, or outside legends (i.e. main padding)
mvPlotStyleVar_LabelPadding = "LabelPadding" #ImVec2, padding between axes labels, tick labels, and plot edge
mvPlotStyleVar_LegendPadding = "LegendPadding"#ImVec2, legend padding from plot edges
mvPlotStyleVar_LegendInnerPadding = "LegendInnerPadding" #ImVec2, legend inner padding from legend edges
mvPlotStyleVar_LegendSpacing = "LegendSpacing"#ImVec2, spacing between legend entries
mvPlotStyleVar_MousePosPadding = "MousePosPadding"#ImVec2, padding between plot edge and interior info text
mvPlotStyleVar_AnnotationPadding = "AnnotationPadding"#ImVec2, text padding around annotation labels
mvPlotStyleVar_FitPadding = "FitPadding" #ImVec2, additional fit padding as a percentage of the fit extents (e.g. ImVec2(0.1f,0.1f) adds 10% to the fit extents of X and Y)
mvPlotStyleVar_PlotDefaultSize = "PlotDefaultSize"#ImVec2, default size used when ImVec2(0,0) is passed to BeginPlot
mvPlotStyleVar_PlotMinSize = "PlotMinSize"   # ImVec2, minimum size plot frame can be when shrunk


# nodes
mvNodeCol_NodeBackground = "NodeBackground"
mvNodeCol_NodeBackgroundHovered = "NodeBackgroundHovered"
mvNodeCol_NodeBackgroundSelected = "NodeBackgroundSelected"
mvNodeCol_NodeOutline = "NodeOutline"
mvNodeCol_TitleBar = "TitleBar"
mvNodeCol_TitleBarHovered = "TitleBarHovered"
mvNodeCol_TitleBarSelected = "TitleBarSelected"
mvNodeCol_Link = "Link"
mvNodeCol_LinkHovered = "LinkHovered"
mvNodeCol_LinkSelected = "LinkSelected"
mvNodeCol_Pin = "Pin"
mvNodeCol_PinHovered = "PinHovered"
mvNodeCol_BoxSelector = "BoxSelector"
mvNodeCol_BoxSelectorOutline = "BoxSelectorOutline"
mvNodeCol_GridBackground = "GridBackground"
mvNodeCol_GridLine = "GridLine"
mvNodesCol_GridLinePrimary = "GridLinePrimary"
mvNodesCol_MiniMapBackground = "MiniMapBackground"
mvNodesCol_MiniMapBackgroundHovered = "MiniMapBackgroundHovered"
mvNodesCol_MiniMapOutline = "MiniMapOutline"
mvNodesCol_MiniMapOutlineHovered = "MiniMapOutlineHovered"
mvNodesCol_MiniMapNodeBackground = "MiniMapNodeBackground"
mvNodesCol_MiniMapNodeBackgroundHovered = "MiniMapNodeBackgroundHovered"
mvNodesCol_MiniMapNodeBackgroundSelected = "MiniMapNodeBackgroundSelected"
mvNodesCol_MiniMapNodeOutline = "MiniMapNodeOutline"
mvNodesCol_MiniMapLink = "MiniMapLink"
mvNodesCol_MiniMapLinkSelected = "MiniMapLinkSelected"
mvNodesCol_MiniMapCanvas = "MiniMapCanvas"
mvNodesCol_MiniMapCanvasOutline = "MiniMapCanvasOutline"

# nodes
mvNodeStyleVar_GridSpacing = "GridSpacing"
mvNodeStyleVar_NodeCornerRounding = "NodeCornerRounding"
mvNodeStyleVar_NodePadding = "NodePadding"
mvNodeStyleVar_NodeBorderThickness = "NodeBorderThickness"
mvNodeStyleVar_LinkThickness = "LinkThickness"
mvNodeStyleVar_LinkLineSegmentsPerLength = "LinkLineSegmentsPerLength"
mvNodeStyleVar_LinkHoverDistance = "LinkHoverDistance"
mvNodeStyleVar_PinCircleRadius = "PinCircleRadius"
mvNodeStyleVar_PinQuadSideLength = "PinQuadSideLength"
mvNodeStyleVar_PinTriangleSideLength = "PinTriangleSideLength"
mvNodeStyleVar_PinLineThickness = "PinLineThickness"
mvNodeStyleVar_PinHoverRadius = "PinHoverRadius"
mvNodeStyleVar_PinOffset = "PinOffset"
mvNodesStyleVar_MiniMapPadding = "MiniMapPadding"
mvNodesStyleVar_MiniMapOffset = "MiniMapOffset"


mvPlotScale_Linear = dcg.AxisScale.LINEAR
mvPlotScale_Time = dcg.AxisScale.TIME
mvPlotScale_Log10 = dcg.AxisScale.LOG10
mvPlotScale_SymLog = dcg.AxisScale.SYMLOG

mvPlotMarker_None = dcg.PlotMarker.NONE  # no marker
mvPlotMarker_Circle = dcg.PlotMarker.CIRCLE  # a circle marker will be rendered at each point
mvPlotMarker_Square = dcg.PlotMarker.SQUARE  # a square maker will be rendered at each point
mvPlotMarker_Diamond = dcg.PlotMarker.DIAMOND  # a diamond marker will be rendered at each point
mvPlotMarker_Up = dcg.PlotMarker.UP  # an upward-pointing triangle marker will up rendered at each point
mvPlotMarker_Down =  dcg.PlotMarker.DOWN  # an downward-pointing triangle marker will up rendered at each point
mvPlotMarker_Left = dcg.PlotMarker.LEFT  # an leftward-pointing triangle marker will up rendered at each point
mvPlotMarker_Right = dcg.PlotMarker.RIGHT  # an rightward-pointing triangle marker will up rendered at each point
mvPlotMarker_Cross = dcg.PlotMarker.CROSS  # a cross marker will be rendered at each point
mvPlotMarker_Plus = dcg.PlotMarker.PLUS  # a plus marker will be rendered at each point
mvPlotMarker_Asterisk = dcg.PlotMarker.ASTERISK  # an asterisk marker will be rendered at each point

mvPlot_Location_Center = dcg.LegendLocation.CENTER
mvPlot_Location_North = dcg.LegendLocation.NORTH
mvPlot_Location_South = dcg.LegendLocation.SOUTH
mvPlot_Location_West = dcg.LegendLocation.WEST
mvPlot_Location_East = dcg.LegendLocation.EAST
mvPlot_Location_NorthWest = dcg.LegendLocation.NORTHWEST
mvPlot_Location_NorthEast = dcg.LegendLocation.NORTHEAST
mvPlot_Location_SouthWest = dcg.LegendLocation.SOUTHWEST
mvPlot_Location_SouthEast = dcg.LegendLocation.SOUTHEAST

mvXAxis = dcg.Axis.X1
mvXAxis2 = dcg.Axis.X2
mvXAxis3 = dcg.Axis.X3
mvYAxis = dcg.Axis.Y1
mvYAxis2 = dcg.Axis.Y2
mvYAxis3 = dcg.Axis.Y3

mvDir_None = None
mvDir_Left = dcg.ButtonDirection.LEFT
mvDir_Right = dcg.ButtonDirection.RIGHT
mvDir_Up = dcg.ButtonDirection.UP
mvDir_Down = dcg.ButtonDirection.DOWN

mvColorEdit_AlphaPreviewNone = "none"
mvColorEdit_AlphaPreview = "full"
mvColorEdit_AlphaPreviewHalf = "half"
mvColorEdit_uint8 = "uint8"
mvColorEdit_float = "float"
mvColorEdit_rgb = "rgb"
mvColorEdit_hsv = "hsv"
mvColorEdit_hex = "hex"
mvColorEdit_input_rgb = "rgb"
mvColorEdit_input_hsv = "hsv"

mvColorPicker_bar = "bar"
mvColorPicker_wheel = "wheel"


# The ones below to not yet exist,
# mapping may change

mvPlotColormap_Default = "deep" # implot.ImPlot default colormap (n=10)
mvPlotColormap_Deep = "deep" # a.k.a. seaborn deep (default) (n=10)
mvPlotColormap_Dark = "dark" # a.k.a. matplotlib "Set1"(n=9)
mvPlotColormap_Pastel = "pastel" # a.k.a. matplotlib "Pastel1" (n=9)
mvPlotColormap_Paired = "paired" # a.k.a. matplotlib "Paired"  (n=12)
mvPlotColormap_Viridis = "viridis" # a.k.a. matplotlib "viridis" (n=11)
mvPlotColormap_Plasma = "plasma" # a.k.a. matplotlib "plasma"  (n=11)
mvPlotColormap_Hot = "hot" # a.k.a. matplotlib/MATLAB "hot"  (n=11)
mvPlotColormap_Cool = "cool" # a.k.a. matplotlib/MATLAB "cool" (n=11)
mvPlotColormap_Pink = "pink" # a.k.a. matplotlib/MATLAB "pink" (n=11)
mvPlotColormap_Jet = "jet" # a.k.a. MATLAB "jet" (n=11)
mvPlotColormap_Twilight = "twilight" # a.k.a. MATLAB "twilight" (n=11)
mvPlotColormap_RdBu = "RdBu" # red/blue, Color Brewer(n=11)
mvPlotColormap_BrBG = "BrBG" # brown/blue-green, Color Brewer (n=11)
mvPlotColormap_PiYG = "PiYG" # pink/yellow-green, Color Brewer (n=11)
mvPlotColormap_Spectral = "spectral" # color spectrum, Color Brewer (n=11)
mvPlotColormap_Greys = "greys" # white/black (n=11)

mvNode_PinShape_Circle = "circle"
mvNode_PinShape_CircleFilled = "circle_filled"
mvNode_PinShape_Triangle = "triangle"
mvNode_PinShape_TriangleFilled = "triangle_filled"
mvNode_PinShape_Quad = "quad"
mvNode_PinShape_QuadFilled = "quad_filled"

mvNodeMiniMap_Location_BottomLeft = "bottom_left"
mvNodeMiniMap_Location_BottomRight = "bottom_right"
mvNodeMiniMap_Location_TopLeft = "top_left"
mvNodeMiniMap_Location_TopRight = "top_right"

mvTable_SizingFixedFit = "sizing_fixed_fit"
mvTable_SizingFixedSame = "sizing_fixed_same"
mvTable_SizingStretchProp = "sizing_stretch_prop"
mvTable_SizingStretchSame = "sizing_stretch_same"

# functions

def wrap_callback(callback):
    if callback is None:
        return None
    return dcg_dpg.DPGCallback(callback)

def run_callbacks(jobs):
    if jobs is None:
        pass
    else:
        for job in jobs:
            if job[0] is None:
                pass
            else:
                sig = inspect.signature(job[0])
                args = []
                for arg in range(len(sig.parameters)):
                    args.append(job[arg+1])
                job[0](*args)

def get_major_version():
    """ return Dear PyGui Major Version """
    raise NotImplementedError("Not DearPyGui")

def get_minor_version():
    """ return Dear PyGui Minor Version """
    raise NotImplementedError("Not DearPyGui")

def get_dearpygui_version():
    """ return Dear PyGui Version """
    raise NotImplementedError("Not DearPyGui")

def configure_item(item : Union[int, str], **kwargs) -> None:
    CONTEXT.get(item).configure(**kwargs)

def configure_app(**kwargs) -> None:
    for (key, value) in kwargs.items():
        try:
            setattr(CONTEXT, key, value)
        except AttributeError:
            try:
                setattr(CONTEXT.viewport, key, value)
            except AttributeError:
                print(f"Unhandled app configure {key}, {value}")

def configure_viewport(item : Union[int, str], **kwargs) -> None:
    CONTEXT.viewport.configure(**kwargs)

def start_dearpygui():
    if not is_viewport_ok():
        raise RuntimeError("Viewport was not created and shown.")
        return

    while(is_dearpygui_running()):
        render_dearpygui_frame()   


@contextmanager
def mutex():
    """ Handles locking/unlocking render thread mutex. """
    try:
        yield CONTEXT.viewport.lock_mutex(wait=True)
    finally:
        CONTEXT.viewport.unlock_mutex()


def popup(parent: Union[int, str], mousebutton: int = mvMouseButton_Right, modal: bool=False, tag:Union[int, str]=0, min_size:Union[List[int], Tuple[int, ...]]=[100,100], max_size: Union[List[int], Tuple[int, ...]] =[30000, 30000], no_move: bool=False, no_background: bool=False) -> int:
    if modal:
        item = window(modal=True, show=False, autosize=True, min_size=min_size, max_size=max_size, no_move=no_move, no_background=no_background, tag=tag)
    else:
        item = window(popup=True, show=False, autosize=True, min_size=min_size, max_size=max_size, no_move=no_move, no_background=no_background, tag=tag)
    def callback(sender, source, user_data, item=item):
        item.show = True
    item.parent = CONTEXT.viewport
    handler = item_clicked_handler(mousebutton, callback=callback)
    parent = CONTEXT.get(parent)
    with parent.mutex:
        parent.handlers += [handler]
    return item


########################################################################################################################
# Information Commands
########################################################################################################################

def get_item_slot(item: Union[int, str]) -> Union[int, None]:
    item = CONTEXT.get(item)
    if isinstance(item, dcg_base.uiItem) or isinstance(item, dcg_base.baseHandler):
        return 1
    elif isinstance(item, dcg_base.drawingItem):
        return 2
    else:
        return 0 # ????=

def is_item_container(item: Union[int, str]) -> Union[bool, None]:
    return CONTEXT.get(item).item_type != dcg_base.ChildType.NONE

def get_item_parent(item: Union[int, str]) -> Union[int, None]:
    return CONTEXT.get(item).parent

def filter_slot(items, slot):
    return [item for item in items if get_item_slot(item) == slot]

def get_item_children(item: Union[int, str] , slot: int = -1) -> Union[dict, List[int], None]:
    children = CONTEXT.get(item).children
    if slot < 0 or slot > 4:
        return (filter_slot(children, 0),
                filter_slot(children, 1),
                filter_slot(children, 2),
                filter_slot(children, 3))
    return filter_slot(children, slot)

def get_item_type(item: Union[int, str]) -> Union[str]:
    return type(CONTEXT.get(item))

def get_item_theme(item: Union[int, str]) -> int:
    return CONTEXT.get(item).theme

def get_item_font(item: Union[int, str]) -> int:
    return CONTEXT.get(item).font

def enable_item(item: Union[int, str]):
    try:
        CONTEXT.get(item).enabled = True
    except AttributeError:
        # TODO: once warning
        pass

def disable_item(item: Union[int, str]):
    try:
        CONTEXT.get(item).enabled = False
    except AttributeError:
        # TODO: once warning
        pass

def set_item_label(item: Union[int, str], label: str):
    CONTEXT.get(item).label = label

def set_item_source(item: Union[int, str], source: Union[int, str]):
    CONTEXT.get(item).shareable_value = CONTEXT.get(source).shareable_value

def set_item_pos(item: Union[int, str], pos: List[float]):
    # Contrary to the description, DPG does it against
    # the window, not the parent.
    CONTEXT.get(item).pos_to_window = pos

def set_item_width(item: Union[int, str], width: int):
    CONTEXT.get(item).width = width

def set_item_height(item: Union[int, str], height: int):
    CONTEXT.get(item).height = height

def set_item_indent(item: Union[int, str], indent: int):
    CONTEXT.get(item).indent = indent

def set_item_callback(item: Union[int, str], callback: Callable):
    try:
        # UIitems
        CONTEXT.get(item).callbacks = wrap_callback(callback)
    except AttributeError:
        # Handlers
        CONTEXT.get(item).callback = wrap_callback(callback)

def set_item_user_data(item: Union[int, str], user_data: Any):
    CONTEXT.get(item).user_data=user_data

def show_item(item: Union[int, str]):
    CONTEXT.get(item).show = True

def hide_item(item: Union[int, str], *, children_only: bool = False):
    item = CONTEXT.get(item)
    if children_only:
        for child in item.children:
            child.show = False
    else:
        item.show = False

########################################################################################################################
# Configuration Getter Commands
########################################################################################################################

def get_item_label(item: Union[int, str]) -> Union[str, None]:
    return CONTEXT.get(item).label

def get_item_indent(item: Union[int, str]) -> Union[int, None]:
    return CONTEXT.get(item).indent

def get_item_width(item: Union[int, str]) -> Union[int, None]:
    return CONTEXT.get(item).width

def get_item_height(item: Union[int, str]) -> Union[int, None]:
    return CONTEXT.get(item).height

def get_item_callback(item: Union[int, str]) -> Union[Callable, None]:
    return CONTEXT.get(item).callbacks[0]

def get_item_user_data(item: Union[int, str]) -> Union[Any, None]:
    return CONTEXT.get(item).user_data

def get_item_source(item: Union[int, str]) -> Union[str, None]:
    return CONTEXT.get(item).shareable_value

########################################################################################################################
# State Commands
########################################################################################################################

def is_item_hovered(item: Union[int, str]) -> Union[bool, None]:
    return CONTEXT.get(item).hovered

def is_item_active(item: Union[int, str]) -> Union[bool, None]:
    return CONTEXT.get(item).active

def is_item_focused(item: Union[int, str]) -> Union[bool, None]:
    return CONTEXT.get(item).focused

def is_item_clicked(item: Union[int, str]) -> Union[bool, None]:
    return max(CONTEXT.get(item).clicked)

def is_item_left_clicked(item: Union[int, str]) -> Union[bool, None]:
    return CONTEXT.get(item).clicked[0]

def is_item_right_clicked(item: Union[int, str]) -> Union[bool, None]:
    return CONTEXT.get(item).clicked[1]

def is_item_middle_clicked(item: Union[int, str]) -> Union[bool, None]:
    return CONTEXT.get(item).clicked[2]

def is_item_visible(item: Union[int, str]) -> Union[bool, None]:
    return CONTEXT.get(item).visible

def is_item_edited(item: Union[int, str]) -> Union[bool, None]:
    return CONTEXT.get(item).edited

def is_item_activated(item: Union[int, str]) -> Union[bool, None]:
    return CONTEXT.get(item).activated

def is_item_deactivated(item: Union[int, str]) -> Union[bool, None]:
    return CONTEXT.get(item).deactivated

def is_item_deactivated_after_edit(item: Union[int, str]) -> Union[bool, None]:
    return CONTEXT.get(item).deactivated_after_edited

def is_item_ok(item: Union[int, str]) -> Union[bool, None]:
    return True

def is_item_shown(item: Union[int, str]) -> Union[bool, None]:
    return CONTEXT.get(item).show

def is_item_enabled(item: Union[int, str]) -> Union[bool, None]:
    item = CONTEXT.get(item)
    try:
        return item.enabled
    except AttributeError:
        return True

def get_item_pos(item: Union[int, str]) -> List[int]:
    return CONTEXT.get(item).pos

def get_available_content_region(item: Union[int, str]) -> List[int]:
    return CONTEXT.get(item).content_region_avail

def get_item_rect_size(item: Union[int, str]) -> List[int]:
    return CONTEXT.get(item).rect_size

def get_item_rect_min(item: Union[int, str]) -> List[int]:
    return CONTEXT.get(item).rect_min

def get_item_rect_max(item: Union[int, str]) -> List[int]:
    return CONTEXT.get(item).rect_max

########################################################################################################################
# Viewport Setter Commands
########################################################################################################################

def set_viewport_clear_color(color: List[int]):
    CONTEXT.viewport.clear_color = color

def set_viewport_small_icon(icon: str):
    CONTEXT.viewport.small_icon=icon

def set_viewport_large_icon(icon: str):
    CONTEXT.viewport.large_icon=icon

def set_viewport_pos(pos: List[float]):
    CONTEXT.viewport.x_pos=pos[0]
    CONTEXT.viewport.y_pos=pos[1]

def set_viewport_width(width: int):
    CONTEXT.viewport.width=width

def set_viewport_height(height: int):
    CONTEXT.viewport.height=height

def set_viewport_min_width(width: int):
    CONTEXT.viewport.min_width=width

def set_viewport_max_width(width: int):
    CONTEXT.viewport.max_width=width

def set_viewport_min_height(height: int):
    CONTEXT.viewport.min_height=height

def set_viewport_max_height(height: int):
    CONTEXT.viewport.max_height=height

def set_viewport_title(title: str):
    CONTEXT.viewport.title=title

def set_viewport_always_top(value: bool):
    CONTEXT.viewport.always_on_top=value

def set_viewport_resizable(value: bool):
    CONTEXT.viewport.resizable=value

def set_viewport_vsync(value: bool):
    CONTEXT.viewport.vsync=value

def set_viewport_decorated(value: bool):
    CONTEXT.viewport.decorated=value

########################################################################################################################
# Viewport Getter Commands
########################################################################################################################

def get_viewport_clear_color() ->List[int]:
    return CONTEXT.viewport.clear_color

def get_viewport_pos() ->List[float]:
    x_pos = CONTEXT.viewport.x_pos
    y_pos = CONTEXT.viewport.y_pos
    return [x_pos, y_pos]

def get_viewport_width() -> int:
    return CONTEXT.viewport.width

def get_viewport_client_width() -> int:
    return CONTEXT.viewport.width

def get_viewport_client_height() -> int:
    return CONTEXT.viewport.height

def get_viewport_height() -> int:
    return CONTEXT.viewport.height

def get_viewport_min_width() -> int:
    return CONTEXT.viewport.min_width

def get_viewport_max_width() -> int:
    return CONTEXT.viewport.max_width

def get_viewport_min_height() -> int:
    return CONTEXT.viewport.min_height

def get_viewport_max_height() -> int:
    return CONTEXT.viewport.max_height

def get_viewport_title() -> str:
    return CONTEXT.viewport.title

def is_viewport_always_top() -> bool:
    return CONTEXT.viewport.always_on_top

def is_viewport_resizable() -> bool:
    return CONTEXT.viewport.resizable

def is_viewport_vsync_on() -> bool:
    return CONTEXT.viewport.vsync

def is_viewport_decorated() -> bool:
    return CONTEXT.viewport.decorated

##########################################################
# Core Wrappings
##########################################################

def add_2d_histogram_series(x : Union[List[float], Tuple[float, ...]], y : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, xbins: int =-1, ybins: int =-1, xmin_range: float =0.0, xmax_range: float =0.0, ymin_range: float =0.0, ymax_range: float =0.0, density: bool =False, outliers: bool =False, col_major: bool =False, **kwargs) -> Union[int, str]:
    return dcg.PlotHistogram2D(CONTEXT, X=x, Y=y, label=label, user_data=user_data, show=show, x_bins=xbins, y_bins=ybins, range_x=(xmin_range, xmax_range), range_y=(ymin_range, ymax_range), density=density, no_outliers=not(outliers), **kwargs)

def alias(alias : str, item : Union[int, str], **kwargs) -> None:
    CONTEXT.get(item).configure(tag = alias)

def bar_series(x : Union[List[float], Tuple[float, ...]], y : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, weight: float =1.0, horizontal: bool =False, **kwargs) -> Union[int, str]:
    parent = kwargs.pop("parent", None)
    if parent is None:
        axis_y = LOCAL_STORAGE.CURRENT_Y_AXIS
    else:
        axis_y = parent

    plot = axis_y.plot

    return dcg.PlotBars(CONTEXT, parent=plot, axes=(dcg.Axis.X1, axis_y.axis), X=x, Y=y, label=label, user_data=user_data, show=show, weight=weight, horizontal=horizontal, **kwargs)

def bool_value(*, label: str =None, user_data: Any =None, default_value: bool =False, parent: Union[int, str] =mvReservedUUID_3, **kwargs) -> Union[int, str]:
    return dcg.SharedBool(CONTEXT, default_value)

def button(*, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, small: bool =False, repeat: bool =False, direction=None, arrow=None, **kwargs) -> Union[int, str]:
    return dcg.Button(CONTEXT, label=label, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, small=small, arrow=direction, repeat=repeat, **kwargs)

def checkbox(*, label: str =None, user_data: Any =None, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: bool =False, **kwargs) -> Union[int, str]:
    return dcg.Checkbox(CONTEXT, label=label, user_data=user_data, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, **kwargs)

def child_window(*, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', drop_callback: Callable =None, show: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, border: bool =True, autosize_x: bool =False, autosize_y: bool =False, no_scrollbar: bool =False, horizontal_scrollbar: bool =False, menubar: bool =False, no_scroll_with_mouse: bool =False, flattened_navigation: bool =True, always_use_window_padding: bool =False, resizable_x: bool =False, resizable_y: bool =False, always_auto_resize: bool =False, frame_style: bool =False, auto_resize_x: bool =False, auto_resize_y: bool =False, **kwargs) -> Union[int, str]:
    return dcg.ChildWindow(CONTEXT, label=label, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, drop_callback=drop_callback, show=show, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, border=border, autosize_x=autosize_x, autosize_y=autosize_y, no_scrollbar=no_scrollbar, horizontal_scrollbar=horizontal_scrollbar, menubar=menubar, no_scroll_with_mouse=no_scroll_with_mouse, flattened_navigation=flattened_navigation, always_use_window_padding=always_use_window_padding, resizable_x=resizable_x, resizable_y=resizable_y, always_auto_resize=always_auto_resize, frame_style=frame_style, auto_resize_x=auto_resize_x, auto_resize_y=auto_resize_y, **kwargs)

def collapsing_header(*, label: str =None, user_data: Any =None, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, closable: bool =False, default_open: bool =False, open_on_double_click: bool =False, open_on_arrow: bool =False, leaf: bool =False, bullet: bool =False, **kwargs) -> Union[int, str]:
    return dcg.CollapsingHeader(CONTEXT, label=label, user_data=user_data, indent=indent, payload_type=payload_type, drag_callback=drag_callback, drop_callback=drop_callback, show=show, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, closable=closable, value=default_open, open_on_double_click=open_on_double_click, open_on_arrow=open_on_arrow, leaf=leaf, bullet=bullet, **kwargs)

def color_button(default_value : Union[List[int], Tuple[int, ...]] =(0, 0, 0, 255), *, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, no_alpha: bool =False, no_border: bool =False, no_drag_drop: bool =False, **kwargs) -> Union[int, str]:
    return dcg.ColorButton(CONTEXT, value=default_value, label=label, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, no_alpha=no_alpha, no_border=no_border, no_drag_drop=no_drag_drop, **kwargs)

def color_edit(default_value : Union[List[int], Tuple[int, ...]] =(0, 0, 0, 255), *, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, no_alpha: bool =False, no_picker: bool =False, no_options: bool =False, no_small_preview: bool =False, no_inputs: bool =False, no_tooltip: bool =False, no_label: bool =False, no_drag_drop: bool =False, alpha_bar: bool =False, alpha_preview: int =mvColorEdit_AlphaPreviewNone, display_mode: int =mvColorEdit_rgb, display_type: int =mvColorEdit_uint8, input_mode: int =mvColorEdit_input_rgb, **kwargs) -> Union[int, str]:
    return dcg.ColorEdit(CONTEXT, value=default_value, label=label, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, no_alpha=no_alpha, no_picker=no_picker, no_options=no_options, no_small_preview=no_small_preview, no_inputs=no_inputs, no_tooltip=no_tooltip, no_label=no_label, no_drag_drop=no_drag_drop, alpha_bar=alpha_bar, alpha_preview=alpha_preview, display_mode=display_mode, display_type=display_type, input_mode=input_mode, **kwargs)

def color_picker(default_value : Union[List[int], Tuple[int, ...]] =(0, 0, 0, 255), *, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, no_alpha: bool =False, no_side_preview: bool =False, no_small_preview: bool =False, no_inputs: bool =False, no_tooltip: bool =False, no_label: bool =False, alpha_bar: bool =False, display_rgb: bool =False, display_hsv: bool =False, display_hex: bool =False, picker_mode: int =mvColorPicker_bar, alpha_preview: int =mvColorEdit_AlphaPreviewNone, display_type: int =mvColorEdit_uint8, input_mode: int =mvColorEdit_input_rgb, **kwargs) -> Union[int, str]:
    return dcg.ColorPicker(CONTEXT, value=default_value, label=label, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, no_alpha=no_alpha, no_side_preview=no_side_preview, no_small_preview=no_small_preview, no_inputs=no_inputs, no_tooltip=no_tooltip, no_label=no_label, alpha_bar=alpha_bar, display_rgb=display_rgb, display_hsv=display_hsv, display_hex=display_hex, picker_mode=picker_mode, alpha_preview=alpha_preview, display_type=display_type, input_mode=input_mode, **kwargs)

def color_value(*, label: str =None, user_data: Any =None, default_value: Union[List[float], Tuple[float, ...]] =(0.0, 0.0, 0.0, 0.0), parent: Union[int, str] =mvReservedUUID_3, **kwargs) -> Union[int, str]:
    return dcg.SharedColor(CONTEXT, default_value)

def combo(items : Union[List[str], Tuple[str, ...]] =(), *, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: str ='', popup_align_left: bool =False, no_arrow_button: bool =False, no_preview: bool =False, fit_width: bool =False, height_mode: str ="regular", **kwargs) -> Union[int, str]:
    return dcg.Combo(CONTEXT, items=items, label=label, user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, popup_align_left=popup_align_left, no_arrow_button=no_arrow_button, no_preview=no_preview, fit_width=fit_width, height_mode=height_mode, **kwargs)

def double4_value(*, label: str =None, user_data: Any =None, default_value: Any =(0.0, 0.0, 0.0, 0.0), parent: Union[int, str] =mvReservedUUID_3, **kwargs) -> Union[int, str]:
    return dcg.SharedDouble4(CONTEXT, default_value)

def double_value(*, label: str =None, user_data: Any =None, default_value: float =0.0, parent: Union[int, str] =mvReservedUUID_3, **kwargs) -> Union[int, str]:
    return dcg.SharedDouble(CONTEXT, default_value)

def drag_double(*, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: float =0.0, format: str ='%0.3f', speed: float =1.0, min_value: float =0.0, max_value: float =100.0, no_input: bool =False, clamped: bool =False, **kwargs) -> Union[int, str]:
    return dcg.Slider(CONTEXT, label=label, format="double", size=1, drag=True, user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, print_format=format, speed=speed, min_value=min_value, max_value=max_value, no_input=no_input, clamped=clamped, **kwargs)

def drag_doublex(*, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: Any =(0.0, 0.0, 0.0, 0.0), size: int =4, format: str ='%0.3f', speed: float =1.0, min_value: float =0.0, max_value: float =100.0, no_input: bool =False, clamped: bool =False, **kwargs) -> Union[int, str]:
    return dcg.Slider(CONTEXT, label=label, format="double", drag=True, user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, size=size, print_format=format, speed=speed, min_value=min_value, max_value=max_value, no_input=no_input, clamped=clamped, **kwargs)

def drag_float(*, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: float =0.0, format: str ='%0.3f', speed: float =1.0, min_value: float =0.0, max_value: float =100.0, no_input: bool =False, clamped: bool =False, **kwargs) -> Union[int, str]:
    return dcg.Slider(CONTEXT, label=label, format="float", drag=True, size=1, user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, print_format=format, speed=speed, min_value=min_value, max_value=max_value, no_input=no_input, clamped=clamped, **kwargs)

def drag_floatx(*, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: Union[List[float], Tuple[float, ...]] =(0.0, 0.0, 0.0, 0.0), size: int =4, format: str ='%0.3f', speed: float =1.0, min_value: float =0.0, max_value: float =100.0, no_input: bool =False, clamped: bool =False, **kwargs) -> Union[int, str]:
    return dcg.Slider(CONTEXT, label=label, format="float", drag=True, user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, size=size, print_format=format, speed=speed, min_value=min_value, max_value=max_value, no_input=no_input, clamped=clamped, **kwargs)

def drag_int(*, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: int =0, format: str ='%d', speed: float =1.0, min_value: int =0, max_value: int =100, no_input: bool =False, clamped: bool =False, **kwargs) -> Union[int, str]:
    return dcg.Slider(CONTEXT, label=label, format="int", size=1, drag=True, user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, print_format=format, speed=speed, min_value=min_value, max_value=max_value, no_input=no_input, clamped=clamped, **kwargs)

def drag_intx(*, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: Union[List[int], Tuple[int, ...]] =(0, 0, 0, 0), size: int =4, format: str ='%d', speed: float =1.0, min_value: int =0, max_value: int =100, no_input: bool =False, clamped: bool =False, **kwargs) -> Union[int, str]:
    return dcg.Slider(CONTEXT, label=label, format="int", drag=True, user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, size=size, print_format=format, speed=speed, min_value=min_value, max_value=max_value, no_input=no_input, clamped=clamped, **kwargs)

def drawlist(width : int, height : int, *, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, **kwargs) -> Union[int, str]:
    return dcg.DrawInWindow(CONTEXT, button=True, width=width, height=height, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, **kwargs)

def dynamic_texture(width : int, height : int, default_value : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, parent: Union[int, str] =mvReservedUUID_2, **kwargs) -> Union[int, str]:
    content = np.asarray(default_value).reshape([height, width, -1])
    if content.dtype == np.float64:
        content = np.asarray(content, dtype=np.float32)
    if content.dtype == np.float32 and content.max() > 1.:
        content /= 255.

    return dcg.Texture(CONTEXT, content, hint_dynamic=True, label=label, user_data=user_data, **kwargs)

def float4_value(*, label: str =None, user_data: Any =None, default_value: Union[List[float], Tuple[float, ...]] =(0.0, 0.0, 0.0, 0.0), parent: Union[int, str] =mvReservedUUID_3, **kwargs) -> Union[int, str]:
    return dcg.SharedFloat4(CONTEXT, default_value)

def float_value(*, label: str =None, user_data: Any =None, default_value: float =0.0, parent: Union[int, str] =mvReservedUUID_3, **kwargs) -> Union[int, str]:
    return dcg.SharedFloat(CONTEXT, default_value)

def float_vect_value(*, label: str =None, user_data: Any =None, default_value: Union[List[float], Tuple[float, ...]] =(), parent: Union[int, str] =mvReservedUUID_3, **kwargs) -> Union[int, str]:
    return dcg.SharedFloatVect(CONTEXT, default_value)

def group(*, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, horizontal: bool =False, horizontal_spacing: float =-1, xoffset: float =0.0, **kwargs) -> Union[int, str]:
    if horizontal:
        target_class = dcg.HorizontalLayout
    else:
        target_class = dcg.VerticalLayout
    if horizontal_spacing != -1:
        kwargs["spacing"] = horizontal_spacing
    if xoffset != 0.:
        # We use a callback as we don't know at this point the number of children
        def assign_spaces(item, other, user_data, xoffset=xoffset):
            num_items = len(item.children)
            positions = [i * xoffset for i in range(num_items)]
            item.positions = positions
        kwargs["callback"] = assign_spaces
    return target_class(CONTEXT, label=label, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, **kwargs)

def handler_registry(*, label: str =None, user_data: Any =None, show: bool =True, **kwargs) -> Union[int, str]:
    item = dcg.HandlerList(CONTEXT, label=label, user_data=user_data, show=show, attach=False, **kwargs)
    # global handler registries concatenate to each other
    with CONTEXT.viewport.mutex:
        CONTEXT.viewport.handlers += [item]
    return item

def image(texture_tag : Union[int, str], *, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, tint_color: Union[List[float], Tuple[float, ...]] =-1, border_color: Union[List[float], Tuple[float, ...]] =(0, 0, 0, 0), uv_min: Union[List[float], Tuple[float, ...]] =(0.0, 0.0), uv_max: Union[List[float], Tuple[float, ...]] =(1.0, 1.0), **kwargs) -> Union[int, str]:
    # TODO: border_color
    return dcg.Image(CONTEXT, texture=CONTEXT.get(texture_tag), label=label, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, drag_callback=drag_callback, drop_callback=drop_callback, show=show, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, color_multiplier=tint_color, uv=(uv_min[0], uv_min[1], uv_max[0], uv_max[1]), **kwargs)

def image_button(texture_tag : Union[int, str], *, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, tint_color: Union[List[float], Tuple[float, ...]] =-1, background_color: Union[List[float], Tuple[float, ...]] =(0, 0, 0, 0), uv_min: Union[List[float], Tuple[float, ...]] =(0.0, 0.0), uv_max: Union[List[float], Tuple[float, ...]] =(1.0, 1.0), **kwargs) -> Union[int, str]:
    return dcg.Image(CONTEXT, button=True, texture=CONTEXT.get(texture_tag), label=label, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, color_multiplier=tint_color, background_color=background_color, uv=(uv_min[0], uv_min[1], uv_max[0], uv_max[1]), **kwargs)

def image_series(texture_tag : Union[int, str], bounds_min : Union[List[float], Tuple[float, ...]], bounds_max : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, uv_min: Union[List[float], Tuple[float, ...]] =(0.0, 0.0), uv_max: Union[List[float], Tuple[float, ...]] =(1.0, 1.0), tint_color: Union[int, List[int], Tuple[int, ...]] =-1, **kwargs) -> Union[int, str]:
    parent = kwargs.pop("parent", None)
    if parent is None:
        axis_y = LOCAL_STORAGE.CURRENT_Y_AXIS
    else:
        axis_y = parent

    plot = axis_y.plot

    # TODO: tint color if set should be attributed to the legend color
    parent_item =  dcg.DrawInPlot(CONTEXT, parent=plot, axes=(dcg.Axis.X1, axis_y.axis), no_legend=False, label=label, user_data=user_data, **kwargs)

    dcg.DrawImage(CONTEXT, parent=parent_item, texture=CONTEXT.get(texture_tag), pmin=bounds_min, pmax=bounds_max, show=show, uv_min=uv_min, uv_max=uv_max, color_multiplier=tint_color)

    return parent_item

def inf_line_series(x : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, horizontal: bool =False, **kwargs) -> Union[int, str]:
    parent = kwargs.pop("parent", None)
    if parent is None:
        axis_y = LOCAL_STORAGE.CURRENT_Y_AXIS
    else:
        axis_y = parent

    plot = axis_y.plot

    return dcg.PlotInfLines(CONTEXT, parent=plot, axes=(dcg.Axis.X1, axis_y.axis), X=x, label=label, user_data=user_data, show=show, horizontal=horizontal, **kwargs)

def input_double(*, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: float =0.0, format: str ='%.3f', min_value: float =0.0, max_value: float =100.0, step: float =0.1, step_fast: float =1.0, min_clamped: bool =False, max_clamped: bool =False, on_enter: bool =False, readonly: bool =False, **kwargs) -> Union[int, str]:
    if not(min_clamped):
        min_value = -1e100
    if not(max_clamped):
        max_value = 1e100

    return dcg.InputValue(CONTEXT, format="double", label=label, user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, print_format=format, min_value=min_value, max_value=max_value, step=step, step_fast=step_fast, callback_on_enter=on_enter, readonly=readonly, **kwargs)

def input_doublex(*, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: Any =(0.0, 0.0, 0.0, 0.0), format: str ='%.3f', min_value: float =0.0, max_value: float =100.0, size: int =4, min_clamped: bool =False, max_clamped: bool =False, on_enter: bool =False, readonly: bool =False, **kwargs) -> Union[int, str]:
    if not(min_clamped):
        min_value = -1e100
    if not(max_clamped):
        max_value = 1e100

    return dcg.InputValue(CONTEXT, format="double", label=label, user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, print_format=format, min_value=min_value, max_value=max_value, size=size, callback_on_enter=on_enter, readonly=readonly, **kwargs)

def input_float(*, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: float =0.0, format: str ='%.3f', min_value: float =0.0, max_value: float =100.0, step: float =0.1, step_fast: float =1.0, min_clamped: bool =False, max_clamped: bool =False, on_enter: bool =False, readonly: bool =False, **kwargs) -> Union[int, str]:
    if not(min_clamped):
        min_value = -1e100
    if not(max_clamped):
        max_value = 1e100

    return dcg.InputValue(CONTEXT, format="float", label=label, user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, print_format=format, min_value=min_value, max_value=max_value, step=step, step_fast=step_fast, callback_on_enter=on_enter, readonly=readonly, **kwargs)

def input_floatx(*, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: Union[List[float], Tuple[float, ...]] =(0.0, 0.0, 0.0, 0.0), format: str ='%.3f', min_value: float =0.0, max_value: float =100.0, size: int =4, min_clamped: bool =False, max_clamped: bool =False, on_enter: bool =False, readonly: bool =False, **kwargs) -> Union[int, str]:
    if not(min_clamped):
        min_value = -1e100
    if not(max_clamped):
        max_value = 1e100

    return dcg.InputValue(CONTEXT, format="float", label=label, user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, print_format=format, min_value=min_value, max_value=max_value, size=size, callback_on_enter=on_enter, readonly=readonly, **kwargs)

def input_int(*, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: int =0, min_value: int =0, max_value: int =100, step: int =1, step_fast: int =100, min_clamped: bool =False, max_clamped: bool =False, on_enter: bool =False, readonly: bool =False, **kwargs) -> Union[int, str]:
    if not(min_clamped):
        min_value = -1e100
    if not(max_clamped):
        max_value = 1e100

    return dcg.InputValue(CONTEXT, format="int", label=label, user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, min_value=min_value, max_value=max_value, step=step, step_fast=step_fast, callback_on_enter=on_enter, readonly=readonly, **kwargs)

def input_intx(*, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: Union[List[int], Tuple[int, ...]] =(0, 0, 0, 0), min_value: int =0, max_value: int =100, size: int =4, min_clamped: bool =False, max_clamped: bool =False, on_enter: bool =False, readonly: bool =False, **kwargs) -> Union[int, str]:
    if not(min_clamped):
        min_value = -1e100
    if not(max_clamped):
        max_value = 1e100

    return dcg.InputValue(CONTEXT, format="int", label=label, user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, min_value=min_value, max_value=max_value, size=size, callback_on_enter=on_enter, readonly=readonly, **kwargs)

def input_text(*, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: str ='', hint: str ='', multiline: bool =False, no_spaces: bool =False, uppercase: bool =False, tab_input: bool =False, decimal: bool =False, hexadecimal: bool =False, readonly: bool =False, password: bool =False, scientific: bool =False, on_enter: bool =False, auto_select_all: bool =False, ctrl_enter_for_new_line: bool =False, no_horizontal_scroll: bool =False, always_overwrite: bool =False, no_undo_redo: bool =False, escape_clears_all: bool =False, **kwargs) -> Union[int, str]:
    return dcg.InputText(CONTEXT, label=label, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, hint=hint, multiline=multiline, no_spaces=no_spaces, uppercase=uppercase, tab_input=tab_input, decimal=decimal, hexadecimal=hexadecimal, readonly=readonly, password=password, scientific=scientific, callback_on_enter=on_enter, auto_select_all=auto_select_all, ctrl_enter_for_new_line=ctrl_enter_for_new_line, no_horizontal_scroll=no_horizontal_scroll, always_overwrite=always_overwrite, no_undo_redo=no_undo_redo, escape_clears_all=escape_clears_all, **kwargs)

def int4_value(*, label: str =None, user_data: Any =None, default_value: Union[List[int], Tuple[int, ...]] =(0, 0, 0, 0), parent: Union[int, str] =mvReservedUUID_3, **kwargs) -> Union[int, str]:
    return dcg.SharedInt4(CONTEXT, default_value)

def int_value(*, label: str =None, user_data: Any =None, default_value: int =0, parent: Union[int, str] =mvReservedUUID_3, **kwargs) -> Union[int, str]:
    return dcg.SharedInt(CONTEXT, default_value)

def item_activated_handler(*, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, **kwargs) -> Union[int, str]:
    return dcg.ActivatedHandler(CONTEXT, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def item_active_handler(*, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, **kwargs) -> Union[int, str]:
    return dcg.ActiveHandler(CONTEXT, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def item_clicked_handler(button : int =-1, *, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, **kwargs) -> Union[int, str]:
    return dcg.ClickedHandler(CONTEXT, button=button, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def item_deactivated_after_edit_handler(*, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, **kwargs) -> Union[int, str]:
    return dcg.DeactivatedAfterEditHandler(CONTEXT, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def item_deactivated_handler(*, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, **kwargs) -> Union[int, str]:
    return dcg.DeactivatedHandler(CONTEXT, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def item_double_clicked_handler(button : int =-1, *, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, **kwargs) -> Union[int, str]:
    return dcg.DoubleClickedHandler(CONTEXT, button=button, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def item_edited_handler(*, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, **kwargs) -> Union[int, str]:
    return dcg.EditedHandler(CONTEXT, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def item_focus_handler(*, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, **kwargs) -> Union[int, str]:
    return dcg.FocusHandler(CONTEXT, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def item_handler_registry(*, label: str =None, user_data: Any =None, show: bool =True, **kwargs) -> Union[int, str]:
    item = dcg.HandlerList(CONTEXT, label=label, user_data=user_data, show=show, **kwargs)
    return item

def item_hover_handler(*, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, **kwargs) -> Union[int, str]:
    return dcg.HoverHandler(CONTEXT, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def item_resize_handler(*, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, **kwargs) -> Union[int, str]:
    return dcg.ResizeHandler(CONTEXT, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def item_toggled_open_handler(*, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, **kwargs) -> Union[int, str]:
    return dcg.ToggledOpenHandler(CONTEXT, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def item_visible_handler(*, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, **kwargs) -> Union[int, str]:
    return dcg.RenderedHandler(CONTEXT, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def key_down_handler(key : int =mvKey_None, *, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, parent: Union[int, str] =mvReservedUUID_1, **kwargs) -> Union[int, str]:
    if key is mvKey_None:
        return dcg.utils.AnyKeyDownHandler(CONTEXT, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)
    else:
        return dcg.KeyDownHandler(CONTEXT, key=key, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def key_press_handler(key : int =mvKey_None, *, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, parent: Union[int, str] =mvReservedUUID_1, **kwargs) -> Union[int, str]:
    if key is mvKey_None:
        return dcg.utils.AnyKeyPressHandler(CONTEXT, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)
    else:
        return dcg.KeyPressHandler(CONTEXT, key=key, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def key_release_handler(key : int =mvKey_None, *, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, parent: Union[int, str] =mvReservedUUID_1, **kwargs) -> Union[int, str]:
    if key is mvKey_None:
        return dcg.AnyKeyReleaseHandler(CONTEXT, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)
    else:
        return dcg.KeyReleaseHandler(CONTEXT, key=key, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def line_series(x : Union[List[float], Tuple[float, ...]], y : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, segments: bool =False, loop: bool =False, skip_nan: bool =False, no_clip: bool =False, shaded: bool =False, **kwargs) -> Union[int, str]:
    parent = kwargs.pop("parent", None)
    if parent is None:
        axis_y = LOCAL_STORAGE.CURRENT_Y_AXIS
    else:
        axis_y = parent

    plot = axis_y.plot

    return dcg.PlotLine(CONTEXT, parent=plot, axes=(dcg.Axis.X1, axis_y.axis), X=x, Y=y, label=label, user_data=user_data, show=show, segments=segments, loop=loop, skip_nan=skip_nan, no_clip=no_clip, shaded=shaded, **kwargs)

def listbox(items : Union[List[str], Tuple[str, ...]] =(), *, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: str ='', num_items: int =3, **kwargs) -> Union[int, str]:
    return dcg.ListBox(CONTEXT, items=items, label=label, user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, num_items_shown_when_open=num_items, **kwargs)

def menu(*, label: str =None, user_data: Any =None, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', drop_callback: Callable =None, show: bool =True, enabled: bool =True, filter_key: str ='', tracked: bool =False, track_offset: float =0.5, **kwargs) -> Union[int, str]:
   return dcg.Menu(CONTEXT, label=label, user_data=user_data, indent=indent, payload_type=payload_type, drop_callback=drop_callback, show=show, enabled=enabled, filter_key=filter_key, tracked=tracked, track_offset=track_offset, **kwargs)

def menu_bar(*, label: str =None, user_data: Any =None, indent: int =0, show: bool =True, **kwargs) -> Union[int, str]:
    return dcg.MenuBar(CONTEXT, label=label, user_data=user_data, indent=indent, show=show, **kwargs)

def menu_item(*, label: str =None, user_data: Any =None, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: bool =False, shortcut: str ='', check: bool =False, **kwargs) -> Union[int, str]:
    return dcg.MenuItem(CONTEXT, label=label, user_data=user_data, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drop_callback=drop_callback, show=show, enabled=enabled, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, shortcut=shortcut, check=check, **kwargs)

def mouse_click_handler(button : int =-1, *, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, parent: Union[int, str] =mvReservedUUID_1, **kwargs) -> Union[int, str]:
    return dcg.MouseClickHandler(CONTEXT, button=button, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def mouse_double_click_handler(button : int =-1, *, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, parent: Union[int, str] =mvReservedUUID_1, **kwargs) -> Union[int, str]:
    return dcg.MouseDoubleClickHandler(CONTEXT, button=button, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def mouse_down_handler(button : int =-1, *, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, parent: Union[int, str] =mvReservedUUID_1, **kwargs) -> Union[int, str]:
    return dcg.MouseDownHandler(CONTEXT, button=button, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def mouse_drag_handler(button : int =-1, threshold : float =10.0, *, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, parent: Union[int, str] =mvReservedUUID_1, **kwargs) -> Union[int, str]:
    return dcg.MouseDragHandler(CONTEXT, button=button, threshold=threshold, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def mouse_move_handler(*, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, parent: Union[int, str] =mvReservedUUID_1, **kwargs) -> Union[int, str]:
    return dcg.MouseMoveHandler(CONTEXT, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def mouse_release_handler(button : int =-1, *, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, parent: Union[int, str] =mvReservedUUID_1, **kwargs) -> Union[int, str]:
    return dcg.MouseReleaseHandler(CONTEXT, button=button, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def mouse_wheel_handler(*, label: str =None, user_data: Any =None, callback: Callable =None, show: bool =True, parent: Union[int, str] =mvReservedUUID_1, **kwargs) -> Union[int, str]:
    return dcg.MouseWheelHandler(CONTEXT, label=label, user_data=user_data, callback=wrap_callback(callback), show=show, **kwargs)

def plot(*, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, no_title: bool =False, no_menus: bool =False, no_box_select: bool =False, no_mouse_pos: bool =False, query: bool =False, query_color: Union[List[float], Tuple[float, ...]] =(0, 255, 0, 255), min_query_rects: int =1, max_query_rects: int =1, crosshairs: bool =False, equal_aspects: bool =False, no_inputs: bool =False, no_frame: bool =False, use_local_time: bool =False, use_ISO8601: bool =False, use_24hour_clock: bool =False, pan_button: int =mvMouseButton_Left, pan_mod: int =mvKey_None, context_menu_button: int =mvMouseButton_Right, fit_button: int =mvMouseButton_Left, box_select_button: int =mvMouseButton_Right, box_select_mod: int =mvKey_None, box_select_cancel_button: int =mvMouseButton_Left, query_toggle_mod: int =mvKey_ModCtrl, horizontal_mod: int =mvKey_ModAlt, vertical_mod: int =mvKey_ModShift, override_mod: int =mvKey_ModCtrl, zoom_mod: int =mvKey_None, zoom_rate: int =0.1, **kwargs) -> Union[int, str]:
    # Won't work if plot are created in a row and them the axes
    LOCAL_STORAGE.Y_AXIS = dcg.Axis.Y1

    return dcg.Plot(CONTEXT, label=label, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, no_title=no_title, no_menus=no_menus, no_box_select=no_box_select, no_mouse_pos=no_mouse_pos, query=query, query_color=query_color, min_query_rects=min_query_rects, max_query_rects=max_query_rects, crosshairs=crosshairs, equal_aspects=equal_aspects, no_inputs=no_inputs, no_frame=no_frame, use_local_time=use_local_time, use_ISO8601=use_ISO8601, use_24hour_clock=use_24hour_clock, pan_button=pan_button, pan_mod=pan_mod, context_menu_button=context_menu_button, fit_button=fit_button, box_select_button=box_select_button, box_select_mod=box_select_mod, box_select_cancel_button=box_select_cancel_button, query_toggle_mod=query_toggle_mod, horizontal_mod=horizontal_mod, vertical_mod=vertical_mod, override_mod=override_mod, zoom_mod=zoom_mod, zoom_rate=zoom_rate, **kwargs)

def plot_axis(axis : int, *, label: str =None, user_data: Any =None, payload_type: str ='$$DPG_PAYLOAD', drop_callback: Callable =None, show: bool =True, no_label: bool =False, no_gridlines: bool =False, no_tick_marks: bool =False, no_tick_labels: bool =False, no_initial_fit: bool =False, no_menus: bool =False, no_side_switch: bool =False, no_highlight: bool =False, opposite: bool =False, foreground_grid: bool =False, tick_format: str ='', scale: int =mvPlotScale_Linear, invert: bool =False, auto_fit: bool =False, range_fit: bool =False, pan_stretch: bool =False, lock_min: bool =False, lock_max: bool =False, **kwargs) -> Union[int, str]:
    parent = kwargs.pop("parent", None)
    if parent is None:
        parent = CONTEXT.fetch_parent_queue_back()
    assert(parent is not None)
    is_x_axis = True
    if axis == mvXAxis:
        axis = dcg.Axis.X1
    elif axis == mvXAxis2:
        axis = dcg.Axis.X2
    elif axis == mvXAxis3:
        axis = dcg.Axis.X3
    elif axis == mvYAxis:
        axis = dcg.Axis.Y1
        is_x_axis = False
    elif axis == mvYAxis2:
        axis = dcg.Axis.Y2
        is_x_axis = False
    elif axis == mvYAxis3:
        axis = dcg.Axis.Y3
        is_x_axis = False
    else:
        assert(False)
    if is_x_axis:
        item = PlotAxisX(CONTEXT, axis, parent, label=label, user_data=user_data, payload_type=payload_type, drop_callback=drop_callback, show=show, no_label=no_label, no_gridlines=no_gridlines, no_tick_marks=no_tick_marks, no_tick_labels=no_tick_labels, no_initial_fit=no_initial_fit, no_menus=no_menus, no_side_switch=no_side_switch, no_highlight=no_highlight, opposite=opposite, foreground_grid=foreground_grid, tick_format=tick_format, scale=scale, invert=invert, auto_fit=auto_fit, range_fit=range_fit, pan_stretch=pan_stretch, lock_min=lock_min, lock_max=lock_max, **kwargs)
    else:
        item = PlotAxisY(CONTEXT, axis, parent, label=label, user_data=user_data, payload_type=payload_type, drop_callback=drop_callback, show=show, no_label=no_label, no_gridlines=no_gridlines, no_tick_marks=no_tick_marks, no_tick_labels=no_tick_labels, no_initial_fit=no_initial_fit, no_menus=no_menus, no_side_switch=no_side_switch, no_highlight=no_highlight, opposite=opposite, foreground_grid=foreground_grid, tick_format=tick_format, scale=scale, invert=invert, auto_fit=auto_fit, range_fit=range_fit, pan_stretch=pan_stretch, lock_min=lock_min, lock_max=lock_max, **kwargs)
    return item

def plot_legend(*, label: str =None, user_data: Any =None, payload_type: str ='$$DPG_PAYLOAD', drop_callback: Callable =None, show: bool =True, location: int =5, horizontal: bool =False, sort: bool =False, outside: bool =False, no_highlight_item: bool =False, no_highlight_axis: bool =False, no_menus: bool =False, no_buttons: bool =False, **kwargs) -> Union[int, str]:
    parent = kwargs.pop("parent", None)
    if parent is None:
        parent = CONTEXT.fetch_parent_queue_back()
    assert(parent is not None)

    item = dcg.PlotLegendConfig(CONTEXT, label=label, user_data=user_data, payload_type=payload_type, drop_callback=drop_callback, show=show, location=location, horizontal=horizontal, sort=sort, outside=outside, no_highlight_item=no_highlight_item, no_highlight_axis=no_highlight_axis, no_menus=no_menus, no_buttons=no_buttons, **kwargs)

    parent.legend_config = item
    return item

def progress_bar(*, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, overlay: str ='', default_value: float =0.0, **kwargs) -> Union[int, str]:
    return dcg.ProgressBar(CONTEXT, label=label, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, drag_callback=drag_callback, drop_callback=drop_callback, show=show, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, overlay=overlay, value=default_value, **kwargs)

def radio_button(items : Union[List[str], Tuple[str, ...]] =(), *, label: str =None, user_data: Any =None, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: str ='', horizontal: bool =False, **kwargs) -> Union[int, str]:
    return dcg.RadioButton(CONTEXT, items=items, label=label, user_data=user_data, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, horizontal=horizontal, **kwargs)

def raw_texture(width : int, height : int, default_value : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, format: int =mvFormat_Float_rgba, parent: Union[int, str] =mvReservedUUID_2, **kwargs) -> Union[int, str]:
    content = np.asarray(default_value).reshape([height, width, -1])
    if content.dtype == np.float64:
        content = np.asarray(content, dtype=np.float32)
    if content.dtype == np.float32 and content.max() > 1.:
        content /= 255.

    return dcg.Texture(CONTEXT, content, hint_dynamic=True, label=label, user_data=user_data, **kwargs)

def scatter_series(x : Union[List[float], Tuple[float, ...]], y : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, no_clip: bool =False, **kwargs) -> Union[int, str]:
    parent = kwargs.pop("parent", None)
    if parent is None:
        axis_y = LOCAL_STORAGE.CURRENT_Y_AXIS
    else:
        axis_y = parent

    plot = axis_y.plot

    return dcg.PlotScatter(CONTEXT, parent=plot, axes=(dcg.Axis.X1, axis_y.axis), X=x, Y=y, label=label, user_data=user_data, show=show, no_clip=no_clip, **kwargs)

def selectable(*, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: bool =False, span_columns: bool =False, disable_popup_close: bool =False, **kwargs) -> Union[int, str]:
    return dcg.Selectable(CONTEXT, label=label, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, span_columns=span_columns, disable_popup_close=disable_popup_close, **kwargs)

def separator(*, label: str =None, user_data: Any =None, indent: int =0, show: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], **kwargs) -> Union[int, str]:
    return dcg.Separator(CONTEXT, label=label, user_data=user_data, indent=indent, show=show, pos=pos, **kwargs)

def shade_series(x : Union[List[float], Tuple[float, ...]], y1 : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, y2: Any =[], **kwargs) -> Union[int, str]:
    parent = kwargs.pop("parent", None)
    if parent is None:
        axis_y = LOCAL_STORAGE.CURRENT_Y_AXIS
    else:
        axis_y = parent

    plot = axis_y.plot

    return dcg.PlotShadedLine(CONTEXT, parent=plot, axes=(dcg.Axis.X1, axis_y.axis), X=x, Y1=y1, label=label, user_data=user_data, show=show, Y2=y2, **kwargs)

def simple_plot(*, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: Union[List[float], Tuple[float, ...]] =(), overlay: str ='', histogram: bool =False, autosize: bool =True, min_scale: float =0.0, max_scale: float =0.0, **kwargs) -> Union[int, str]:
    return dcg.SimplePlot(CONTEXT, label=label, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, drag_callback=drag_callback, drop_callback=drop_callback, show=show, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, overlay=overlay, histogram=histogram, autoscale=autosize, scale_min=min_scale, scale_max=max_scale, **kwargs)

def slider_double(*, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: float =0.0, vertical: bool =False, no_input: bool =False, clamped: bool =False, min_value: float =0.0, max_value: float =100.0, format: str ='%.3f', **kwargs) -> Union[int, str]:
    return dcg.Slider(CONTEXT, label=label, format="double", size=1, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, vertical=vertical, no_input=no_input, clamped=clamped, min_value=min_value, max_value=max_value, print_format=format, **kwargs)

def slider_doublex(*, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: Any =(0.0, 0.0, 0.0, 0.0), size: int =4, no_input: bool =False, clamped: bool =False, min_value: float =0.0, max_value: float =100.0, format: str ='%.3f', **kwargs) -> Union[int, str]:
    return dcg.Slider(CONTEXT, label=label, format="double", user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, size=size, no_input=no_input, clamped=clamped, min_value=min_value, max_value=max_value, print_format=format, **kwargs)

def slider_float(*, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: float =0.0, vertical: bool =False, no_input: bool =False, clamped: bool =False, min_value: float =0.0, max_value: float =100.0, format: str ='%.3f', **kwargs) -> Union[int, str]:
    return dcg.Slider(CONTEXT, label=label, format="float", size=1, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, vertical=vertical, no_input=no_input, clamped=clamped, min_value=min_value, max_value=max_value, print_format=format, **kwargs)

def slider_floatx(*, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: Union[List[float], Tuple[float, ...]] =(0.0, 0.0, 0.0, 0.0), size: int =4, no_input: bool =False, clamped: bool =False, min_value: float =0.0, max_value: float =100.0, format: str ='%.3f', **kwargs) -> Union[int, str]:
    return dcg.Slider(CONTEXT, label=label, format="float", user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, size=size, no_input=no_input, clamped=clamped, min_value=min_value, max_value=max_value, print_format=format, **kwargs)

def slider_int(*, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: int =0, vertical: bool =False, no_input: bool =False, clamped: bool =False, min_value: int =0, max_value: int =100, format: str ='%d', **kwargs) -> Union[int, str]:
    return dcg.Slider(CONTEXT, label=label, format="int", size=1, user_data=user_data, width=width, height=height, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, vertical=vertical, no_input=no_input, clamped=clamped, min_value=min_value, max_value=max_value, print_format=format, **kwargs)

def slider_intx(*, label: str =None, user_data: Any =None, width: int =0, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, enabled: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_value: Union[List[int], Tuple[int, ...]] =(0, 0, 0, 0), size: int =4, no_input: bool =False, clamped: bool =False, min_value: int =0, max_value: int =100, format: str ='%d', **kwargs) -> Union[int, str]:
    return dcg.Slider(CONTEXT, label=label, format="int", user_data=user_data, width=width, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, enabled=enabled, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_value, size=size, no_input=no_input, clamped=clamped, min_value=min_value, max_value=max_value, print_format=format, **kwargs)

def spacer(*, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, show: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], **kwargs) -> Union[int, str]:
    return dcg.Spacer(CONTEXT, label=label, user_data=user_data, width=width, height=height, indent=indent, show=show, pos=pos, **kwargs)

def stage(*, label: str =None, user_data: Any =None, **kwargs) -> Union[int, str]:
    item = dcg.PlaceHolderParent(CONTEXT, **kwargs)
    return item

def stair_series(x : Union[List[float], Tuple[float, ...]], y : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, pre_step: bool =False, shaded: bool =False, **kwargs) -> Union[int, str]:
    parent = kwargs.pop("parent", None)
    if parent is None:
        axis_y = LOCAL_STORAGE.CURRENT_Y_AXIS
    else:
        axis_y = parent

    plot = axis_y.plot

    return dcg.PlotStairs(CONTEXT, parent=plot, axes=(dcg.Axis.X1, axis_y.axis), X=x, Y=y, label=label, user_data=user_data, show=show, pre_step=pre_step, shaded=shaded, **kwargs)

def static_texture(width : int, height : int, default_value : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, parent: Union[int, str] =mvReservedUUID_2, **kwargs) -> Union[int, str]:
    content = np.asarray(default_value).reshape([height, width, -1])
    if content.dtype == np.float64:
        content = np.asarray(content, dtype=np.float32)
    if content.dtype == np.float32 and content.max() > 1.:
        content /= 255.
    return dcg.Texture(CONTEXT, content, label=label, user_data=user_data, **kwargs)

def stem_series(x : Union[List[float], Tuple[float, ...]], y : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, indent: int =0, show: bool =True, horizontal: bool =False, **kwargs) -> Union[int, str]:
    parent = kwargs.pop("parent", None)
    if parent is None:
        axis_y = LOCAL_STORAGE.CURRENT_Y_AXIS
    else:
        axis_y = parent

    plot = axis_y.plot

    return dcg.PlotStems(CONTEXT, parent=plot, axes=(dcg.Axis.X1, axis_y.axis), X=x, Y=y, label=label, user_data=user_data, indent=indent, show=show, horizontal=horizontal, **kwargs)

def string_value(*, label: str =None, user_data: Any =None, default_value: str ='', parent: Union[int, str] =mvReservedUUID_3, **kwargs) -> Union[int, str]:
    return dcg.SharedStr(CONTEXT, label=label, user_data=user_data, value=default_value, **kwargs)

def subplots(rows : int, columns : int, *, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, callback: Callable =None, show: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, row_ratios: Union[List[float], Tuple[float, ...]] =[], column_ratios: Union[List[float], Tuple[float, ...]] =[], no_title: bool =False, no_menus: bool =False, no_resize: bool =False, no_align: bool =False, share_series: bool =False, link_rows: bool =False, link_columns: bool =False, link_all_x: bool =False, link_all_y: bool =False, column_major: bool =False, **kwargs) -> Union[int, str]:
    return dcg.Subplots(CONTEXT, rows=rows, cols=columns, label=label, user_data=user_data, width=width, height=height, indent=indent, callback=wrap_callback(callback), show=show, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, row_ratios=row_ratios, column_ratios=column_ratios, no_title=no_title, no_menus=no_menus, no_resize=no_resize, no_align=no_align, share_legends=share_series, share_rows=link_rows, share_cols=link_columns, share_x_all=link_all_x, share_y_all=link_all_y, col_major=column_major, **kwargs)

def tab(*, label: str =None, user_data: Any =None, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', drop_callback: Callable =None, show: bool =True, filter_key: str ='', tracked: bool =False, track_offset: float =0.5, closable: bool =False, no_tooltip: bool =False, order_mode: int =0, **kwargs) -> Union[int, str]:
    return dcg.Tab(CONTEXT, label=label, user_data=user_data, indent=indent, payload_type=payload_type, drop_callback=drop_callback, show=show, filter_key=filter_key, tracked=tracked, track_offset=track_offset, closable=closable, no_tooltip=no_tooltip, order_mode=order_mode, **kwargs)

def tab_bar(*, label: str =None, user_data: Any =None, indent: int =0, callback: Callable =None, show: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, reorderable: bool =False, **kwargs) -> Union[int, str]:
    return dcg.TabBar(CONTEXT, label=label, user_data=user_data, indent=indent, callback=wrap_callback(callback), show=show, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, reorderable=reorderable, **kwargs)

def tab_button(*, label: str =None, user_data: Any =None, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', callback: Callable =None, drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, filter_key: str ='', tracked: bool =False, track_offset: float =0.5, no_reorder: bool =False, leading: bool =False, trailing: bool =False, no_tooltip: bool =False, **kwargs) -> Union[int, str]:
    return dcg.TabButton(CONTEXT, label=label, user_data=user_data, indent=indent, payload_type=payload_type, callback=wrap_callback(callback), drag_callback=drag_callback, drop_callback=drop_callback, show=show, filter_key=filter_key, tracked=tracked, track_offset=track_offset, no_reorder=no_reorder, leading=leading, trailing=trailing, no_tooltip=no_tooltip, **kwargs)

def table(*, label: str =None, user_data: Any =None, width: int =0, height: int =0, indent: int =0, callback: Callable =None, show: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', header_row: bool =True, clipper: bool =False, inner_width: int =0, policy: int =0, freeze_rows: int =0, freeze_columns: int =0, sort_multi: bool =False, sort_tristate: bool =False, resizable: bool =False, reorderable: bool =False, hideable: bool =False, sortable: bool =False, context_menu_in_body: bool =False, row_background: bool =False, borders_innerH: bool =False, borders_outerH: bool =False, borders_innerV: bool =False, borders_outerV: bool =False, no_host_extendX: bool =False, no_host_extendY: bool =False, no_keep_columns_visible: bool =False, precise_widths: bool =False, no_clip: bool =False, pad_outerX: bool =False, no_pad_outerX: bool =False, no_pad_innerX: bool =False, scrollX: bool =False, scrollY: bool =False, no_saved_settings: bool =False, **kwargs) -> Union[int, str]:
    table = dcg.Table(CONTEXT)
    table.header = header_row
    flags = dcg.TableFlag.NONE
    if resizable:
        flags |= dcg.TableFlag.RESIZABLE
    if reorderable:
        flags |= dcg.TableFlag.REORDERABLE
    if hideable:
        flags |= dcg.TableFlag.HIDEABLE
    if sortable:
        flags |= dcg.TableFlag.SORTABLE
    if no_saved_settings:
        flags |= dcg.TableFlag.NO_SAVED_SETTINGS
    if context_menu_in_body:
        flags |= dcg.TableFlag.CONTEXT_MENU_IN_BODY
    if row_background:
        flags |= dcg.TableFlag.ROW_BG
    if borders_innerH:
        flags |= dcg.TableFlag.BORDERS_INNER_H
    if borders_outerH:
        flags |= dcg.TableFlag.BORDERS_OUTER_H
    if borders_innerV:
        flags |= dcg.TableFlag.BORDERS_INNER_V
    if borders_outerV:
        flags |= dcg.TableFlag.BORDERS_OUTER_V
    if no_host_extendX:
        flags |= dcg.TableFlag.NO_HOST_EXTEND_X
    if no_host_extendY:
        flags |= dcg.TableFlag.NO_HOST_EXTEND_Y
    if no_keep_columns_visible:
        flags |= dcg.TableFlag.NO_KEEP_COLUMNS_VISIBLE
    if precise_widths:
        flags |= dcg.TableFlag.PRECISE_WIDTHS
    if no_clip:
        flags |= dcg.TableFlag.NO_CLIP
    if pad_outerX:
        flags |= dcg.TableFlag.PAD_OUTER_X
    if no_pad_outerX:
        flags |= dcg.TableFlag.NO_PAD_OUTER_X
    if no_pad_innerX:
        flags |= dcg.TableFlag.NO_PAD_INNER_X
    if scrollX:
        flags |= dcg.TableFlag.SCROLL_X
    if scrollY:
        flags |= dcg.TableFlag.SCROLL_Y
    if sort_multi:
        flags |= dcg.TableFlag.SORT_MULTI
    if sort_tristate:
        flags |= dcg.TableFlag.SORT_TRISTATE

    if policy == mvTable_SizingFixedFit:
        flags |= dcg.TableFlag.SIZING_FIXED_FIT
    elif policy == mvTable_SizingFixedSame:
        flags |= dcg.TableFlag.SIZING_FIXED_SAME
    elif policy == mvTable_SizingStretchProp:
        flags |= dcg.TableFlag.SIZING_STRETCH_PROP
    elif policy == mvTable_SizingStretchSame:
        flags |= dcg.TableFlag.SIZING_STRETCH_SAME

    table.flags = flags
    table.num_cols_visible = 0
    table.num_rows_visible = 0
    return table

def table_cell(*, label: str =None, user_data: Any =None, height: int =0, show: bool =True, filter_key: str ='', **kwargs) -> Union[int, str]:
    return dcg.Layout(CONTEXT)

def table_column(*, label: str =None, user_data: Any =None, width: int =0, show: bool =True, enabled: bool =True, init_width_or_weight: float =0.0, default_hide: bool =False, default_sort: bool =False, width_stretch: bool =False, width_fixed: bool =False, no_resize: bool =False, no_reorder: bool =False, no_hide: bool =False, no_clip: bool =False, no_sort: bool =False, no_sort_ascending: bool =False, no_sort_descending: bool =False, no_header_width: bool =False, prefer_sort_ascending: bool =True, prefer_sort_descending: bool =False, indent_enable: bool =False, indent_disable: bool =False, angled_header: bool =False, no_header_label: bool =False, **kwargs) -> Union[int, str]:
    table : dcg.Table = kwargs.pop("parent", CONTEXT.fetch_last_created_container())
    if table is None:
        raise RuntimeError("table column must be added to a table")

    # Increase the visible count
    col_idx = table.num_cols_visible
    table.num_cols_visible += 1

    col_config : dcg.TableColConfig = table.col_config[col_idx]
    col_config.label = label
    col_config.width = init_width_or_weight#width
    col_config.show = show
    col_config.enabled = enabled
    col_config.stretch_weight = init_width_or_weight
    #col_config.default_hide = default_hide
    #col_config.default_sort = default_sort
    if width_stretch:
        col_config.stretch = True
    elif width_fixed:
        col_config.stretch = False
    else:
        col_config.stretch = None
    col_config.no_resize = no_resize
    col_config.no_reorder = no_reorder
    col_config.no_hide = no_hide
    col_config.no_clip = no_clip
    col_config.no_sort = no_sort
    #col_config.no_sort_ascending = no_sort_ascending
    #col_config.no_sort_descending = no_sort_descending
    #col_config.no_header_width = no_header_width
    col_config.prefer_sort_ascending = prefer_sort_ascending
    col_config.prefer_sort_descending = prefer_sort_descending
    #col_config.indent_enable = indent_enable
    #col_config.indent_disable = indent_disable
    #col_config.angled_header = angled_header
    #col_config.no_header_label = no_header_label

    return col_config
    #return table_column(label=label, user_data=user_data, width=width, show=show, enabled=enabled, init_width_or_weight=init_width_or_weight, default_hide=default_hide, default_sort=default_sort, width_stretch=width_stretch, width_fixed=width_fixed, no_resize=no_resize, no_reorder=no_reorder, no_hide=no_hide, no_clip=no_clip, no_sort=no_sort, no_sort_ascending=no_sort_ascending, no_sort_descending=no_sort_descending, no_header_width=no_header_width, prefer_sort_ascending=prefer_sort_ascending, prefer_sort_descending=prefer_sort_descending, indent_enable=indent_enable, indent_disable=indent_disable, angled_header=angled_header, no_header_label=no_header_label, **kwargs)

def table_row(*, label: str =None, user_data: Any =None, height: int =0, show: bool =True, filter_key: str ='', **kwargs) -> Union[int, str]:
    table : dcg.Table = kwargs.pop("parent", CONTEXT.fetch_last_created_container())
    if table is None:
        raise RuntimeError("table row must be added to a table")
    if height != 0:
        table.row_config[table.num_rows_visible].min_height = height
    table.num_rows_visible += 1
    return table.next_row
    #return table_row(label=label, user_data=user_data, height=height, show=show, filter_key=filter_key, **kwargs)

def text(default_value : str ='', *, label: str =None, user_data: Any =None, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, wrap: int =-1, bullet: bool =False, show_label: bool =False, **kwargs) -> Union[int, str]:
    return dcg.Text(CONTEXT, value=default_value, label=label, user_data=user_data, indent=indent, payload_type=payload_type, drag_callback=drag_callback, drop_callback=drop_callback, show=show, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, wrap=wrap, bullet=bullet, show_label=show_label, **kwargs)

def texture_registry(*, label: str =None, user_data: Any =None, show: bool =False, **kwargs) -> Union[int, str]:
    return dcg.PlaceHolderParent(CONTEXT)

def theme(*, label: str =None, user_data: Any =None, **kwargs) -> Union[int, str]:
    item = dcg.ThemeList(CONTEXT, label=label, user_data=user_data, **kwargs)
    return item

def theme_color(target : int =0, value : Union[List[int], Tuple[int, ...]] =(0, 0, 0, 255), *, category: int =0, **kwargs) -> Union[int, str]:
    # Note: This is ok but not very efficient, and purely for
    # dpg backward compatibility. If you have many elements in your theme,
    # prefer using a single dcgThemeColor
    if category == mvThemeCat_Core:
        theme_element = dcg.ThemeColorImGui(CONTEXT, parent=None, **kwargs)
    elif category == mvThemeCat_Plots:
        theme_element = dcg.ThemeColorImPlot(CONTEXT, parent=None, **kwargs)
    else:
        raise NotImplementedError("Theme category not implemented")
    setattr(theme_element, target, value)
    #theme_element.parent = CONTEXT.fetch_parent_queue_back()
    return theme_element

def theme_style(target : int =0, x : float =1.0, y : float =-1.0, *, category: int =0, **kwargs) -> Union[int, str]:
    # Note: This is ok but not very efficient, and purely for
    # dpg backward compatibility. If you have many elements in your theme,
    # prefer using a single dcgThemeStyle
    if category == mvThemeCat_Core:
        theme_element = dcg.ThemeStyleImGui(CONTEXT, parent=None, **kwargs)
    elif category == mvThemeCat_Plots:
        theme_element = dcg.ThemeStyleImPlot(CONTEXT, parent=None, **kwargs)
    else:
        raise NotImplementedError("Theme category not implemented")
    try:
        setattr(theme_element, target, (x, y))
    except Exception:
        setattr(theme_element, target, x)

    return theme_element

def tooltip(parent : Union[int, str], *, label: str =None, user_data: Any =None, show: bool =True, delay: float =0.0, hide_on_activity: bool =False, **kwargs) -> Union[int, str]:
    item = dcg.Tooltip(CONTEXT, attach=False, target=CONTEXT.get(parent), label=label, user_data=user_data, show=show, delay=delay, hide_on_activity=hide_on_activity, **kwargs)
    # Contrary to DPG, tooltips in DCG can only be sibling of UI elements
    # and not of plotElements for example. DPG does convert 'parent' in
    # 'insert after'. This won't work in our case all cases, so here we find
    # a place within one of the parents to insert ourselves somewhere.
    # There will be always a place to insert as viewports can accept tooltips,
    # but for performance it's better to insert low to benefit from check
    # skipping if the parent item is not visible.
    if parent is None:
        parent = last_item()
    while True:
        try:
            item.parent = parent
            return item
        except Exception:
            parent = parent.parent

def tree_node(*, label: str =None, user_data: Any =None, indent: int =0, payload_type: str ='$$DPG_PAYLOAD', drag_callback: Callable =None, drop_callback: Callable =None, show: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], filter_key: str ='', tracked: bool =False, track_offset: float =0.5, default_open: bool =False, open_on_double_click: bool =False, open_on_arrow: bool =False, leaf: bool =False, bullet: bool =False, selectable: bool =False, span_text_width: bool =False, span_full_width: bool =False, **kwargs) -> Union[int, str]:
    return dcg.TreeNode(CONTEXT, label=label, user_data=user_data, indent=indent, payload_type=payload_type, drag_callback=drag_callback, drop_callback=drop_callback, show=show, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, value=default_open, open_on_double_click=open_on_double_click, open_on_arrow=open_on_arrow, leaf=leaf, bullet=bullet, selectable=selectable, span_text_width=span_text_width, span_full_width=span_full_width, **kwargs)

def value_registry(*, label: str =None, user_data: Any =None, **kwargs) -> Union[int, str]:
    return dcg.PlaceHolderParent(CONTEXT, label=label, user_data=user_data, **kwargs)

def viewport_drawlist(*, label: str =None, user_data: Any =None, show: bool =True, filter_key: str ='', front: bool =True, **kwargs) -> Union[int, str]:
    return dcg.ViewportDrawList(CONTEXT, parent=CONTEXT.viewport, label=label, user_data=user_data, show=show, filter_key=filter_key, front=front, **kwargs)

def viewport_menu_bar(*, label: str =None, user_data: Any =None, indent: int =0, show: bool =True, **kwargs) -> Union[int, str]:
    return menu_bar(parent=CONTEXT.viewport, label=label, user_data=user_data, indent=indent, show=show, **kwargs)

def window(*, label: str =None, user_data: Any =None, width: int =0, height: int =0, show: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], min_size: Union[List[int], Tuple[int, ...]] =[100, 100], max_size: Union[List[int], Tuple[int, ...]] =[30000, 30000], menubar: bool =False, collapsed: bool =False, autosize: bool =False, no_resize: bool =False, unsaved_document: bool =False, no_title_bar: bool =False, no_move: bool =False, no_scrollbar: bool =False, no_collapse: bool =False, horizontal_scrollbar: bool =False, no_focus_on_appearing: bool =False, no_bring_to_front_on_focus: bool =False, no_close: bool =False, no_background: bool =False, modal: bool =False, popup: bool =False, no_saved_settings: bool =False, no_open_over_existing_popup: bool =True, no_scroll_with_mouse: bool =False, on_close: Callable =None, **kwargs) -> Union[int, str]:
    return dcg.Window(CONTEXT, parent=CONTEXT.viewport, label=label, user_data=user_data, width=width, height=height, show=show, pos=pos, min_size=min_size, max_size=max_size, menubar=menubar, collapsed=collapsed, autosize=autosize, no_resize=no_resize, unsaved_document=unsaved_document, no_title_bar=no_title_bar, no_move=no_move, no_scrollbar=no_scrollbar, no_collapse=no_collapse, horizontal_scrollbar=horizontal_scrollbar, no_focus_on_appearing=no_focus_on_appearing, no_bring_to_front_on_focus=no_bring_to_front_on_focus, has_close_button=not(no_close), no_background=no_background, modal=modal, popup=popup, no_saved_settings=no_saved_settings, no_open_over_existing_popup=no_open_over_existing_popup, no_scroll_with_mouse=no_scroll_with_mouse, on_close=wrap_callback(on_close), **kwargs)

def bind_item_handler_registry(item : Union[int, str], handler_registry : Union[int, str], **kwargs) -> None:
    CONTEXT.get(item).handlers = CONTEXT.get(handler_registry)

def bind_item_theme(item : Union[int, str], theme : Union[int, str], **kwargs) -> None:
    CONTEXT.get(item).theme = CONTEXT.get(theme)

def bind_theme(theme : Union[int, str], **kwargs) -> None:
    if isinstance(theme, int) and theme == 0:
        CONTEXT.viewport.theme = None
    else:
        CONTEXT.viewport.theme = CONTEXT.get(theme)

def create_context(**kwargs) -> None:
    global CONTEXT
    CONTEXT = DPGContext(**kwargs)
    return CONTEXT

def create_viewport(*, title: str ='Dear PyGui', small_icon: str ='', large_icon: str ='', width: int =1280, height: int =800, x_pos: int =100, y_pos: int =100, min_width: int =250, max_width: int =10000, min_height: int =250, max_height: int =10000, resizable: bool =True, vsync: bool =True, always_on_top: bool =False, decorated: bool =True, clear_color: Union[List[float], Tuple[float, ...]] =(0, 0, 0, 255), disable_close: bool =False, **kwargs) -> None:
    CONTEXT.viewport.configure(title=title, small_icon=small_icon, large_icon=large_icon, width=width, height=height, x_pos=x_pos, y_pos=y_pos, min_width=min_width, max_width=max_width, min_height=min_height, max_height=max_height, resizable=resizable, vsync=vsync, always_on_top=always_on_top, decorated=decorated, clear_color=clear_color, disable_close=disable_close, **kwargs)

def delete_item(item : Union[int, str], *, children_only: bool =False, slot: int =-1, **kwargs) -> None:
    if not(children_only):
        try:
            item = CONTEXT.get(item)
        except KeyError:
            return # already deleted
        item.delete_item()
    elif slot == -1:
        CONTEXT.get(item).children = []
    else:
        for child in filter_slot(CONTEXT.get(item).children, slot):
            child.delete_item()

def destroy_context(**kwargs) -> None:
    global CONTEXT

    CONTEXT = None

def does_alias_exist(alias : str, **kwargs) -> bool:
    try:
        item = CONTEXT.get(alias)
        return True
    except Exception:
        return False

def does_item_exist(item : Union[int, str], **kwargs) -> bool:
    try:
        item = CONTEXT.get(item)
        return True
    except Exception:
        return False

def draw_arrow(p1 : Union[List[float], Tuple[float, ...]], p2 : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, color: Union[int, List[int], Tuple[int, ...]] =-1, thickness: float =1.0, size: int =4, **kwargs) -> Union[int, str]:
    return dcg.DrawArrow(CONTEXT, p1=p1, p2=p2, label=label, user_data=user_data, show=show, color=color, thickness=thickness, size=size, **kwargs)

def draw_bezier_cubic(p1 : Union[List[float], Tuple[float, ...]], p2 : Union[List[float], Tuple[float, ...]], p3 : Union[List[float], Tuple[float, ...]], p4 : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, color: Union[int, List[int], Tuple[int, ...]] =-1, thickness: float =1.0, segments: int =0, **kwargs) -> Union[int, str]:
    return dcg.DrawBezierCubic(CONTEXT, p1=p1, p2=p2, p3=p3, p4=p4, label=label, user_data=user_data, show=show, color=color, thickness=thickness, segments=segments, **kwargs)

def draw_bezier_quadratic(p1 : Union[List[float], Tuple[float, ...]], p2 : Union[List[float], Tuple[float, ...]], p3 : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, color: Union[int, List[int], Tuple[int, ...]] =-1, thickness: float =1.0, segments: int =0, **kwargs) -> Union[int, str]:
    return dcg.DrawBezierQuadratic(CONTEXT, p1=p1, p2=p2, p3=p3, label=label, user_data=user_data, show=show, color=color, thickness=thickness, segments=segments, **kwargs)

def draw_circle(center : Union[List[float], Tuple[float, ...]], radius : float, *, label: str =None, user_data: Any =None, show: bool =True, color: Union[int, List[int], Tuple[int, ...]] =-1, fill: Union[int, List[int], Tuple[int, ...]] =0, thickness: float =1.0, segments: int =0, **kwargs) -> Union[int, str]:
    return dcg.DrawCircle(CONTEXT, center=center, radius=radius, label=label, user_data=user_data, show=show, color=color, fill=fill, thickness=thickness, segments=segments, **kwargs)

def draw_ellipse(pmin : Union[List[float], Tuple[float, ...]], pmax : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, color: Union[int, List[int], Tuple[int, ...]] =-1, fill: Union[int, List[int], Tuple[int, ...]] =0, thickness: float =1.0, segments: int =32, **kwargs) -> Union[int, str]:
    return dcg.DrawEllipse(CONTEXT, pmin=pmin, pmax=pmax, label=label, user_data=user_data, show=show, color=color, fill=fill, thickness=thickness, segments=segments, **kwargs)

def draw_image(texture_tag : Union[int, str], pmin : Union[List[float], Tuple[float, ...]], pmax : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, uv_min: Union[List[float], Tuple[float, ...]] =(0.0, 0.0), uv_max: Union[List[float], Tuple[float, ...]] =(1.0, 1.0), color: Union[int, List[int], Tuple[int, ...]] =-1, **kwargs) -> Union[int, str]:
    texture = CONTEXT.get(texture_tag)
    return dcg.DrawImage(CONTEXT, texture=CONTEXT.get(texture_tag), pmin=pmin, pmax=pmax, label=label, user_data=user_data, show=show, uv_min=uv_min, uv_max=uv_max, color_multiplier=color, **kwargs)

def draw_image_quad(texture_tag : Union[int, str], p1 : Union[List[float], Tuple[float, ...]], p2 : Union[List[float], Tuple[float, ...]], p3 : Union[List[float], Tuple[float, ...]], p4 : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, uv1: Union[List[float], Tuple[float, ...]] =(0.0, 0.0), uv2: Union[List[float], Tuple[float, ...]] =(1.0, 0.0), uv3: Union[List[float], Tuple[float, ...]] =(1.0, 1.0), uv4: Union[List[float], Tuple[float, ...]] =(0.0, 1.0), color: Union[int, List[int], Tuple[int, ...]] =-1, **kwargs) -> Union[int, str]:
    texture = CONTEXT.get(texture_tag)
    return dcg.DrawImage(CONTEXT, texture=CONTEXT.get(texture_tag), p1=p1, p2=p2, p3=p3, p4=p4, label=label, user_data=user_data, show=show, uv1=uv1, uv2=uv2, uv3=uv3, uv4=uv4, color_multiplier=color, **kwargs)

def draw_line(p1 : Union[List[float], Tuple[float, ...]], p2 : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, color: Union[int, List[int], Tuple[int, ...]] =-1, thickness: float =1.0, **kwargs) -> Union[int, str]:
    return dcg.DrawLine(CONTEXT, p1=p1, p2=p2, label=label, user_data=user_data, show=show, color=color, thickness=thickness, **kwargs)

def draw_polygon(points : List[List[float]], *, label: str =None, user_data: Any =None, show: bool =True, color: Union[int, List[int], Tuple[int, ...]] =-1, fill: Union[int, List[int], Tuple[int, ...]] =0, thickness: float =1.0, **kwargs) -> Union[int, str]:
    return dcg.DrawPolygon(CONTEXT, points=points, label=label, user_data=user_data, show=show, color=color, fill=fill, thickness=thickness, **kwargs)

def draw_polyline(points : List[List[float]], *, label: str =None, user_data: Any =None, show: bool =True, closed: bool =False, color: Union[int, List[int], Tuple[int, ...]] =-1, thickness: float =1.0, **kwargs) -> Union[int, str]:
    return dcg.DrawPolyline(CONTEXT, points=points, label=label, user_data=user_data, show=show, closed=closed, color=color, thickness=thickness, **kwargs)

def draw_quad(p1 : Union[List[float], Tuple[float, ...]], p2 : Union[List[float], Tuple[float, ...]], p3 : Union[List[float], Tuple[float, ...]], p4 : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, color: Union[int, List[int], Tuple[int, ...]] =-1, fill: Union[int, List[int], Tuple[int, ...]] =0, thickness: float =1.0, **kwargs) -> Union[int, str]:
    return dcg.DrawQuad(CONTEXT, p1=p1, p2=p2, p3=p3, p4=p4, label=label, user_data=user_data, show=show, color=color, fill=fill, thickness=thickness, **kwargs)

def draw_rectangle(pmin : Union[List[float], Tuple[float, ...]], pmax : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, color: Union[int, List[int], Tuple[int, ...]] =-1, fill: Union[int, List[int], Tuple[int, ...]] =0, multicolor: bool =False, rounding: float =0.0, thickness: float =1.0, corner_colors: Any =None, **kwargs) -> Union[int, str]:
    return dcg.DrawRect(CONTEXT, pmin=pmin, pmax=pmax, label=label, user_data=user_data, show=show, color=color, fill=fill, multicolor=multicolor, rounding=rounding, thickness=thickness, corner_colors=corner_colors, **kwargs)

def draw_text(pos : Union[List[float], Tuple[float, ...]], text : str, *, label: str =None, user_data: Any =None, show: bool =True, color: Union[int, List[int], Tuple[int, ...]] =-1, size: float =10.0, **kwargs) -> Union[int, str]:
    return dcg.DrawText(CONTEXT, pos=pos, text=text, label=label, user_data=user_data, show=show, color=color, size=size, **kwargs)

def draw_triangle(p1 : Union[List[float], Tuple[float, ...]], p2 : Union[List[float], Tuple[float, ...]], p3 : Union[List[float], Tuple[float, ...]], *, label: str =None, user_data: Any =None, show: bool =True, color: Union[int, List[int], Tuple[int, ...]] =-1, fill: Union[int, List[int], Tuple[int, ...]] =0, thickness: float =1.0, **kwargs) -> Union[int, str]:
    return dcg.DrawTriangle(CONTEXT, p1=p1, p2=p2, p3=p3, label=label, user_data=user_data, show=show, color=color, fill=fill, thickness=thickness, **kwargs)

def empty_container_stack(**kwargs) -> None:
    while CONTEXT.fetch_parent_queue_back() is not None:
        CONTEXT.pop_next_parent()

def fit_axis_data(axis : Union[int, str], **kwargs) -> None:
    return CONTEXT.get(axis).fit()

def focus_item(item : Union[int, str], **kwargs) -> None:
    CONTEXT.get(item).focused = True

def generate_uuid(**kwargs) -> Union[int, str]:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def get_alias_id(alias : str, **kwargs) -> Union[int, str]:
    return CONTEXT.get(alias).uuid

def get_aliases(**kwargs) -> Union[List[str], Tuple[str, ...]]:
    return list(CONTEXT.tag_to_uuid.keys())

def get_children_recursive(item):
    item = CONTEXT.get(item)
    result = [item]
    children = item.children
    result += children
    for c in children:
        result += get_children_recursive(c)
    return result

def get_all_items(**kwargs) -> Union[List[int], Tuple[int, ...]]:
    return get_children_recursive(CONTEXT.viewport)

def get_axis_limits(axis : Union[int, str], **kwargs) -> Union[List[float], Tuple[float, ...]]:
    item = CONTEXT.get(axis)
    return (item.min, item.max)

def get_clipboard_text(**kwargs) -> str:
    return CONTEXT.clipboard

def get_frame_count(**kwargs) -> int:
    return CONTEXT.viewport.metrics["frame_count"]

def get_item_alias(item : Union[int, str], **kwargs) -> str:
    return CONTEXT.get_item_tag(CONTEXT.get(item))

item_configuration_keys = set([
    "filter_key",
    "payload_type",
    "label",
    "use_internal_label",
    "source",
    "show",
    "enabled",
    "tracked",
    "width",
    "track_offset",
    "height",
    "indent",
    "callback",
    "drop_callback",
    "drag_callback",
    "user_data"
]) # + specific item keys

item_info_keys = set([
    "children",
    "type",
    "target",
    "parent",
    "theme",
    "handlers",
    "font",
    "container"
    "hover_handler_applicable",
    "active_handler_applicable",
    "focus_handler_applicable",
    "clicked_handler_applicable",
    "visible_handler_applicable",
    "edited_handler_applicable",
    "activated_handler_applicable",
    "deactivated_handler_applicable",
    "toggled_open_handler_applicable",
    "resized_handler_applicable"
])

item_state_keys = set([
    "ok",
    "pos",
    "hovered",
    "active",
    "focused",
    "clicked",
    "left_clicked",
    "right_clicked",
    "middle_clicked",
    "visible",
    "edited",
    "activated",
    "deactivated",
    "deactivated_after_edit",
    "toggled_open",
    "rect_min",
    "rect_max",
    "rect_size",
    "resized",
    "content_region_avail"
])

item_info_and_state_keys = item_info_keys.union(item_state_keys)

def get_item_configuration(item : Union[int, str], **kwargs) -> dict:
    item = CONTEXT.get(item)
    item_attributes = set(dir(item))
    configuration_attributes = item_attributes.difference(item_info_and_state_keys)
    if isinstance(item, dcg_base.baseTheme):
        # Theme uses attributes for its values
        # Keep only the generic ones
        configuration_attributes = configuration_attributes.intersection(item_configuration_keys)
    result = {}
    for attribute in configuration_attributes:
        try:
            result[attribute] = getattr(item, attribute)
        except AttributeError:
            # Some attributes are currently visible but unreachable
            pass
    if "callback_on_enter" in configuration_attributes:
        result["on_enter"] = getattr(item, "callback_on_enter")

    return result

def get_item_info(item : Union[int, str], **kwargs) -> dict:
    item = CONTEXT.get(item)
    result = {
        "children": item.children,
        "parent": item.parent
    }
    if hasattr(item, "theme"):
        result["theme"] = item.theme
    if hasattr(item, "handlers"):
        result["handlers"] = item.handlers
    if hasattr(item, "font"):
        result["font"] = item.font
    # Ignoring the other fields, which seem
    # mainly useful for debugging during developpement
    return result

def get_item_state(item : Union[int, str], **kwargs) -> dict:
    item = CONTEXT.get(item)
    result = {}
    keys = ["hovered", "active", "activated", "deactivated",
            "edited", "focused", "edited", "rect_size",
            "resized", "visible", "content_region_avail"]
    # These states are available as is.
    for key in keys:
        try:
            result[key] = item[key]
        except AttributeError:
            pass
    # These states are renamed
    keys = [("deactivated_after_edit", "deactivated_after_edited"),
            ("toggle_open", "toggled"),
            ("pos", "pos_to_window")]
    for (key_before, key_after) in keys:
        try:
            result[key_after] = item[key_before]
        except AttributeError:
            pass

    # These states completly changed
    try:
        result["clicked"] = max(item.clicked)
        result["left_clicked"] = item.clicked[0]
        result["right_clicked"] = item.clicked[1]
        result["middle_clicked"] = item.clicked[2]
    except AttributeError:
        pass

    result["ok"] = True
    if "visible" not in result:
        result["visible"] = True
    if "pos" not in result:
        result["pos"] = (0, 0)
    return result

def get_mouse_drag_delta(button=0, **kwargs) -> Tuple[float, float]:
    return CONTEXT.get_mouse_drag_delta(button, **kwargs)

def get_mouse_pos(*, local: bool =True, **kwargs) -> Union[List[int], Tuple[int, ...]]:
    return CONTEXT.get_mouse_position(**kwargs)

def get_value(item : Union[int, str], **kwargs) -> Any:
    return CONTEXT.get(item).value

def get_values(items : Union[List[int], Tuple[int, ...]], **kwargs) -> Any:
    return [CONTEXT.get(item).value for item in items]

def get_viewport_configuration(item : Union[int, str], **kwargs) -> dict:
    keys = ["clear_color", "small_icon", "larg_icon",
             "x_pos", "y_pos", "width", "height",
            "client_width", "client_height",
            "resizable", "vsync",
            "min_width", "max_width",
            "min_height", "max_height",
            "always_on_top", "decorated",
            "title", "disable_close"]
    result = {}
    viewport = CONTEXT.viewport
    for key in keys:
        result[key] = getattr(viewport, key)

    return result

def get_windows(**kwargs) -> Union[List[int], Tuple[int, ...]]:
    return [item for item in CONTEXT.viewport.children if isinstance(item, dcg_base.Window)]

def is_dearpygui_running(**kwargs) -> bool:
    return CONTEXT.running

def is_key_down(key : int, **kwargs) -> bool:
    return CONTEXT.is_key_down(dcg.Key(key), **kwargs)

def is_key_pressed(key : int, **kwargs) -> bool:
    return CONTEXT.is_key_pressed(dcg.Key(key), **kwargs)

def is_key_released(key : int, **kwargs) -> bool:
    return CONTEXT.is_key_released(dcg.Key(key), **kwargs)

def is_mouse_button_clicked(button : int, **kwargs) -> bool:
    return CONTEXT.is_mouse_clicked(button, *kwargs)

def is_mouse_button_double_clicked(button : int, **kwargs) -> bool:
    return CONTEXT.is_mouse_double_clicked(button, *kwargs)

def is_mouse_button_down(button : int, **kwargs) -> bool:
    return CONTEXT.is_mouse_down(button, **kwargs)

def is_mouse_button_dragging(button : int, threshold : float, **kwargs) -> bool:
    return CONTEXT.is_mouse_dragging(button, threshold, **kwargs)

def is_mouse_button_released(button : int, **kwargs) -> bool:
    return CONTEXT.is_mouse_released(button, **kwargs)

def is_viewport_ok(**kwargs) -> bool:
    try:
        return CONTEXT.viewport.shown
    except RuntimeError:
        return False

def last_container(**kwargs) -> Union[int, str]:
    return CONTEXT.fetch_last_created_container()

def last_item(**kwargs) -> Union[int, str]:
    return CONTEXT.fetch_last_created_item()

def last_root(**kwargs) -> Union[int, str]:
    item = CONTEXT.fetch_last_created_container()
    while item.parent is not CONTEXT.viewport:
        item = item.parent
    return item

def lock_mutex(**kwargs) -> None:
    return CONTEXT.viewport.lock_mutex(wait=True)

def maximize_viewport(**kwargs) -> None:
    CONTEXT.viewport.maximized = True

def minimize_viewport(**kwargs) -> None:
    CONTEXT.viewport.minimized = True

def move_item(item : Union[int, str], parent=None, before=None, **kwargs) -> None:
    item = CONTEXT.get(item)
    if before is not None:
        item.previous_sibling = before
    elif parent is not None:
        item.parent = parent
    else:
        raise ValueError("Neither parent nor before are set")

def move_item_down(item : Union[int, str], **kwargs) -> None:
    # The logic seems reverse
    next_sibling = item.next_sibling
    if next_sibling is not None:
        item.previous_sibling = next_sibling

def move_item_up(item : Union[int, str], **kwargs) -> None:
    # The logic seems reverse
    prev_sibling = item.previous_sibling
    if prev_sibling is not None:
        item.next_sibling = prev_sibling

def output_frame_buffer(file : str ='', *, callback: Callable =None, **kwargs) -> Any:
    CONTEXT.viewport.retrieve_framebuffer=True
    return FrameBufferCallback(CONTEXT, callback, **kwargs)

def pop_container_stack(**kwargs) -> Union[int, str]:
    return CONTEXT.pop_next_parent(**kwargs)

def push_container_stack(item : Union[int, str], **kwargs) -> bool:
    return CONTEXT.push_next_parent(item)

def remove_alias(alias : str, **kwargs) -> None:
    CONTEXT.get(alias).configure(tag = None)

def render_dearpygui_frame(**kwargs) -> None:
    return CONTEXT.viewport.render_frame()

def reorder_items(container : Union[int, str], slot : int, new_order : Union[List[int], Tuple[int, ...]], **kwargs) -> None:
    container = CONTEXT.get(container)
    for item in new_order:
        item.parent = container

def reset_axis_limits_constraints(axis : Union[int, str], **kwargs) -> None:
    item = CONTEXT.get(axis)
    item.constraint_min = -math.inf
    item.constraint_max = math.inf

def reset_axis_ticks(axis : Union[int, str], **kwargs) -> None:
    CONTEXT.get(axis).labels = None

def reset_axis_zoom_constraints(axis : Union[int, str], **kwargs) -> None:
    item = CONTEXT.get(axis)
    item.zoom_min = 0.
    item.zoom_max = math.inf

def reset_pos(item : Union[int, str], **kwargs) -> None:
    CONTEXT.get(item).pos_to_default = (0, 0)

def set_axis_limits(axis : Union[int, str], ymin : float, ymax : float, **kwargs) -> None:
    item = CONTEXT.get(axis)
    item.min = ymin
    item.max = ymax
    item.lock_min = True
    item.lock_max = True

def set_axis_limits_auto(axis : Union[int, str], **kwargs) -> None:
    item = CONTEXT.get(axis)
    item.lock_min = False
    item.lock_max = False

def set_axis_limits_constraints(axis : Union[int, str], vmin : float, vmax : float, **kwargs) -> None:
    item = CONTEXT.get(axis)
    item.constraint_min = vmin
    item.constraint_max = vmax

def set_axis_ticks(axis : Union[int, str], label_pairs : Any, **kwargs) -> None:
    labels = []
    coords = []
    for (label, coord) in label_pairs:
        labels.append(label)
        coords.append(coord)

    item = CONTEXT.get(axis)
    item.labels = labels
    item.labels_coord = coords

def set_axis_zoom_constraints(axis : Union[int, str], vmin : float, vmax : float, **kwargs) -> None:
    item = CONTEXT.get(axis)
    item.zoom_min = vmin
    item.zoom_max = vmax

def set_clip_space(item : Union[int, str], top_left_x : float, top_left_y : float, width : float, height : float, min_depth : float, max_depth : float, **kwargs) -> None:
    return CONTEXT.get(item).clip_space(top_left_x, top_left_y, width, height, min_depth, max_depth, **kwargs)

def set_clipboard_text(text : str, **kwargs) -> None:
    CONTEXT.clipboard = text

def set_frame_callback(frame : int, callback : Callable, *, user_data: Any =None, **kwargs) -> str:
    return FrameCallback(CONTEXT, frame, callback, user_data=user_data, **kwargs)

def set_item_alias(item : Union[int, str], alias : str, **kwargs) -> None:
    CONTEXT.get(item).configure(tag=alias)

def set_item_children(item : Union[int, str], source : Union[int, str], slot : int, **kwargs) -> None:
    source = CONTEXT.get(source)
    item = CONTEXT.get(item)
    for child in source.children:
        child.parent = item

def set_primary_window(window : Union[int, str], value : bool, **kwargs) -> None:
    CONTEXT.get(window).primary = value

def set_value(item : Union[int, str], value : Any, **kwargs) -> None:
    item = CONTEXT.get(item)
    if isinstance(item, dcg_base.Texture):
        item.set_value(value)
    else:
        item.value = value

def set_viewport_resize_callback(callback : Callable, *, user_data: Any =None, **kwargs) -> str:
    CONTEXT.viewport.resize_callback = (callback, user_data)

def setup_dearpygui(**kwargs) -> None:
    CONTEXT.running = True

def show_viewport(*, minimized: bool =False, maximized: bool =False, **kwargs) -> None:
    CONTEXT.viewport.initialize(minimized=minimized, maximized=maximized)

def stop_dearpygui(**kwargs) -> None:
    CONTEXT.running = False

def toggle_viewport_fullscreen(**kwargs) -> None:
    CONTEXT.viewport.fullscreen = True

def unlock_mutex(**kwargs) -> None:
    return CONTEXT.viewport.unlock_mutex()

def unstage(item : Union[int, str], **kwargs) -> None:
    item = CONTEXT.get(item)
    assert(isinstance(item, dcg_base.PlaceHolderParent))
    # Ideally we'd lock the target parent mutex rather
    # than the viewport. The locking is to force the unstage
    # to be atomic (all done in one frame).
    with mutex():
        for child in item.children:
            child.configure(**kwargs)
    item.delete_item()


"""
Most features below have a direct DCG equivalent
or a indirect way of getting the same thing, except
a few exceptions.

The reasons they are not implemented is mainly the lack
of interest for this wrapper.

"""

def not_implemented_feature(*args, **kwargs):
    """ Not implemented feature """
    raise NotImplementedError("Not implemented")

show_style_editor = not_implemented_feature
show_metrics = not_implemented_feature
show_about = not_implemented_feature
show_debug = not_implemented_feature
show_documentation = not_implemented_feature
show_font_manager = not_implemented_feature
show_item_registry = not_implemented_feature
get_item_disabled_theme = not_implemented_feature
set_item_track_offset = not_implemented_feature
set_item_payload_type = not_implemented_feature
set_item_drag_callback = not_implemented_feature
set_item_drop_callback = not_implemented_feature
track_item = not_implemented_feature
untrack_item = not_implemented_feature
get_item_filter_key = not_implemented_feature
is_item_tracked = not_implemented_feature
get_item_track_offset = not_implemented_feature
get_item_drag_callback = not_implemented_feature
get_item_drop_callback = not_implemented_feature
is_item_toggled_open = not_implemented_feature
add_3d_slider = not_implemented_feature
area_series = not_implemented_feature
axis_tag = not_implemented_feature
bar_group_series = not_implemented_feature
candle_series = not_implemented_feature
char_remap = not_implemented_feature
clipper = not_implemented_feature
colormap = not_implemented_feature
colormap_button = not_implemented_feature
colormap_registry = not_implemented_feature
colormap_scale = not_implemented_feature
colormap_slider = not_implemented_feature
custom_series = not_implemented_feature
date_picker = not_implemented_feature
digital_series = not_implemented_feature
drag_line = not_implemented_feature
drag_payload = not_implemented_feature
drag_point = not_implemented_feature
drag_rect = not_implemented_feature
draw_layer = not_implemented_feature
draw_node = not_implemented_feature
error_series = not_implemented_feature
file_dialog = not_implemented_feature
file_extension = not_implemented_feature
filter_set = not_implemented_feature
font = not_implemented_feature
font_chars = not_implemented_feature
font_range = not_implemented_feature
font_range_hint = not_implemented_feature
font_registry = not_implemented_feature
heat_series = not_implemented_feature
histogram_series = not_implemented_feature
knob_float = not_implemented_feature
loading_indicator = not_implemented_feature
node = not_implemented_feature
node_attribute = not_implemented_feature
node_editor = not_implemented_feature
node_link = not_implemented_feature
pie_series = not_implemented_feature
plot_annotation = not_implemented_feature
series_value = not_implemented_feature
template_registry = not_implemented_feature
text_point = not_implemented_feature
theme_component = not_implemented_feature
time_picker = not_implemented_feature
apply_transform = not_implemented_feature
bind_colormap = not_implemented_feature
bind_item_font = not_implemented_feature
capture_next_item = not_implemented_feature
clear_selected_links = not_implemented_feature
clear_selected_nodes = not_implemented_feature
create_fps_matrix = not_implemented_feature
create_lookat_matrix = not_implemented_feature
create_orthographic_matrix = not_implemented_feature
create_perspective_matrix = not_implemented_feature
create_rotation_matrix = not_implemented_feature
create_scale_matrix = not_implemented_feature
create_translation_matrix = not_implemented_feature
get_active_window = not_implemented_feature
get_app_configuration = not_implemented_feature
get_callback_queue = not_implemented_feature
get_colormap_color = not_implemented_feature
get_delta_time = not_implemented_feature
get_drawing_mouse_pos = not_implemented_feature
get_file_dialog_info = not_implemented_feature
get_focused_item = not_implemented_feature
get_frame_count = not_implemented_feature
get_global_font_scale = not_implemented_feature
get_item_types = not_implemented_feature
get_platform = not_implemented_feature
get_plot_mouse_pos = not_implemented_feature
get_plot_query_rects = not_implemented_feature
get_selected_links = not_implemented_feature
get_selected_nodes = not_implemented_feature
get_text_size = not_implemented_feature
get_total_time = not_implemented_feature
get_x_scroll = not_implemented_feature
get_x_scroll_max = not_implemented_feature
get_y_scroll = not_implemented_feature
get_y_scroll_max = not_implemented_feature
highlight_table_cell = not_implemented_feature
highlight_table_column = not_implemented_feature
highlight_table_row = not_implemented_feature
is_table_cell_highlighted = not_implemented_feature
is_table_column_highlighted = not_implemented_feature
is_table_row_highlighted = not_implemented_feature
load_image = not_implemented_feature
sample_colormap = not_implemented_feature
save_image = not_implemented_feature
save_init_file = not_implemented_feature
set_exit_callback = not_implemented_feature
set_global_font_scale = not_implemented_feature
set_table_row_color = not_implemented_feature
set_x_scroll = not_implemented_feature
set_y_scroll = not_implemented_feature
show_imgui_demo = not_implemented_feature
show_implot_demo = not_implemented_feature
show_item_debug = not_implemented_feature
show_tool = not_implemented_feature
split_frame = not_implemented_feature
top_container_stack = not_implemented_feature
unhighlight_table_cell = not_implemented_feature
unhighlight_table_column = not_implemented_feature
unhighlight_table_row = not_implemented_feature
unset_table_row_color = not_implemented_feature

# Accept both with and without add_

add_bar_series = bar_series
add_button = button
add_checkbox = checkbox
add_child_window = child_window
add_clipper = clipper
add_color_button = color_button
add_color_edit = color_edit
add_color_picker = color_picker
add_color_value = color_value
add_colormap = colormap
add_colormap_button = colormap_button
add_colormap_scale = colormap_scale
add_colormap_slider = colormap_slider
add_collapsing_header = collapsing_header
add_colormap_registry = colormap_registry
add_combo = combo
add_custom_series = custom_series
add_date_picker = date_picker
add_digital_series = digital_series
add_double4_value = double4_value
add_double_value = double_value
add_drag_double = drag_double
add_drag_doublex = drag_doublex
add_drag_float = drag_float
add_drag_floatx = drag_floatx
add_drag_int = drag_int
add_drag_intx = drag_intx
add_drag_line = drag_line
add_drag_payload = drag_payload
add_drag_point = drag_point
add_drag_rect = drag_rect
add_draw_layer = draw_layer
add_draw_node = draw_node
add_drawlist = drawlist
add_dynamic_texture = dynamic_texture
add_error_series = error_series
add_file_dialog = file_dialog
add_file_extension = file_extension
add_filter_set = filter_set
add_float4_value = float4_value
add_float_value = float_value
add_float_vect_value = float_vect_value
add_font = font
add_font_chars = font_chars
add_font_range = font_range
add_font_range_hint = font_range_hint
add_font_registry = font_registry
add_group = group
add_handler_registry = handler_registry
add_heat_series = heat_series
add_histogram_series = histogram_series
add_image = image
add_image_button = image_button
add_image_series = image_series
add_inf_line_series = inf_line_series
add_input_double = input_double
add_input_doublex = input_doublex
add_input_float = input_float
add_input_floatx = input_floatx
add_input_int = input_int
add_input_intx = input_intx
add_input_text = input_text
add_int4_value = int4_value
add_int_value = int_value
add_item_activated_handler = item_activated_handler
add_item_active_handler = item_active_handler
add_item_clicked_handler = item_clicked_handler
add_item_deactivated_after_edit_handler = item_deactivated_after_edit_handler
add_item_deactivated_handler = item_deactivated_handler
add_item_double_clicked_handler = item_double_clicked_handler
add_item_edited_handler = item_edited_handler
add_item_focus_handler = item_focus_handler
add_item_handler_registry = item_handler_registry
add_item_hover_handler = item_hover_handler
add_item_resize_handler = item_resize_handler
add_item_toggled_open_handler = item_toggled_open_handler
add_item_visible_handler = item_visible_handler
add_key_down_handler = key_down_handler
add_key_press_handler = key_press_handler
add_key_release_handler = key_release_handler
add_knob_float = knob_float
add_line_series = line_series
add_listbox = listbox
add_loading_indicator = loading_indicator
add_menu = menu
add_menu_bar = menu_bar
add_menu_item = menu_item
add_mouse_click_handler = mouse_click_handler
add_mouse_double_click_handler = mouse_double_click_handler
add_mouse_down_handler = mouse_down_handler
add_mouse_drag_handler = mouse_drag_handler
add_mouse_move_handler = mouse_move_handler
add_mouse_release_handler = mouse_release_handler
add_mouse_wheel_handler = mouse_wheel_handler
add_node = node
add_node_attribute = node_attribute
add_node_editor = node_editor
add_node_link = node_link
add_pie_series = pie_series
add_plot = plot
add_plot_annotation = plot_annotation
add_plot_axis = plot_axis
add_plot_legend = plot_legend
add_progress_bar = progress_bar
add_radio_button = radio_button
add_raw_texture = raw_texture
add_scatter_series = scatter_series
add_selectable = selectable
add_separator = separator
add_series_value = series_value
add_shade_series = shade_series
add_simple_plot = simple_plot
add_slider_double = slider_double
add_slider_doublex = slider_doublex
add_slider_float = slider_float
add_slider_floatx = slider_floatx
add_slider_int = slider_int
add_slider_intx = slider_intx
add_spacer = spacer
add_stage = stage
add_stair_series = stair_series
add_static_texture = static_texture
add_string_value = string_value
add_stem_series = stem_series
add_subplots = subplots
add_tab = tab
add_tab_bar = tab_bar
add_tab_button = tab_button
add_table = table
add_table_cell = table_cell
add_table_column = table_column
add_table_row = table_row
add_template_registry = template_registry
add_text = text
add_text_point = text_point
add_texture_registry = texture_registry
add_theme = theme
add_theme_color = theme_color
add_theme_component = theme_component
add_theme_style = theme_style
add_time_picker = time_picker
add_tooltip = tooltip
add_tree_node = tree_node
add_value_registry = value_registry
add_viewport_drawlist = viewport_drawlist
add_viewport_menu_bar = viewport_menu_bar
add_window = window