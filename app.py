from flask import Flask, jsonify
import os
import requests

app = Flask(__name__)

@app.route("/")
def hello():
    return "Welcome to the Python Kubernetes web application!"

@app.route("/info")
def info():
    # Assuming the application runs inside a K8s cluster with proper RBAC
    KUBERNETES_SERVICE_HOST = os.getenv('KUBERNETES_SERVICE_HOST', 'kubernetes.default.svc')
    KUBERNETES_PORT_443_TCP_PORT = os.getenv('KUBERNETES_PORT_443_TCP_PORT', '443')
    url = f"https://{KUBERNETES_SERVICE_HOST}:{KUBERNETES_PORT_443_TCP_PORT}/api/v1/namespaces/default/pods"
    headers = {
        "Authorization": f"Bearer {open('/var/run/secrets/kubernetes.io/serviceaccount/token').read()}"
    }
    response = requests.get(url, headers=headers, verify="/var/run/secrets/kubernetes.io/serviceaccount/ca.crt")
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

