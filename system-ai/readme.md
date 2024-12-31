# AI Service Documentation

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
  - [AI Service Deployment](#ai-service-deployment)
  - [AI Service Kubernetes Service](#ai-service-kubernetes-service)
  - [AI Service Python Application](#ai-service-python-application)
  - [Dockerfile](#dockerfile)
- [Deployment](#deployment)
  - [Prerequisites](#prerequisites)
  - [Deploying the AI Service](#deploying-the-ai-service)
    - [Using Kubernetes Manifests](#using-kubernetes-manifests)
    - [Building and Pushing the Docker Image](#building-and-pushing-the-docker-image)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Model Management](#model-management)
- [Security](#security)
  - [Securing the AI Service](#securing-the-ai-service)
  - [Managing Secrets](#managing-secrets)
- [Monitoring](#monitoring)
  - [Metrics Collection](#metrics-collection)
  - [Logging](#logging)
- [Testing](#testing)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Debugging Steps](#debugging-steps)
- [Further Reading](#further-reading)
- [Links](#links)

---

## Overview

The **AI Service** within the Laboratory Swarm Application is responsible for making predictions based on drone telemetry data. It exposes a RESTful API endpoint that accepts telemetry data, processes it using a pre-trained machine learning model, and returns predictions. This service is containerized using Docker and deployed on a Kubernetes cluster, ensuring scalability, reliability, and ease of management.

## Architecture

![AI Service Architecture](./architecture.png)

*Figure: High-level architecture of the AI Service component.*

The AI Service interacts with other components such as the API Service and the Data Processing Service to provide real-time predictions. It leverages Kubernetes for deployment and scalability, Istio for secure service communication, and integrates with monitoring tools to ensure optimal performance and reliability.

## Components

### AI Service Deployment

The AI Service is deployed as a Kubernetes Deployment, ensuring that the service is highly available and can scale as needed. Below is the YAML configuration for deploying the AI Service.

**File: `system-ai/ai-service-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-service
  labels:
    app: ai-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ai-service
  template:
    metadata:
      labels:
        app: ai-service
    spec:
      containers:
        - name: ai-service
          image: localhost:5000/ai-service:latest
          ports:
            - containerPort: 9000
          env:
            - name: MODEL_PATH
              value: "/app/model.joblib"
```

**Key Parameters:**

- `replicas`: Number of AI Service instances. Initially set to `1` but can be scaled based on demand.
- `selector`: Matches pods with the label `app: ai-service`.
- `containers`: Defines the container specifications.
  - `image`: Docker image for the AI Service. Replace `localhost:5000/ai-service:latest` with your container registry path.
  - `ports`: Exposes port `9000` for the Flask application.
  - `env`: Sets environment variables, such as the path to the machine learning model.

### AI Service Kubernetes Service

A Kubernetes Service exposes the AI Service Deployment, enabling other services within the cluster to communicate with it.

**File: `system-ai/ai-service-service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-service
spec:
  selector:
    app: ai-service
  ports:
    - port: 9000
      targetPort: 9000
      protocol: TCP
      name: http
  type: ClusterIP
```

**Key Parameters:**

- `selector`: Routes traffic to pods labeled `app: ai-service`.
- `ports`: Defines the port mapping.
  - `port`: The port exposed within the cluster.
  - `targetPort`: The port on which the AI Service container is listening.
- `type`: `ClusterIP` ensures the service is only accessible within the Kubernetes cluster.

### AI Service Python Application

The AI Service is built using Python's Flask framework. It loads a pre-trained machine learning model and exposes an API endpoint for making predictions.

**File: `system-ai/ai_service.py`**

```python
from flask import Flask, request, jsonify
import joblib
import os

app = Flask(__name__)
model = joblib.load(os.getenv("MODEL_PATH", "/app/model.joblib"))

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    try:
        X = [data['x'], data['y'], data['battery'], data['speed']]
        prediction = model.predict([X])
        return jsonify({'prediction': prediction[0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9000)
```

**Key Features:**

- **Endpoint**: `/predict` accepts POST requests with JSON payload containing telemetry data.
- **Model Loading**: Loads a machine learning model from the specified `MODEL_PATH`.
- **Prediction Logic**: Extracts features (`x`, `y`, `battery`, `speed`) from the request and returns the prediction result.
- **Error Handling**: Returns appropriate error messages for invalid inputs or processing errors.

### Dockerfile

The Dockerfile defines the containerization process for the AI Service, ensuring that all dependencies are installed and the application is correctly configured.

**File: `system-ai/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY model.joblib /app/model.joblib
COPY ai_service.py /app/ai_service.py
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV MODEL_PATH=/app/model.joblib

CMD ["python", "ai_service.py"]
```

**Key Steps:**

1. **Base Image**: Uses a slim version of Python 3.11 for a lightweight container.
2. **Working Directory**: Sets `/app` as the working directory.
3. **Copy Files**: Copies the machine learning model, application code, and requirements into the container.
4. **Install Dependencies**: Installs Python dependencies specified in `requirements.txt`.
5. **Environment Variable**: Sets `MODEL_PATH` to point to the model file.
6. **Command**: Starts the Flask application.

**Example `requirements.txt`:**

Ensure you have a `requirements.txt` file with the necessary dependencies.

```txt
flask
joblib
scikit-learn
```

## Deployment

### Prerequisites

Before deploying the AI Service, ensure the following prerequisites are met:

- **Kubernetes Cluster**: A functional Kubernetes cluster (v1.18+).
- **Kubectl**: The Kubernetes command-line tool is installed and configured.
- **Container Registry**: Access to a container registry (e.g., Docker Hub, Google Container Registry) to store and pull the AI Service Docker image.
- **Namespace**: Create a dedicated namespace for the AI Service to isolate it from other components.

```bash
kubectl create namespace system-ai
```

- **Model File**: Ensure that the `model.joblib` file is available and correctly placed in the `/app` directory during the Docker build process.

### Deploying the AI Service

You can deploy the AI Service using **Kubernetes Manifests** or **Helm Charts**. Below are the steps for both methods.

#### Using Kubernetes Manifests

1. **Navigate to the AI Service Configuration Directory:**

   ```bash
   cd infrastructure/system-ai
   ```

2. **Apply the Deployment Manifest:**

   ```bash
   kubectl apply -f ai-service-deployment.yaml -n system-ai
   ```

3. **Apply the Service Manifest:**

   ```bash
   kubectl apply -f ai-service-service.yaml -n system-ai
   ```

4. **Verify the Deployment:**

   ```bash
   kubectl get deployments -n system-ai
   kubectl get pods -n system-ai
   kubectl get services -n system-ai
   ```

   Ensure that the AI Service pod is running and the service is correctly configured.

#### Using Helm

*(Optional)* If you prefer using Helm for deployment, you can create a custom Helm chart for the AI Service.

1. **Create a Helm Chart:**

   ```bash
   helm create ai-service
   ```

2. **Customize the Helm Chart:**

   Update the `values.yaml` file with the AI Service configurations, such as image repository, tag, environment variables, and replica count.

3. **Install the AI Service Using Helm:**

   ```bash
   helm install ai-service ./ai-service -n system-ai
   ```

4. **Verify the Deployment:**

   ```bash
   kubectl get deployments -n system-ai
   kubectl get pods -n system-ai
   kubectl get services -n system-ai
   ```

## Configuration

### Environment Variables

Environment variables allow you to configure the AI Service without modifying the codebase. Key environment variables include:

- **MODEL_PATH**: Specifies the path to the machine learning model file.

**Example Configuration in Deployment:**

```yaml
env:
  - name: MODEL_PATH
    value: "/app/model.joblib"
```

### Model Management

- **Updating the Model**: To update the machine learning model, replace the `model.joblib` file and rebuild the Docker image.
- **Model Storage**: Store models in a secure location and manage access using Kubernetes Secrets if necessary.

## Security

### Securing the AI Service

- **Authentication and Authorization**: Integrate with Istio's security features to enforce mutual TLS and role-based access controls.
- **Input Validation**: Ensure that all incoming data is validated to prevent injection attacks and ensure data integrity.
- **TLS Encryption**: Use TLS to encrypt communications between services.

### Managing Secrets

- **Kubernetes Secrets**: Store sensitive information, such as database credentials and API keys, using Kubernetes Secrets.
  
  **Creating a Secret for the AI Service:**

  ```bash
  kubectl create secret generic ai-service-secret \
    --from-literal=MODEL_PATH="/app/model.joblib" \
    -n system-ai
  ```

- **Accessing Secrets in Pods:**

  ```yaml
  env:
    - name: MODEL_PATH
      valueFrom:
        secretKeyRef:
          name: ai-service-secret
          key: MODEL_PATH
  ```

## Monitoring

### Metrics Collection

Monitoring the AI Service ensures that it operates efficiently and helps in identifying issues proactively.

- **Prometheus**: Scrapes metrics from the AI Service.
  
  **Example Prometheus Scrape Configuration:**

  ```yaml
  scrape_configs:
    - job_name: 'ai-service'
      static_configs:
        - targets: ['ai-service.system-ai.svc.cluster.local:9000']
  ```

- **Exporting Custom Metrics**: Integrate Prometheus client libraries to expose custom metrics from the AI Service.

### Logging

Centralized logging helps in troubleshooting and auditing.

- **Fluentd**: Collects logs from the AI Service pods and forwards them to a centralized logging system like Elasticsearch or Loki.
  
  **Example Fluentd Configuration:**

  ```yaml
  apiVersion: apps/v1
  kind: DaemonSet
  metadata:
    name: fluentd
    namespace: logging
  spec:
    selector:
      matchLabels:
        app: fluentd
    template:
      metadata:
        labels:
          app: fluentd
      spec:
        containers:
          - name: fluentd
            image: fluent/fluentd:v1.12-debian-1
            volumeMounts:
              - name: varlog
                mountPath: /var/log
              - name: config
                mountPath: /fluentd/etc
        volumes:
          - name: varlog
            hostPath:
              path: /var/log
          - name: config
            configMap:
              name: fluentd-config
  ```

## Testing

### Unit Tests

Ensure that individual components of the AI Service function correctly.

- **Tools**: Use Python's `unittest` or `pytest` frameworks.
- **Example Test Case:**

  ```python
  import unittest
  from ai_service import app

  class TestAIService(unittest.TestCase):
      def setUp(self):
          self.app = app.test_client()
          self.app.testing = True

      def test_predict_success(self):
          response = self.app.post('/predict', json={
              'x': 1.0,
              'y': 2.0,
              'battery': 80,
              'speed': 5
          })
          self.assertEqual(response.status_code, 200)
          self.assertIn('prediction', response.json)

      def test_predict_failure(self):
          response = self.app.post('/predict', json={
              'x': 1.0,
              'battery': 80,
              'speed': 5
          })
          self.assertEqual(response.status_code, 400)
          self.assertIn('error', response.json)

  if __name__ == '__main__':
      unittest.main()
  ```

### Integration Tests

Test the interactions between the AI Service and other components like the API Service and PostgreSQL.

- **Tools**: Use tools like `pytest` with fixtures that spin up necessary services.
- **Example Integration Test:**

  ```python
  import requests

  def test_ai_service_integration():
      url = 'http://ai-service.system-ai.svc.cluster.local:9000/predict'
      payload = {
          'x': 1.0,
          'y': 2.0,
          'battery': 80,
          'speed': 5
      }
      response = requests.post(url, json=payload)
      assert response.status_code == 200
      assert 'prediction' in response.json()
  ```

### End-to-End Tests

Validate the entire workflow from data ingestion to prediction.

- **Tools**: Use frameworks like `Selenium` for UI interactions or `Postman` for API workflows.
- **Example Scenario**:
  1. Send telemetry data through the API Service.
  2. Ensure the AI Service processes the data and returns a prediction.
  3. Verify that the prediction is stored or utilized as expected.

## Troubleshooting

### Common Issues

1. **Service Unavailability**
   - **Symptoms**: AI Service endpoint returns `503` errors or is unreachable.
   - **Solutions**:
     - Check the status of AI Service pods.
       ```bash
       kubectl get pods -n system-ai
       ```
     - Inspect pod logs for errors.
       ```bash
       kubectl logs <ai-service-pod-name> -n system-ai
       ```
     - Verify service configurations and ensure the correct port is exposed.

2. **Model Loading Failures**
   - **Symptoms**: AI Service fails to start or returns errors related to model loading.
   - **Solutions**:
     - Ensure that the `model.joblib` file is correctly copied into the container.
     - Verify the `MODEL_PATH` environment variable is correctly set.
     - Check file permissions and paths within the container.

3. **Prediction Errors**
   - **Symptoms**: AI Service returns errors when processing prediction requests.
   - **Solutions**:
     - Validate the input payload structure.
     - Ensure the machine learning model is compatible with the input data.
     - Inspect application logs for detailed error messages.

4. **High Resource Consumption**
   - **Symptoms**: AI Service pods consume excessive CPU or memory, leading to performance degradation.
   - **Solutions**:
     - Review and adjust resource requests and limits in the deployment manifest.
     - Optimize the machine learning model for efficiency.
     - Implement Horizontal Pod Autoscaling if necessary.

### Debugging Steps

1. **Inspect Pod Status and Logs**
   - Check if AI Service pods are running without issues.
     ```bash
     kubectl get pods -n system-ai
     ```
   - View logs for the AI Service pod.
     ```bash
     kubectl logs <ai-service-pod-name> -n system-ai
     ```

2. **Verify Deployment and Service Configuration**
   - Retrieve and review the deployment YAML.
     ```bash
     kubectl get deployment ai-service -n system-ai -o yaml
     ```
   - Retrieve and review the service YAML.
     ```bash
     kubectl get service ai-service -n system-ai -o yaml
     ```

3. **Test Connectivity**
   - Use port-forwarding to access the AI Service locally for testing.
     ```bash
     kubectl port-forward service/ai-service 9000:9000 -n system-ai
     ```
   - Send a test prediction request.
     ```bash
     curl -X POST http://localhost:9000/predict -H "Content-Type: application/json" -d '{"x":1.0,"y":2.0,"battery":80,"speed":5}'
     ```

4. **Check Network Policies and RBAC**
   - Ensure that Network Policies are not blocking traffic to the AI Service.
     ```bash
     kubectl get networkpolicy -n system-ai
     ```
   - Verify RBAC permissions for the AI Service.
     ```bash
     kubectl describe rolebinding <rolebinding-name> -n system-ai
     ```

5. **Use Istio Diagnostics**
   - Analyze Istio configurations to identify potential issues.
     ```bash
     istioctl analyze
     ```

## Further Reading

- [Flask Documentation](https://flask.palletsprojects.com/en/2.0.x/)
- [Joblib Documentation](https://joblib.readthedocs.io/en/latest/)
- [Kubernetes Deployment Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes Service Documentation](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Docker Documentation](https://docs.docker.com/)
- [Prometheus Monitoring](https://prometheus.io/docs/introduction/overview/)
- [Istio Service Mesh](https://istio.io/latest/docs/)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Secure Kubernetes Networking](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [RBAC in Kubernetes](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

## Links

- [Root Documentation](../../README.md)
- [Infrastructure Documentation](../README.md)
- [Security Documentation](../security/README.md)
- [Kubernetes Monitoring Tools Documentation](../kubernetes/README.md)
- [Istio Configuration Documentation](../istio/README.md)
- [Policies Documentation](../security/policies/README.md)
- [Virtual Services Documentation](../istio/virtualservices/README.md)
- [StatefulSets Documentation](../statefulset/README.md)
- [API Service Documentation](../server/api-service/README.md)
- [Authentication Service Documentation](../server/auth-service/README.md)
- [Data Processing Service Documentation](../server/data-processing-service/README.md)
- [Prometheus Documentation](https://prometheus.io/docs/introduction/overview/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Kubernetes RBAC Documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Kubernetes Network Policies Documentation](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

---

**AI-Powered Predictions! 🤖**

---

If you encounter any issues or have questions regarding the AI Service component, please refer to the [Troubleshooting](#troubleshooting) section or reach out to the project maintainers.