# Mogu Character System — Deep Reference

This is the canonical reference for the Mogu character design system. Read this when you need exact proportions, expression rules, cap shape/texture options, multi-Mogu composition rules, or the absorption ceremony sequence.

---

## 1. Canonical SVG Reference

**Source of truth:** `mogu-visual/components/mogu.svg`

The SVG defines the character in a 140×170 viewBox. All measurements below are in SVG units.

| Element | Attributes | Notes |
|---------|------------|-------|
| Stem | `<rect x="50" y="95" width="40" height="50" rx="14" fill="#F5EDE0"/>` | Rounded rectangle, soft corners |
| Cap | `<ellipse cx="70" cy="82" rx="52" ry="38" fill="#FF4D4D"/>` | Dominant dome, 2.6× wider than stem |
| Cap highlight | `<ellipse cx="55" cy="68" rx="18" ry="10" fill="#FF7070" opacity="0.5"/>` | Upper-left shift, subtle polish |
| Spot 1 | `<circle cx="42" cy="72" r="6" fill="#FF8080" opacity="0.7"/>` | Scattered, varied sizes |
| Spot 2 | `<circle cx="68" cy="55" r="5" fill="#FF8080" opacity="0.7"/>` | |
| Spot 3 | `<circle cx="90" cy="68" r="7" fill="#FF8080" opacity="0.7"/>` | |
| Eye (left) | `<circle cx="60" cy="115" r="4.5" fill="#0a0a0a"/>` | Solid black dots |
| Eye (right) | `<circle cx="80" cy="115" r="4.5" fill="#0a0a0a"/>` | |
| Mouth | `<path d="M63,127 Q70,133 77,127" stroke="#0a0a0a" stroke-width="2.5" fill="none" stroke-linecap="round"/>` | Upward arc (neutral) |
| Feet (left) | `<ellipse cx="58" cy="145" rx="10" ry="4" fill="#EBE0D0"/>` | Grounding ellipses |
| Feet (right) | `<ellipse cx="82" cy="145" rx="10" ry="4" fill="#EBE0D0"/>` | |

---

## 2. Proportions (Scale-Independent Ratios)

These ratios hold at any render size:

| Ratio | Value | Notes |
|-------|-------|-------|
| Cap width / Stem width | 2.6× | Cap `rx=52`, stem `width=40` → 104/40 = 2.6 |
| Cap height / Total height | ~45% | Cap zone: 82±38 = 44–120, total height 170 → 76/170 ≈ 45% |
| Stem height / Total height | ~30% | Stem: y=95 to 145, height 50 → 50/170 ≈ 29% |
| Feet zone / Total height | ~15% | Feet at y=145±4 = 141–149 → 25/170 ≈ 15% |
| Eye spacing | Stem width × 50% | Eyes at x=60 and x=80, spacing=20, stem width=40 → 20/40 = 50% |
| Mouth below eyes | Stem height × 24% | Eyes at y=115, mouth at y=127, offset=12 → 12/50 = 24% |
| Eye radius | Stem width × 11% | Eye `r=4.5`, stem width=40 → 4.5/40 ≈ 11% |

---

## 3. Invariants (Never Change)

These values are fixed for all Mogus:

- **Stem fill:** `#F5EDE0` (warm cream)
- **Eyes fill:** `#0a0a0a` (near-black)
- **Eye radius:** `stem_width × 11%` (≈4.5 at canonical scale)
- **Feet fill:** `#EBE0D0` (slightly darker cream)
- **Cap highlight:** cap color lightened 20%, opacity 0.5
- **Spot color (default texture):** cap color lightened 25%, opacity 0.7

**Do not change:**
- Stem or feet colors
- Eye color (black dots in all expressions except alert, which adds whites)
- Proportions listed above

---

## 4. Expression System

**Rule:** Only eyes and mouth change. No new elements. Alert is the only expression with eye-whites.

### 4.1 Neutral

**When to use:** Default, idle, at rest, no active task.

**SVG:**
```svg
<!-- Eyes: solid dots -->
<circle cx="60" cy="115" r="4.5" fill="#0a0a0a"/>
<circle cx="80" cy="115" r="4.5" fill="#0a0a0a"/>
<!-- Mouth: upward arc -->
<path d="M63,127 Q70,133 77,127" stroke="#0a0a0a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
```

