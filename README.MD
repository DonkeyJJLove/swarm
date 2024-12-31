# Laboratory Swarm Application Documentation

The Laboratory Swarm Application is a sophisticated system designed to manage and monitor a fleet of drones within a Kubernetes cluster. This documentation provides a comprehensive overview of the project's architecture, deployment procedures, and operational guidelines, organized across various levels of abstraction corresponding to the project's directory structure.

## Table of Contents

- [Root Documentation](#root-documentation)
  - [Overview](#overview)
  - [Architecture](#architecture)
  - [Directory Structure](#directory-structure)
  - [Getting Started](#getting-started)
  - [Deployment](#deployment)
  - [Monitoring and Logging](#monitoring-and-logging)
  - [Security](#security)
  - [Contributing](#contributing)
  - [License](#license)
- [Component Documentation](#component-documentation)
  - [Aggregator](aggregator/README.md)
    - [MQTT Bridge](aggregator/mqtt_bridge/README.md)
  - [Aggregator API](aggregator-api/README.md)
  - [Drones](drones/README.md)
  - [Infrastructure](infrastructure/README.md)
    - [Istio Configuration](infrastructure/istio/README.md)
      - [Alert Rules](infrastructure/istio/alertrules/README.md)
      - [Destination Rules](infrastructure/istio/destinationrules/README.md)
      - [Gateways](infrastructure/istio/gateways/README.md)
      - [Policies](infrastructure/istio/policies/README.md)
      - [Virtual Services](infrastructure/istio/virtualservices/README.md)
    - [Kubernetes Monitoring Tools](infrastructure/kubernetes/README.md)
    - [StatefulSets](infrastructure/statefulset/README.md)
  - [Security](security/README.md)
    - [Network Policies and RBAC](security/policies/README.md)
  - [Server](server/README.md)
  - [AI Service](system-ai/README.md)

---

## Root Documentation

### Overview

The Laboratory Swarm Application is a comprehensive system designed to manage and monitor a fleet of drones within a Kubernetes cluster. The application comprises multiple components that work together to collect, process, store, and visualize telemetry data from drones. Additionally, it integrates with AI services for advanced data analysis and decision-making.

### Architecture

The system architecture is organized into several key modules:

- **Aggregator**: Collects telemetry data from drones via UDP and MQTT protocols and forwards the data to the Aggregator API.
- **Aggregator API**: Receives processed data from the Aggregator and MQTT Bridge, stores it in a PostgreSQL database, and provides endpoints for data retrieval.
- **Drones**: Simulated drone instances that generate and send telemetry data to the Aggregator.
- **MQTT Bridge**: Bridges MQTT messages from drones to the Aggregator API.
- **Server**: Provides endpoints for data access and visualization.
- **AI Service**: Integrates AI models for predictive analytics and decision-making.
- **Infrastructure**: Manages Kubernetes resources, including Istio configurations for traffic management, monitoring tools like Prometheus, Grafana, Jaeger, and stateful services.
- **Security**: Defines network policies and RBAC configurations to secure inter-component communication.

### Directory Structure

```
.
├── aggregator
│   ├── aggregator-deployment.yaml
│   ├── aggregator-service.yaml
│   ├── aggregator.py
│   ├── Dockerfile
│   ├── mqtt_bridge
│   │   ├── Dockerfile
│   │   ├── mosquitto-deployment.yaml
│   │   ├── mosquitto-service.yaml
│   │   ├── mosquitto.conf
│   │   ├── mqtt_bridge-deployment.yaml
│   │   ├── mqtt_bridge.py
│   │   └── requirements.txt
│   └── requirements.txt
├── aggregator-api
│   ├── aggregator-api-deployment.yaml
│   ├── aggregator-api-service.yaml
│   ├── aggregator_api.py
│   ├── Dockerfile
│   └── requirements.txt
├── drones
│   ├── Dockerfile
│   ├── drone-deployment.yaml
│   ├── drone-service.yaml
│   ├── drone_logic.py
│   └── requirements.txt
├── infrastructure
│   ├── istio
│   │   ├── alertrules
│   │   │   └── serwer-alerts.yaml
│   │   ├── destinationrules
│   │   │   ├── aggregator-destinationrule.yaml
│   │   │   └── serwer-destinationrule.yaml
│   │   ├── gateways
│   │   │   ├── egress-gateway.yaml
│   │   │   └── ingress-gateway.yaml
│   │   ├── policies
│   │   │   ├── circuit-breaker.yaml
│   │   │   └── rate-limit.yaml
│   │   └── virtualservices
│   │       ├── eegress-virtualservice.yaml
│   │       └── swarm-virtualservice.yaml
│   ├── kubernetes
│   │   ├── alertmanager.yaml
│   │   ├── grafana.yaml
│   │   ├── jaeger.yaml
│   │   └── prometheus.yaml
│   └── statefulset
│       ├── postgresql-service.yaml
│       └── postgresql-statefulset.yaml
├── security
│   └── policies
│       ├── network-policy.yaml
│       └── rbac.yaml
├── server
│   ├── app.py
│   ├── Dockerfile
│   ├── postgresql-secret.yaml
│   ├── requirements.txt
│   └── visualization.py
├── system-ai
│   ├── ai-service-deployment.yaml
│   ├── ai-service-service.yaml
│   ├── ai_service.py
│   └── Dockerfile
└── README.md
```

### Getting Started

To get started with the Laboratory Swarm Application, follow these steps:

1. **Prerequisites**:
   - Kubernetes Cluster (v1.18+)
   - Docker
   - kubectl
   - Helm (optional, for package management)
   - Istio Service Mesh installed on the cluster

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/laboratory-swarm.git
   cd laboratory-swarm
   ```

3. **Build and Push Docker Images**:
   - Build Docker images for each component (Aggregator, MQTT Bridge, Aggregator API, Drones, Server, AI Service).
   - Push the images to your Docker registry.
   ```bash
   docker build -t localhost:5000/aggregator:latest ./aggregator
   docker push localhost:5000/aggregator:latest

   docker build -t localhost:5000/mqtt-bridge:latest ./aggregator/mqtt_bridge
   docker push localhost:5000/mqtt-bridge:latest

   docker build -t localhost:5000/aggregator-api:latest ./aggregator-api
   docker push localhost:5000/aggregator-api:latest

   docker build -t localhost:5000/drone:latest ./drones
   docker push localhost:5000/drone:latest

   docker build -t localhost:5000/server:latest ./server
   docker push localhost:5000/server:latest

   docker build -t localhost:5000/ai-service:latest ./system-ai
   docker push localhost:5000/ai-service:latest
   ```

4. **Apply Kubernetes Manifests**:
   - Deploy the necessary components to the Kubernetes cluster.
   ```bash
   kubectl apply -f security/policies/network-policy.yaml
   kubectl apply -f security/policies/rbac.yaml

   kubectl apply -f infrastructure/statefulset/postgresql-service.yaml
   kubectl apply -f infrastructure/statefulset/postgresql-statefulset.yaml

   kubectl apply -f aggregator/aggregator-deployment.yaml
   kubectl apply -f aggregator/aggregator-service.yaml

   kubectl apply -f aggregator/mqtt_bridge/mosquitto-deployment.yaml
   kubectl apply -f aggregator/mqtt_bridge/mosquitto-service.yaml
   kubectl apply -f aggregator/mqtt_bridge/mosquitto.conf
   kubectl apply -f aggregator/mqtt_bridge/mqtt_bridge-deployment.yaml

   kubectl apply -f aggregator-api/aggregator-api-deployment.yaml
   kubectl apply -f aggregator-api/aggregator-api-service.yaml

   kubectl apply -f drones/drone-deployment.yaml
   kubectl apply -f drones/drone-service.yaml

   kubectl apply -f server/postgresql-secret.yaml
   kubectl apply -f server/server-deployment.yaml
   kubectl apply -f server/server-service.yaml

   kubectl apply -f system-ai/ai-service-deployment.yaml
   kubectl apply -f system-ai/ai-service-service.yaml

   kubectl apply -f infrastructure/istio/
   kubectl apply -f infrastructure/kubernetes/
   ```

5. **Configure Ingress and DNS**:
   - Ensure that DNS records point to your Istio Ingress Gateway.
   - Configure VirtualServices and Gateways as per your environment.

6. **Access the Services**:
   - Access the Server endpoints for data and visualization.
   - Use Prometheus, Grafana, and Jaeger for monitoring and tracing.
   - Set up Alertmanager for receiving alerts.

## Deployment

Deployment is managed through Kubernetes manifests organized within the project's directory structure. Each component has its own deployment and service configurations to ensure modularity and scalability.

Refer to individual component [README.md](#component-documentation) files for detailed deployment instructions.

## Monitoring and Logging

The infrastructure includes robust monitoring and logging tools:

- **Prometheus**: Collects metrics from all components.
- **Grafana**: Visualizes metrics through dashboards.
- **Jaeger**: Traces requests across services for performance analysis.
- **Alertmanager**: Manages alerts based on Prometheus rules and sends notifications via Slack.

Configurations for these tools are located under `infrastructure/kubernetes` and `infrastructure/istio`.

## Security

Security is enforced through Kubernetes NetworkPolicies and RBAC:

- **Network Policies**: Define allowed inbound and outbound traffic between services.
- **RBAC**: Controls access permissions for service accounts to interact with Kubernetes resources.

Refer to the [Security Documentation](security/README.md) for detailed configurations.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes with clear messages.
4. Push to your fork and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Component Documentation

### Aggregator

[Aggregator Documentation](aggregator/README.md)

#### MQTT Bridge

[MQTT Bridge Documentation](aggregator/mqtt_bridge/README.md)

### Aggregator API

[Aggregator API Documentation](aggregator-api/README.md)

### Drones

[Drones Documentation](drones/README.md)

### Infrastructure

[Infrastructure Documentation](infrastructure/README.md)

#### Istio Configuration

[Istio Configuration Documentation](infrastructure/istio/README.md)

##### Alert Rules

[Alert Rules Documentation](infrastructure/istio/alertrules/README.md)

##### Destination Rules

[Destination Rules Documentation](infrastructure/istio/destinationrules/README.md)

##### Gateways

[Gateways Documentation](infrastructure/istio/gateways/README.md)

##### Policies

[Policies Documentation](infrastructure/istio/policies/README.md)

##### Virtual Services

[Virtual Services Documentation](infrastructure/istio/virtualservices/README.md)

#### Kubernetes Monitoring Tools

[Kubernetes Monitoring Tools Documentation](infrastructure/kubernetes/README.md)

#### StatefulSets

[StatefulSets Documentation](infrastructure/statefulset/README.md)

### Security

[Security Documentation](security/README.md)

#### Network Policies and RBAC

[Network Policies and RBAC Documentation](security/policies/README.md)

### Server

[Server Documentation](server/README.md)

### AI Service

[AI Service Documentation](system-ai/README.md)

---

Each component's documentation provides detailed insights into its purpose, configuration, deployment, and best practices. For in-depth information, refer to the respective [README.md](#component-documentation) files within each directory.

If you have any questions or need further assistance, feel free to reach out to the project maintainers.

---

## Final Note

This documentation aims to provide a clear and organized understanding of the Laboratory Swarm Application's structure and functionality. By following the guidelines and configurations outlined in each component's documentation, you can effectively deploy, manage, and maintain the system within your Kubernetes environment.

For any additional information or updates, please refer to the project's repository or contact the maintainers.