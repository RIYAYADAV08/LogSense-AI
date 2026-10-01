import os
import subprocess

from flask import Flask, jsonify, render_template, request, send_from_directory

from analyzer import detect_anomalies

app = Flask(__name__, static_folder="frontend/dist/assets", static_url_path="/assets")
DIST = os.path.join(os.path.dirname(__file__), "frontend", "dist")
LAST_RESULT = {}


@app.route("/")
def index():
    # Serve the built React dashboard; fall back to the plain HTML page if it isn't built.
    if os.path.exists(os.path.join(DIST, "index.html")):
        return send_from_directory(DIST, "index.html")
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    global LAST_RESULT
    file = request.files.get("logfile")
    text = file.read().decode("utf-8", errors="ignore") if file else request.get_data(as_text=True)
    LAST_RESULT = detect_anomalies(text)
    return jsonify(LAST_RESULT)


@app.route("/api/remediate", methods=["POST"])
def remediate():
    """Run the Ansible playbook for a service. Dry-run unless REMEDIATE=1."""
    service = (request.get_json(silent=True) or {}).get("service", "")
    if service not in {"nginx", "mysql", "sshd", "app"}:  # allow-list: never pass raw input to a shell
        return jsonify(error="Unknown service"), 400
    cmd = ["ansible-playbook", "ansible/remediate.yml", "-e", f"service_name={service}"]
    if os.environ.get("REMEDIATE") != "1":
        cmd.append("--check")
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return jsonify(command=" ".join(cmd), returncode=out.returncode, output=out.stdout[-2000:])
    except FileNotFoundError:
        return jsonify(command=" ".join(cmd), error="ansible-playbook is not installed"), 501


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
