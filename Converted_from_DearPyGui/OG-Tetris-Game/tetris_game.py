import dearcygui as dcg
import imageio

import time
from theme_settings import *
from config import *
import config
import tetrominos_handler
import threading

C = config.C
# Configure viewport
C.viewport.initialize(title="Tetris Game",
                      x_pos=0,
                      y_pos=0,
                      width=1000,
                      height=790,
                      max_height=790,
                      max_width=1000,
                      min_width=100,
                      wait_for_input=True)

def set_main_window(sender, target, value):
    config.level = value
    # Function sets up the displays of the main game window

    # Play audio for selection made
    tetrominos_handler.audio_effectsDispatcher("selection.wav")

    # Main window config
    with dcg.Window(C,
                   pos=[0, 0],
                   autosize=True,
                   no_collapse=True,
                   no_resize=True,
                   has_close_button=False,
                   no_move=True,
                   primary=True,
                   no_scrollbar=True,
                   no_scroll_with_mouse=True,
                   no_title_bar=True):
        with dcg.HorizontalLayout(C):
            # Score board and help window config
            with dcg.ChildWindow(C, width=320, no_scrollbar=True, no_scroll_with_mouse=True):
                dcg.Spacer(C, height=10)

                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value=" Your level : ")
                    dcg.Text(C, value=str(config.level), tag="level_text")

                dcg.Spacer(C)

                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value=" Full lines : ")
                    dcg.Text(C, value="0", tag="full_line_text")

                dcg.Spacer(C, height=10)

                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value=" SCORE : ")
                    dcg.Text(C, value="0", color=(161, 94, 33), tag="score_text")

                dcg.Spacer(C, height=50)

                dcg.Button(C, label="H E L P",
                           width=-1,
                           theme=dummy_button_theme)

                dcg.Spacer(C, height=20)
                dcg.Text(C, value=" LEFT KEY  : Left")
                dcg.Text(C, value=" RIGHT KEY : Right")
                dcg.Text(C, value=" UP KEY    : Rotate")
                dcg.Text(C, value=" DOWN KEY  : Speed up")
                dcg.Text(C, value=" SPACE     : Drop")

                dcg.Spacer(C, height=50)
                dcg.Button(C, label="Next :", width=-1,
                           theme=dummy_button_theme)

                next_block_board = dcg.Plot(C,
                              no_menus=False, no_title=True,
                              no_mouse_pos=True, width=315,
                              height=160, equal_aspects=True,
                              theme=no_border_board_theme)

                next_block_board.X1.configure(no_gridlines=True,
                                              no_tick_marks=True,
                                              no_tick_labels=True,
                                              no_highlight=True,
                                              no_side_switch=True,
                                              lock_min=True,
                                              lock_max=True,
                                              min=0, max=8)
                next_block_board.Y1.configure(no_gridlines=True,
                                              no_tick_marks=True,
                                              no_tick_labels=True,
                                              no_highlight=True,
                                              no_side_switch=True,
                                              lock_min=True,
                                              lock_max=True,
                                              min=0, max=4)
                dcg.DrawInPlot(C, tag="next_block_board", parent=next_block_board)

            # Tetris board window config
            with dcg.VerticalLayout(C):
                with dcg.Plot(C, no_menus=False, no_title=True,
                              no_mouse_pos=True, width=325,
                              height=650, equal_aspects=True) as tetris_board:
                    tetris_board.X1.configure(no_gridlines=True,
                                              no_tick_marks=True,
                                              no_tick_labels=True,
                                              no_highlight=True,
                                              no_side_switch=True,
                                              lock_min=True,
                                              lock_max=True,
                                              min=0, max=10)
                    tetris_board.Y1.configure(no_gridlines=True,
                                              no_tick_marks=True,
                                              no_tick_labels=True,
                                              no_highlight=True,
                                              no_side_switch=True,
                                              lock_min=True,
                                              lock_max=True,
                                              min=0, max=20)
                    dcg.PlotInfLines(C, X=[n for n in range(10)], theme=sharp_lines_theme)
                    dcg.PlotInfLines(C, X=[n for n in range(120)], horizontal=True, theme=sharp_lines_theme)
                    dcg.DrawInPlot(C, tag="tetris_board")

                dcg.Button(C, label="Play TETRIS !",
                           width=325,
                           callback=tetrominos_handler.create_blocksDispatcher,
                           tag="play_button",
                           font=play_font,
                           theme=play_button_theme)

            # Statistics window config
            with dcg.ChildWindow(C, no_scrollbar=True, no_scroll_with_mouse=True):
                dcg.Spacer(C, height=10)

                dcg.Button(C, label="STATISTICS", width=-1, theme=dummy_button_theme)
                with dcg.Plot(C, no_menus=False, no_title=True,
                              no_mouse_pos=True, width=315,
                              height=560, equal_aspects=True,
                              theme=no_border_board_theme,
                              tag="statistics_window") as statistics_window:

                    statistics_window.X1.configure(no_gridlines=True,
                                                   no_tick_marks=True,
                                                   no_tick_labels=True,
                                                   lock_min=True,
                                                   lock_max=True,
                                                   no_highlight=True,
                                                   no_side_switch=True,
                                                   min=0, max=10)
                    statistics_window.Y1.configure(no_gridlines=True,
                                                   no_tick_marks=True,
                                                   no_tick_labels=True,
                                                   no_highlight=True,
                                                   no_side_switch=True,
                                                   lock_min=True,
                                                   lock_max=True,
                                                   min=0, max=19)
                    with dcg.DrawInPlot(C):
                        tetrominos_handler.BlockStatistics(C)

                dcg.Button(C, label="-------------------", width=-1, theme=dummy_button_theme)

                with dcg.HorizontalLayout(C):
                    dcg.Text(C, value=" Total")
                    dcg.Spacer(C, width=160)
                    dcg.Text(C, value="0", tag="Total_block_stat")

    enter_level_screen.parent = None
    C.viewport.wake()


