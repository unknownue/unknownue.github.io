// GLSL classic 2D gradient noise ("Perlin noise")
// Copyright (c) 2011, 2024 Stefan Gustavson
// with thanks to Ian McEwan for several details.
// Distributed under the permissive MIT license:
// https://github.com/stegu/webgl-noise
// Please give credit, and please keep this header.

// Different permutation polynomials for x and y to avoid artifacts
fn mod289_vec4(x: vec4<f32>) -> vec4<f32> {
    return x - floor(x * (1.0 / 289.0)) * 289.0;
}

fn mod289_vec2(x: vec2<f32>) -> vec2<f32> {
    return x - floor(x * (1.0 / 289.0)) * 289.0;
}

fn permute_vec4(x: vec4<f32>) -> vec4<f32> {
    return mod289_vec4(((x * 34.0) + 10.0) * x);
}

// A fifth degree interpolating function to replace the cubic interpolation
fn fade_vec2(t: vec2<f32>) -> vec2<f32> {
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0); // Better than (3.0-2.0*t)*t*t
}

// Classic 2-D "Perlin" noise
// Returns noise value in range [-1, 1]
fn perlin_noise_2d(P: vec2<f32>) -> f32 {
    var Pi = floor(P);
    let Pf = fract(P);
    
    // Four choice(vec2 P) {
    let vec4_h = permute_vec4(permute_vec4(vec4<f32>(Pi.x, Pi.x, Pi.x + 1.0, Pi.x + 1.0)) + vec4<f32>(Pi.y, Pi.y + 1.0, Pi.y, Pi.y + 1.0));
    
    // Pi = mod(Pi, 289.0); // avoids truncation in the hash function
    Pi = mod289_vec2(Pi);
    
    // Gradients are generated as points along a diamond shape
    let gx = fract(vec4_h * (1.0 / 41.0)) * 2.0 - 1.0;
    let gy = abs(gx) - 0.5;
    let tx = floor(gx + 0.5);
    let gx_final = gx - tx;
    
    // Rearrange components to create the four gradients
    let g00 = vec2<f32>(gx_final.x, gy.x);
    let g10 = vec2<f32>(gx_final.y, gy.y);
    let g01 = vec2<f32>(gx_final.z, gy.z);
    let g11 = vec2<f32>(gx_final.w, gy.w);
    
    // Factors to scale gradients to equal lengths
    let norm = inverseSqrt(vec4<f32>(dot(g00, g00), dot(g01, g01), dot(g10, g10), dot(g11, g11)));
    let g00_norm = g00 * norm.x;
    let g01_norm = g01 * norm.y;
    let g10_norm = g10 * norm.z;
    let g11_norm = g11 * norm.w;
    
    // Extrapolated contributions from each corner
    let n00 = dot(g00_norm, vec2<f32>(Pf.x, Pf.y));
    let n10 = dot(g10_norm, vec2<f32>(Pf.x - 1.0, Pf.y));
    let n01 = dot(g01_norm, vec2<f32>(Pf.x, Pf.y - 1.0));
    let n11 = dot(g11_norm, vec2<f32>(Pf.x - 1.0, Pf.y - 1.0));
    
    // Successive interpolations, first along x, then along y
    let fade_xy = fade_vec2(Pf);
    let n_x = mix(vec2<f32>(n00, n01), vec2<f32>(n10, n11), fade_xy.x);
    let n = mix(n_x.x, n_x.y, fade_xy.y);
    
    // Empirical factor to scale output to [-1,1]
    return 1.5876 * n;
}

// Fractal Brownian Motion (FBM) - multiple octaves of Perlin noise
// Parameters:
//   position: 2D coordinate
//   octaves: number of noise layers to combine
//   persistence: amplitude reduction factor for each octave (typically 0.5)
//   lacunarity: frequency increase factor for each octave (typically 2.0)
fn perlin_fbm_2d(position: vec2<f32>, octaves: i32, persistence: f32, lacunarity: f32) -> f32 {
    var value = 0.0;
    var amplitude = 1.0;
    var frequency = 1.0;
    var pos = position;
    
    for (var i = 0; i < octaves; i++) {
        value += amplitude * perlin_noise_2d(pos * frequency);
        amplitude *= persistence;
        frequency *= lacunarity;
    }
    
    return value;
}

// Convenience function for simple Perlin noise without FBM
fn perlin_simple_2d(position: vec2<f32>) -> f32 {
    return perlin_noise_2d(position);
}

// Hash function for pseudo-random number generation (alternative implementation)
fn hash_2d(p: vec2<f32>) -> f32 {
    var h = dot(p, vec2<f32>(127.1, 311.7));
    return fract(sin(h) * 43758.5453123);
}

// Simple noise function using hash (alternative implementation, lower quality)
fn simple_noise_2d(p: vec2<f32>) -> f32 {
    let i = floor(p);
    let f = fract(p);
    
    // Four corners of the unit square
    let a = hash_2d(i);
    let b = hash_2d(i + vec2<f32>(1.0, 0.0));
    let c = hash_2d(i + vec2<f32>(0.0, 1.0));
    let d = hash_2d(i + vec2<f32>(1.0, 1.0));
    
    // Smooth interpolation using smoothstep
    let u = f * f * (3.0 - 2.0 * f);
    
    // Bilinear interpolation
    return mix(
        mix(a, b, u.x),
        mix(c, d, u.x),
        u.y
    );
}
