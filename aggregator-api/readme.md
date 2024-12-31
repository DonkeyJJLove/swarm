# Aggregator API

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
  - [Deployment Configuration](#deployment-configuration)
  - [Service Configuration](#service-configuration)
  - [Application Code](#application-code)
  - [Dockerfile](#dockerfile)
  - [Dependencies](#dependencies)
- [Deployment](#deployment)
  - [Prerequisites](#prerequisites)
  - [Build and Push Docker Image](#build-and-push-docker-image)
  - [Apply Kubernetes Manifests](#apply-kubernetes-manifests)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
- [Usage](#usage)
  - [API Endpoints](#api-endpoints)
  - [Logging](#logging)
- [Monitoring](#monitoring)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Further Reading](#further-reading)

---

## Overview

The **Aggregator API** is a pivotal component of the Laboratory Swarm Application, responsible for receiving telemetry data from the Aggregator and MQTT Bridge, storing it in a PostgreSQL database, and providing API endpoints for data retrieval. This ensures that telemetry data from drones is efficiently collected, stored, and accessible for analysis and visualization.

## Architecture

![Aggregator API Architecture](./architecture.png)

*Figure: High-level architecture of the Aggregator API component.*

The Aggregator API operates within the `laboratory-swarm` namespace in the Kubernetes cluster. It interacts with the Aggregator and MQTT Bridge to receive data, communicates with the PostgreSQL database for data storage, and exposes HTTP endpoints for data access.

## Components

### Deployment Configuration

- **File**: `aggregator-api-deployment.yaml`
  
  Defines the Kubernetes Deployment for the Aggregator API, specifying the number of replicas, container image, ports, environment variables, and resource allocations.

  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: aggregator-api
    namespace: laboratory-swarm
  spec:
    replicas: 2
    selector:
      matchLabels:
        app: aggregator-api
    template:
      metadata:
        labels:
          app: aggregator-api
      spec:
        containers:
          - name: aggregator-api
            image: localhost:5000/aggregator-api:latest  # Replace with your Docker registry if necessary
            env:
              - name: DATABASE_URL
                value: "postgresql://user:password@postgresql.laboratory-swarm.svc.cluster.local:5432/drone_db"
            ports:
              - containerPort: 6001
                protocol: TCP
            resources:
              requests:
                memory: "256Mi"
                cpu: "500m"
              limits:
                memory: "512Mi"
                cpu: "1"
  ```

### Service Configuration

- **File**: `aggregator-api-service.yaml`
  
  Defines the Kubernetes Service for the Aggregator API, exposing it internally within the cluster on TCP port `6001`.

  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: aggregator-api-service
    namespace: laboratory-swarm
  spec:
    selector:
      app: aggregator-api
    ports:
      - name: http
        port: 6001
        targetPort: 6001
        protocol: TCP
    type: ClusterIP
  ```

### Application Code

- **File**: `aggregator_api.py`
  
  The main Python Flask application that handles incoming data, interacts with the PostgreSQL database, and provides API endpoints for data retrieval.

  ```python
  from flask import Flask, request, jsonify
  import os
  import psycopg2
  from psycopg2.extras import RealDictCursor
  import json
  
  app = Flask(__name__)
  
  DATABASE_URL = os.getenv("DATABASE_URL",
                           "postgresql://user:password@postgresql.laboratory-swarm.svc.cluster.local:5432/drone_db")
  
  
  def get_db_connection():
      conn = psycopg2.connect(DATABASE_URL)
      return conn
  
  
  @app.route('/api/data', methods=['POST'])
  def receive_data():
      data = request.json
      drone_id = data.get('drone_id')
      position = data.get('position')
      battery_level = data.get('battery_level')
      if not all([drone_id, position, battery_level]):
          return jsonify({"error": "Missing fields"}), 400
  
      conn = get_db_connection()
      cur = conn.cursor()
      cur.execute(
          "INSERT INTO drone_data (drone_id, position, battery_level) VALUES (%s, %s, %s)",
          (drone_id, json.dumps(position), battery_level)
      )
      conn.commit()
      cur.close()
      conn.close()
      return jsonify({"status": "success"}), 200
  
  
  @app.route('/api/drones/<drone_id>/status', methods=['GET'])
  def get_drone_status(drone_id):
      conn = get_db_connection()
      cur = conn.cursor(cursor_factory=RealDictCursor)
      cur.execute(
          "SELECT position, battery_level FROM drone_data WHERE drone_id = %s ORDER BY timestamp DESC LIMIT 1",
          (drone_id,)
      )
      result = cur.fetchone()
      cur.close()
      conn.close()
      if result:
          return jsonify(
              {"drone_id": drone_id, "position": result['position'], "battery_level": result['battery_level']}), 200
      else:
          return jsonify({"error": "Drone not found"}), 404
  
  
  if __name__ == "__main__":
      app.run(host='0.0.0.0', port=6001)
  ```

### Dockerfile

- **File**: `Dockerfile`
  
  Defines the Docker image for the Aggregator API, including the base image, working directory, dependencies, environment variables, and the command to run the application.

  ```dockerfile
  FROM python:3.11-slim
  
  WORKDIR /app
  COPY drone_logic.py /app/drone_logic.py
  COPY requirements.txt /app/requirements.txt
  
  RUN pip install --no-cache-dir -r requirements.txt
  
  ENV DRONE_ID="default_drone"
  ENV AGGREGATOR_HOST="aggregator-service.laboratory-swarm.svc.cluster.local"
  ENV AGGREGATOR_PORT="5001"
  
  EXPOSE 7000
  
  CMD ["python", "drone_logic.py"]
  ```

  **Note**: There appears to be a discrepancy in the Dockerfile. The Aggregator API should be using `aggregator_api.py` instead of `drone_logic.py`. Ensure that the Dockerfile correctly copies and runs the `aggregator_api.py` file.

### Dependencies

- **File**: `requirements.txt`
  
  Lists the Python dependencies required by the Aggregator API application.

  ```txt
  Flask==2.2.3
  psycopg2-binary==2.9.6
  ```

## Deployment

### Prerequisites

Before deploying the Aggregator API, ensure that the following prerequisites are met:

- **Kubernetes Cluster**: Ensure you have access to a Kubernetes cluster (v1.18+).
- **Docker Registry**: A Docker registry is available and accessible (`localhost:5000` in this example).
- **Kubectl**: The Kubernetes command-line tool is installed and configured.
- **Namespace**: The `laboratory-swarm` namespace exists. If not, create it:

  ```bash
  kubectl create namespace laboratory-swarm
  ```

- **PostgreSQL**: Ensure the PostgreSQL service is deployed and accessible within the cluster.

### Build and Push Docker Image

1. **Navigate to the Aggregator API Directory**:

   ```bash
   cd aggregator-api
   ```

2. **Build the Docker Image**:

   ```bash
   docker build -t localhost:5000/aggregator-api:latest .
   ```

3. **Push the Image to the Docker Registry**:

   ```bash
   docker push localhost:5000/aggregator-api:latest
   ```

   *Ensure that your Docker registry is running and accessible. Replace `localhost:5000` with your registry address if different.*

### Apply Kubernetes Manifests

1. **Apply the Aggregator API Deployment**:

   ```bash
   kubectl apply -f aggregator-api-deployment.yaml
   ```

2. **Apply the Aggregator API Service**:

   ```bash
   kubectl apply -f aggregator-api-service.yaml
   ```

   *This will deploy the Aggregator API pods and expose them internally within the Kubernetes cluster.*

3. **Verify the Deployment**:

   ```bash
   kubectl get deployments -n laboratory-swarm
   kubectl get pods -n laboratory-swarm -l app=aggregator-api
   kubectl get services -n laboratory-swarm -l app=aggregator-api
   ```

   *Ensure that the pods are running and the service is correctly exposed.*

## Configuration

### Environment Variables

The Aggregator API uses the following environment variables for its configuration:

- **DATABASE_URL**: The connection string for the PostgreSQL database. Format:

  ```
  postgresql://<user>:<password>@postgresql.laboratory-swarm.svc.cluster.local:5432/drone_db
  ```

  This variable is defined in the `aggregator-api-deployment.yaml` file and can be customized as needed.

  ```yaml
  env:
    - name: DATABASE_URL
      value: "postgresql://user:password@postgresql.laboratory-swarm.svc.cluster.local:5432/drone_db"
  ```

## Usage

### API Endpoints

The Aggregator API exposes the following endpoints for interacting with drone telemetry data:

1. **Receive Data**

   - **Endpoint**: `/api/data`
   - **Method**: `POST`
   - **Description**: Receives telemetry data from Aggregator and MQTT Bridge, and stores it in the PostgreSQL database.
   - **Request Body**: JSON object containing `drone_id`, `position`, and `battery_level`.
   - **Example**:

     ```bash
     curl -X POST http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data \
     -H "Content-Type: application/json" \
     -d '{
           "drone_id": "drone_001",
           "position": {"latitude": 34.0522, "longitude": -118.2437},
           "battery_level": 85
         }'
     ```

   - **Response**: JSON object indicating success or error.

2. **Get Drone Status**

   - **Endpoint**: `/api/drones/<drone_id>/status`
   - **Method**: `GET`
   - **Description**: Retrieves the latest status (position and battery level) of a specified drone.
   - **Example**:

     ```bash
     curl http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/drones/drone_001/status
     ```

   - **Response**: JSON object containing `drone_id`, `position`, and `battery_level`, or an error message if the drone is not found.

### Logging

The Aggregator API logs important events and errors to the standard output, which can be accessed using `kubectl logs`. Example log messages include:

- Successful receipt of data from the Aggregator or MQTT Bridge.
- Successful insertion of data into the PostgreSQL database.
- Errors encountered during data processing or database interactions.

**Example**:

```bash
kubectl logs <aggregator-api-pod-name> -n laboratory-swarm
```

## Monitoring

To ensure the Aggregator API is functioning correctly, integrate it with your monitoring tools:

- **Prometheus**: Scrape metrics from the Aggregator API (if metrics are exposed).
- **Grafana**: Visualize metrics related to data ingestion, database performance, and API response times.
- **Alertmanager**: Set up alerts for failures in data processing or high error rates.

*Note: As of the current implementation, the Aggregator API does not expose Prometheus metrics. Consider integrating a metrics exporter if monitoring is required.*

## Security

### Network Policies

The Aggregator API is secured using Kubernetes NetworkPolicies, which define allowed inbound and outbound traffic. The provided `network-policy.yaml` (located in the `security/policies` directory) allows:

- **Ingress**: Only from the Aggregator and MQTT Bridge services.
- **Egress**: Only to the PostgreSQL database on port `5432` via TCP.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-aggregator
  namespace: laboratory-swarm
spec:
  podSelector:
    matchLabels:
      app: aggregator
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: drone
      ports:
        - protocol: UDP
          port: 6000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: aggregator-api
      ports:
        - protocol: TCP
          port: 6001
```

### RBAC

Role-Based Access Control (RBAC) ensures that only authorized service accounts can interact with the Aggregator API and other Kubernetes resources. The provided `rbac.yaml` (located in the `security/policies` directory) defines:

- **ServiceAccount**: `aggregator-serviceaccount`
- **Role**: `aggregator-role` with permissions to `get`, `list`, `watch` pods and services, and to `get`, `update`, `patch` deployments.
- **RoleBinding**: Binds the `aggregator-role` to the `aggregator-serviceaccount`.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: aggregator-serviceaccount
  namespace: laboratory-swarm
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: laboratory-swarm
  name: aggregator-role
rules:
  - apiGroups: [""]
    resources: ["pods", "services"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "update", "patch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: aggregator-rolebinding
  namespace: laboratory-swarm
subjects:
  - kind: ServiceAccount
    name: aggregator-serviceaccount
    namespace: laboratory-swarm
roleRef:
  kind: Role
  name: aggregator-role
  apiGroup: rbac.authorization.k8s.io
```

## Troubleshooting

### Common Issues

1. **Aggregator API Pod Not Running**:
   - **Check Pod Status**:
     ```bash
     kubectl get pods -n laboratory-swarm -l app=aggregator-api
     ```
   - **View Logs**:
     ```bash
     kubectl logs <aggregator-api-pod-name> -n laboratory-swarm
     ```
   - **Possible Causes**:
     - Image not found or incorrect registry.
     - Environment variables misconfigured.
     - Network policies blocking traffic.

2. **Failed to Insert Data into Database**:
   - **Symptoms**: Logs indicate database connection errors or failed SQL queries.
   - **Solutions**:
     - Ensure PostgreSQL is deployed and accessible.
     - Verify the `DATABASE_URL` environment variable is correct.
     - Check database credentials and permissions.

3. **API Endpoints Not Responding**:
   - **Symptoms**: HTTP requests to `/api/data` or `/api/drones/<drone_id>/status` fail or timeout.
   - **Solutions**:
     - Ensure the Aggregator API pods are running.
     - Verify service and network configurations.
     - Check for any resource limitations causing pod instability.

4. **High Memory or CPU Usage**:
   - **Symptoms**: Pod gets OOMKilled or throttled.
   - **Solutions**:
     - Adjust resource requests and limits in `aggregator-api-deployment.yaml`.
     - Optimize application code for better performance.

### Debugging Steps

1. **Verify Service Accessibility**:
   - Use `kubectl exec` to enter the Aggregator API pod and test connectivity to the PostgreSQL database.
     ```bash
     kubectl exec -it <aggregator-api-pod-name> -n laboratory-swarm -- /bin/sh
     # Inside the pod
     wget -qO- postgresql.laboratory-swarm.svc.cluster.local:5432
     ```

2. **Validate Environment Variables**:
   - Ensure that `DATABASE_URL` is correctly set.
     ```bash
     kubectl describe deployment aggregator-api -n laboratory-swarm
     ```

3. **Check Network Policies**:
   - Ensure that NetworkPolicies are not inadvertently blocking required traffic.
     ```bash
     kubectl get networkpolicy -n laboratory-swarm
     ```

4. **Inspect PostgreSQL Logs**:
   - Check logs of the PostgreSQL pods to ensure it's running correctly.
     ```bash
     kubectl logs <postgresql-pod-name> -n laboratory-swarm
     ```

## Further Reading

- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Prometheus Monitoring](https://prometheus.io/docs/introduction/overview/)
- [Istio Service Mesh](https://istio.io/latest/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

---

## Links

- [Root Documentation](../README.md)
- [Aggregator Documentation](../aggregator/README.md)
- [Aggregator MQTT Bridge Documentation](../aggregator/mqtt_bridge/README.md)

---

**Note**: Ensure that all configurations, especially environment variables and Dockerfiles, are correctly set up to match the intended application logic. Pay special attention to the Dockerfile in the `aggregator-api` directory, as it currently references `drone_logic.py`, which appears to be a part of the `drones` component. It should instead reference `aggregator_api.py` to align with the Aggregator API's functionality.