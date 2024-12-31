# Drones

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

The **Drones** component is a simulated fleet of drone instances within the Laboratory Swarm Application. Each drone generates and sends telemetry data, such as position and battery level, to the Aggregator via UDP and MQTT protocols. This simulation enables testing and development of the system's data collection, aggregation, and processing capabilities without the need for physical drones.

## Architecture

![Drones Architecture](./architecture.png)

*Figure: High-level architecture of the Drones component.*

The Drones operate within the `laboratory-swarm` namespace in the Kubernetes cluster. Each drone instance runs a Python application that simulates telemetry data generation and communication with the Aggregator and MQTT Broker.

## Components

### Deployment Configuration

- **File**: `drones/drone-deployment.yaml`
  
  Defines the Kubernetes Deployment for the Drones, specifying the number of replicas, container image, ports, environment variables, and resource allocations. This deployment simulates multiple drones by running multiple pod replicas.

  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: drone
    namespace: laboratory-swarm
  spec:
    replicas: 10
    selector:
      matchLabels:
        app: drone
    template:
      metadata:
        labels:
          app: drone
      spec:
        containers:
          - name: drone
            image: localhost:5000/drone:latest  # Replace with your Docker registry if necessary
            env:
              - name: DRONE_ID
                valueFrom:
                  fieldRef:
                    fieldPath: metadata.name
              - name: MQTT_BROKER
                value: "mqtt-broker.laboratory-swarm.svc.cluster.local"
              - name: MQTT_PORT
                value: "1883"
              - name: AGGREGATOR_HOST
                value: "aggregator-service.laboratory-swarm.svc.cluster.local"
              - name: AGGREGATOR_PORT
                value: "6000"
            ports:
              - containerPort: 7000
                protocol: TCP
            resources:
              requests:
                memory: "64Mi"
                cpu: "100m"
              limits:
                memory: "128Mi"
                cpu: "200m"
  ```

### Service Configuration

- **File**: `drones/drone-service.yaml`
  
  Defines the Kubernetes Service for the Drones, exposing it internally within the cluster on TCP port `7000`. This service facilitates communication with other components that may need to interact with the drones.

  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: drone-service
    namespace: laboratory-swarm
  spec:
    selector:
      app: drone
    ports:
      - port: 7000
        targetPort: 7000
        protocol: TCP
        name: drone
    type: ClusterIP
  ```

### Application Code

- **File**: `drones/drone_logic.py`
  
  The main Python application that simulates drone behavior by generating telemetry data and sending it to the Aggregator via UDP. Each drone instance generates random positions and battery levels, emulating real-world drone telemetry.

  ```python
  import os
  import socket
  import time
  import random
  import uuid
  import json
  
  # Retrieve DRONE_ID from environment variable or generate a unique ID
  DRONE_NAME = os.getenv("DRONE_ID", f"drone_{uuid.uuid4().hex[:8]}")
  AGGREGATOR_HOST = os.getenv("AGGREGATOR_HOST", "aggregator-service.laboratory-swarm.svc.cluster.local")
  AGGREGATOR_PORT = int(os.getenv("AGGREGATOR_PORT", "6000"))
  
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  
  position = {"latitude": random.uniform(-90, 90), "longitude": random.uniform(-180, 180)}
  battery_level = 100
  
  while True:
      # Create a JSON-formatted message
      data = {
          "drone_id": DRONE_NAME,
          "position": position,
          "battery_level": battery_level
      }
      message = json.dumps(data)
      try:
          # Send data to the Aggregator via UDP
          sock.sendto(message.encode(), (AGGREGATOR_HOST, AGGREGATOR_PORT))
          print(f"Drone {DRONE_NAME} published data: {data}")
      except Exception as e:
          print(f"Error sending data: {e}")
  
      # Simulate battery drain
      battery_level = max(battery_level - random.randint(0, 5), 0)
  
      # Simulate movement by slightly altering position
      position["latitude"] += random.uniform(-0.001, 0.001)
      position["longitude"] += random.uniform(-0.001, 0.001)
  
      time.sleep(5)
  ```

### Dockerfile

