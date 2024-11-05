# Set up themes
import dearcygui as dcg
from config import C

with dcg.ThemeList(C) as global_theme:  # Sets up the default theme
    # Styles
    dcg.ThemeStyleImGui(C,
                        WindowPadding=(4, 4),
                        FramePadding=(8, 8),
                        ItemSpacing=(4, 4),
                        ChildRounding=4,
                        FrameRounding=4,
                        ChildBorderSize=0
                        )
    # Colors
    dcg.ThemeColorImGui(C,
                        WindowBg=(0, 0, 0),
                        FrameBg=(0, 0, 0),
                        PopupBg=(0, 0, 0),
                        ChildBg=(0, 0, 0),
                        MenuBarBg=(48, 48, 48),
                        Text=(168, 168, 168),
                        Button=(0, 0, 0),
                        ButtonHovered=(33, 33, 33),
                        ButtonActive=(33, 33, 33)
                        )
    dcg.ThemeColorImPlot(C,
                         PlotBg=(0, 0, 0),
                         AxisGrid=(30, 30, 255),
                         Line=(0, 0, 255),
                         FrameBg=(0, 0, 0),
                         PlotBorder=(30, 30, 255)
                         )

with dcg.ThemeList(C) as dummy_button_theme:
    dcg.ThemeColorImGui(C,
                        Button=(0, 0, 0),
                        ButtonHovered=(0, 0, 0),
                        ButtonActive=(0, 0, 0))

with dcg.ThemeList(C) as play_button_theme:
    dcg.ThemeColorImGui(C,
                        Text=(161, 94, 33))

with dcg.ThemeList(C) as no_border_board_theme:
    dcg.ThemeColorImPlot(C,
                        PlotBorder=(0, 0, 0))

sharp_lines_theme = dcg.ThemeStyleImPlot(C, LineWeight=0.9, no_scaling=True)