**Canvas 2D (in canonical scale `s = size / 170`):**
```javascript
// Eyes
ctx.fillStyle = '#0a0a0a';
ctx.beginPath();
ctx.arc(60 * s, 115 * s, 4.5 * s, 0, Math.PI * 2);
ctx.fill();
ctx.beginPath();
ctx.arc(80 * s, 115 * s, 4.5 * s, 0, Math.PI * 2);
ctx.fill();
// Mouth
ctx.strokeStyle = '#0a0a0a';
ctx.lineWidth = 2.5 * s;
ctx.lineCap = 'round';
ctx.beginPath();
ctx.moveTo(63 * s, 127 * s);
ctx.quadraticCurveTo(70 * s, 133 * s, 77 * s, 127 * s);
ctx.stroke();
```

---

### 4.2 Curious

**When to use:** Encountering new input, reading keywords, inspecting data.

**SVG:**
```svg
<!-- Left eye: normal -->
<circle cx="60" cy="115" r="4.5" fill="#0a0a0a"/>
<!-- Right eye: bigger, shifted up -->
<circle cx="80" cy="113" r="5.5" fill="#0a0a0a"/>
<!-- Mouth: small circle "o" -->
<circle cx="70" cy="129" r="3.5" stroke="#0a0a0a" stroke-width="2.5" fill="none"/>
```

**Canvas 2D:**
```javascript
ctx.fillStyle = '#0a0a0a';
// Left eye: normal
ctx.beginPath();
ctx.arc(60 * s, 115 * s, 4.5 * s, 0, Math.PI * 2);
ctx.fill();
// Right eye: bigger, shifted up
ctx.beginPath();
ctx.arc(80 * s, 113 * s, 5.5 * s, 0, Math.PI * 2);
ctx.fill();
// Mouth: small circle
ctx.strokeStyle = '#0a0a0a';
ctx.lineWidth = 2.5 * s;
ctx.beginPath();
ctx.arc(70 * s, 129 * s, 3.5 * s, 0, Math.PI * 2);
ctx.stroke();
```

---

### 4.3 Processing

**When to use:** Actively computing, transforming, analyzing.

**SVG:**
```svg
<!-- Eyes: horizontal lines -->
<line x1="54" y1="115" x2="66" y2="115" stroke="#0a0a0a" stroke-width="3" stroke-linecap="round"/>
<line x1="74" y1="115" x2="86" y2="115" stroke="#0a0a0a" stroke-width="3" stroke-linecap="round"/>
<!-- Mouth: wavy line -->
<path d="M60,128 Q65,124 70,128 Q75,132 80,128" stroke="#0a0a0a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
```

**Canvas 2D:**
```javascript
ctx.strokeStyle = '#0a0a0a';
ctx.lineWidth = 3 * s;
ctx.lineCap = 'round';
// Left eye
ctx.beginPath();
ctx.moveTo(54 * s, 115 * s);
ctx.lineTo(66 * s, 115 * s);
ctx.stroke();
// Right eye
ctx.beginPath();
ctx.moveTo(74 * s, 115 * s);
ctx.lineTo(86 * s, 115 * s);
ctx.stroke();
// Mouth: wavy
ctx.lineWidth = 2.5 * s;
ctx.beginPath();
ctx.moveTo(60 * s, 128 * s);
ctx.quadraticCurveTo(65 * s, 124 * s, 70 * s, 128 * s);
ctx.quadraticCurveTo(75 * s, 132 * s, 80 * s, 128 * s);
ctx.stroke();
```

---

### 4.4 Proud

**When to use:** Task complete, output delivered, success.

**SVG:**
```svg
<!-- Eyes: upward arcs (happy squint) -->
<path d="M55,114 Q60,110 65,114" stroke="#0a0a0a" stroke-width="3" fill="none" stroke-linecap="round"/>
<path d="M75,114 Q80,110 85,114" stroke="#0a0a0a" stroke-width="3" fill="none" stroke-linecap="round"/>
<!-- Mouth: wide grin -->
<path d="M60,126 Q70,136 80,126" stroke="#0a0a0a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
```

