import moderngl
import dearcygui as dcg
import imageio
import os
import numpy as np
import pyrr
from collections import deque
import time


cube_vertex_shader = """
#version 330 core
in vec3 position;
in vec2 texCoord;
out vec2 vTexCoord;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    gl_Position = projection * view * model * vec4(position, 1.0);
    vTexCoord = texCoord;
}
"""

cube_fragment_shader = """
#version 330 core
in vec2 vTexCoord;
out vec4 fragColor;
uniform sampler2D tex;

void main() {
    fragColor = 0.9 * texture(tex, vTexCoord) + 0.1;
}
"""

class CubeDemo:
    def __init__(self, C : dcg.Context):
        self.C = C
        shared_context = C.create_new_shared_gl_context(3, 3)
        if shared_context is None:
            raise ValueError("Failed to create shared context")
    
        self.shared_context = shared_context
        shared_context.make_current()
        ctx = moderngl.create_context()
        self.ctx = ctx
        self.program = ctx.program(vertex_shader=cube_vertex_shader, fragment_shader=cube_fragment_shader)
        # Define cube vertices and indices
        cube_vertices = np.array([
            # front face
            -1.0, -1.0, -1.0,  1.0, 1.0,
            -1.0,  1.0, -1.0,  1.0, 0.0,
            1.0,  1.0, -1.0,  0.0, 0.0,
            1.0, -1.0, -1.0,  0.0, 1.0,

            # back face
            1.0, -1.0,  1.0,  1.0, 1.0,
            1.0,  1.0,  1.0,  1.0, 0.0,
            -1.0,  1.0,  1.0,  0.0, 0.0,
            -1.0, -1.0,  1.0,  0.0, 1.0,

            # left face
            -1.0, -1.0,  1.0,  1.0, 1.0,
            -1.0,  1.0,  1.0,  1.0, 0.0,
            -1.0,  1.0, -1.0,  0.0, 0.0,
            -1.0, -1.0, -1.0,  0.0, 1.0,

            # right face
            1.0, -1.0, -1.0,  1.0, 1.0,
            1.0,  1.0, -1.0,  1.0, 0.0,
            1.0,  1.0,  1.0,  0.0, 0.0,
            1.0, -1.0,  1.0,  0.0, 1.0,

            # top face
            -1.0,  1.0, -1.0,  1.0, 1.0,
            -1.0,  1.0,  1.0,  1.0, 0.0,
            1.0,  1.0,  1.0,  0.0, 0.0,
            1.0,  1.0, -1.0,  0.0, 1.0,

            # bottom face
            -1.0, -1.0,  1.0,  1.0, 1.0,
            -1.0, -1.0, -1.0,  1.0, 0.0,
            1.0, -1.0, -1.0,  0.0, 0.0,
            1.0, -1.0,  1.0,  0.0, 1.0
        ], dtype='f4')

        cube_indices = np.array([
            # front
            0, 1, 2, 2, 3, 0,
            # back
            4, 5, 6, 6, 7, 4,
            # left
            8, 9, 10, 10, 11, 8,
            # right
            12, 13, 14, 14, 15, 12,
            # top
            16, 17, 18, 18, 19, 16,
            # bottom
            20, 21, 22, 22, 23, 20
        ], dtype='i4')
        self.vbo = ctx.buffer(cube_vertices.tobytes())
        self.ibo = ctx.buffer(cube_indices.tobytes())
        self.vao = ctx.vertex_array(
            self.program,
            [(self.vbo, '3f 2f', 'position', 'texCoord')],
            self.ibo
        )
        shared_context.release()
        texture = dcg.Texture(C)
        texture.allocate(width=512, height=512, num_chans=4, uint8=True)
        shared_context.make_current()
        # Create framebuffer using the DCG texture ID
        dcg_texture = ctx.external_texture(texture.texture_id, (texture.width, texture.height), 4, 0, "f1")
        depth_rb = ctx.depth_renderbuffer((texture.width, texture.height))
        fbo = ctx.framebuffer(
            color_attachments=[dcg_texture],
            depth_attachment=depth_rb
        )
        alternative_texture = ctx.texture((512, 512), 4, dtype='f1')

        self.alternative_texture = alternative_texture

        depth_rb = ctx.depth_renderbuffer((texture.width, texture.height))
        alternative_fbo = ctx.framebuffer(
            color_attachments=[alternative_texture],
            depth_attachment=depth_rb
        )

        shared_context.release()
        self.texture = texture
        self.fbo_dcg = fbo
        self.fbo_internal = alternative_fbo
        self.window_internal_texture = None

    def __render(self, fbo, moderngl_window_texture, angle1, angle2, angle3):
        ctx = self.ctx
        moderngl_window_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        moderngl_window_texture.repeat_x = False
        moderngl_window_texture.repeat_y = False
        moderngl_window_texture.use(0)
        fbo.use()

        ctx.enable(moderngl.DEPTH_TEST)
        ctx.enable(moderngl.CULL_FACE)
        ctx.front_face = 'ccw'

        # Calculate rotation matrix
        rotation = pyrr.matrix44.create_from_eulers([np.radians(angle1),
                                                     np.radians(angle2),
                                                     np.radians(angle3)])
        model_matrix = pyrr.matrix44.create_identity()
        model_matrix = pyrr.matrix44.multiply(model_matrix, rotation)

        # Set uniform values
        self.program['model'].write(model_matrix.astype('f4').tobytes())
        self.program['view'].write(pyrr.matrix44.create_look_at(
            eye=[3.0, 3.0, 3.0],
            target=[0.0, 0.0, 0.0],
            up=[0.0, 1.0, 0.0]
        ).astype('f4').tobytes())
        self.program['projection'].write(pyrr.matrix44.create_perspective_projection(
            fovy=45.0, aspect=1.0, near=0.1, far=100.0
        ).astype('f4').tobytes())

        # clear fbo
        ctx.clear()

        # Render the cube
        self.vao.render(moderngl.TRIANGLES)

    def __del__(self):
        self.shared_context.make_current()
        self.vao.release()
        self.vbo.release()
        self.ibo.release()
        self.program.release()
        self.fbo_dcg.release()
        self.fbo_internal.release()
        self.alternative_texture.release()
        if self.window_internal_texture is not None:
            self.window_internal_texture.release()
        self.ctx.release()
        self.shared_context.release()

    def render_finish(self, angle1, angle2, angle3):
        """
        Render using gl finish for synchronization
        """
        shared_context = self.shared_context
        ctx = self.ctx
        shared_context.make_current()
        window_texture = self.C.viewport.framebuffer
        moderngl_window_texture = \
            ctx.external_texture(window_texture.texture_id,
                                 (window_texture.width, window_texture.height),
                                 4, 0, "f1")
        self.__render(self.fbo_dcg, moderngl_window_texture, angle1, angle2, angle3)
        ctx.finish()
        shared_context.release()

    def render_numpy(self, angle1, angle2, angle3):
        """
        Render downloading to a numpy array and reuploading back
        """
        window_texture = self.C.viewport.framebuffer
        image = window_texture.read() # numpy array
        shared_context = self.shared_context
        ctx = self.ctx
        shared_context.make_current()
        if self.window_internal_texture is None:
            self.window_internal_texture = ctx.texture((image.shape[1], image.shape[0]), 4, dtype='f1')
        self.window_internal_texture.write(image.tobytes())
        self.__render(self.fbo_internal, self.window_internal_texture, angle1, angle2, angle3)
        result = self.alternative_texture.read()
        result = np.frombuffer(result, dtype=np.uint8).reshape((self.texture.height, self.texture.width, 4))
        shared_context.release()
        self.texture.set_value(result)

    def render_no_syncs(self, angle1, angle2, angle3):
        """
        Render without any synchronization
        """
        shared_context = self.shared_context
        ctx = self.ctx
        shared_context.make_current()
        window_texture = self.C.viewport.framebuffer
        moderngl_window_texture = \
            ctx.external_texture(window_texture.texture_id,
                                 (window_texture.width, window_texture.height),
                                 4, 0, "f1")
        self.__render(self.fbo_dcg, moderngl_window_texture, angle1, angle2, angle3)
        shared_context.release()

    def render_with_syncs(self, angle1, angle2, angle3):
        """
        Render using synchronization
        """
        shared_context = self.shared_context
        ctx = self.ctx
        shared_context.make_current()
        window_texture = self.C.viewport.framebuffer
        moderngl_window_texture = \
            ctx.external_texture(window_texture.texture_id,
                                 (window_texture.width, window_texture.height),
                                 4, 0, "f1")
        window_texture.gl_begin_read()
        self.texture.gl_begin_write()
        self.__render(self.fbo_dcg, moderngl_window_texture, angle1, angle2, angle3)
        window_texture.gl_end_read()
        self.texture.gl_end_write()
        shared_context.release()


