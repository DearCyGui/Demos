import moderngl
import dearcygui as dcg
import imageio
import os
import numpy as np

vertex_shader = """
#version 330 core
in vec2 position;
out vec2 texCoord;

void main() {
    gl_Position = vec4(position, 0.0, 1.0);
    texCoord = position * 0.5 + 0.5;
}
"""

fragment_shader = """
#version 330 core
in vec2 texCoord;
out vec4 fragColor;
uniform sampler2D tex;
uniform int blurWidth;
uniform int blurHeight;

void main() {
    vec2 texSize = textureSize(tex, 0);
    vec2 texelSize = 1.0 / texSize;
    vec4 result = vec4(0.0);
    float weight = 0.0;
    
    for(int x = -blurWidth; x <= blurWidth; x++) {
        for(int y = -blurHeight; y <= blurHeight; y++) {
            vec2 offset = vec2(x * texelSize.x, y * texelSize.y);
            float w = 1.0 / (1.0 + length(vec2(x,y)));
            result += texture(tex, texCoord + offset) * w;
            weight += w;
        }
    }
    
    fragColor = result / weight;
}
"""

def demo_moderngl_sharing():
    C = dcg.Context()
    blur_width = dcg.SharedInt(C, 1)
    blur_height = dcg.SharedInt(C, 1)
    
    C.viewport.initialize(vsync=True, 
                         wait_for_input=True,
                         title="ModernGL sharing")

    # Load image
    path = os.path.join(os.path.dirname(__file__), "lenapashm.png")
    image = imageio.imread(path)
    # Add noise
    image = image + 40. * np.random.randn(*image.shape)
    image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Create DCG texture
    texture = dcg.Texture(C)
    texture.set_value(image)
    C.viewport.render_frame()

    # Get shared context from DCG
    shared_context = C.create_new_shared_gl_context(3, 3)
    if shared_context is None:
        raise ValueError("Failed to create shared context")
    
    shared_context.make_current()
    ctx = moderngl.create_context()

    # Create ModernGL program
    program = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

    # Create quad vertices and indices
    vertices = np.array([
        -1.0, -1.0,
         1.0, -1.0,
         1.0,  1.0,
        -1.0,  1.0
    ], dtype='f4')
    
    indices = np.array([0, 1, 2, 0, 2, 3], dtype='i4')

    # Create vertex buffer and vertex array
    vbo = ctx.buffer(vertices.tobytes())
    ibo = ctx.buffer(indices.tobytes())
    vao = ctx.vertex_array(
        program,
        [(vbo, '2f', 'position')],
        ibo
    )

    # Create input texture
    if len(image.shape) == 2:
        image = image[:,:,np.newaxis]
    if image.shape[2] < 4:
        image = np.concatenate([
            image, 
            np.ones((image.shape[0], image.shape[1], 4-image.shape[2]), dtype=np.uint8) * 255
        ], axis=2)
    
    input_texture = ctx.texture(image.shape[:2], 4, data=image.tobytes())
    input_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
    input_texture.repeat_x = False
    input_texture.repeat_y = False
    input_texture.use(0)
    
    # Create framebuffer using the DCG texture ID
    dcg_texture = ctx.external_texture(texture.texture_id, (texture.width, texture.height), 4, 0, "f1")
    fbo = ctx.framebuffer(
        color_attachments=[dcg_texture]
    )

    shared_context.release()

    def refresh_image():
        shared_context.make_current()
        
        # Render to framebuffer
        fbo.use()
        input_texture.use(0)
        
        program['blurWidth'].value = blur_width.value
        program['blurHeight'].value = blur_height.value
        program['tex'].value = 0
        
        vao.render()
        ctx.finish() # Unsure this is needed
        
        C.viewport.wake()
        shared_context.release()

    # Initial render
    refresh_image()

    with dcg.Window(C, primary=True):
        dcg.Image(C, texture=texture, width=512, height=512)
        with dcg.ChildWindow(C, width=0, height=0):
            dcg.Slider(C, label="Blur width", shareable_value=blur_width,
                      min_value=1, format='int', max_value=10, width=100,
                      callback=refresh_image)
            dcg.Slider(C, label="Blur height", shareable_value=blur_height,
                      min_value=1, format='int', max_value=10, width=100,
                      callback=refresh_image)

    while C.running:
        C.viewport.render_frame()

if __name__ == "__main__":
    demo_moderngl_sharing()
