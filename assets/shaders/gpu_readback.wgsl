// Edge detection compute shader for image processing
// This shader applies Sobel edge detection to an input texture

@group(0) @binding(0) var input_texture: texture_2d<f32>;
@group(0) @binding(1) var texture_sampler: sampler;
@group(0) @binding(2) var output_texture: texture_storage_2d<rgba8unorm, write>;

// Sobel edge detection kernels for X and Y gradients
// Sobel X kernel (detects vertical edges)
const SOBEL_X: array<array<f32, 3>, 3> = array<array<f32, 3>, 3>(
    array<f32, 3>(-1.0, 0.0, 1.0),
    array<f32, 3>(-2.0, 0.0, 2.0),
    array<f32, 3>(-1.0, 0.0, 1.0)
);

// Sobel Y kernel (detects horizontal edges)
const SOBEL_Y: array<array<f32, 3>, 3> = array<array<f32, 3>, 3>(
    array<f32, 3>(-1.0, -2.0, -1.0),
    array<f32, 3>( 0.0,  0.0,  0.0),
    array<f32, 3>( 1.0,  2.0,  1.0)
);

@compute @workgroup_size(8, 8)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
    let texture_dims = textureDimensions(input_texture);
    let coords = vec2<i32>(i32(global_id.x), i32(global_id.y));
    
    // Check if we're within bounds
    if (coords.x >= i32(texture_dims.x) || coords.y >= i32(texture_dims.y)) {
        return;
    }
    
    // Initialize gradient accumulators
    var gx = vec3<f32>(0.0, 0.0, 0.0);
    var gy = vec3<f32>(0.0, 0.0, 0.0);
    
    // Apply 3x3 Sobel edge detection kernels
    for (var dy: i32 = -1; dy <= 1; dy++) {
        for (var dx: i32 = -1; dx <= 1; dx++) {
            // Calculate sample coordinates
            let sample_coords = coords + vec2<i32>(dx, dy);
            
            // Clamp coordinates to texture bounds
            let clamped_coords = clamp(
                sample_coords, 
                vec2<i32>(0, 0), 
                vec2<i32>(i32(texture_dims.x) - 1, i32(texture_dims.y) - 1)
            );
            
            // Sample the input texture
            let sample_color = textureLoad(input_texture, clamped_coords, 0);
            
            // Convert to grayscale for edge detection
            let luminance = dot(sample_color.rgb, vec3<f32>(0.299, 0.587, 0.114));
            
            // Get the corresponding kernel weights
            let sobel_x_weight = SOBEL_X[dy + 1][dx + 1];
            let sobel_y_weight = SOBEL_Y[dy + 1][dx + 1];
            
            // Accumulate gradients
            gx += vec3<f32>(luminance) * sobel_x_weight;
            gy += vec3<f32>(luminance) * sobel_y_weight;
        }
    }
    
    // Calculate gradient magnitude
    let magnitude = length(vec2<f32>(gx.r, gy.r));
    
    // Create edge output - white edges on black background
    let edge_intensity = clamp(magnitude * 2.0, 0.0, 1.0); // Amplify edges
    let result_color = vec4<f32>(edge_intensity, edge_intensity, edge_intensity, 1.0);
    
    // Write the edge detection result to the output texture
    textureStore(output_texture, coords, result_color);
}