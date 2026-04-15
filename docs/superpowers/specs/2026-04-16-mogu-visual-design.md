# Mogu Visual — Design Spec

**Date:** 2026-04-16
**Status:** Approved
**Skill name:** `mogu-visual`

## Overview

A Claude Code skill that transforms technical descriptions into interactive, animated HTML visualizations starring Mogu — a mushroom character brand. Users describe a technical concept in natural language; the AI refines it into a structured scene script, then generates a self-contained HTML file with Canvas 2D animations, interactive parameter controls, and the Mogu character system.

**Core identity:** Mogu is a mushroom whose cap is the canvas for expressing concepts. The stem, face, and feet never change — only the cap shape, texture, color, and facial expression vary. This creates a consistent brand that can absorb any concept.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Character | Mogu (mushroom) | Natural top-bottom structure; cap = concept canvas, stem = invariant identity |
| Brand strategy | Single character, shape-shifting cap | Like Kirby absorbing abilities — same character, infinite variations |
| Interaction depth | Interactive playground | Users can adjust parameters and see real-time system behavior changes |
| Tech stack | Single HTML file, CDN deps OK, no build step | Open in browser and go; zero friction |
| Input flow | Natural language → scene script → confirm → generate | AI extracts structure, user validates before generation |
| Output | One-off consumption in browser | Not embedded, not persisted — generated, viewed, done |
| Architecture | Prompt-heavy + component snippets | Flexible generation with code reference pieces for consistency |

## Character Specification

### Canonical SVG

The following SVG is the single source of truth for Mogu. All generations must match these proportions.

```svg
<svg viewBox="0 0 140 170">
  <!-- Stem -->
  <rect x="50" y="95" width="40" height="50" rx="14" fill="#F5EDE0"/>
  <!-- Cap -->
  <ellipse cx="70" cy="82" rx="52" ry="38" fill="#FF4D4D"/>
  <!-- Cap highlight -->
  <ellipse cx="55" cy="68" rx="18" ry="10" fill="#FF7070" opacity="0.5"/>
  <!-- Spots (3, varied size) -->
  <circle cx="42" cy="72" r="6" fill="#FF8080" opacity="0.7"/>
  <circle cx="68" cy="55" r="5" fill="#FF8080" opacity="0.7"/>
  <circle cx="90" cy="68" r="7" fill="#FF8080" opacity="0.7"/>
  <!-- Face on stem -->
  <circle cx="60" cy="115" r="4.5" fill="#0a0a0a"/>
  <circle cx="80" cy="115" r="4.5" fill="#0a0a0a"/>
  <path d="M63,127 Q70,133 77,127" stroke="#0a0a0a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <!-- Feet -->
  <ellipse cx="58" cy="145" rx="10" ry="4" fill="#EBE0D0"/>
  <ellipse cx="82" cy="145" rx="10" ry="4" fill="#EBE0D0"/>
</svg>
```

### Proportions (scale-independent)

| Ratio | Value |
|-------|-------|
| Cap width / Stem width | 2.6x |
| Cap height / Total height | ~45% |
| Stem height / Total height | ~30% |
| Feet zone / Total height | ~15% |
| Eye spacing | Stem width × 50% |
| Mouth below eyes | Stem height × 24% |

### Invariants (never change)

| Element | Value |
|---------|-------|
| Stem fill | `#F5EDE0` |
| Eyes fill | `#0a0a0a` |
| Eye radius | stem_width × 11% |
| Feet fill | `#EBE0D0` |
| Cap highlight | cap_color lightened 20%, opacity 0.5 |
| Spot color | cap_color lightened 25%, opacity 0.7 |

### Variables (change per concept)

- Cap fill color
- Cap shape (silhouette)
- Cap texture (surface pattern)
- Spot shapes (can morph from circles to concept icons)
- Facial expression (eyes + mouth only)

### Expression System

5 core expressions. Only the eyes and mouth change — no new elements are ever added (no eyebrows, no blush, no accessories).