**Canvas 2D:**
```javascript
ctx.strokeStyle = '#0a0a0a';
ctx.lineWidth = 3 * s;
ctx.lineCap = 'round';
// Left eye
ctx.beginPath();
ctx.moveTo(55 * s, 114 * s);
ctx.quadraticCurveTo(60 * s, 110 * s, 65 * s, 114 * s);
ctx.stroke();
// Right eye
ctx.beginPath();
ctx.moveTo(75 * s, 114 * s);
ctx.quadraticCurveTo(80 * s, 110 * s, 85 * s, 114 * s);
ctx.stroke();
// Mouth: wide grin
ctx.lineWidth = 2.5 * s;
ctx.beginPath();
ctx.moveTo(60 * s, 126 * s);
ctx.quadraticCurveTo(70 * s, 136 * s, 80 * s, 126 * s);
ctx.stroke();
```

---

### 4.5 Alert

**When to use:** Error, warning, high-priority signal, unexpected input.

**SVG:**
```svg
<!-- Eye whites -->
<circle cx="60" cy="113" r="6" fill="#ffffff"/>
<circle cx="80" cy="113" r="6" fill="#ffffff"/>
<!-- Pupils -->
<circle cx="61" cy="114" r="3.5" fill="#0a0a0a"/>
<circle cx="81" cy="114" r="3.5" fill="#0a0a0a"/>
<!-- Mouth: inverted-V -->
<path d="M64,129 L70,124 L76,129" stroke="#0a0a0a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
```

**Canvas 2D:**
```javascript
// Eye whites
ctx.fillStyle = '#ffffff';
ctx.beginPath();
ctx.arc(60 * s, 113 * s, 6 * s, 0, Math.PI * 2);
ctx.fill();
ctx.beginPath();
ctx.arc(80 * s, 113 * s, 6 * s, 0, Math.PI * 2);
ctx.fill();
// Pupils
ctx.fillStyle = '#0a0a0a';
ctx.beginPath();
ctx.arc(61 * s, 114 * s, 3.5 * s, 0, Math.PI * 2);
ctx.fill();
ctx.beginPath();
ctx.arc(81 * s, 114 * s, 3.5 * s, 0, Math.PI * 2);
ctx.fill();
// Mouth: inverted-V
ctx.strokeStyle = '#0a0a0a';
ctx.lineWidth = 2.5 * s;
ctx.lineCap = 'round';
ctx.beginPath();
ctx.moveTo(64 * s, 129 * s);
ctx.lineTo(70 * s, 124 * s);
ctx.lineTo(76 * s, 129 * s);
ctx.stroke();
```

---

## 5. Cap Shape System

**Principle:** Shape = structural metaphor for the concept.

AI can invent new shapes beyond these 8 references. Each shape function receives:
- `ctx` — Canvas 2D context
- `cx, cy` — cap center position (scaled)
- `capRx, capRy` — cap ellipse radii (scaled)

The function must call `ctx.beginPath()`, draw the path, and leave it open for the caller to fill.

---

### 5.1 Classic Dome (Default)

**Silhouette:** Standard ellipse.

**Semantic mapping:** Default, general-purpose, no specific structure.

**Canvas 2D:**
```javascript
function classicDome(ctx, cx, cy, capRx, capRy) {
  ctx.beginPath();
  ctx.ellipse(cx, cy, capRx, capRy, 0, 0, Math.PI * 2);
}
```

---

### 5.2 Flat / Shiitake

**Silhouette:** Wide, low ellipse (squashed dome).

**Semantic mapping:** Platform, infrastructure, foundation, database.

**Canvas 2D:**
```javascript
function flatCap(ctx, cx, cy, capRx, capRy) {
  ctx.beginPath();
  ctx.ellipse(cx, cy, capRx, capRy * 0.6, 0, 0, Math.PI * 2);
}
```

---

### 5.3 Pointy / Wizard

**Silhouette:** Tall cone.

**Semantic mapping:** Algorithm, logic, security, encryption, decision tree.

