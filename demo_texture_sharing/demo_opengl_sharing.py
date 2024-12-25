import OpenGL.GL as gl
try:
    import OpenGL.EGL as egl
except (ImportError, AttributeError):
    egl = None
try:
    import OpenGL.GLX as glx
except (ImportError, AttributeError):
    glx = None
try:
    import OpenGL.WGL as wgl
except (ImportError, AttributeError):
    wgl = None
try:
    from OpenGL import cgl
except (ImportError, AttributeError):
    cgl = None
import dearcygui as dcg
import imageio
import os
import numpy as np
import ctypes
import argparse

vertex_shader = """
#version 330 core
in vec2 position;
out vec2 texCoord;

void main() {
    gl_Position = vec4(position, 0.0, 1.0);
    texCoord = position * 0.5 + 0.5;
}
"""

gl_7x7_blur_shader = """
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



def demo_opengl_sharing(use_dcg_context=True):
    # This demo demonstrates how to create
    # a shared context with OpenGL and import
    # a dcg Texture into the Opengl context
    # and render to it.
    C = dcg.Context()
    blur_width = dcg.SharedInt(C, 1)
    blur_height = dcg.SharedInt(C, 1)
    C.viewport.initialize(vsync=True,
                          wait_for_input=True,
                          title="OpenGL sharing")
    path = os.path.join(os.path.dirname(__file__), "lenapashm.png")
    image = imageio.imread(path)
    # Add noise
    image = image + 40. * np.random.randn(*image.shape)
    image = np.clip(image, 0, 255).astype(np.uint8)
    texture = dcg.Texture(C)
    texture.set_value(image) # initialize the texture
    C.viewport.render_frame()
    backend = "NONE"
    # First method to get a shared gl context: ask DCG
    if use_dcg_context:
        try:
            shared_context = C.create_new_shared_gl_context(3, 3)
            if shared_context is None:
                raise ValueError("Failed to create shared context")
            backend = "DCG"
        except:
            pass
    # Second method: More manual, but more freedom.
    # Make current the context
    with C.rendering_context as rc:
        if rc.name != "GL":
            raise ValueError("This demo requires an OpenGL rendering context")

        # Try retrieving the EGL context and display
        if backend == "NONE" and egl is not None:
            egl_display = egl.eglGetCurrentDisplay()
            egl_context = egl.eglGetCurrentContext()
            if egl_display != egl.EGL_NO_DISPLAY and egl_context != egl.EGL_NO_CONTEXT:
                backend = "EGL"

        # Try GLX
        if backend == "NONE" and glx is not None:
            # Get current display and GLX context
            glx_display = glx.glXGetCurrentDisplay()
            glx_context = glx.glXGetCurrentContext()
            
            if glx_display and glx_context:
                backend = "GLX"

        # Try WGL
        if backend == "NONE" and wgl is not None:
            wgl_context = wgl.wglGetCurrentContext()
            wgl_dc = wgl.wglGetCurrentDC()
            
            if wgl_context and wgl_dc:
                backend = "WGL"

        # Try CGL (Mac)
        if backend == "NONE" and cgl is not None:
            cgl_context = cgl.CGLGetCurrentContext()
            if cgl_context:
                backend = "CGL"

    if backend == "NONE":
        raise ValueError("Couldn't determine the context type")

    if backend == "DCG":
        shared_context.make_current()

    if backend == "EGL":
        # Create config for shared context
        config_attribs = (egl.EGLint * 11)(
            egl.EGL_RED_SIZE, 8,
            egl.EGL_GREEN_SIZE, 8, 
            egl.EGL_BLUE_SIZE, 8,
            egl.EGL_ALPHA_SIZE, 8,
            egl.EGL_RENDERABLE_TYPE, egl.EGL_OPENGL_BIT,
            egl.EGL_NONE
        )
        num_configs = egl.EGLint()
        configs = (egl.EGLConfig * 1)()
        egl.eglChooseConfig(egl_display, config_attribs, configs, 1, num_configs)

        if not num_configs.value:
            raise RuntimeError("No suitable EGL configs found")

        # Create shared context
        context_attribs = (egl.EGLint * 3)(
            egl.EGL_CONTEXT_CLIENT_VERSION, 3,
            egl.EGL_NONE
        )
        shared_context = egl.eglCreateContext(egl_display, configs[0], egl_context, context_attribs)
        if shared_context == egl.EGL_NO_CONTEXT:
            error = egl.eglGetError()
            raise RuntimeError(f"Failed to create EGL context: {error}")

        # Make context current with no surface
        if not egl.eglMakeCurrent(egl_display, egl.EGL_NO_SURFACE, egl.EGL_NO_SURFACE, shared_context):
            error = egl.eglGetError() 
            raise RuntimeError(f"Failed to make context current: {error}")

    if backend == "GLX":
        # Get matching FB config
        fb_configs = None
        n_configs = ctypes.c_int(0)
        fb_config_attribs = (ctypes.c_int * 13)(
            glx.GLX_RENDER_TYPE, glx.GLX_RGBA_BIT,
            glx.GLX_DRAWABLE_TYPE, glx.GLX_PBUFFER_BIT,
            glx.GLX_RED_SIZE, 8,
            glx.GLX_GREEN_SIZE, 8,
            glx.GLX_BLUE_SIZE, 8,
            glx.GLX_ALPHA_SIZE, 8,
            0
        )
        fb_configs = glx.glXChooseFBConfig(glx_display, 0, fb_config_attribs, ctypes.byref(n_configs))
        if not fb_configs or n_configs.value == 0:
            raise RuntimeError("Failed to find matching FB config")

        shared_context = glx.glXCreateNewContext(
            glx_display,
            fb_configs[0],
            glx.GLX_RGBA_TYPE,
            glx_context,
            True
        )

        if not shared_context:
            raise RuntimeError("Failed to create GLX context")

        # Create pbuffer for off-screen rendering
        pbuffer_attribs = [
            glx.GLX_PBUFFER_WIDTH, 1,
            glx.GLX_PBUFFER_HEIGHT, 1,
            0
        ]
        pbuffer_attribs_array = (ctypes.c_int * len(pbuffer_attribs))(*pbuffer_attribs)
        pbuffer = glx.glXCreatePbuffer(glx_display, fb_configs[0], pbuffer_attribs_array)

        # Make context current
        if not glx.glXMakeContextCurrent(glx_display, pbuffer, pbuffer, shared_context):
            raise RuntimeError("Failed to make GLX context current")

    if backend == "WGL":
        # Create dummy window for context creation
        WNDCLASS = ctypes.wintypes.WNDCLASS()
        WNDCLASS.lpfnWndProc = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p)(lambda h, m, w, l: 0)
        WNDCLASS.style = 0
        WNDCLASS.hInstance = 0
        WNDCLASS.lpszClassName = "DummyClass"
        ctypes.windll.user32.RegisterClassA(ctypes.byref(WNDCLASS))
        
        dummy_window = ctypes.windll.user32.CreateWindowExA(
            0, WNDCLASS.lpszClassName, "", 0,
            0, 0, 1, 1, 0, 0, WNDCLASS.hInstance, 0
        )
        
        dummy_dc = ctypes.windll.user32.GetDC(dummy_window)
        
        # Create shared context using wglCreateContextAttribsARB
        attribs = [
            wgl.WGL_CONTEXT_MAJOR_VERSION_ARB, 3,
            wgl.WGL_CONTEXT_MINOR_VERSION_ARB, 3,
            wgl.WGL_CONTEXT_PROFILE_MASK_ARB, wgl.WGL_CONTEXT_CORE_PROFILE_BIT_ARB,
            0
        ]
        attribs_array = (ctypes.c_int * len(attribs))(*attribs)
        
        shared_context = wgl.wglCreateContextAttribsARB(dummy_dc, wgl_context, attribs_array)
        if not shared_context:
            raise RuntimeError("Failed to create WGL context")

        # Make context current
        if not wgl.wglMakeCurrent(dummy_dc, shared_context):
            raise RuntimeError("Failed to make WGL context current")

    if backend == "CGL":
        # Create shared context for Mac
        pixel_format = cgl.CGLGetPixelFormat(cgl_context)
        if not pixel_format:
            raise RuntimeError("Failed to get pixel format")

        new_context = cgl.CGLContextObj()
        error = cgl.CGLCreateContext(pixel_format, cgl_context, ctypes.byref(new_context))
        if error != cgl.kCGLNoError:
            raise RuntimeError(f"Failed to create CGL context: {error}")

        shared_context = new_context
        error = cgl.CGLSetCurrentContext(shared_context)
        if error != cgl.kCGLNoError:
            raise RuntimeError(f"Failed to make CGL context current: {error}")

    # Get DCG texture GL handle
    gl_texture_handle = texture.texture_id
    # Since we created a shared GL context, they share the texture ids.

    # Create shader program
    vert_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    gl.glShaderSource(vert_shader, vertex_shader)
    gl.glCompileShader(vert_shader)

    frag_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    gl.glShaderSource(frag_shader, gl_7x7_blur_shader)
    gl.glCompileShader(frag_shader)

    program = gl.glCreateProgram()
    gl.glAttachShader(program, vert_shader)
    gl.glAttachShader(program, frag_shader)
    gl.glLinkProgram(program)

    # Create VBO/EBO
    vertices = np.array([
        -1.0, -1.0,
         1.0, -1.0,
         1.0,  1.0,
        -1.0,  1.0
    ], dtype=np.float32)
    
    indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

    vbo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

    ebo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW)

    # Create VAO
    vao = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
    
    # Set up vertex attributes
    position_loc = gl.glGetAttribLocation(program, 'position')
    gl.glEnableVertexAttribArray(position_loc)
    gl.glVertexAttribPointer(position_loc, 2, gl.GL_FLOAT, False, 0, None)

    # Create framebuffer
    fbo = gl.glGenFramebuffers(1)
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo)
    gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, 
                     gl.GL_TEXTURE_2D, gl_texture_handle, 0)

    # Make sure the numpy array is of the right format and convert if needed
    image = np.ascontiguousarray(image)
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    # make sure it is rgba
    if len(image.shape) == 2:
        image = image[:,:,np.newaxis]
    if image.shape[2] < 4:
        image = np.concatenate([image, np.ones((image.shape[0], image.shape[1], 4-image.shape[2]), dtype=np.uint8) * 255], axis=2)

    # Create input texture and upload the image
    input_texture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, input_texture)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, texture.width, texture.height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image.data)

    # Release context
    if backend == "DCG":
        shared_context.release()
    elif backend == "EGL":
        egl.eglMakeCurrent(egl_display, egl.EGL_NO_SURFACE, egl.EGL_NO_SURFACE, egl.EGL_NO_CONTEXT)
    elif backend == "GLX":
        glx.glXMakeContextCurrent(glx_display, 0, 0, None)
    elif backend == "WGL":
        wgl.wglMakeCurrent(None, None)
    elif backend == "CGL":
        cgl.CGLSetCurrentContext(None)


    def refresh_image():
        """Render blur effect to texture"""
        # Make shared context current
        if backend == "DCG":
            shared_context.make_current()
        elif backend == "EGL":
            egl.eglMakeCurrent(egl_display, egl.EGL_NO_SURFACE, egl.EGL_NO_SURFACE, shared_context)
        elif backend == "GLX":
            glx.glXMakeContextCurrent(glx_display, pbuffer, pbuffer, shared_context)
        elif backend == "WGL":
            wgl.wglMakeCurrent(dummy_dc, shared_context)
        elif backend == "CGL":
            cgl.CGLSetCurrentContext(shared_context)
        
        # Set up GL state
        gl.glViewport(0, 0, texture.width, texture.height)
        gl.glUseProgram(program)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo)
        gl.glBindVertexArray(vao)
        
        # Set uniforms
        gl.glUniform1i(gl.glGetUniformLocation(program, "blurWidth"), blur_width.value)
        gl.glUniform1i(gl.glGetUniformLocation(program, "blurHeight"), blur_height.value)
        gl.glUniform1i(gl.glGetUniformLocation(program, "tex"), 0)
        
        # Bind texture
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, input_texture)
        
        # Draw quad
        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)
        
        # Submit and share with the other context
        gl.glFlush()
        C.viewport.wake()
        
        # Release context
        if backend == "DCG":
            shared_context.release()
        elif backend == "EGL":
            egl.eglMakeCurrent(egl_display, egl.EGL_NO_SURFACE, egl.EGL_NO_SURFACE, egl.EGL_NO_CONTEXT)
        elif backend == "GLX":
            glx.glXMakeContextCurrent(glx_display, 0, 0, None)
        elif backend == "WGL":
            wgl.wglMakeCurrent(None, None)
        elif backend == "CGL":
            cgl.CGLSetCurrentContext(None)

    # Initial render
    refresh_image()

    with dcg.Window(C, primary=True):
        dcg.Image(C, texture=texture, width=512, height=512)
        with dcg.ChildWindow(C, width=0, height=0):
            dcg.Slider(C, label="Blur width", shareable_value=blur_width, min_value=1, format='int', max_value=10, width=100, callback=refresh_image)
            dcg.Slider(C, label="Blur height", shareable_value=blur_height, min_value=1, format='int', max_value=10, width=100, callback=refresh_image)
    while C.running:
        C.viewport.render_frame()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OpenGL sharing demo')
    parser.add_argument('--no-dcg-context', action='store_false', 
                      dest='use_dcg_context',
                      help='Do not use the shared context provided by DearCyGui')
    args = parser.parse_args()
    demo_opengl_sharing(use_dcg_context=args.use_dcg_context)