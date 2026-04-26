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
  <title>λΣ^R Verified Flow Demo</title>
  <style>
    :root{
      --bg:#0b1020;
      --panel:rgba(255,255,255,0.06);
      --text:rgba(255,255,255,0.92);
      --muted:rgba(255,255,255,0.70);
      --faint:rgba(255,255,255,0.50);
      --line:rgba(255,255,255,0.12);
      --accent:#8ab4ff;
      --accent2:#b0ffcf;
    }

    body{
      margin:0;
      min-height:100vh;
      font-family:ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
      background:
        radial-gradient(900px 500px at 20% 10%, rgba(138,180,255,0.20), transparent 60%),
        radial-gradient(900px 500px at 80% 20%, rgba(176,255,207,0.10), transparent 60%),
        var(--bg);
      color:var(--text);
      display:flex;
      align-items:center;
      justify-content:center;
      padding:32px;
    }

    .card{
      width:min(720px, 100%);
      background:var(--panel);
      border:1px solid var(--line);
      border-radius:18px;
      padding:28px;
      box-shadow:0 18px 60px rgba(0,0,0,0.45);
    }

    .label{
      font-size:0.72rem;
      letter-spacing:0.14em;
      text-transform:uppercase;
      color:var(--faint);
      margin-bottom:10px;
    }

    h1{
      margin:0 0 12px 0;
      font-size:1.8rem;
      line-height:1.15;
      letter-spacing:-0.02em;
    }

    .badge{
      display:inline-block;
      padding:4px 12px;
      border-radius:999px;
      border:1px solid var(--line);
      background:rgba(255,255,255,0.05);
      color:var(--faint);
      font-size:0.82rem;
      margin-bottom:22px;
    }

    .state{
      font-size:1.15rem;
      margin:18px 0;
      color:var(--muted);
    }

    #state{
      color:var(--accent2);
      font-weight:700;
      font-family:ui-monospace, SFMono-Regular, Menlo, monospace;
    }

    button{
      padding:10px 16px;
      margin:0 8px 12px 0;
      border-radius:8px;
      border:1px solid var(--line);
      background:rgba(255,255,255,0.06);
      color:var(--text);
      font-weight:600;
      cursor:pointer;
    }

    button:hover{
      background:linear-gradient(90deg, var(--accent), var(--accent2));
      color:#000;
    }

    pre{
      margin-top:18px;
      padding:16px;
      border-radius:10px;
      background:#050a18;
      border:1px solid var(--line);
      color:var(--accent2);
      font-family:ui-monospace, SFMono-Regular, Menlo, monospace;
      white-space:pre-wrap;
      min-height:90px;
    }

    .note{
      margin-top:16px;
      color:var(--faint);
      font-size:0.9rem;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="label">AAD Systems · Executable Research Demo</div>

    <h1>Verified Flow Engine (λΣᴿ)</h1>

    <div class="badge">Type Theory · Runtime Semantics · Proof-Carrying Execution</div>

    <div class="state">
      Current State: <span id="state">Q1</span>
    </div>

    <button onclick="send('Yes')">Yes</button>
    <button onclick="send('No')">No</button>
    <button onclick="send('Text')">Text</button>
    <button onclick="reset()">Reset</button>

    <pre id="output">Awaiting transition...</pre>

    <div class="note">
      Each valid transition returns a next state together with a proof object.
    </div>
  </div>

<script>
let currentState = "Q1";

function reset() {
  currentState = "Q1";
  document.getElementById("state").innerText = "Q1";
  document.getElementById("output").innerText = "Reset to Q1";
}

function send(action) {
  fetch("/step", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({state: currentState, action: action})
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      document.getElementById("output").innerText = data.error;
      return;
    }

    currentState = data.next_state;

    document.getElementById("state").innerText = currentState;
    document.getElementById("output").innerText =
      JSON.stringify(data.proof, null, 2);

    if (currentState === "END") {
      setTimeout(() => {
        reset();
      }, 1400);
    }
  });
}
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