def demo_moderngl_sharing():
    C = dcg.Context()
    C.viewport.initialize(title="ModernGL sharing 2", vsync=False)
    C.viewport.retrieve_framebuffer = True
    cube = CubeDemo(C)

    with dcg.Window(C):
        dcg.Text(C, value="This is embedded moderngl rendering using DCG")
        rendering_type = dcg.Combo(C, items=["glFinish", "numpy", "no syncs", "with syncs"])
        rendering_type.value = "glFinish"
        text = dcg.TextValue(C, print_format="FPS: %.2f", shareable_value=dcg.SharedDouble(C, 0))
        # rotating angles of the cube
        angle1 = dcg.Slider(C, min_value=0, max_value=360, value=0)
        angle2 = dcg.Slider(C, min_value=0, max_value=360, value=0)
        angle3 = dcg.Slider(C, min_value=0, max_value=360, value=0)
        image = dcg.Image(C, texture=cube.texture)

    frame_times = deque(maxlen=600)  # Store last 600 frames
    last_time = time.perf_counter()

    while C.running:
        current_time = time.perf_counter()
        frame_time = current_time - last_time
        frame_times.append(frame_time)
        last_time = current_time
        C.viewport.render_frame()
        rendering_type_value = rendering_type.value
        if rendering_type_value == "glFinish":
            cube.render_finish(angle1.value, angle2.value, angle3.value)
        elif rendering_type_value == "numpy":
            cube.render_numpy(angle1.value, angle2.value, angle3.value)
        elif rendering_type_value == "no syncs":
            cube.render_no_syncs(angle1.value, angle2.value, angle3.value)
        elif rendering_type_value == "with syncs":
            cube.render_with_syncs(angle1.value, angle2.value, angle3.value)
        avg_frame_time = sum(frame_times) / len(frame_times)
        fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        text.value = fps

if __name__ == "__main__":
    demo_moderngl_sharing()
