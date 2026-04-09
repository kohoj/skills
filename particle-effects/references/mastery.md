# Master-Level Particle Effects — Principles & Anti-Patterns

The difference between amateur and professional particle work is not the algorithm — it is the
**details**. This reference codifies the judgment calls that separate a CodePen toy from a Lusion
portfolio piece. Every principle here is derived from studying the output of specific masters.

Read this file when generating any particle effect. These are not optional polish steps — they
are fundamental quality requirements baked into every line of code.

## Table of Contents

1. [Color: The #1 Amateur Tell](#1-color)
2. [Motion: Weight, Flow, Breath](#2-motion)
3. [Composition: Depth, Layers, Space](#3-composition)
4. [Polish: The Last 20% That Is 80% of the Impact](#4-polish)
5. [Anti-Patterns: What Screams Amateur](#5-anti-patterns)

---

## 1. Color

**Principle: Every color choice should be intentional. Random colors = amateur.**

### Never use pure colors

| Amateur | Pro | Why |
|---------|-----|-----|
| `#ffffff` | `#f0e6ff` or `#e8f4ff` | Pure white is harsh; tinted whites feel designed |
| `#ff0000` | `#ff4444` or `#e63946` | Pure primaries feel like a default; muted tones feel chosen |
| `#000000` background | `#08080f` or `#0a0a1a` | Pure black kills depth; dark blue/purple adds atmosphere |
| Random RGB per particle | Palette of 4-7 harmonious colors | Random looks like confetti; palettes feel curated |

### Color ramp over lifetime (flight404's signature)

Robert Hodgin's particle work always has color evolution. Particles are born one color and die
another. This single technique adds more visual richness than any physics improvement:

```javascript
// Good: color shifts over lifetime
const lifeRatio = life / maxLife;
color.r = lerp(birthColor.r, deathColor.r, 1 - lifeRatio);
color.g = lerp(birthColor.g, deathColor.g, 1 - lifeRatio);
color.b = lerp(birthColor.b, deathColor.b, 1 - lifeRatio);

// Bad: static color for entire lifetime
color.set(0.8, 0.3, 1.0); // stays purple forever — flat, lifeless
```

### Use perceptually uniform color spaces for interpolation

RGB interpolation creates muddy midpoints. Use HSL or OKLab for smooth gradients:

```javascript
// In the fragment shader — HSL-based color shift
vec3 hsl = rgb2hsl(vColor);
hsl.x += vLifeRatio * 0.1; // subtle hue shift over lifetime
hsl.z *= 0.5 + vLifeRatio * 0.5; // brighter when young, dimmer when dying
vec3 finalColor = hsl2rgb(hsl);
```

### Warm-cool contrast (Lusion's palette strategy)

The best particle effects use warm highlights against cool shadows (or vice versa).
Never use a single-temperature palette:

- Smoke: cool blue/purple base + warm orange/pink edge highlights
- Galaxy: warm yellow core + cool blue arms
- Fire: hot white center + warm orange + cool dark red edges
- Ambient: cool blue/cyan particles + occasional warm gold accent (1 in 20 particles)

### Palette construction

Build a palette of 5-7 colors. Assign probabilities:
- 60% — dominant mood color (e.g., deep blue)
- 25% — secondary color (e.g., purple)
- 10% — accent color (e.g., cyan or gold)
- 5% — highlight color (e.g., near-white tinted)

```javascript
function pickColor(palette, weights) {
  let r = Math.random(), acc = 0;
  for (let i = 0; i < palette.length; i++) {
    acc += weights[i];
    if (r < acc) return palette[i].clone();
  }
  return palette[0].clone();
}
```

---

## 2. Motion

**Principle: Every particle should move as if it has mass. Weightless motion looks fake.**

### Easing — never linear

Linear interpolation makes everything look robotic. Use easing for all transitions:

```javascript
// Bad: linear
pos += (target - pos) * 0.05;

// Good: spring physics — has overshoot, settle, weight
vel += (target - pos) * stiffness;
vel *= damping;
pos += vel;

// Also good: exponential decay (smooth, no overshoot)
pos += (target - pos) * (1 - Math.exp(-speed * dt));
```

### Multi-octave noise (iq's depth technique)

A single layer of noise looks mechanical. Layer 2-3 octaves at different frequencies
and amplitudes. This creates the fractal richness found in natural phenomena:

```javascript
// Bad: single noise layer
vx += noise(x * freq, y * freq, t) * amp;

// Good: FBM-style layered noise
vx += noise(x * freq, y * freq, t) * amp;
vx += noise(x * freq * 2.13, y * freq * 2.13, t * 1.37) * amp * 0.35;
vx += noise(x * freq * 4.37, y * freq * 4.37, t * 1.71) * amp * 0.15;
// Use irrational-ish multipliers to avoid repetition
```

### Velocity inheritance (akella's trail technique)

When particles spawn from a moving source (cursor, scrolling element), they must inherit
the source's velocity. Without this, trails look like they're being placed, not emitted:

```javascript
// Bad: particles spawn with zero velocity
particle.vx = 0;

// Good: inherit source momentum
particle.vx = mouseVelocity.x * 0.3 + randomSpread;
particle.vy = mouseVelocity.y * 0.3 + randomSpread;
```

### Graceful birth and death

Particles that pop into existence and vanish abruptly look cheap. Always fade in
and fade out:

```javascript
const lifeRatio = life / maxLife; // 1.0 = just born, 0.0 = about to die
const fadeIn  = Math.min(1, (1 - lifeRatio) * 6);  // first ~15% of life
const fadeOut = Math.min(1, lifeRatio * 3);          // last ~33% of life
const alpha = fadeIn * fadeOut;
// Peak alpha is never 1.0 — it's a smooth mountain shape
```

### Damping values matter enormously

| Damping | Feel | Use for |
|---------|------|---------|
| 0.85-0.90 | Heavy, viscous, slow | Underwater, thick smoke |
| 0.91-0.95 | Natural, weighted | Most effects — the sweet spot |
| 0.96-0.99 | Light, floaty, drifty | Space, zero-gravity, ambient |

### Stagger timing

Never spawn all particles at the same time. Stagger births so the system builds up
organically. For scatter/assemble animations, add per-particle delay based on distance
or random offset:

```javascript
// Stagger assembly by distance from center
const delay = Math.sqrt(tx * tx + ty * ty) * 0.1;
particle.assembleTime = globalTime + delay;
```

---

## 3. Composition

**Principle: The space between particles matters as much as the particles themselves.**

### Layer at multiple scales (flight404's depth)

A single layer of same-sized particles looks flat. Use 2-3 layers:

- **Background layer**: many tiny, dim, slow particles (atmosphere)
- **Mid layer**: medium particles, normal speed (the main effect)
- **Foreground layer**: few large, bright, fast particles (depth cue)

The foreground layer can be just 2-5% of total particles but creates a powerful
sense of depth and dimension.

```javascript
// When initializing particles, assign layers
const layerRoll = Math.random();
if (layerRoll < 0.15) {
  // Background: small, dim, slow
  particle.size = 0.3 + Math.random() * 0.3;
  particle.speedMult = 0.5;
  particle.alpha = 0.3;
} else if (layerRoll < 0.95) {
  // Mid: standard
  particle.size = 0.6 + Math.random() * 0.6;
  particle.speedMult = 1.0;
  particle.alpha = 1.0;
} else {
  // Foreground: large, bright, fast
  particle.size = 1.5 + Math.random() * 1.0;
  particle.speedMult = 1.5;
  particle.alpha = 1.2; // can exceed 1 with additive blending
}
```

### Size variation is depth

Even in 2D, varying particle sizes creates an illusion of 3D depth.
Never use uniform sizes:

```javascript
// Bad: all same size
sizes[i] = 1.0;

// Good: log-normal distribution — many small, few large
sizes[i] = Math.exp(Math.random() * 1.2 - 0.3); // range ~0.4 to 3.3
```

### Negative space (Lusion's restraint)

The temptation is to fill the screen with particles. Resist it. Professional work uses
particle density strategically — areas of high density draw the eye, areas of emptiness
give the eye room to rest. This is the difference between "wow" and "noisy."

- Ambient effects: max 30-40% screen coverage
- Focal effects (morph, galaxy): dense center, sparse edges
- Never cover the entire viewport uniformly

### Screen-aware composition

Position the effect's center of gravity intentionally. For full-screen backgrounds,
slightly offset from dead center (rule of thirds). For focal effects, ensure the
effect doesn't compete with UI elements.

---

## 4. Polish

**Principle: Post-processing is not optional. It is the difference between WebGL demo and shipped product.**

### Bloom — always, but subtle

UnrealBloomPass with low strength (0.2-0.5) adds perceived luminosity without washing
out the image. The key settings:

| Parameter | Amateur | Pro |
|-----------|---------|-----|
| strength | 1.0+ (everything glows) | 0.2-0.5 (selective glow) |
| threshold | 0.0 (everything blooms) | 0.3-0.6 (only bright particles) |
| radius | 1.0+ (huge halo) | 0.3-0.7 (tight, focused) |

### Additive blending opacity rules

With additive blending, opacity must be LOW to prevent color saturation:
- For dense effects (smoke, galaxy): opacity 0.05-0.15
- For medium effects (ambient, morph): opacity 0.15-0.35
- For sparse effects (trails, bursts): opacity 0.3-0.6

If the assembled image / effect looks washed out or white, opacity is too high.

### Responsive and pixel-perfect

```javascript
// Always handle resize
window.addEventListener('resize', onResize);

// Always use devicePixelRatio for crisp particles on retina
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));

// Cap at 2 — higher is wasteful and kills performance
```

### Performance budgets

| Target | Particles | Approach |
|--------|-----------|----------|
| 60fps desktop | up to 30K | CPU physics + GPU render |
| 60fps desktop | 30K-500K | GPGPU (FBO ping-pong) |
| 60fps mobile | up to 5K | Canvas 2D or lightweight Points |
| 60fps mobile | 5K-50K | GPGPU, reduce overdraw |

### lil-gui is a design tool, not a debug panel

Group parameters semantically. Name them for the user (not the developer):
- "Wind Strength" not "noiseAmplitude"
- "Glow Intensity" not "bloomStrength"
- "Particle Density" not "particleCount"

Include presets if the effect has distinct moods:
```javascript
const presets = {
  dreamy:    { noiseSpeed: 0.08, damping: 0.97, bloomStrength: 0.5, opacity: 0.12 },
  energetic: { noiseSpeed: 0.3,  damping: 0.90, bloomStrength: 0.3, opacity: 0.25 },
  minimal:   { noiseSpeed: 0.05, damping: 0.98, bloomStrength: 0.1, opacity: 0.08 },
};
gui.add({ preset: 'dreamy' }, 'preset', Object.keys(presets)).onChange(key => {
  Object.assign(params, presets[key]);
  gui.controllersRecursive().forEach(c => c.updateDisplay());
});
```

---

## 5. Anti-Patterns

These are the most common mistakes that immediately mark an effect as amateur.
Check every implementation against this list before shipping.

### The deadly sins

| Sin | What it looks like | Fix |
|-----|-------------------|-----|
| **White-out** | Dense areas burn to pure white | Lower opacity, raise bloom threshold |
| **Uniform soup** | All particles same size, speed, color | Add size variation, layering, palette |
| **Linear motion** | Particles move at constant speed | Add easing, spring physics, damping |
| **Hard edges** | Particles appear/disappear instantly | Add fade in/out over first/last 15% of life |
| **Noise jitter** | Random shake instead of flow | Use curl/simplex noise, never Math.random() per frame |
| **Screen stuffing** | Particles everywhere, no breathing room | Reduce count, add negative space, use density gradients |
| **Single-temp palette** | All blue, all orange, no contrast | Add warm-cool contrast, even if subtle |
| **Dead calm** | Particles at rest are perfectly still | Add very subtle noise idle drift (amp 0.002-0.005) |
| **GPU waste** | 100K particles for a 50-particle effect | Match tech stack to actual particle count |
| **Missing GUI** | Hard-coded values, no way to tune | Always include lil-gui with grouped parameters |

### The "just good enough" trap

It is tempting to stop when the effect "works." Working is not the bar. The bar is:
would this look at home on a Lusion or Active Theory project page? If not, iterate.

The most common gap between "works" and "ships" is post-processing (bloom, color grading)
and motion quality (spring physics instead of lerp, noise instead of random).
