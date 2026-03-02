struct PaintUniforms {
    mouse_position: vec3<f32>,
    is_additive: i32,
    canvas_ws_dims: vec2<f32>,
}

@group(0) @binding(0) var img_output: texture_storage_2d<rgba32float, read_write>;

@group(0) @binding(1) var<uniform> uniforms: PaintUniforms;

const BRUSH_SIZE_DEFAULT: f32 = 0.45;
const BRUSH_SIZE_MULTIPLIER: f32 = 0.75 * 0.9;

@compute @workgroup_size(1, 1, 1)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
    var BRUSH_SIZE: f32 = BRUSH_SIZE_DEFAULT;
    var is_additive: bool = uniforms.is_additive > 0;

    if (!is_additive) {
        BRUSH_SIZE = BRUSH_SIZE_MULTIPLIER;
    }

    let pixel_coords = vec2<i32>(global_id.xy);
    let dims = textureDimensions(img_output);

    var pixel = textureLoad(img_output, pixel_coords);

    let x = (f32(pixel_coords.x) * 2.0 - f32(dims.x)) / f32(dims.x);
    let y = (f32(pixel_coords.y) * 2.0 - f32(dims.y)) / f32(dims.y);

    let pixel_ws = vec3<f32>(x * uniforms.canvas_ws_dims.x / 2.0, 0.0, y * uniforms.canvas_ws_dims.y / 2.0);

    var d = distance(pixel_ws, uniforms.mouse_position);
    d = clamp(d, 0.0, BRUSH_SIZE);
    d = (BRUSH_SIZE - d) / BRUSH_SIZE;

    if (d > 0.0) {
        d = 1.0;
    } else {
        d = 0.0;
    }

    if (is_additive) {
        pixel = max(pixel, vec4<f32>(d, d, d, 1.0));
    } else {
        let v = max(pixel.x - d, 0.0);
        pixel = vec4<f32>(v, v, v, 1.0);
    }

    textureStore(img_output, pixel_coords, pixel);
}
