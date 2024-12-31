# MQTT Bridge

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
  - [Mosquitto MQTT Broker](#mosquitto-mqtt-broker)
    - [Deployment Configuration](#deployment-configuration)
    - [Service Configuration](#service-configuration)
    - [Configuration File](#configuration-file)
  - [MQTT Bridge Application](#mqtt-bridge-application)
    - [Deployment Configuration](#deployment-configuration-1)
    - [Service Configuration](#service-configuration-1)
    - [Application Code](#application-code)
    - [Dockerfile](#dockerfile-1)
    - [Dependencies](#dependencies-1)
- [Deployment](#deployment)
  - [Prerequisites](#prerequisites-1)
  - [Build and Push Docker Image](#build-and-push-docker-image-1)
  - [Apply Kubernetes Manifests](#apply-kubernetes-manifests-1)
- [Configuration](#configuration-1)
  - [Environment Variables](#environment-variables-1)
- [Usage](#usage-1)
  - [Functionality](#functionality-1)
  - [Logging](#logging-1)
- [Monitoring](#monitoring-1)
- [Security](#security-1)
- [Troubleshooting](#troubleshooting-1)
- [Further Reading](#further-reading-1)

---

## Overview

The **MQTT Bridge** is an essential component of the Laboratory Swarm Application, facilitating seamless communication between drones and the Aggregator API through the MQTT protocol. It comprises an MQTT broker (Mosquitto) and a bridge application that subscribes to specific MQTT topics, processes incoming messages, and forwards the data to the Aggregator API for storage and analysis.

## Architecture

![MQTT Bridge Architecture](./architecture.png)

*Figure: High-level architecture of the MQTT Bridge component.*

The MQTT Bridge operates within the `laboratory-swarm` namespace in the Kubernetes cluster. It consists of two primary parts:

1. **Mosquitto MQTT Broker**: Handles MQTT protocol communications, allowing drones to publish telemetry data to designated topics.
2. **MQTT Bridge Application**: Subscribes to MQTT topics, processes incoming messages, and forwards them to the Aggregator API via HTTP POST requests.

## Components

### Mosquitto MQTT Broker

#### Deployment Configuration

- **File**: `mqtt_bridge/mosquitto-deployment.yaml`
  
  Defines the Kubernetes Deployment for the Mosquitto MQTT Broker, specifying the number of replicas, container image, ports, and volume mounts for configuration and data storage.

  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: mqtt-broker
    namespace: laboratory-swarm
  spec:
    replicas: 1
    selector:
      matchLabels:
        app: mqtt-broker
    template:
      metadata:
        labels:
          app: mqtt-broker
      spec:
        containers:
          - name: mqtt-broker
            image: eclipse-mosquitto:2.0
            ports:
              - containerPort: 1883
                protocol: TCP
            volumeMounts:
              - name: mosquitto-config
                mountPath: /mosquitto/config/mosquitto.conf
                subPath: mosquitto.conf
              - name: mosquitto-data
                mountPath: /mosquitto/data
        volumes:
          - name: mosquitto-config
            configMap:
              name: mosquitto-config
          - name: mosquitto-data
            emptyDir: {}
  ```

#### Service Configuration

- **File**: `mqtt_bridge/mosquitto-service.yaml`
  
  Defines the Kubernetes Service for the Mosquitto MQTT Broker, exposing it internally within the cluster on TCP port `1883`.

  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: mqtt-broker
    namespace: laboratory-swarm
  spec:
    selector:
      app: mqtt-broker
    ports:
      - port: 1883
        targetPort: 1883
        protocol: TCP
        name: mqtt
    type: ClusterIP
  ```

#### Configuration File

- **File**: `mqtt_bridge/mosquitto.conf`
  
  The configuration file for Mosquitto MQTT Broker, defining listener ports and security settings.

  ```conf
  listener 1883
  allow_anonymous true

  # -- ADDITIONAL COMMENTS AND PARAMETERS --
  # listener 8883
  # certfile /mosquitto/config/certs/server.crt
  # keyfile  /mosquitto/config/certs/server.key
  # cafile   /mosquitto/config/certs/ca.crt
  # require_certificate false
  
  # Uncomment and configure the above sections to enable TLS.
  
  # Example of configuring ACLs and passwords:
  # allow_anonymous false
  # password_file /mosquitto/config/passwordfile
  # acl_file /mosquitto/config/aclfile
  ```

### MQTT Bridge Application

#### Deployment Configuration

- **File**: `mqtt_bridge/mqtt_bridge-deployment.yaml`
  
  Defines the Kubernetes Deployment for the MQTT Bridge application, specifying the number of replicas, container image, environment variables, and resource allocations. It includes an init container to ensure the MQTT Broker is ready before the bridge starts.

  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: mqtt-bridge
    namespace: laboratory-swarm
  spec:
    replicas: 1
    selector:
      matchLabels:
        app: mqtt-bridge
    template:
      metadata:
        labels:
          app: mqtt-bridge
      spec:
        initContainers:
          - name: wait-for-mqtt
            image: nicolaka/netshoot
            command: ["sh", "-c", "until nc -z mqtt-broker 1883; do echo waiting for mqtt-broker; sleep 2; done"]
        containers:
          - name: mqtt-bridge
            image: localhost:5000/mqtt-bridge:latest
            env:
              - name: MQTT_BROKER
                value: "mqtt-broker.laboratory-swarm.svc.cluster.local"
              - name: MQTT_PORT
                value: "1883"
              - name: TARGET_API_URL
                value: "http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data"
              - name: MQTT_TOPIC
                value: "drone/positions"
            resources:
              requests:
                memory: "128Mi"
                cpu: "250m"
              limits:
                memory: "256Mi"
                cpu: "500m"
  ```

#### Service Configuration

- **File**: `mqtt_bridge/mqtt_bridge-service.yaml`
  
  Defines the Kubernetes Service for the MQTT Bridge application, exposing it internally within the cluster on TCP port `1883`.

  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: mqtt-bridge
    namespace: laboratory-swarm
  spec:
    selector:
      app: mqtt-bridge
    ports:
      - port: 1883
        targetPort: 1883
        protocol: TCP
        name: mqtt
    type: ClusterIP
  ```

#### Application Code

- **File**: `mqtt_bridge/mqtt_bridge.py`
  
  The main Python application that subscribes to MQTT topics, processes incoming messages, and forwards them to the Aggregator API.

  ```python
  import os
  import paho.mqtt.client as mqtt
  import requests
  import json
  
  MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt-broker.laboratory-swarm.svc.cluster.local")
  MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
  TARGET_API_URL = os.getenv("TARGET_API_URL",
                             "http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data")
  MQTT_TOPIC = os.getenv("MQTT_TOPIC", "drone/positions")
  
  
  def on_connect(client, userdata, flags, rc):
      """
      Callback function executed upon connecting to the MQTT broker.
      rc == 0 indicates a successful connection, after which it subscribes to the specified topic.
      """
      if rc == 0:
          print(f"[mqtt_bridge] Connected to {MQTT_BROKER}:{MQTT_PORT}")
          client.subscribe(MQTT_TOPIC)
          print(f"[mqtt_bridge] Subscribed to topic '{MQTT_TOPIC}'")
      else:
          print(f"[mqtt_bridge] Connection failed (rc={rc})")
  
  
  def on_message(client, userdata, msg):
      """
      Callback function executed for each received MQTT message.
      Processes the message payload and forwards it to the Aggregator API.
      """
      payload_str = msg.payload.decode(errors='replace')
      print(f"[mqtt_bridge] Received on {msg.topic}: {payload_str}")
  
      # Forward data to Aggregator API
      try:
          data = json.loads(payload_str)
          response = requests.post(TARGET_API_URL, json=data)
          if response.status_code == 200:
              print("[mqtt_bridge] Successfully sent data to Aggregator API.")
          else:
              print(f"[mqtt_bridge] Failed to send data to Aggregator API: {response.status_code}")
      except Exception as e:
          print(f"[mqtt_bridge] Error sending data to Aggregator API: {e}")
  
  
  if __name__ == "__main__":
      print("[mqtt_bridge] Starting up MQTT bridge...")
  
      client = mqtt.Client()
      client.on_connect = on_connect
      client.on_message = on_message
  
      try:
          client.connect(MQTT_BROKER, MQTT_PORT, 60)
          client.loop_forever()
      except Exception as e:
          print(f"[mqtt_bridge] Fatal error: {e}")
  ```

#### Dockerfile

- **File**: `mqtt_bridge/Dockerfile`
  
  Defines the Docker image for the MQTT Bridge application, including the base image, working directory, dependencies, environment variables, and the command to run the application.

  ```dockerfile
  FROM python:3.11-slim
  
  WORKDIR /app
  
  COPY mqtt_bridge.py /app/mqtt_bridge.py
  COPY requirements.txt /app/requirements.txt
  
  RUN pip install --no-cache-dir -r requirements.txt
  
  ENV MQTT_BROKER=mqtt-broker.laboratory-swarm.svc.cluster.local
  ENV MQTT_PORT=1883
  ENV TARGET_API_URL=http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data
  ENV MQTT_TOPIC=drone/positions
  
  CMD ["python", "mqtt_bridge.py"]
  ```

#### Dependencies

- **File**: `mqtt_bridge/requirements.txt`
  
  Lists the Python dependencies required by the MQTT Bridge application.

  ```txt
  paho-mqtt==1.6.1
  requests==2.28.2
  ```

## Deployment

### Prerequisites

Before deploying the MQTT Bridge, ensure that the following prerequisites are met:

- **Kubernetes Cluster**: Ensure you have access to a Kubernetes cluster (v1.18+).
- **Docker Registry**: A Docker registry is available and accessible (`localhost:5000` in this example).
- **Kubectl**: The Kubernetes command-line tool is installed and configured.
- **Namespace**: The `laboratory-swarm` namespace exists. If not, create it:
  
  ```bash
  kubectl create namespace laboratory-swarm
  ```

- **Mosquitto ConfigMap**: Create a ConfigMap for Mosquitto configuration.

  ```bash
  kubectl apply -f mqtt_bridge/mosquitto.conf
  ```

### Build and Push Docker Image

1. **Navigate to the MQTT Bridge Directory**:

   ```bash
   cd aggregator/mqtt_bridge
   ```

2. **Build the Docker Image**:

   ```bash
   docker build -t localhost:5000/mqtt-bridge:latest .
   ```

3. **Push the Image to the Docker Registry**:

   ```bash
   docker push localhost:5000/mqtt-bridge:latest
   ```

   *Ensure that your Docker registry is running and accessible. Replace `localhost:5000` with your registry address if different.*

### Apply Kubernetes Manifests

1. **Apply the Mosquitto Deployment**:

   ```bash
   kubectl apply -f mosquitto-deployment.yaml
   ```

2. **Apply the Mosquitto Service**:

   ```bash
   kubectl apply -f mosquitto-service.yaml
   ```

3. **Apply the MQTT Bridge Deployment**:

   ```bash
   kubectl apply -f mqtt_bridge-deployment.yaml
   ```

4. **Apply the MQTT Bridge Service**:

   ```bash
   kubectl apply -f mqtt_bridge-service.yaml
   ```

5. **Verify the Deployment**:

   ```bash
   kubectl get deployments -n laboratory-swarm
   kubectl get pods -n laboratory-swarm -l app=mqtt-bridge
   kubectl get services -n laboratory-swarm -l app=mqtt-bridge
   ```

   *Ensure that the pods are running and the services are correctly exposed.*

## Configuration

### Environment Variables

The MQTT Bridge uses the following environment variables for its configuration:

- **MQTT_BROKER**: The hostname of the MQTT broker. Default is `mqtt-broker.laboratory-swarm.svc.cluster.local`.
- **MQTT_PORT**: The port on which the MQTT broker is listening. Default is `1883`.
- **TARGET_API_URL**: The endpoint URL of the Aggregator API where processed data is forwarded. Default is `http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data`.
- **MQTT_TOPIC**: The MQTT topic to subscribe to for incoming telemetry data. Default is `drone/positions`.

These variables are defined in the `mqtt_bridge-deployment.yaml` file and can be customized as needed.

```yaml
env:
  - name: MQTT_BROKER
    value: "mqtt-broker.laboratory-swarm.svc.cluster.local"
  - name: MQTT_PORT
    value: "1883"
  - name: TARGET_API_URL
    value: "http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data"
  - name: MQTT_TOPIC
    value: "drone/positions"
```

## Usage

### Functionality

The MQTT Bridge performs the following functions:

1. **Connecting to MQTT Broker**: Establishes a connection to the Mosquitto MQTT Broker using the specified broker address and port.
2. **Subscribing to MQTT Topics**: Subscribes to the defined MQTT topic (`drone/positions`) to receive telemetry data from drones.
3. **Processing Incoming Messages**: For each received MQTT message, it decodes the payload, parses the JSON data, and validates the necessary fields.
4. **Forwarding Data to Aggregator API**: Sends the processed data to the Aggregator API via an HTTP POST request for storage and further analysis.

### Logging

The MQTT Bridge logs important events and errors to the standard output, which can be accessed using `kubectl logs`. Example log messages include:

- Successful connection to the MQTT broker.
- Successful subscription to the MQTT topic.
- Receipt of MQTT messages from drones.
- Successful forwarding of data to the Aggregator API.
- Errors encountered during message processing or data forwarding.

**Example**:

```bash
kubectl logs <mqtt-bridge-pod-name> -n laboratory-swarm
```

## Monitoring

To ensure the MQTT Bridge is functioning correctly, integrate it with your monitoring tools:

- **Prometheus**: Scrape metrics from the MQTT Bridge (if metrics are exposed).
- **Grafana**: Visualize metrics related to MQTT message ingestion and forwarding.
- **Alertmanager**: Set up alerts for failures in data forwarding or high error rates.

*Note: As of the current implementation, the MQTT Bridge does not expose Prometheus metrics. Consider integrating a metrics exporter if monitoring is required.*

## Security

### Network Policies

The MQTT Bridge is secured using Kubernetes NetworkPolicies, which define allowed inbound and outbound traffic. The provided `network-policy.yaml` allows:

- **Ingress**:
  - Only pods labeled `app=drone` can send UDP traffic on port `6000`.
- **Egress**:
  - Only to pods labeled `app=aggregator-api` on port `6001` via TCP.

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

Role-Based Access Control (RBAC) ensures that only authorized service accounts can interact with the MQTT Bridge and other Kubernetes resources. The provided `rbac.yaml` defines:

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

1. **MQTT Bridge Pod Not Running**:
   - **Check Pod Status**:
     ```bash
     kubectl get pods -n laboratory-swarm -l app=mqtt-bridge
     ```
   - **View Logs**:
     ```bash
     kubectl logs <mqtt-bridge-pod-name> -n laboratory-swarm
     ```
   - **Possible Causes**:
     - Image not found or incorrect registry.
     - Environment variables misconfigured.
     - Network policies blocking traffic.

2. **Failed to Connect to MQTT Broker**:
   - **Symptoms**: Logs indicate failed connections to the MQTT broker.
   - **Solutions**:
     - Ensure the Mosquitto MQTT Broker is deployed and running.
     - Verify the `MQTT_BROKER` and `MQTT_PORT` environment variables are correct.
     - Check network policies to allow traffic between MQTT Bridge and MQTT Broker.

3. **Failed to Send Data to Aggregator API**:
   - **Symptoms**: Logs indicate failed HTTP POST requests.
   - **Solutions**:
     - Ensure Aggregator API is deployed and accessible.
     - Verify the `TARGET_API_URL` is correct.
     - Check network policies to allow egress to the Aggregator API.

4. **High Memory or CPU Usage**:
   - **Symptoms**: Pod gets OOMKilled or throttled.
   - **Solutions**:
     - Adjust resource requests and limits in `mqtt_bridge-deployment.yaml`.
     - Optimize application code for better performance.

### Debugging Steps

1. **Verify Service Accessibility**:
   - Use `kubectl exec` to enter the MQTT Bridge pod and test connectivity to the MQTT Broker and Aggregator API.
     ```bash
     kubectl exec -it <mqtt-bridge-pod-name> -n laboratory-swarm -- /bin/sh
     # Inside the pod
     wget -qO- mqtt-broker.laboratory-swarm.svc.cluster.local:1883
     wget -qO- http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data
     ```

2. **Validate Environment Variables**:
   - Ensure that `MQTT_BROKER`, `MQTT_PORT`, `TARGET_API_URL`, and `MQTT_TOPIC` are correctly set.
     ```bash
     kubectl describe deployment mqtt-bridge -n laboratory-swarm
     ```

3. **Check Network Policies**:
   - Ensure that NetworkPolicies are not inadvertently blocking required traffic.
     ```bash
     kubectl get networkpolicy -n laboratory-swarm
     ```

4. **Inspect Mosquitto Logs**:
   - Check logs of the Mosquitto MQTT Broker to ensure it is running correctly.
     ```bash
     kubectl logs <mosquitto-pod-name> -n laboratory-swarm
     ```

## Further Reading

- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
- [Mosquitto MQTT Broker Documentation](https://mosquitto.org/documentation/)
- [Paho MQTT Python Client](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)
- [Prometheus Monitoring](https://prometheus.io/docs/introduction/overview/)
- [Istio Service Mesh](https://istio.io/latest/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)

---

## Links

- [Root Documentation](../README.md)
- [Aggregator Documentation](README.md)
- [Aggregator API Documentation](../aggregator-api/README.md)
