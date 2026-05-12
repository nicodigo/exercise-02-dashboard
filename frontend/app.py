"""
Exercise 02 — Flask Dashboard

Flask frontend that consumes the Node Registry REST API.
"""

import os
from flask import Flask, request, redirect, render_template_string

import requests

app = Flask(__name__)

API_URL = os.environ.get("API_URL", "http://api:8080")

HTML_TEMPLATE = """
<!doctype html>
<html>
<head><title>Node Registry Dashboard</title></head>
<body>
<h1>Node Registry Dashboard</h1>

<h2>Health</h2>
<p>Status: {{ status }}</p>
<p>DB connection: {{ db_connection }}</p>
<p>Active nodes: {{ nodes_count }}</p>

<h2>Nodes</h2>
<table border="1">
<tr><th>Name</th><th>Host</th><th>Port</th><th>Status</th><th>Created At</th><th>Updated At</th></tr>
{% for node in nodes %}
<tr>
<td>{{ node.name }}</td>
<td>{{ node.host }}</td>
<td>{{ node.port }}</td>
<td>{{ node.status }}</td>
<td>{{ node.created_at }}</td>
<td>{{ node.updated_at }}</td>
</tr>
{% endfor %}
</table>

<h2>Register a New Node</h2>
<form method="post" action="/">
<label>Name: <input type="text" name="name" required></label><br>
<label>Host: <input type="text" name="host" required></label><br>
<label>Port: <input type="number" name="port" min="1" max="65535" value="5432" required></label><br>
<input type="submit" value="Register">
</form>

<h2>Delete a Node</h2>
<form method="post" action="/delete">
<label>Node name: <input type="text" name="name" required></label><br>
<input type="submit" value="Delete">
</form>

{% if message %}
<p>{{ message }}</p>
{% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    if request.method == "POST":
        name = request.form.get("name")
        host = request.form.get("host")
        port = request.form.get("port")
        if not name or not host:
            message = "Name and Host are required."
        else:
            try:
                resp = requests.post(
                    f"{API_URL}/api/nodes",
                    json={"name": name, "host": host, "port": int(port)},
                    timeout=5,
                )
                if resp.status_code == 201:
                    return redirect("/")
                else:
                    message = f"Registration failed (HTTP {resp.status_code}): {resp.text}"
            except requests.RequestException as e:
                message = f"Registration request failed: {e}"
    # Fetch health and nodes
    try:
        health_resp = requests.get(f"{API_URL}/health", timeout=5)
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            status = health_data.get("status", "?")
            db_connection = health_data.get("db_connection", "?")
            nodes_count = health_data.get("nodes_count", "?")
        else:
            status = f"Error {health_resp.status_code}"
            db_connection = "?"
            nodes_count = "?"
    except requests.RequestException as e:
        status = f"Error: {e}"
        db_connection = "?"
        nodes_count = "?"

    try:
        nodes_resp = requests.get(f"{API_URL}/api/nodes", timeout=5)
        if nodes_resp.status_code == 200:
            nodes = nodes_resp.json()
        else:
            nodes = []
    except requests.RequestException:
        nodes = []

    return render_template_string(
        HTML_TEMPLATE,
        status=status,
        db_connection=db_connection,
        nodes_count=nodes_count,
        nodes=nodes,
        message=message,
    )

@app.route("/delete", methods=["POST"])
def delete():
    name = request.form.get("name")
    if not name:
        return redirect("/")
    try:
        resp = requests.delete(f"{API_URL}/api/nodes/{name}", timeout=5)
        if resp.status_code == 204:
            pass  # success
        else:
            # could show error but redirect anyway
            pass
    except requests.RequestException:
        pass
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501)
