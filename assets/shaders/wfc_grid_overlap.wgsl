#import bevy_sprite::mesh2d_vertex_output::VertexOutput

@group(2) @binding(0) var grid_texture: texture_2d<f32>;
@group(2) @binding(1) var grid_sampler: sampler;
@group(2) @binding(2) var pattern_counts_texture: texture_2d<f32>;
@group(2) @binding(3) var pattern_counts_sampler: sampler;

// Gaussian blur kernel weights for 3x3 kernel
const BLUR_KERNEL: array<f32, 9> = array<f32, 9>(
    0.0625, 0.125, 0.0625,
    0.125,  0.25,  0.125,
    0.0625, 0.125, 0.0625
);

// Gaussian blur function
fn gaussian_blur(texture: texture_2d<f32>, sampler_: sampler, uv: vec2<f32>) -> vec4<f32> {
    let texture_size = vec2<f32>(textureDimensions(texture));
    let texel_size = 1.0 / texture_size;
    
    var result = vec4<f32>(0.0);
    
    // Apply 3x3 Gaussian kernel
    for (var i = 0; i < 3; i++) {
        for (var j = 0; j < 3; j++) {
            let offset = vec2<f32>(f32(i - 1), f32(j - 1)) * texel_size;
            let sample_uv = uv + offset;
            let weight = BLUR_KERNEL[i * 3 + j];
            result += textureSampleLevel(texture, sampler_, sample_uv, 0.0) * weight;
        }
    }
    
    return result;
}

@fragment
fn fragment(mesh: VertexOutput) -> @location(0) vec4<f32> {
    // Sample the pattern counts texture
    // Red channel: normalized pattern count (0.0 to 1.0)
    // Green channel: 1.0 if multiple patterns, 0.0 if single pattern
    let pattern_data = textureSampleLevel(pattern_counts_texture, pattern_counts_sampler, mesh.uv, 0.0);
    let normalized_pattern_count = pattern_data.r;
    let has_multiple_patterns = pattern_data.g;
    
    // Apply blur if this pixel has multiple possible patterns
    if (has_multiple_patterns > 0.5) {
        return gaussian_blur(grid_texture, grid_sampler, mesh.uv);
    } else {
        // Direct UV sampling from the grid texture for determined pixels
        return textureSampleLevel(grid_texture, grid_sampler, mesh.uv, 0.0);
    }
}