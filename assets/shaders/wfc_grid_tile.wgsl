#import bevy_sprite::mesh2d_vertex_output::VertexOutput

@group(2) @binding(0) var atlas_texture: texture_2d<f32>;
@group(2) @binding(1) var atlas_sampler: sampler;
@group(2) @binding(2) var tile_indices_texture: texture_2d<u32>;
@group(2) @binding(3) var tile_indices_sampler: sampler;

struct GridTileUniforms {
    atlas_size: vec4<f32>,
    tile_size: vec4<f32>,
    grid_size: vec4<f32>,
}

@group(2) @binding(4) var<uniform> uniforms: GridTileUniforms;

// Structure to hold blend result
struct BlendResult {
    color: vec4<f32>,
    total_weight: f32,
}

// Generate a pseudo-random number based on seed (deterministic)
fn random(seed: vec2<f32>) -> f32 {
    return fract(sin(dot(seed, vec2<f32>(12.9898, 78.233))) * 43758.5453);
}

// Calculate Gaussian weight based on distance
fn gaussian_weight(distance_sq: f32, sigma: f32) -> f32 {
    return exp(-distance_sq / (2.0 * sigma * sigma));
}

// Calculate neighbor weight based on position type
fn neighbor_weight(offset_index: i32) -> f32 {
    if (offset_index < 4) {
        // Direct neighbors (up, down, left, right) get higher weight
        return 1.5;
    } else {
        // Diagonal neighbors get lower weight
        return 1.0;
    }
}

// Apply rotation transformation to UV coordinates
fn apply_rotation(uv: vec2<f32>, rotation: u32) -> vec2<f32> {
    var rotated_uv = uv;
    
    // Apply rotation based on orientation value (0-7 for different rotations/reflections)
    switch (rotation) {
        case 0u: {
            // No rotation
            rotated_uv = uv;
        }
        case 1u: {
            // 90° counter-clockwise rotation
            rotated_uv = vec2<f32>(1.0 - uv.y, uv.x);
        }
        case 2u: {
            // 180° rotation
            rotated_uv = vec2<f32>(1.0 - uv.x, 1.0 - uv.y);
        }
        case 3u: {
            // 270° counter-clockwise rotation (90° clockwise)
            rotated_uv = vec2<f32>(uv.y, 1.0 - uv.x);
        }
        case 4u: {
            // Horizontal reflection
            rotated_uv = vec2<f32>(1.0 - uv.x, uv.y);
        }
        case 5u: {
            // Horizontal reflection + 90° rotation
            rotated_uv = vec2<f32>(1.0 - uv.y, 1.0 - uv.x);
        }
        case 6u: {
            // Horizontal reflection + 180° rotation
            rotated_uv = vec2<f32>(uv.x, 1.0 - uv.y);
        }
        case 7u: {
            // Horizontal reflection + 270° rotation
            rotated_uv = vec2<f32>(uv.y, uv.x);
        }
        default: {
            rotated_uv = uv;
        }
    }
    
    return rotated_uv;
}

// Sample a tile texture at given tile index and orientation with local UV
fn sample_tile_by_index(tile_index: u32, orientation: u32, local_uv: vec2<f32>) -> vec4<f32> {
    // Calculate atlas coordinates for this tile
    let tiles_per_row = uniforms.atlas_size.x / uniforms.tile_size.x;
    let tile_row = floor(f32(tile_index) / tiles_per_row);
    let tile_col = f32(tile_index) - (tile_row * tiles_per_row);
    
    // Apply rotation transformation to the local UV coordinates
    let rotated_uv = apply_rotation(local_uv, orientation);
    
    // Calculate UV coordinates in the atlas texture
    let atlas_tile_start = vec2<f32>(tile_col, tile_row) * uniforms.tile_size.xy;
    let atlas_uv = (atlas_tile_start + rotated_uv * uniforms.tile_size.xy) / uniforms.atlas_size.xy;
    
    // Sample from the atlas texture
    return textureSampleLevel(atlas_texture, atlas_sampler, atlas_uv, 0.0);
}

// Check if coordinates are within grid bounds
fn is_in_bounds(coords: vec2<f32>) -> bool {
    return coords.x >= 0.0 && coords.x < uniforms.grid_size.x &&
           coords.y >= 0.0 && coords.y < uniforms.grid_size.y;
}

// Check if a tile at given coordinates is determined (not 255)
fn is_tile_determined(tile_coords: vec2<f32>) -> bool {
    if (!is_in_bounds(tile_coords)) {
        return false;
    }
    let tile_pixel_coords = vec2<i32>(i32(tile_coords.x), i32(tile_coords.y));
    let tile_data = textureLoad(tile_indices_texture, tile_pixel_coords, 0);
    return tile_data.r != 255;
}

// Get tile data at given coordinates
fn get_tile_data(tile_coords: vec2<f32>) -> vec4<u32> {
    let tile_pixel_coords = vec2<i32>(i32(tile_coords.x), i32(tile_coords.y));
    return textureLoad(tile_indices_texture, tile_pixel_coords, 0);
}

