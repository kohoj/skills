---
name: mogu-visual
description: |
  Transform technical descriptions into interactive animated HTML visualizations
  starring Mogu — a mushroom character whose cap adapts to each concept.
  Generates self-contained HTML files with Canvas 2D animations, interactive
  parameter controls, and a consistent character brand.
  Use when: "explain how X works", "visualize this concept", "make an interactive
  demo of", "show me how Y works visually", "mogu", "technical animation",
  "interactive diagram", "concept visualization", or any request to turn a
  technical mechanism into an interactive, visual, character-driven explanation.
  Also use when the user describes a system they want to understand better and
  would benefit from seeing it animated, even if they don't say "visualize" —
  e.g., "I don't get how Kafka partitions work", "can you show me load balancing",
  "explain consensus algorithms".
---

# Mogu Visual

Transform technical concepts into interactive animated HTML visualizations starring Mogu.

Before writing any code, read `references/character.md` -- it contains the canonical Mogu
specification that governs every visual decision below. If the reference fails to load,
the inline quick reference in Section 4 of this document is sufficient to draw a correct Mogu.

## Workflow

### Step 1: Understand the Concept

Parse the user's technical description. If the request is ambiguous, ask 1-2 clarifying
questions before proceeding:

- **Audience?** Developer, student, PM, general public?
- **Which aspect?** The whole system or a specific mechanism (e.g., "just the rebalancing part")?
- **Depth?** High-level overview or implementation-level detail?

Identify which scene archetype best fits the concept (see `references/scenes.md`):

| # | Archetype | When to use |
|---|-----------|-------------|
| 1 | **Pipeline** | Sequential stages, conveyor belt, ETL |
| 2 | **Network** | Nodes with edges, mesh, routing |
| 3 | **Pool/Queue** | Shared resource, workers grabbing tasks |
| 4 | **State Machine** | Single entity, morphing states |
| 5 | **Guard/Gate** | Gatekeeper, accept/reject, validation |
| 6 | **Tree** | Parent-child hierarchy, traversal |
| 7 | **Race** | Parallel tracks, contention, locks |
| 8 | **Transform** | Input goes in, different output comes out |
| 9 | **Broadcast** | One-to-many fan-out, pub/sub |
| -- | **Custom** | Combine archetypes or invent a new one |

### Step 2: Write the Scene Script

Produce a structured scene script using this template:

```
Scene: [title]
Archetype: [pipeline | network | pool | state-machine | guard | tree | race | transform | broadcast | custom]
Actors:
  - [role] ([size: small|medium|large], [cap color], [cap shape], [texture])
Items: [what flows between actors]
Parameters:
  - [name]: [slider|toggle|stepper] [range] [default] — [what it affects]
Key Moments:
  - [trigger] → [visual effect]
```

Present the scene script to the user for confirmation before generating code. This
is the contract -- changes after code generation are expensive.

### Step 3: Design the Cast

Select cap shapes, textures, and colors for each Mogu actor. Follow rules from
`references/character.md`:

- **Size = importance.** Central component gets the largest Mogu.
- **Same color = same role.** All API services share one color, all databases another.
- **Max 3 cap colors per scene.** More than 3 creates visual noise. Use shape/texture
  variation instead if you need more groups.
- **Colors:** Saturated but muted. Must pair with cream stem `#F5EDE0`.

### Step 4: Generate HTML

Produce a single self-contained HTML file with:

- **Canvas 2D** for animation (60fps game loop via `requestAnimationFrame`)
- **DOM overlay** for the control panel (sliders, toggles, steppers)
- Drawing code patterns copied from `components/widgets.js`
- **Absorption Ceremony** as the opening sequence (3-second intro)
- CDN imports optional (GSAP, D3) -- only when they add clear value

The HTML file must open in any browser with no build step, no local server, no dependencies
beyond optional CDN links.

### Step 5: Quality Gate

Check every item before delivering. If any row fails, fix it before handing off.