| Expression | Eyes | Mouth | When |
|------------|------|-------|------|
| **neutral** | Two solid dots | Upward arc | Default idle state |
| **curious** | One eye slightly larger | Circle (open "o") | Concept arrives, about to absorb |
| **processing** | Horizontal lines (closed) | Wavy line | Digesting a concept |
| **proud** | Upward arcs (happy squint) | Wide upward arc | Absorption complete |
| **alert** | Circles with white fill + dark pupil | Inverted V ("^") | Error, exception, anomaly |

Alert is the only expression with eye-whites — fear "stretches" the eyes open.

### Cap Shape System

Reference shapes (AI can invent new ones following the same principle: shape = structural metaphor):

| Shape | Silhouette | Semantic mapping |
|-------|-----------|-----------------|
| Classic Dome | Standard ellipse | Default, general concepts |
| Flat / Shiitake | Wide, low ellipse | Platform, infrastructure, coverage |
| Pointy / Wizard | Tall cone | Algorithm, logic, security, precision |
| Wavy / Ruffled | Undulating edge | Streaming, async, event-driven |
| Multi-bump | Overlapping circles | Distributed, concurrent, cluster |
| Droopy / Melting | Dripping edges | Cache, memory leak, GC, decay |
| Split / Forked | Two-lobed | Load balancing, branching, A/B test |
| Spiky / Urchin | Triangular protrusions | Firewall, validation, defense |

### Cap Texture System

Reference textures (AI can invent new ones following the same principle: texture = surface pattern mapped to concept characteristics):

| Texture | Visual | Semantic mapping |
|---------|--------|-----------------|
| Classic Spots | Scattered circles, varied size | Default, generic |
| Ridges / Stripes | Vertical lines like gill folds | Ordered flow, sequential |
| Hexagonal | Honeycomb grid | Network topology, distributed nodes |
| Circuit | PCB trace lines + junction dots | Computation, hardware, processing |
| Swirl | Spiral curves | Recursion, loops, cycles |
| Constellation | Dots connected by lines | Node networks, graph structures |
| Scales | Overlapping arcs | Queues, layered/stacked structures |
| Lightning / Cracks | Zigzag paths | Energy bursts, events, interrupts |

### Cap Color Guidelines

Colors should be rich and grounded — no neon, no raw Tailwind palette. Must pair with the cream stem `#F5EDE0`.

The AI selects colors that feel appropriate for the concept domain. No rigid domain→color mapping — just the principle: **saturated but muted, as if the mushroom grew that way naturally**.

### Multi-Mogu System

When a concept has multiple components, use multiple Mogus:

- **Size = importance.** Central component (broker, database) gets a large Mogu; auxiliary roles get small Mogus.
- **Same SVG, different render width.** All Mogus use the identical viewBox and paths. Only the CSS/canvas render size differs.
- **Same cap color = same role.** Three green Mogus = three consumers.
- **Max 3 cap colors per scene.** More than that creates visual chaos.

### Absorption Ceremony

Every generated HTML opens with this ~3 second intro sequence. It is the brand signature.

1. **Idle** — Mogu in default state, red cap, neutral face
2. **Notice** — Concept keywords float toward Mogu; eyes shift to curious (one eye widens, mouth becomes "o")
3. **Swallow** — Cap inflates (ellipse ry increases ~15%), eyes close to processing lines, wavy mouth
4. **Ready** — Cap settles to new color + shape + texture; spots morph to concept icons; face becomes proud

## Workflow

### Phase 1: Conversational Refinement

1. User provides a natural language technical description
2. AI asks 1-2 clarifying questions (audience? which aspect to focus on?)
3. AI produces a **scene script** — a structured intermediate representation:

```
Scene: [title]
Archetype: [pipeline | network | pool | state-machine | guard | tree | race | transform | broadcast | custom]
Actors:
  - [role] ([size], [cap color], [cap shape], [texture])
  ...
Items: [what flows between actors, shape, color]
Parameters:
  - [name]: [type slider|toggle|stepper] [range] [default] [what it affects]
  ...
Key Moments:
  - [trigger] → [visual effect]
  ...
```

### Phase 2: User Confirmation

User reviews the scene script. Can adjust actors, parameters, key moments. AI only proceeds to generation after explicit confirmation.

### Phase 3: HTML Generation

AI reads SKILL.md → references/ → components/, then generates a single self-contained HTML file:

