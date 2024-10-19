# All settings required for tetris blocks (aka tetrominos)
import time
import threading
import imageio
import math
import random
from playsound import playsound
import pandas as pd
import os
import config
from theme_settings import *
from config import *
import tetrominos_handler

current_block_lock = threading.Lock()

for block in block_names:
    # Extract data from images and add static textures for each cell of a block
    data = imageio.imread(f"textures/{block}-block.jpg")
    texture = dcg.Texture(C, data, tag=f"{block}_block")
    textures.append(texture)

def audio_effectsDispatcher(file_name):
    # Function creates a new thread that runs the audio file so that the main code does not lag or interfere
    play_audio_thread = threading.Thread(name="play audio", target=play_audio_effect, args=(file_name,), daemon=True)
    play_audio_thread.start()


def play_audio_effect(file_name):
    playsound(os.path.join(os.path.join(os.path.abspath(os.path.abspath("tetris_game.py")[:-14]), "sounds"), file_name))


def create_blocksDispatcher():
    # Function creates a new thread that controls the continuous movement of the new blocks
    C.viewport.handlers += [
        dcg.KeyPressHandler(C, callback=tetrominos_handler.key_press_handler)
    ]
    C["play_button"].enabled = False
    C["play_button"].theme = play_button_theme

    create_blocks_thread = threading.Thread(name="create blocks", target=create_blocks, args=(), daemon=True)
    create_blocks_thread.start()


def create_blocks():
    # Play audio effect to indicate selection
    tetrominos_handler.audio_effectsDispatcher("selection.wav")

    # Set up the speed for level chosen by the user
    # CSV file contains speed to reach the bottom of the board, i.e. to cross 20 cells. Divide the speed by 20 to get
    # time per each cell
    block_speeds_data = pd.read_csv("block_speeds_data.csv")
    config.speed = (block_speeds_data.values[config.level][1]) / 20

    random_blocks = [random.randint(0, 6), random.randint(0, 6)]

    config.current_block = \
        tetrominos_handler.Block(C,
                                 block_names[random_blocks[0]]+'_block',
                                 parent=C["tetris_board"])

    C["next_block_board"].children = [
        tetrominos_handler.BlockDrawing(C,
                                        block_names[random_blocks[1]]+'_block', (3, 2))
    ]

    C.viewport.wake() # Trigger draw (wait_for_input)
    time.sleep(config.speed)

    # If any of the blocks occupy these cells, then the game ends
    top_cells = [(3, 19), (4, 19), (5, 19), (6, 19), (3, 18), (4, 18), (5, 18), (6, 18)]

    while True:
        # No active block
        if config.current_block is None:
            # We don't need the lock as we are the only thread
            # that can update current_block from None

            # Check if top cells are occupied
            if len(config.cells_occupied.intersection(top_cells)) > 0:
                break

            random_blocks.pop(0)
            random_blocks.append(random.randint(0, 6))
            check_complete_line()
            config.current_block = \
                tetrominos_handler.Block(C,
                                         block_names[random_blocks[0]]+'_block',
                                         parent=C["tetris_board"])

            C["next_block_board"].children = [
                tetrominos_handler.BlockDrawing(C, block_names[random_blocks[1]]+'_block', (3, 2))
            ]
            C.viewport.wake() # Trigger draw (wait_for_input)
            time.sleep(config.speed)
            continue
        # Active block
        # The lock is to prevent current block getting None between the initial check and now
        current_block_lock.acquire(blocking=True)
        if config.current_block is not None:
            # Move down
            config.current_block.move_block_down()
        current_block_lock.release()
        C.viewport.wake() # Trigger draw (wait_for_input)
        time.sleep(config.speed)

    # Fade the board by placing a semi-transparent rectangle
    dcg.DrawRect(C, pmin=[0,0], pmax=[10, 20], color=[0, 0, 0, 150], thickness=0,
                 fill=[0, 0, 0, 150], parent=C["tetris_board"])

    # Show GAME OVER text on the board
    dcg.DrawText(C, pos=[0.5, 11], text="GAME OVER", size=1, parent=C["tetris_board"])

    # Play the game over tune
    audio_effectsDispatcher("gameover.wav")

    C.viewport.wake() # Trigger draw (wait_for_input)


def check_complete_line():
    # Function checks every horizontal line to see if a complete row has been filled. If so, the line disappears

    row = 0
    lines_completed = 0  # Total lines completed together (max 4 using I block)

    while row < 20:
        cell_count = 0  # Count the number of cells occupied in the given row. If equals 10, then line is complete
        for point in config.cells_occupied:
            if point[1] == row:
                cell_count += 1

        if cell_count == 10:
            # Increase complete lines in one-go
            lines_completed += 1
            # Increase full lines text display
            config.full_lines += 1
            C["full_line_text"].value = str(config.full_lines)

            # Check if level up is needed using the number of full lines completed
            if min((config.level*10 + 10), 100) == config.full_lines:
                config.level += 1
                C["level_text"].value = str(config.level)

                # Speed up to match the speed for the corresponding level
                block_speeds_data = pd.read_csv("block_speeds_data.csv")
                config.speed = (block_speeds_data.values[config.level][1]) / 20

                # Play audio effect
                audio_effectsDispatcher("success.wav")

            to_delete = []
            for (pos, block) in config.dead_blocks.items():
                if pos[1] == row:
                    block.delete_item()
                    to_delete.append(pos)
            for pos in to_delete:
                del config.dead_blocks[pos]

            audio_effectsDispatcher("line.wav")

            C.viewport.wake() # Trigger draw (wait_for_input)
            time.sleep(0.1)
            new_dead_blocks = {}
            config.cells_occupied = set()

            for (pos, block) in config.dead_blocks.items():
                if pos[1] > row:
                    pos = (pos[0], pos[1]-1)
                    block.pos = pos
                config.cells_occupied.add(pos)
                new_dead_blocks[pos] = block
            config.dead_blocks = new_dead_blocks
            C.viewport.wake() # Trigger draw (wait_for_input)
            time.sleep(0.1)
        else:
            row += 1

    if lines_completed == 1:
        config.score += 40*(config.level + 1)

    elif lines_completed == 2:
        config.score += 100*(config.level + 1)

    elif lines_completed == 3:
        config.score += 300*(config.level + 1)

    elif lines_completed == 4:
        config.score += 1200*(config.level + 1)

    C["score_text"].value = str(config.score)


def key_press_handler(sender, target, key):
    current_block_lock.acquire(blocking=True)
    if config.current_block is not None:
        if key == dcg.constants.mvKey_Up:
            config.current_block.try_rotate()
        elif key == dcg.constants.mvKey_Left:
            config.current_block.try_left()
        elif key == dcg.constants.mvKey_Right:
            config.current_block.try_right()
        elif key == dcg.constants.mvKey_Down:
            if config.current_block.move_block_down():
                config.score += 1
                C["score_text"].value = str(config.score)
                audio_effectsDispatcher("fall.wav")
        elif key == dcg.constants.mvKey_Spacebar:
            # Hard drop block
            cells_dropped = 0  # Count of number of cells the block dropped. Used to calculate the score

            while config.current_block.move_block_down():
                cells_dropped += 1

            # Update the score accordingly
            config.score += cells_dropped*2
            C["score_text"].value = str(config.score)

            if cells_dropped >= 1:
                audio_effectsDispatcher("fall.wav")
    current_block_lock.release()
    C.viewport.wake() # Trigger draw (wait_for_input)

