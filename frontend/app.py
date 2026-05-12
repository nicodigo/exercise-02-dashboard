"""
Exercise 02 — Streamlit Dashboard

Streamlit frontend that consumes the Node Registry REST API.
"""

import os
import streamlit as st
import requests

API_URL = os.environ.get("API_URL", "http://api:8080")

st.set_page_config(page_title="Node Registry Dashboard", layout="wide")
st.title("Node Registry Dashboard")

# ── Health indicator ──────────────────────────────────────────────
st.header("Health")
try:
    health_resp = requests.get(f"{API_URL}/health", timeout=5)
except requests.RequestException as e:
    st.error(f"Could not reach API: {e}")
    st.stop()

if health_resp.status_code == 200:
    health_data = health_resp.json()
    col1, col2, col3 = st.columns(3)
    col1.metric("Status", health_data.get("status", "?"))
    col2.metric("DB connection", health_data.get("db_connection", "?"))
    col3.metric("Active nodes", health_data.get("nodes_count", "?"))
else:
    st.error(f"Health endpoint returned status {health_resp.status_code}")

# ── Node list ────────────────────────────────────────────────────
st.header("Registered Nodes")
try:
    nodes_resp = requests.get(f"{API_URL}/api/nodes", timeout=5)
    if nodes_resp.status_code == 200:
        nodes = nodes_resp.json()
        if nodes:
            st.dataframe(nodes)
        else:
            st.info("No nodes registered yet.")
    else:
        st.error(f"Could not fetch nodes (HTTP {nodes_resp.status_code}): {nodes_resp.text}")
except requests.RequestException as e:
    st.error(f"Failed to fetch nodes: {e}")

# ── Register node form ────────────────────────────────────────────
st.header("Register a New Node")
with st.form(key="register_form"):
    name_inp = st.text_input("Name", key="reg_name")
    host_inp = st.text_input("Host", key="reg_host")
    port_inp = st.number_input("Port", min_value=1, max_value=65535, value=5432, step=1, key="reg_port")
    submitted = st.form_submit_button("Register")
    if submitted:
        if not name_inp or not host_inp:
            st.error("Name and Host are required.")
        else:
            try:
                resp = requests.post(
                    f"{API_URL}/api/nodes",
                    json={"name": name_inp, "host": host_inp, "port": int(port_inp)},
                    timeout=5,
                )
                if resp.status_code == 201:
                    st.success(f"Node '{name_inp}' registered successfully.")
                    st.rerun()
                else:
                    st.error(f"Registration failed (HTTP {resp.status_code}): {resp.text}")
            except requests.RequestException as e:
                st.error(f"Registration request failed: {e}")

# ── Delete node ──────────────────────────────────────────────────
st.header("Delete a Node")
with st.form(key="delete_form"):
    del_name = st.text_input("Node name to delete", key="del_name")
    submitted_del = st.form_submit_button("Delete")
    if submitted_del:
        if not del_name:
            st.error("Please enter a node name.")
        else:
            try:
                resp = requests.delete(f"{API_URL}/api/nodes/{del_name}", timeout=5)
                if resp.status_code == 204:
                    st.success(f"Node '{del_name}' deleted successfully.")
                    st.rerun()
                else:
                    st.error(f"Deletion failed (HTTP {resp.status_code}): {resp.text}")
            except requests.RequestException as e:
                st.error(f"Deletion request failed: {e}")
