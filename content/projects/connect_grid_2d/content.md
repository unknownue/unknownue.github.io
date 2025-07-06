+++
title = "Connect Grid 2D"
date = 2025-07-06
description = "2D grid-based puzzle game where players connect matching colored pairs by drawing paths"
draft = false

[taxonomies]
tags = ["wasm", "bevy", "rust", "puzzle", "game", "grid"]
+++

# Connect Grid 2D

A grid-based puzzle game where players connect matching colored pairs by drawing paths between them.

## Gameplay

- **Objective**: Connect all pairs of matching colored dots on the grid
- **Challenge**: Paths cannot cross each other
- **Strategy**: Plan your routes carefully to avoid blocking other connections

## Features

- **Interactive Grid**: Click and drag to draw connection paths
- **Color Matching**: Connect dots of the same color
- **Path Validation**: Real-time feedback on valid/invalid moves
- **Multiple Levels**: Progressive difficulty with larger grids

## Controls

- **Mouse**: Click on a colored dot and drag to create a path
- **Release**: Complete the connection on a matching colored dot
- **Clear**: Failed connections are automatically cleared

This puzzle game demonstrates pathfinding algorithms and interactive grid-based gameplay mechanics, providing a foundation for more complex puzzle games. 

{{ wasm_viewer(path="app.js", id="connect_grid_2d-demo") }} 

