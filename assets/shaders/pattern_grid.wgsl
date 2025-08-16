#import bevy_sprite::mesh2d_vertex_output::VertexOutput

// Material uniforms
@group(2) @binding(0) var<uniform> color_a: vec4<f32>;
@group(2) @binding(1) var<uniform> color_b: vec4<f32>;
@group(2) @binding(2) var<uniform> scale: f32;

// The mod function correctly defined in terms of the fract function
fn cmod(x: f32, a: f32) -> f32 {
    return a * fract(x / a);
}

// Anti-aliased step function
fn aastep(edge: f32, value: f32) -> f32 {
    let w = fwidth(value) * 0.5;
    return 1.0 - smoothstep(edge - w, edge + w, value);
}

// Checkerboard pattern function
fn checkerboard(p: vec2<f32>) -> f32 {
    let steps = floor(p.x) + floor(p.y); // Stair-steps, integer-valued
    return cmod(steps, 2.0); // Wraps all integers to only 0.0 and 1.0
}

// Antialiased version of checkerboard pattern
fn aacheckers(p: vec2<f32>) -> f32 {
    let ramps = 2.0 * abs(fract(p) - 0.5); // "Triangle waves" in x & y
    let stripes = step(vec2<f32>(0.5, 0.5), ramps); // 50% stripes
    return abs(stripes.x - stripes.y); // "XOR" at overlaps, preserving AA
}

// Polka-dots pattern function
fn polka_dots(p: vec2<f32>) -> f32 {
    // Center each cell at (0.5, 0.5)
    let cell_pos = fract(p) - 0.5;
    // Calculate distance from center of each cell
    let distance = length(cell_pos);
    // Create circular dots with radius of 0.3
    return step(distance, 0.3);
}

// Gridlines pattern function
fn gridlines(p: vec2<f32>) -> f32 {
    let q = fract(p); // Square grid of size 1x1
    let grid_x = step(0.9, q.x); // Threshold x
    let grid_y = step(0.9, q.y); // Threshold y
    return max(grid_x, grid_y); // Overlay the two
}

// A pattern of (x,y) grid lines, done right
fn aagridlines(p: vec2<f32>) -> f32 {
    let ramps = 2.0 * abs(fract(p) - 0.5); // "Triangle waves" in x and y
    let lines_x = aastep(0.55, ramps.x) - aastep(0.45, ramps.x); // 0.1 wide in x
    let lines_y = aastep(0.55, ramps.y) - aastep(0.45, ramps.y); // 0.1 wide in y
    return max(lines_x, lines_y); // Overlap the two sets of lines
}

fn bricks(p: vec2<f32>) -> f32 {
    let q = fract(p + vec2<f32>(0.5 * floor(p.y), 0.0)); // Staggered grid
    let brickx = step(0.05, q.x) - step(0.95, q.x); // vertical gaps
    let bricky = step(0.05, q.y) - step(0.95, q.y); // horizontal gaps
    return min(brickx, bricky); // If either is 0, return 0
}

fn aa_bricks(p: vec2<f32>) -> f32 {
    var q = fract(p + vec2<f32>(0.5 * floor(p.y), 0.0)); // Staggered grid
    q = 2.0 * abs(q - 0.5); // Change from sawtooth to triangle
    let brickx = 1.0 - step(0.90, q.x); // vertical gaps at both sides
    let bricky = 1.0 - step(0.90, q.y); // horizontal gaps at top and bottom
    
    return min(brickx, bricky); // If either is 0, return 0
}

// Find the closest point from p in a hexagonal grid.
// The grid is not quite regular. Scale p,y by 2.0/sqrt(3.0) before the function call if you prefer a regular hex grid, with grid points at pesky irrational coordinates in y.
fn hextiling(p: vec2<f32>) -> vec2<f32> {
    // Lower left vertex p0 of local integer-aligned 1x2 rectangular cell
    let p0 = vec2<f32>(floor(p.x), 2.0 * floor(p.y * 0.5));
    // Midpoint p4 of that cell
    let p4 = p0 + vec2<f32>(0.5, 1.0);
    // Vector from midpoint to p (local cell coordinates)
    let v4 = p - p4;
    // Set px to the closest corner, based on signs of v4.x and v4.y
    let dx = vec2<f32>(select(0.5, -0.5, v4.x < 0.0), select(1.0, -1.0, v4.y < 0.0));
    let px = p4 + dx;
    let vx = p - px; // Vector from corner to p (also: vx = v4 - dx)
    // Determine whether the corner px or the center p4 is closer.
    // The vector ex is the normal to the decision boundary.
    let ex = vec2<f32>(select(2.0/3.0, -2.0/3.0, v4.x < 0.0), dx.y);
    // Use the line equation for points half-way between p4 and px
    let d = dot(v4, ex) - 2.0/3.0; // If d is negative, p4 is closer
    // Return the closest grid point
    return select(px, p4, d < 0.0);
}

// Polka-dot pattern in a hexagonal tiling.
// The range of R is 0.0 (no dots) to 2.0/3.0 (dots cover the plane).
// The dots will start to overlap if R>0.5.
fn hexpolkadots(p: vec2<f32>, R: f32) -> f32 {
    // Compute the distance to the nearest gridpoint of a hexagonal grid, and create a circle around it
    return 1.0 - step(R, length(p - hextiling(p)));
}

@fragment
fn fragment(mesh: VertexOutput) -> @location(0) vec4<f32> {
    let scaled_uv = mesh.uv * scale;
    
    // Use shader defines to select pattern at compile time
#ifdef POLKA_DOTS
    let pattern_value = polka_dots(scaled_uv);
#endif

#ifdef AA_CHECKERS
    // let pattern_value = aacheckers((scaled_uv + 0.5) * 0.5);
    let pattern_value = aacheckers(scaled_uv);
#endif

#ifdef CHECKERBOARD
    let pattern_value = checkerboard(scaled_uv);
#endif

#ifdef GRIDLINES
    let pattern_value = gridlines(scaled_uv);
#endif

#ifdef AAGRIDLINES
    // let pattern_value = aagridlines(scaled_uv);
    let pattern_value = aagridlines(scaled_uv* 0.5);
#endif

#ifdef BRICKS
    let pattern_value = bricks(scaled_uv);
#endif

#ifdef AA_BRICKS
    let pattern_value = aa_bricks(scaled_uv);
#endif

#ifdef HEXTILING
    let pattern_value = hexpolkadots(scaled_uv, 0.2);
#endif
    
    return mix(color_a, color_b, pattern_value);
}
