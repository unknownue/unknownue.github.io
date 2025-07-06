+++
title = "Pattern - Grid"
date = 2025-07-06
description = "Grid Pattern with shader"
draft = false

[taxonomies]
tags = ["wasm", "bevy", "rust", "pattern", "shader", "graphics"]
+++

# Grid Pattern Generator

A shader-based grid pattern generation demo showcasing geometric procedural graphics techniques.

## Features

Generates customizable geometric grid patterns using fragment shaders:

- **Grid Spacing**: Adjustable spacing between grid lines
- **Line Thickness**: Variable thickness for grid lines
- **Color Schemes**: Multiple color palettes and gradients
- **Real-time Controls**: Interactive parameter modification
- **Pattern Variations**: Different grid styles and layouts

## Technical Implementation

- **GPU-accelerated**: All patterns generated on GPU using WGSL shaders
- **Fragment Shader**: Procedural grid generation in screen space
- **Mathematical Patterns**: Pure algorithmic pattern creation without textures
- **Real-time Performance**: Smooth interactive parameter updates

## Controls

- Adjust grid parameters through the interface
- Experiment with different color schemes
- Modify spacing and thickness in real-time

This demo serves as an educational example for geometric shader programming and demonstrates how simple mathematical functions can create complex visual patterns. 

{{ wasm_viewer(path="app.js", id="pattern_grid-demo") }} 

