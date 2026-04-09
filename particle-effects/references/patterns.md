# Interaction Patterns — Full Reference

Each pattern includes: what it looks like, how it works, key parameters with recommended ranges,
common variants, classic references, and a ready-to-use prompt example.

## Table of Contents

1. [Pattern 01: Ambient Background](#pattern-01-ambient-background)
2. [Pattern 02: Mouse Trail](#pattern-02-mouse-trail)
3. [Pattern 03: Image/Text Morph](#pattern-03-imagetext-morph)
4. [Pattern 04: Hover Burst](#pattern-04-hover-burst)
5. [Pattern 05: Scroll Reveal](#pattern-05-scroll-reveal)
6. [Pattern 06: Radial Pulse](#pattern-06-radial-pulse)
7. [Pattern 07: Galaxy / Spiral](#pattern-07-galaxy--spiral)
8. [Pattern 08: Fluid / Smoke](#pattern-08-fluid--smoke)
9. [Pattern 09: Dissolve / Disintegrate](#pattern-09-dissolve--disintegrate)
10. [Pattern 10: Physics Playground](#pattern-10-physics-playground)

---

## Pattern 01: Ambient Background

**Effect:** Slow-drifting atmospheric particles across the page background, setting mood.

**Core tech combo:** Large count of low-opacity point sprites + simplex noise drive + additive blending

### Key Parameters

| Parameter | Range | Notes |
|-----------|-------|-------|
| Particle count | 1,000 - 10,000 | More = denser atmosphere |
| Speed | 0.1 - 0.5 | Very slow — ambient, not distracting |
| Alpha | 0.1 - 0.4 | Low opacity for subtlety |
| Size | 1 - 4px | Small dots |
| Interaction | None or subtle mouse parallax | Should not demand attention |

### Variants

- **Starfield** — white dots + occasional twinkle (random alpha oscillation)
- **Floating dust** — warm colors + slight downward gravity
- **Deep sea** — blue-green + slow upward drift
- **Node network** — proximity lines connecting nearby particles (distance-based)

### Prompt Example

> "Create a Three.js ambient particle background with 5000 particles driven by 3D simplex noise.
> Use additive blending, soft white color fading to transparent. Add subtle mouse parallax.
> Include a lil-gui panel to adjust particle count, noise speed, noise scale, and particle size."

---

## Pattern 02: Mouse Trail

**Effect:** Particles spawn and fade along the cursor's path.

**Core tech combo:** Mouse position as emitter + velocity inherited from cursor + short lifetime + alpha decay

### Key Parameters

| Parameter | Range | Notes |
|-----------|-------|-------|
| Emission rate | 5 - 20 per frame | Higher = denser trail |
| Lifetime | 0.3 - 1.5s | Short-lived for crisp trails |
| Initial velocity | Mouse speed x 0.1 - 0.5 | Inherit cursor momentum |
| Size decay | Large to small | Shrink over lifetime |

### Variants

- **Stardust trail** — multicolor + random scatter angle
- **Ink trail** — large particles + fast shrink + dark colors
- **Smoke trail** — curl noise driven diffusion + gray tones
- **Spark trail** — high initial speed + gravity + warm orange/yellow

### Prompt Example

> "Build a mouse trail particle effect using Canvas 2D. Spawn 10 particles per frame at cursor
> position with velocity inherited from mouse movement. Each particle should have 0.8s lifetime,
> shrink linearly, and use additive blending with a warm golden color ramp (white -> gold ->
> transparent). Add lil-gui for trail length, particle size, gravity, and color."

---

## Pattern 03: Image/Text Morph

**Effect:** An image or text dissolves into particles, then reassembles or scatters.

**Core tech combo:** Canvas samples pixel colors/positions -> particles target those positions -> lerp/spring to settle or noise to scatter

### Key Parameters

| Parameter | Range | Notes |
|-----------|-------|-------|
| Particle count | 5,000 - 50,000 | = number of sampled points |
| Sampling interval | Every 2-4 pixels | Denser = more particles, more detail |
| Spring stiffness | 0.01 - 0.1 | How quickly particles snap to target |
| Spring damping | 0.8 - 0.95 | Higher = less oscillation |
| Scatter force | curl noise or directional burst | What drives the "scatter" phase |

### Variants

- **Image assemble** — particles fly from random positions toward the image shape
- **Image shatter** — mouse proximity pushes particles away, they return when cursor leaves
- **Text typing** — characters appear one by one, each formed from converging particles (canvas sampling per character)
- **Logo breathing** — particles hover near the logo shape with noise-driven idle drift

### Classic References

- Codrops "Interactive Particles" — image sampling + mouse repulsion
- Codrops "3D Typing Effects with Three.js" — text particle typing effect
- CodePen "threejs image particle" by Google Creative Lab

### Prompt Example

> "Create a Three.js particle system that samples an uploaded image's pixels to create a point
> cloud. Use ShaderMaterial with custom vertex/fragment shaders. Particles should start scattered
> randomly, then animate to their target image positions using spring physics (stiffness: 0.03,
> damping: 0.9). On mouse proximity, particles should be repelled with a radius of 100px. Add
> curl noise displacement for an organic idle animation. Include lil-gui for spring stiffness,
> damping, noise amplitude, noise speed, and repel radius."

---

## Pattern 04: Hover Burst

**Effect:** Particles explode outward from a button or element on mouse hover.

**Core tech combo:** hover event triggers -> short burst of high-rate emission -> radial velocity + gravity + fast alpha decay

### Key Parameters

| Parameter | Range | Notes |
|-----------|-------|-------|
| Burst count | 20 - 100 | One-shot emission on hover |
| Radial speed | 50 - 200 | Initial outward velocity |
| Lifetime | 0.3 - 0.8s | Quick burst, quick fade |
| Gravity | Optional | Downward pull for sparks, none for explosions |

### Variants

- **Confirmation burst** — green upward particles + checkmark
- **Edge sparks** — particles emit along the button border
- **Bubble pop** — large circle shrinks and splits into many small circles
- **Ripple pulse** — ring expands outward + alpha decay

### Prompt Example

> "Create a button hover particle burst effect using Canvas 2D. On mouseenter, emit 50 particles
> in a radial pattern with random speed (100-250px/s), random angle, and a 0.6s lifetime.
> Particles should fade out and shrink. Use a pastel color palette. Make it a reusable function:
> burstAt(x, y, color, count)."

---

## Pattern 05: Scroll Reveal

**Effect:** Elements materialize through particle animation as they scroll into view.

**Core tech combo:** IntersectionObserver or scroll position triggers -> particles converge from scattered to shape -> or scatter from shape

### Key Parameters

| Parameter | Range | Notes |
|-----------|-------|-------|
| Trigger point | Element 30-50% in viewport | When animation starts |
| Animation duration | 1 - 3s | Total convergence/scatter time |
| Easing | easeOutExpo or spring | Organic deceleration |

### Variants

- **Number/text particle convergence** — digits form from converging particles
- **Divider line flows** — section dividers formed by flowing particles
- **Image particle assembly** — image assembles from scattered particles
- **Background density shift** — ambient particle density increases as you scroll

### Prompt Example

> "Create a scroll-triggered particle reveal effect. When a section scrolls into view, 3000
> particles converge from random positions to form the text 'Hello'. Use GSAP ScrollTrigger
> for scroll detection and Three.js for particle rendering. Particles should use spring
> interpolation to reach their target positions."

---

## Pattern 06: Radial Pulse

**Effect:** Concentric rings of particles expand outward from a center, breathing rhythmically.

**Core tech combo:** Ring/circle emitter + sin wave modulates radius + alpha fades with distance

### Key Parameters

| Parameter | Range | Notes |
|-----------|-------|-------|
| Emitter shape | ring / circle emitter | Circular spawn region |
| Radius animation | baseRadius + amplitude * sin(time * frequency) | Breathing motion |
| Pulse frequency | 0.5 - 2 Hz | Rhythm of the breathing |
| Layer count | 2-3 rings at different phases | Depth and visual richness |

### Variants

- **Audio visualizer** — audio frequency drives radius
- **Heartbeat** — fast-slow-fast rhythm pattern
- **Radar sweep** — one-directional rotating fan emission
- **Water ripple** — concentric expanding rings, fading out

### Prompt Example

> "Create a radial pulse particle effect with Three.js. Particles emit from a ring that breathes
> (radius oscillates sinusoidally between 50 and 200). Each pulse spawns 200 particles that drift
> outward with decreasing speed and fading alpha. Layer 3 pulses with phase offsets of 120 degrees.
> Use additive blending and a cyan-to-transparent color ramp."

---

## Pattern 07: Galaxy / Spiral

**Effect:** Particles form a rotating galaxy or spiral arm structure.

**Core tech combo:** Logarithmic spiral distribution + vortex rotation + FBM noise perturbation + color mapping

### Key Parameters

| Parameter | Range | Notes |
|-----------|-------|-------|
| Particle count | 10,000 - 1,000,000 | Large counts need GPGPU |
| Spiral arms | 2 - 6 | Number of arms |
| Arm sweep angle | 2pi - 6pi | How tightly wound the spiral is |
| Core brightness | Higher density + brighter color at center | Visual anchor |

### Variants

- **Classic spiral galaxy** — flat disk + central bulge + spiral arms
- **Nebula vortex** — volumetric feel + curl noise perturbation
- **Data visualization spiral** — particle size/color maps to data values
- **Black hole accretion disk** — particles attracted to center + high-speed rotation

### Classic References

- Three.js Roadmap "Galaxy Simulation with WebGPU Compute Shaders"
- Chrome Experiments "One Million Particles"
- Shadertoy "Galaxy" by various authors

### Prompt Example

> "Create a spiral galaxy particle system with Three.js and GPGPU (using FBO ping-pong for WebGL,
> or compute shader for WebGPU). Generate 100,000 particles distributed along 4 logarithmic spiral
> arms with FBM noise perturbation. Color particles from blue (outer) to white-yellow (inner core).
> Add slow rotation and a lil-gui panel for arm count, spread, rotation speed, and noise amplitude."

---

## Pattern 08: Fluid / Smoke

**Effect:** Particles move like smoke, fog, or liquid — organic and flowing.

**Core tech combo:** Curl noise velocity field + high particle density + soft blending + narrow color ramp

### Key Parameters

| Parameter | Range | Notes |
|-----------|-------|-------|
| Noise type | curl noise | Must be divergence-free for fluid look |
| Noise frequency | 0.5 - 3.0 | Low = large swirls, high = fine turbulence |
| Noise evolution speed | 0.1 - 0.5 | How fast the flow field changes over time |
| Particle alpha | 0.05 - 0.2 | Very low — semi-transparent layers build up volume |

### Variants

- **Colorful smoke** — multiple curl noise layers with different hues
- **Underwater** — rising bubbles + curl-driven currents
- **Fire** — vertical curl noise + bottom hot-color to top dark-red gradient
- **Aurora** — horizontally stretched curl noise + green/purple color band

### Classic References

- Shadertoy "Visualizing Curl Noise" (mlsSWH)
- Shadertoy "Curl Noise Animation" (Wl2cW1)
- OPENFUSE "Strange Attractors & Curl Noise"
- Bitangent Noise (high-performance curl alternative): github.com/atyuwen/bitangent_noise

### Prompt Example

> "Create a smoke simulation using Three.js with curl noise. Use a fragment-shader-based GPGPU
> approach (FBO ping-pong) to update 50,000 particle positions per frame. Drive velocity with 3D
> curl noise (simplex-based). Render with additive blending and very low alpha (0.08). Add mouse
> interaction: mouse position acts as a wind force pushing smoke. Include lil-gui for noise
> frequency, noise evolution speed, particle alpha, wind strength."

---

## Pattern 09: Dissolve / Disintegrate

**Effect:** A 3D object progressively crumbles into particles that drift away — like Thanos' snap.

**Core tech combo:** Mesh vertices as initial particle positions -> noise threshold controls dissolve progress -> vertices exceeding threshold gain velocity -> bloom highlights the dissolve edge

### Key Parameters

| Parameter | Range | Notes |
|-----------|-------|-------|
| Dissolve direction | noise-based (organic) or directional (up/down/left/right) | Visual style choice |
| Edge glow | emission color + bloom near the dissolve threshold | The "magic" look |
| Drift force | curl noise or gravity + random | What drives freed particles |
| Progress control | uniform float (0-1) | Animatable dissolve progress |

### Classic References

- Codrops "Implementing a Dissolve Effect with Shaders and Particles in Three.js" (2025)
- Codrops "Crafting a Dreamy Particle Effect with Three.js and GPGPU" (2024)

### Prompt Example

> "Create a Thanos-snap dissolve effect on a 3D mesh using Three.js. Use noise-based threshold
> to progressively dissolve the mesh. Particles at the dissolve edge should glow (emissive +
> Unreal Bloom post-processing). Dissolved vertices become free particles driven by curl noise
> and gravity. Control dissolve progress with a slider (0 to 1). Include lil-gui for dissolve
> speed, noise scale, glow intensity, particle drift speed."

---

## Pattern 10: Physics Playground

**Effect:** Particles interact with each other through real physics — collisions, attraction, repulsion, elasticity.

**Core tech combo:** N-body simulation or spatial hashing + collision detection + force accumulation

### Key Parameters

| Parameter | Range | Notes |
|-----------|-------|-------|
| Attraction/repulsion radius | Tunable | How far forces reach |
| Collision elasticity | 0-1 | Bounce vs. absorb |
| Global gravity | Tunable | Downward pull |
| Boundary behavior | Bounce / wrap / die | What happens at edges |

### Variants

- **Particle Life** — different colored particles have different attraction/repulsion rules -> emergent life-like behavior
- **Boids flock** — separation + alignment + cohesion -> bird/fish schooling
- **Spring mesh** — particles connected by springs -> cloth/soft body simulation
- **Gravity simulation** — multiple gravity sources + particle orbits

### Classic References

- lisyarus "Particle Life Simulation in Browser Using WebGPU"
- WebGPU Samples "computeBoids" (official)
- Chrome Experiments "Flocking Simulation"
- Codrops "When Cells Collide" (2025) — Rapier physics + cell particles

### Prompt Example

> "Create a Particle Life simulation with WebGPU compute shaders. 6 particle types (colors),
> each with random attraction/repulsion rules to other types. Use spatial hashing for O(n*m)
> performance. Render as colored point sprites with additive blending. Include lil-gui to
> randomize rules, adjust interaction radius, friction, and particle count."
