# Mogu Visual — Complete Worked Examples

This document shows three complete end-to-end examples demonstrating the full Mogu Visual pipeline: from natural language input → scene script → key implementation code.

---

## Example 1: Message Queue (Pipeline Archetype)

### Input

"Explain how a message queue works with producers, a broker, and consumers"

### Scene Script

```
Scene: Message Queue
Archetype: pipeline
Actors:
  - Producer (small, #EF4444 red cap, classic dome, classic spots) — emits messages
  - Broker (large, #3068B0 denim blue cap, flat/shiitake shape, hexagonal texture) — queues messages
  - Consumer x3 (small, #3A8860 forest cap, classic dome, classic spots) — processes messages
Items: messages (small colored rectangles, flow Producer → Broker → Consumers)
Parameters:
  - message_rate: slider 1-50/s, default 5 — how fast producer emits
  - consumer_count: stepper 1-5, default 3 — number of active consumers
  - queue_capacity: slider 10-100, default 30 — broker queue depth limit
Key Moments:
  - consumer dies → click to kill a consumer, messages pile up in broker, broker cap inflates
  - rate spike → push rate above capacity, broker alert expression, messages overflow
```

### Key Implementation Code

```javascript
// Message Queue Visualization

// State
var messages = []; // { x, y, state: 'traveling' | 'queued' | 'consuming', targetConsumer: index }
var consumers = [{ x: 700, y: 200, active: true }, { x: 700, y: 300, active: true }, { x: 700, y: 400, active: true }];
var queuedMessages = [];
var messageRate = 5; // messages per second
var queueCapacity = 30;
var consumerCount = 3;
var timeSinceLastMessage = 0;

var producerPos = { x: 100, y: 300 };
var brokerPos = { x: 400, y: 300 };

function update(dt) {
  // Spawn new messages based on rate
  timeSinceLastMessage += dt;
  var interval = 1.0 / messageRate;
  if (timeSinceLastMessage >= interval) {
    messages.push({ 
      x: producerPos.x + 40, 
      y: producerPos.y, 
      state: 'traveling', 
      targetX: brokerPos.x - 60,
      targetY: brokerPos.y 
    });
    timeSinceLastMessage = 0;
  }

  // Update message positions
  for (var i = messages.length - 1; i >= 0; i--) {
    var msg = messages[i];
    
    if (msg.state === 'traveling') {
      // Move toward broker
      var dx = msg.targetX - msg.x;
      var dy = msg.targetY - msg.y;
      var dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 5) {
        // Arrived at broker — queue it
        if (queuedMessages.length < queueCapacity) {
          msg.state = 'queued';
          queuedMessages.push(msg);
        } else {
          // Queue overflow — remove message
          messages.splice(i, 1);
        }
      } else {
        msg.x += (dx / dist) * 150 * dt;
        msg.y += (dy / dist) * 150 * dt;
      }
    } else if (msg.state === 'queued') {
      // Wait in broker queue
      // Check if we can assign to a consumer
      var activeConsumers = consumers.filter(function(c) { return c.active; });
      if (activeConsumers.length > 0 && Math.random() < 0.5 * dt) {
        var consumer = activeConsumers[Math.floor(Math.random() * activeConsumers.length)];
        msg.state = 'consuming';
        msg.targetX = consumer.x;
        msg.targetY = consumer.y;
        queuedMessages.splice(queuedMessages.indexOf(msg), 1);
      }
    } else if (msg.state === 'consuming') {
      // Move toward consumer
      var dx = msg.targetX - msg.x;
      var dy = msg.targetY - msg.y;
      var dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 5) {
        // Consumed — remove
        messages.splice(i, 1);
      } else {
        msg.x += (dx / dist) * 200 * dt;
        msg.y += (dy / dist) * 200 * dt;
      }
    }
  }
}

function draw(ctx, width, height) {
  // Determine broker expression based on queue load
  var queueLoad = queuedMessages.length / queueCapacity;
  var brokerExpr = queueLoad > 0.9 ? 'alert' : queueLoad > 0.5 ? 'processing' : 'neutral';
  
  // Broker cap inflation based on queue size
  var baseSize = 120;
  var brokerSize = baseSize * (1 + queueLoad * 0.3);

  // Draw Producer Mogu
  drawMogu(ctx, producerPos.x, producerPos.y, 80, '#EF4444', 'proud');

  // Draw Broker Mogu with dynamic cap shape
  function flatCap(ctx, cx, cy, capRx, capRy) {
    ctx.beginPath();
    ctx.ellipse(cx, cy, capRx, capRy * 0.6, 0, 0, Math.PI * 2);
  }
  function hexTexture(ctx, cx, cy, capRx, capRy, spotColor) {
    ctx.globalAlpha = 0.7;
    ctx.strokeStyle = spotColor;
    ctx.lineWidth = capRx * 0.03;
    var hexSize = capRx * 0.2;
    var positions = [
      [cx - hexSize, cy - hexSize * 0.6],
      [cx + hexSize, cy - hexSize * 0.6],
      [cx, cy],
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
  drawMogu(ctx, brokerPos.x, brokerPos.y, brokerSize, '#3068B0', brokerExpr, flatCap, hexTexture);

  // Draw queue visualization inside broker
  ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
  ctx.fillRect(brokerPos.x - 40, brokerPos.y - 50, 80, 100);
  ctx.fillStyle = '#3068B0';
  var queueHeight = (queuedMessages.length / queueCapacity) * 100;
  ctx.fillRect(brokerPos.x - 40, brokerPos.y + 50 - queueHeight, 80, queueHeight);

  // Draw Consumer Mogus
  for (var i = 0; i < consumerCount; i++) {
    if (consumers[i].active) {
      drawMogu(ctx, consumers[i].x, consumers[i].y, 80, '#3A8860', 'processing');
    } else {
      // Dead consumer — faded
      ctx.globalAlpha = 0.3;
      drawMogu(ctx, consumers[i].x, consumers[i].y, 80, '#8C8C8C', 'alert');
      ctx.globalAlpha = 1.0;
    }
  }

  // Draw messages
  messages.forEach(function(msg) {
    ctx.fillStyle = '#FFB84D';
    ctx.fillRect(msg.x - 6, msg.y - 6, 12, 12);
  });
}
```