def press_any_key_to_start():
    # Function continues to show enter level screen when any key is pressed
    # Play audio effect to indicate selection
    tetrominos_handler.audio_effectsDispatcher("selection.wav")

    # Continue with setting up enter level screen
    welcome_screen.parent = None
    enter_level_screen.show = True
    enter_level_screen.primary = True
    C.viewport.wake()


# Welcome screen config
with dcg.Window(C, modal=True, autosize=True, no_collapse=True,
                no_resize=True, has_close_button=False, no_move=True,
                no_title_bar=True, no_scrollbar=True, no_scroll_with_mouse=True) as welcome_screen:
    data = imageio.imread("textures/welcome_screen.jpg")
    dcg.Image(C, texture=dcg.Texture(C, data))
welcome_screen.handlers = [
    dcg.KeyReleaseHandler(C, callback=press_any_key_to_start),
    dcg.MouseReleaseHandler(C, callback=press_any_key_to_start)
]


# Enter level screen config
with dcg.Window(C, autosize=True, no_collapse=True, no_resize=True,
                has_close_button=False, no_move=True, no_scrollbar=True,
                no_scroll_with_mouse=True, no_title_bar=True, show=False) as enter_level_screen:
    dcg.Spacer(C, height=350)

    with dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.CENTER):
        dcg.Text(C, value="Enter your level (0-9) > ")
        dcg.InputValue(C, format="int", label="", step=0, min_value=0,
                           max_value=9, width=100, on_enter=True,
                           callback=set_main_window)



def background_theme():
    # Function starts a new thread to play the background theme
    play_theme_thread = threading.Thread(name="play theme", target=theme_audio, args=(), daemon=True)
    play_theme_thread.start()


def theme_audio():
    # Function loops the background theme
    while True:
        tetrominos_handler.audio_effectsDispatcher("theme.mp3")
        time.sleep(84)

C.viewport.theme = global_theme
C.viewport.font = regular_font

# Initiates the theme playback
background_theme()

welcome_screen.primary = True
while C.running:
    #C.viewport.scale = 1./C.viewport.dpi
    C.viewport.render_frame()