- **File**: `drones/Dockerfile`
  
  Defines the Docker image for the Drones application, including the base image, working directory, dependencies, environment variables, and the command to run the application.

  ```dockerfile
  FROM python:3.11-slim
  
  WORKDIR /app
  COPY drone_logic.py /app/drone_logic.py
  COPY requirements.txt /app/requirements.txt
  
  RUN pip install --no-cache-dir -r requirements.txt
  
  ENV DRONE_ID="default_drone"
  ENV AGGREGATOR_HOST="aggregator-service.laboratory-swarm.svc.cluster.local"
  ENV AGGREGATOR_PORT="6000"
  
  EXPOSE 7000
  
  CMD ["python", "drone_logic.py"]
  ```

### Dependencies

- **File**: `drones/requirements.txt`
  
  Lists the Python dependencies required by the Drones application. Currently, no dependencies are specified but can be added as needed.

  ```txt
  # Example Python dependencies, uncomment or add as needed
  # paho-mqtt==1.6.1
  # requests==2.28.2
  ```

## Deployment

### Prerequisites

Before deploying the Drones, ensure that the following prerequisites are met:

- **Kubernetes Cluster**: Ensure you have access to a Kubernetes cluster (v1.18+).
- **Docker Registry**: A Docker registry is available and accessible (`localhost:5000` in this example).
- **Kubectl**: The Kubernetes command-line tool is installed and configured.
- **Namespace**: The `laboratory-swarm` namespace exists. If not, create it:

  ```bash
  kubectl create namespace laboratory-swarm
  ```

- **Aggregator and MQTT Broker**: Ensure the Aggregator and MQTT Broker components are deployed and accessible within the cluster.

### Build and Push Docker Image

1. **Navigate to the Drones Directory**:

   ```bash
   cd drones
   ```

2. **Build the Docker Image**:

   ```bash
   docker build -t localhost:5000/drone:latest .
   ```

3. **Push the Image to the Docker Registry**:

   ```bash
   docker push localhost:5000/drone:latest
   ```

   *Ensure that your Docker registry is running and accessible. Replace `localhost:5000` with your registry address if different.*

### Apply Kubernetes Manifests

1. **Apply the Drones Deployment**:

   ```bash
   kubectl apply -f drone-deployment.yaml
   ```

2. **Apply the Drones Service**:

   ```bash
   kubectl apply -f drone-service.yaml
   ```

   *This will deploy the drone pods and expose them internally within the Kubernetes cluster.*

3. **Verify the Deployment**:

   ```bash
   kubectl get deployments -n laboratory-swarm
   kubectl get pods -n laboratory-swarm -l app=drone
   kubectl get services -n laboratory-swarm -l app=drone
   ```

   *Ensure that the pods are running and the service is correctly exposed.*

## Configuration

### Environment Variables

The Drones application uses the following environment variables for its configuration:

- **DRONE_ID**: A unique identifier for each drone instance. It is automatically set from the pod's metadata name.
  
- **MQTT_BROKER**: The hostname of the MQTT Broker. Default is `mqtt-broker.laboratory-swarm.svc.cluster.local`.
  
- **MQTT_PORT**: The port on which the MQTT Broker is listening. Default is `1883`.
  
- **AGGREGATOR_HOST**: The hostname of the Aggregator service. Default is `aggregator-service.laboratory-swarm.svc.cluster.local`.
  
- **AGGREGATOR_PORT**: The port on which the Aggregator is listening for UDP packets. Default is `6000`.

These variables are defined in the `drone-deployment.yaml` file and can be customized as needed.

```yaml
env:
  - name: DRONE_ID
    valueFrom:
      fieldRef:
        fieldPath: metadata.name
  - name: MQTT_BROKER
    value: "mqtt-broker.laboratory-swarm.svc.cluster.local"
  - name: MQTT_PORT
    value: "1883"
  - name: AGGREGATOR_HOST
    value: "aggregator-service.laboratory-swarm.svc.cluster.local"
  - name: AGGREGATOR_PORT
    value: "6000"
```

## Usage

### Functionality

The Drones perform the following functions:

1. **Telemetry Data Generation**: Each drone instance generates telemetry data, including a unique drone ID, position (latitude and longitude), and battery level.
2. **Data Transmission via UDP**: The telemetry data is sent to the Aggregator using the UDP protocol on port `6000`.
3. **Simulation of Real-World Behavior**: The application simulates battery drain and slight positional changes to emulate realistic drone behavior.

### Logging

The Drones log important events and errors to the standard output, which can be accessed using `kubectl logs`. Example log messages include:

- Successful publication of telemetry data.
- Errors encountered during data transmission.

**Example**:

```bash
kubectl logs <drone-pod-name> -n laboratory-swarm
```