### What This Teaches

- **State management**: tracking messages through multiple states (traveling, queued, consuming)
- **Dynamic expression**: broker expression changes based on queue load
- **Visual feedback**: cap size inflates as queue fills, providing instant visual cue
- **Parameter interaction**: message_rate and consumer_count directly affect visual behavior
- **Cap shape/texture**: flat/shiitake shape + hexagonal texture convey "platform/infrastructure"

---

## Example 2: Load Balancer (Broadcast + Guard Hybrid)

### Input

"How does a load balancer distribute requests to servers?"

### Scene Script

```
Scene: Load Balancer
Archetype: broadcast + guard
Actors:
  - Client Cloud (small, #E07850 terracotta cap, multi-bump shape) — source of requests
  - Load Balancer (large, #E8A840 honey gold cap, split/forked shape, scales texture) — distributes
  - Server x3 (medium, #2898A0 teal cap, classic dome, circuit texture) — processes requests
Items: requests (small circles, rain from top → LB → servers)
Parameters:
  - algorithm: toggle [Round Robin | Least Connections | Random], default Round Robin
  - request_rate: slider 1-30/s, default 8
  - server_count: stepper 1-5, default 3
Key Moments:
  - server overloaded → one server processes too many, turns alert, LB reroutes
  - server dies → click to kill, LB removes from pool, remaining servers handle more
```

### Key Implementation Code