- Canvas 2D for main animation (60fps game loop via requestAnimationFrame)
- DOM overlay for control panel (sliders, toggles, steppers)
- CDN imports optional (GSAP for animation, D3 for data-driven scenes)
- Opens with Absorption Ceremony
- All parameters affect actual system behavior, not just cosmetics

## Scene Archetypes

Reference patterns (AI can combine or invent new ones):

| Archetype | Visual pattern | Example concepts |
|-----------|---------------|-----------------|
| Pipeline | Left→right conveyor, items flow between Mogus | MQ, ETL, CI/CD |
| Network | Mogus as nodes, connections + packets | Microservices, DNS, P2P |
| Pool/Queue | Items stack up, Mogus pick them off | Thread pool, connection pool |
| State Machine | Single Mogu, cap morphs per state transition | TCP states, order flow |
| Guard/Gate | Mogu as gatekeeper, accept/reject | Auth, firewall, validation |
| Tree | Parent-child Mogu hierarchy | DOM, filesystem, B-tree |
| Race | Multiple Mogus on parallel tracks | Thread contention, locks, deadlock |
| Transform | Item enters one side of Mogu, exits transformed | Encryption, compilation, serialization |
| Broadcast | One Mogu emits to many | Pub/Sub, event bus, webhooks |

## Interaction & Animation Principles

### Interaction

- Every scene exposes **2-3+ adjustable parameters** (sliders, toggles, steppers)
- Parameters must **genuinely change system behavior** — not cosmetic
- Control panel overlaid on canvas edge, never obscuring core animation
- Real-time response to parameter changes, no restart needed

### Animation

- **Idle bounce:** Mogu has subtle y-axis sinusoidal oscillation (~2px, period 2-3s)
- **Squash & stretch:** On receiving items, body compresses then springs back
- **Cap pulse:** Spots glow/pulse when processing
- **Eye tracking:** Eyes look toward the nearest moving object in the scene
- **Eased motion:** Items move along paths with ease-in-out, never linear
- **Error flash:** On error, Mogu switches to alert expression + cap briefly flashes red
- **Ambient life:** Scene is never fully static — always some ambient particle or subtle motion

### Rendering

- Canvas 2D for the main scene (game loop at 60fps)
- DOM overlay for UI controls
- Mogu drawn via function: `drawMogu(ctx, x, y, size, capColor, capShape, texture, expression)`
- Optional CDN: GSAP (animation easing), D3 (data-driven layouts)

## Quality Gate

Check before delivering generated HTML:

| Check | Failure symptom | Fix |
|-------|----------------|-----|
| Character consistency | Mogu proportions wrong, missing cap highlight or feet | Compare against canonical SVG ratios |
| Interactivity works | Sliders/controls don't affect animation | Bind parameters to game loop variables |
| Animation smoothness | Stuttering, teleporting items | Use requestAnimationFrame, not setInterval |
| Concept accuracy | Visualization doesn't match the technical concept | Re-examine scene script mapping |
| Self-contained | White screen or errors on open | Verify CDN links, no local dependencies |
| Not a dead scene | Nothing moves without interaction | Add idle bounce + ambient particles |
| Not skin-deep | Changing params only changes color, not behavior | Parameters must affect data flow/rate/count |

## Skill File Structure

```
mogu-visual/
├── SKILL.md                    # Main prompt guide (AI reads this first)
├── references/
│   ├── character.md            # Mogu spec: canonical SVG, proportions, expressions, cap system
│   ├── scenes.md               # Scene archetypes with visual patterns
│   ├── interactions.md         # Interaction components: sliders, toggles, timeline
│   └── examples.md             # 3-5 complete examples (MQ, load balancer, encryption, etc.)
├── components/
│   ├── mogu.svg                # Canonical Mogu SVG reference
│   ├── mogu-expressions.svg    # All 5 expression variants on full Mogu
│   └── widgets.js              # Reusable code snippets (drawMogu function, game loop, controls)
```

**SKILL.md** is the entry point AI reads every time. It contains the workflow, links to references, and the core rules. References are read on-demand for depth. Components are code snippets AI can copy and adapt into generated HTML.
