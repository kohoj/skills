# Mogu Visual — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code skill that transforms technical descriptions into interactive animated HTML visualizations starring Mogu, a mushroom character whose cap shape/texture/color adapts to each concept.

**Architecture:** Prompt-heavy skill with reusable code components. SKILL.md is the AI's entry point with workflow + rules. references/ provides deep guidance (character spec, scene patterns, interaction patterns, complete examples). components/ provides copy-paste-ready code (canonical SVG, Canvas 2D drawing functions, game loop, UI controls).

**Tech Stack:** SVG (character reference), Canvas 2D + vanilla JS (generated output), no build step, CDN optional (GSAP, D3).

**Spec:** `docs/superpowers/specs/2026-04-16-mogu-visual-design.md`

---

### Task 1: Scaffold directory + canonical Mogu SVG

**Files:**
- Create: `mogu-visual/components/mogu.svg`
- Create: `mogu-visual/components/mogu-expressions.svg`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p mogu-visual/references mogu-visual/components
```

- [ ] **Step 2: Write canonical Mogu SVG**

Write `mogu-visual/components/mogu.svg` — the single source of truth for Mogu's shape and proportions. This is the exact SVG from the design spec, with inline comments documenting every measurement ratio:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 170">
  <!--
    Mogu — Canonical Reference
    ==========================
    Cap:Stem:Feet height ratio = 45:30:15 (remaining 10% overlap)
    Cap width / Stem width = 2.6x
    Eye spacing = Stem width × 50%
    Mouth below eyes = Stem height × 24%

    INVARIANTS (never change):
      Stem fill:      #F5EDE0
      Eyes fill:      #0a0a0a
      Eye radius:     stem_width × 11% (≈4.5 at this scale)
      Feet fill:      #EBE0D0
      Cap highlight:  cap_color lightened 20%, opacity 0.5
      Spot color:     cap_color lightened 25%, opacity 0.7

    VARIABLES (change per concept):
      Cap fill, Cap shape, Cap texture, Spot shapes, Expression
  -->

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

- [ ] **Step 3: Write expression variants SVG**

Write `mogu-visual/components/mogu-expressions.svg` — all 5 expressions rendered on the full Mogu body. Each expression is in its own `<g>` with an `id` for easy reference:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 200">
  <!--
    Mogu Expression System
    ======================
    5 expressions. Only eyes + mouth change. No new elements ever.
    Alert is the ONLY expression with eye-whites.

    Layout: 5 Mogus side by side, each in a 150×200 cell.
  -->

  <!-- 1. NEUTRAL — default idle -->
  <g id="neutral" transform="translate(5,15)">
    <rect x="50" y="95" width="40" height="50" rx="14" fill="#F5EDE0"/>
    <ellipse cx="70" cy="82" rx="52" ry="38" fill="#FF4D4D"/>
    <ellipse cx="55" cy="68" rx="18" ry="10" fill="#FF7070" opacity="0.5"/>
    <circle cx="42" cy="72" r="6" fill="#FF8080" opacity="0.7"/>
    <circle cx="68" cy="55" r="5" fill="#FF8080" opacity="0.7"/>
    <circle cx="90" cy="68" r="7" fill="#FF8080" opacity="0.7"/>
    <circle cx="60" cy="115" r="4.5" fill="#0a0a0a"/>
    <circle cx="80" cy="115" r="4.5" fill="#0a0a0a"/>
    <path d="M63,127 Q70,133 77,127" stroke="#0a0a0a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <ellipse cx="58" cy="145" rx="10" ry="4" fill="#EBE0D0"/>
    <ellipse cx="82" cy="145" rx="10" ry="4" fill="#EBE0D0"/>
    <text x="70" y="175" text-anchor="middle" font-family="system-ui" font-size="10" fill="#888">neutral</text>
  </g>

  <!-- 2. CURIOUS — concept arrives -->
  <g id="curious" transform="translate(155,15)">
    <rect x="50" y="95" width="40" height="50" rx="14" fill="#F5EDE0"/>
    <ellipse cx="70" cy="82" rx="52" ry="38" fill="#FF4D4D"/>
    <ellipse cx="55" cy="68" rx="18" ry="10" fill="#FF7070" opacity="0.5"/>
    <circle cx="42" cy="72" r="6" fill="#FF8080" opacity="0.7"/>
    <circle cx="68" cy="55" r="5" fill="#FF8080" opacity="0.7"/>
    <circle cx="90" cy="68" r="7" fill="#FF8080" opacity="0.7"/>
    <!-- One eye bigger -->
    <circle cx="60" cy="115" r="4.5" fill="#0a0a0a"/>
    <circle cx="80" cy="113" r="5.5" fill="#0a0a0a"/>
    <!-- O mouth -->
    <circle cx="70" cy="129" r="3.5" fill="#0a0a0a"/>
    <ellipse cx="58" cy="145" rx="10" ry="4" fill="#EBE0D0"/>
    <ellipse cx="82" cy="145" rx="10" ry="4" fill="#EBE0D0"/>
    <text x="70" y="175" text-anchor="middle" font-family="system-ui" font-size="10" fill="#888">curious</text>
  </g>

  <!-- 3. PROCESSING — digesting concept -->
  <g id="processing" transform="translate(305,15)">
    <rect x="50" y="95" width="40" height="50" rx="14" fill="#F5EDE0"/>
    <ellipse cx="70" cy="82" rx="52" ry="38" fill="#FF4D4D"/>
    <ellipse cx="55" cy="68" rx="18" ry="10" fill="#FF7070" opacity="0.5"/>
    <circle cx="42" cy="72" r="6" fill="#FF8080" opacity="0.7"/>
    <circle cx="68" cy="55" r="5" fill="#FF8080" opacity="0.7"/>
    <circle cx="90" cy="68" r="7" fill="#FF8080" opacity="0.7"/>
    <!-- Line eyes = shut -->
    <line x1="54" y1="115" x2="66" y2="115" stroke="#0a0a0a" stroke-width="3" stroke-linecap="round"/>
    <line x1="74" y1="115" x2="86" y2="115" stroke="#0a0a0a" stroke-width="3" stroke-linecap="round"/>
    <!-- Wavy mouth -->
    <path d="M60,128 Q65,124 70,128 Q75,132 80,128" stroke="#0a0a0a" stroke-width="2" fill="none" stroke-linecap="round"/>
    <ellipse cx="58" cy="145" rx="10" ry="4" fill="#EBE0D0"/>
    <ellipse cx="82" cy="145" rx="10" ry="4" fill="#EBE0D0"/>
    <text x="70" y="175" text-anchor="middle" font-family="system-ui" font-size="10" fill="#888">processing</text>
  </g>

  <!-- 4. PROUD — absorption complete -->
  <g id="proud" transform="translate(455,15)">
    <rect x="50" y="95" width="40" height="50" rx="14" fill="#F5EDE0"/>
    <ellipse cx="70" cy="82" rx="52" ry="38" fill="#FF4D4D"/>
    <ellipse cx="55" cy="68" rx="18" ry="10" fill="#FF7070" opacity="0.5"/>
    <circle cx="42" cy="72" r="6" fill="#FF8080" opacity="0.7"/>
    <circle cx="68" cy="55" r="5" fill="#FF8080" opacity="0.7"/>
    <circle cx="90" cy="68" r="7" fill="#FF8080" opacity="0.7"/>
    <!-- Arc eyes = happy squint -->
    <path d="M55,114 Q60,110 65,114" stroke="#0a0a0a" stroke-width="3" fill="none" stroke-linecap="round"/>
    <path d="M75,114 Q80,110 85,114" stroke="#0a0a0a" stroke-width="3" fill="none" stroke-linecap="round"/>
    <!-- Wide grin -->
    <path d="M60,126 Q70,136 80,126" stroke="#0a0a0a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <ellipse cx="58" cy="145" rx="10" ry="4" fill="#EBE0D0"/>
    <ellipse cx="82" cy="145" rx="10" ry="4" fill="#EBE0D0"/>
    <text x="70" y="175" text-anchor="middle" font-family="system-ui" font-size="10" fill="#888">proud</text>
  </g>

  <!-- 5. ALERT — error/exception -->
  <g id="alert" transform="translate(605,15)">
    <rect x="50" y="95" width="40" height="50" rx="14" fill="#F5EDE0"/>
    <ellipse cx="70" cy="82" rx="52" ry="38" fill="#FF4D4D"/>
    <ellipse cx="55" cy="68" rx="18" ry="10" fill="#FF7070" opacity="0.5"/>
    <circle cx="42" cy="72" r="6" fill="#FF8080" opacity="0.7"/>
    <circle cx="68" cy="55" r="5" fill="#FF8080" opacity="0.7"/>
    <circle cx="90" cy="68" r="7" fill="#FF8080" opacity="0.7"/>
    <!-- White eyes with pupils — ONLY expression with eye-whites -->
    <circle cx="60" cy="113" r="6" fill="white"/>
    <circle cx="80" cy="113" r="6" fill="white"/>
    <circle cx="61" cy="114" r="3.5" fill="#0a0a0a"/>
    <circle cx="81" cy="114" r="3.5" fill="#0a0a0a"/>
    <!-- Inverted V mouth -->
    <path d="M64,129 L70,124 L76,129" stroke="#0a0a0a" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    <ellipse cx="58" cy="145" rx="10" ry="4" fill="#EBE0D0"/>
    <ellipse cx="82" cy="145" rx="10" ry="4" fill="#EBE0D0"/>
    <text x="70" y="175" text-anchor="middle" font-family="system-ui" font-size="10" fill="#888">alert</text>
  </g>
</svg>
```

