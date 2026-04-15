# Scene Archetypes Reference

Visual patterns for common software concepts, powered by Mogu characters.

Each archetype is a **design template**, not a rigid rule. The AI can combine, modify, or invent new archetypes. The principle: **find the visual metaphor that best matches the concept's structure**.

---

## 1. Pipeline

**Left-to-right conveyor belt** — items flow through sequential processing stages.

### Visual Pattern
Items enter from the left, pass through 2-4 Mogus positioned horizontally, exit on the right. Each Mogu represents a processing stage.

### Layout (800×500 canvas)
```
Stage 1 Mogu: (150, 250)
Stage 2 Mogu: (350, 250)
Stage 3 Mogu: (550, 250)
Input queue: x < 100
Output area: x > 700
```

### Actors
- **Ingester** (left) — green cap, neutral expression, receives raw items
- **Processor** (middle) — blue cap, processing expression, transforms items
- **Emitter** (right) — purple cap, proud expression when successful output

### Item Motion
Items spawn at x=50, move along y=250 horizontal path. Each Mogu briefly "holds" the item (pause 0.3s), then releases it downstream. Items are small circles or boxes (8-12px) with color coding:
- Gray = raw input
- Yellow = processing
- Green = completed

### Parameters
1. **Throughput** (slider, 1-10 items/sec) — spawn rate of new items
2. **Stage Delay** (slider, 0-2s) — processing time per Mogu
3. **Error Rate** (slider, 0-50%) — chance an item turns red and stops at a stage

### Key Moments
- **Backpressure**: items stack up behind a slow Mogu (queue visualizes as overlapping circles)
- **Error**: red item appears, Mogu switches to alert expression, item blinks 3× then vanishes
- **Burst**: 5+ items queued, ingester Mogu switches to processing expression

### Code Sketch
```javascript
// State
var mogus = [
  { x: 150, y: 250, cap: '#4CAF50', expr: 'neutral', holding: null },
  { x: 350, y: 250, cap: '#2196F3', expr: 'neutral', holding: null },
  { x: 550, y: 250, cap: '#9C27B0', expr: 'neutral', holding: null }
];
var items = []; // { x, y, vx, stage, color }

function update(dt) {
  // Spawn items
  if (Math.random() < throughput * dt) {
    items.push({ x: 50, y: 250, vx: 60, stage: 0, color: '#aaa' });
  }

  items.forEach(function (item) {
    var mogu = mogus[item.stage];
    var distToMogu = Math.abs(item.x - mogu.x);

    if (distToMogu < 10 && !mogu.holding) {
      // Mogu captures item
      mogu.holding = item;
      mogu.expr = 'processing';
      setTimeout(function () {
        mogu.holding = null;
        mogu.expr = 'neutral';
        item.stage++;
        item.color = item.stage === 3 ? '#4CAF50' : '#FFEB3B';
      }, stageDelay * 1000);
    } else if (!mogu.holding) {
      item.x += item.vx * dt; // item moves
    }
  });

  // Remove completed items
  items = items.filter(function (i) { return i.x < 750; });
}

function draw(ctx) {
  mogus.forEach(function (m) {
    drawMogu(ctx, m.x, m.y, 80, m.cap, m.expr);
  });
  items.forEach(function (i) {
    ctx.fillStyle = i.color;
    ctx.beginPath();
    ctx.arc(i.x, i.y, 8, 0, Math.PI * 2);
    ctx.fill();
  });
}
```

**Example Concepts**: message queue (RabbitMQ), ETL pipeline (extract→transform→load), CI/CD (build→test→deploy)

---

## 2. Network

**Nodes with edges** — Mogus as vertices, items (packets) move along edges between them.

### Visual Pattern
3-6 Mogus scattered across the canvas, connected by lines. Packets travel along edges. Topology can be mesh, star, or tree depending on concept.

### Layout (800×500 canvas)
```
Node A: (200, 150)
Node B: (600, 150)
Node C: (400, 350)
Edges: A↔B, A↔C, B↔C (for mesh)
```

### Actors
- **Router Mogus** — orange cap, alert expression when forwarding
- **Client Mogus** — green cap, curious expression when sending
- **Server Mogus** — blue cap, processing expression when handling requests

### Item Motion
Packets are small circles (6px) with a tail (last 3 positions drawn fading). They follow linear interpolation along edges at ~200px/sec. When a packet reaches a Mogu:
1. Mogu briefly changes to alert expression
2. Packet disappears or spawns new packets to other nodes (depending on routing logic)

### Parameters
1. **Topology** (stepper, 3-8 nodes) — number of Mogus in the network
2. **Latency** (slider, 0-500ms) — per-edge travel time
3. **Packet Rate** (slider, 1-20/sec) — frequency of new packets

### Key Moments
- **Broadcast**: one Mogu sends packets to all neighbors simultaneously (fan-out animation)
- **Congestion**: multiple packets on same edge, drawn overlapping with slight offset
- **Partition**: an edge turns gray/dashed, packets fail to cross, Mogus on each side switch to alert