| Check | Failure | Fix |
|-------|---------|-----|
| Character consistency | Proportions wrong, missing highlight/feet | Compare to canonical SVG in Section 4 |
| Interactivity works | Controls don't affect animation | Bind params to game loop via state object |
| Animation smoothness | Stuttering | Use `requestAnimationFrame`, not `setInterval` |
| Concept accuracy | Doesn't match the technical concept | Re-examine scene script, fix the metaphor |
| Self-contained | Errors on open | Check CDN links, inline all critical code |
| Not dead | No motion without interaction | Add idle bounce + ambient particle/item motion |
| Not skin-deep | Params only change cosmetics | Params must affect behavior (rate, count, routing) |

## Mogu Character Quick Reference

This section is the fallback specification. If `references/character.md` loads, prefer that.
If it does not, everything below is sufficient to draw a correct Mogu.

### Canonical SVG

Source of truth. ViewBox: `0 0 140 170`.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 170">
  <!-- Stem: rx=14 gives soft rounded corners -->
  <rect x="50" y="95" width="40" height="50" rx="14" fill="#F5EDE0"/>

  <!-- Cap: dominant dome, ~2.6x wider than stem -->
  <ellipse cx="70" cy="82" rx="52" ry="38" fill="#FF4D4D"/>

  <!-- Cap highlight: subtle polish, shifted upper-left -->
  <ellipse cx="55" cy="68" rx="18" ry="10" fill="#FF7070" opacity="0.5"/>

  <!-- Spots: 3 circles, varied size, scattered unevenly -->
  <circle cx="42" cy="72" r="6" fill="#FF8080" opacity="0.7"/>
  <circle cx="68" cy="55" r="5" fill="#FF8080" opacity="0.7"/>
  <circle cx="90" cy="68" r="7" fill="#FF8080" opacity="0.7"/>

  <!-- Eyes: solid black dots on stem, no highlights -->
  <circle cx="60" cy="115" r="4.5" fill="#0a0a0a"/>
  <circle cx="80" cy="115" r="4.5" fill="#0a0a0a"/>

  <!-- Mouth: simple upward arc -->
  <path d="M63,127 Q70,133 77,127" stroke="#0a0a0a" stroke-width="2.5" fill="none" stroke-linecap="round"/>

  <!-- Feet: small ellipses for grounding -->
  <ellipse cx="58" cy="145" rx="10" ry="4" fill="#EBE0D0"/>
  <ellipse cx="82" cy="145" rx="10" ry="4" fill="#EBE0D0"/>
</svg>
```

### Proportions (Scale-Independent Ratios)

These ratios hold at any render size. The `size` parameter in `drawMogu()` maps to
the viewBox height (170 units).

| Ratio | Value | Derivation |
|-------|-------|------------|
| Cap width / Stem width | 2.6x | Cap `rx=52` (diameter 104), stem `width=40` |
| Cap height / Total height | ~45% | Cap zone 76px out of 170px |
| Stem height / Total height | ~30% | Stem 50px out of 170px |
| Feet zone / Total height | ~15% | Feet at y=145, ±4px |
| Eye spacing | Stem width x 50% | Eyes at x=60, x=80; spacing=20, stem=40 |
| Mouth below eyes | Stem height x 24% | Eyes y=115, mouth y=127; offset=12/50 |
| Eye radius | Stem width x 11% | r=4.5, stem=40 |

### Invariants (Never Change)

These values are fixed across all Mogus regardless of concept:

| Property | Value | Notes |
|----------|-------|-------|
| Stem fill | `#F5EDE0` | Warm cream |
| Eyes fill | `#0a0a0a` | Near-black |
| Eye radius | `stem_width x 11%` | ~4.5 at canonical scale |
| Feet fill | `#EBE0D0` | Slightly darker cream |
| Cap highlight | Cap color lightened 20%, opacity 0.5 | Upper-left shift |
| Spot color | Cap color lightened 25%, opacity 0.7 | Default texture |