**Canvas 2D:**
```javascript
function pointyCap(ctx, cx, cy, capRx, capRy) {
  ctx.beginPath();
  ctx.moveTo(cx - capRx, cy + capRy * 0.3);
  ctx.quadraticCurveTo(cx, cy - capRy * 1.2, cx + capRx, cy + capRy * 0.3);
  ctx.lineTo(cx - capRx, cy + capRy * 0.3);
}
```

---

### 5.4 Wavy / Ruffled

**Silhouette:** Undulating edge.

**Semantic mapping:** Streaming, async, event-driven, reactive, real-time.

**Canvas 2D:**
```javascript
function wavyCap(ctx, cx, cy, capRx, capRy) {
  ctx.beginPath();
  var steps = 12;
  for (var i = 0; i <= steps; i++) {
    var angle = (i / steps) * Math.PI * 2;
    var wave = Math.sin(angle * 4) * capRy * 0.15;
    var x = cx + Math.cos(angle) * (capRx + wave);
    var y = cy + Math.sin(angle) * (capRy + wave);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
}
```

---

### 5.5 Multi-bump

**Silhouette:** Overlapping circles (three lobes).

**Semantic mapping:** Distributed systems, concurrent processes, clustering, microservices.

**Canvas 2D:**
```javascript
function multiBumpCap(ctx, cx, cy, capRx, capRy) {
  var r = capRx * 0.5;
  ctx.beginPath();
  ctx.arc(cx - capRx * 0.4, cy, r, 0, Math.PI * 2);
  ctx.arc(cx + capRx * 0.4, cy, r, 0, Math.PI * 2);
  ctx.arc(cx, cy - capRy * 0.3, r, 0, Math.PI * 2);
}
```

---

### 5.6 Droopy / Melting

**Silhouette:** Dripping edges.

**Semantic mapping:** Cache overflow, memory leak, garbage collection, degradation.

**Canvas 2D:**
```javascript
function droopyCap(ctx, cx, cy, capRx, capRy) {
  ctx.beginPath();
  ctx.ellipse(cx, cy, capRx, capRy, 0, Math.PI, 0, true); // top arc
  // Bottom drips
  ctx.quadraticCurveTo(cx + capRx * 0.8, cy + capRy * 1.5, cx + capRx * 0.6, cy + capRy);
  ctx.quadraticCurveTo(cx + capRx * 0.2, cy + capRy * 1.3, cx, cy + capRy);
  ctx.quadraticCurveTo(cx - capRx * 0.2, cy + capRy * 1.3, cx - capRx * 0.6, cy + capRy);
  ctx.quadraticCurveTo(cx - capRx * 0.8, cy + capRy * 1.5, cx - capRx, cy);
  ctx.closePath();
}
```

---

### 5.7 Split / Forked

**Silhouette:** Two-lobed, split down the middle.

**Semantic mapping:** Load balancing, branching logic, A/B testing, version fork.

**Canvas 2D:**
```javascript
function splitCap(ctx, cx, cy, capRx, capRy) {
  var offset = capRx * 0.3;
  ctx.beginPath();
  // Left lobe
  ctx.ellipse(cx - offset, cy, capRx * 0.6, capRy, 0, 0, Math.PI * 2);
  ctx.closePath();
  ctx.beginPath();
  // Right lobe
  ctx.ellipse(cx + offset, cy, capRx * 0.6, capRy, 0, 0, Math.PI * 2);
}
```

---

### 5.8 Spiky / Urchin

**Silhouette:** Triangular protrusions radiating outward.

**Semantic mapping:** Firewall, defense, security perimeter, rate limiting, DDoS protection.

**Canvas 2D:**
```javascript
function spikyCap(ctx, cx, cy, capRx, capRy) {
  ctx.beginPath();
  var spikes = 8;
  for (var i = 0; i < spikes; i++) {
    var angle = (i / spikes) * Math.PI * 2;
    var nextAngle = ((i + 1) / spikes) * Math.PI * 2;
    var midAngle = (angle + nextAngle) / 2;
    // Inner point
    var x1 = cx + Math.cos(angle) * capRx * 0.7;
    var y1 = cy + Math.sin(angle) * capRy * 0.7;
    // Spike tip
    var x2 = cx + Math.cos(midAngle) * capRx * 1.2;
    var y2 = cy + Math.sin(midAngle) * capRy * 1.2;
    if (i === 0) ctx.moveTo(x1, y1);
    else ctx.lineTo(x1, y1);
    ctx.lineTo(x2, y2);
  }
  ctx.closePath();
}
```