### Code Sketch
```javascript
var nodes = [
  { id: 'A', x: 200, y: 150, cap: '#FF9800', expr: 'neutral' },
  { id: 'B', x: 600, y: 150, cap: '#4CAF50', expr: 'neutral' },
  { id: 'C', x: 400, y: 350, cap: '#2196F3', expr: 'neutral' }
];
var edges = [ ['A', 'B'], ['A', 'C'], ['B', 'C'] ];
var packets = []; // { from, to, progress: 0..1 }

function update(dt) {
  packets.forEach(function (p) {
    p.progress += (1 / latency) * dt;
    if (p.progress >= 1) {
      var target = nodes.find(function (n) { return n.id === p.to; });
      target.expr = 'alert';
      setTimeout(function () { target.expr = 'neutral'; }, 200);
      p.done = true;
    }
  });
  packets = packets.filter(function (p) { return !p.done; });

  // Spawn random packet
  if (Math.random() < packetRate * dt) {
    var edge = edges[Math.floor(Math.random() * edges.length)];
    packets.push({ from: edge[0], to: edge[1], progress: 0 });
  }
}

function draw(ctx) {
  // Draw edges
  ctx.strokeStyle = '#333';
  ctx.lineWidth = 2;
  edges.forEach(function (e) {
    var n1 = nodes.find(function (n) { return n.id === e[0]; });
    var n2 = nodes.find(function (n) { return n.id === e[1]; });
    ctx.beginPath();
    ctx.moveTo(n1.x, n1.y);
    ctx.lineTo(n2.x, n2.y);
    ctx.stroke();
  });

  // Draw nodes
  nodes.forEach(function (n) {
    drawMogu(ctx, n.x, n.y, 70, n.cap, n.expr);
  });

  // Draw packets
  packets.forEach(function (p) {
    var n1 = nodes.find(function (n) { return n.id === p.from; });
    var n2 = nodes.find(function (n) { return n.id === p.to; });
    var x = n1.x + (n2.x - n1.x) * ease.out(p.progress);
    var y = n1.y + (n2.y - n1.y) * ease.out(p.progress);
    ctx.fillStyle = '#FFEB3B';
    ctx.beginPath();
    ctx.arc(x, y, 6, 0, Math.PI * 2);
    ctx.fill();
  });
}
```

**Example Concepts**: microservices mesh, DNS resolution (recursive queries), P2P gossip protocol, Raft consensus

---

## 3. Pool/Queue

**Shared resource pool** — items accumulate in a central area, worker Mogus grab them one at a time.

### Visual Pattern
A central "pool zone" (rectangle) where items stack up. 2-4 worker Mogus positioned around the pool, each periodically reaching in to grab an item, process it, then return for another.

### Layout (800×500 canvas)
```
Pool zone: rect(300, 150, 200, 200) — center area
Worker 1: (150, 250)
Worker 2: (650, 250)
Worker 3: (400, 400) — optional
Items spawn at (400, 50), fall into pool
```

### Actors
- **Queue Manager Mogu** — sits at top of pool zone (400, 100), gray cap, neutral expression, doesn't move
- **Worker Mogus** — colored caps (green, blue, orange), curious expression when idle, processing when holding item

### Item Motion
1. Items spawn above pool, fall vertically (gravity: 200px/s²) into pool zone
2. Items in pool stack up, slight jitter to simulate pile
3. Worker Mogu extends a "grabber line" (thin arc) to nearest item, pulls it toward itself (lerp over 0.5s)
4. Worker processes item (cap changes to processing expression, item fades out over 1-2s)
5. Worker returns to idle, repeats

### Parameters
1. **Workers** (stepper, 1-6) — number of worker Mogus
2. **Arrival Rate** (slider, 1-20 items/sec) — how fast items spawn
3. **Processing Time** (slider, 0.5-5s) — how long each worker holds an item

### Key Moments
- **Starvation**: pool empty, all workers idle with curious expression
- **Overload**: pool has 20+ items stacked, some clip outside the pool zone, queue manager switches to alert
- **Balanced**: workers grab items at same rate as arrival, pool stays around 3-5 items

### Code Sketch
```javascript
var pool = { x: 300, y: 150, w: 200, h: 200, items: [] };
var workers = [
  { x: 150, y: 250, cap: '#4CAF50', expr: 'curious', holding: null },
  { x: 650, y: 250, cap: '#2196F3', expr: 'curious', holding: null }
];

function update(dt) {
  // Spawn items
  if (Math.random() < arrivalRate * dt) {
    pool.items.push({ x: 400, y: 50, vy: 0 });
  }

  // Items fall into pool
  pool.items.forEach(function (item) {
    if (item.y < pool.y + pool.h - 20) {
      item.vy += 200 * dt; // gravity
      item.y += item.vy * dt;
    }
  });

  // Workers grab items
  workers.forEach(function (w) {
    if (!w.holding && pool.items.length > 0) {
      w.holding = pool.items.shift();
      w.expr = 'processing';
      setTimeout(function () {
        w.holding = null;
        w.expr = 'curious';
      }, processingTime * 1000);
    }
  });
}

function draw(ctx) {
  // Pool zone
  ctx.strokeStyle = '#555';
  ctx.strokeRect(pool.x, pool.y, pool.w, pool.h);

  // Items in pool
  pool.items.forEach(function (item, i) {
    ctx.fillStyle = '#FFEB3B';
    ctx.beginPath();
    ctx.arc(item.x + (i % 5 - 2) * 10, item.y, 8, 0, Math.PI * 2);
    ctx.fill();
  });

  // Workers
  workers.forEach(function (w) {
    drawMogu(ctx, w.x, w.y, 80, w.cap, w.expr);
    if (w.holding) {
      ctx.fillStyle = '#FFEB3B';
      ctx.beginPath();
      ctx.arc(w.x, w.y - 50, 8, 0, Math.PI * 2);
      ctx.fill();
    }
  });
}
```

