import dearcygui as dcg

def create_new_font(C, size, **kwargs):
    # Manual DPI handling (method 2 described in Font texture)
    # This is needed for sharp fonts even for small sizes.
    current_scale = C.viewport.dpi * C.viewport.scale
    size = round(size*current_scale)
    # Load the default texture at the target size
    font_texture = dcg.FontTexture(C)
    font_texture.add_custom_font(*dcg.fonts.make_extended_latin_font(size, **kwargs))
    font = font_texture[0]
    # end of method 2 of manual DPI handling
    font.scale = 1./current_scale
    return font_texture[0]