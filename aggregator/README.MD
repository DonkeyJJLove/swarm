# Aggregator

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
  - [Functionality](#functionality)
  - [Logging](#logging)
- [Monitoring](#monitoring)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Further Reading](#further-reading)

---

## Overview

The **Aggregator** is a critical component of the Laboratory Swarm Application, responsible for collecting telemetry data from drones using the UDP protocol. It processes incoming data and forwards it to the Aggregator API for storage and further analysis. This ensures real-time data aggregation and seamless integration with other system components.

## Architecture

![Aggregator Architecture](./architecture.png)

*Figure: High-level architecture of the Aggregator component.*

The Aggregator operates within the `laboratory-swarm` namespace in the Kubernetes cluster and interacts with drones sending UDP packets on port `6000`. Upon receiving data, it processes and forwards it to the Aggregator API via HTTP POST requests.

## Components

### Deployment Configuration

- **File**: `aggregator-deployment.yaml`
  
  Defines the Kubernetes Deployment for the Aggregator, specifying the number of replicas, container image, ports, environment variables, and resource allocations.

  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: aggregator
    namespace: laboratory-swarm
  spec:
    replicas: 1
    selector:
      matchLabels:
        app: aggregator
    template:
      metadata:
        labels:
          app: aggregator
      spec:
        containers:
          - name: aggregator
            image: localhost:5000/aggregator:latest  # Replace with your Docker registry if necessary
            ports:
              - containerPort: 6000
                protocol: UDP
            env:
              - name: AGGREGATOR_PORT
                value: "6000"
              - name: AGGREGATOR_API_URL
                value: "http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data"
            resources:
              requests:
                memory: "128Mi"
                cpu: "250m"
              limits:
                memory: "256Mi"
                cpu: "500m"
  ```

### Service Configuration

- **File**: `aggregator-service.yaml`
  
  Defines the Kubernetes Service for the Aggregator, exposing it internally within the cluster on UDP port `6000`.

  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: aggregator-service
    namespace: laboratory-swarm
  spec:
    selector:
      app: aggregator
    ports:
      - name: aggregator-udp
        port: 6000
        targetPort: 6000
        protocol: UDP
    type: ClusterIP
  ```

### Application Code

- **File**: `aggregator.py`
  
  The main Python application that listens for UDP packets, processes incoming data, and forwards it to the Aggregator API.

  ```python
  import socket
  import threading
  import os
  import json
  import requests
  
  # Read environment variables with default values
  AGGREGATOR_PORT = int(os.getenv("AGGREGATOR_PORT", "6000"))
  AGGREGATOR_API_URL = os.getenv("AGGREGATOR_API_URL",
                                 "http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data")
  
  
  def handle_message(data, addr):
      """
      Handle each received UDP message in a separate thread.
  
      :param data: Raw data from the socket
      :param addr: Tuple (ip, port) of the sender
      """
      try:
          # Decode message with 'replace' to handle errors
          message = data.decode(errors='replace')
          print(f"[aggregator] Received from {addr}: {message}")
  
          # Forward data to Aggregator API
          data_json = json.loads(message)
          response = requests.post(AGGREGATOR_API_URL, json=data_json)
          if response.status_code == 200:
              print("[aggregator] Data successfully sent to Aggregator API.")
          else:
              print(f"[aggregator] Failed to send data to Aggregator API: {response.status_code}")
      except Exception as e:
          print(f"[aggregator] Error processing message: {e}")
  
  
  def run_aggregator():
      """
      Main listening loop. Creates a UDP socket and listens for messages on AGGREGATOR_PORT.
      Each received message is handled in a separate thread to prevent blocking.
      """
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      sock.bind(("", AGGREGATOR_PORT))
      print(f"[aggregator] Listening on port {AGGREGATOR_PORT} (UDP)")
  
      while True:
          data, addr = sock.recvfrom(1024)
          # Handle each packet in a separate thread
          threading.Thread(
              target=handle_message,
              args=(data, addr),
              daemon=True
          ).start()
  
  
  if __name__ == "__main__":
      run_aggregator()
  ```

### Dockerfile

- **File**: `Dockerfile`
  
  Defines the Docker image for the Aggregator, including the base image, working directory, dependencies, environment variables, and the command to run the application.

  ```dockerfile
  # ----------------------------------------------------------------------------
  # Base Image: python:3.11-slim
  # Maintainer: d2j3
  # Version: 1.0
  # Description: Docker image for the UDP data aggregator (aggregator.py)
  # Application: data-aggregator
  # ----------------------------------------------------------------------------
  
  # Use official lightweight Python image
  FROM python:3.11-slim
  
  # Metadata
  LABEL org.opencontainers.image.title="Data Aggregator"
  LABEL org.opencontainers.image.description="A lightweight UDP data aggregator application."
  LABEL org.opencontainers.image.version="1.0"
  LABEL org.opencontainers.image.authors="d2j3"
  LABEL org.opencontainers.image.licenses="MIT"
  
  # Set working directory
  WORKDIR /app
  
  # Copy dependencies and install
  COPY requirements.txt ./
  RUN pip install --no-cache-dir -r requirements.txt
  
  # Copy application code
  COPY aggregator.py /app/aggregator.py
  
  # Set environment variables
  ENV AGGREGATOR_PORT=6000
  ENV AGGREGATOR_API_URL=http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data
  
  # Expose UDP port
  EXPOSE 6000/udp
  
  # Command to run the application
  CMD ["python", "aggregator.py"]
  ```

### Dependencies

- **File**: `requirements.txt`
  
  Lists the Python dependencies required by the Aggregator application. Currently, no dependencies are specified but can be uncommented or added as needed.

  ```txt
  # Example Python dependencies, uncomment or add as needed
  
  # requests==2.28.2
  # psycopg2==2.9.6
  # pymongo==4.3.3
  # redis==4.5.5
  ```

## Deployment

### Prerequisites

Before deploying the Aggregator, ensure that the following prerequisites are met:

- **Kubernetes Cluster**: Ensure you have access to a Kubernetes cluster (v1.18+).
- **Docker Registry**: A Docker registry is available and accessible (`localhost:5000` in this example).
- **Kubectl**: The Kubernetes command-line tool is installed and configured.
- **Namespace**: The `laboratory-swarm` namespace exists. If not, create it:

  ```bash
  kubectl create namespace laboratory-swarm
  ```

### Build and Push Docker Image

1. **Navigate to the Aggregator Directory**:

   ```bash
   cd aggregator
   ```

2. **Build the Docker Image**:

   ```bash
   docker build -t localhost:5000/aggregator:latest .
   ```

3. **Push the Image to the Docker Registry**:

   ```bash
   docker push localhost:5000/aggregator:latest
   ```

   *Ensure that your Docker registry is running and accessible. Replace `localhost:5000` with your registry address if different.*

### Apply Kubernetes Manifests

1. **Apply the Aggregator Deployment**:

   ```bash
   kubectl apply -f aggregator-deployment.yaml
   ```

2. **Apply the Aggregator Service**:

   ```bash
   kubectl apply -f aggregator-service.yaml
   ```

   *This will deploy the Aggregator pod and expose it internally within the Kubernetes cluster.*

3. **Verify the Deployment**:

   ```bash
   kubectl get deployments -n laboratory-swarm
   kubectl get pods -n laboratory-swarm -l app=aggregator
   kubectl get services -n laboratory-swarm -l app=aggregator
   ```

   *Ensure that the pod is running and the service is correctly exposed.*

## Configuration

### Environment Variables

The Aggregator uses the following environment variables for its configuration:

- **AGGREGATOR_PORT**: The UDP port on which the Aggregator listens for incoming data. Default is `6000`.

- **AGGREGATOR_API_URL**: The endpoint URL of the Aggregator API where processed data is forwarded. Default is `http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data`.

These variables are defined in the `aggregator-deployment.yaml` file and can be customized as needed.

```yaml
env:
  - name: AGGREGATOR_PORT
    value: "6000"
  - name: AGGREGATOR_API_URL
    value: "http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data"
```

## Usage

### Functionality

The Aggregator performs the following functions:

1. **Listening for UDP Messages**: It listens on the specified UDP port (`6000` by default) for incoming telemetry data from drones.

2. **Processing Incoming Data**: Each received UDP packet is decoded and parsed as JSON. The Aggregator ensures that the data contains the necessary fields before forwarding.

3. **Forwarding Data to Aggregator API**: Validated data is sent to the Aggregator API via an HTTP POST request for storage and further processing.

### Logging

The Aggregator logs important events and errors to the standard output, which can be accessed using `kubectl logs`. Example log messages include:

- Successful receipt of data from a drone.
- Successful forwarding of data to the Aggregator API.
- Errors encountered during message processing or data forwarding.

**Example**:

```bash
kubectl logs <aggregator-pod-name> -n laboratory-swarm
```

## Monitoring

To ensure the Aggregator is functioning correctly, integrate it with your monitoring tools:

- **Prometheus**: Scrape metrics from the Aggregator (if metrics are exposed).
- **Grafana**: Visualize metrics related to data ingestion and forwarding.
- **Alertmanager**: Set up alerts for failures in data forwarding or high error rates.

*Note: As of the current implementation, the Aggregator does not expose Prometheus metrics. Consider integrating a metrics exporter if monitoring is required.*

## Security

### Network Policies

The Aggregator is secured using Kubernetes NetworkPolicies, which define allowed inbound and outbound traffic. The provided `network-policy.yaml` allows:

- **Ingress**: Only pods labeled `app=drone` can send UDP traffic on port `6000`.
- **Egress**: Only to pods labeled `app=aggregator-api` on port `6001` via TCP.

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

Role-Based Access Control (RBAC) ensures that only authorized service accounts can interact with the Aggregator and other Kubernetes resources. The provided `rbac.yaml` defines:

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

1. **Aggregator Pod Not Running**:
   - **Check Pod Status**:
     ```bash
     kubectl get pods -n laboratory-swarm -l app=aggregator
     ```
   - **View Logs**:
     ```bash
     kubectl logs <aggregator-pod-name> -n laboratory-swarm
     ```
   - **Possible Causes**:
     - Image not found or incorrect registry.
     - Environment variables misconfigured.
     - Network policies blocking traffic.

2. **Failed to Send Data to Aggregator API**:
   - **Symptoms**: Logs indicate failed HTTP POST requests.
   - **Solutions**:
     - Ensure Aggregator API is deployed and accessible.
     - Verify the `AGGREGATOR_API_URL` is correct.
     - Check network policies to allow egress to the Aggregator API.

3. **High Memory or CPU Usage**:
   - **Symptoms**: Pod gets OOMKilled or throttled.
   - **Solutions**:
     - Adjust resource requests and limits in `aggregator-deployment.yaml`.
     - Optimize application code for better performance.

### Debugging Steps

1. **Verify Service Accessibility**:
   - Use `kubectl exec` to enter the Aggregator pod and test connectivity to the Aggregator API.
     ```bash
     kubectl exec -it <aggregator-pod-name> -n laboratory-swarm -- /bin/sh
     # Inside the pod
     wget -qO- http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data
     ```

2. **Validate Environment Variables**:
   - Ensure that `AGGREGATOR_PORT` and `AGGREGATOR_API_URL` are correctly set.
     ```bash
     kubectl describe deployment aggregator -n laboratory-swarm
     ```

3. **Check Network Policies**:
   - Ensure that NetworkPolicies are not inadvertently blocking required traffic.
     ```bash
     kubectl get networkpolicy -n laboratory-swarm
     ```

## Further Reading

- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Prometheus Monitoring](https://prometheus.io/docs/introduction/overview/)
- [Istio Service Mesh](https://istio.io/latest/docs/)

---

## Links

- [Root Documentation](../README.md)
- [Aggregator MQTT Bridge Documentation](mqtt_bridge/README.md)