// Get a deterministic random tile for a specific position
fn get_deterministic_random_tile(tile_coords: vec2<f32>) -> u32 {
    // Use tile coordinates as deterministic seed to ensure same tile is always chosen for same position
    let max_tiles = (uniforms.atlas_size.x / uniforms.tile_size.x) * (uniforms.atlas_size.y / uniforms.tile_size.y);
    let seed = tile_coords * 1000.0; // Scale up coordinates for better distribution
    let random_value = random(seed);
    return u32(random_value * max_tiles) % u32(max_tiles);
}

// Sample tile color at given coordinates (either determined or random)
fn sample_tile_at_coords(coords: vec2<f32>, local_uv: vec2<f32>, use_random: bool) -> vec4<f32> {
    if (!use_random && is_tile_determined(coords)) {
        let tile_data = get_tile_data(coords);
        return sample_tile_by_index(tile_data.r, tile_data.g, local_uv);
    } else {
        let random_tile_index = get_deterministic_random_tile(coords);
        return sample_tile_by_index(random_tile_index, 0u, local_uv);
    }
}

// Blend colors using direct neighbor sampling (8-connected)
fn blend_direct_neighbors(center_coords: vec2<f32>, local_uv: vec2<f32>) -> BlendResult {
    var blended_color = vec4<f32>(0.0, 0.0, 0.0, 0.0);
    var total_weight = 0.0;
    
    // Define neighbor offsets (8-connected neighborhood)
    let neighbor_offsets = array<vec2<f32>, 8>(
        vec2<f32>(-1.0, -1.0), vec2<f32>(0.0, -1.0), vec2<f32>(1.0, -1.0),
        vec2<f32>(-1.0,  0.0),                        vec2<f32>(1.0,  0.0),
        vec2<f32>(-1.0,  1.0), vec2<f32>(0.0,  1.0), vec2<f32>(1.0,  1.0)
    );
    
    // Sample from neighboring tiles and blend their textures
    for (var i = 0; i < 8; i++) {
        let neighbor_coords = center_coords + neighbor_offsets[i];
        
        if (is_in_bounds(neighbor_coords) && is_tile_determined(neighbor_coords)) {
            let neighbor_data = get_tile_data(neighbor_coords);
            let neighbor_color = sample_tile_by_index(neighbor_data.r, neighbor_data.g, local_uv);
            let weight = neighbor_weight(i);
            
            blended_color += neighbor_color * weight;
            total_weight += weight;
        }
    }
    
    return BlendResult(blended_color, total_weight);
}

// Blend colors using Gaussian sampling within radius
fn blend_gaussian_radius(center_coords: vec2<f32>, local_uv: vec2<f32>, radius: i32, sigma: f32, use_random: bool) -> BlendResult {
    var blended_color = vec4<f32>(0.0, 0.0, 0.0, 0.0);
    var total_weight = 0.0;
    
    // Apply Gaussian blur using tiles in (2*radius+1)x(2*radius+1) grid centered on current tile
    for (var dy = -radius; dy <= radius; dy++) {
        for (var dx = -radius; dx <= radius; dx++) {
            let sample_coords = center_coords + vec2<f32>(f32(dx), f32(dy));
            
            // Calculate Gaussian weight based on distance from center
            let distance_sq = f32(dx * dx + dy * dy);
            let weight = gaussian_weight(distance_sq, sigma);
            
            let sample_color = sample_tile_at_coords(sample_coords, local_uv, use_random);
            
            blended_color += sample_color * weight;
            total_weight += weight;
        }
    }
    
    return BlendResult(blended_color, total_weight);
}

// Finalize blend result with normalization and transparency
fn finalize_blend(blend_result: BlendResult, alpha_multiplier: f32) -> vec4<f32> {
    var final_color = blend_result.color;
    
    if (blend_result.total_weight > 0.0) {
        final_color = final_color / blend_result.total_weight;
    }
    
    final_color.a = final_color.a * alpha_multiplier;
    return final_color;
}

@fragment
fn fragment(mesh: VertexOutput) -> @location(0) vec4<f32> {
    // Calculate which tile we're in based on UV coordinates
    let grid_uv = mesh.uv * uniforms.grid_size.xy;
    let tile_coords = floor(grid_uv);
    let tile_local_uv = fract(grid_uv);
    
    // Get current tile data
    let current_tile_data = get_tile_data(tile_coords);
    
    // If tile is determined, render normally
    if current_tile_data.r != 255 {
        return sample_tile_by_index(current_tile_data.r, current_tile_data.g, tile_local_uv);
    }
    
    // Tile is uncollapsed - try blending with determined neighbors first
    let neighbor_blend = blend_direct_neighbors(tile_coords, tile_local_uv);
    
    if (neighbor_blend.total_weight > 0.0) {
        // We have determined neighbors, use them for blending
        return finalize_blend(neighbor_blend, 0.7);
    }
    
    // No determined neighbors - use Gaussian blur on random tiles
    let gaussian_blend = blend_gaussian_radius(tile_coords, tile_local_uv, 2, 1.0, true);
    return finalize_blend(gaussian_blend, 0.5);
}