- [ ] **Step 4: Verify SVGs render correctly**

Open both files in a browser to verify they render as expected:

```bash
open mogu-visual/components/mogu.svg
open mogu-visual/components/mogu-expressions.svg
```

- [ ] **Step 5: Commit**

```bash
git add mogu-visual/components/
git commit -m "feat(mogu-visual): add canonical SVG and expression variants"
```

---

### Task 2: Write widgets.js — Canvas 2D drawing code

**Files:**
- Create: `mogu-visual/components/widgets.js`

This file contains standalone code snippets (not a module/class library) that AI copies into generated HTML. Each snippet is self-contained, clearly documented, and immediately usable.

- [ ] **Step 1: Write the drawMogu function**

Write `mogu-visual/components/widgets.js`:

```javascript
// ============================================================
// MOGU VISUAL — Reusable Code Snippets
// ============================================================
// These are copy-paste-ready snippets for generated HTML files.
// Each section is independent. Copy what you need.
// ============================================================


// ------------------------------------------------------------
// 1. DRAW MOGU — Canvas 2D rendering function
// ------------------------------------------------------------
// Draws a single Mogu character on a Canvas 2D context.
//
// Parameters:
//   ctx         - CanvasRenderingContext2D
//   x, y        - center position of the Mogu (center of stem)
//   size        - render height in pixels (proportions scale from this)
//   capColor    - hex string for cap fill, e.g. '#FF4D4D'
//   expression  - 'neutral' | 'curious' | 'processing' | 'proud' | 'alert'
//   capShape    - (optional) function(ctx, cx, cy, capW, capH) to draw custom cap path
//   texture     - (optional) function(ctx, cx, cy, capW, capH, spotColor) to draw cap texture
//
// Canonical proportions (from viewBox 0 0 140 170):
//   Total height = 170 units. Cap top ~44, cap center 82, stem top 95, stem bottom 145, feet 149.
//   We normalize everything to a 0-1 range and multiply by `size`.

function drawMogu(ctx, x, y, size, capColor, expression, capShape, texture) {
  const s = size / 170; // scale factor: 1 unit in viewBox = s pixels

  // --- Colors derived from cap ---
  const highlightColor = lightenColor(capColor, 0.20);
  const spotColor = lightenColor(capColor, 0.25);

  // --- Dimensions ---
  const stemW = 40 * s, stemH = 50 * s, stemRx = 14 * s;
  const stemX = x - stemW / 2, stemY = y - 75 * s + 95 * s; // y is center; stem top at 95/170
  const capCx = x, capCy = y - 75 * s + 82 * s;
  const capRx = 52 * s, capRy = 38 * s;
  const footY = y - 75 * s + 145 * s;

  ctx.save();

  // --- Stem ---
  roundRect(ctx, stemX, stemY, stemW, stemH, stemRx);
  ctx.fillStyle = '#F5EDE0';
  ctx.fill();

  // --- Cap ---
  if (capShape) {
    capShape(ctx, capCx, capCy, capRx, capRy);
    ctx.fillStyle = capColor;
    ctx.fill();
  } else {
    ctx.beginPath();
    ctx.ellipse(capCx, capCy, capRx, capRy, 0, 0, Math.PI * 2);
    ctx.fillStyle = capColor;
    ctx.fill();
  }

  // --- Cap highlight ---
  ctx.beginPath();
  ctx.ellipse(capCx - 15 * s, capCy - 14 * s, 18 * s, 10 * s, 0, 0, Math.PI * 2);
  ctx.fillStyle = highlightColor;
  ctx.globalAlpha = 0.5;
  ctx.fill();
  ctx.globalAlpha = 1;

  // --- Spots / Texture ---
  if (texture) {
    texture(ctx, capCx, capCy, capRx, capRy, spotColor);
  } else {
    // Default: 3 scattered circles
    const spots = [
      { dx: -28, dy: -10, r: 6 },
      { dx: -2,  dy: -27, r: 5 },
      { dx: 20,  dy: -14, r: 7 },
    ];
    ctx.globalAlpha = 0.7;
    ctx.fillStyle = spotColor;
    for (const sp of spots) {
      ctx.beginPath();
      ctx.arc(capCx + sp.dx * s, capCy + sp.dy * s, sp.r * s, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  // --- Face (expression) ---
  drawExpression(ctx, x, stemY, stemW, stemH, s, expression);

  // --- Feet ---
  ctx.fillStyle = '#EBE0D0';
  ctx.beginPath();
  ctx.ellipse(x - 12 * s, footY, 10 * s, 4 * s, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.ellipse(x + 12 * s, footY, 10 * s, 4 * s, 0, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();
}

function drawExpression(ctx, cx, stemY, stemW, stemH, s, expression) {
  const eyeY = stemY + stemH * 0.4;
  const mouthY = stemY + stemH * 0.64;
  const eyeSpacing = stemW * 0.25;
  const eyeR = stemW * 0.11;

  switch (expression) {
    case 'neutral':
      // Dot eyes
      ctx.fillStyle = '#0a0a0a';
      ctx.beginPath(); ctx.arc(cx - eyeSpacing, eyeY, eyeR, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(cx + eyeSpacing, eyeY, eyeR, 0, Math.PI * 2); ctx.fill();
      // Arc mouth
      ctx.beginPath();
      ctx.moveTo(cx - 7 * s, mouthY);
      ctx.quadraticCurveTo(cx, mouthY + 6 * s, cx + 7 * s, mouthY);
      ctx.strokeStyle = '#0a0a0a'; ctx.lineWidth = 2.5 * s; ctx.lineCap = 'round';
      ctx.stroke();
      break;

    case 'curious':
      ctx.fillStyle = '#0a0a0a';
      ctx.beginPath(); ctx.arc(cx - eyeSpacing, eyeY, eyeR, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(cx + eyeSpacing, eyeY - 2 * s, eyeR * 1.2, 0, Math.PI * 2); ctx.fill();
      // O mouth
      ctx.beginPath(); ctx.arc(cx, mouthY + 2 * s, 3.5 * s, 0, Math.PI * 2); ctx.fill();
      break;

    case 'processing':
      // Line eyes (shut)
      ctx.strokeStyle = '#0a0a0a'; ctx.lineWidth = 3 * s; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(cx - eyeSpacing - 6 * s, eyeY); ctx.lineTo(cx - eyeSpacing + 6 * s, eyeY); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(cx + eyeSpacing - 6 * s, eyeY); ctx.lineTo(cx + eyeSpacing + 6 * s, eyeY); ctx.stroke();
      // Wavy mouth
      ctx.lineWidth = 2 * s;
      ctx.beginPath();
      ctx.moveTo(cx - 10 * s, mouthY);
      ctx.quadraticCurveTo(cx - 5 * s, mouthY - 4 * s, cx, mouthY);
      ctx.quadraticCurveTo(cx + 5 * s, mouthY + 4 * s, cx + 10 * s, mouthY);
      ctx.stroke();
      break;

    case 'proud':
      // Arc eyes (happy squint)
      ctx.strokeStyle = '#0a0a0a'; ctx.lineWidth = 3 * s; ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(cx - eyeSpacing - 5 * s, eyeY);
      ctx.quadraticCurveTo(cx - eyeSpacing, eyeY - 4 * s, cx - eyeSpacing + 5 * s, eyeY);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(cx + eyeSpacing - 5 * s, eyeY);
      ctx.quadraticCurveTo(cx + eyeSpacing, eyeY - 4 * s, cx + eyeSpacing + 5 * s, eyeY);
      ctx.stroke();
      // Wide grin
      ctx.lineWidth = 2.5 * s;
      ctx.beginPath();
      ctx.moveTo(cx - 10 * s, mouthY - 1 * s);
      ctx.quadraticCurveTo(cx, mouthY + 10 * s, cx + 10 * s, mouthY - 1 * s);
      ctx.stroke();
      break;

    case 'alert':
      // White eyes with pupils
      ctx.fillStyle = 'white';
      ctx.beginPath(); ctx.arc(cx - eyeSpacing, eyeY - 2 * s, eyeR * 1.3, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(cx + eyeSpacing, eyeY - 2 * s, eyeR * 1.3, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#0a0a0a';
      ctx.beginPath(); ctx.arc(cx - eyeSpacing + 1 * s, eyeY - 1 * s, eyeR * 0.78, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(cx + eyeSpacing + 1 * s, eyeY - 1 * s, eyeR * 0.78, 0, Math.PI * 2); ctx.fill();
      // Inverted V mouth
      ctx.strokeStyle = '#0a0a0a'; ctx.lineWidth = 2.5 * s; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
      ctx.beginPath();
      ctx.moveTo(cx - 6 * s, mouthY + 2 * s);
      ctx.lineTo(cx, mouthY - 3 * s);
      ctx.lineTo(cx + 6 * s, mouthY + 2 * s);
      ctx.stroke();
      break;
  }
}

// --- Helpers ---

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

function lightenColor(hex, amount) {
  const num = parseInt(hex.replace('#', ''), 16);
  const r = Math.min(255, ((num >> 16) & 0xFF) + Math.round(255 * amount));
  const g = Math.min(255, ((num >> 8) & 0xFF) + Math.round(255 * amount));
  const b = Math.min(255, (num & 0xFF) + Math.round(255 * amount));
  return '#' + ((r << 16) | (g << 8) | b).toString(16).padStart(6, '0');
}


// ------------------------------------------------------------
// 2. GAME LOOP — requestAnimationFrame boilerplate
// ------------------------------------------------------------

function createGameLoop(canvas, updateFn, drawFn) {
  const ctx = canvas.getContext('2d');
  let lastTime = 0;
  let running = true;

  function resize() {
    canvas.width = canvas.clientWidth * devicePixelRatio;
    canvas.height = canvas.clientHeight * devicePixelRatio;
    ctx.scale(devicePixelRatio, devicePixelRatio);
  }

  function frame(time) {
    if (!running) return;
    const dt = Math.min((time - lastTime) / 1000, 0.05); // cap at 50ms
    lastTime = time;
    updateFn(dt);
    ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);
    drawFn(ctx, canvas.clientWidth, canvas.clientHeight);
    requestAnimationFrame(frame);
  }

  window.addEventListener('resize', resize);
  resize();
  requestAnimationFrame(frame);

  return { stop: () => { running = false; }, ctx, resize };
}


// ------------------------------------------------------------
// 3. UI CONTROLS — slider, toggle, stepper
// ------------------------------------------------------------

function createSlider(container, label, min, max, value, step, onChange) {
  const wrapper = document.createElement('div');
  wrapper.style.cssText = 'display:flex;align-items:center;gap:8px;margin:6px 0;';
  const lbl = document.createElement('span');
  lbl.style.cssText = 'font-size:12px;color:#aaa;min-width:100px;';
  lbl.textContent = label;
  const input = document.createElement('input');
  input.type = 'range'; input.min = min; input.max = max;
  input.value = value; input.step = step;
  input.style.cssText = 'flex:1;accent-color:#FF4D4D;';
  const val = document.createElement('span');
  val.style.cssText = 'font-size:12px;color:#eee;min-width:36px;text-align:right;font-family:monospace;';
  val.textContent = value;
  input.addEventListener('input', () => {
    val.textContent = input.value;
    onChange(parseFloat(input.value));
  });
  wrapper.append(lbl, input, val);
  container.appendChild(wrapper);
  return input;
}

function createToggle(container, label, value, onChange) {
  const wrapper = document.createElement('div');
  wrapper.style.cssText = 'display:flex;align-items:center;gap:8px;margin:6px 0;cursor:pointer;';
  const box = document.createElement('div');
  box.style.cssText = `width:36px;height:20px;border-radius:10px;background:${value ? '#FF4D4D' : '#333'};position:relative;transition:background 0.2s;`;
  const knob = document.createElement('div');
  knob.style.cssText = `width:16px;height:16px;border-radius:50%;background:white;position:absolute;top:2px;left:${value ? '18px' : '2px'};transition:left 0.2s;`;
  box.appendChild(knob);
  const lbl = document.createElement('span');
  lbl.style.cssText = 'font-size:12px;color:#aaa;';
  lbl.textContent = label;
  let state = value;
  wrapper.addEventListener('click', () => {
    state = !state;
    box.style.background = state ? '#FF4D4D' : '#333';
    knob.style.left = state ? '18px' : '2px';
    onChange(state);
  });
  wrapper.append(box, lbl);
  container.appendChild(wrapper);
  return { get: () => state };
}

function createStepper(container, label, min, max, value, onChange) {
  const wrapper = document.createElement('div');
  wrapper.style.cssText = 'display:flex;align-items:center;gap:6px;margin:6px 0;';
  const lbl = document.createElement('span');
  lbl.style.cssText = 'font-size:12px;color:#aaa;min-width:100px;';
  lbl.textContent = label;
  const btnMinus = document.createElement('button');
  btnMinus.textContent = '−'; btnMinus.style.cssText = 'width:24px;height:24px;border:1px solid #333;background:#1a1a1a;color:#eee;border-radius:4px;cursor:pointer;font-size:14px;';
  const val = document.createElement('span');
  val.style.cssText = 'font-size:13px;color:#eee;min-width:24px;text-align:center;font-family:monospace;';
  val.textContent = value;
  const btnPlus = document.createElement('button');
  btnPlus.textContent = '+'; btnPlus.style.cssText = btnMinus.style.cssText;
  let current = value;
  btnMinus.addEventListener('click', () => { if (current > min) { current--; val.textContent = current; onChange(current); } });
  btnPlus.addEventListener('click', () => { if (current < max) { current++; val.textContent = current; onChange(current); } });
  wrapper.append(lbl, btnMinus, val, btnPlus);
  container.appendChild(wrapper);
  return { get: () => current };
}


// ------------------------------------------------------------
// 4. EASING FUNCTIONS
// ------------------------------------------------------------

const ease = {
  inOut: t => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
  out:   t => t * (2 - t),
  in:    t => t * t,
  spring: (t, damping = 0.5) => {
    const s = 1 - damping;
    return 1 - Math.exp(-6 * t) * Math.cos(6.28 * s * t);
  },
};


// ------------------------------------------------------------
// 5. IDLE BOUNCE — subtle y-axis oscillation
// ------------------------------------------------------------

function idleBounce(time, period = 2.5, amplitude = 2) {
  return Math.sin(time * Math.PI * 2 / period) * amplitude;
}
```