**Example Concepts**: thread pool, connection pool (DB), task queue (Celery, Redis Queue), semaphore-controlled resources

---

## 4. State Machine

**Single Mogu, morphing cap** — one Mogu character whose cap shape/color changes to represent different states.

### Visual Pattern
One large Mogu at canvas center. Cap morphs (smooth lerp) when transitioning between states. Items (events) arrive from left, trigger state transitions, exit right.

### Layout (800×500 canvas)
```
Mogu: (400, 250) — center, size=120
Event queue: x < 150
State label: above Mogu at (400, 120)
```

### Actors
- **State Machine Mogu** — cap color and shape change per state:
  - **IDLE**: gray ellipse cap, neutral expression
  - **ACTIVE**: blue ellipse cap, processing expression
  - **SUCCESS**: green ellipse cap, proud expression
  - **ERROR**: red ellipse cap, alert expression

### Item Motion
Events are labeled circles (e.g., "START", "PROCESS", "FAIL"). They spawn at x=100, move toward Mogu at ~100px/sec. On contact:
1. Mogu evaluates event against current state
2. If valid transition: cap color lerps to new state over 0.5s, event disappears
3. If invalid: event bounces off (x velocity reverses), Mogu briefly shows alert expression

### Parameters
1. **Event Rate** (slider, 0.5-5 events/sec) — how often events spawn
2. **Auto-reset** (toggle) — if ON, Mogu auto-transitions back to IDLE after 3s in SUCCESS/ERROR
3. **Invalid Chance** (slider, 0-50%) — probability of invalid event for current state

### Key Moments
- **Valid Transition**: smooth cap morph, expression changes to match new state
- **Invalid Event**: event bounces, Mogu briefly alert, then returns to previous expression
- **Looping**: if auto-reset ON, SUCCESS/ERROR states flash proud/alert, then fade back to IDLE

### Code Sketch
```javascript
var states = {
  IDLE: { color: '#aaa', expr: 'neutral', next: 'ACTIVE' },
  ACTIVE: { color: '#2196F3', expr: 'processing', next: 'SUCCESS' },
  SUCCESS: { color: '#4CAF50', expr: 'proud', next: 'IDLE' },
  ERROR: { color: '#F44336', expr: 'alert', next: 'IDLE' }
};
var currentState = 'IDLE';
var mogu = { x: 400, y: 250, cap: '#aaa', expr: 'neutral', targetCap: '#aaa' };
var events = [];

function update(dt) {
  // Spawn events
  if (Math.random() < eventRate * dt) {
    var label = Math.random() < invalidChance ? 'INVALID' : 'NEXT';
    events.push({ x: 100, y: 250, vx: 100, label: label });
  }

  events.forEach(function (e) {
    e.x += e.vx * dt;

    // Check collision with Mogu
    if (Math.abs(e.x - mogu.x) < 60) {
      if (e.label === 'NEXT') {
        // Valid transition
        currentState = states[currentState].next;
        mogu.targetCap = states[currentState].color;
        mogu.expr = states[currentState].expr;
        e.done = true;
      } else {
        // Invalid event
        e.vx *= -1;
        mogu.expr = 'alert';
        setTimeout(function () { mogu.expr = states[currentState].expr; }, 300);
      }
    }

    if (e.x > 800 || e.x < 0) e.done = true;
  });
  events = events.filter(function (e) { return !e.done; });

  // Lerp cap color
  mogu.cap = lerpColor(mogu.cap, mogu.targetCap, 2 * dt);
}

function draw(ctx) {
  drawMogu(ctx, mogu.x, mogu.y, 120, mogu.cap, mogu.expr);

  ctx.fillStyle = '#eee';
  ctx.font = '16px system-ui';
  ctx.textAlign = 'center';
  ctx.fillText(currentState, mogu.x, 120);

  events.forEach(function (e) {
    ctx.fillStyle = '#FFEB3B';
    ctx.beginPath();
    ctx.arc(e.x, e.y, 10, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#000';
    ctx.font = '8px system-ui';
    ctx.fillText(e.label, e.x, e.y + 3);
  });
}
```

**Example Concepts**: TCP connection states (SYN, ESTABLISHED, FIN-WAIT), order lifecycle (PENDING→PROCESSING→SHIPPED→DELIVERED), authentication flow (LOGGED_OUT→AUTHENTICATING→LOGGED_IN)

