import os
import requests
from flask import Flask, render_template_string, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
colors = ["#FFC0CB", "#FFD700", "#7FFFD4", "#00FFFF", "#8A2BE2", "#A52A2A"]

def get_cluster_info():
    KUBERNETES_SERVICE_HOST = os.getenv('KUBERNETES_SERVICE_HOST', 'kubernetes.default.svc')
    KUBERNETES_PORT_443_TCP_PORT = os.getenv('KUBERNETES_PORT_443_TCP_PORT', '443')
    
    base_url = f"https://{KUBERNETES_SERVICE_HOST}:{KUBERNETES_PORT_443_TCP_PORT}/api/v1"
    resources = {
        'pods': f"{base_url}/namespaces/default/pods",
        'nodes': f"{base_url}/nodes",
        'deployments': f"{base_url}/apis/apps/v1/namespaces/default/deployments"
    }

    headers = {}
    try:
        with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as token_file:
            token = token_file.read().strip()
        headers = {"Authorization": f"Bearer {token}"}
    except IOError as e:
        app.logger.error("Failed to read token file: %s", e)
        return {"error": "Failed to read token file"}

    results = {}
    for key, url in resources.items():
        try:
            response = requests.get(url, headers=headers, verify="/var/run/secrets/kubernetes.io/serviceaccount/ca.crt")
            if response.status_code == 200:
                results[key] = response.json()
            else:
                app.logger.error(f'API Request for {key} failed with status code: {response.status_code}')
                results[key] = {"error": f"API request for {key} failed with unexpected status code"}
        except requests.exceptions.RequestException as e:
            app.logger.error(f"API request for {key} failed: {e}")
            results[key] = {"error": f"API request for {key} failed"}

    return results

@app.route("/")
def hello():
    # Existing color rotation logic
    color_index = session.get('color_index', 0)
    color = colors[color_index]
    color_index = (color_index + 1) % len(colors)
    session['color_index'] = color_index

    # Fetch cluster information
    cluster_info = get_cluster_info()

    # Format HTML response
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Python Kubernetes Web Application</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                line-height: 1.6;
            }}
            .container {{
                max-width: 800px;
                margin: auto;
                padding: 20px;
                background-color: #f4f4f4;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
            }}
        </style>
    </head>
    <body style="background-color: {color};">
        <div class="container">
            <h1>Welcome to the Python Kubernetes Web Application - APT Test Phase V7</h1>
            <p>In this phase, my primary goal is to display Kubernetes cluster information directly within this application interface. I am utilizing Kubernetes' Role-Based Access Control (RBAC) to meticulously configure the necessary permissions. This ensures secure API access to the various Kubernetes resources, including deployed pods, nodes, and deployments.</p>
            <p>To achieve this, I leverage a dedicated service account, which is bound to specific roles through role-bindings. These roles precisely define the permissible actions that the application can perform on the Kubernetes API, ensuring both security and functionality.</p>
            <p>Stay tuned as I enhance the application's capabilities and integrate more comprehensive cluster insights!</p>
            <h2>Pod Information:</h2>
            <ul>
                {format_info(cluster_info.get('pods', []), 'pods')}
            </ul>
            <h2>Node Information:</h2>
            <ul>
                {format_info(cluster_info.get('nodes', []), 'nodes')}
            </ul>
            <h2>Deployment Information:</h2>
            <ul>
                {format_info(cluster_info.get('deployments', []), 'deployments')}
            </ul>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

def format_info(data, resource_type):
    if 'error' in data:
        return f"<li>Error: {data['error']}</li>"

    items = data.get('items', [])
    if resource_type == 'pods':
        return ''.join(f"<li>{item['metadata']['name']} - {item['status'].get('phase', 'Unknown')}</li>" for item in items)
    elif resource_type == 'nodes':
        return ''.join(f"<li>{item['metadata']['name']} - {item['status']['conditions'][-1]['type']}</li>" for item in items)
    elif resource_type == 'deployments':
        return ''.join(f"<li>{item['metadata']['name']} - {item['spec']['replicas']} replicas</li>" for item in items)

    return "<li>No data available</li>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