- [ ] **Step 2: Create a test HTML to verify drawMogu works**

Create `mogu-visual/components/test-widgets.html` (development-only test page, not part of the skill):

```html
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Mogu Widget Test</title></head>
<body style="background:#0a0a0a; margin:0;">
<canvas id="c" style="width:100vw;height:100vh;display:block;"></canvas>
<script src="widgets.js"></script>
<script>
const canvas = document.getElementById('c');
const expressions = ['neutral','curious','processing','proud','alert'];
const colors = ['#FF4D4D','#3068B0','#2898A0','#6850A0','#E07850'];
let time = 0;

createGameLoop(canvas,
  (dt) => { time += dt; },
  (ctx, w, h) => {
    expressions.forEach((expr, i) => {
      const x = (i + 0.5) * (w / 5);
      const y = h / 2 + idleBounce(time + i * 0.5);
      drawMogu(ctx, x, y, 150, colors[i], expr);
    });
  }
);
</script>
</body></html>
```

- [ ] **Step 3: Open test page and verify all 5 expressions render correctly**

```bash
open mogu-visual/components/test-widgets.html
```

Verify: 5 Mogus in a row, each a different color and expression, all gently bouncing.

- [ ] **Step 4: Commit**

```bash
git add mogu-visual/components/widgets.js mogu-visual/components/test-widgets.html
git commit -m "feat(mogu-visual): add Canvas 2D drawing code and UI controls"
```