---

## 6. Cap Texture System

**Principle:** Texture = surface pattern mapped to concept characteristics.

AI can invent new textures. Each texture function receives:
- `ctx` — Canvas 2D context
- `cx, cy` — cap center position (scaled)
- `capRx, capRy` — cap ellipse radii (scaled)
- `spotColor` — derived color (cap lightened 25%)

The function should set `ctx.globalAlpha = 0.7` and draw the pattern, then restore `ctx.globalAlpha = 1.0`.

---

### 6.1 Classic Spots (Default)

**Visual:** Scattered circles, varied sizes, uneven distribution.

**Semantic mapping:** Default, general-purpose.

**Canvas 2D:**
```javascript
function classicSpots(ctx, cx, cy, capRx, capRy, spotColor) {
  ctx.globalAlpha = 0.7;
  ctx.fillStyle = spotColor;
  ctx.beginPath();
  ctx.arc(cx - capRx * 0.5, cy - capRy * 0.3, capRx * 0.12, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(cx - capRx * 0.05, cy - capRy * 0.7, capRx * 0.1, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(cx + capRx * 0.4, cy - capRy * 0.35, capRx * 0.13, 0, Math.PI * 2);
  ctx.fill();
  ctx.globalAlpha = 1.0;
}
```

---

### 6.2 Ridges / Stripes

**Visual:** Vertical lines, evenly spaced.

**Semantic mapping:** Ordered flow, pipeline, assembly line, sequential processing.

**Canvas 2D:**
```javascript
function ridgesTexture(ctx, cx, cy, capRx, capRy, spotColor) {
  ctx.globalAlpha = 0.7;
  ctx.strokeStyle = spotColor;
  ctx.lineWidth = capRx * 0.04;
  var count = 5;
  for (var i = -count; i <= count; i++) {
    var x = cx + (i / count) * capRx * 0.8;
    ctx.beginPath();
    ctx.moveTo(x, cy - capRy * 0.8);
    ctx.lineTo(x, cy + capRy * 0.5);
    ctx.stroke();
  }
  ctx.globalAlpha = 1.0;
}
```

---

### 6.3 Hexagonal

**Visual:** Honeycomb grid.

**Semantic mapping:** Network topology, mesh, peer-to-peer, graph structure.

**Canvas 2D:**
```javascript
function hexagonalTexture(ctx, cx, cy, capRx, capRy, spotColor) {
  ctx.globalAlpha = 0.7;
  ctx.strokeStyle = spotColor;
  ctx.lineWidth = capRx * 0.03;
  var hexSize = capRx * 0.2;
  var positions = [
    [cx - hexSize, cy - hexSize * 0.6],
    [cx + hexSize, cy - hexSize * 0.6],
    [cx, cy],
    [cx - hexSize, cy + hexSize * 0.6],
    [cx + hexSize, cy + hexSize * 0.6]
  ];
  positions.forEach(function(pos) {
    ctx.beginPath();
    for (var i = 0; i < 6; i++) {
      var angle = (i / 6) * Math.PI * 2;
      var x = pos[0] + Math.cos(angle) * hexSize * 0.5;
      var y = pos[1] + Math.sin(angle) * hexSize * 0.5;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
  });
  ctx.globalAlpha = 1.0;
}
```

---

### 6.4 Circuit

**Visual:** PCB trace lines + dots (nodes).

**Semantic mapping:** Computation, digital logic, circuits, CPU, binary operations.

