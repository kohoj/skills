# Particle Effects Terminology Dictionary

Complete terminology reference for particle systems. Use this when you need the precise English
term for a concept, or when you encounter casual descriptions that need to be translated to
technical language.

## Table of Contents

1. [Particle System Basics](#particle-system-basics)
2. [Motion & Physics](#motion--physics)
3. [Rendering & Visual](#rendering--visual)
4. [Noise Types](#noise-types)

---

## Particle System Basics

| Casual Description | Technical Term | English | Definition |
|---|---|---|---|
| Where particles come from | Emitter | Emitter | The spawn point — can be a point, line, surface, or volume |
| How long particles live | Lifetime / TTL | Lifetime / Time To Live | Duration from birth to death |
| How fast particles spawn | Emission Rate | Emission Rate | Number of particles generated per second |
| Particles fade out | Alpha Decay | Alpha Fade / Decay | Opacity decreases over time until fully transparent |
| Particles grow/shrink | Size Curve | Size over Lifetime | Size changes along a curve over the particle's lifespan |
| Particles change color | Color Ramp | Color over Lifetime / Color Ramp | Color shifts along a gradient over the particle's lifespan |
| Particles glow when overlapping | Additive Blend | Additive Blending | Colors add rather than occlude — produces a luminous glow |
| External forces on particles | Force Field | Force Field | External forces applied to particles (gravity, wind, attraction) |
| Particles leave a trail | Motion Trail | Motion Trail / Ribbon Trail | Residual trace along the particle's trajectory |
| Huge particle counts, still smooth | GPU Particles | GPU Particles / GPGPU | Positions computed on GPU — supports 10K to millions |

## Motion & Physics

| Casual Description | Technical Term | English | Definition |
|---|---|---|---|
| Flows like smoke | Curl Noise | Curl Noise | Divergence-free noise field — particles follow streamlines for natural smoke/fluid look |
| Flows like water | Flow Field | Flow Field / Vector Field | Each point in space has a velocity vector; particles follow it |
| Attracted to a point | Attractor | Attractor / Gravity Well | A point that pulls particles — closer = stronger |
| Random jitter | Noise Perturbation | Brownian Motion / Noise Perturbation | Random noise layered on top of particle motion |
| Spiraling motion | Vortex | Vortex | Rotational force that spins particles around a center |
| Spring-back to position | Spring Force | Spring Force / Elastic | Particles snap back to a target position after displacement |
| Bounces off walls | Collision | Collision / Boundary Check | Particles bounce or die when hitting a boundary |
| Gradually slows down | Damping | Damping / Friction | Velocity multiplied by a factor < 1 each frame — gradual deceleration |
| Chaotic butterfly paths | Strange Attractor | Strange Attractor (Lorenz, Aizawa...) | Chaotic system trajectories — unpredictable but structurally beautiful |
| Momentum-based movement | Integration | Velocity Integration / Verlet | Position updated from velocity, velocity updated from acceleration |

## Rendering & Visual

| Casual Description | Technical Term | English | Definition |
|---|---|---|---|
| Particles glow | Bloom | Bloom / Unreal Bloom | Post-processing that bleeds bright areas into soft light |
| Soft round particles | Point Sprite | Point Sprite / gl_PointSize | GPU-rendered circular particles — best performance |
| Custom image particles | Textured Particle | Textured Particle / Sprite Sheet | Images replace simple dots |
| Background blur | DOF | Depth of Field (DOF) | Distant particles blur based on depth |
| Many identical 3D shapes | Instancing | InstancedMesh / Instancing | Single draw call renders thousands of identical geometries |
| GPU-computed positions | Compute Shader | Compute Shader / FBO (Framebuffer Object) | GPU computes particle physics — WebGL uses FBO trick, WebGPU uses native compute |
| Lines between nearby particles | Proximity Lines | Proximity Lines / Connection Lines | Lines drawn between particles within a distance threshold |
| Color encodes data | Color Mapping | Color Mapping / Heat Map | Values (speed, density, etc.) mapped to a color gradient |

## Noise Types

Noise is the foundation of organic-looking particle motion. Choosing the wrong noise type is the
most common reason particle effects look "off" or mechanical.

| Noise | English | Visual Character | Best For | Performance |
|---|---|---|---|---|
| Perlin Noise | Perlin Noise | Smooth continuous random undulation | Terrain, clouds, organic motion | Good |
| Simplex Noise | Simplex Noise | Similar to Perlin but faster, no directional bias | Large-scale particle fields, flow fields | Better than Perlin |
| Curl Noise | Curl Noise | Divergence-free, follows streamlines | Smoke, fluid, dreamy drift | Moderate (requires gradient computation) |
| Bitangent Noise | Bitangent Noise | Similar to curl but cheaper to compute | High-performance curl noise alternative | Better than curl |
| FBM | FBM (Fractal Brownian Motion) | Multi-octave layered richness | Fire, clouds, complex organic textures | Expensive (multiple noise calls) |
| Worley Noise | Worley / Voronoi Noise | Cellular, cracked patterns | Bubbles, cells, fracture effects | Moderate |

### When to use which noise

- **"Make it flow smoothly"** → Simplex or Curl
- **"Make it look like smoke/fog"** → Curl Noise (the only divergence-free option)
- **"Make it look like fire"** → FBM (multi-layer detail gives flame richness)
- **"Make it look like bubbles/cells"** → Worley
- **"Just some gentle random drift"** → Simplex (simplest, fastest, looks good)
- **"Curl noise is too expensive"** → Bitangent Noise (same visual, cheaper math)

### Implementation notes

- **simplex-noise** npm package provides ready-to-use 2D/3D/4D simplex noise
- Curl noise is computed from the curl of a noise field — take the cross product of the gradient
- FBM is just noise() called at multiple frequencies and summed: `fbm(p) = noise(p) + 0.5*noise(2p) + 0.25*noise(4p) + ...`
- For GPU implementations, GLSL noise functions are widely available (Ashima/webgl-noise)
