// simple simplex noise (c) Stefan Gustavson,
// version 2024-11-12, published under CC-BY-SA 4.0
// https://creativecommons.org/licenses/by-sa/4.0/

fn ssimplex(p: vec2<f32>) -> f32 {
    // Staggered grid, points at integer y and integer+half x
    // (Yields a slightly non-uniform triangular/hex grid.)
    let r0 = vec2<f32>(floor(p.x - p.y * 0.5), floor(p.y)); // Transform back to skewed space
    let r1 = floor(r0); // Tells us which grid quadrilateral contains p
    let r2 = r0 - r1; // Tells us which of the two triangles contains p
    let cmp = step(r2.y, r2.x); // Equivalent to r2.x>r2.y ? 1.0 : 0.0
    let r1a = r1 + vec2<f32>(cmp, 0.0); // r1a is the offset to the second corner
    let i1 = r1 + vec2<f32>(1.0, 1.0); // Grid coordinates, used for hash
    let p0 = vec2<f32>(r1.x + r1.y * 0.5, r1.y); // Transform back to p space
    let p1 = vec2<f32>(r1a.x + r1a.y * 0.5, r1a.y);
    let p2 = vec2<f32>(i1.x + i1.y * 0.5, i1.y);
    let v0 = p - p0; 
    let v1 = p - p1; 
    let v2 = p - p2; // Vectors from corners to p
    
    // Compute a simple hash for each of the three corners
    let h = vec3<f32>(r1.x % 289.0, r1a.x % 289.0, i1.x % 289.0); // Hash coords
    let g = vec3<f32>(r1.y, r1a.y, i1.y);
    var hash = ((h * 34.0 + 10.0) * h) % 289.0; // Mod to avoid truncations below
    
    hash = (hash * 51.0 + 2.0 * hash + g) % 289.0; // These are not great.
    hash = (hash * 34.0 + 10.0 * hash) % 289.0; // but "good enough"
    
    // Generate three gradients
    let gx = cos(hash); // sin and cos are usually fast these days
    let gy = sin(hash);
    let g0 = vec2<f32>(gx.x, gy.x); 
    let g1 = vec2<f32>(gx.y, gy.y); 
    let g2 = vec2<f32>(gx.z, gy.z);
    
    // Compute the kernels of influence from each corner
    var w = max(0.5 - vec3<f32>(dot(v0, v0), dot(v1, v1), dot(v2, v2)), vec3<f32>(0.0)); // radial decay
    w = max(w, vec3<f32>(0.0)); // Cut off the negative part
    
    let w2 = w * w; 
    let w4 = w2 * w2; // w^4 is our final radial weight
    let gdotv = vec3<f32>(dot(g0, v0), dot(g1, v1), dot(g2, v2)); // extrapolated ramps
    
    // Compute and sum up the three contributions in one go
    let n = dot(w4, gdotv);
    return n * 49.0; // Scale the value to span the range [-1, 1]
}

// Simplex Fractal Brownian Motion (FBM) function
fn simplex_fbm_2d(position: vec2<f32>, octaves: i32, persistence: f32, lacunarity: f32) -> f32 {
    var value = 0.0;
    var amplitude = 1.0;
    var frequency = 1.0;
    var pos = position;
    
    for (var i = 0; i < octaves; i++) {
        value += amplitude * ssimplex(pos * frequency);
        amplitude *= persistence;
        frequency *= lacunarity;
    }
    
    return value;
}

// Convenience function for simple Simplex noise without FBM
fn simplex_simple_2d(position: vec2<f32>) -> f32 {
    return ssimplex(position);
}
