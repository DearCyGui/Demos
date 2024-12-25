import numpy as np
import dearcygui as dcg
import os
import imageio
from cuda import cuda
import OpenGL.GL as gl

# Untested for now

# CUDA kernel for Gaussian blur
cuda_kernel = """
extern "C" __global__ void blur(uchar4 *src, int w, int h, uchar4 *dst) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int y = blockIdx.y * blockDim.y + threadIdx.y;
    
    if (x >= w || y >= h)
        return;
        
    float4 result = make_float4(0.0f, 0.0f, 0.0f, 0.0f);
    
    #define ANCHOR_X ((KERNEL_SIZE_X-1)/2)
    #define ANCHOR_Y ((KERNEL_SIZE_Y-1)/2)
    
    for (int sy = 0; sy < KERNEL_SIZE_Y; sy++) {
        float4 col = make_float4(0.0f, 0.0f, 0.0f, 0.0f);
        for (int sx = 0; sx < KERNEL_SIZE_X; sx++) {
            int py = min(h-1, max(0, y - ANCHOR_Y + sy));
            int px = min(w-1, max(0, x + sx - ANCHOR_X));
            uchar4 val = src[py * w + px];
            col.x += val.x;
            col.y += val.y;
            col.z += val.z;
            col.w += val.w;
        }
        result.x += col.x;
        result.y += col.y;
        result.z += col.z;
        result.w += col.w;
    }
    
    float scale = 1.0f / (KERNEL_SIZE_X * KERNEL_SIZE_Y);
    dst[y * w + x] = make_uchar4(
        (unsigned char)(result.x * scale),
        (unsigned char)(result.y * scale),
        (unsigned char)(result.z * scale),
        (unsigned char)(result.w * scale)
    );
}
"""

def check_cuda_errors(err):
    if err != cuda.CUresult.CUDA_SUCCESS:
        raise RuntimeError(f"CUDA error: {err}")

def demo_cuda_sharing():
    C = dcg.Context()
    blur_width = dcg.SharedInt(C, 1)
    blur_height = dcg.SharedInt(C, 1)
    C.viewport.initialize(vsync=True,
                        wait_for_input=True,
                        title="CUDA-GL sharing")

    # Initialize CUDA
    check_cuda_errors(cuda.cuInit(0))
    device = cuda.CUdevice(0)
    ctx = cuda.CUcontext(0)
    ctx.push()

    # Load and prepare image
    path = os.path.join(os.path.dirname(__file__), "lenapashm.png")
    image = imageio.imread(path)
    image = image + 40. * np.random.randn(*image.shape)
    image = np.clip(image, 0, 255).astype(np.uint8)
    image = np.ascontiguousarray(image)
    
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    if len(image.shape) == 2:
        image = image[:,:,np.newaxis]
    if image.shape[2] < 4:
        image = np.concatenate([image, np.ones((image.shape[0], image.shape[1], 4-image.shape[2]), dtype=np.uint8) * 255], axis=2)

    texture = dcg.Texture(C)
    texture.set_value(image)

    # Allocate CUDA memory
    height, width = image.shape[:2]
    size = width * height * 4
    d_src = cuda.cuMemAlloc(size)
    d_dst = cuda.cuMemAlloc(size)
    cuda.cuMemcpyHtoD(d_src, image.ctypes.data, size)

    # Create CUDA module with kernel
    def compile_kernel(blur_w, blur_h):
        options = [f'-DKERNEL_SIZE_X={blur_w}', f'-DKERNEL_SIZE_Y={blur_h}']
        return cuda.cuModuleLoadData(cuda.cuLinkCreate(options, cuda_kernel))

    module = compile_kernel(blur_width.value, blur_height.value)
    kernel = module.get_function('blur')

    def refresh_image():
        nonlocal module, kernel
        
        # Recompile kernel with new sizes
        module = compile_kernel(blur_width.value, blur_height.value)
        kernel = module.get_function('blur')

        # Register GL texture with CUDA
        resource = cuda.CUDA_GRAPHICS_RESOURCE()
        check_cuda_errors(cuda.cuGraphicsGLRegisterImage(
            resource, texture.texture_id, gl.GL_TEXTURE_2D,
            cuda.CUgraphicsRegisterFlags.CUDA_GRAPHICS_REGISTER_FLAGS_WRITE_DISCARD))

        # Map GL texture to CUDA
        check_cuda_errors(cuda.cuGraphicsMapResources(1, resource, 0))
        array = cuda.CUarray(0)
        check_cuda_errors(cuda.cuGraphicsSubResourceGetMappedArray(array, resource, 0, 0))

        # Launch kernel
        block = (16, 16, 1)
        grid = ((width + block[0] - 1) // block[0],
                (height + block[1] - 1) // block[1],
                1)
        
        kernel.launch(grid, block, (d_src, width, height, d_dst))
        
        # Copy result to GL texture
        copy_params = cuda.CUDA_MEMCPY2D()
        copy_params.srcMemoryType = cuda.CUmemorytype.CU_MEMORYTYPE_DEVICE
        copy_params.srcDevice = d_dst
        copy_params.srcPitch = width * 4
        copy_params.dstMemoryType = cuda.CUmemorytype.CU_MEMORYTYPE_ARRAY
        copy_params.dstArray = array
        copy_params.Width = width * 4
        copy_params.Height = height
        check_cuda_errors(cuda.cuMemcpy2D(copy_params))

        # Unmap resource
        check_cuda_errors(cuda.cuGraphicsUnmapResources(1, resource, 0))
        check_cuda_errors(cuda.cuGraphicsUnregisterResource(resource))
        
        C.viewport.wake()

    with dcg.Window(C, primary=True):
        dcg.Image(C, texture=texture, width=512, height=512)
        with dcg.ChildWindow(C, width=0, height=0):
            dcg.Slider(C, label="Blur width", shareable_value=blur_width, min_value=1, format='int', max_value=10, width=100, callback=refresh_image)
            dcg.Slider(C, label="Blur height", shareable_value=blur_height, min_value=1, format='int', max_value=10, width=100, callback=refresh_image)

    while C.running:
        C.viewport.render_frame()

    # Cleanup
    cuda.cuMemFree(d_src)
    cuda.cuMemFree(d_dst)
    ctx.pop()

if __name__ == "__main__":
    demo_cuda_sharing()