```javascript
// Load Balancer Visualization

// State
var requests = []; // { x, y, state: 'incoming' | 'routing' | 'processing', targetServer: index }
var servers = [
  { x: 600, y: 150, active: true, load: 0 },
  { x: 600, y: 300, active: true, load: 0 },
  { x: 600, y: 450, active: true, load: 0 }
];
var algorithm = 'roundRobin'; // 'roundRobin' | 'leastConnections' | 'random'
var requestRate = 8;
var serverCount = 3;
var roundRobinIndex = 0;
var timeSinceLastRequest = 0;

var clientPos = { x: 100, y: 300 };
var lbPos = { x: 350, y: 300 };

function update(dt) {
  // Spawn requests
  timeSinceLastRequest += dt;
  var interval = 1.0 / requestRate;
  if (timeSinceLastRequest >= interval) {
    requests.push({ 
      x: clientPos.x + 30, 
      y: clientPos.y, 
      state: 'incoming',
      targetX: lbPos.x,
      targetY: lbPos.y
    });
    timeSinceLastRequest = 0;
  }

  // Update requests
  for (var i = requests.length - 1; i >= 0; i--) {
    var req = requests[i];

    if (req.state === 'incoming') {
      // Move to load balancer
      var dx = req.targetX - req.x;
      var dy = req.targetY - req.y;
      var dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 5) {
        // Arrived — select server based on algorithm
        var targetServer = selectServer();
        if (targetServer !== null) {
          req.state = 'routing';
          req.targetServer = targetServer;
          req.targetX = servers[targetServer].x;
          req.targetY = servers[targetServer].y;
        } else {
          // No available servers — drop request
          requests.splice(i, 1);
        }
      } else {
        req.x += (dx / dist) * 200 * dt;
        req.y += (dy / dist) * 200 * dt;
      }
    } else if (req.state === 'routing') {
      // Move to selected server
      var dx = req.targetX - req.x;
      var dy = req.targetY - req.y;
      var dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 5) {
        req.state = 'processing';
        servers[req.targetServer].load++;
      } else {
        req.x += (dx / dist) * 250 * dt;
        req.y += (dy / dist) * 250 * dt;
      }
    } else if (req.state === 'processing') {
      // Processing — random completion
      if (Math.random() < 0.8 * dt) {
        servers[req.targetServer].load--;
        requests.splice(i, 1);
      }
    }
  }
}

function selectServer() {
  var activeServers = servers.map(function(s, i) { return s.active ? i : null; }).filter(function(x) { return x !== null; });
  if (activeServers.length === 0) return null;

  if (algorithm === 'roundRobin') {
    // Round robin
    var attempts = 0;
    while (!servers[roundRobinIndex % servers.length].active && attempts < servers.length) {
      roundRobinIndex++;
      attempts++;
    }
    var selected = roundRobinIndex % servers.length;
    roundRobinIndex++;
    return selected;
  } else if (algorithm === 'leastConnections') {
    // Least connections
    var minLoad = Infinity;
    var minIndex = null;
    activeServers.forEach(function(i) {
      if (servers[i].load < minLoad) {
        minLoad = servers[i].load;
        minIndex = i;
      }
    });
    return minIndex;
  } else {
    // Random
    return activeServers[Math.floor(Math.random() * activeServers.length)];
  }
}

function draw(ctx, width, height) {
  // Draw Client Mogu
  function multiBumpCap(ctx, cx, cy, capRx, capRy) {
    var r = capRx * 0.5;
    ctx.beginPath();
    ctx.arc(cx - capRx * 0.4, cy, r, 0, Math.PI * 2);
    ctx.arc(cx + capRx * 0.4, cy, r, 0, Math.PI * 2);
    ctx.arc(cx, cy - capRy * 0.3, r, 0, Math.PI * 2);
  }
  drawMogu(ctx, clientPos.x, clientPos.y, 70, '#E07850', 'neutral', multiBumpCap);

  // Draw Load Balancer
  function splitCap(ctx, cx, cy, capRx, capRy) {
    var offset = capRx * 0.3;
    ctx.beginPath();
    ctx.ellipse(cx - offset, cy, capRx * 0.6, capRy, 0, 0, Math.PI * 2);
    ctx.closePath();
    ctx.beginPath();
    ctx.ellipse(cx + offset, cy, capRx * 0.6, capRy, 0, 0, Math.PI * 2);
  }
  function scalesTexture(ctx, cx, cy, capRx, capRy, spotColor) {
    ctx.globalAlpha = 0.7;
    ctx.strokeStyle = spotColor;
    ctx.lineWidth = capRx * 0.03;
    var scaleW = capRx * 0.3;
    for (var row = 0; row < 2; row++) {
      for (var col = 0; col < 3; col++) {
        var x = cx + (col - 1) * scaleW * 0.8;
        var y = cy + (row - 0.5) * capRy * 0.5;
        ctx.beginPath();
        ctx.arc(x, y, scaleW * 0.4, 0, Math.PI, true);
        ctx.stroke();
      }
    }
    ctx.globalAlpha = 1.0;
  }
  drawMogu(ctx, lbPos.x, lbPos.y, 110, '#E8A840', 'processing', splitCap, scalesTexture);

  // Draw Servers
  function circuitTexture(ctx, cx, cy, capRx, capRy, spotColor) {
    ctx.globalAlpha = 0.7;
    ctx.strokeStyle = spotColor;
    ctx.lineWidth = capRx * 0.025;
    ctx.beginPath();
    ctx.moveTo(cx - capRx * 0.6, cy - capRy * 0.4);
    ctx.lineTo(cx - capRx * 0.2, cy - capRy * 0.4);
    ctx.lineTo(cx - capRx * 0.2, cy);
    ctx.lineTo(cx + capRx * 0.3, cy);
    ctx.stroke();
    ctx.fillStyle = spotColor;
    ctx.beginPath();
    ctx.arc(cx + capRx * 0.3, cy, capRx * 0.06, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1.0;
  }

  for (var i = 0; i < serverCount; i++) {
    var server = servers[i];
    if (server.active) {
      // Color shifts based on load
      var loadRatio = Math.min(server.load / 5, 1);
      var serverExpr = loadRatio > 0.7 ? 'alert' : 'processing';
      var serverColor = loadRatio > 0.7 ? '#EF4444' : '#2898A0';
      drawMogu(ctx, server.x, server.y, 90, serverColor, serverExpr, null, circuitTexture);
      
      // Load indicator
      ctx.fillStyle = '#aaa';
      ctx.font = '12px monospace';
      ctx.fillText('Load: ' + server.load, server.x - 25, server.y + 60);
    } else {
      ctx.globalAlpha = 0.3;
      drawMogu(ctx, server.x, server.y, 90, '#8C8C8C', 'alert');
      ctx.globalAlpha = 1.0;
    }
  }

  // Draw requests
  requests.forEach(function(req) {
    ctx.fillStyle = '#52C77A';
    ctx.beginPath();
    ctx.arc(req.x, req.y, 5, 0, Math.PI * 2);
    ctx.fill();
  });
}
```