---

## 5. Guard/Gate

**Mogu as gatekeeper** — items approach, Mogu inspects, allows/rejects based on criteria.

### Visual Pattern
One Mogu at center, acting as a checkpoint. Items approach from left. Mogu evaluates each (brief pause), then either:
- **Allow**: item continues to right, Mogu shows proud expression
- **Reject**: item bounces back or vanishes, Mogu shows alert expression

### Layout (800×500 canvas)
```
Guard Mogu: (400, 250)
Input lane: y=250, x < 400
Accept lane: y=200, x > 400
Reject zone: y=300, x > 400 (items fade out here)
```

### Actors
- **Guard Mogu** — yellow/orange cap, neutral when idle, alert when rejecting, proud when accepting

### Item Motion
Items spawn at x=50, move right at ~80px/sec. When within 60px of guard:
1. Item stops
2. Mogu evaluates (0.5s delay)
3. **If valid**: item gains green glow, moves to accept lane (y lerps to 200), continues right
4. **If invalid**: item gains red glow, moves to reject zone (y lerps to 300), fades out

### Parameters
1. **Rejection Rate** (slider, 0-100%) — probability an item is rejected
2. **Inspection Time** (slider, 0.2-2s) — how long Mogu holds each item
3. **Strict Mode** (toggle) — if ON, rejected items turn red and blink 3× before vanishing

### Key Moments
- **Acceptance**: item glows green, Mogu briefly proud, item continues smoothly
- **Rejection**: item glows red, Mogu briefly alert, item bounces or fades
- **Queue Buildup**: multiple items waiting, stacked horizontally before guard

### Code Sketch
```javascript
var guard = { x: 400, y: 250, cap: '#FF9800', expr: 'neutral' };
var items = []; // { x, y, vx, state: 'approaching'|'inspecting'|'accepted'|'rejected' }

function update(dt) {
  // Spawn items
  if (Math.random() < 2 * dt) {
    items.push({ x: 50, y: 250, vx: 80, state: 'approaching' });
  }

  items.forEach(function (item) {
    if (item.state === 'approaching') {
      item.x += item.vx * dt;
      if (Math.abs(item.x - guard.x) < 60) {
        item.state = 'inspecting';
        item.vx = 0;
        setTimeout(function () {
          if (Math.random() < rejectionRate) {
            item.state = 'rejected';
            guard.expr = 'alert';
          } else {
            item.state = 'accepted';
            guard.expr = 'proud';
          }
          setTimeout(function () { guard.expr = 'neutral'; }, 300);
        }, inspectionTime * 1000);
      }
    } else if (item.state === 'accepted') {
      item.y += (200 - item.y) * 3 * dt; // lerp to accept lane
      item.x += 100 * dt;
    } else if (item.state === 'rejected') {
      item.y += (300 - item.y) * 3 * dt; // lerp to reject zone
      item.opacity = Math.max(0, (item.opacity || 1) - dt);
    }
  });

  items = items.filter(function (i) { return i.x < 800 && i.opacity !== 0; });
}

function draw(ctx) {
  drawMogu(ctx, guard.x, guard.y, 100, guard.cap, guard.expr);

  items.forEach(function (item) {
    ctx.globalAlpha = item.opacity || 1;
    ctx.fillStyle = item.state === 'accepted' ? '#4CAF50' : item.state === 'rejected' ? '#F44336' : '#FFEB3B';
    ctx.beginPath();
    ctx.arc(item.x, item.y, 8, 0, Math.PI * 2);
    ctx.fill();
  });
  ctx.globalAlpha = 1;
}
```

**Example Concepts**: authentication middleware, firewall (packet filtering), validation layer (schema check), access control (RBAC gate)

---

## 6. Tree

**Parent-child hierarchy** — Mogus arranged in tree structure, items propagate down branches.

### Visual Pattern
Root Mogu at top center, child Mogus below in expanding rows. Lines connect parents to children. Items spawn at root, propagate down based on routing logic.

### Layout (800×500 canvas, binary tree example)
```
Root:        (400, 80)
Level 1:     (250, 200), (550, 200)
Level 2:     (150, 320), (350, 320), (450, 320), (650, 320)
Lines: parent→children
```

### Actors
- **Root Mogu** — large (size=90), purple cap, processing expression
- **Branch Mogus** — medium (size=70), blue cap, neutral expression
- **Leaf Mogus** — small (size=50), green cap, curious expression

### Item Motion
Items spawn at root, pause briefly, then "fall" down a branch to a random child (or deterministic based on item ID). Path is a smooth bezier curve from parent to child, travel time ~0.8s. When item reaches a leaf, it blinks 3× then vanishes.

### Parameters
1. **Branching Factor** (stepper, 2-4) — children per node (rebuilds tree)
2. **Depth** (stepper, 2-4) — tree depth (rebuilds tree)
3. **Spawn Rate** (slider, 0.5-5 items/sec) — items entering at root

