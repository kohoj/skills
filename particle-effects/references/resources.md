# Resources — Libraries, Tools & Classic Cases

## Essential Websites & Communities

| Website | Value | URL |
|---------|-------|-----|
| **Chrome Experiments** | Google's graphics experiments — tons of Three.js + particle demos | experiments.withgoogle.com |
| **Shadertoy** | Pure shader community — bleeding-edge particle algorithms | shadertoy.com |
| **CodePen** | Runnable frontend demos — search "three.js particles" | codepen.io |
| **Codrops** (tympanus.net) | High-quality Three.js tutorials with complete code | tympanus.net/codrops |
| **Three.js Discourse** | Official forum — Showcase section for inspiration | discourse.threejs.org |
| **webgpu.com** | WebGPU community — cutting-edge compute shader particle cases | webgpu.com |
| **The Book of Shaders** | Essential shader primer — start here if new to GLSL | thebookofshaders.com |
| **Three.js Roadmap Blog** | WebGPU + Three.js hands-on tutorials | threejsroadmap.com/blog |

## Key Libraries & Tools

| Library | Purpose | Notes |
|---------|---------|-------|
| **Three.js** | 3D rendering engine | The go-to framework for particle systems |
| **lil-gui** | Parameter tweaking panel | Three.js official recommendation (replaced dat.gui) |
| **three-nebula** | Three.js particle engine | JSON-configurable particle system |
| **tsparticles** | Lightweight 2D particle library | Great for simple background effects — zero-config |
| **React Three Fiber** | React + Three.js binding | Best choice for React projects |
| **GSAP** | Animation timeline library | ScrollTrigger pairs perfectly with scroll-based particle effects |
| **simplex-noise** | JS noise library | npm-ready simplex noise implementation |

## Classic Cases by Pattern

### Ambient Background
- Chrome Experiments "One Million Particles" — million-particle mouse-interactive field
- tsparticles official demo — ready-to-use background particles

### Mouse Trail
- Codrops "Interactive WebGL Hover Effects" — mouse trail shader distortion
- cursor-effects.js — pre-built mouse particle effects library

### Image/Text Morph
- Codrops "Interactive Particles" — image sampling + mouse repulsion
- Codrops "3D Typing Effects with Three.js" — text particle typing effect
- Codrops "3D Particle Explorations" — various 3D particle morphing
- CodePen "threejs image particle" (by Google Creative Lab) — image-to-particle conversion

### Dissolve
- Codrops "Implementing a Dissolve Effect" (2025) — Thanos-style dissolve + bloom
- Codrops "Crafting a Dreamy Particle Effect with GPGPU" (2024) — dreamy GPGPU particles

### Fluid / Smoke
- Shadertoy "Visualizing Curl Noise" (ID: mlsSWH) — curl noise visualization
- Shadertoy "Interactive Particles" (ID: McXXzH) — interactive particles + attractors
- OPENFUSE "Strange Attractors & Curl Noise" — strange attractor + curl noise hybrid
- Maxime Heckel "Field Guide to TSL and WebGPU" (2025) — modern WebGPU particle techniques

### Physics / Simulation
- lisyarus "Particle Life in WebGPU" — emergent particle life simulation
- WebGPU Samples "computeBoids" — official Boids flocking example
- Codrops "When Cells Collide" (2025) — Rapier physics engine + cell particles

### Galaxy / Large Scale
- Three.js Roadmap "Galaxy Simulation with WebGPU Compute Shaders" — complete galaxy tutorial
- Shadertoy "Galaxy" series — various galaxy rendering approaches

## lil-gui Standard Template

Every particle effect should include a lil-gui panel. Here is the standard parameter structure:

```javascript
import GUI from 'lil-gui';
const gui = new GUI();

const params = {
  // Emitter
  particleCount: 10000,
  emissionRate: 100,
  lifetime: 2.0,

  // Physics
  noiseFrequency: 1.5,
  noiseAmplitude: 0.3,
  noiseSpeed: 0.2,
  gravity: -0.1,
  damping: 0.98,

  // Rendering
  particleSize: 2.0,
  opacity: 0.6,
  bloom: true,
  bloomStrength: 0.8,
  blendMode: 'additive' // 'additive' | 'normal' | 'subtractive'
};

const emitterFolder = gui.addFolder('Emitter');
emitterFolder.add(params, 'particleCount', 100, 100000).step(100);
emitterFolder.add(params, 'emissionRate', 1, 500);
emitterFolder.add(params, 'lifetime', 0.1, 10.0);

const physicsFolder = gui.addFolder('Physics');
physicsFolder.add(params, 'noiseFrequency', 0.1, 5.0);
physicsFolder.add(params, 'noiseAmplitude', 0.0, 2.0);
physicsFolder.add(params, 'noiseSpeed', 0.0, 1.0);
physicsFolder.add(params, 'gravity', -2.0, 2.0);
physicsFolder.add(params, 'damping', 0.8, 1.0);

const renderFolder = gui.addFolder('Rendering');
renderFolder.add(params, 'particleSize', 0.5, 10.0);
renderFolder.add(params, 'opacity', 0.01, 1.0);
renderFolder.add(params, 'bloom');
renderFolder.add(params, 'bloomStrength', 0.0, 3.0);
```

### lil-gui Best Practices

1. **Always include lil-gui** — explicitly require it in your prompt
2. **List the exact parameters you want** — the more specific, the better the output
3. **Group parameters into folders** — Emitter, Physics, Rendering
4. **Require real-time preview** — parameter changes should apply immediately (no restart needed)