**Canvas 2D:**
```javascript
function circuitTexture(ctx, cx, cy, capRx, capRy, spotColor) {
  ctx.globalAlpha = 0.7;
  ctx.strokeStyle = spotColor;
  ctx.lineWidth = capRx * 0.025;
  // Traces
  ctx.beginPath();
  ctx.moveTo(cx - capRx * 0.6, cy - capRy * 0.4);
  ctx.lineTo(cx - capRx * 0.2, cy - capRy * 0.4);
  ctx.lineTo(cx - capRx * 0.2, cy);
  ctx.lineTo(cx + capRx * 0.3, cy);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(cx + capRx * 0.3, cy - capRy * 0.6);
  ctx.lineTo(cx + capRx * 0.3, cy + capRy * 0.2);
  ctx.stroke();
  // Nodes
  ctx.fillStyle = spotColor;
  ctx.beginPath();
  ctx.arc(cx - capRx * 0.2, cy - capRy * 0.4, capRx * 0.06, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(cx + capRx * 0.3, cy, capRx * 0.06, 0, Math.PI * 2);
  ctx.fill();
  ctx.globalAlpha = 1.0;
}
```

---

### 6.5 Swirl

**Visual:** Spiral curves.

**Semantic mapping:** Recursion, loops, iteration, cycles, spin-locks.

**Canvas 2D:**
```javascript
function swirlTexture(ctx, cx, cy, capRx, capRy, spotColor) {
  ctx.globalAlpha = 0.7;
  ctx.strokeStyle = spotColor;
  ctx.lineWidth = capRx * 0.04;
  ctx.lineCap = 'round';
  ctx.beginPath();
  var turns = 2;
  var steps = 40;
  for (var i = 0; i <= steps; i++) {
    var t = i / steps;
    var angle = t * Math.PI * 2 * turns;
    var radius = t * capRx * 0.6;
    var x = cx + Math.cos(angle) * radius;
    var y = cy + Math.sin(angle) * radius * (capRy / capRx);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();
  ctx.globalAlpha = 1.0;
}
```

---

### 6.6 Constellation

**Visual:** Dots connected by lines.

**Semantic mapping:** Node networks, service mesh, graph connections, distributed nodes.

**Canvas 2D:**
```javascript
function constellationTexture(ctx, cx, cy, capRx, capRy, spotColor) {
  ctx.globalAlpha = 0.7;
  var nodes = [
    [cx - capRx * 0.4, cy - capRy * 0.5],
    [cx + capRx * 0.3, cy - capRy * 0.4],
    [cx - capRx * 0.2, cy + capRy * 0.1],
    [cx + capRx * 0.4, cy + capRy * 0.2],
    [cx, cy - capRy * 0.1]
  ];
  // Lines
  ctx.strokeStyle = spotColor;
  ctx.lineWidth = capRx * 0.02;
  ctx.beginPath();
  ctx.moveTo(nodes[0][0], nodes[0][1]);
  ctx.lineTo(nodes[4][0], nodes[4][1]);
  ctx.lineTo(nodes[1][0], nodes[1][1]);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(nodes[2][0], nodes[2][1]);
  ctx.lineTo(nodes[4][0], nodes[4][1]);
  ctx.lineTo(nodes[3][0], nodes[3][1]);
  ctx.stroke();
  // Dots
  ctx.fillStyle = spotColor;
  nodes.forEach(function(node) {
    ctx.beginPath();
    ctx.arc(node[0], node[1], capRx * 0.05, 0, Math.PI * 2);
    ctx.fill();
  });
  ctx.globalAlpha = 1.0;
}
```

---

### 6.7 Scales

**Visual:** Overlapping arcs.

**Semantic mapping:** Queues, layered structures, stacks, buffers, pagination.

**Canvas 2D:**
```javascript
function scalesTexture(ctx, cx, cy, capRx, capRy, spotColor) {
  ctx.globalAlpha = 0.7;
  ctx.strokeStyle = spotColor;
  ctx.lineWidth = capRx * 0.03;
  var rows = 3;
  var cols = 4;
  var scaleW = capRx * 0.3;
  var scaleH = capRy * 0.25;
  for (var row = 0; row < rows; row++) {
    for (var col = 0; col < cols; col++) {
      var x = cx + (col - cols / 2 + 0.5) * scaleW * 0.8;
      var y = cy + (row - rows / 2 + 0.5) * scaleH * 0.7;
      ctx.beginPath();
      ctx.arc(x, y, scaleW * 0.4, 0, Math.PI, true);
      ctx.stroke();
    }
  }
  ctx.globalAlpha = 1.0;
}
```

