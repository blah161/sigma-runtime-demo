# app.py
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- State Machine ---
TRANSITIONS = {
    ("Q1", "Yes"): "Q2",
    ("Q1", "No"): "Q3",
    ("Q2", "Text"): "END",
    ("Q3", "Text"): "END",
}

# --- Proof Generator ---
def make_proof(s, action, s_next):
    return {
    "type": "Proof",
    "from": s,
    "action": action,
    "to": s_next,
    "rule": f"{s} + {action} -> {s_next}",
    "valid": True
}

# --- Runtime (λΣ^R) ---
def step(state, action):
    key = (state, action)
    if key not in TRANSITIONS:
        return None, {"error": "Invalid transition"}

    next_state = TRANSITIONS[key]
    proof = make_proof(state, action, next_state)
    return next_state, proof

# --- UI ---
HTML = """
<!doctype html>
<html>
<head>
<title>λΣ^R Runtime</title>

<style>
:root{
  --bg:#0b1020;
  --panel:rgba(255,255,255,0.06);
  --line:rgba(255,255,255,0.12);
  --text:#fff;
  --muted:rgba(255,255,255,0.65);
  --accent:#8ab4ff;
  --accent2:#b0ffcf;
}

body{
  margin:0;
  font-family:system-ui;
  background:var(--bg);
  color:var(--text);
}

/* LAYOUT */
.container{
  display:grid;
  grid-template-columns: 1fr 1fr;
  height:100vh;
}

/* LEFT: GRAPH */
.graph{
  display:flex;
  align-items:center;
  justify-content:center;
  border-right:1px solid var(--line);
}

/* RIGHT: CONSOLE */
.console{
  padding:24px;
  display:flex;
  flex-direction:column;
}

.header{
  font-size:0.8rem;
  letter-spacing:0.14em;
  color:var(--muted);
}

.state{
  font-size:1.4rem;
  margin:12px 0;
  color:var(--accent2);
  font-family:monospace;
}

.controls button{
  margin:6px;
  padding:10px 14px;
  border:none;
  border-radius:6px;
  background:var(--panel);
  color:white;
  cursor:pointer;
}

.controls button:hover{
  background:linear-gradient(90deg,var(--accent),var(--accent2));
  color:black;
}
.controls button:disabled{
  opacity:0.25;
  cursor:not-allowed;
  background:rgba(255,255,255,0.04);
  color:rgba(255,255,255,0.3);
}

/* PROOF STREAM */
.log{
  margin-top:16px;
  flex:1;
  overflow:auto;
  background:#050a18;
  padding:12px;
  border-radius:8px;
  font-family:monospace;
  font-size:0.9rem;
}

.entry{
  margin-bottom:10px;
  color:var(--accent2);
}

/* GRAPH SVG */
.node{
  fill: #111;
  stroke: var(--line);
  stroke-width:2;
}

.node.active{
  stroke: var(--accent2);
  stroke-width:4;
}

.edge{
  stroke: var(--muted);
  stroke-width:2;
}

.edge.active{
  stroke: var(--accent);
  stroke-width:4;

  /* flowing dash */
  stroke-dasharray:8;
  animation:
    flow 0.8s linear infinite,
    glowPulse 1.2s ease-in-out infinite;

  /* glow */
  filter: drop-shadow(0 0 6px rgba(138,180,255,0.6))
          drop-shadow(0 0 14px rgba(176,255,207,0.4));
}

/* motion */
@keyframes flow{
  to { stroke-dashoffset: -16; }
}

/* pulsing energy */
@keyframes glowPulse{
  0%   { opacity:0.7; }
  50%  { opacity:1; }
  100% { opacity:0.7; }
}

</style>
</head>

<body>

<div class="container">

<!-- GRAPH -->
<div class="graph">

<svg width="300" height="220">

<line id="e1" class="edge" x1="60" y1="60" x2="150" y2="30"/>
<line id="e2" class="edge" x1="60" y1="60" x2="150" y2="120"/>
<line id="e3" class="edge" x1="150" y1="30" x2="240" y2="80"/>
<line id="e4" class="edge" x1="150" y1="120" x2="240" y2="80"/>

<circle id="Q1" class="node active" cx="60" cy="60" r="20"/>
<circle id="Q2" class="node" cx="150" cy="30" r="20"/>
<circle id="Q3" class="node" cx="150" cy="120" r="20"/>
<circle id="END" class="node" cx="240" cy="80" r="20"/>

<text x="60" y="95" fill="white" font-size="12" text-anchor="middle">Q1</text>
<text x="150" y="60" fill="white" font-size="12" text-anchor="middle">Q2</text>
<text x="150" y="155" fill="white" font-size="12" text-anchor="middle">Q3</text>
<text x="240" y="115" fill="white" font-size="12" text-anchor="middle">END</text>

</svg>

</div>

<!-- CONSOLE -->
<div class="console">

<div class="header">AAD SYSTEMS · λΣᴿ RUNTIME</div>

<div class="state">STATE: <span id="state">Q1</span></div>

<div class="controls">
<button onclick="send('Yes')">Yes</button>
<button onclick="send('No')">No</button>
<button onclick="send('Text')">Text</button>
<button onclick="reset()">Reset</button>
</div>


<div style="color:#8ab4ff; margin-bottom:6px;">Execution Trace</div>
<div class="log" id="log"></div>
</div>

</div>

<script>

let currentState = "Q1";

function reset(){
  currentState = "Q1";
  updateState("Q1");
// document.getElementById("log").innerHTML = "";}

function highlightEdge(from,to){

  let edge = null;

  if(from==="Q1" && to==="Q2") edge = e1;
  if(from==="Q1" && to==="Q3") edge = e2;
  if(from==="Q2" && to==="END") edge = e3;
  if(from==="Q3" && to==="END") edge = e4;

  if(!edge) return;

  edge.classList.add("active");

  // fade out trail after delay
  setTimeout(()=>{
    edge.classList.remove("active");
  }, 900);
}

function updateState(state){
  document.getElementById("state").innerText = state;

  // highlight node
  document.querySelectorAll(".node").forEach(n=>n.classList.remove("active"));
  document.getElementById(state).classList.add("active");

  // disable all buttons first
  document.querySelectorAll(".controls button").forEach(b => b.disabled = true);

  // enable only valid transitions
  if(state === "Q1"){
    enableButton("Yes");
    enableButton("No");
  }

  if(state === "Q2" || state === "Q3"){
    enableButton("Text");
  }
}
function enableButton(label){
  document.querySelectorAll(".controls button").forEach(b=>{
    if(b.innerText === label){
      b.disabled = false;
    }
  });
}

function log(proof){
  const time = new Date().toLocaleTimeString();
  const div = document.createElement("div");
  div.className="entry";
  div.innerHTML = `
<span style="color:#8ab4ff">[${time}]</span>

<div style="margin-top:6px">
  <span style="color:#b0ffcf">TRANSITION</span><br>
  State: ${proof.from} → ${proof.to}<br>
  Action: ${proof.action}<br>
  Rule: ${proof.rule}<br>
  <span style="color:#b0ffcf">Status: ${proof.valid ? "VALID" : "INVALID"}</span>
</div>
`;
  document.getElementById("log").appendChild(div);
}

function send(action){
  fetch("/step", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({state:currentState, action:action})
  })
  .then(r=>r.json())
  .then(data=>{

    if(data.error){
      log({
        from: currentState,
        to: "—",
        action: action,
        rule: "Invalid transition",
        valid: false
      });
      return;
    }

    highlightEdge(currentState, data.next_state);

    currentState = data.next_state;

    updateState(currentState);
    log(data.proof);

    if(currentState==="END"){
  log({
    from: "SYSTEM",
    to: "END",
    action: "COMPLETE",
    rule: "Execution complete",
    valid: true
  });

  setTimeout(() => {
    reset();
  }, 1400);
}

});
}
updateState("Q1");
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/step", methods=["POST"])
def step_route():
    data = request.json
    state = data["state"]
    action = data["action"]

    next_state, proof = step(state, action)

    if next_state is None:
        return jsonify(proof)

    return jsonify({
        "next_state": next_state,
        "proof": proof
    })

import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