---

### Task 3: Write references/character.md

**Files:**
- Create: `mogu-visual/references/character.md`

This is the deep reference for the Mogu character system. AI reads it when it needs exact proportions, expression rules, cap shape/texture options, multi-Mogu rules, and the absorption ceremony sequence.

- [ ] **Step 1: Write character.md**

The content should include all sections from the design spec's Character Specification:
- Canonical SVG (point to `components/mogu.svg`)
- Proportions table (scale-independent ratios)
- Invariants and variables tables
- Expression system with rules (only eyes+mouth change, alert is the only one with eye-whites)
- Cap shape system (8 reference shapes with semantic mappings, plus the principle for inventing new ones)
- Cap texture system (8 reference textures with semantic mappings, plus the principle for inventing new ones)
- Cap color guidelines ("saturated but muted, as if the mushroom grew that way naturally")
- Multi-Mogu rules (size=importance, same color=same role, max 3 cap colors)
- Absorption ceremony (4-step sequence with exact visual changes per step)

Copy the relevant sections from the design spec at `docs/superpowers/specs/2026-04-16-mogu-visual-design.md`, but add Canvas 2D code examples for each cap shape and texture (showing how to draw them with `ctx.beginPath()` / `ctx.arc()` / etc).

- [ ] **Step 2: Commit**