### Key Moments
- **Cascade**: one item at root spawns multiple items, one per child (fan-out)
- **Hot Path**: one branch gets 80% of traffic, those Mogus switch to processing expression
- **Leaf Overload**: a leaf accumulates 5+ items, switches to alert expression

### Code Sketch
```javascript
// Tree structure
var tree = {
  root: { x: 400, y: 80, cap: '#9C27B0', expr: 'processing', children: [] }
};

function buildTree(node, depth, maxDepth, branchFactor, xLeft, xRight, y) {
  if (depth >= maxDepth) return;
  var childY = y + 120;
  var childCount = branchFactor;
  var childWidth = (xRight - xLeft) / childCount;
  for (var i = 0; i < childCount; i++) {
    var childX = xLeft + childWidth * (i + 0.5);
    var child = { x: childX, y: childY, cap: depth === maxDepth - 1 ? '#4CAF50' : '#2196F3', expr: 'neutral', children: [] };
    node.children.push(child);
    buildTree(child, depth + 1, maxDepth, branchFactor, xLeft + i * childWidth, xLeft + (i + 1) * childWidth, childY);
  }
}

buildTree(tree.root, 0, 3, 2, 0, 800, 80);

var items = []; // { x, y, targetNode, progress: 0..1 }

function update(dt) {
  if (Math.random() < spawnRate * dt) {
    items.push({ x: tree.root.x, y: tree.root.y, targetNode: tree.root.children[Math.floor(Math.random() * tree.root.children.length)], progress: 0 });
  }

  items.forEach(function (item) {
    item.progress += dt;
    if (item.progress >= 1) {
      if (item.targetNode.children.length > 0) {
        item.targetNode = item.targetNode.children[Math.floor(Math.random() * item.targetNode.children.length)];
        item.progress = 0;
      } else {
        item.done = true; // reached leaf
      }
    }
  });
  items = items.filter(function (i) { return !i.done; });
}

function draw(ctx) {
  // Draw edges
  function drawEdges(node) {
    node.children.forEach(function (child) {
      ctx.strokeStyle = '#555';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(node.x, node.y + 25);
      ctx.lineTo(child.x, child.y - 25);
      ctx.stroke();
      drawEdges(child);
    });
  }
  drawEdges(tree.root);

  // Draw nodes
  function drawNodes(node, depth) {
    var size = 90 - depth * 20;
    drawMogu(ctx, node.x, node.y, size, node.cap, node.expr);
    node.children.forEach(function (c) { drawNodes(c, depth + 1); });
  }
  drawNodes(tree.root, 0);

  // Draw items
  items.forEach(function (item) {
    var t = ease.inOut(item.progress);
    var x = item.x + (item.targetNode.x - item.x) * t;
    var y = item.y + (item.targetNode.y - item.y) * t;
    ctx.fillStyle = '#FFEB3B';
    ctx.beginPath();
    ctx.arc(x, y, 6, 0, Math.PI * 2);
    ctx.fill();
  });
}
```

**Example Concepts**: DOM tree traversal, filesystem hierarchy, B-tree index lookup, organizational chart

---

## 7. Race

**Parallel tracks with competition** — multiple Mogus side-by-side, racing toward a goal. Visualizes concurrency, contention, locks.

### Visual Pattern
3-5 horizontal lanes, one Mogu per lane at left edge. A "finish line" on the right. Mogus race toward it at variable speeds. Optionally: a shared resource (lock) that only one can access at a time.

### Layout (800×500 canvas, 3 racers)
```
Lane 1: y=150, Mogu starts at (100, 150)
Lane 2: y=250, Mogu starts at (100, 250)
Lane 3: y=350, Mogu starts at (100, 350)
Finish line: x=700
Lock zone: rect(400, 100, 80, 300) — only one Mogu can be inside at once
```

### Actors
- **Racer Mogus** — different cap colors (red, blue, green), processing expression when moving, alert when blocked

### Item Motion
Each Mogu has a velocity (randomized or influenced by parameters). They move right. If a lock zone is present:
- First Mogu to enter gets exclusive access, others must wait (velocity→0, expression→alert)
- Lock holder continues at full speed through the zone, releases lock on exit
- Waiting Mogus resume when lock is free

### Parameters
1. **Racers** (stepper, 2-6) — number of Mogus
2. **Lock** (toggle) — enable/disable shared resource contention
3. **Speed Variance** (slider, 0-100%) — how much speeds differ (0=all same, 100=wide range)

### Key Moments
- **Deadlock Simulation** (advanced): two locks, Mogu A holds lock 1 waits for lock 2, Mogu B holds lock 2 waits for lock 1 — both stuck, expressions→alert, blinking effect
- **Photo Finish**: two Mogus cross finish line within 0.1s, both briefly show proud expression
- **Starvation**: one Mogu blocked for 5+ seconds, cap color darkens, expression→processing with wavy mouth

