import dearcygui as dcg

class TetrisContext(dcg.Context):
    def __init__(self):
        super().__init__()
        self.textures = []

        # Names of all blocks
        self.block_names = ["I", "J", "L", "O", "S", "T", "Z"]

        # Set up lists to track walls and cells occupied
        self.cell_boundary1 = [(n, -1) for n in range(10)]  # Bottom Wall
        self.cell_boundary2 = [(10, n) for n in range(20)]  # Right Wall
        self.cell_boundary3 = [(n, 20) for n in range(10)]  # Top Wall
        self.cell_boundary4 = [(-1, n) for n in range(20)]  # Left Wall

        # All points in all walls combined
        self.cell_boundary = set(
            self.cell_boundary1 + \
            self.cell_boundary2 + \
            self.cell_boundary3 + \
            self.cell_boundary4)
        self.cells_occupied = set()  # Set of all cells occupied by tetris blocks

        # List of all block numbers active on the tetris board
        self.block_numbers = []

        # Count of blocks created
        self.block_count = 0

        # Current moving block
        self.current_block = None

        # Unactive block pieces
        self.dead_blocks = {}

        # Keep track of level and corresponding speed
        self.level = 0
        self.speed = 0

        # Keep track of full lines completed
        self.full_lines = 0

        # Keep track of score
        self.score = 0

        # Fonts
        self.main_font_registry = dcg.FontTexture(self)
        self.main_font_registry.add_font_file('fonts/PressStart2P-vaV7.ttf', size=15)
        self.main_font_registry.add_font_file('fonts/PressStart2P-vaV7.ttf', size=18)
        self.main_font_registry.build()
        self.regular_font = self.main_font_registry[0]
        self.play_font = self.main_font_registry[1]

        # Themes
        with dcg.ThemeList(self) as self.global_theme:  # Sets up the default theme
            # Styles
            dcg.ThemeStyleImGui(self,
                                WindowPadding=(4, 4),
                                FramePadding=(8, 8),
                                ItemSpacing=(4, 4),
                                ChildRounding=4,
                                FrameRounding=4,
                                ChildBorderSize=0
                                )
            # Colors
            dcg.ThemeColorImGui(self,
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
            dcg.ThemeColorImPlot(self,
                                 PlotBg=(0, 0, 0),
                                 AxisGrid=(30, 30, 255),
                                 Line=(0, 0, 255),
                                 FrameBg=(0, 0, 0),
                                 PlotBorder=(30, 30, 255)
                                 )

        with dcg.ThemeList(self) as self.dummy_button_theme:
            dcg.ThemeColorImGui(self,
                                Button=(0, 0, 0),
                                ButtonHovered=(0, 0, 0),
                                ButtonActive=(0, 0, 0))

        with dcg.ThemeList(self) as self.play_button_theme:
            dcg.ThemeColorImGui(self,
                                Text=(161, 94, 33))

        with dcg.ThemeList(self) as self.no_border_board_theme:
            dcg.ThemeColorImPlot(self,
                                 PlotBorder=(0, 0, 0))

        self.sharp_lines_theme = dcg.ThemeStyleImPlot(self, LineWeight=0.9, no_scaling=True)