### What This Teaches

- **Algorithm implementation**: three different load balancing strategies (round-robin, least-connections, random)
- **Dynamic visual feedback**: server cap color shifts from teal to red as load increases
- **Health management**: server death removes it from the pool, visual fades inactive servers
- **Cap shape meaning**: split/forked shape conveys "branching logic" of load balancing
- **Texture semantics**: scales texture represents "queuing/layered structure" of request distribution

---

## Example 3: Public Key Encryption (Transform Archetype)

### Input

"Show how public key encryption works — encrypting with a public key and decrypting with a private key"

### Scene Script

```
Scene: Public Key Encryption
Archetype: transform (two-stage)
Actors:
  - Sender Mogu (medium, #3068B0 denim blue cap, classic dome) — has receiver's public key
  - Encrypt Transform (large, #3A8860 forest cap, spiky/urchin shape, circuit texture) — encryption engine
  - Channel (visual only, no Mogu) — shows ciphertext traveling
  - Decrypt Transform (large, #6850A0 plum cap, pointy/wizard shape, constellation texture) — decryption engine
  - Receiver Mogu (medium, #C85080 rose cap, classic dome) — has private key
Items:
  - Plaintext: readable text block (green) → enters encrypt Mogu
  - Ciphertext: garbled block (red, scrambled pattern) → travels channel → enters decrypt Mogu
  - Recovered plaintext: readable again (green) → reaches receiver
Parameters:
  - key_size: toggle [128-bit | 256-bit], default 128-bit — affects visual complexity of transform animation
  - show_keys: toggle, default on — show/hide key icons on transform Mogus
Key Moments:
  - wrong key → toggle to show what happens with wrong decryption key, garbled output, alert expression
  - man in the middle → ciphertext in channel is visually unreadable, demonstrating encryption value
```

### Key Implementation Code

