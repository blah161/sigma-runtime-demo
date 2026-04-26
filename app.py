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
</head>
<body>
  <h2>Verified Flow Engine (λΣ^R)</h2>
  <p><b>Current State:</b> <span id="state">Q1</span></p>

  <button onclick="send('Yes')">Yes</button>
  <button onclick="send('No')">No</button>
  <button onclick="send('Text')">Text</button>

  <pre id="output"></pre>

<script>
let currentState = "Q1";

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
    currentState = "Q1";
    document.getElementById("state").innerText = "Q1";
    document.getElementById("output").innerText = "Reset to Q1";
  }, 1200);
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