```bash
git add mogu-visual/references/character.md
git commit -m "feat(mogu-visual): add character reference doc"
```

---

### Task 4: Write references/scenes.md

**Files:**
- Create: `mogu-visual/references/scenes.md`

This is the deep reference for scene archetypes. For each archetype, provide: visual layout description, which Mogu roles to use, how items move, which parameters to expose, and a Canvas 2D code sketch showing the scene layout.

- [ ] **Step 1: Write scenes.md**

Cover all 9 archetypes from the spec (Pipeline, Network, Pool/Queue, State Machine, Guard/Gate, Tree, Race, Transform, Broadcast). For each:

```markdown
## Pipeline

**Layout:** Mogus arranged left-to-right, connected by a horizontal path. Items spawn at left edge, move through each Mogu, exit at right.

**Actors:**
- Source Mogu (small, left edge) — emits items
- Processing Mogus (medium, center) — items pause here briefly
- Sink Mogu (small, right edge) — receives items

**Item motion:** Linear left→right along the path, with a brief pause + squash at each Mogu. Speed controlled by a rate slider.

**Parameters to expose:**
- Item rate (slider, 1-50/s)
- Processing time (slider, 50-500ms per stage)
- Number of stages (stepper, 1-5)

**Canvas layout sketch:**
[provide approximate x,y positions for a 800×500 canvas]
```

