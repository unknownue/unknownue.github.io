+++
title = "Pattern - Noise"
date = 2025-07-06
description = "Noise Pattern with shader"
draft = false

[taxonomies]
tags = ["wasm", "bevy", "rust", "pattern", "shader", "graphics"]
+++

# Noise Pattern Generator

A shader-based noise pattern generation demo showcasing organic procedural graphics techniques using various noise algorithms.

## Features

Creates organic noise-based patterns using advanced noise algorithms:

- **Perlin Noise**: Classic Perlin noise with customizable parameters
- **Simplex Noise**: Modern simplex noise implementations
- **Layered Noise**: Multiple noise layers for complex textures
- **Animated Effects**: Time-based noise animation
- **Fractal Patterns**: Multi-octave noise for detailed textures

## Noise Algorithms

- **Perlin Noise Variations**: Different implementations and parameters
- **Simplex Noise**: Improved gradient noise with better visual quality
- **Fractal Brownian Motion**: Layered noise for natural-looking patterns
- **Turbulence**: Absolute value operations for different texture types

## Technical Implementation

- **GPU-accelerated**: All noise generated on GPU using WGSL shaders
- **Multiple Algorithms**: Various noise functions for comparison
- **Real-time Animation**: Time-based parameter updates
- **Procedural Generation**: Mathematical noise without texture assets

## Controls

- Switch between different noise algorithms
- Adjust noise parameters like frequency and amplitude
- Control animation speed and direction
- Modify color mapping and visualization

This demo provides educational examples of noise-based procedural generation and demonstrates how different noise algorithms can create diverse organic patterns and textures. 

{{ wasm_viewer(path="app.js", id="pattern_noise-demo") }} 