### Code Sketch
```javascript
var racers = [
  { y: 150, x: 100, vx: 80, cap: '#F44336', expr: 'processing', blocked: false },
  { y: 250, x: 100, vx: 60, cap: '#2196F3', expr: 'processing', blocked: false },
  { y: 350, x: 100, vx: 90, cap: '#4CAF50', expr: 'processing', blocked: false }
];
var lockZone = { x: 400, width: 80, holder: null };
var finishLine = 700;

function update(dt) {
  racers.forEach(function (r) {
    if (r.x >= finishLine) {
      r.expr = 'proud';
      return;
    }

    if (lockEnabled) {
      var inLock = r.x >= lockZone.x && r.x < lockZone.x + lockZone.width;
      if (inLock) {
        if (lockZone.holder === null || lockZone.holder === r) {
          lockZone.holder = r;
          r.blocked = false;
          r.expr = 'processing';
        } else {
          r.blocked = true;
          r.expr = 'alert';
          return; // don't move
        }
      } else if (lockZone.holder === r) {
        lockZone.holder = null; // release lock
      }
    }

    r.x += r.vx * dt;
  });
}

function draw(ctx) {
  // Lock zone
  if (lockEnabled) {
    ctx.fillStyle = 'rgba(255, 235, 59, 0.1)';
    ctx.fillRect(lockZone.x, 100, lockZone.width, 300);
    ctx.strokeStyle = '#FFEB3B';
    ctx.strokeRect(lockZone.x, 100, lockZone.width, 300);
  }

  // Finish line
  ctx.strokeStyle = '#eee';
  ctx.setLineDash([5, 5]);
  ctx.beginPath();
  ctx.moveTo(finishLine, 100);
  ctx.lineTo(finishLine, 400);
  ctx.stroke();
  ctx.setLineDash([]);

  // Racers
  racers.forEach(function (r) {
    drawMogu(ctx, r.x, r.y, 70, r.cap, r.expr);
  });
}
```

**Example Concepts**: thread contention, database locks, mutex/semaphore, race conditions, deadlock visualization

---

## 8. Transform

**Item enters, exits transformed** — Mogu acts as a black box. Item goes in one side, different item comes out the other.

### Visual Pattern
One large Mogu at center. Input items enter from left, briefly disappear inside Mogu (opacity→0), then output items emerge from right side. Visual indicator shows transformation (color change, shape change, or label change).

### Layout (800×500 canvas)
```
Transform Mogu: (400, 250), size=120
Input zone: x < 300
Output zone: x > 500
```

### Actors
- **Transformer Mogu** — dual-color cap (gradient or split), processing expression when actively transforming

### Item Motion
1. Input item spawns at x=50, moves right at 100px/sec
2. At x=340 (near Mogu), item lerps toward Mogu center (x=400, y=250) over 0.3s, opacity fades to 0
3. Mogu cap briefly pulses (size +10% for 0.2s)
4. Output item spawns at Mogu center, lerps to x=500 over 0.3s, opacity fades in from 0
5. Output continues right, exits at x=800

### Parameters
1. **Transform Type** (stepper, 3 options) — "Encrypt" (gray→locked icon), "Compile" (text→binary), "Serialize" (object→JSON string)
2. **Processing Time** (slider, 0.2-3s) — delay between input absorption and output emission
3. **Batch Mode** (toggle) — if ON, Mogu waits for 3 items before emitting batch output

### Key Moments
- **Transform**: input disappears, Mogu cap pulses, output emerges with new appearance
- **Batch Accumulation**: Mogu "swells" slightly (size increases by 5% per buffered item)
- **Error**: occasionally (5% chance), output is red "error" item, Mogu briefly shows alert expression

### Code Sketch
```javascript
var mogu = { x: 400, y: 250, cap: '#673AB7', expr: 'processing', size: 120, queue: [] };
var items = []; // { x, y, type: 'input'|'output', opacity: 1, label: 'A'|'B' }

function update(dt) {
  if (Math.random() < 2 * dt) {
    items.push({ x: 50, y: 250, type: 'input', opacity: 1, label: 'A', vx: 100 });
  }

  items.forEach(function (item) {
    if (item.type === 'input') {
      item.x += item.vx * dt;
      if (item.x >= 340 && !item.absorbing) {
        item.absorbing = true;
        item.vx = 0;
        var absorbTime = 0;
        var absorbInterval = setInterval(function () {
          absorbTime += 0.05;
          item.opacity = 1 - absorbTime / 0.3;
          item.x += (mogu.x - item.x) * 0.15;
          item.y += (mogu.y - item.y) * 0.15;
          if (absorbTime >= 0.3) {
            clearInterval(absorbInterval);
            item.done = true;
            mogu.queue.push('transform');
            setTimeout(function () {
              mogu.queue.shift();
              items.push({ x: mogu.x, y: mogu.y, type: 'output', opacity: 0, label: 'B', vx: 100 });
            }, processingTime * 1000);
          }
        }, 50);
      }
    } else if (item.type === 'output') {
      if (item.opacity < 1) {
        item.opacity = Math.min(1, item.opacity + dt * 3);
        item.x += (500 - item.x) * 5 * dt;
      } else {
        item.x += item.vx * dt;
      }
    }
  });

  items = items.filter(function (i) { return !i.done && i.x < 850; });
}

function draw(ctx) {
  var displaySize = mogu.size + mogu.queue.length * 5;
  drawMogu(ctx, mogu.x, mogu.y, displaySize, mogu.cap, mogu.expr);

  items.forEach(function (item) {
    ctx.globalAlpha = item.opacity;
    ctx.fillStyle = item.label === 'A' ? '#aaa' : '#4CAF50';
    ctx.beginPath();
    ctx.arc(item.x, item.y, 10, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#000';
    ctx.font = '10px system-ui';
    ctx.textAlign = 'center';
    ctx.fillText(item.label, item.x, item.y + 3);
  });
  ctx.globalAlpha = 1;
}
```