```javascript
// Public Key Encryption Visualization

// State
var items = []; // { x, y, type: 'plaintext' | 'encrypting' | 'ciphertext' | 'decrypting' | 'recovered', content: string, scrambleProgress: 0-1 }
var keySize = 128; // 128 or 256
var showKeys = true;
var wrongKey = false;
var timeSinceLastItem = 0;
var itemInterval = 3; // seconds between items

var senderPos = { x: 80, y: 300 };
var encryptPos = { x: 250, y: 300 };
var decryptPos = { x: 550, y: 300 };
var receiverPos = { x: 720, y: 300 };

function update(dt) {
  // Spawn plaintext items
  timeSinceLastItem += dt;
  if (timeSinceLastItem >= itemInterval) {
    items.push({
      x: senderPos.x + 40,
      y: senderPos.y,
      type: 'plaintext',
      content: 'HELLO',
      scrambleProgress: 0,
      targetX: encryptPos.x - 50,
      targetY: encryptPos.y
    });
    timeSinceLastItem = 0;
  }

  // Update items
  for (var i = items.length - 1; i >= 0; i--) {
    var item = items[i];

    if (item.type === 'plaintext') {
      // Move to encrypt Mogu
      var dx = item.targetX - item.x;
      var dy = item.targetY - item.y;
      var dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 5) {
        item.type = 'encrypting';
        item.scrambleProgress = 0;
      } else {
        item.x += (dx / dist) * 100 * dt;
        item.y += (dy / dist) * 100 * dt;
      }
    } else if (item.type === 'encrypting') {
      // Animate scramble inside encrypt Mogu
      item.scrambleProgress += dt * 0.8;
      if (item.scrambleProgress >= 1) {
        item.type = 'ciphertext';
        item.x = encryptPos.x + 50;
        item.targetX = decryptPos.x - 50;
        item.scrambleProgress = 1;
      }
    } else if (item.type === 'ciphertext') {
      // Travel through channel to decrypt Mogu
      var dx = item.targetX - item.x;
      var dy = item.targetY - item.y;
      var dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 5) {
        item.type = 'decrypting';
        item.scrambleProgress = 1;
      } else {
        item.x += (dx / dist) * 120 * dt;
        item.y += (dy / dist) * 120 * dt;
      }
    } else if (item.type === 'decrypting') {
      // Animate unscramble (or fail if wrong key)
      if (wrongKey) {
        item.scrambleProgress = 1; // stays scrambled
        if (Math.random() < 0.5 * dt) {
          item.type = 'recovered'; // but still garbled
          item.x = decryptPos.x + 50;
          item.targetX = receiverPos.x;
        }
      } else {
        item.scrambleProgress -= dt * 0.8;
        if (item.scrambleProgress <= 0) {
          item.type = 'recovered';
          item.scrambleProgress = 0;
          item.x = decryptPos.x + 50;
          item.targetX = receiverPos.x;
        }
      }
    } else if (item.type === 'recovered') {
      // Move to receiver
      var dx = item.targetX - item.x;
      var dy = item.targetY - item.y;
      var dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 5) {
        items.splice(i, 1);
      } else {
        item.x += (dx / dist) * 100 * dt;
        item.y += (dy / dist) * 100 * dt;
      }
    }
  }
}

function draw(ctx, width, height) {
  // Draw Sender
  drawMogu(ctx, senderPos.x, senderPos.y, 90, '#3068B0', 'neutral');

  // Draw Encrypt Mogu (spiky shape)
  function spikyCap(ctx, cx, cy, capRx, capRy) {
    ctx.beginPath();
    var spikes = 8;
    for (var i = 0; i < spikes; i++) {
      var angle = (i / spikes) * Math.PI * 2;
      var nextAngle = ((i + 1) / spikes) * Math.PI * 2;
      var midAngle = (angle + nextAngle) / 2;
      var x1 = cx + Math.cos(angle) * capRx * 0.7;
      var y1 = cy + Math.sin(angle) * capRy * 0.7;
      var x2 = cx + Math.cos(midAngle) * capRx * 1.2;
      var y2 = cy + Math.sin(midAngle) * capRy * 1.2;
      if (i === 0) ctx.moveTo(x1, y1);
      else ctx.lineTo(x1, y1);
      ctx.lineTo(x2, y2);
    }
    ctx.closePath();
  }
  function circuitTexture(ctx, cx, cy, capRx, capRy, spotColor) {
    ctx.globalAlpha = 0.7;
    ctx.strokeStyle = spotColor;
    ctx.lineWidth = capRx * 0.025;
    ctx.beginPath();
    ctx.moveTo(cx - capRx * 0.5, cy);
    ctx.lineTo(cx + capRx * 0.5, cy);
    ctx.stroke();
    ctx.fillStyle = spotColor;
    ctx.beginPath();
    ctx.arc(cx, cy, capRx * 0.08, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1.0;
  }
  var encryptExpr = items.some(function(i) { return i.type === 'encrypting'; }) ? 'processing' : 'neutral';
  drawMogu(ctx, encryptPos.x, encryptPos.y, 120, '#3A8860', encryptExpr, spikyCap, circuitTexture);
  
  if (showKeys) {
    ctx.fillStyle = '#FFD966';
    ctx.font = '12px monospace';
    ctx.fillText('🔓', encryptPos.x - 10, encryptPos.y - 80);
  }

  // Draw Decrypt Mogu (pointy/wizard shape)
  function pointyCap(ctx, cx, cy, capRx, capRy) {
    ctx.beginPath();
    ctx.moveTo(cx - capRx, cy + capRy * 0.3);
    ctx.quadraticCurveTo(cx, cy - capRy * 1.2, cx + capRx, cy + capRy * 0.3);
    ctx.lineTo(cx - capRx, cy + capRy * 0.3);
  }
  function constellationTexture(ctx, cx, cy, capRx, capRy, spotColor) {
    ctx.globalAlpha = 0.7;
    var nodes = [
      [cx - capRx * 0.3, cy - capRy * 0.4],
      [cx + capRx * 0.3, cy - capRy * 0.3],
      [cx, cy]
    ];
    ctx.strokeStyle = spotColor;
    ctx.lineWidth = capRx * 0.02;
    ctx.beginPath();
    ctx.moveTo(nodes[0][0], nodes[0][1]);
    ctx.lineTo(nodes[2][0], nodes[2][1]);
    ctx.lineTo(nodes[1][0], nodes[1][1]);
    ctx.stroke();
    ctx.fillStyle = spotColor;
    nodes.forEach(function(node) {
      ctx.beginPath();
      ctx.arc(node[0], node[1], capRx * 0.05, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.globalAlpha = 1.0;
  }
  var decryptExpr = wrongKey && items.some(function(i) { return i.type === 'decrypting'; }) ? 'alert' : 
                    items.some(function(i) { return i.type === 'decrypting'; }) ? 'processing' : 'neutral';
  drawMogu(ctx, decryptPos.x, decryptPos.y, 120, '#6850A0', decryptExpr, pointyCap, constellationTexture);
  
  if (showKeys) {
    ctx.fillStyle = wrongKey ? '#EF4444' : '#52C77A';
    ctx.font = '12px monospace';
    ctx.fillText('🔐', decryptPos.x - 10, decryptPos.y - 80);
  }

  // Draw Receiver
  var receiverExpr = wrongKey && items.some(function(i) { return i.type === 'recovered' && i.scrambleProgress > 0; }) ? 'alert' : 'proud';
  drawMogu(ctx, receiverPos.x, receiverPos.y, 90, '#C85080', receiverExpr);

  // Draw items
  items.forEach(function(item) {
    if (item.type === 'encrypting' || item.type === 'decrypting') {
      // Inside transform Mogu — don't draw (absorbed)
      return;
    }

    var isScrambled = item.scrambleProgress > 0;
    ctx.fillStyle = isScrambled ? '#EF4444' : '#52C77A';
    ctx.fillRect(item.x - 20, item.y - 8, 40, 16);
    
    ctx.fillStyle = '#0a0a0a';
    ctx.font = '10px monospace';
    var displayText = item.content;
    if (isScrambled) {
      // Scramble visual
      displayText = '';
      for (var j = 0; j < item.content.length; j++) {
        displayText += String.fromCharCode(65 + Math.floor(Math.random() * 26));
      }
    }
    ctx.fillText(displayText, item.x - 15, item.y + 3);
  });

  // Channel visualization
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
  ctx.lineWidth = 2;
  ctx.setLineDash([5, 5]);
  ctx.beginPath();
  ctx.moveTo(encryptPos.x + 60, encryptPos.y);
  ctx.lineTo(decryptPos.x - 60, decryptPos.y);
  ctx.stroke();
  ctx.setLineDash([]);
}
```

