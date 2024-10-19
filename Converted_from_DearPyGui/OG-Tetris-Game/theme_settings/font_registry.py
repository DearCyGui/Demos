# Add all fonts
import dearcygui as dcg
from config import C

main_font_registry = dcg.FontTexture(C)
main_font_registry.add_font_file('fonts/PressStart2P-vaV7.ttf', size=15)
main_font_registry.add_font_file('fonts/PressStart2P-vaV7.ttf', size=18)
main_font_registry.build()
regular_font = main_font_registry[0]
play_font = main_font_registry[1]