import pyopencl as cl
import OpenGL.GL as gl
from pyopencl.tools import get_gl_sharing_context_properties
import numpy as np
import dearcygui as dcg
import os
import imageio
import ctypes

if not(cl.have_gl()):
    raise ValueError("pyopencl needs to be built with 'export PYOPENCL_ENABLE_GL=ON'")


# A simple gaussian kernel without border handling
blur_kernel = """
#define ANCHOR_X ((KERNEL_SIZE_X-1)/2)
#define ANCHOR_Y ((KERNEL_SIZE_Y-1)/2)
__kernel void blur(__global const uchar4 *src,
                   int w, int h,
                   __global uchar4 *dst)
{
    int x = (int)get_global_id(0);
    int y = (int)get_global_id(1);
    float4 result = (float4)0.;

    if (x >= w || y >= h)
        return;

    #pragma unroll
    for (int sy = 0; sy < KERNEL_SIZE_Y; sy++) {
        float4 col = (float4)0.;
        #pragma unroll
        for (int sx = 0; sx < KERNEL_SIZE_X; sx++) {
            uchar4 val = src[min(h-1, max(0, y - ANCHOR_Y + sy)) * w + 
                       min(w-1, max(0, x + sx - ANCHOR_X))];
            col += convert_float4(val);
        }
        result += col;
    }
    dst[y * w + x] = convert_uchar4(result / (KERNEL_SIZE_X * KERNEL_SIZE_Y));
}
"""

def check_platform_extensions(platform):
    """Check if platform supports required extensions for GL sharing"""
    try:
        devices = platform.get_devices()
        if not devices:
            return False
        
        # Check for required extensions
        required_extensions = {'cl_khr_gl_sharing', 'cl_khr_gl_event'}
        for device in devices:
            extensions = device.extensions.split()
            if not required_extensions.issubset(set(extensions)):
                return False
        return True
    except:
        return False

def demo_opencl_sharing():
    # This demo demonstrates how to create
    # a shared context with OpenCL and import
    # a dcg Texture into the OpenCL context
    # and render to it.
    C = dcg.Context()
    blur_width = dcg.SharedFloat(C, 1)
    blur_height = dcg.SharedFloat(C, 1)
    C.viewport.initialize(vsync=True,
                          wait_for_input=True,
                          title="OpenGL sharing")
    path = os.path.join(os.path.dirname(__file__), "lenapashm.png")
    image = imageio.imread(path)
    # Add noise
    image = image + 40. * np.random.randn(*image.shape)
    image = np.clip(image, 0, 255).astype(np.uint8)

    # Make sure the numpy array is of the right format and convert if needed
    image = np.ascontiguousarray(image)
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)

    # make sure it is rgba
    if len(image.shape) == 2:
        image = image[:,:,np.newaxis]
    if image.shape[2] < 4:
        image = np.concatenate([image, np.ones((image.shape[0], image.shape[1], 4-image.shape[2]), dtype=np.uint8) * 255], axis=2)

    texture = dcg.Texture(C)
    texture.set_value(image) # initialize the texture
    with C.rendering_context as rc:
        if rc.name != "GL":
            raise ValueError("This demo requires an OpenGL rendering context")
        
        platforms = cl.get_platforms()
        if not platforms:
            raise ValueError("No OpenCL platforms found")

        ctx = None
        for platform in platforms:
            try:
                if not check_platform_extensions(platform):
                    print(f"Platform {platform.name} does not support required extensions, skipping...")
                    continue
                
                ctx = cl.Context(
                    dev_type=cl.device_type.ALL,
                    properties=[(cl.context_properties.PLATFORM, platform)] + \
                        get_gl_sharing_context_properties())
                print(f"Successfully created context with platform: {platform.name}")
                break
            except Exception as e:
                print(f"Failed to create context with platform {platform.name}: {e}")
                continue
        
        if ctx is None:
            raise ValueError("Could not create OpenCL context with GL sharing support")

    queue = cl.CommandQueue(ctx)

    mf = cl.mem_flags
    src = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=image)
    # Create output buffer and shared texture
    dst = cl.Buffer(ctx, mf.WRITE_ONLY, image.nbytes)
    tex_cl = cl.GLTexture(ctx, mf.WRITE_ONLY, gl.GL_TEXTURE_2D, 0, 
                            texture.texture_id, 2)

    def refresh_image():
        # Rebuild program with new kernel size
        build_flags = f"-DKERNEL_SIZE_X={int(blur_width.value)} -DKERNEL_SIZE_Y={int(blur_height.value)}"
        program = cl.Program(ctx, blur_kernel).build(options=build_flags)
            
        # Run the kernel
        program.blur(queue, image.shape, None,
                     src, 
                     np.int32(image.shape[1]),
                     np.int32(image.shape[0]),
                     dst)
        # It is possible to render to the texture directly,
        # using different syntax for the kernel. However
        # it is often simpler to reason in terms of buffers
        # with no tiling when writing OpenCL kernels, and
        # texture tiling can be quite complex. Thus in most
        # cases it should be simpler to just do a copy.
        cl.enqueue_acquire_gl_objects(queue, [tex_cl])
        cl.enqueue_copy(queue, tex_cl, dst, offset=0, origin=(0,0),
                        region=(image.shape[0], image.shape[1]))
        cl.enqueue_release_gl_objects(queue, [tex_cl])
        queue.flush()
        C.viewport.wake()

    with dcg.Window(C, primary=True):
        dcg.Image(C, texture=texture, width=512, height=512)
        with dcg.ChildWindow(C, width=0, height=0):
            dcg.Slider(C, label="Blur width", shareable_value=blur_width, min_value=1, print_format="%.0f", max_value=10, width=100, callback=refresh_image)
            dcg.Slider(C, label="Blur height", shareable_value=blur_height, min_value=1, print_format="%.0f", max_value=10, width=100, callback=refresh_image)
    while C.running:
        C.viewport.render_frame()

if __name__ == "__main__":
    demo_opencl_sharing()