---

### 6.8 Lightning / Cracks

**Visual:** Zigzag paths.

**Semantic mapping:** Energy, events, interrupts, exceptions, lightning-fast, error propagation.

**Canvas 2D:**
```javascript
function lightningTexture(ctx, cx, cy, capRx, capRy, spotColor) {
  ctx.globalAlpha = 0.7;
  ctx.strokeStyle = spotColor;
  ctx.lineWidth = capRx * 0.04;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'miter';
  // Bolt 1
  ctx.beginPath();
  ctx.moveTo(cx - capRx * 0.3, cy - capRy * 0.6);
  ctx.lineTo(cx - capRx * 0.1, cy - capRy * 0.2);
  ctx.lineTo(cx - capRx * 0.25, cy - capRy * 0.1);
  ctx.lineTo(cx - capRx * 0.05, cy + capRy * 0.3);
  ctx.stroke();
  // Bolt 2
  ctx.beginPath();
  ctx.moveTo(cx + capRx * 0.4, cy - capRy * 0.5);
  ctx.lineTo(cx + capRx * 0.2, cy - capRy * 0.1);
  ctx.lineTo(cx + capRx * 0.35, cy);
  ctx.lineTo(cx + capRx * 0.15, cy + capRy * 0.4);
  ctx.stroke();
  ctx.globalAlpha = 1.0;
}
```

---

## 7. Cap Color Guidelines

**Principle:** Colors should be saturated but muted — "as if the mushroom grew that way naturally". Must pair harmoniously with the cream stem (`#F5EDE0`).

**No rigid domain→color mapping.** Instead, choose from these curated palette suggestions, or invent new colors following the same saturation/brightness principles.

### Curated Cap Color Palette

| Color | Hex | Semantic Suggestions |
|-------|-----|----------------------|
| Red | `#FF4D4D` | Default, error, alert, critical path, fire |
| Orange | `#FF8C42` | Warmth, activity, build, deployment, queue |
| Amber | `#FFB84D` | Warning, caution, cache, fallback |
| Yellow | `#FFD966` | Highlight, indexing, search, brightness |
| Lime | `#A3D977` | Growth, scaling, optimization, eco-mode |
| Green | `#52C77A` | Success, health, pass, ready, active |
| Teal | `#4DBFBF` | Flow, streaming, data pipeline, fresh |
| Sky Blue | `#5BA3E0` | Cloud, API, interface, communication |
| Blue | `#5680E0` | Logic, stable, default service, core |
| Indigo | `#7B68EE` | Deep computation, AI/ML, complex algorithm |
| Purple | `#A66FD9` | Magic, transformation, middleware, orchestration |
| Magenta | `#E066A6` | Creative, UX, frontend, design system |
| Pink | `#FF6B9D` | Playful, user-facing, delight, animation |
| Brown | `#A67C52` | Persistence, storage, database, logs |
| Gray | `#8C8C8C` | Neutral, deprecated, archived, inactive |

**When choosing colors:**
- Avoid neon/fluorescent tones (too harsh)
- Avoid very dark colors (lost detail against dark UIs)
- Test against the cream stem to ensure contrast and harmony
- Use hue shifts to differentiate related concepts (e.g., blue → indigo for deeper logic)

---

## 8. Multi-Mogu Rules

When multiple Mogus appear in a single scene (e.g., system architecture diagram):

1. **Size = Importance**
   - Central or primary component → largest Mogu
   - Supporting services → medium
   - Utilities or helpers → small
   - Use the same SVG, just vary `size` parameter in `drawMogu()`

2. **Same Cap Color = Same Role**
   - All API services → same blue
   - All databases → same brown
   - All caches → same amber
   - This creates instant visual grouping

3. **Max 3 Cap Colors Per Scene**
   - Exceeding 3 colors creates visual noise
   - If you need more than 3 groups, use size + shape variation instead
   - Exception: absorption ceremony intro can use >3 colors for keyword diversity

4. **Spatial Arrangement**
   - Data flow: left → right (input → output)
   - Hierarchy: top → bottom (control → execution)
   - Peer services: horizontal row, equal size

