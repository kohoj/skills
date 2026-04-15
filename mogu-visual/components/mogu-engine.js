// =============================================================================
// mogu-engine.js — MoguScene: modular scene engine for Mogu Visual
// =============================================================================
//
// Replaces inlined boilerplate. AI writes ~150 lines of scene-specific code;
// the engine handles rendering, animation, controls, and absorption ceremony.
//
// Usage:
//   <script src="mogu-engine.js"></script>
//   <script>
//     var scene = new MoguScene(document.getElementById('canvas'), { ... });
//     scene.addActor('a', { label:'A', x:0.2, y:0.5, size:80, cap:{color:'#F00'} });
//     scene.start(['keyword1','keyword2'], '#3068B0');
//   </script>
//
// =============================================================================

(function (global) {
  'use strict';

  // --- Utilities ---

  function roundRect(ctx, x, y, w, h, r) {
    r = Math.min(r, w/2, h/2); ctx.beginPath(); ctx.moveTo(x+r, y);
    ctx.lineTo(x+w-r, y); ctx.arcTo(x+w, y, x+w, y+r, r);
    ctx.lineTo(x+w, y+h-r); ctx.arcTo(x+w, y+h, x+w-r, y+h, r);
    ctx.lineTo(x+r, y+h); ctx.arcTo(x, y+h, x, y+h-r, r);
    ctx.lineTo(x, y+r); ctx.arcTo(x, y, x+r, y, r); ctx.closePath();
  }

  function lightenColor(hex, amount) {
    hex = hex.replace('#','');
    if (hex.length === 3) hex = hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];
    var r = parseInt(hex.substring(0,2),16), g = parseInt(hex.substring(2,4),16), b = parseInt(hex.substring(4,6),16);
    r = Math.round(r+(255-r)*amount); g = Math.round(g+(255-g)*amount); b = Math.round(b+(255-b)*amount);
    return '#'+((1<<24)+(r<<16)+(g<<8)+b).toString(16).slice(1);
  }

  function lerpColor(cA, cB, t) {
    function p(h) { h=h.replace('#',''); if(h.length===3) h=h[0]+h[0]+h[1]+h[1]+h[2]+h[2]; return [parseInt(h.substring(0,2),16),parseInt(h.substring(2,4),16),parseInt(h.substring(4,6),16)]; }
    var a=p(cA), b=p(cB);
    return '#'+((1<<24)+(Math.round(a[0]+(b[0]-a[0])*t)<<16)+(Math.round(a[1]+(b[1]-a[1])*t)<<8)+Math.round(a[2]+(b[2]-a[2])*t)).toString(16).slice(1);
  }

  var ease = {
    inOut: function(t) { return t<0.5 ? 4*t*t*t : 1-Math.pow(-2*t+2,3)/2; },
    out: function(t) { return 1-Math.pow(1-t,3); },
    'in': function(t) { return t*t*t; },
    spring: function(t,d) { d=d!==undefined?d:0.5; return 1-Math.exp(-6*t)*Math.cos(t*Math.PI*2*(1+d*3)); }
  };

  function idleBounce(time, period, amplitude) {
    period = period !== undefined ? period : 2.5;
    amplitude = amplitude !== undefined ? amplitude : 2;
    return Math.sin((time/period)*Math.PI*2) * amplitude;
  }

  // --- Built-in cap shapes ---

  var capShapes = {
    dome: null, // default ellipse handled by drawMogu
    flat: function(ctx,cx,cy,rx,ry) { ctx.beginPath(); ctx.ellipse(cx,cy,rx*1.1,ry*0.55,0,0,Math.PI*2); },
    pointy: function(ctx,cx,cy,rx,ry) {
      ctx.beginPath(); ctx.moveTo(cx,cy-ry*1.6);
      ctx.quadraticCurveTo(cx+rx*0.6,cy-ry*0.4,cx+rx,cy); ctx.quadraticCurveTo(cx+rx*0.5,cy+ry*0.5,cx,cy+ry*0.3);
      ctx.quadraticCurveTo(cx-rx*0.5,cy+ry*0.5,cx-rx,cy); ctx.quadraticCurveTo(cx-rx*0.6,cy-ry*0.4,cx,cy-ry*1.6); ctx.closePath();
    },
    wavy: function(ctx,cx,cy,rx,ry) {
      ctx.beginPath(); for(var i=0;i<=12;i++){var a=(i/12)*Math.PI*2,w=1+Math.sin(a*4)*0.12; if(i===0)ctx.moveTo(cx+Math.cos(a)*rx*w,cy+Math.sin(a)*ry*w); else ctx.lineTo(cx+Math.cos(a)*rx*w,cy+Math.sin(a)*ry*w);} ctx.closePath();
    },
    bumpy: function(ctx,cx,cy,rx,ry) {
      ctx.beginPath(); var bR=rx*0.28;
      for(var i=0;i<6;i++){var a=(i/6)*Math.PI*2-Math.PI/2,bx=cx+Math.cos(a)*(rx-bR*0.3),by=cy+Math.sin(a)*(ry-bR*0.3); ctx.moveTo(bx+bR,by); ctx.arc(bx,by,bR,0,Math.PI*2);}
      ctx.ellipse(cx,cy,rx*0.6,ry*0.6,0,0,Math.PI*2);
    },
    droopy: function(ctx,cx,cy,rx,ry) {
      ctx.beginPath(); ctx.ellipse(cx,cy-ry*0.15,rx,ry*0.85,0,0,Math.PI*2);
      for(var i=0;i<5;i++){var dx=cx+((i-2)/2)*rx*0.7,dy=cy+ry*0.6+Math.abs(Math.sin(i*1.8))*ry*0.3; ctx.moveTo(dx+rx*0.1,dy); ctx.arc(dx,dy,rx*0.1,0,Math.PI*2);}
    },
    split: function(ctx,cx,cy,rx,ry) { ctx.beginPath(); ctx.ellipse(cx-rx*0.35,cy,rx*0.55,ry,0,0,Math.PI*2); ctx.ellipse(cx+rx*0.35,cy,rx*0.55,ry,0,0,Math.PI*2); },
    spiky: function(ctx,cx,cy,rx,ry) {
      ctx.beginPath(); for(var i=0;i<=16;i++){var a=(i/16)*Math.PI*2-Math.PI/2,r=i%2===0?1.2:0.85; if(i===0)ctx.moveTo(cx+Math.cos(a)*rx*r,cy+Math.sin(a)*ry*r); else ctx.lineTo(cx+Math.cos(a)*rx*r,cy+Math.sin(a)*ry*r);} ctx.closePath();
    }
  };

  // --- Built-in textures ---

  var capTextures = {
    spots: null, // default spots handled by drawMogu
    stripes: function(ctx,cx,cy,rx,ry,sc) {
      ctx.globalAlpha=0.5; ctx.strokeStyle=sc; ctx.lineWidth=2;
      for(var i=0;i<5;i++){var x=((i-2)/2)*rx*0.6; ctx.beginPath(); ctx.moveTo(cx+x,cy-ry*0.6); ctx.lineTo(cx+x,cy+ry*0.4); ctx.stroke();}
      ctx.globalAlpha=1;
    },
    hex: function(ctx,cx,cy,rx,ry,sc) {
      ctx.globalAlpha=0.4; ctx.strokeStyle=sc; ctx.lineWidth=1.2; var hR=rx*0.12;
      for(var r=0;r<3;r++) for(var c=0;c<4;c++){var hx=cx+(c-2+0.5+(r%2)*0.5)*hR*1.8,hy=cy+(r-1)*hR*1.5; ctx.beginPath(); for(var s=0;s<=6;s++){var a=(s/6)*Math.PI*2-Math.PI/6; if(s===0)ctx.moveTo(hx+Math.cos(a)*hR,hy+Math.sin(a)*hR); else ctx.lineTo(hx+Math.cos(a)*hR,hy+Math.sin(a)*hR);} ctx.closePath(); ctx.stroke();}
      ctx.globalAlpha=1;
    },
    circuit: function(ctx,cx,cy,rx,ry,sc) {
      ctx.globalAlpha=0.45; ctx.strokeStyle=sc; ctx.lineWidth=1.5;
      ctx.beginPath(); ctx.moveTo(cx-rx*0.5,cy); ctx.lineTo(cx-rx*0.1,cy); ctx.lineTo(cx-rx*0.1,cy-ry*0.4); ctx.lineTo(cx+rx*0.2,cy-ry*0.4); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(cx,cy+ry*0.2); ctx.lineTo(cx+rx*0.3,cy+ry*0.2); ctx.lineTo(cx+rx*0.3,cy-ry*0.1); ctx.stroke();
      ctx.fillStyle=sc; var j=[{x:cx-rx*0.1,y:cy},{x:cx+rx*0.2,y:cy-ry*0.4},{x:cx+rx*0.3,y:cy-ry*0.1}];
      for(var k=0;k<j.length;k++){ctx.beginPath(); ctx.arc(j[k].x,j[k].y,rx*0.03,0,Math.PI*2); ctx.fill();}
      ctx.globalAlpha=1;
    },
    swirl: function(ctx,cx,cy,rx,ry,sc) {
      ctx.globalAlpha=0.4; ctx.strokeStyle=sc; ctx.lineWidth=2; ctx.beginPath();
      for(var i=0;i<=50;i++){var t=i/50,a=t*Math.PI*3,rad=t*rx*0.5; if(i===0)ctx.moveTo(cx+Math.cos(a)*rad,cy+Math.sin(a)*rad*(ry/rx)); else ctx.lineTo(cx+Math.cos(a)*rad,cy+Math.sin(a)*rad*(ry/rx));}
      ctx.stroke(); ctx.globalAlpha=1;
    },
    constellation: function(ctx,cx,cy,rx,ry,sc) {
      var n=[{x:cx-rx*0.4,y:cy-ry*0.3},{x:cx+rx*0.1,y:cy-ry*0.5},{x:cx+rx*0.4,y:cy-ry*0.2},{x:cx-rx*0.2,y:cy+ry*0.1},{x:cx+rx*0.25,y:cy+ry*0.2}];
      ctx.globalAlpha=0.5; ctx.strokeStyle=sc; ctx.lineWidth=1;
      for(var i=0;i<n.length-1;i++){ctx.beginPath(); ctx.moveTo(n[i].x,n[i].y); ctx.lineTo(n[i+1].x,n[i+1].y); ctx.stroke();}
      ctx.beginPath(); ctx.moveTo(n[0].x,n[0].y); ctx.lineTo(n[3].x,n[3].y); ctx.stroke();
      ctx.globalAlpha=0.7; ctx.fillStyle=sc;
      for(var i=0;i<n.length;i++){ctx.beginPath(); ctx.arc(n[i].x,n[i].y,rx*0.04,0,Math.PI*2); ctx.fill();}
      ctx.globalAlpha=1;
    },
    scales: function(ctx,cx,cy,rx,ry,sc) {
      ctx.globalAlpha=0.4; ctx.strokeStyle=sc; ctx.lineWidth=1.5;
      for(var r=0;r<3;r++) for(var c=0;c<4;c++){var sx=cx+(c-2+0.5)*rx*0.28,sy=cy+(r-1)*ry*0.35; ctx.beginPath(); ctx.arc(sx,sy,rx*0.12,0,Math.PI,true); ctx.stroke();}
      ctx.globalAlpha=1;
    },
    lightning: function(ctx,cx,cy,rx,ry,sc) {
      ctx.globalAlpha=0.5; ctx.strokeStyle=sc; ctx.lineWidth=1.5; ctx.lineCap='round';
      for(var b=0;b<3;b++){var bx=cx+(b-1)*rx*0.35,by=cy-ry*0.5; ctx.beginPath(); ctx.moveTo(bx,by);
        for(var s=1;s<=4;s++) ctx.lineTo(bx+((s%2===0?-1:1)*rx*0.12),by+(ry*0.9/4)*s);
        ctx.stroke();}
      ctx.globalAlpha=1;
    }
  };

  // --- Expression drawing ---

  function drawExpression(ctx, expression, s) {
    var lw = 2.5*s;
    switch (expression) {
      case 'curious':
        ctx.fillStyle='#0a0a0a'; ctx.beginPath(); ctx.arc(60*s,115*s,4.5*s,0,Math.PI*2); ctx.fill();
        ctx.beginPath(); ctx.arc(80*s,113*s,5.5*s,0,Math.PI*2); ctx.fill();
        ctx.strokeStyle='#0a0a0a'; ctx.lineWidth=lw; ctx.beginPath(); ctx.arc(70*s,129*s,3.5*s,0,Math.PI*2); ctx.stroke(); break;
      case 'processing':
        ctx.strokeStyle='#0a0a0a'; ctx.lineWidth=3*s; ctx.lineCap='round';
        ctx.beginPath(); ctx.moveTo(54*s,115*s); ctx.lineTo(66*s,115*s); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(74*s,115*s); ctx.lineTo(86*s,115*s); ctx.stroke();
        ctx.lineWidth=lw; ctx.beginPath(); ctx.moveTo(60*s,128*s);
        ctx.quadraticCurveTo(65*s,124*s,70*s,128*s); ctx.quadraticCurveTo(75*s,132*s,80*s,128*s); ctx.stroke(); break;
      case 'proud':
        ctx.strokeStyle='#0a0a0a'; ctx.lineWidth=3*s; ctx.lineCap='round';
        ctx.beginPath(); ctx.moveTo(55*s,114*s); ctx.quadraticCurveTo(60*s,110*s,65*s,114*s); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(75*s,114*s); ctx.quadraticCurveTo(80*s,110*s,85*s,114*s); ctx.stroke();
        ctx.lineWidth=lw; ctx.beginPath(); ctx.moveTo(60*s,126*s); ctx.quadraticCurveTo(70*s,136*s,80*s,126*s); ctx.stroke(); break;
      case 'alert':
        ctx.fillStyle='#ffffff'; ctx.beginPath(); ctx.arc(60*s,113*s,6*s,0,Math.PI*2); ctx.fill();
        ctx.beginPath(); ctx.arc(80*s,113*s,6*s,0,Math.PI*2); ctx.fill();
        ctx.fillStyle='#0a0a0a'; ctx.beginPath(); ctx.arc(61*s,114*s,3.5*s,0,Math.PI*2); ctx.fill();
        ctx.beginPath(); ctx.arc(81*s,114*s,3.5*s,0,Math.PI*2); ctx.fill();
        ctx.strokeStyle='#0a0a0a'; ctx.lineWidth=lw; ctx.lineCap='round';
        ctx.beginPath(); ctx.moveTo(64*s,129*s); ctx.lineTo(70*s,124*s); ctx.lineTo(76*s,129*s); ctx.stroke(); break;
      case 'neutral': default:
        ctx.fillStyle='#0a0a0a'; ctx.beginPath(); ctx.arc(60*s,115*s,4.5*s,0,Math.PI*2); ctx.fill();
        ctx.beginPath(); ctx.arc(80*s,115*s,4.5*s,0,Math.PI*2); ctx.fill();
        ctx.strokeStyle='#0a0a0a'; ctx.lineWidth=lw; ctx.lineCap='round';
        ctx.beginPath(); ctx.moveTo(63*s,127*s); ctx.quadraticCurveTo(70*s,133*s,77*s,127*s); ctx.stroke(); break;
    }
  }

  // --- Core Mogu renderer ---

  function resolveCapShape(cap) {
    if (!cap || !cap.shape) return null;
    return typeof cap.shape === 'function' ? cap.shape : (capShapes[cap.shape] || null);
  }
  function resolveTexture(cap) {
    if (!cap || !cap.texture) return null;
    return typeof cap.texture === 'function' ? cap.texture : (capTextures[cap.texture] || null);
  }

  function drawMogu(ctx, x, y, size, capColor, expression, capShapeFn, textureFn) {
    expression = expression || 'neutral';
    var s = size/170, ox = x-70*s, oy = y-85*s;
    ctx.save(); ctx.translate(ox, oy);
    var hl = lightenColor(capColor, 0.2), sp = lightenColor(capColor, 0.25);
    // Feet
    ctx.fillStyle='#EBE0D0';
    ctx.beginPath(); ctx.ellipse(58*s,145*s,10*s,4*s,0,0,Math.PI*2); ctx.fill();
    ctx.beginPath(); ctx.ellipse(82*s,145*s,10*s,4*s,0,0,Math.PI*2); ctx.fill();
    // Stem
    ctx.fillStyle='#F5EDE0'; roundRect(ctx,50*s,95*s,40*s,50*s,14*s); ctx.fill();
    // Cap
    if (capShapeFn) { capShapeFn(ctx,70*s,82*s,52*s,38*s); ctx.fillStyle=capColor; ctx.fill(); }
    else { ctx.fillStyle=capColor; ctx.beginPath(); ctx.ellipse(70*s,82*s,52*s,38*s,0,0,Math.PI*2); ctx.fill(); }
    // Highlight
    ctx.globalAlpha=0.5; ctx.fillStyle=hl; ctx.beginPath(); ctx.ellipse(55*s,68*s,18*s,10*s,0,0,Math.PI*2); ctx.fill(); ctx.globalAlpha=1;
    // Texture
    if (textureFn) { textureFn(ctx,70*s,82*s,52*s,38*s,sp); }
    else { ctx.globalAlpha=0.7; ctx.fillStyle=sp; ctx.beginPath(); ctx.arc(42*s,72*s,6*s,0,Math.PI*2); ctx.fill(); ctx.beginPath(); ctx.arc(68*s,55*s,5*s,0,Math.PI*2); ctx.fill(); ctx.beginPath(); ctx.arc(90*s,68*s,7*s,0,Math.PI*2); ctx.fill(); ctx.globalAlpha=1; }
    drawExpression(ctx, expression, s);
    ctx.restore();
  }

  // --- MoguScene constructor ---

  function MoguScene(canvas, options) {
    options = options || {};
    this._canvas = canvas;
    this._ctx = canvas.getContext('2d');
    this._bg = options.background || '#0a0a0a';
    this._title = options.title || '';
    this._actors = {};       // id -> actor
    this._actorOrder = [];   // draw order
    this._connections = [];
    this._items = [];        // animated items in flight
    this._params = {};       // id -> { value }
    this._stats = {};        // key -> value
    this._updateFn = null;
    this._drawFn = null;
    this._time = 0;
    this._running = false;
    this._lastTime = 0;
    this._rafId = 0;
    this._ceremony = null;
    this._buildDOM();
    this._resize();
    var self = this;
    this._resizeHandler = function () { self._resize(); };
    window.addEventListener('resize', this._resizeHandler);
  }

  // --- DOM: control panel, stats overlay ---

  MoguScene.prototype._buildDOM = function () {
    if (!MoguScene._stylesInjected) {
      MoguScene._stylesInjected = true;
      var s = document.createElement('style');
      s.textContent = '.mogu-control{display:flex;align-items:center;gap:8px;margin:6px 0;font-family:system-ui,sans-serif;font-size:13px;color:#aaa}'
        +'.mogu-control label{min-width:70px;text-align:right;color:#aaa}.mogu-control .mogu-value{min-width:36px;text-align:center;color:#eee;font-variant-numeric:tabular-nums}'
        +'.mogu-control input[type=range]{-webkit-appearance:none;appearance:none;height:4px;background:#333;border-radius:2px;outline:none;flex:1}'
        +'.mogu-control input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:14px;height:14px;border-radius:50%;background:#FF4D4D;cursor:pointer}'
        +'.mogu-toggle{position:relative;width:36px;height:20px;background:#333;border-radius:10px;cursor:pointer;transition:background 0.2s;flex-shrink:0}'
        +'.mogu-toggle.on{background:#FF4D4D}.mogu-toggle .mogu-toggle-knob{position:absolute;top:2px;left:2px;width:16px;height:16px;background:#eee;border-radius:50%;transition:left 0.2s}'
        +'.mogu-toggle.on .mogu-toggle-knob{left:18px}'
        +'.mogu-stepper{display:flex;align-items:center;gap:4px}.mogu-stepper button{width:26px;height:26px;border:none;border-radius:4px;background:#333;color:#eee;font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;line-height:1}'
        +'.mogu-stepper button:hover{background:#FF4D4D}.mogu-stepper button:active{background:#cc3d3d}';
      document.head.appendChild(s);
    }
    // Control panel
    this._controlPanel = document.createElement('div');
    this._controlPanel.id = 'mogu-controls';
    this._controlPanel.style.cssText = 'position:fixed;top:16px;right:16px;background:rgba(26,26,26,0.92);border:1px solid #333;border-radius:10px;padding:14px 18px;z-index:10;min-width:230px;backdrop-filter:blur(8px);font-family:system-ui,sans-serif;display:none;';
    var h3 = document.createElement('h3');
    h3.style.cssText = 'color:#eee;font-size:14px;margin:0 0 10px;font-weight:600;';
    h3.textContent = 'Parameters';
    this._controlPanel.appendChild(h3);
    this._paramContainer = document.createElement('div');
    this._controlPanel.appendChild(this._paramContainer);
    document.body.appendChild(this._controlPanel);
    // Stats
    this._statsEl = document.createElement('div');
    this._statsEl.style.cssText = 'position:fixed;bottom:16px;left:16px;color:#555;font-size:12px;font-family:"SF Mono",Monaco,monospace;z-index:10;';
    document.body.appendChild(this._statsEl);
  };

  MoguScene.prototype._resize = function () {
    var dpr = window.devicePixelRatio || 1, rect = this._canvas.getBoundingClientRect();
    this._canvas.width = rect.width * dpr;
    this._canvas.height = rect.height * dpr;
    this._ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };

  // --- Actor management ---

  MoguScene.prototype.addActor = function (id, cfg) {
    var actor = {
      id: id, label: cfg.label || id,
      x: cfg.x !== undefined ? cfg.x : 0.5,
      y: cfg.y !== undefined ? cfg.y : 0.5,
      size: cfg.size || 80,
      cap: cfg.cap || {},
      expression: cfg.expression || 'neutral',
      bouncePeriod: cfg.bouncePeriod !== undefined ? cfg.bouncePeriod : 2.5,
      bounceAmplitude: cfg.bounceAmplitude !== undefined ? cfg.bounceAmplitude : 2,
      bouncePhase: cfg.bouncePhase !== undefined ? cfg.bouncePhase : 0,
      _capShapeFn: resolveCapShape(cfg.cap),
      _textureFn: resolveTexture(cfg.cap)
    };
    this._actors[id] = actor;
    this._actorOrder.push(id);
    return actor;
  };

  MoguScene.prototype.removeActor = function (id) {
    delete this._actors[id];
    var idx = this._actorOrder.indexOf(id);
    if (idx !== -1) this._actorOrder.splice(idx, 1);
  };

  MoguScene.prototype.getActor = function (id) { return this._actors[id] || null; };

  MoguScene.prototype.setExpression = function (id, expr) {
    if (this._actors[id]) this._actors[id].expression = expr;
  };

  MoguScene.prototype.setCapColor = function (id, color) {
    if (this._actors[id]) this._actors[id].cap.color = color;
  };

  MoguScene.prototype.getActorPos = function (id) {
    var a = this._actors[id]; if (!a) return {x:0,y:0};
    var r = this._canvas.getBoundingClientRect();
    return { x: a.x * r.width, y: a.y * r.height };
  };

  // --- Connections ---

  MoguScene.prototype.connect = function (fromId, toId, opts) {
    opts = opts || {};
    this._connections.push({ from:fromId, to:toId, style:opts.style||'dashed', color:opts.color||'#222', arrow:opts.arrow!==undefined?opts.arrow:true });
  };

  MoguScene.prototype.disconnect = function (fromId, toId) {
    for (var i = this._connections.length-1; i >= 0; i--)
      if (this._connections[i].from===fromId && this._connections[i].to===toId) this._connections.splice(i,1);
  };

  // --- Parameters (controls UI) ---

  MoguScene.prototype.addParam = function (cfg) {
    var self = this;
    this._params[cfg.id] = { value: cfg.value };
    this._controlPanel.style.display = '';

    var row = document.createElement('div'); row.className = 'mogu-control';
    var lbl = document.createElement('label'); lbl.textContent = cfg.label;

    if (cfg.type === 'slider') {
      var input = document.createElement('input');
      input.type='range'; input.min=cfg.min; input.max=cfg.max; input.value=cfg.value; input.step=cfg.step||1;
      var val = document.createElement('span'); val.className='mogu-value'; val.textContent=cfg.value;
      input.addEventListener('input', function(){ var v=parseFloat(input.value); val.textContent=v; self._params[cfg.id].value=v; });
      row.appendChild(lbl); row.appendChild(input); row.appendChild(val);
    } else if (cfg.type === 'stepper') {
      var stepper = document.createElement('div'); stepper.className='mogu-stepper';
      var btnM = document.createElement('button'); btnM.textContent='\u2212';
      var val = document.createElement('span'); val.className='mogu-value'; val.textContent=cfg.value;
      var btnP = document.createElement('button'); btnP.textContent='+';
      var cur = cfg.value;
      function upd(v){ cur=Math.max(cfg.min,Math.min(cfg.max,v)); val.textContent=cur; self._params[cfg.id].value=cur; }
      btnM.addEventListener('click', function(){ upd(cur-1); });
      btnP.addEventListener('click', function(){ upd(cur+1); });
      stepper.appendChild(btnM); stepper.appendChild(val); stepper.appendChild(btnP);
      row.appendChild(lbl); row.appendChild(stepper);
    } else if (cfg.type === 'toggle') {
      var toggle = document.createElement('div'); toggle.className='mogu-toggle'+(cfg.value?' on':'');
      var knob = document.createElement('div'); knob.className='mogu-toggle-knob'; toggle.appendChild(knob);
      var tState = !!cfg.value;
      toggle.addEventListener('click', function(){ tState=!tState; toggle.className='mogu-toggle'+(tState?' on':''); self._params[cfg.id].value=tState; });
      row.appendChild(lbl); row.appendChild(toggle);
    }
    this._paramContainer.appendChild(row);
  };

  MoguScene.prototype.param = function (id) {
    return this._params[id] ? this._params[id].value : undefined;
  };

  // --- Item spawning ---

  MoguScene.prototype.spawnItem = function (cfg) {
    var item = {
      from:cfg.from, to:cfg.to, color:cfg.color||'#FF6B9D', shape:cfg.shape||'circle',
      size:cfg.size!==undefined?cfg.size:5, speed:cfg.speed!==undefined?cfg.speed:1.5,
      arc:cfg.arc!==undefined?cfg.arc:20, glow:cfg.glow!==undefined?cfg.glow:true,
      onArrive:cfg.onArrive||null, progress:0, _active:true
    };
    this._items.push(item);
    return item;
  };

  MoguScene.prototype.removeItem = function (item) { item._active = false; };
  MoguScene.prototype.getItems = function () { return this._items.filter(function(i){return i._active;}); };

  // --- Callbacks and stats ---

  MoguScene.prototype.onUpdate = function (fn) { this._updateFn = fn; };
  MoguScene.prototype.onDraw = function (fn) { this._drawFn = fn; };
  MoguScene.prototype.setStat = function (key, value) { this._stats[key] = value; };

  // --- Zones (boundary/domain regions) ---

  MoguScene.prototype.addZone = function (id, cfg) {
    this._zones = this._zones || [];
    this._zones.push({
      id: id,
      x: cfg.x || 0, y: cfg.y || 0,        // top-left, normalized 0-1
      w: cfg.w || 0.3, h: cfg.h || 0.3,     // width/height, normalized 0-1
      color: cfg.color || 'rgba(255,255,255,0.06)',
      borderColor: cfg.borderColor || 'rgba(255,255,255,0.15)',
      label: cfg.label || '',
      labelColor: cfg.labelColor || '#666'
    });
  };

  MoguScene.prototype.removeZone = function (id) {
    this._zones = (this._zones||[]).filter(function(z){ return z.id !== id; });
  };

  // --- Gauges (metric/resource bars) ---

  MoguScene.prototype.addGauge = function (id, cfg) {
    this._gauges = this._gauges || [];
    this._gauges.push({
      id: id,
      actorId: cfg.actorId,                  // attached to which actor
      label: cfg.label || '',
      value: cfg.value || 0,                 // 0-1
      max: cfg.max || 1,
      threshold: cfg.threshold,              // optional: 0-1, draws a threshold marker
      color: cfg.color || '#52C77A',
      warnColor: cfg.warnColor || '#FFB84D',
      dangerColor: cfg.dangerColor || '#FF4D4D',
      width: cfg.width || 60,
      height: cfg.height || 8,
      offsetY: cfg.offsetY || 0              // extra y offset below actor
    });
  };

  MoguScene.prototype.setGauge = function (id, value) {
    var gauges = this._gauges || [];
    for (var i = 0; i < gauges.length; i++) {
      if (gauges[i].id === id) { gauges[i].value = value; return; }
    }
  };

  MoguScene.prototype.removeGauge = function (id) {
    this._gauges = (this._gauges||[]).filter(function(g){ return g.id !== id; });
  };

  // --- Ghost actors (derived/projection copies) ---

  MoguScene.prototype.addGhost = function (sourceActorId, ghostId, cfg) {
    var src = this._actors[sourceActorId];
    if (!src) return;
    this.addActor(ghostId, {
      label: cfg.label || src.label + ' (derived)',
      x: cfg.x !== undefined ? cfg.x : src.x + 0.05,
      y: cfg.y !== undefined ? cfg.y : src.y + 0.05,
      size: cfg.size || Math.round(src.size * 0.75),
      cap: { color: cfg.capColor || src.cap.color, shape: src.cap.shape, texture: src.cap.texture },
      bouncePhase: (cfg.bouncePhase !== undefined ? cfg.bouncePhase : src.bouncePhase + 0.5)
    });
    this._ghosts = this._ghosts || {};
    this._ghosts[ghostId] = { sourceId: sourceActorId, opacity: cfg.opacity || 0.5, staleOffset: cfg.staleOffset || 0 };
  };

  // --- Annotations (text callouts on canvas) ---

  MoguScene.prototype.addAnnotation = function (id, cfg) {
    this._annotations = this._annotations || [];
    this._annotations.push({
      id: id,
      x: cfg.x || 0.5, y: cfg.y || 0.5,    // normalized
      text: cfg.text || '',
      color: cfg.color || '#888',
      fontSize: cfg.fontSize || 11,
      bg: cfg.bg || null                      // optional background color
    });
  };

  MoguScene.prototype.removeAnnotation = function (id) {
    this._annotations = (this._annotations||[]).filter(function(a){ return a.id !== id; });
  };

  // --- Start / Stop ---

  MoguScene.prototype.start = function (keywords, targetColor) {
    if (keywords && keywords.length > 0) {
      this._ceremony = {
        keywords: keywords, targetColor: targetColor || '#3068B0',
        kwState: keywords.map(function(kw,i){ return {text:kw, alpha:0, offsetX:120, scale:1, delay:i*0.1}; })
      };
    }
    this._running = true; this._lastTime = 0; this._time = 0;
    var self = this;
    function tick(ts) {
      if (!self._running) return;
      var dt = self._lastTime ? Math.min((ts-self._lastTime)/1000, 0.05) : 0;
      self._lastTime = ts; self._time += dt;
      self._update(dt); self._draw();
      self._rafId = requestAnimationFrame(tick);
    }
    this._rafId = requestAnimationFrame(tick);
  };

  MoguScene.prototype.stop = function () {
    this._running = false; cancelAnimationFrame(this._rafId);
    window.removeEventListener('resize', this._resizeHandler);
    if (this._controlPanel && this._controlPanel.parentNode) this._controlPanel.parentNode.removeChild(this._controlPanel);
    if (this._statsEl && this._statsEl.parentNode) this._statsEl.parentNode.removeChild(this._statsEl);
  };

  // --- Internal update ---

  MoguScene.prototype._update = function (dt) {
    var t = this._time;
    if (this._ceremony && t < 3.0) { this._updateCeremony(dt, t); return; }
    // Update items
    for (var i = this._items.length-1; i >= 0; i--) {
      var item = this._items[i];
      if (!item._active) { this._items.splice(i,1); continue; }
      item.progress += dt / item.speed;
      if (item.progress >= 1) { if (item.onArrive) item.onArrive(item); this._items.splice(i,1); }
    }
    if (this._updateFn) this._updateFn(dt, t);
  };

  // --- Internal draw ---

  MoguScene.prototype._draw = function () {
    var ctx = this._ctx, rect = this._canvas.getBoundingClientRect();
    var w = rect.width, h = rect.height, t = this._time;
    // 1. Background
    ctx.fillStyle = this._bg; ctx.fillRect(0,0,w,h);
    // Ceremony override
    if (this._ceremony && t < 3.0) { this._drawCeremony(ctx,w,h,t); return; }
    // 2. Zones (behind everything else)
    this._drawZones(ctx,w,h);
    // 3. Connections
    this._drawConnections(ctx,w,h);
    // 4. Items
    this._drawItems(ctx,w,h,t);
    // 5. Actors (with ghost opacity)
    this._drawActors(ctx,w,h,t);
    // 6. Labels
    this._drawLabels(ctx,w,h,t);
    // 7. Gauges (on top of actors)
    this._drawGauges(ctx,w,h,t);
    // 8. Annotations
    this._drawAnnotations(ctx,w,h);
    // 9. Custom draw
    if (this._drawFn) this._drawFn(ctx,w,h,t);
    // 7. Stats
    this._renderStats();
    // 8. Title
    if (this._title) {
      ctx.fillStyle='#444'; ctx.font='11px "SF Mono",Monaco,monospace'; ctx.textAlign='right';
      ctx.fillText('Mogu Visual / '+this._title, w-16, h-16);
    }
  };

  // --- Connection rendering ---

  MoguScene.prototype._drawConnections = function (ctx, w, h) {
    for (var i = 0; i < this._connections.length; i++) {
      var c = this._connections[i], fa = this._actors[c.from], ta = this._actors[c.to];
      if (!fa || !ta) continue;
      var fx=fa.x*w, fy=fa.y*h, tx=ta.x*w, ty=ta.y*h;
      var dx=tx-fx, dy=ty-fy, dist=Math.sqrt(dx*dx+dy*dy);
      if (dist < 1) continue;
      var nx=dx/dist, ny=dy/dist, sOff=fa.size*0.22, eOff=ta.size*0.22;
      ctx.strokeStyle=c.color; ctx.lineWidth=2;
      if (c.style==='dashed') ctx.setLineDash([6,4]);
      else if (c.style==='dotted') ctx.setLineDash([2,4]);
      else ctx.setLineDash([]);
      ctx.beginPath(); ctx.moveTo(fx+nx*sOff,fy+ny*sOff); ctx.lineTo(tx-nx*eOff,ty-ny*eOff); ctx.stroke();
      ctx.setLineDash([]);
      if (c.arrow) {
        var ax=tx-nx*eOff, ay=ty-ny*eOff, angle=Math.atan2(dy,dx);
        ctx.fillStyle = c.color==='#222' ? '#333' : c.color;
        ctx.save(); ctx.translate(ax,ay); ctx.rotate(angle);
        ctx.beginPath(); ctx.moveTo(0,0); ctx.lineTo(-8,-4); ctx.lineTo(-8,4); ctx.closePath(); ctx.fill(); ctx.restore();
      }
    }
  };

  // --- Item rendering ---

  MoguScene.prototype._drawItems = function (ctx, w, h) {
    for (var i = 0; i < this._items.length; i++) {
      var it = this._items[i]; if (!it._active) continue;
      var fa = this._actors[it.from], ta = this._actors[it.to];
      if (!fa || !ta) continue;
      var p = Math.min(it.progress, 1), ep = ease.inOut(p);
      var ix = fa.x*w + (ta.x*w - fa.x*w)*ep;
      var iy = fa.y*h + (ta.y*h - fa.y*h)*ep - Math.sin(p*Math.PI)*it.arc;
      if (it.glow) { ctx.globalAlpha=0.25; ctx.fillStyle=it.color; ctx.beginPath(); ctx.arc(ix,iy,it.size+4,0,Math.PI*2); ctx.fill(); }
      ctx.globalAlpha=0.9; ctx.fillStyle=it.color;
      if (it.shape==='square') ctx.fillRect(ix-it.size,iy-it.size,it.size*2,it.size*2);
      else if (it.shape==='diamond') { ctx.save(); ctx.translate(ix,iy); ctx.rotate(Math.PI/4); ctx.fillRect(-it.size,-it.size,it.size*2,it.size*2); ctx.restore(); }
      else if (it.shape==='triangle') { ctx.beginPath(); ctx.moveTo(ix,iy-it.size); ctx.lineTo(ix+it.size,iy+it.size*0.7); ctx.lineTo(ix-it.size,iy+it.size*0.7); ctx.closePath(); ctx.fill(); }
      else { ctx.beginPath(); ctx.arc(ix,iy,it.size,0,Math.PI*2); ctx.fill(); }
      ctx.globalAlpha=1;
    }
  };

  // --- Label rendering ---

  MoguScene.prototype._drawLabels = function (ctx, w, h, t) {
    var count = this._actorOrder.length, useShort = count > 3;
    ctx.fillStyle='#555'; ctx.font='11px system-ui,sans-serif'; ctx.textAlign='center';
    for (var i = 0; i < count; i++) {
      var a = this._actors[this._actorOrder[i]]; if (!a) continue;
      var bounce = idleBounce(t + a.bouncePhase, a.bouncePeriod, a.bounceAmplitude);
      var ly = a.y*h + a.size*0.35 + 12 + bounce;
      ctx.fillText(useShort ? a.label.substring(0,3)+(i+1) : a.label, a.x*w, ly);
    }
  };

  // --- Zone rendering ---

  MoguScene.prototype._drawZones = function (ctx, w, h) {
    var zones = this._zones || [];
    for (var i = 0; i < zones.length; i++) {
      var z = zones[i];
      var zx = z.x * w, zy = z.y * h, zw = z.w * w, zh = z.h * h;
      // Fill
      ctx.fillStyle = z.color;
      ctx.fillRect(zx, zy, zw, zh);
      // Border
      ctx.strokeStyle = z.borderColor;
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 3]);
      ctx.strokeRect(zx, zy, zw, zh);
      ctx.setLineDash([]);
      // Label
      if (z.label) {
        ctx.fillStyle = z.labelColor;
        ctx.font = '10px system-ui, sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(z.label, zx + 6, zy + 14);
      }
    }
  };

  // --- Gauge rendering ---

  MoguScene.prototype._drawGauges = function (ctx, w, h, t) {
    var gauges = this._gauges || [];
    for (var i = 0; i < gauges.length; i++) {
      var g = gauges[i], a = this._actors[g.actorId];
      if (!a) continue;
      var bounce = idleBounce(t + a.bouncePhase, a.bouncePeriod, a.bounceAmplitude);
      var gx = a.x * w - g.width / 2;
      var gy = a.y * h + a.size * 0.35 + 18 + bounce + g.offsetY;
      var ratio = Math.min(g.value / g.max, 1);
      // Background
      ctx.fillStyle = '#1a1a1a';
      roundRect(ctx, gx, gy, g.width, g.height, 3);
      ctx.fill();
      ctx.strokeStyle = '#333'; ctx.lineWidth = 1; ctx.stroke();
      // Fill
      if (ratio > 0) {
        var fillColor = ratio < 0.5 ? g.color : ratio < 0.85 ? g.warnColor : g.dangerColor;
        roundRect(ctx, gx + 1, gy + 1, (g.width - 2) * ratio, g.height - 2, 2);
        ctx.fillStyle = fillColor;
        ctx.fill();
      }
      // Threshold marker
      if (g.threshold !== undefined) {
        var tx = gx + g.width * g.threshold;
        ctx.strokeStyle = '#FF4D4D'; ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.moveTo(tx, gy - 2); ctx.lineTo(tx, gy + g.height + 2); ctx.stroke();
      }
      // Label
      if (g.label) {
        ctx.fillStyle = '#555'; ctx.font = '9px system-ui, sans-serif'; ctx.textAlign = 'center';
        ctx.fillText(g.label + ': ' + Math.round(g.value) + '/' + Math.round(g.max), a.x * w, gy + g.height + 10);
      }
    }
  };

  // --- Annotation rendering ---

  MoguScene.prototype._drawAnnotations = function (ctx, w, h) {
    var anns = this._annotations || [];
    for (var i = 0; i < anns.length; i++) {
      var a = anns[i];
      var ax = a.x * w, ay = a.y * h;
      if (a.bg) {
        var m = ctx.measureText(a.text);
        ctx.fillStyle = a.bg;
        roundRect(ctx, ax - m.width / 2 - 4, ay - a.fontSize + 2, m.width + 8, a.fontSize + 6, 3);
        ctx.fill();
      }
      ctx.fillStyle = a.color;
      ctx.font = a.fontSize + 'px system-ui, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(a.text, ax, ay);
    }
  };

  // --- Ghost actor opacity override ---

  MoguScene.prototype._drawActors = function (ctx, w, h, t) {
    var ghosts = this._ghosts || {};
    for (var i = 0; i < this._actorOrder.length; i++) {
      var a = this._actors[this._actorOrder[i]]; if (!a) continue;
      var bounce = idleBounce(t + a.bouncePhase, a.bouncePeriod, a.bounceAmplitude);
      var ghost = ghosts[a.id];
      if (ghost) {
        ctx.globalAlpha = ghost.opacity;
        // Stale lag: offset the bounce slightly
        bounce = idleBounce(t + a.bouncePhase - ghost.staleOffset, a.bouncePeriod, a.bounceAmplitude);
      }
      drawMogu(ctx, a.x*w, a.y*h + bounce, a.size, a.cap.color||'#FF4D4D', a.expression, a._capShapeFn, a._textureFn);
      if (ghost) ctx.globalAlpha = 1;
    }
  };

  // --- Stats rendering ---

  MoguScene.prototype._renderStats = function () {
    var keys = Object.keys(this._stats);
    if (!keys.length) { this._statsEl.textContent = ''; return; }
    var parts = [];
    for (var i = 0; i < keys.length; i++) parts.push(keys[i]+': '+this._stats[keys[i]]);
    this._statsEl.textContent = parts.join('  |  ');
  };

  // --- Absorption ceremony ---

  MoguScene.prototype._updateCeremony = function (dt, t) {
    var cer = this._ceremony; if (!cer) return;
    // Phase 2: keywords float in (0.8-1.5s)
    if (t >= 0.8 && t < 1.5) {
      for (var i=0; i<cer.kwState.length; i++) {
        var kw=cer.kwState[i], elapsed=t-0.8-kw.delay;
        if (elapsed>0) { var p=Math.min(elapsed/0.5,1); kw.alpha=ease.out(p); kw.offsetX=120*(1-ease.out(p)); }
      }
    }
    // Phase 3: keywords shrink (1.5-2.2s)
    if (t >= 1.5 && t < 2.2) {
      for (var i=0; i<cer.kwState.length; i++) {
        var kw=cer.kwState[i], p=Math.min((t-1.5)/0.7,1);
        kw.scale = 1-ease['in'](p); kw.alpha = 1-ease['in'](p);
      }
    }
  };

  MoguScene.prototype._drawCeremony = function (ctx, w, h, t) {
    var cer = this._ceremony, cx=w/2, cy=h/2;
    var bounce = idleBounce(t, 2.5, 2);
    var expr='neutral', capColor='#FF4D4D', capInflate=1.0;
    if (t>=0.8 && t<1.5) expr='curious';
    if (t>=1.5 && t<2.2) { expr='processing'; capInflate = 1+0.15*ease.spring(Math.min((t-1.5)/0.7,1),0.5); }
    if (t>=2.2) {
      expr='proud'; var ct=Math.min((t-2.2)/0.5,1);
      capColor = lerpColor('#FF4D4D', cer.targetColor, ease.out(ct));
      capInflate = 1+0.15*(1-ease.out(Math.min((t-2.2)/0.3,1)));
      if (t>=2.5 && t<2.7) bounce -= Math.sin(((t-2.5)/0.2)*Math.PI)*6;
    }
    var shapeFn = capInflate!==1 ? function(c,mcx,mcy,rx,ry){ c.beginPath(); c.ellipse(mcx,mcy,rx,ry*capInflate,0,0,Math.PI*2); } : null;
    drawMogu(ctx, cx, cy+bounce, 120, capColor, expr, shapeFn, null);
    // Keywords
    if (t >= 0.8) {
      ctx.font="16px 'SF Mono',Monaco,monospace"; ctx.textAlign='left';
      for (var i=0; i<cer.kwState.length; i++) {
        var kw=cer.kwState[i]; if(kw.alpha<=0) continue;
        ctx.globalAlpha=kw.alpha; ctx.fillStyle='#aaa'; ctx.save();
        ctx.translate(cx+80+kw.offsetX, cy-50+i*26); ctx.scale(kw.scale,kw.scale);
        ctx.fillText(kw.text,0,0); ctx.restore();
      }
      ctx.globalAlpha=1;
    }
    ctx.fillStyle='#555'; ctx.font='12px system-ui,sans-serif'; ctx.textAlign='center';
    var phase = t<0.8?'idle':t<1.5?'notice':t<2.2?'swallow':'ready';
    ctx.fillText('Absorption Ceremony: '+phase, cx, h-30);
  };

  // --- Expose globally ---
  global.MoguScene = MoguScene;

})(typeof window !== 'undefined' ? window : this);
