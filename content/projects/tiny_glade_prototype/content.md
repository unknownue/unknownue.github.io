+++
title = "Prototype of tiny glade game"
date = 2025-07-06
description = "Prototype implemention of tiny glade game"
draft = false

[taxonomies]
tags = ["wasm", "bevy", "rust", "game", "prototype", "simulation"]
+++

# Tiny Glade Prototype

A prototype implementation inspired by the charming aesthetics and mechanics of Tiny Glade, focusing on peaceful building and landscape creation.

## Features

- **Curve-based Building**: Draw smooth curves that transform into structures
- **Procedural Generation**: Automatic detail generation based on user input
- **Peaceful Gameplay**: Relaxing, non-competitive building experience
- **Organic Aesthetics**: Natural-looking structures and landscapes

## Gameplay Mechanics

- **Curve Drawing**: Click and drag to create curved paths
- **Automatic Structures**: Curves automatically generate walls, paths, or fences
- **Landscape Integration**: Buildings blend naturally with the terrain
- **Iterative Design**: Modify and refine your creations continuously

## Technical Implementation

- **Bezier Curves**: Smooth curve generation and manipulation
- **Procedural Mesh**: Dynamic geometry creation from curve data
- **Shader Effects**: Stylized rendering for aesthetic appeal
- **Real-time Updates**: Instant feedback on design changes

## Controls

- **Mouse**: Click and drag to draw curves
- **Modify**: Adjust existing curves by dragging control points
- **Build**: Watch structures automatically form from your curves

This prototype explores the intersection of creativity and technology, demonstrating how simple user input can generate complex, beautiful structures through procedural algorithms.


{{ wasm_viewer(path="app.js", id="tiny_glade_prototype-demo") }} 

