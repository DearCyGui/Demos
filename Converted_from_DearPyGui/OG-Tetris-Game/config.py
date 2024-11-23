# Sets up all important config variables
import dearcygui as dcg
import dearcygui.dearpygui

# Context
# We use DPGContext, which has support
# for "tag" arguments
class ContextWithTag(dearcygui.dearpygui.DPGContext):
    # Use C[] syntax for tag instead of C.get
    def __getitem__(self, tag):
        return self.get(tag)
C = ContextWithTag()

textures = []

# Names of all blocks
block_names = ["I", "J", "L", "O", "S", "T", "Z"]


# Set up lists to track walls and cells occupied
cell_boundary1 = [(n, -1) for n in range(10)]  # Bottom Wall
cell_boundary2 = [(10, n) for n in range(20)]  # Right Wall
cell_boundary3 = [(n, 20) for n in range(10)]  # Top Wall
cell_boundary4 = [(-1, n) for n in range(20)]  # Left Wall

 # All points in all walls combined
cell_boundary = set(cell_boundary1 + cell_boundary2 + cell_boundary3 + cell_boundary4)
cells_occupied = set()  # Set of all cells occupied by tetris blocks

# List of all block numbers active on the tetris board
block_numbers = []

# Count of blocks created
block_count = 0

# Current moving block
current_block = None

# Unactive block pieces
dead_blocks = {}

# Keep track of level and corresponding speed
level = 0
speed = 0

# Keep track of full lines completed
full_lines = 0

# Keep track of score
score = 0