**Example Concepts**: encryption/decryption, compilation (source→bytecode), serialization (object→JSON), image compression, hashing

---

## 9. Broadcast

**One-to-many distribution** — single sender Mogu at center, multiple receiver Mogus in a circle or arc around it. Sender emits items that fan out to all receivers simultaneously.

### Visual Pattern
Central broadcaster Mogu, 4-8 subscriber Mogus arranged in a circle around it (radius ~200px). When broadcaster emits, items radiate outward along straight lines to each subscriber.

### Layout (800×500 canvas, 6 subscribers)
```
Broadcaster: (400, 250)
Subscribers: evenly spaced on circle, radius=200
  Sub 0: (400 + 200*cos(0°), 250 + 200*sin(0°)) = (600, 250)
  Sub 1: (400 + 200*cos(60°), 250 + 200*sin(60°)) ≈ (500, 77)
  ... and so on
```

### Actors
- **Broadcaster Mogu** — red cap, proud expression when emitting
- **Subscriber Mogus** — blue caps, curious expression when idle, processing when receiving item

### Item Motion
1. Event spawns at broadcaster center (x=400, y=250)
2. N copies of the event are created, one per subscriber
3. Each copy lerps from broadcaster to its target subscriber over 0.8s
4. On arrival, subscriber briefly switches to processing expression, item vanishes

### Parameters
1. **Subscribers** (stepper, 3-10) — number of receiver Mogus (rebuilds circle)
2. **Broadcast Rate** (slider, 0.5-5 events/sec) — how often broadcaster emits
3. **Partition** (toggle) — if ON, randomly exclude 1-2 subscribers from each broadcast (simulates topic filtering)

### Key Moments
- **Fan-out**: all items radiate simultaneously from center, creating a star pattern
- **Partition**: some subscribers don't receive the message (their item turns gray and fades before reaching them)
- **Overload**: broadcaster emits faster than subscribers can "process", items queue up at subscriber positions (overlapping circles)

### Code Sketch
```javascript
var broadcaster = { x: 400, y: 250, cap: '#F44336', expr: 'neutral' };
var subscribers = [];
var subscriberCount = 6;
var items = []; // { x, y, targetX, targetY, progress: 0..1 }

function rebuildSubscribers() {
  subscribers = [];
  var angleStep = (Math.PI * 2) / subscriberCount;
  for (var i = 0; i < subscriberCount; i++) {
    var angle = i * angleStep;
    subscribers.push({
      x: broadcaster.x + 200 * Math.cos(angle),
      y: broadcaster.y + 200 * Math.sin(angle),
      cap: '#2196F3',
      expr: 'curious'
    });
  }
}
rebuildSubscribers();

function update(dt) {
  if (Math.random() < broadcastRate * dt) {
    broadcaster.expr = 'proud';
    subscribers.forEach(function (sub) {
      if (!partition || Math.random() > 0.3) {
        items.push({ x: broadcaster.x, y: broadcaster.y, targetX: sub.x, targetY: sub.y, progress: 0, target: sub });
      }
    });
    setTimeout(function () { broadcaster.expr = 'neutral'; }, 200);
  }

  items.forEach(function (item) {
    item.progress += dt * 1.25;
    if (item.progress >= 1) {
      item.target.expr = 'processing';
      setTimeout(function () { item.target.expr = 'curious'; }, 300);
      item.done = true;
    }
  });
  items = items.filter(function (i) { return !i.done; });
}

function draw(ctx) {
  // Draw lines from broadcaster to subscribers
  ctx.strokeStyle = '#333';
  ctx.setLineDash([5, 5]);
  subscribers.forEach(function (sub) {
    ctx.beginPath();
    ctx.moveTo(broadcaster.x, broadcaster.y);
    ctx.lineTo(sub.x, sub.y);
    ctx.stroke();
  });
  ctx.setLineDash([]);

  // Draw subscribers
  subscribers.forEach(function (sub) {
    drawMogu(ctx, sub.x, sub.y, 60, sub.cap, sub.expr);
  });

  // Draw broadcaster
  drawMogu(ctx, broadcaster.x, broadcaster.y, 100, broadcaster.cap, broadcaster.expr);

  // Draw items
  items.forEach(function (item) {
    var t = ease.out(item.progress);
    var x = item.x + (item.targetX - item.x) * t;
    var y = item.y + (item.targetY - item.y) * t;
    ctx.fillStyle = '#FFEB3B';
    ctx.beginPath();
    ctx.arc(x, y, 6, 0, Math.PI * 2);
    ctx.fill();
  });
}
```