Also include a section on **combining archetypes** — e.g., a Pipeline where one stage fans out into a Broadcast.

- [ ] **Step 2: Commit**

```bash
git add mogu-visual/references/scenes.md
git commit -m "feat(mogu-visual): add scene archetypes reference"
```

---

### Task 5: Write references/interactions.md

**Files:**
- Create: `mogu-visual/references/interactions.md`

Reference for interactive controls and animation patterns. Covers: when to use each control type, how to bind controls to game loop parameters, animation principles with code, and the absorption ceremony implementation.

- [ ] **Step 1: Write interactions.md**

Sections:

1. **Control selection guide** — when to use slider vs toggle vs stepper
2. **Control panel layout** — CSS patterns for overlay panels (fixed position, semi-transparent background, never obscuring > 20% of canvas)
3. **Parameter binding pattern** — code showing how a slider value flows into the game loop update function
4. **Animation principles with code:**
   - Idle bounce (sinusoidal, code provided in widgets.js, explain period/amplitude tuning)
   - Squash & stretch (scale transform on receive, spring easing)
   - Cap pulse (globalAlpha oscillation on spots during processing)
   - Eye tracking (atan2 from eye center to nearest item, clamp displacement)
   - Item path motion (parametric t from 0-1 along bezier, ease-in-out)
   - Error flash (cap fillStyle lerp to red and back over 300ms)