### What This Teaches

- **Two-stage transform**: plaintext → encrypting (absorbed) → ciphertext → decrypting (absorbed) → recovered
- **Visual scramble effect**: text morphs from readable to garbled based on `scrambleProgress`
- **Wrong-key scenario**: demonstrates failed decryption, output stays garbled, decrypt Mogu shows alert
- **Shape semantics**: spiky/urchin for encryption (security/defense), pointy/wizard for decryption (logic/algorithm)
- **Texture semantics**: circuit for encryption (computation), constellation for decryption (network/connection)
- **Key visualization**: lock/unlock icons show public/private keys, color-coded for correctness

---

## Summary

These three examples demonstrate:

1. **Message Queue** — state-driven pipeline with dynamic visual feedback (cap inflation, expression)
2. **Load Balancer** — algorithm selection with real-time load visualization (color shift, load counter)
3. **Public Key Encryption** — multi-stage transform with visual encoding/decoding (scramble animation, wrong-key handling)

All examples follow the same pattern:
- Natural language input → scene script → implementation
- Use `drawMogu(ctx, x, y, size, capColor, expression, capShape, texture)` from `widgets.js`
- Implement `update(dt)` for state transitions and `draw(ctx, width, height)` for rendering
- Cap shapes/textures convey structural metaphors
- Expressions and dynamic sizing provide real-time feedback
