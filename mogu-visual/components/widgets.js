// =============================================================================
// widgets.js — Mogu Visual: Canvas 2D drawing code
// =============================================================================
//
// Copy-paste-ready functions for generating Mogu character visualizations.
// NOT a module — just standalone snippets AI copies into generated HTML.
//
// Sections:
//   1. drawMogu        — draw a single Mogu character on a Canvas 2D context
//   2. createGameLoop  — requestAnimationFrame loop with high-DPI and resize
//   3. UI Controls     — createSlider, createToggle, createStepper
//   4. Easing          — ease.inOut, ease.out, ease.in, ease.spring
//   5. idleBounce      — sinusoidal y-offset for idle animation
//
// Canonical SVG reference: mogu.svg (viewBox 0 0 140 170)
// =============================================================================


// ---------------------------------------------------------------------------
// Section 1: drawMogu
// ---------------------------------------------------------------------------

/**
 * Draw a rounded rectangle (polyfill for older Canvas implementations).
 * @param {CanvasRenderingContext2D} ctx
 * @param {number} x       - left edge
 * @param {number} y       - top edge
 * @param {number} w       - width
 * @param {number} h       - height
 * @param {number} r       - corner radius
 */
function roundRect(ctx, x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.arcTo(x + w, y, x + w, y + r, r);
  ctx.lineTo(x + w, y + h - r);
  ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
  ctx.lineTo(x + r, y + h);
  ctx.arcTo(x, y + h, x, y + h - r, r);
  ctx.lineTo(x, y + r);
  ctx.arcTo(x, y, x + r, y, r);
  ctx.closePath();
}

/**
 * Lighten a hex color by a given amount (0-1).
 * @param {string} hex     - e.g. '#FF4D4D'
 * @param {number} amount  - 0 = no change, 1 = white
 * @returns {string}       - hex string like '#FF8080'
 */