5. **Absorption ceremony implementation** — step-by-step timeline with code:
   - 0-0.8s: idle → keywords fade in (CSS animation on floating text elements)
   - 0.8-1.5s: curious expression, keywords drift toward cap
   - 1.5-2.2s: cap ry animates to ry*1.15, processing expression
   - 2.2-3.0s: cap color transitions to target, spots morph, proud expression

- [ ] **Step 2: Commit**

```bash
git add mogu-visual/references/interactions.md
git commit -m "feat(mogu-visual): add interaction patterns reference"
```

---

### Task 6: Write references/examples.md

**Files:**
- Create: `mogu-visual/references/examples.md`

3 complete worked examples showing the full pipeline: concept → scene script → key code excerpts from the generated HTML.

- [ ] **Step 1: Write examples.md**

Three examples of increasing complexity:

**Example 1: Message Queue (Pipeline archetype)**
- Input: "Explain how a message queue works"
- Scene script (fully filled out)
- Key code: game loop with producer emitting items, broker queuing them, consumers pulling
- Parameters: message rate, consumer count, queue capacity
- Key moment: consumer dies → messages pile up in broker

**Example 2: Load Balancer (Broadcast + Guard archetype)**
- Input: "How does a load balancer distribute requests?"
- Scene script
- Key code: requests rain from top, LB Mogu distributes to server Mogus using round-robin or least-connections
- Parameters: algorithm toggle (round-robin / least-connections / random), request rate, server count
- Key moment: server overloaded → alert expression, LB reroutes