5. **Same Cap Shape/Texture = Same Structure Type**
   - All async services → wavy cap
   - All distributed components → multi-bump cap
   - All security layers → spiky cap
   - This reinforces the structural metaphor

---

## 9. Absorption Ceremony

The **Absorption Ceremony** is the 4-step brand intro sequence. It shows a Mogu encountering a new concept, absorbing it, and transforming into its semantic form.

**Total duration:** 3 seconds  
**Framerate:** 60 fps (use `requestAnimationFrame`)

---

### Step 1: Idle (0–0.8s)

**State:**
- Cap color: `#FF4D4D` (red)
- Expression: `neutral`
- Cap shape: classic dome
- Cap texture: classic spots
- Y-offset: sinusoidal idle bounce (±2px, 2.5s period)

**Notes:** The Mogu is at rest, unaware of the incoming concept.

---

### Step 2: Notice (0.8–1.5s)

**State:**
- Expression: `curious`
- Keywords float in from the right (slide + fade)
  - Font: `16px 'SF Mono', 'Monaco', monospace`
  - Color: `#aaa`
  - Stagger: 0.1s between each keyword
  - Movement: translate from `x + 100px` to `x`, ease-out
  - Opacity: 0 → 1, ease-out
- Y-offset: idle bounce continues

**Notes:** The Mogu notices the new concept. Keywords orbit or approach the cap.

---

### Step 3: Swallow (1.5–2.2s)

**State:**
- Expression: `processing`
- Cap inflates: `capRy` increases by 15% (spring easing with overshoot)
  - Peak at 1.8s, settle by 2.2s
- Keywords: scale down + move toward cap center, then fade out
  - Scale: 1 → 0, ease-in
  - Opacity: 1 → 0, ease-in
- Cap pulses gently (subtle opacity or scale fluctuation)

**Notes:** The Mogu absorbs the concept. Visual metaphor: the cap "eats" the keywords.

---

### Step 4: Ready (2.2–3.0s)

**State:**
- Expression: `proud`
- Cap color: transition to final semantic color (ease-out, 0.5s)
- Cap shape: morph to final semantic shape (if applicable, ease-out, 0.5s)
- Cap texture: cross-fade to final texture (if applicable, 0.3s)
- `capRy`: return to normal (ease-out, 0.3s)
- Y-offset: one final bounce (small hop, 0.2s)

**Notes:** Transformation complete. The Mogu is now the concept.

---

### Animation Implementation Notes

**Easing functions:** Use the `ease` object from `widgets.js`:
- `ease.out` — for most transitions (smooth deceleration)
- `ease.spring` — for cap inflation in step 3 (overshoot effect)

**Timing control:**
```javascript
var time = 0; // seconds, incremented each frame by dt

// Example progress calculation for step 3 (swallow)
if (time >= 1.5 && time < 2.2) {
  var stepTime = time - 1.5;
  var stepDuration = 0.7;
  var t = Math.min(stepTime / stepDuration, 1);
  var inflateAmount = ease.spring(t, 0.5); // spring overshoot
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

// Usage in step 4:
if (time >= 2.2 && time < 2.7) {
  var stepTime = time - 2.2;
  var t = ease.out(stepTime / 0.5);
  capColor = lerpColor('#FF4D4D', finalColor, t);
}
```

---

## Summary

This document defines the Mogu character system at the code level. When generating Mogu visualizations:

1. **Proportions and invariants** (§2–3) are fixed — never change them.
2. **Expressions** (§4) convey state — choose based on the task phase.
3. **Cap shapes** (§5) encode structural metaphors — match concept architecture.
4. **Cap textures** (§6) encode surface characteristics — match concept behavior.
5. **Cap colors** (§7) follow the curated palette — no rigid mapping, but stay harmonious.
6. **Multi-Mogu scenes** (§8) use size, color, and shape to show relationships.
7. **Absorption ceremony** (§9) is the brand intro — use it when introducing Mogu for the first time.

All drawing code is Canvas 2D compatible and works with the `drawMogu()` function signature in `mogu-visual/components/widgets.js`.
