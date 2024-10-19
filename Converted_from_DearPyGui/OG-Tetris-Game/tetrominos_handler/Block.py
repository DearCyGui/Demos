import dearcygui as dcg
import math
import time
import threading
import config
from config import *

def get_distance_between_points(point1: list, point2: list):
    # Calculates the distance between two points
    return math.sqrt(math.pow((point2[0] - point1[0]), 2) + math.pow((point2[1] - point1[1]), 2))

# Add pos to DrawImage to control block position more easily
class BlockPiece(dcg.DrawImage):
    def __init__(self, context, **kwargs):
        super().__init__(context, **kwargs)

    @property
    def pos(self):
        return (self.pmin[0], self.pmax[1])

    @pos.setter
    def pos(self, value):
        self.pmin = (value[0], value[1]+1)
        self.pmax = (value[0]+1, value[1])

class BlockDrawing(dcg.DrawingList):
    def __init__(self, context, name, start_pos, **kwargs):
        super().__init__(context, **kwargs)

        shape = {
            "I_block": [(0, 0), (1, 0),  (2, 0),  (3, 0) ],
            "J_block": [(0, 0), (0, -1), (1, -1), (2, -1)],
            "L_block": [(2, 0), (0, -1), (1, -1), (2, -1)],
            "O_block": [(1, 0), (2, 0),  (1, -1), (2, -1)],
            "S_block": [(1, 0), (2, 0),  (0, -1), (1, -1)],
            "T_block": [(1, 0), (0, -1), (1, -1), (2, -1)],
            "Z_block": [(0, 0), (1, -1), (1, 0), (2, -1)]
        }
        self.name = name
        self.positions = []

        texture=context[name]

        for pos_delta in shape[name]:
            pos = (start_pos[0] + pos_delta[0],
                   start_pos[1] + pos_delta[1])
            self.positions.append(pos)

            # Draw the cell
            BlockPiece(context,
                       texture=texture,
                       pos=pos,
                       parent=self)

    def preview_shift(self, dx, dy):
        """Returns the list of updated positions if the block were shifted"""
        new_positions = []
        for p in self.positions:
            new_positions.append((p[0]+dx, p[1]+dy))
        return new_positions

    def preview_rotation(self):
        """Returns the list of updated positions if the block were rotated 90 degrees clockwise"""
        if self.name == "O_block":
            # No rotation for O_block
            return self.positions
        rotation_point = self.positions[1]
        new_positions = []
        for p in self.positions:
            radius = get_distance_between_points(p, rotation_point)
            # Shift the origin to the rotation point and calculate the angle of points
            x = p[0] - rotation_point[0]
            y = p[1] - rotation_point[1]
            if p[1] - rotation_point[1] >= 0:
                # If the point is above the rotation point
                angle_of_rotation = math.degrees(math.atan2(y, -x))
            else:
                # If the point is below the rotation point
                angle_of_rotation = 180 - math.degrees(math.atan2(y, x))
            # Apply the rotation
            x = round(radius*math.sin(math.radians(angle_of_rotation)))
            y = round(radius*math.cos(math.radians(angle_of_rotation)))
            # map to the original coordinates
            new_positions.append((rotation_point[0] + x,
                                  rotation_point[1] + y))
        return new_positions

    def apply_positions(self, new_positions):
        """Apply a previewed update"""
        # Update DrawImage positions
        for (p, c) in zip(new_positions, self.children):
            c.pos = p
        self.positions = new_positions


class Block(BlockDrawing):
    def __init__(self, context, name, *args, **kwargs):
        super().__init__(context, name, (3, 19), *args, **kwargs)
        self.cells = 4  # Number of cells occupied by the block
        config.block_count += 1

        # Mark occupied blocks
        config.cells_occupied.update(self.positions)

        # Update statistics
        # Take the value shown, add 1 and set value
        text_item = C[name+"_stat"]
        text_item.text = str(int(text_item.text)+1)
        text_total = C["Total_block_stat"]
        text_total.value = str(int(text_total.value)+1)

    def try_motion(self, new_positions):
        """Perform a motion of it is allowed"""
        config.cells_occupied.difference_update(self.positions)
        forbidden = config.cells_occupied.union(config.cell_boundary)
        if len(forbidden.intersection(set(new_positions))) == 0:
            self.apply_positions(new_positions)
        config.cells_occupied.update(self.positions)

    def try_rotate(self):
        """Try to rotate 90 degrees clockwise"""
        new_positions = self.preview_rotation()
        self.try_motion(new_positions)

    def try_left(self):
        """Try to move left"""
        new_positions = self.preview_shift(-1, 0)
        self.try_motion(new_positions)

    def try_right(self):
        """Try to move right"""
        new_positions = self.preview_shift(1, 0)
        self.try_motion(new_positions)

    def move_block_down(self):
        # Function controls the continuous downward movement of the blocks
        success = True
        new_positions = self.preview_shift(0, -1)
        config.cells_occupied.difference_update(self.positions)
        forbidden = config.cells_occupied.union(config.cell_boundary)
        if len(forbidden.intersection(set(new_positions))) == 0:
            self.apply_positions(new_positions)
        else:
            config.current_block = None # Block has stopped moving
            # Register the block pieces to the dead list
            for c in self.children:
                config.dead_blocks[c.pos] = c
            # Move the block pieces to the parent
            for c in self.children:
                c.parent = self.parent
            # Remove ourselves from the rendering tree.
            self.parent = None
            # Will be deleted when not referenced anymore
            success = False
        config.cells_occupied.update(self.positions)
        return success


class BlockStatistics(dcg.DrawingList):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)
        names_pos = [("I", (2, 15)),
                     ("J", (1, 1)),
                     ("L", (1, 18)),
                     ("O", (3, 4)),
                     ("S", (3, 10)),
                     ("T", (1, 13)),
                     ("Z", (1, 7))]
        for (name, pos) in names_pos:
            name += "_block"
            BlockDrawing(context,
                         name,
                         pos,
                         parent=self)
            y = pos[1]
            if y == 15:
                y = 15.5
            dcg.DrawLine(context,
                         p1=[6.5, y],
                         p2=[7.5, y],
                         thickness=0.1,
                         color=[168, 168, 168],
                         parent=self)
            dcg.DrawText(context,
                         pos=[8.5, y + 0.3],
                         text="0", size=0.5,
                         color=[168, 168, 168],
                         tag=name+"_stat")
