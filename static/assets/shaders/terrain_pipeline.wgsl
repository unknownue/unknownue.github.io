//! Specialized shader for terrain rendering

#import bevy_pbr::{
    mesh_functions,
    view_transformations::position_world_to_clip
}

struct Vertex {
    @builtin(instance_index) instance_index: u32,
    @location(0) position: vec3<f32>,
    @location(1) normal: vec3<f32>,
    @location(2) uv: vec2<f32>,
};

struct VertexOutput {
    @builtin(position) clip_position: vec4<f32>,
    @location(0) world_position: vec4<f32>,
    @location(1) world_normal: vec3<f32>,
    @location(2) uv: vec2<f32>,
};

@vertex
fn vertex(vertex: Vertex) -> VertexOutput {
    var out: VertexOutput;
    
    // Transform positions from model to world space
    var world_from_local = mesh_functions::get_world_from_local(vertex.instance_index);
    out.world_position = mesh_functions::mesh_position_local_to_world(world_from_local, vec4(vertex.position, 1.0));
    out.clip_position = position_world_to_clip(out.world_position.xyz);
    
    // Transform normals
    out.world_normal = mesh_functions::mesh_normal_local_to_world(vertex.normal, vertex.instance_index);
    
    // Pass UVs to fragment shader
    out.uv = vertex.uv;
    
    return out;
}

@fragment
fn fragment(in: VertexOutput) -> @location(0) vec4<f32> {
    // Normalize the interpolated normal
    let normal = normalize(in.world_normal);
    
    // Simple terrain coloring based on height
    let height = in.world_position.y;
    
    // Base color is greenish (grass-like)
    var color = vec3<f32>(0.3, 0.7, 0.3);
    
    // Simple lighting based on normal
    let light_dir = normalize(vec3<f32>(0.5, 0.8, 0.2));
    let diffuse = max(dot(normal, light_dir), 0.2);
    
    // Apply lighting and return final color
    return vec4<f32>(color * diffuse, 1.0);
} 