Never change stem/feet colors, eye color, or the proportions above.

### Expression System

Only eyes and mouth change. No new elements added. Alert is the only expression
with eye-whites.

| Expression | Eyes | Mouth | When to use |
|------------|------|-------|-------------|
| **Neutral** | Solid dots (r=4.5) | Upward arc `M63,127 Q70,133 77,127` | Default, idle, at rest |
| **Curious** | Left dot normal, right dot bigger (r=5.5) shifted up to y=113 | Small circle "o" at (70, 129) r=3.5 | Encountering new input, inspecting data |
| **Processing** | Horizontal lines (x1=54..66, x1=74..86 at y=115) | Wavy line `M60,128 Q65,124 70,128 Q75,132 80,128` | Actively computing, transforming |
| **Proud** | Upward arcs (happy squint) `M55,114 Q60,110 65,114` | Wide grin `M60,126 Q70,136 80,126` | Task complete, success, output delivered |
| **Alert** | White circles (r=6) + dark pupils (r=3.5, offset +1x, +1y) | Inverted-V `M64,129 L70,124 L76,129` | Error, warning, unexpected input |

### Cap Shapes (8 Reference Shapes)

Shape = structural metaphor. The AI can invent new shapes beyond these.

| Shape | Silhouette | Semantic mapping |
|-------|-----------|------------------|
| **Classic Dome** | Standard ellipse | Default, general-purpose |
| **Flat / Shiitake** | Wide, low ellipse (capRy x 0.6) | Platform, infrastructure, database |
| **Pointy / Wizard** | Tall cone (quadratic curve) | Algorithm, logic, security, encryption |
| **Wavy / Ruffled** | Undulating edge (sin wave x 4) | Streaming, async, event-driven, reactive |
| **Multi-bump** | Three overlapping circles | Distributed systems, concurrency, microservices |
| **Droopy / Melting** | Dripping edges (quadratic drips) | Cache overflow, memory leak, GC, degradation |
| **Split / Forked** | Two lobes, split down middle | Load balancing, branching, A/B testing, fork |
| **Spiky / Urchin** | Triangular protrusions (8 spikes) | Firewall, defense, rate limiting, DDoS protection |

Each shape function receives `(ctx, cx, cy, capRx, capRy)`, calls `ctx.beginPath()`,
draws the path, and leaves it open for the caller to fill.

### Cap Textures (8 Reference Textures)

Texture = surface pattern mapped to concept characteristics.

| Texture | Visual | Semantic mapping |
|---------|--------|------------------|
| **Classic Spots** | Scattered circles, varied sizes | Default, general-purpose |
| **Ridges / Stripes** | Vertical lines, evenly spaced | Ordered flow, pipeline, sequential |
| **Hexagonal** | Honeycomb grid | Network topology, mesh, P2P, graph |
| **Circuit** | PCB trace lines + dots | Computation, digital logic, CPU, binary |
| **Swirl** | Spiral curves (2 turns) | Recursion, loops, iteration, cycles |
| **Constellation** | Dots connected by lines | Node networks, service mesh, distributed |
| **Scales** | Overlapping arcs | Queues, stacks, buffers, pagination |
| **Lightning / Cracks** | Zigzag paths | Energy, events, interrupts, exceptions |

Each texture function receives `(ctx, cx, cy, capRx, capRy, spotColor)`, sets
`ctx.globalAlpha = 0.7`, draws the pattern, then restores `ctx.globalAlpha = 1.0`.

### Cap Color Palette

Colors should be saturated but muted -- "as if the mushroom grew that way naturally."
Must pair with the cream stem `#F5EDE0`. No rigid domain-to-color mapping.