**Example 3: Encryption (Transform archetype)**
- Input: "Show how public key encryption works"
- Scene script with two phases (encrypt + decrypt)
- Key code: plaintext item enters Mogu, emerges as ciphertext (different color/shape), second Mogu decrypts
- Parameters: key size toggle (visual complexity of transform animation)
- Key moment: wrong key used → alert, garbled output

Each example should include ~50-80 lines of the most important generated code (drawScene function, update function), not the full HTML.

- [ ] **Step 2: Commit**

```bash
git add mogu-visual/references/examples.md
git commit -m "feat(mogu-visual): add complete worked examples"
```

---

### Task 7: Write SKILL.md

**Files:**
- Create: `mogu-visual/SKILL.md`

The main entry point. This is what the AI reads first every time. It must contain the complete workflow, core rules, and pointers to references.

- [ ] **Step 1: Write SKILL.md**

Structure (modeled after particle-effects/SKILL.md):

```markdown
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

Transform technical concepts into interactive animated HTML visualizations
starring Mogu — a mushroom character brand.

Before writing any code, read `references/character.md` — it contains the canonical
Mogu specification that governs every visual decision below.

## Workflow

### Step 1: Understand the Concept
[natural language → clarifying questions → scene script]

### Step 2: Choose Scene Archetype
[match to archetype from references/scenes.md, or compose/invent]

### Step 3: Design the Cast
[select Mogu roles, cap shapes, textures, colors]
[point to references/character.md for cap system]

### Step 4: Define Interactions
[select parameters, control types]
[point to references/interactions.md]

### Step 5: Generate HTML
[single file, Canvas 2D + DOM controls]
[copy drawing code from components/widgets.js]
[open with Absorption Ceremony]

### Step 6: Quality Gate
[checklist from spec]

## Quick Reference
- Character spec, proportions, expressions: `references/character.md`
- Scene archetypes with layout patterns: `references/scenes.md`
- Interaction controls, animation code: `references/interactions.md`
- Complete worked examples: `references/examples.md`
- Canonical SVG: `components/mogu.svg`
- Expression variants: `components/mogu-expressions.svg`
- Canvas 2D drawing code: `components/widgets.js`

## Scene Script Template
[the template from the spec]
```

Fill in each section with the full content — no "see spec" references. The SKILL.md must be self-contained enough to guide generation even if references fail to load, while pointing to references for depth.

- [ ] **Step 2: Commit**

```bash
git add mogu-visual/SKILL.md
git commit -m "feat(mogu-visual): add main skill guide"
```

---

### Task 8: Update README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add mogu-visual to README.md**

Add a new section after the ascii-rendering entry, following the same format:

```markdown
### mogu-visual

Transform technical descriptions into interactive animated HTML visualizations starring Mogu — a mushroom character whose cap shape, texture, and color adapt to each concept. Generates self-contained HTML files with Canvas 2D animations and interactive parameter controls.

**Features:** Mogu character brand with 5 expressions, 8+ cap shapes, 8+ cap textures, 9 scene archetypes, interactive parameter controls, absorption ceremony intro animation.

\`\`\`bash
npx skills add https://github.com/kohoj/skills --skill mogu-visual
\`\`\`
```

Also add to Prerequisites:

```markdown
- **mogu-visual**: No dependencies. Generated HTML files may optionally load GSAP or D3 from CDN.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add mogu-visual to README"
```

---

### Task 9: End-to-end test — invoke the skill

This is a manual verification step. No code to write.

- [ ] **Step 1: Invoke the skill with a test concept**

Use the skill to generate a visualization for "Explain how a message queue works with producers, a broker, and consumers."

Verify:
- AI reads SKILL.md and follows the workflow
- AI produces a scene script and asks for confirmation
- AI generates a single HTML file
- HTML opens in browser without errors
- Mogu characters render correctly (proportions match canonical SVG)
- At least 2 interactive parameters work (e.g., message rate, consumer count)
- Absorption ceremony plays on load
- Idle bounce animation is present
- Changing parameters visibly affects the scene behavior (not just cosmetics)

- [ ] **Step 2: Fix any issues found and commit**

```bash
git add -A
git commit -m "fix(mogu-visual): post-test adjustments"
```

---

Plan complete and saved to `docs/superpowers/plans/2026-04-16-mogu-visual.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
