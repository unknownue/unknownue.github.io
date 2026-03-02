#import bevy_sprite::mesh2d_vertex_output::VertexOutput

@group(2) @binding(0) var<uniform> blur_intensity: f32;
@group(2) @binding(1) var base_color_texture: texture_2d<f32>;
@group(2) @binding(2) var base_color_sampler: sampler;

// Gaussian blur implementation for uncertainty visualization
fn gaussian_blur(uv: vec2<f32>, blur_size: f32) -> vec4<f32> {
    let texel_size = 1.0 / vec2<f32>(textureDimensions(base_color_texture));
    var color = vec4<f32>(0.0);
    var total_weight = 0.0;
    
    // 5x5 Gaussian kernel for better blur quality
    for (var x = -2; x <= 2; x++) {
        for (var y = -2; y <= 2; y++) {
            let offset = vec2<f32>(f32(x), f32(y)) * texel_size * blur_size;
            let sample_uv = uv + offset;
            
            // Gaussian weight calculation
            let distance_sq = f32(x * x + y * y);
            let weight = exp(-0.5 * distance_sq / (blur_size * blur_size + 0.1));
            
            color += textureSample(base_color_texture, base_color_sampler, sample_uv) * weight;
            total_weight += weight;
        }
    }
    
    return color / total_weight;
}

@fragment
fn fragment(mesh: VertexOutput) -> @location(0) vec4<f32> {
    if (blur_intensity > 0.0) {
        return gaussian_blur(mesh.uv, blur_intensity);
    } else {
        // No blur, return original texture
        return textureSample(base_color_texture, base_color_sampler, mesh.uv);
    }
} 