| Color | Hex | Semantic suggestions |
|-------|-----|----------------------|
| Red | `#FF4D4D` | Default, error, alert, critical path |
| Orange | `#FF8C42` | Activity, build, deployment, queue |
| Amber | `#FFB84D` | Warning, caution, cache, fallback |
| Yellow | `#FFD966` | Highlight, indexing, search |
| Lime | `#A3D977` | Growth, scaling, optimization |
| Green | `#52C77A` | Success, health, pass, ready |
| Teal | `#4DBFBF` | Flow, streaming, data pipeline |
| Sky Blue | `#5BA3E0` | Cloud, API, interface, communication |
| Blue | `#5680E0` | Logic, stable, core service |
| Indigo | `#7B68EE` | Deep computation, AI/ML, complex algorithm |
| Purple | `#A66FD9` | Transformation, middleware, orchestration |
| Magenta | `#E066A6` | Creative, UX, frontend, design system |
| Pink | `#FF6B9D` | Playful, user-facing, delight |
| Brown | `#A67C52` | Persistence, storage, database, logs |
| Gray | `#8C8C8C` | Neutral, deprecated, archived, inactive |

### Multi-Mogu Rules

When multiple Mogus appear in a single scene:

1. **Size = importance.** Primary component = largest. Helpers = small.
2. **Same cap color = same role.** All API services share one blue. All DBs share one brown.
3. **Max 3 cap colors per scene.** Use shape/texture variation for additional groups.
4. **Spatial arrangement:** Data flow left-to-right. Hierarchy top-to-bottom. Peers in a row.
5. **Same shape/texture = same structure type.** All async services get wavy caps.

### Absorption Ceremony

The 4-step brand intro sequence. Total duration: 3 seconds at 60fps.

**Step 1: Idle (0-0.8s)**
- Cap: `#FF4D4D` (red), classic dome, classic spots
- Expression: neutral
- Y-offset: sinusoidal idle bounce (+-2px, 2.5s period)

**Step 2: Notice (0.8-1.5s)**
- Expression: curious
- Keywords float in from the right (stagger 0.1s, slide + fade, monospace `#aaa`)
- Idle bounce continues

**Step 3: Swallow (1.5-2.2s)**
- Expression: processing
- Cap inflates: `capRy` increases by 15% (spring easing with overshoot)
- Keywords scale down toward cap center, fade out

**Step 4: Ready (2.2-3.0s)**
- Expression: proud
- Cap color lerps to final semantic color (ease-out, 0.5s)
- Cap shape morphs to final shape (if different from dome)
- `capRy` returns to normal (ease-out, 0.3s)
- One final small hop

After the ceremony, the Mogu is the concept and the main visualization begins.

**Timing control:**
```javascript
var time = 0; // seconds, incremented each frame by dt

if (time >= 1.5 && time < 2.2) {
  var stepTime = time - 1.5;
  var stepDuration = 0.7;
  var t = Math.min(stepTime / stepDuration, 1);
  var inflateAmount = ease.spring(t, 0.5);
  capRy = baseCapRy * (1 + 0.15 * inflateAmount);
}
```

**Color interpolation (RGB lerp):**
```javascript
function lerpColor(hex1, hex2, t) {
  var r1 = parseInt(hex1.substring(1, 3), 16);
  var g1 = parseInt(hex1.substring(3, 5), 16);
  var b1 = parseInt(hex1.substring(5, 7), 16);
  var r2 = parseInt(hex2.substring(1, 3), 16);
  var g2 = parseInt(hex2.substring(3, 5), 16);
  var b2 = parseInt(hex2.substring(5, 7), 16);
  var r = Math.round(r1 + (r2 - r1) * t);
  var g = Math.round(g1 + (g2 - g1) * t);
  var b = Math.round(b1 + (b2 - b1) * t);
  return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}
```

## Quick Reference Links

- Character spec: `references/character.md`
- Scene archetypes: `references/scenes.md`
- Interaction patterns: `references/interactions.md`
- Complete examples: `references/examples.md`
- Canonical SVG: `components/mogu.svg`
- Expression variants: `components/mogu-expressions.svg`
- Canvas 2D code: `components/widgets.js`
