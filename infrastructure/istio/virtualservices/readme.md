# Virtual Services Documentation

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
  - [Swarm Virtual Service](#swarm-virtual-service)
  - [Aggregator Virtual Service](#aggregator-virtual-service)
- [Deployment](#deployment)
  - [Prerequisites](#prerequisites)
  - [Apply Virtual Services Configurations](#apply-virtual-services-configurations)
- [Configuration](#configuration)
  - [Virtual Service Parameters](#virtual-service-parameters)
- [Monitoring](#monitoring)
  - [Metrics and Telemetry](#metrics-and-telemetry)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Further Reading](#further-reading)
- [Links](#links)

---

## Overview

The **Virtual Services** component within the Istio Service Mesh for the Laboratory Swarm Application defines the traffic routing rules that control how requests are directed to various services. Virtual Services enable advanced traffic management capabilities such as traffic splitting, fault injection, retries, timeouts, and mirroring. By configuring Virtual Services, you can achieve fine-grained control over the flow of traffic within your microservices architecture, enhancing both performance and reliability.

## Architecture

![Virtual Services Architecture](./architecture.png)

*Figure: High-level architecture of the Virtual Services component.*

Virtual Services operate in tandem with other Istio configurations like Gateways and Destination Rules to manage the flow of traffic. They allow you to define how requests are routed to services, enabling scenarios like A/B testing, canary deployments, and traffic mirroring for testing new service versions without impacting production traffic.

## Components

### Swarm Virtual Service

The **Swarm Virtual Service** manages traffic routing for the main application services within the Laboratory Swarm Application. It defines rules for directing incoming requests to different versions of services, enabling controlled rollouts and testing.

- **File**: `virtualservices/swarm-virtualservice.yaml`

  #### Configuration

  ```yaml
  apiVersion: networking.istio.io/v1alpha3
  kind: VirtualService
  metadata:
    name: swarm-virtualservice
    namespace: laboratory-swarm
  spec:
    hosts:
      - "*"
    gateways:
      - ingress-gateway.laboratory-swarm
    http:
      - match:
          - uri:
              prefix: /api/v1/
        route:
          - destination:
              host: aggregator-api-service.laboratory-swarm.svc.cluster.local
              subset: v1
            weight: 90
          - destination:
              host: aggregator-api-service.laboratory-swarm.svc.cluster.local
              subset: v2
            weight: 10
        retries:
          attempts: 3
          perTryTimeout: 2s
          retryOn: gateway-error,connect-failure,refused-stream
      - match:
          - uri:
              prefix: /api/v2/
        route:
          - destination:
              host: aggregator-api-service.laboratory-swarm.svc.cluster.local
              subset: v2
    ```

  #### Parameters

  - `hosts`: Specifies the services to which the Virtual Service applies. Using `"*"` allows it to match any host.
  - `gateways`: Associates the Virtual Service with specific gateways, such as the Ingress Gateway.
  - `http`: Defines HTTP routing rules.
    - `match.uri.prefix`: Matches requests based on the URI prefix.
    - `route.destination.host`: Specifies the target service.
    - `route.destination.subset`: Targets a specific subset (version) of the service.
    - `weight`: Distributes traffic between different subsets.
    - `retries`: Configures retry policies for transient failures.

### Aggregator Virtual Service

The **Aggregator Virtual Service** manages traffic routing for the Aggregator API, enabling features like fault injection, traffic mirroring, and traffic shifting. This facilitates testing and ensures the Aggregator API remains resilient under various conditions.

- **File**: `virtualservices/aggregator-virtualservice.yaml`

  #### Configuration

  ```yaml
  apiVersion: networking.istio.io/v1alpha3
  kind: VirtualService
  metadata:
    name: aggregator-virtualservice
    namespace: laboratory-swarm
  spec:
    hosts:
      - "aggregator-api-service.laboratory-swarm.svc.cluster.local"
    gateways:
      - ingress-gateway.laboratory-swarm
    http:
      - match:
          - uri:
              prefix: /api/data
        route:
          - destination:
              host: aggregator-api-service.laboratory-swarm.svc.cluster.local
              subset: stable
        fault:
          delay:
            percentage:
              value: 5
            fixedDelay: 2s
          abort:
            percentage:
              value: 2
            httpStatus: 500
      - match:
          - uri:
              prefix: /api/test
        route:
          - destination:
              host: aggregator-api-canary-service.laboratory-swarm.svc.cluster.local
              subset: canary
        mirror:
          host: aggregator-api-canary-service.laboratory-swarm.svc.cluster.local
          subset: canary
    ```

  #### Parameters

  - `hosts`: Specifies the target service for the Virtual Service.
  - `gateways`: Associates the Virtual Service with specific gateways.
  - `http`: Defines HTTP routing rules.
    - `match.uri.prefix`: Matches requests based on the URI prefix.
    - `route.destination.host`: Specifies the primary target service.
    - `route.destination.subset`: Targets a specific subset (version) of the service.
    - `fault`: Injects faults into the traffic flow to simulate failures.
      - `delay`: Introduces artificial delays.
        - `percentage.value`: Percentage of requests to delay.
        - `fixedDelay`: Duration of the delay.
      - `abort`: Aborts requests with specified HTTP status codes.
        - `percentage.value`: Percentage of requests to abort.
        - `httpStatus`: HTTP status code to return upon aborting.
    - `mirror`: Duplicates traffic to a secondary service for testing purposes without affecting the primary service's responses.

## Deployment

### Prerequisites

Before deploying Virtual Services, ensure the following prerequisites are met:

- **Kubernetes Cluster**: A functional Kubernetes cluster (v1.18+).
- **Istio Service Mesh**: Istio is installed and configured on the cluster.
- **Kubectl**: The Kubernetes command-line tool is installed and configured.
- **Namespace Labels**: Ensure that the `laboratory-swarm` namespace is labeled for Istio injection if automatic sidecar injection is enabled.

  ```bash
  kubectl label namespace laboratory-swarm istio-injection=enabled
  ```

### Apply Virtual Services Configurations

Deploy the Virtual Services by applying the YAML manifests located within the `infrastructure/istio/virtualservices` directory.

1. **Navigate to the Virtual Services Configuration Directory**:

   ```bash
   cd infrastructure/istio/virtualservices
   ```

2. **Apply the Swarm Virtual Service Manifest**:

   ```bash
   kubectl apply -f swarm-virtualservice.yaml
   ```

3. **Apply the Aggregator Virtual Service Manifest**:

   ```bash
   kubectl apply -f aggregator-virtualservice.yaml
   ```

4. **Verify the Deployment**:

   ```bash
   kubectl get virtualservices -n laboratory-swarm
   ```

   You should see both `swarm-virtualservice` and `aggregator-virtualservice` listed among the VirtualServices.

## Configuration

### Virtual Service Parameters

Each Virtual Service consists of several key parameters that define its behavior and impact on traffic management. Understanding these parameters is crucial for effective traffic routing and policy enforcement.

- **hosts**: Specifies the services to which the Virtual Service applies. This can be a specific service or a wildcard (`"*"`).
- **gateways**: Associates the Virtual Service with one or more gateways, such as the Ingress Gateway.
- **http**: Defines HTTP routing rules, which can include matching conditions, routing destinations, fault injections, retries, timeouts, and traffic mirroring.
  - **match**: Specifies the conditions under which the rule applies, such as URI prefixes, headers, or query parameters.
  - **route**: Defines the target destinations for matching traffic, including service subsets and weights for traffic splitting.
  - **fault**: Configures fault injection parameters to simulate failures and test service resilience.
    - **delay**: Introduces artificial delays in responses.
    - **abort**: Aborts requests with specified HTTP status codes.
  - **retries**: Configures retry policies for handling transient failures.
  - **mirror**: Duplicates traffic to a secondary service for testing purposes without impacting the primary service's responses.

**Example Swarm Virtual Service Configuration**:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: swarm-virtualservice
  namespace: laboratory-swarm
spec:
  hosts:
    - "*"
  gateways:
    - ingress-gateway.laboratory-swarm
  http:
    - match:
        - uri:
            prefix: /api/v1/
      route:
        - destination:
            host: aggregator-api-service.laboratory-swarm.svc.cluster.local
            subset: v1
          weight: 90
        - destination:
            host: aggregator-api-service.laboratory-swarm.svc.cluster.local
            subset: v2
          weight: 10
      retries:
        attempts: 3
        perTryTimeout: 2s
        retryOn: gateway-error,connect-failure,refused-stream
    - match:
        - uri:
            prefix: /api/v2/
      route:
        - destination:
            host: aggregator-api-service.laboratory-swarm.svc.cluster.local
            subset: v2
```

## Monitoring

Virtual Services significantly influence the flow of traffic within the service mesh and should be monitored to ensure they are functioning as intended.

### Metrics and Telemetry

Istio Virtual Services emit various metrics that can be collected and visualized using Prometheus and Grafana:

- **Request Metrics**:
  - `istio_requests_total`: Total number of requests processed.
  - `istio_request_duration_seconds`: Duration of requests.
  - `istio_requests_total{response_code=~"5.."}: Number of requests resulting in 5xx errors.
  
- **Retry Metrics**:
  - `istio_retries_total`: Total number of retry attempts.
  - `istio_retries_success`: Number of successful retries.
  - `istio_retries_fail`: Number of failed retries.
  
- **Fault Injection Metrics**:
  - `istio_fault_injections_total`: Total number of fault injections performed.
  - `istio_fault_delays_total`: Total number of delayed responses.
  - `istio_fault_aborts_total`: Total number of aborted responses.
  
- **Traffic Mirroring Metrics**:
  - `istio_mirrored_requests_total`: Total number of mirrored requests.
  
**Grafana Dashboards**:

- **Traffic Routing Dashboard**: Visualizes request distribution across service subsets, success and error rates.
- **Retry and Timeout Dashboard**: Monitors retry attempts, successes, and failures.
- **Fault Injection Dashboard**: Tracks the number and types of fault injections, delays, and aborts.
- **Traffic Mirroring Dashboard**: Compares primary and mirrored traffic metrics to assess the impact of mirrored requests.

Ensure that Prometheus is configured to scrape these metrics and that Grafana dashboards are set up to visualize them effectively.

## Security

Virtual Services enhance the security of the service mesh by enabling controlled and secure traffic management.

### TLS Termination

- **Ingress Gateway**: Handles TLS termination, decrypting incoming HTTPS traffic before routing it to internal services.
- **Egress Gateway**: Ensures that outbound traffic is encrypted, maintaining data integrity and confidentiality.

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

### RBAC Integration

Virtual Services work in tandem with Kubernetes RBAC to ensure that only authorized entities can modify traffic management rules and access sensitive services.

- **Least Privilege**: Grant only necessary permissions to service accounts managing Virtual Services.
- **Audit Trails**: Implement auditing mechanisms to track changes to Virtual Services for compliance and security reviews.

**Example RBAC Configuration**:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: laboratory-swarm
  name: virtualservice-manager
rules:
  - apiGroups: ["networking.istio.io"]
    resources: ["virtualservices"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: virtualservice-manager-binding
  namespace: laboratory-swarm
subjects:
  - kind: User
    name: "istio-admin"
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: virtualservice-manager
  apiGroup: rbac.authorization.k8s.io
```

## Troubleshooting

### Common Issues

1. **Virtual Service Not Routing Traffic Correctly**:
   - **Symptoms**: Requests are not reaching the intended service subsets or services.
   - **Solutions**:
     - Verify the `hosts` and `gateways` fields in the Virtual Service configuration.
     - Ensure that the `subset` names in Virtual Services match those defined in Destination Rules.
     - Check for typos or syntax errors in the YAML manifests.
     - Use Istio’s diagnostic tools to analyze configurations:
       
       ```bash
       istioctl analyze
       ```

2. **Fault Injection Not Working as Expected**:
   - **Symptoms**: No delays or aborts are being introduced despite configurations.
   - **Solutions**:
     - Confirm that the `fault` section is correctly defined in the Virtual Service.
     - Ensure that the percentages are set appropriately and that there is sufficient traffic to observe the faults.
     - Check Istio sidecar proxy logs for any errors related to fault injection.

3. **Retries and Timeouts Not Behaving Properly**:
   - **Symptoms**: Services are not retrying failed requests or experiencing unexpected timeouts.
   - **Solutions**:
     - Verify the `retries` section in the Virtual Service configuration.
     - Ensure that the `perTryTimeout` is set to an appropriate duration.
     - Monitor retry metrics to assess if retries are being attempted.

4. **Traffic Mirroring Causing Performance Issues**:
   - **Symptoms**: Increased load on the mirrored service or degraded performance.
   - **Solutions**:
     - Adjust the `mirror` settings to limit the percentage of mirrored traffic.
     - Monitor the mirrored service’s performance and adjust resources as needed.
     - Temporarily disable traffic mirroring to isolate the issue.

5. **TLS Handshake Failures**:
   - **Symptoms**: Clients cannot establish secure connections with services.
   - **Solutions**:
     - Ensure that TLS certificates are correctly configured and valid.
     - Verify that the `credentialName` in the Virtual Service matches the Kubernetes Secret containing the TLS certificates.
     - Check that the minimum TLS protocol version is supported by clients.

### Debugging Steps

1. **Inspect Virtual Service Configuration**:
   - Retrieve and review the current Virtual Service configuration to ensure it is correctly defined.
     
     ```bash
     kubectl get virtualservice swarm-virtualservice -n laboratory-swarm -o yaml
     kubectl get virtualservice aggregator-virtualservice -n laboratory-swarm -o yaml
     ```

2. **Check Pod Status and Logs**:
   - Verify that all relevant pods are running without errors.
     
     ```bash
     kubectl get pods -n laboratory-swarm
     kubectl logs <pod-name> -n laboratory-swarm
     ```

3. **Validate Istio Configurations**:
   - Use Istio’s `istioctl` tool to validate configurations and identify potential issues.
     
     ```bash
     istioctl validate -f swarm-virtualservice.yaml
     istioctl validate -f aggregator-virtualservice.yaml
     ```

4. **Monitor Metrics**:
   - Use Prometheus and Grafana to monitor request rates, error rates, and other relevant metrics to identify anomalies.
   
5. **Use Istio’s Diagnostic Tools**:
   - Analyze traffic flows and configurations to ensure that Virtual Services are influencing routing as intended.
     
     ```bash
     istioctl proxy-config routes <pod-name> -n laboratory-swarm
     ```

6. **Test Routing Rules**:
   - Use tools like `curl`, `hey`, or `fortio` to generate test traffic and observe how it is routed based on Virtual Service configurations.
   
   **Example**:
   
   ```bash
   curl -I http://<ingress-gateway-external-ip>/api/v1/resource
   ```

7. **Review Network Policies**:
   - Ensure that Kubernetes NetworkPolicies are not inadvertently blocking traffic as per Virtual Service routing.
     
     ```bash
     kubectl get networkpolicy -n laboratory-swarm
     ```

## Further Reading

- [Istio VirtualService Documentation](https://istio.io/latest/docs/reference/config/networking/virtual-service/)
- [Istio Traffic Management](https://istio.io/latest/docs/concepts/traffic-management/)
- [Istio Fault Injection](https://istio.io/latest/docs/tasks/traffic-management/fault-injection/)
- [Istio Retries and Timeouts](https://istio.io/latest/docs/tasks/traffic-management/retries-timeouts/)
- [Istio Traffic Mirroring](https://istio.io/latest/docs/tasks/traffic-management/mirroring/)
- [Prometheus Monitoring for Istio](https://istio.io/latest/docs/tasks/observability/metrics/)
- [Grafana Dashboards for Istio](https://grafana.com/docs/grafana/latest/)
- [Kubernetes RBAC Documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

## Links

- [Istio Configuration Documentation](../README.md)
- [Alert Rules Documentation](../alertrules/README.md)
- [Destination Rules Documentation](../destinationrules/README.md)
- [Gateways Documentation](../gateways/README.md)
- [Policies Documentation](../policies/README.md)
- [Kubernetes Monitoring Tools Documentation](../../kubernetes/README.md)
- [StatefulSets Documentation](../../statefulset/README.md)

---

If you encounter any issues or have questions regarding the Virtual Services component, please refer to the [Troubleshooting](#troubleshooting) section or reach out to the project maintainers.