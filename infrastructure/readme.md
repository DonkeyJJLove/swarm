# Infrastructure

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
  - [Istio Configuration](istio/README.md)
    - [Alert Rules](istio/alertrules/README.md)
    - [Destination Rules](istio/destinationrules/README.md)
    - [Gateways](istio/gateways/README.md)
    - [Policies](istio/policies/README.md)
    - [Virtual Services](istio/virtualservices/README.md)
  - [Kubernetes Monitoring Tools](kubernetes/README.md)
  - [StatefulSets](statefulset/README.md)
- [Deployment](#deployment)
  - [Prerequisites](#prerequisites)
  - [Apply Kubernetes Manifests](#apply-kubernetes-manifests)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
- [Monitoring](#monitoring)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Further Reading](#further-reading)
- [Links](#links)

---

## Overview

The **Infrastructure** component of the Laboratory Swarm Application encompasses the foundational services and configurations necessary for the smooth operation, monitoring, and management of the system within the Kubernetes cluster. This includes the service mesh provided by Istio, monitoring and logging tools like Prometheus, Grafana, Jaeger, and Alertmanager, as well as essential stateful services such as PostgreSQL.

## Architecture

![Infrastructure Architecture](./architecture.png)

*Figure: High-level architecture of the Infrastructure component.*

The Infrastructure ensures reliable traffic management, comprehensive monitoring, and secure communication between different components of the Laboratory Swarm Application.

## Components

### Istio Configuration

The **Istio Service Mesh** manages traffic between microservices, providing features like load balancing, traffic routing, security, and observability.

- [Istio Configuration Documentation](istio/README.md)

  - [Alert Rules](istio/alertrules/README.md)
  - [Destination Rules](istio/destinationrules/README.md)
  - [Gateways](istio/gateways/README.md)
  - [Policies](istio/policies/README.md)
  - [Virtual Services](istio/virtualservices/README.md)

### Kubernetes Monitoring Tools

Comprehensive monitoring and logging are achieved using a suite of tools:

- **Prometheus**: Collects and stores metrics.
- **Grafana**: Visualizes metrics through dashboards.
- **Jaeger**: Traces requests across services.
- **Alertmanager**: Manages and routes alerts.

- [Kubernetes Monitoring Tools Documentation](kubernetes/README.md)

### StatefulSets

StatefulSets manage stateful applications, ensuring stable and unique network identifiers, stable storage, and ordered deployment and scaling.

- **PostgreSQL**: A robust relational database used for storing drone telemetry data.

- [StatefulSets Documentation](statefulset/README.md)

## Deployment

### Prerequisites

Before deploying the Infrastructure components, ensure the following prerequisites are met:

- **Kubernetes Cluster**: A functional Kubernetes cluster (v1.18+).
- **Kubectl**: The Kubernetes command-line tool is installed and configured.
- **Namespace**: Ensure the `monitoring` namespace exists for monitoring tools.
  
  ```bash
  kubectl create namespace monitoring
  ```

- **Istio Service Mesh**: Istio is installed and configured on the cluster.

### Apply Kubernetes Manifests

Deploy the Infrastructure components by applying the Kubernetes manifests located within the `infrastructure` directory.

1. **Istio Configurations**:

   Apply all Istio configurations:
   
   ```bash
   kubectl apply -f infrastructure/istio/
   ```

2. **Kubernetes Monitoring Tools**:

   Deploy Prometheus, Grafana, Jaeger, and Alertmanager:
   
   ```bash
   kubectl apply -f infrastructure/kubernetes/
   ```

3. **StatefulSets**:

   Deploy the PostgreSQL StatefulSet and Service:
   
   ```bash
   kubectl apply -f infrastructure/statefulset/postgresql-service.yaml
   kubectl apply -f infrastructure/statefulset/postgresql-statefulset.yaml
   ```

4. **Verify Deployments**:

   Check the status of the deployments to ensure all components are running correctly:
   
   ```bash
   kubectl get deployments -n monitoring
   kubectl get pods -n monitoring
   kubectl get statefulsets -n laboratory-swarm
   kubectl get pods -n laboratory-swarm -l app=postgresql
   ```

## Configuration

### Environment Variables

Configuration parameters for the Infrastructure components are typically defined within their respective Kubernetes manifests. Key environment variables include:

- **Istio**: Configuration is managed via Istio resources like VirtualServices, DestinationRules, Gateways, and EnvoyFilters.
  
- **Prometheus**: Configured through Prometheus CRDs and ServiceMonitors.
  
- **Grafana**: Admin credentials and data sources are configured via environment variables and Kubernetes Secrets.

- **Jaeger**: Configuration is defined within the Jaeger CRD.

- **PostgreSQL**: Credentials and database settings are managed via Kubernetes Secrets.

Ensure that sensitive information like passwords and API keys are stored securely using Kubernetes Secrets and referenced appropriately in the manifests.

## Monitoring

The Infrastructure provides robust monitoring and logging capabilities to ensure the health and performance of the Laboratory Swarm Application:

- **Prometheus**: Scrapes metrics from all monitored services and stores them for analysis.
  
- **Grafana**: Connects to Prometheus to visualize metrics through customizable dashboards.
  
- **Jaeger**: Enables distributed tracing, allowing tracking of requests across multiple services.
  
- **Alertmanager**: Handles alerts generated by Prometheus, routing them to appropriate notification channels like Slack.

Ensure that Grafana dashboards and Prometheus alert rules are configured to monitor critical metrics and trigger alerts as needed.

## Security

Security within the Infrastructure is enforced through:

- **Istio Service Mesh**: Provides mutual TLS, secure communication between services, and traffic policies.
  
- **Network Policies**: Define allowed inbound and outbound traffic, ensuring that only authorized services can communicate.
  
- **RBAC**: Controls access permissions for Kubernetes resources, ensuring that only authorized service accounts can perform specific actions.

Ensure that all security policies are correctly configured and regularly reviewed to maintain the security posture of the application.

## Troubleshooting

### Common Issues

1. **Istio Components Not Running**:
   - **Check Istio Pods**:
     ```bash
     kubectl get pods -n istio-system
     ```
   - **View Logs**:
     ```bash
     kubectl logs <istio-pod-name> -n istio-system
     ```
   - **Solutions**:
     - Ensure Istio is correctly installed.
     - Verify configuration files for syntax errors.

2. **Monitoring Tools Not Accessible**:
   - **Symptoms**: Unable to access Prometheus, Grafana, or Jaeger dashboards.
   - **Solutions**:
     - Check the service types and ensure port forwarding or ingress is correctly set up.
     - Verify that the pods are running without errors.

3. **PostgreSQL StatefulSet Issues**:
   - **Symptoms**: PostgreSQL pods not starting, data not persisting.
   - **Solutions**:
     - Ensure PersistentVolumeClaims are correctly bound.
     - Check logs for PostgreSQL pods:
       ```bash
       kubectl logs <postgresql-pod-name> -n laboratory-swarm
       ```

4. **Network Connectivity Problems**:
   - **Symptoms**: Services cannot communicate as expected.
   - **Solutions**:
     - Verify NetworkPolicies are correctly configured.
     - Use `kubectl exec` to test connectivity between pods.

### Debugging Steps

1. **Check Pod Status**:
   - Use `kubectl get pods` to verify that all pods are in the `Running` state.

2. **Inspect Logs**:
   - Use `kubectl logs` to view logs of individual pods for error messages.

3. **Verify Configurations**:
   - Ensure that all YAML manifests are correctly applied and contain no syntax errors.

4. **Network Tests**:
   - Use tools like `curl`, `wget`, or `nc` within pods to test service connectivity.

## Further Reading

- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
- [Istio Service Mesh Documentation](https://istio.io/latest/docs/)
- [Prometheus Monitoring Documentation](https://prometheus.io/docs/introduction/overview/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jaeger Tracing Documentation](https://www.jaegertracing.io/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

---

## Links

- [Root Documentation](../README.md)
- [Istio Configuration Documentation](istio/README.md)
- [Kubernetes Monitoring Tools Documentation](kubernetes/README.md)
- [StatefulSets Documentation](statefulset/README.md)


---

If you encounter any issues or have questions regarding the Infrastructure component, please refer to the [Troubleshooting](#troubleshooting) section or reach out to the project maintainers.