# Interactions Reference

Complete guide to interactive controls and animation patterns for Mogu Visual.

All code examples are copy-paste ready and compatible with `widgets.js`.

---

## 1. Control Selection Guide

Choose the right control type for your parameter:

### Slider
**Use for:** Continuous values where fine-grained control matters.

**Examples:**
- Message spawn rate (0.5 - 50 messages/sec)
- Animation speed multiplier (0.1 - 5.0x)
- Threshold values (0 - 100%)
- Opacity/alpha (0 - 1.0)

**When to use:** The range is wide and intermediate values are meaningful. Users need to scrub through values to find the right setting.

### Toggle
**Use for:** Boolean on/off states or mode switches.

**Examples:**
- Enable/disable idle bounce
- Show/hide debug info
- Pause/resume simulation
- Toggle algorithm variants (e.g., random vs. priority-based routing)

**When to use:** There are exactly two states with no middle ground.

### Stepper
**Use for:** Discrete integer values where only specific integers make sense.

**Examples:**
- Number of Mogu characters (2 - 10)
- Number of grid partitions (2, 3, 4, ...)
- Maximum queue depth (1, 2, 3, ...)
- Animation frame count

**When to use:** The parameter is inherently discrete (you can't have 3.7 characters) or only certain integers are meaningful.

---

## 2. Control Panel Layout

### Fixed Overlay Panel Pattern

A semi-transparent dark panel that never obscures more than 20% of the canvas.

#### HTML Structure

```html
<div id="panel" class="control-panel"></div>
```

#### CSS (Complete)

```css
.control-panel {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 280px;
  max-height: 80vh;
  overflow-y: auto;
  background: rgba(10, 10, 10, 0.85);
  border-radius: 8px;
  padding: 16px;
  backdrop-filter: blur(8px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  font-family: system-ui, -apple-system, sans-serif;
}

/* Scrollbar styling */
.control-panel::-webkit-scrollbar {
  width: 8px;
}

.control-panel::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.control-panel::-webkit-scrollbar-thumb {
  background: rgba(255, 77, 77, 0.5);
  border-radius: 4px;
}

.control-panel::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 77, 77, 0.7);
}

/* Optional: panel header */
.panel-header {
  font-size: 14px;
  font-weight: 600;
  color: #eee;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
```

#### Sidebar Variant (Left Side)

For left-side placement, adjust:

```css
.control-panel {
  left: 20px;
  right: auto;
  bottom: 20px;
}
```

---

## 3. Parameter Binding Pattern

Complete example showing how slider values flow into the game loop.

```javascript
// --- State object ---
const state = {
  messageRate: 10,    // messages per second
  idleBounce: true,
  maxQueue: 5
};

// --- Control panel setup ---
const panel = document.getElementById('panel');

createSlider(panel, 'Message Rate', 1, 100, 10, 1, (v) => {
  state.messageRate = v;
});

createToggle(panel, 'Idle Bounce', true, (v) => {
  state.idleBounce = v;
});

createStepper(panel, 'Max Queue', 1, 20, 5, (v) => {
  state.maxQueue = v;
});

// --- Game loop integration ---
let spawnTimer = 0;
let time = 0;

function update(dt) {
  time += dt;
  spawnTimer += dt;

  // Use state.messageRate to control spawn timing
  const spawnInterval = 1 / state.messageRate;
  if (spawnTimer > spawnInterval) {
    spawnMessage();
    spawnTimer = 0;
  }

  // Use state.maxQueue to limit queue size
  messages = messages.slice(0, state.maxQueue);
}

function draw(ctx, width, height) {
  const baseY = height / 2;
  const yOffset = state.idleBounce ? idleBounce(time, 2.5, 3) : 0;

  drawMogu(ctx, width / 2, baseY + yOffset, 120, '#FF4D4D', 'neutral');
}
```

**Key pattern:** Controls mutate a shared `state` object, and update/draw functions read from it each frame.

---

## 4. Animation Principles with Code

### a) Idle Bounce

Sinusoidal y-offset for calm, breathing motion.

```javascript
// --- Example: single Mogu with idle bounce ---
let time = 0;

function update(dt) {
  time += dt;
}

function draw(ctx, width, height) {
  const baseY = height / 2;

  // Period: 2.5s (calm), amplitude: 3px (subtle)
  const yOffset = idleBounce(time, 2.5, 3);

  drawMogu(ctx, width / 2, baseY + yOffset, 120, '#6C5CE7', 'neutral');
}
```

**Tuning guide:**
- **Period:** 2-3s for calm/meditative, 1-1.5s for energetic/excited
- **Amplitude:** 2px = very subtle, 3px = noticeable but gentle, 5px = bouncy/playful

**Multiple Mogu with phase offset:**

```javascript
const mogus = [
  { x: 200, phase: 0 },
  { x: 400, phase: 0.3 },
  { x: 600, phase: 0.7 }
];

function draw(ctx, width, height) {
  const baseY = height / 2;
  mogus.forEach(m => {
    const yOffset = idleBounce(time + m.phase, 2.5, 3);
    drawMogu(ctx, m.x, baseY + yOffset, 100, '#FF4D4D', 'neutral');
  });
}
```

---

### b) Squash & Stretch (Item Received)

Mogu compresses vertically then springs back when receiving an item.

```javascript
/**
 * Play a squash-and-stretch animation on a Mogu.
 * @param {object} mogu - Mogu object with { x, y, size, capColor, expression, squashT }
 * @param {number} dt   - delta time in seconds
 */
function animateSquash(mogu, dt) {
  if (mogu.squashT === undefined || mogu.squashT >= 1) {
    mogu.squashT = 1;
    return;
  }

  mogu.squashT += dt * 4; // 0.25s duration
  mogu.squashT = Math.min(mogu.squashT, 1);
}

function drawMoguWithSquash(ctx, mogu) {
  ctx.save();
  ctx.translate(mogu.x, mogu.y);

  // Spring easing: overshoot and settle
  const t = ease.spring(mogu.squashT, 0.5);

  // Interpolate scaleY from 0.85 (squashed) to 1.0 (normal)
  const scaleY = 0.85 + (1 - 0.85) * t;
  const scaleX = 1 / scaleY; // preserve volume

  ctx.scale(scaleX, scaleY);
  ctx.translate(-mogu.x, -mogu.y);

  drawMogu(ctx, mogu.x, mogu.y, mogu.size, mogu.capColor, mogu.expression);
  ctx.restore();
}

// --- Trigger squash on item received ---
function onItemReceived(mogu) {
  mogu.squashT = 0; // reset animation
}

// --- In game loop ---
function update(dt) {
  mogus.forEach(m => animateSquash(m, dt));
}

function draw(ctx, width, height) {
  mogus.forEach(m => drawMoguWithSquash(ctx, m));
}
```

---

### c) Cap Pulse (Processing State)

Spots globalAlpha oscillates during processing to indicate active thinking.

```javascript
/**
 * Draw Mogu with pulsing cap spots during processing state.
 */
function drawMoguWithPulse(ctx, mogu, time) {
  if (mogu.expression !== 'processing') {
    drawMogu(ctx, mogu.x, mogu.y, mogu.size, mogu.capColor, mogu.expression);
    return;
  }

  // Pulse period: 1 second, oscillate alpha between 0.5 and 0.9
  const pulse = Math.sin(time * Math.PI * 2); // -1 to 1
  const alpha = 0.7 + pulse * 0.2; // 0.5 to 0.9

  // Custom texture function for pulsing spots
  const pulseTexture = (ctx, cx, cy, capRx, capRy, spotColor) => {
    ctx.globalAlpha = alpha;
    ctx.fillStyle = spotColor;
    ctx.beginPath();
    ctx.arc(cx - 28, cy - 10, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(cx - 2, cy - 27, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(cx + 20, cy - 14, 7, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1.0;
  };

  drawMogu(ctx, mogu.x, mogu.y, mogu.size, mogu.capColor, mogu.expression, null, pulseTexture);
}

// --- In game loop ---
let time = 0;

function update(dt) {
  time += dt;
}

function draw(ctx, width, height) {
  mogus.forEach(m => drawMoguWithPulse(ctx, m, time));
}
```

---

### d) Eye Tracking (Item Follows)

Eyes shift toward the nearest moving item (max 2px displacement).

```javascript
/**
 * Calculate eye offset toward target position.
 * @param {number} moguX
 * @param {number} moguY
 * @param {number} targetX
 * @param {number} targetY
 * @returns {{ dx: number, dy: number }}
 */
function calculateEyeOffset(moguX, moguY, targetX, targetY) {
  const dx = targetX - moguX;
  const dy = targetY - moguY;
  const angle = Math.atan2(dy, dx);

  // Max displacement: 2px
  const maxDist = 2;
  const eyeDx = Math.cos(angle) * maxDist;
  const eyeDy = Math.sin(angle) * maxDist;

  return { dx: eyeDx, dy: eyeDy };
}

/**
 * Custom drawExpression with eye offset.
 */
function drawExpressionWithTracking(ctx, expression, s, eyeOffset) {
  const lw = 2.5 * s;
  const offsetX = eyeOffset.dx || 0;
  const offsetY = eyeOffset.dy || 0;

  ctx.fillStyle = '#0a0a0a';
  ctx.beginPath();
  ctx.arc((60 + offsetX) * s, (115 + offsetY) * s, 4.5 * s, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc((80 + offsetX) * s, (115 + offsetY) * s, 4.5 * s, 0, Math.PI * 2);
  ctx.fill();

  // Mouth (unchanged)
  ctx.strokeStyle = '#0a0a0a';
  ctx.lineWidth = lw;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(63 * s, 127 * s);
  ctx.quadraticCurveTo(70 * s, 133 * s, 77 * s, 127 * s);
  ctx.stroke();
}

/**
 * Draw Mogu with eye tracking toward target.
 */
function drawMoguWithEyeTracking(ctx, mogu, targetX, targetY) {
  const eyeOffset = calculateEyeOffset(mogu.x, mogu.y, targetX, targetY);

  // Copy drawMogu logic but replace drawExpression call
  const s = mogu.size / 170;
  const offsetX = mogu.x - 70 * s;
  const offsetY = mogu.y - 85 * s;

  ctx.save();
  ctx.translate(offsetX, offsetY);

  const highlightColor = lightenColor(mogu.capColor, 0.2);
  const spotColor = lightenColor(mogu.capColor, 0.25);

  // Feet
  ctx.fillStyle = '#EBE0D0';
  ctx.beginPath();
  ctx.ellipse(58 * s, 145 * s, 10 * s, 4 * s, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.ellipse(82 * s, 145 * s, 10 * s, 4 * s, 0, 0, Math.PI * 2);
  ctx.fill();

  // Stem
  ctx.fillStyle = '#F5EDE0';
  roundRect(ctx, 50 * s, 95 * s, 40 * s, 50 * s, 14 * s);
  ctx.fill();

  // Cap
  ctx.fillStyle = mogu.capColor;
  ctx.beginPath();
  ctx.ellipse(70 * s, 82 * s, 52 * s, 38 * s, 0, 0, Math.PI * 2);
  ctx.fill();

  // Highlight
  ctx.globalAlpha = 0.5;
  ctx.fillStyle = highlightColor;
  ctx.beginPath();
  ctx.ellipse(55 * s, 68 * s, 18 * s, 10 * s, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.globalAlpha = 1.0;

  // Spots
  ctx.globalAlpha = 0.7;
  ctx.fillStyle = spotColor;
  ctx.beginPath();
  ctx.arc(42 * s, 72 * s, 6 * s, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(68 * s, 55 * s, 5 * s, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(90 * s, 68 * s, 7 * s, 0, Math.PI * 2);
  ctx.fill();
  ctx.globalAlpha = 1.0;

  // Expression with eye tracking
  drawExpressionWithTracking(ctx, mogu.expression, s, eyeOffset);

  ctx.restore();
}

// --- In game loop ---
function draw(ctx, width, height) {
  const nearestItem = items.length > 0 ? items[0] : { x: mogu.x, y: mogu.y };
  drawMoguWithEyeTracking(ctx, mogu, nearestItem.x, nearestItem.y);
}
```

---

### e) Item Path Motion (Bezier Curve)

Parametric animation of an item traveling along a bezier curve between two positions.

```javascript
/**
 * Quadratic bezier interpolation.
 * @param {number} t      - progress [0, 1]
 * @param {object} p0     - start point { x, y }
 * @param {object} p1     - control point { x, y }
 * @param {object} p2     - end point { x, y }
 * @returns {{ x: number, y: number }}
 */
function bezier(t, p0, p1, p2) {
  const u = 1 - t;
  return {
    x: u * u * p0.x + 2 * u * t * p1.x + t * t * p2.x,
    y: u * u * p0.y + 2 * u * t * p1.y + t * t * p2.y
  };
}

/**
 * Animate an item along a bezier path with ease-in-out.
 * @param {object} item   - { x, y, startX, startY, endX, endY, t }
 * @param {number} dt     - delta time in seconds
 */
function animateItemPath(item, dt) {
  if (item.t >= 1) return;

  item.t += dt * 1.5; // 0.67s duration
  item.t = Math.min(item.t, 1);

  const easedT = ease.inOut(item.t);

  // Control point: arc upward
  const controlX = (item.startX + item.endX) / 2;
  const controlY = Math.min(item.startY, item.endY) - 60;

  const p0 = { x: item.startX, y: item.startY };
  const p1 = { x: controlX, y: controlY };
  const p2 = { x: item.endX, y: item.endY };

  const pos = bezier(easedT, p0, p1, p2);
  item.x = pos.x;
  item.y = pos.y;
}

/**
 * Start an item traveling from Mogu A to Mogu B.
 */
function sendItem(fromMogu, toMogu) {
  items.push({
    x: fromMogu.x,
    y: fromMogu.y,
    startX: fromMogu.x,
    startY: fromMogu.y,
    endX: toMogu.x,
    endY: toMogu.y,
    t: 0
  });
}

// --- In game loop ---
function update(dt) {
  items.forEach(item => animateItemPath(item, dt));
  items = items.filter(item => item.t < 1);
}

function draw(ctx, width, height) {
  items.forEach(item => {
    ctx.fillStyle = '#FFD700';
    ctx.beginPath();
    ctx.arc(item.x, item.y, 8, 0, Math.PI * 2);
    ctx.fill();
  });
}
```

---

### f) Error Flash (Cap Color Lerp)

Cap briefly flashes red when an error occurs (300ms flash).

```javascript
/**
 * Linear interpolate between two hex colors.
 * @param {string} colorA - hex color like '#FF4D4D'
 * @param {string} colorB - hex color like '#FF0000'
 * @param {number} t      - interpolation factor [0, 1]
 * @returns {string}      - hex color
 */
function lerpColor(colorA, colorB, t) {
  const hexToRgb = (hex) => {
    hex = hex.replace('#', '');
    if (hex.length === 3) {
      hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }
    return {
      r: parseInt(hex.substring(0, 2), 16),
      g: parseInt(hex.substring(2, 4), 16),
      b: parseInt(hex.substring(4, 6), 16)
    };
  };

  const rgbToHex = (r, g, b) => {
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  };

  const a = hexToRgb(colorA);
  const b = hexToRgb(colorB);

  const r = Math.round(a.r + (b.r - a.r) * t);
  const g = Math.round(a.g + (b.g - a.g) * t);
  const bVal = Math.round(a.b + (b.b - a.b) * t);

  return rgbToHex(r, g, bVal);
}

/**
 * Play error flash animation on Mogu.
 * @param {object} mogu - { baseCapColor, flashT }
 * @param {number} dt
 */
function animateErrorFlash(mogu, dt) {
  if (mogu.flashT === undefined || mogu.flashT >= 1) {
    mogu.capColor = mogu.baseCapColor;
    mogu.flashT = 1;
    return;
  }

  mogu.flashT += dt * (1 / 0.3); // 0.3s duration
  mogu.flashT = Math.min(mogu.flashT, 1);

  // Lerp to red and back: 0-0.5 -> red, 0.5-1 -> back to base
  const errorColor = '#FF0000';
  let t;
  if (mogu.flashT < 0.5) {
    t = mogu.flashT * 2; // 0-0.5 maps to 0-1
    mogu.capColor = lerpColor(mogu.baseCapColor, errorColor, t);
  } else {
    t = (mogu.flashT - 0.5) * 2; // 0.5-1 maps to 0-1
    mogu.capColor = lerpColor(errorColor, mogu.baseCapColor, t);
  }
}

/**
 * Trigger error flash.
 */
function onError(mogu) {
  mogu.flashT = 0;
}

// --- In game loop ---
function update(dt) {
  mogus.forEach(m => animateErrorFlash(m, dt));
}

function draw(ctx, width, height) {
  mogus.forEach(m => {
    drawMogu(ctx, m.x, m.y, m.size, m.capColor, m.expression);
  });
}
```

---

## 5. Absorption Ceremony Implementation

Complete multi-step animation for concept absorption. A Mogu sees keywords, gets curious, absorbs them, and transforms.

### Timeline

| Time (s) | What happens | Code section |
|----------|-------------|--------------|
| 0-0.8    | Idle, keywords fade in as floating text | CSS keyframe |
| 0.8-1.5  | Expression → curious, keywords drift toward cap | JS animation |
| 1.5-2.2  | Cap inflates (ry → ry×1.15), expression → processing | Ellipse ry interpolation |
| 2.2-3.0  | Cap color transitions, spots morph, expression → proud | Color lerp + spot shape |

### Complete Implementation

```javascript
/**
 * Play the full absorption ceremony animation.
 * @param {CanvasRenderingContext2D} ctx
 * @param {object} mogu     - { x, y, size, baseCapColor, expression, capRy, capColor, ceremonyT }
 * @param {string} targetColor - final cap color after absorption
 * @param {object} keywords    - { words: string[], positions: [{x,y,alpha}] }
 * @param {Function} onComplete - callback when ceremony finishes
 */
function playAbsorption(ctx, mogu, targetColor, keywords, onComplete) {
  const duration = 3.0; // total duration in seconds

  // Initialize if first call
  if (mogu.ceremonyT === undefined) {
    mogu.ceremonyT = 0;
    mogu.baseExpression = mogu.expression;
    mogu.targetColor = targetColor;
    mogu.baseCapRy = 38; // canonical ry from SVG
    mogu.inflatedCapRy = mogu.baseCapRy * 1.15;
    mogu.ceremonyActive = true;

    // Initialize keyword positions (spread around Mogu)
    keywords.positions = keywords.words.map((word, i) => ({
      x: mogu.x + (Math.random() - 0.5) * 200,
      y: mogu.y - 100 - Math.random() * 50,
      alpha: 0,
      word: word
    }));
  }

  mogu.ceremonyT += 1 / 60; // assume 60fps, increment by frame time

  const t = mogu.ceremonyT;

  // --- Phase 1: 0-0.8s — Keywords fade in ---
  if (t < 0.8) {
    const fadeT = t / 0.8;
    keywords.positions.forEach(kw => {
      kw.alpha = fadeT;
    });
    mogu.expression = 'neutral';
  }

  // --- Phase 2: 0.8-1.5s — Curious, keywords drift toward cap ---
  else if (t < 1.5) {
    mogu.expression = 'curious';
    const driftT = (t - 0.8) / (1.5 - 0.8);
    const easedT = ease.out(driftT);

    keywords.positions.forEach(kw => {
      const targetX = mogu.x + (Math.random() - 0.5) * 40;
      const targetY = mogu.y - 60;
      kw.x = kw.x + (targetX - kw.x) * easedT;
      kw.y = kw.y + (targetY - kw.y) * easedT;
      kw.alpha = 1 - easedT * 0.5; // start fading out
    });
  }

  // --- Phase 3: 1.5-2.2s — Cap inflates, processing ---
  else if (t < 2.2) {
    mogu.expression = 'processing';
    const inflateT = (t - 1.5) / (2.2 - 1.5);
    const easedT = ease.spring(inflateT, 0.5);

    const s = mogu.size / 170;
    mogu.capRy = (mogu.baseCapRy + (mogu.inflatedCapRy - mogu.baseCapRy) * easedT) * s;

    keywords.positions.forEach(kw => {
      kw.alpha = Math.max(0, 0.5 - inflateT * 0.5); // fade out
    });
  }

  // --- Phase 4: 2.2-3.0s — Color transition, proud ---
  else if (t < 3.0) {
    mogu.expression = 'proud';
    const colorT = (t - 2.2) / (3.0 - 2.2);
    const easedT = ease.out(colorT);

    mogu.capColor = lerpColor(mogu.baseCapColor, mogu.targetColor, easedT);

    const s = mogu.size / 170;
    mogu.capRy = (mogu.inflatedCapRy - (mogu.inflatedCapRy - mogu.baseCapRy) * easedT) * s;

    keywords.positions.forEach(kw => {
      kw.alpha = 0; // fully faded
    });
  }

  // --- Phase 5: Complete ---
  else {
    mogu.ceremonyActive = false;
    mogu.capColor = mogu.targetColor;
    mogu.baseCapColor = mogu.targetColor;
    mogu.expression = 'proud';
    mogu.capRy = mogu.baseCapRy * (mogu.size / 170);
    if (onComplete) onComplete();
  }
}

/**
 * Draw Mogu with ceremony animation (custom cap shape for inflation).
 */
function drawMoguWithCeremony(ctx, mogu) {
  if (!mogu.ceremonyActive) {
    drawMogu(ctx, mogu.x, mogu.y, mogu.size, mogu.capColor, mogu.expression);
    return;
  }

  // Custom cap shape with inflated ry
  const capShapeInflated = (ctx, cx, cy, capRx, capRy) => {
    ctx.beginPath();
    ctx.ellipse(cx, cy, capRx, mogu.capRy, 0, 0, Math.PI * 2);
  };

  drawMogu(ctx, mogu.x, mogu.y, mogu.size, mogu.capColor, mogu.expression, capShapeInflated);
}

/**
 * Draw floating keywords.
 */
function drawKeywords(ctx, keywords) {
  ctx.font = '14px system-ui, sans-serif';
  ctx.textAlign = 'center';

  keywords.positions.forEach(kw => {
    if (kw.alpha <= 0) return;
    ctx.globalAlpha = kw.alpha;
    ctx.fillStyle = '#ffffff';
    ctx.fillText(kw.word, kw.x, kw.y);
  });

  ctx.globalAlpha = 1.0;
}

// --- Usage Example ---
const mogu = {
  x: 400,
  y: 300,
  size: 140,
  baseCapColor: '#FF4D4D',
  capColor: '#FF4D4D',
  expression: 'neutral',
  ceremonyActive: false
};

const keywords = {
  words: ['REST', 'API', 'JSON', 'HTTP'],
  positions: []
};

function startAbsorption() {
  mogu.ceremonyT = 0;
  mogu.ceremonyActive = true;
}

function update(dt) {
  if (mogu.ceremonyActive) {
    playAbsorption(ctx, mogu, '#6C5CE7', keywords, () => {
      console.log('Absorption complete!');
    });
  }
}

function draw(ctx, width, height) {
  drawMoguWithCeremony(ctx, mogu);
  if (mogu.ceremonyActive) {
    drawKeywords(ctx, keywords);
  }
}
```

---

## 6. Color Lerp Helper

Complete implementation for smooth color transitions (used in error flash and absorption ceremony).

```javascript
/**
 * Linear interpolate between two hex colors.
 *
 * @param {string} colorA - hex color like '#FF4D4D' or '#F4D' (3-char shorthand supported)
 * @param {string} colorB - hex color like '#6C5CE7'
 * @param {number} t      - interpolation factor [0, 1]
 *                          t=0 returns colorA, t=1 returns colorB
 * @returns {string}      - interpolated hex color
 *
 * @example
 * lerpColor('#FF4D4D', '#6C5CE7', 0)    // '#FF4D4D'
 * lerpColor('#FF4D4D', '#6C5CE7', 0.5)  // '#B5A09A' (midpoint)
 * lerpColor('#FF4D4D', '#6C5CE7', 1)    // '#6C5CE7'
 */
function lerpColor(colorA, colorB, t) {
  // Parse hex to RGB
  const hexToRgb = (hex) => {
    hex = hex.replace('#', '');
    if (hex.length === 3) {
      hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }
    return {
      r: parseInt(hex.substring(0, 2), 16),
      g: parseInt(hex.substring(2, 4), 16),
      b: parseInt(hex.substring(4, 6), 16)
    };
  };

  // Convert RGB to hex
  const rgbToHex = (r, g, b) => {
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  };

  const a = hexToRgb(colorA);
  const b = hexToRgb(colorB);

  const r = Math.round(a.r + (b.r - a.r) * t);
  const g = Math.round(a.g + (b.g - a.g) * t);
  const bVal = Math.round(a.b + (b.b - a.b) * t);

  return rgbToHex(r, g, bVal);
}

// --- Example: Transition from red to purple over time ---
let transitionTime = 0;

function update(dt) {
  transitionTime += dt * 0.5; // 2-second transition
  transitionTime = Math.min(transitionTime, 1);
}

function draw(ctx, width, height) {
  const currentColor = lerpColor('#FF4D4D', '#6C5CE7', transitionTime);
  drawMogu(ctx, width / 2, height / 2, 140, currentColor, 'neutral');
}
```

**Use cases:**
- Error flash (pulse to red and back)
- Absorption ceremony (gradual color shift)
- Mood transitions (calm blue → alert orange)
- Multi-stage processing (green → yellow → red based on queue depth)

---

## 7. Label Layout Rules

Text overlap is the most common visual bug in generated scenes. Follow these rules:

### Labels below Mogus

Always position role labels (e.g., "Producer", "Broker") **below** the Mogu, offset by at least `moguSize * 0.35` from the Mogu's center y. Never use a hardcoded y-offset that ignores Mogu size.

```javascript
// Good: label position adapts to Mogu size
ctx.fillText('Broker', brokerX, brokerY + brokerSize * 0.35 + 12);

// Bad: hardcoded offset collides at large sizes
ctx.fillText('Broker', brokerX, brokerY + 80);
```

### No stacking without clearance

If there's a queue bar, counter, or status indicator between a Mogu and its label, the label goes below **all** intermediate elements:

```javascript
var labelY = queueBarY + queueBarH + 16; // below the queue bar, not below the Mogu
ctx.fillText('Broker', brokerX, labelY);
```

### Shorten labels when actors multiply

| Count | Label style |
|-------|-------------|
| 1-3 actors | Full name: "Consumer 1", "Consumer 2" |
| 4-5 actors | Short: "C1", "C2", "C3" |
| 6+ actors  | No labels — use cap color legend instead |

### Counts inside containers

Render queue/buffer counts **inside** their bar (using `textBaseline = 'middle'`), not as separate text below:

```javascript
ctx.textBaseline = 'middle';
ctx.fillText(count + '/' + max, barCenterX, barCenterY);
ctx.textBaseline = 'alphabetic'; // restore
```

### Overflow capping

Items that stack (queue pills, pending tasks) must have a **max visible count**. If there are 50 items in a queue, show 16 pills max and let the fill bar communicate the rest:

```javascript
var maxVisible = pillCols * 2; // e.g., 2 rows of 8
var visibleCount = Math.min(queue.length, maxVisible);
```

### Test at extremes

Before delivering, mentally simulate:
- Max actor count (e.g., 5 consumers) — do labels overlap?
- Max queue depth — do pills overflow into the Mogu?
- Minimum window size — does the control panel obscure the scene?

---

## Summary

This reference covers:
1. **Control selection** — when to use slider/toggle/stepper
2. **Panel layout** — fixed overlay CSS with backdrop blur
3. **Parameter binding** — state object pattern for game loop integration
4. **6 animation principles** — idle bounce, squash & stretch, cap pulse, eye tracking, bezier paths, error flash
5. **Absorption ceremony** — complete 4-phase timeline with code
6. **Color lerp helper** — smooth color transitions
7. **Label layout rules** — preventing text overlap in generated scenes

All code is copy-paste ready and compatible with `widgets.js` from the Mogu Visual components.