**Example Concepts**: pub/sub messaging (Redis Pub/Sub, NATS), event bus, webhooks (one event triggers multiple HTTP calls), multicast network packets

---

## Combining Archetypes

Complex concepts often require **mixing** multiple archetypes. Here are examples:

### 1. Pipeline + Broadcast: Kafka with Partitions

**Structure**: A horizontal pipeline (3 stages: Producer → Broker → Consumer Group), but at the Consumer stage, the item **broadcasts** to 3 consumer Mogus in parallel.

**Layout**:
- Producer Mogu: (150, 250)
- Broker Mogu: (400, 250)
- Consumer Group: 3 Mogus in vertical column at x=650, y=150/250/350

**Motion**:
- Items flow left-to-right (pipeline) from Producer → Broker
- At Broker, each item **clones** into 3 copies (broadcast)
- Copies fan out to the 3 consumers

**Code Adjustment**: Combine pipeline's sequential flow with broadcast's fan-out logic at the final stage.

**Example Concepts**: Kafka (topic → partitions → consumer group), load balancer (single entry → multiple backends)

---

### 2. Guard + Pool: Connection Pool with Auth

**Structure**: Items (connection requests) first pass through a **Guard** Mogu (authentication check). Accepted items enter a **Pool** where worker Mogus (DB connections) grab them.

**Layout**:
- Guard Mogu: (200, 250)
- Pool zone: rect(400, 150, 200, 200)
- Workers: 3 Mogus around the pool at (350, 250), (600, 250), (475, 350)

**Motion**:
1. Items approach guard from left
2. Guard accepts/rejects (Guard archetype)
3. Accepted items fall into pool
4. Workers grab items from pool (Pool archetype)

**Code Adjustment**: Chain guard logic (step 2) before pool spawn (step 3).

**Example Concepts**: authenticated connection pool, API rate limiter + task queue, ACL + thread pool

---

### 3. Network + State Machine: Distributed Consensus (Raft)

**Structure**: 3-5 Mogus in a **Network** (nodes with edges). Each Mogu is also a **State Machine** (cap color changes: FOLLOWER=gray, CANDIDATE=yellow, LEADER=red). Items (vote requests, heartbeats) travel along edges.

**Layout**:
- Nodes in a mesh: (200, 250), (400, 150), (400, 350), (600, 250)
- Each node has state stored internally

**Motion**:
- Packets travel along edges (Network archetype)
- When a node receives a vote request, its state transitions (State Machine archetype)
- Leader node periodically broadcasts heartbeats (Broadcast archetype integrated)

**Code Adjustment**: Each Mogu has a `state` property. Packet handling triggers state transitions. Leader broadcasts heartbeat packets.

**Example Concepts**: Raft consensus, Paxos, leader election, distributed lock manager

---

## Archetype Selection Guide

When the AI receives a concept request, it should:

1. **Identify the structural pattern**: Is it sequential (Pipeline), many-to-one (Pool), one-to-many (Broadcast), state-based (State Machine), hierarchical (Tree), competitive (Race), conditional (Guard), networked (Network), or transformational (Transform)?

2. **Check for combinations**: Does the concept have multiple structural elements? Example: "distributed task queue with priority" = Pool (queue) + Guard (priority filter).

3. **Map actors to roles**: Who are the key entities? What do they do? Assign Mogu roles (worker, manager, router, etc.) with appropriate cap colors and expressions.

4. **Design item flow**: What moves through the system? Requests, packets, events, data? How do items transform, split, merge, or vanish?

5. **Choose parameters**: What should the user control? Common parameters: rate, count, delay, error probability, mode toggles.

6. **Implement with widgets**: Use `drawMogu`, `createSlider`, `createToggle`, `createStepper` from `widgets.js`. Use `ease` functions for smooth motion.

---

## Notes

- **Expression as feedback**: Use Mogu expressions to show system state. `alert` = error/blocked, `processing` = active work, `proud` = success, `curious` = idle, `neutral` = default.

- **Cap color semantics**: Consistent color coding helps users parse the scene. Suggested palette:
  - Gray `#aaa` = idle/neutral
  - Blue `#2196F3` = active processor
  - Green `#4CAF50` = success/output
  - Red `#F44336` = error/sender
  - Orange `#FF9800` = warning/guard
  - Purple `#9C27B0` = special/root

- **Canvas size**: Default to 800×500 for desktop. For mobile, scale down or use responsive CSS. All coordinates in code sketches assume 800×500.

- **Performance**: Keep item counts < 100 simultaneous. Use `items = items.filter(...)` to clean up off-screen or completed items each frame.

- **Accessibility**: If generating HTML, include text labels above or below canvas describing the concept (e.g., "Visualization of a message queue with 3 worker threads").

---

**End of Scene Archetypes Reference**

These 9 archetypes + combinations provide a **visual vocabulary** for explaining software systems. The AI's job is to **recognize the pattern** in the user's concept request and **compose** the right archetype (or combination) with contextually appropriate Mogu roles, item flows, and parameters.