Sample log output:

```
Drone drone-001 published data: {'drone_id': 'drone-001', 'position': {'latitude': 34.0522, 'longitude': -118.2437}, 'battery_level': 85}
Error sending data: [Errno 111] Connection refused
```

## Monitoring

To ensure the Drones are functioning correctly, integrate them with your monitoring tools:

- **Prometheus**: Scrape metrics from the Drones (if metrics are exposed).
- **Grafana**: Visualize metrics related to data generation and transmission rates.
- **Alertmanager**: Set up alerts for failures in data transmission or battery depletion thresholds.

*Note: As of the current implementation, the Drones do not expose Prometheus metrics. Consider integrating a metrics exporter if monitoring is required.*

## Security

### Network Policies

The Drones are secured using Kubernetes NetworkPolicies, which define allowed inbound and outbound traffic. The provided `network-policy.yaml` allows:

- **Ingress**:
  - Only from the MQTT Broker and Aggregator services on the specified ports.
  
- **Egress**:
  - Only to the MQTT Broker on port `1883` and Aggregator on port `6000`.

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

Role-Based Access Control (RBAC) ensures that only authorized service accounts can interact with the Drones and other Kubernetes resources. The provided `rbac.yaml` defines:

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

1. **Drones Pod Not Running**:
   - **Check Pod Status**:
     ```bash
     kubectl get pods -n laboratory-swarm -l app=drone
     ```
   - **View Logs**:
     ```bash
     kubectl logs <drone-pod-name> -n laboratory-swarm
     ```
   - **Possible Causes**:
     - Image not found or incorrect registry.
     - Environment variables misconfigured.
     - Network policies blocking traffic.

2. **Failed to Send Data to Aggregator**:
   - **Symptoms**: Logs indicate failed UDP transmissions.
   - **Solutions**:
     - Ensure Aggregator is deployed and accessible.
     - Verify the `AGGREGATOR_HOST` and `AGGREGATOR_PORT` environment variables are correct.
     - Check network policies to allow egress traffic to the Aggregator.

3. **High Battery Drain or Stagnant Position**:
   - **Symptoms**: Battery levels deplete rapidly or position does not change.
   - **Solutions**:
     - Review the `drone_logic.py` to adjust battery drain rates and movement simulation.
     - Ensure the application logic is functioning as intended.

4. **Resource Limitations**:
   - **Symptoms**: Pods are throttled or OOMKilled.
   - **Solutions**:
     - Adjust resource requests and limits in `drone-deployment.yaml`.
     - Optimize application code for better performance.

### Debugging Steps

1. **Verify Service Accessibility**:
   - Use `kubectl exec` to enter the Drone pod and test connectivity to the Aggregator.
     ```bash
     kubectl exec -it <drone-pod-name> -n laboratory-swarm -- /bin/sh
     # Inside the pod
     nc -zv aggregator-service.laboratory-swarm.svc.cluster.local 6000
     ```
   
2. **Validate Environment Variables**:
   - Ensure that `DRONE_ID`, `MQTT_BROKER`, `MQTT_PORT`, `AGGREGATOR_HOST`, and `AGGREGATOR_PORT` are correctly set.
     ```bash
     kubectl describe deployment drone -n laboratory-swarm
     ```

3. **Check Network Policies**:
   - Ensure that NetworkPolicies are not inadvertently blocking required traffic.
     ```bash
     kubectl get networkpolicy -n laboratory-swarm
     ```
   
4. **Inspect Aggregator Logs**:
   - Check logs of the Aggregator to ensure it is receiving data from drones.
     ```bash
     kubectl logs <aggregator-pod-name> -n laboratory-swarm
     ```

## Further Reading

- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
- [Python Socket Programming](https://docs.python.org/3/library/socket.html)
- [Docker Documentation](https://docs.docker.com/)
- [Prometheus Monitoring](https://prometheus.io/docs/introduction/overview/)
- [Istio Service Mesh](https://istio.io/latest/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

## Links

- [Root Documentation](../README.md)
- [Aggregator Documentation](../aggregator/README.md)
- [Aggregator MQTT Bridge Documentation](../aggregator/mqtt_bridge/README.md)
- [Aggregator API Documentation](../aggregator-api/README.md)

---

If you encounter any issues or have questions regarding the Drones component, please refer to the [Troubleshooting](#troubleshooting) section or reach out to the project maintainers.