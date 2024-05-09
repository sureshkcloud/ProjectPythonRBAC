from flask import Flask, render_template
import os
import requests

app = Flask(__name__)

@app.route('/')
def home():
    # Retrieving environment variables and Kubernetes API information if needed
    node_name = os.getenv('NODE_NAME', 'Unknown Node')
    pod_name = os.getenv('POD_NAME', 'Unknown Pod')
    
    # Assembling Kubernetes cluster information
    try:
        resp = requests.get('https://kubernetes.default.svc.cluster.local/api/v1/namespaces/default/pods', 
                            headers={'Authorization': f'Bearer {os.getenv("KUBERNETES_TOKEN")}'}, 
                            verify='/var/run/secrets/kubernetes.io/serviceaccount/ca.crt')
        pod_info = resp.json()
    except Exception as e:
        pod_info = {"error": str(e)}

    # The URL of the image to be displayed
    image_url = "https://static.wixstatic.com/media/7906c6_b278bf68dd524ee7974e32d61142a986~mv2.jpg/v1/fill/w_454,h_224,al_c,q_80,usm_0.66_1.00_0.01,enc_auto/namo%20tech%20logo_edited.jpg"

    # Data passed to the HTML template
    context = {
        "node_name": node_name,
        "pod_name": pod_name,
        "pod_info": pod_info,
        "image_url": image_url,
        "footer": "This application is open source and freely usable for all.",
        "creator_tag": "created by #sureshkcloud"
    }

    return render_template('index.html', **context)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

