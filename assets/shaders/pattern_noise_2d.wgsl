#import bevy_sprite::mesh2d_vertex_output::VertexOutput
#import bevy_render::globals::Globals
#import "shaders/lib/perlin_noise.wgsl"::{perlin_fbm_2d, perlin_simple_2d}
#import "shaders/lib/simplex_noise.wgsl"::{simplex_fbm_2d, simplex_simple_2d}
#import "shaders/lib/psrdnoise2.wgsl"::{psrdnoise2, NG2}

// Noise parameters uniform buffer
struct NoiseParams {
    scale: f32,
    octaves: f32,
    persistence: f32,
    lacunarity: f32,
    noise_type: f32, // 0.0 = Perlin Simple, 1.0 = Perlin FBM, 2.0 = Simplex Simple, 3.0 = Simplex FBM, 4.0 = psrdnoise2
    period_x: f32,   // Period for psrdnoise2 x-axis
    period_y: f32,   // Period for psrdnoise2 y-axis
    rotation: f32,   // Rotation angle for psrdnoise2
}

@group(0) @binding(1) var<uniform> globals: Globals;
@group(2) @binding(0) var<uniform> params: NoiseParams;

// Combined noise function that can switch between different noise types
fn get_noise_value(p: vec2<f32>) -> f32 {
    let noise_type_int = i32(params.noise_type);
    
    switch (noise_type_int) {
        case 0: {
            // Perlin Simple
            return perlin_simple_2d(p);
        }
        case 1: {
            // Perlin FBM
            return perlin_fbm_2d(p, i32(params.octaves), params.persistence, params.lacunarity);
        }
        case 2: {
            // Simplex Simple
            return simplex_simple_2d(p);
        }
        case 3: {
            // Simplex FBM
            return simplex_fbm_2d(p, i32(params.octaves), params.persistence, params.lacunarity);
        }
        case 4: {
            // psrdnoise2 - Periodic rotational derivative noise
            let period = vec2<f32>(params.period_x, params.period_y);
            let noise_stats = psrdnoise2(p, period, params.rotation);
            return noise_stats.noise;
        }
        default: {
            // Default to Perlin Simple
            return perlin_simple_2d(p);
        }
    }
}

// Color mapping function for noise visualization
fn noise_to_color(noise_val: f32) -> vec3<f32> {
    let n = (noise_val + 1.0) * 0.5; // Normalize to [0, 1]
    
    // Create a color gradient from dark blue to bright yellow
    if (n < 0.25) {
        // Dark blue to blue
        return mix(vec3<f32>(0.0, 0.0, 0.2), vec3<f32>(0.0, 0.0, 1.0), n * 4.0);
    } else if (n < 0.5) {
        // Blue to cyan
        return mix(vec3<f32>(0.0, 0.0, 1.0), vec3<f32>(0.0, 1.0, 1.0), (n - 0.25) * 4.0);
    } else if (n < 0.75) {
        // Cyan to green
        return mix(vec3<f32>(0.0, 1.0, 1.0), vec3<f32>(0.0, 1.0, 0.0), (n - 0.5) * 4.0);
    } else {
        // Green to yellow
        return mix(vec3<f32>(0.0, 1.0, 0.0), vec3<f32>(1.0, 1.0, 0.0), (n - 0.75) * 4.0);
    }
}

@fragment
fn fragment(mesh: VertexOutput) -> @location(0) vec4<f32> {
    // Get UV coordinates
    let uv = mesh.uv;
    
    // Center the coordinates and apply scale
    let pos = (uv - 0.5) * params.scale;
    
    // Add time-based animation
    let animated_pos = pos + vec2<f32>(globals.time * 0.1, globals.time * 0.07);
    
    // Generate noise using selected noise type
    let noise_value = get_noise_value(animated_pos);
    
    // Convert noise to color
    let color = noise_to_color(noise_value);
    
    return vec4<f32>(color, 1.0);
}