function lightenColor(hex, amount) {
  hex = hex.replace('#', '');
  if (hex.length === 3) {
    hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
  }
  var r = parseInt(hex.substring(0, 2), 16);
  var g = parseInt(hex.substring(2, 4), 16);
  var b = parseInt(hex.substring(4, 6), 16);
  r = Math.round(r + (255 - r) * amount);
  g = Math.round(g + (255 - g) * amount);
  b = Math.round(b + (255 - b) * amount);
  return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

/**
 * Draw expression (eyes + mouth) for a Mogu character.
 *
 * All coordinates are in canonical SVG space (viewBox 0 0 140 170).
 * The caller applies transforms so this function draws at canonical coords.
 *
 * @param {CanvasRenderingContext2D} ctx
 * @param {string} expression  - 'neutral'|'curious'|'processing'|'proud'|'alert'
 * @param {number} s           - uniform scale factor (size / 170)
 */
function drawExpression(ctx, expression, s) {
  var lw = 2.5 * s; // line width, scaled

  switch (expression) {

    // --- Neutral: dot eyes + upward arc mouth ---
    case 'neutral':
    default:
      // Eyes: solid dots
      ctx.fillStyle = '#0a0a0a';
      ctx.beginPath();
      ctx.arc(60 * s, 115 * s, 4.5 * s, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(80 * s, 115 * s, 4.5 * s, 0, Math.PI * 2);
      ctx.fill();
      // Mouth: upward arc
      ctx.strokeStyle = '#0a0a0a';
      ctx.lineWidth = lw;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(63 * s, 127 * s);
      ctx.quadraticCurveTo(70 * s, 133 * s, 77 * s, 127 * s);
      ctx.stroke();
      break;

    // --- Curious: one eye bigger + circle "o" mouth ---
    case 'curious':
      ctx.fillStyle = '#0a0a0a';
      // Left eye: normal
      ctx.beginPath();
      ctx.arc(60 * s, 115 * s, 4.5 * s, 0, Math.PI * 2);
      ctx.fill();
      // Right eye: bigger, shifted up slightly
      ctx.beginPath();
      ctx.arc(80 * s, 113 * s, 5.5 * s, 0, Math.PI * 2);
      ctx.fill();
      // Mouth: small circle "o"
      ctx.strokeStyle = '#0a0a0a';
      ctx.lineWidth = lw;
      ctx.beginPath();
      ctx.arc(70 * s, 129 * s, 3.5 * s, 0, Math.PI * 2);
      ctx.stroke();
      break;

    // --- Processing: horizontal line eyes + wavy mouth ---
    case 'processing':
      ctx.strokeStyle = '#0a0a0a';
      ctx.lineWidth = 3 * s;
      ctx.lineCap = 'round';
      // Left eye: horizontal line
      ctx.beginPath();
      ctx.moveTo(54 * s, 115 * s);
      ctx.lineTo(66 * s, 115 * s);
      ctx.stroke();
      // Right eye: horizontal line
      ctx.beginPath();
      ctx.moveTo(74 * s, 115 * s);
      ctx.lineTo(86 * s, 115 * s);
      ctx.stroke();
      // Mouth: wavy line
      ctx.lineWidth = lw;
      ctx.beginPath();
      ctx.moveTo(60 * s, 128 * s);
      ctx.quadraticCurveTo(65 * s, 124 * s, 70 * s, 128 * s);
      ctx.quadraticCurveTo(75 * s, 132 * s, 80 * s, 128 * s);
      ctx.stroke();
      break;

    // --- Proud: upward arc eyes (happy squint) + wide grin ---
    case 'proud':
      ctx.strokeStyle = '#0a0a0a';
      ctx.lineWidth = 3 * s;
      ctx.lineCap = 'round';
      // Left eye: upward arc (happy squint)
      ctx.beginPath();
      ctx.moveTo(55 * s, 114 * s);
      ctx.quadraticCurveTo(60 * s, 110 * s, 65 * s, 114 * s);
      ctx.stroke();
      // Right eye: upward arc
      ctx.beginPath();
      ctx.moveTo(75 * s, 114 * s);
      ctx.quadraticCurveTo(80 * s, 110 * s, 85 * s, 114 * s);
      ctx.stroke();
      // Mouth: wide grin
      ctx.lineWidth = lw;
      ctx.beginPath();
      ctx.moveTo(60 * s, 126 * s);
      ctx.quadraticCurveTo(70 * s, 136 * s, 80 * s, 126 * s);
      ctx.stroke();
      break;

    // --- Alert: white circle eyes with dark pupils + inverted-V mouth ---
    case 'alert':
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
      ctx.lineWidth = lw;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(64 * s, 129 * s);
      ctx.lineTo(70 * s, 124 * s);
      ctx.lineTo(76 * s, 129 * s);
      ctx.stroke();
      break;
  }
}

/**
 * Draw a single Mogu character on a Canvas 2D context.
 *
 * All proportions are derived from the canonical SVG (viewBox 0 0 140 170).
 * The `size` parameter maps to the full viewBox height (170 units).
 *
 * @param {CanvasRenderingContext2D} ctx
 * @param {number} x           - center x position on canvas
 * @param {number} y           - center y position on canvas
 * @param {number} size        - render height in pixels (maps to viewBox height 170)
 * @param {string} capColor    - hex color for the cap, e.g. '#FF4D4D'
 * @param {string} [expression='neutral'] - 'neutral'|'curious'|'processing'|'proud'|'alert'
 * @param {Function} [capShape]   - optional: function(ctx, cx, cy, capRx, capRy) to draw custom cap path
 * @param {Function} [texture]    - optional: function(ctx, cx, cy, capRx, capRy, spotColor) for cap texture
 */
function drawMogu(ctx, x, y, size, capColor, expression, capShape, texture) {
  expression = expression || 'neutral';

  // Scale factor: canonical viewBox height is 170
  var s = size / 170;

  // Canonical center of the character in viewBox coords is (70, 85) roughly.
  // We translate so the caller's (x, y) is the center of the character.
  // ViewBox spans 0..140 horizontally (center=70) and 0..170 vertically (center=85).
  var offsetX = x - 70 * s;
  var offsetY = y - 85 * s;

  ctx.save();
  ctx.translate(offsetX, offsetY);

  // Derived colors
  var highlightColor = lightenColor(capColor, 0.2);
  var spotColor = lightenColor(capColor, 0.25);

  // --- Feet: drawn first (behind stem) ---
  ctx.fillStyle = '#EBE0D0';
  ctx.beginPath();
  ctx.ellipse(58 * s, 145 * s, 10 * s, 4 * s, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.ellipse(82 * s, 145 * s, 10 * s, 4 * s, 0, 0, Math.PI * 2);
  ctx.fill();

  // --- Stem: rounded rectangle ---
  ctx.fillStyle = '#F5EDE0';
  roundRect(ctx, 50 * s, 95 * s, 40 * s, 50 * s, 14 * s);
  ctx.fill();

  // --- Cap ---
  if (capShape) {
    // Custom cap shape via user-provided function
    capShape(ctx, 70 * s, 82 * s, 52 * s, 38 * s);
    ctx.fillStyle = capColor;
    ctx.fill();
  } else {
    // Default ellipse cap
    ctx.fillStyle = capColor;
    ctx.beginPath();
    ctx.ellipse(70 * s, 82 * s, 52 * s, 38 * s, 0, 0, Math.PI * 2);
    ctx.fill();
  }

  // --- Cap highlight ---
  ctx.globalAlpha = 0.5;
  ctx.fillStyle = highlightColor;
  ctx.beginPath();
  ctx.ellipse(55 * s, 68 * s, 18 * s, 10 * s, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.globalAlpha = 1.0;

  // --- Spots (or custom texture) ---
  if (texture) {
    texture(ctx, 70 * s, 82 * s, 52 * s, 38 * s, spotColor);
  } else {
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
  }

  // --- Expression (eyes + mouth) ---
  drawExpression(ctx, expression, s);

  ctx.restore();
}


// ---------------------------------------------------------------------------
// Section 2: Game loop
// ---------------------------------------------------------------------------

/**
 * Create a requestAnimationFrame game loop with high-DPI support and resize.
 *
 * @param {HTMLCanvasElement} canvas   - the canvas element
 * @param {Function} updateFn         - called each frame: updateFn(dt) where dt is seconds
 * @param {Function} drawFn           - called each frame: drawFn(ctx, width, height)
 * @returns {{ stop: Function, ctx: CanvasRenderingContext2D, resize: Function }}
 */
function createGameLoop(canvas, updateFn, drawFn) {
  var ctx = canvas.getContext('2d');
  var running = true;
  var lastTime = 0;
  var rafId = 0;

  /**
   * Resize the canvas to match its CSS dimensions at the current devicePixelRatio.
   */
  function resize() {
    var dpr = window.devicePixelRatio || 1;
    var rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function tick(timestamp) {
    if (!running) return;

    // dt in seconds, capped at 50ms to prevent spiral-of-death
    var dt = lastTime ? Math.min((timestamp - lastTime) / 1000, 0.05) : 0;
    lastTime = timestamp;

    var rect = canvas.getBoundingClientRect();
    var w = rect.width;
    var h = rect.height;

    updateFn(dt);

    ctx.clearRect(0, 0, w, h);
    drawFn(ctx, w, h);

    rafId = requestAnimationFrame(tick);
  }

  // Initial setup
  resize();
  window.addEventListener('resize', resize);
  rafId = requestAnimationFrame(tick);

  return {
    stop: function () {
      running = false;
      cancelAnimationFrame(rafId);
      window.removeEventListener('resize', resize);
    },
    ctx: ctx,
    resize: resize
  };
}


// ---------------------------------------------------------------------------
// Section 3: UI Controls
// ---------------------------------------------------------------------------
// Dark theme: backgrounds #1a1a1a, text #aaa/#eee, accent #FF4D4D

/**
 * Shared styles injected once for all UI controls.
 */
var _widgetStylesInjected = false;
function _injectWidgetStyles() {
  if (_widgetStylesInjected) return;
  _widgetStylesInjected = true;
  var style = document.createElement('style');
  style.textContent = [
    '.mogu-control { display:flex; align-items:center; gap:8px; margin:6px 0; font-family:system-ui,sans-serif; font-size:13px; color:#aaa; }',
    '.mogu-control label { min-width:70px; text-align:right; color:#aaa; }',
    '.mogu-control .mogu-value { min-width:36px; text-align:center; color:#eee; font-variant-numeric:tabular-nums; }',

    // Slider
    '.mogu-control input[type=range] { -webkit-appearance:none; appearance:none; height:4px; background:#333; border-radius:2px; outline:none; flex:1; }',
    '.mogu-control input[type=range]::-webkit-slider-thumb { -webkit-appearance:none; width:14px; height:14px; border-radius:50%; background:#FF4D4D; cursor:pointer; }',

    // Toggle
    '.mogu-toggle { position:relative; width:36px; height:20px; background:#333; border-radius:10px; cursor:pointer; transition:background 0.2s; flex-shrink:0; }',
    '.mogu-toggle.on { background:#FF4D4D; }',
    '.mogu-toggle .mogu-toggle-knob { position:absolute; top:2px; left:2px; width:16px; height:16px; background:#eee; border-radius:50%; transition:left 0.2s; }',
    '.mogu-toggle.on .mogu-toggle-knob { left:18px; }',

    // Stepper
    '.mogu-stepper { display:flex; align-items:center; gap:4px; }',
    '.mogu-stepper button { width:26px; height:26px; border:none; border-radius:4px; background:#333; color:#eee; font-size:16px; cursor:pointer; display:flex; align-items:center; justify-content:center; line-height:1; }',
    '.mogu-stepper button:hover { background:#FF4D4D; }',
    '.mogu-stepper button:active { background:#cc3d3d; }',
  ].join('\n');
  document.head.appendChild(style);
}

/**
 * Create a range slider with label and live value display.
 *
 * @param {HTMLElement} container - DOM element to append into
 * @param {string} label         - display label
 * @param {number} min
 * @param {number} max
 * @param {number} value         - initial value
 * @param {number} step
 * @param {Function} onChange    - called with new numeric value
 * @returns {HTMLInputElement}   - the range input element
 */
function createSlider(container, label, min, max, value, step, onChange) {
  _injectWidgetStyles();
  var row = document.createElement('div');
  row.className = 'mogu-control';

  var lbl = document.createElement('label');
  lbl.textContent = label;

  var input = document.createElement('input');
  input.type = 'range';
  input.min = min;
  input.max = max;
  input.value = value;
  input.step = step;

  var val = document.createElement('span');
  val.className = 'mogu-value';
  val.textContent = value;

  input.addEventListener('input', function () {
    var v = parseFloat(input.value);
    val.textContent = v;
    onChange(v);
  });

  row.appendChild(lbl);
  row.appendChild(input);
  row.appendChild(val);
  container.appendChild(row);
  return input;
}

/**
 * Create a toggle switch with label.
 *
 * @param {HTMLElement} container - DOM element to append into
 * @param {string} label         - display label
 * @param {boolean} value        - initial on/off state
 * @param {Function} onChange    - called with new boolean value
 * @returns {HTMLElement}        - the toggle element
 */
function createToggle(container, label, value, onChange) {
  _injectWidgetStyles();
  var row = document.createElement('div');
  row.className = 'mogu-control';

  var lbl = document.createElement('label');
  lbl.textContent = label;

  var toggle = document.createElement('div');
  toggle.className = 'mogu-toggle' + (value ? ' on' : '');

  var knob = document.createElement('div');
  knob.className = 'mogu-toggle-knob';
  toggle.appendChild(knob);

  var state = value;
  toggle.addEventListener('click', function () {
    state = !state;
    toggle.className = 'mogu-toggle' + (state ? ' on' : '');
    onChange(state);
  });

  row.appendChild(lbl);
  row.appendChild(toggle);
  container.appendChild(row);
  return toggle;
}

/**
 * Create a stepper (+/- buttons) with label and value display.
 *
 * @param {HTMLElement} container - DOM element to append into
 * @param {string} label         - display label
 * @param {number} min
 * @param {number} max
 * @param {number} value         - initial value
 * @param {Function} onChange    - called with new numeric value
 * @returns {{ setValue: Function }} - control handle
 */
function createStepper(container, label, min, max, value, onChange) {
  _injectWidgetStyles();
  var row = document.createElement('div');
  row.className = 'mogu-control';

  var lbl = document.createElement('label');
  lbl.textContent = label;

  var stepper = document.createElement('div');
  stepper.className = 'mogu-stepper';

  var btnMinus = document.createElement('button');
  btnMinus.textContent = '\u2212'; // minus sign
  var val = document.createElement('span');
  val.className = 'mogu-value';
  val.textContent = value;
  var btnPlus = document.createElement('button');
  btnPlus.textContent = '+';

  var current = value;

  function update(v) {
    current = Math.max(min, Math.min(max, v));
    val.textContent = current;
    onChange(current);
  }

  btnMinus.addEventListener('click', function () { update(current - 1); });
  btnPlus.addEventListener('click', function () { update(current + 1); });

  stepper.appendChild(btnMinus);
  stepper.appendChild(val);
  stepper.appendChild(btnPlus);

  row.appendChild(lbl);
  row.appendChild(stepper);
  container.appendChild(row);

  return {
    setValue: function (v) {
      current = Math.max(min, Math.min(max, v));
      val.textContent = current;
    }
  };
}


// ---------------------------------------------------------------------------
// Section 4: Easing functions
// ---------------------------------------------------------------------------

/**
 * Easing functions. All take t in [0, 1] and return eased t in [0, 1].
 * spring() also takes a damping parameter.
 */
var ease = {

  /** Smooth acceleration then deceleration (cubic). */
  inOut: function (t) {
    return t < 0.5
      ? 4 * t * t * t
      : 1 - Math.pow(-2 * t + 2, 3) / 2;
  },

  /** Deceleration only (cubic ease-out). */
  out: function (t) {
    return 1 - Math.pow(1 - t, 3);
  },

  /** Acceleration only (cubic ease-in). */
  in: function (t) {
    return t * t * t;
  },

  /**
   * Spring-like overshoot and settle.
   * @param {number} t       - progress [0, 1]
   * @param {number} [damping=0.5] - lower = more bounce (0-1 range typical)
   * @returns {number}
   */
  spring: function (t, damping) {
    damping = damping !== undefined ? damping : 0.5;
    return 1 - Math.exp(-6 * t) * Math.cos(t * Math.PI * 2 * (1 + damping * 3));
  }
};


// ---------------------------------------------------------------------------
// Section 5: idleBounce
// ---------------------------------------------------------------------------

/**
 * Sinusoidal y-offset for subtle idle animation.
 *
 * @param {number} time       - elapsed time in seconds
 * @param {number} [period=2.5]    - oscillation period in seconds
 * @param {number} [amplitude=2]   - max pixel offset
 * @returns {number}          - y offset in pixels (positive = down)
 */
function idleBounce(time, period, amplitude) {
  period = period !== undefined ? period : 2.5;
  amplitude = amplitude !== undefined ? amplitude : 2;
  return Math.sin((time / period) * Math.PI * 2) * amplitude;
}
