# Gateways Documentation

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
  - [Ingress Gateway](#ingress-gateway)
  - [Egress Gateway](#egress-gateway)
- [Deployment](#deployment)
  - [Prerequisites](#prerequisites)
  - [Apply Gateway Configurations](#apply-gateway-configurations)
- [Configuration](#configuration)
  - [Gateway Parameters](#gateway-parameters)
- [Monitoring](#monitoring)
  - [Metrics and Telemetry](#metrics-and-telemetry)
- [Security](#security)
  - [TLS Termination](#tls-termination)
  - [Mutual TLS](#mutual-tls)
- [Troubleshooting](#troubleshooting)
- [Further Reading](#further-reading)
- [Links](#links)

---

## Overview

The **Gateways** component within the Istio Service Mesh is crucial for managing ingress and egress traffic in the Laboratory Swarm Application. Gateways define how external traffic enters the service mesh (Ingress Gateway) and how internal services communicate with external services (Egress Gateway). Proper configuration of gateways ensures secure, reliable, and efficient traffic flow, enabling advanced traffic management features such as load balancing, traffic routing, and security policies.

## Architecture

![Gateways Architecture](./architecture.png)

*Figure: High-level architecture of the Istio Gateways component.*

Gateways operate at the edge of the service mesh, handling all incoming and outgoing traffic. The **Ingress Gateway** manages external HTTP/HTTPS requests, routing them to appropriate internal services based on defined Virtual Services. The **Egress Gateway** controls and secures traffic leaving the cluster, enforcing policies and ensuring that outbound communications adhere to security standards.

## Components

### Ingress Gateway

The **Ingress Gateway** is responsible for managing incoming traffic from external clients to the services within the Kubernetes cluster. It acts as the entry point, handling tasks such as TLS termination, traffic routing, and load balancing.

- **File**: `gateways/ingress-gateway.yaml`

  #### Configuration

  ```yaml
  apiVersion: networking.istio.io/v1alpha3
  kind: Gateway
  metadata:
    name: ingress-gateway
    namespace: laboratory-swarm
  spec:
    selector:
      istio: ingressgateway # Use Istio's default ingress gateway
    servers:
      - port:
          number: 80
          name: http
          protocol: HTTP
        hosts:
          - "*"
      - port:
          number: 443
          name: https
          protocol: HTTPS
        tls:
          mode: SIMPLE
          credentialName: ingress-cert # Kubernetes Secret containing TLS cert
          minProtocolVersion: TLSV1_2
        hosts:
          - "*"
  ```

  #### Parameters

  - `selector`: Identifies the Istio ingress gateway deployment.
  - `servers`: Defines the ports and protocols the gateway listens on.
    - **HTTP Server**: Listens on port 80 for unencrypted traffic.
    - **HTTPS Server**: Listens on port 443 for encrypted traffic, using TLS termination with certificates stored in Kubernetes Secrets.

### Egress Gateway

The **Egress Gateway** manages outbound traffic from the Kubernetes cluster to external services. It enforces security policies, monitors traffic, and ensures that outbound communications comply with organizational standards.

- **File**: `gateways/egress-gateway.yaml`

  #### Configuration

  ```yaml
  apiVersion: networking.istio.io/v1alpha3
  kind: Gateway
  metadata:
    name: egress-gateway
    namespace: laboratory-swarm
  spec:
    selector:
      istio: egressgateway # Use Istio's default egress gateway
    servers:
      - port:
          number: 443
          name: https
          protocol: HTTPS
        hosts:
          - "external-service.example.com"
        tls:
          mode: SIMPLE
          credentialName: egress-cert # Kubernetes Secret containing TLS cert
          minProtocolVersion: TLSV1_2
  ```

  #### Parameters

  - `selector`: Identifies the Istio egress gateway deployment.
  - `servers`: Defines the ports and protocols the gateway listens on.
    - **HTTPS Server**: Listens on port 443 for encrypted outbound traffic to specified external hosts, using TLS termination with certificates stored in Kubernetes Secrets.

## Deployment

### Prerequisites

Before deploying Istio Gateways, ensure the following prerequisites are met:

- **Kubernetes Cluster**: A functional Kubernetes cluster (v1.18+).
- **Istio Service Mesh**: Istio is installed and configured on the cluster.
- **Kubectl**: The Kubernetes command-line tool is installed and configured.
- **Namespace Labels**: Ensure that the `laboratory-swarm` namespace is labeled for Istio injection if automatic sidecar injection is enabled.

  ```bash
  kubectl label namespace laboratory-swarm istio-injection=enabled
  ```

- **TLS Certificates**: Create Kubernetes Secrets containing TLS certificates for Ingress and Egress Gateways.

  **Example**:

  ```bash
  kubectl create -n laboratory-swarm secret tls ingress-cert --key=path/to/tls.key --cert=path/to/tls.crt
  kubectl create -n laboratory-swarm secret tls egress-cert --key=path/to/tls.key --cert=path/to/tls.crt
  ```

### Apply Gateway Configurations

Deploy the Gateway configurations by applying the YAML manifests located within the `infrastructure/istio/gateways` directory.

1. **Navigate to the Gateways Configuration Directory**:

   ```bash
   cd infrastructure/istio/gateways
   ```

2. **Apply the Ingress Gateway Manifest**:

   ```bash
   kubectl apply -f ingress-gateway.yaml
   ```

3. **Apply the Egress Gateway Manifest**:

   ```bash
   kubectl apply -f egress-gateway.yaml
   ```

4. **Verify the Deployment**:

   ```bash
   kubectl get gateways -n laboratory-swarm
   kubectl get pods -n istio-system -l istio=ingressgateway
   kubectl get pods -n istio-system -l istio=egressgateway
   ```

   *Ensure that both Ingress and Egress Gateway pods are running without errors.*

## Configuration

### Gateway Parameters

Each Gateway configuration consists of several key parameters that define its behavior:

- **selector**: Determines which Istio Gateway deployment the configuration applies to.
- **servers**: Specifies the ports, protocols, and TLS settings the Gateway listens on.
  - **port.number**: The port number.
  - **port.name**: A unique name for the port.
  - **port.protocol**: The protocol used (`HTTP`, `HTTPS`).
  - **tls**: TLS settings for secure communication.
    - **mode**: Determines the TLS mode (`SIMPLE`, `MUTUAL`, etc.).
    - **credentialName**: References the Kubernetes Secret containing TLS certificates.
    - **minProtocolVersion**: Sets the minimum TLS version (e.g., `TLSV1_2`).
- **hosts**: Defines the hostnames that the Gateway will accept traffic for. Use `"*"` to accept traffic for any host or specify particular domains for stricter control.

**Example Ingress Gateway Configuration**:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: ingress-gateway
  namespace: laboratory-swarm
spec:
  selector:
    istio: ingressgateway
  servers:
    - port:
        number: 80
        name: http
        protocol: HTTP
      hosts:
        - "*"
    - port:
        number: 443
        name: https
        protocol: HTTPS
      tls:
        mode: SIMPLE
        credentialName: ingress-cert
        minProtocolVersion: TLSV1_2
      hosts:
        - "*"
```

## Monitoring

Gateways play a critical role in the traffic flow within the service mesh and should be monitored to ensure they are functioning correctly.

### Metrics and Telemetry

Istio Gateways emit various metrics that can be collected and visualized using Prometheus and Grafana:

- **Request Metrics**: Number of requests, request duration, error rates.
- **Connection Metrics**: Number of active connections, connection duration.
- **TLS Metrics**: TLS handshake success/failure rates, encryption levels.

**Example Prometheus Query**:

```promql
istio_requests_total{destination_service=~"ingress-gateway.*"} 
```

**Grafana Dashboards**:

- **Ingress Gateway Dashboard**: Visualizes incoming traffic, request rates, and error rates.
- **Egress Gateway Dashboard**: Monitors outbound traffic, connection pools, and latency.

Ensure that Prometheus is configured to scrape metrics from Istio Gateways and that Grafana dashboards are set up to visualize these metrics effectively.

## Security

Istio Gateways enhance the security of the Laboratory Swarm Application by managing and enforcing traffic policies at the network edge.

### TLS Termination

- **Ingress Gateway**: Handles TLS termination, decrypting incoming HTTPS traffic before routing it to internal services.
- **Egress Gateway**: Ensures that outbound traffic is encrypted, maintaining data integrity and confidentiality.

**Configuration Highlights**:

- **TLS Mode**: Set to `SIMPLE` for basic TLS termination or `MUTUAL` for mutual TLS.
- **Certificate Management**: TLS certificates are stored securely in Kubernetes Secrets and referenced in Gateway configurations.

### Mutual TLS

- **Purpose**: Ensures that both client and server authenticate each other, providing an additional layer of security.
- **Configuration**: Set the `tls.mode` to `MUTUAL` and provide the necessary client certificates.

**Example**:

```yaml
tls:
  mode: MUTUAL
  credentialName: ingress-mutual-cert
  clientCertificate: /etc/certs/client-cert.pem
  privateKey: /etc/certs/client-key.pem
  caCertificates: /etc/certs/ca-cert.pem
```

**Best Practices**:

- **Use Strong Certificates**: Ensure that TLS certificates use strong encryption standards.
- **Regularly Rotate Certificates**: Implement a certificate rotation strategy to maintain security over time.
- **Restrict Host Access**: Define specific hostnames in Gateway configurations to limit exposure.

## Troubleshooting

### Common Issues

1. **Gateway Not Accepting Traffic**:
   - **Symptoms**: External requests are not reaching internal services.
   - **Solutions**:
     - Verify that the Gateway is correctly deployed and running.
     - Ensure that DNS records point to the Ingress Gateway's external IP.
     - Check Firewall rules and Security Groups to allow traffic on required ports (80, 443).

2. **TLS Handshake Failures**:
   - **Symptoms**: Clients cannot establish a secure connection with the Gateway.
   - **Solutions**:
     - Confirm that TLS certificates are correctly configured and valid.
     - Ensure that the `credentialName` in the Gateway configuration matches the Kubernetes Secret.
     - Verify that the minimum TLS protocol version is supported by clients.

3. **Ingress/Egress Gateway Pod Crashes**:
   - **Symptoms**: Gateway pods are in a CrashLoopBackOff or Failed state.
   - **Solutions**:
     - Inspect pod logs for error messages.
       ```bash
       kubectl logs <gateway-pod-name> -n istio-system
       ```
     - Check resource allocations to ensure sufficient CPU and memory.
     - Validate Gateway YAML configurations for syntax errors.

4. **Traffic Routing Issues**:
   - **Symptoms**: Requests are not being routed to the intended services or endpoints.
   - **Solutions**:
     - Verify that Virtual Services are correctly configured to route traffic through the Gateway.
     - Use Istio’s `istioctl` tool to inspect and validate routing rules.
       ```bash
       istioctl proxy-config routes <pod-name> -n laboratory-swarm
       ```

5. **Egress Traffic Blocked**:
   - **Symptoms**: Services cannot communicate with external endpoints.
   - **Solutions**:
     - Ensure that Egress Gateway is correctly configured and running.
     - Verify NetworkPolicies to allow outbound traffic through the Egress Gateway.
     - Check that Destination Rules for egress traffic are correctly set up.

### Debugging Steps

1. **Inspect Gateway Configuration**:
   - Retrieve the current Gateway configuration to ensure it is correctly defined.
     ```bash
     kubectl get gateway ingress-gateway -n laboratory-swarm -o yaml
     kubectl get gateway egress-gateway -n laboratory-swarm -o yaml
     ```

2. **Check Pod Status and Logs**:
   - Verify that Gateway pods are running without errors.
     ```bash
     kubectl get pods -n istio-system -l istio=ingressgateway
     kubectl logs <ingress-gateway-pod-name> -n istio-system
     ```
   - Similarly, check Egress Gateway pods.
     ```bash
     kubectl get pods -n istio-system -l istio=egressgateway
     kubectl logs <egress-gateway-pod-name> -n istio-system
     ```

3. **Validate TLS Certificates**:
   - Ensure that the TLS certificates referenced in the Gateway configurations are present and valid.
     ```bash
     kubectl get secret ingress-cert -n laboratory-swarm
     kubectl describe secret ingress-cert -n laboratory-swarm
     ```

4. **Use Istio’s Diagnostic Tools**:
   - Analyze Istio configurations for potential issues.
     ```bash
     istioctl analyze
     ```

5. **Test Connectivity**:
   - From an external client, attempt to reach the Ingress Gateway's external IP or domain.
   - Use tools like `curl` to test HTTPS connections.
     ```bash
     curl -k https://<ingress-gateway-external-ip>
     ```

6. **Review Network Policies**:
   - Ensure that NetworkPolicies are not inadvertently blocking traffic to or from the Gateways.
     ```bash
     kubectl get networkpolicy -n laboratory-swarm
     ```

## Further Reading

- [Istio Gateway Documentation](https://istio.io/latest/docs/reference/config/networking/gateway/)
- [Istio Traffic Management](https://istio.io/latest/docs/concepts/traffic-management/)
- [Securing Traffic with Istio](https://istio.io/latest/docs/concepts/security/)
- [Prometheus Metrics for Istio Gateways](https://istio.io/latest/docs/ops/integrations/prometheus/)
- [Istio TLS Best Practices](https://istio.io/latest/docs/tasks/security/authentication/mtls-migration/)
- [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Istioctl Command-Line Tool](https://istio.io/latest/docs/ops/diagnostic-tools/istioctl/)

## Links

- [Istio Configuration Documentation](../README.md)
- [Alert Rules Documentation](alertrules/README.md)
- [Destination Rules Documentation](destinationrules/README.md)
- [Policies Documentation](../policies/README.md)
- [Virtual Services Documentation](../virtualservices/README.md)
- [Kubernetes Monitoring Tools Documentation](../../kubernetes/README.md)
- [StatefulSets Documentation](../../statefulset/README.md)

---

If you encounter any issues or have questions regarding the Gateways component, please refer to the [Troubleshooting](#troubleshooting) section or reach out to the project maintainers.