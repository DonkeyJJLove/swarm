# Policies Documentation

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
  - [Circuit Breakers](#circuit-breakers)
  - [Rate Limiting](#rate-limiting)
  - [Fault Injection](#fault-injection)
  - [Retries and Timeouts](#retries-and-timeouts)
  - [Mirror Traffic](#mirror-traffic)
- [Deployment](#deployment)
  - [Prerequisites](#prerequisites)
  - [Apply Policy Configurations](#apply-policy-configurations)
- [Configuration](#configuration)
  - [Policy Parameters](#policy-parameters)
- [Monitoring](#monitoring)
  - [Metrics and Telemetry](#metrics-and-telemetry)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Further Reading](#further-reading)
- [Links](#links)

---

## Overview

The **Policies** component within the Istio Service Mesh for the Laboratory Swarm Application encompasses a set of configurations that govern traffic behavior, enhance resilience, and enforce operational standards across microservices. By defining policies such as circuit breakers, rate limiting, fault injection, and retries, you can ensure robust, efficient, and secure communication between services. These policies help in mitigating failures, managing load, and maintaining the overall health of the application.

## Architecture

![Policies Architecture](./architecture.png)

*Figure: High-level architecture of the Policies component.*

Policies operate alongside other Istio configurations like Destination Rules and Virtual Services to control and manage traffic flow within the service mesh. They are crucial for implementing best practices in traffic management, ensuring that services can handle varying loads and recover gracefully from failures.

## Components

### Circuit Breakers

**Circuit Breakers** prevent a service from being overwhelmed by limiting the number of concurrent connections or requests it can handle. They help in maintaining system stability by isolating failing services and preventing cascading failures across the mesh.

- **File**: `policies/circuit-breakers.yaml`

  #### Configuration

  ```yaml
  apiVersion: networking.istio.io/v1alpha3
  kind: DestinationRule
  metadata:
    name: circuit-breaker
    namespace: laboratory-swarm
  spec:
    host: aggregator-api-service.laboratory-swarm.svc.cluster.local
    trafficPolicy:
      connectionPool:
        tcp:
          maxConnections: 100
        http:
          http1MaxPendingRequests: 1000
          maxRequestsPerConnection: 100
      outlierDetection:
        consecutive5xxErrors: 5
        interval: 1s
        baseEjectionTime: 30s
        maxEjectionPercent: 100
  ```

  #### Parameters

  - `connectionPool`: Defines the maximum number of connections and requests.
    - `tcp.maxConnections`: Maximum number of TCP connections.
    - `http.http1MaxPendingRequests`: Maximum number of pending HTTP requests.
    - `http.maxRequestsPerConnection`: Maximum number of requests per HTTP connection.
  - `outlierDetection`: Configures criteria for ejecting unhealthy hosts.
    - `consecutive5xxErrors`: Number of consecutive 5xx errors before ejecting.
    - `interval`: Time interval between ejection evaluations.
    - `baseEjectionTime`: Duration a host remains ejected.
    - `maxEjectionPercent`: Maximum percentage of hosts that can be ejected.

### Rate Limiting

**Rate Limiting** controls the rate of incoming requests to a service, preventing it from being overwhelmed and ensuring fair usage across consumers. It helps in managing traffic spikes and maintaining consistent performance.

- **File**: `policies/rate-limiting.yaml`

  #### Configuration

  ```yaml
  apiVersion: networking.istio.io/v1alpha3
  kind: EnvoyFilter
  metadata:
    name: rate-limit-filter
    namespace: laboratory-swarm
  spec:
    workloadSelector:
      labels:
        app: aggregator-api
    configPatches:
      - applyTo: HTTP_FILTER
        match:
          context: SIDECAR_INBOUND
          listener:
            filterChain:
              filter:
                name: "envoy.http_connection_manager"
        patch:
          operation: INSERT_BEFORE
          value:
            name: envoy.rate_limit
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.rate_limit.v3.RateLimit
              domain: drone_aggregator
              failure_mode_deny: true
              rate_limit_service:
                grpc_service:
                  envoy_grpc:
                    cluster_name: rate_limit_cluster
                  timeout: 0.25s
  ```

  #### Parameters

  - `domain`: Namespace for rate limiting rules.
  - `failure_mode_deny`: Deny requests if rate limit service is unavailable.
  - `rate_limit_service`: Configuration for the external rate limit service.

### Fault Injection

**Fault Injection** allows the simulation of failures within the service mesh, such as delays or aborts, to test the resilience and robustness of services. It is useful for identifying weaknesses and ensuring that services can gracefully handle unexpected failures.

- **File**: `policies/fault-injection.yaml`

  #### Configuration

  ```yaml
  apiVersion: networking.istio.io/v1alpha3
  kind: VirtualService
  metadata:
    name: fault-injection
    namespace: laboratory-swarm
  spec:
    hosts:
      - aggregator-api-service.laboratory-swarm.svc.cluster.local
    http:
      - route:
          - destination:
              host: aggregator-api-service.laboratory-swarm.svc.cluster.local
        fault:
          delay:
            percentage:
              value: 10
            fixedDelay: 5s
          abort:
            percentage:
              value: 5
            httpStatus: 500
  ```

  #### Parameters

  - `fault.delay`: Introduces a fixed delay in responses.
    - `percentage.value`: Percentage of requests to delay.
    - `fixedDelay`: Duration of the delay.
  - `fault.abort`: Aborts requests with a specified HTTP status.
    - `percentage.value`: Percentage of requests to abort.
    - `httpStatus`: HTTP status code to return.

### Retries and Timeouts

**Retries and Timeouts** enhance the reliability of services by specifying how clients should handle transient failures and how long they should wait for responses. Proper configuration ensures that services can recover from temporary issues without overwhelming the system.

- **File**: `policies/retries-timeouts.yaml`

  #### Configuration

  ```yaml
  apiVersion: networking.istio.io/v1alpha3
  kind: DestinationRule
  metadata:
    name: retries-timeouts
    namespace: laboratory-swarm
  spec:
    host: aggregator-api-service.laboratory-swarm.svc.cluster.local
    trafficPolicy:
      connectionPool:
        http:
          http1MaxPendingRequests: 1000
          maxRequestsPerConnection: 100
      retries:
        attempts: 3
        perTryTimeout: 2s
        retryOn: gateway-error,connect-failure,refused-stream
      loadBalancer:
        simple: LEAST_CONN
  ```

  #### Parameters

  - `retries.attempts`: Number of retry attempts.
  - `retries.perTryTimeout`: Timeout for each retry attempt.
  - `retries.retryOn`: Conditions under which retries should occur.
    - `gateway-error`, `connect-failure`, `refused-stream`: Specific error conditions to trigger retries.
  - `connectionPool`: Configures connection pooling settings.
  - `loadBalancer`: Defines the load balancing strategy.

### Mirror Traffic

**Mirror Traffic** duplicates incoming traffic to a secondary service without affecting the primary service's responses. This is useful for testing new service versions or gathering additional telemetry data without impacting production traffic.

- **File**: `policies/mirror-traffic.yaml`

  #### Configuration

  ```yaml
  apiVersion: networking.istio.io/v1alpha3
  kind: VirtualService
  metadata:
    name: mirror-traffic
    namespace: laboratory-swarm
  spec:
    hosts:
      - aggregator-api-service.laboratory-swarm.svc.cluster.local
    http:
      - route:
          - destination:
              host: aggregator-api-service.laboratory-swarm.svc.cluster.local
              subset: stable
        mirror:
          host: aggregator-api-canary-service.laboratory-swarm.svc.cluster.local
          subset: canary
  ```

  #### Parameters

  - `route`: Defines the primary service routing.
  - `mirror.host`: Specifies the secondary service to receive mirrored traffic.
  - `mirror.subset`: Defines the subset of the secondary service.

## Deployment

### Prerequisites

Before deploying the Policies component, ensure the following prerequisites are met:

- **Kubernetes Cluster**: A functional Kubernetes cluster (v1.18+).
- **Istio Service Mesh**: Istio is installed and configured on the cluster.
- **Prometheus Operator**: Installed to manage Prometheus and related custom resources.
- **Kubectl**: The Kubernetes command-line tool is installed and configured.
- **Namespace Labels**: Ensure that the `laboratory-swarm` namespace is labeled for Istio injection if automatic sidecar injection is enabled.

  ```bash
  kubectl label namespace laboratory-swarm istio-injection=enabled
  ```

### Apply Policy Configurations

Deploy the Policy configurations by applying the YAML manifests located within the `infrastructure/istio/policies` directory.

1. **Navigate to the Policies Configuration Directory**:

   ```bash
   cd infrastructure/istio/policies
   ```

2. **Apply the Circuit Breakers Manifest**:

   ```bash
   kubectl apply -f circuit-breakers.yaml
   ```

3. **Apply the Rate Limiting Manifest**:

   ```bash
   kubectl apply -f rate-limiting.yaml
   ```

4. **Apply the Fault Injection Manifest**:

   ```bash
   kubectl apply -f fault-injection.yaml
   ```

5. **Apply the Retries and Timeouts Manifest**:

   ```bash
   kubectl apply -f retries-timeouts.yaml
   ```

6. **Apply the Mirror Traffic Manifest**:

   ```bash
   kubectl apply -f mirror-traffic.yaml
   ```

7. **Verify the Deployment**:

   ```bash
   kubectl get envoyfilters -n laboratory-swarm
   kubectl get virtualservices -n laboratory-swarm
   kubectl get destinationrules -n laboratory-swarm
   ```

   *Ensure that all policy configurations are applied correctly without errors.*

## Configuration

### Policy Parameters

Each policy type consists of specific parameters that define its behavior and impact on traffic management. Understanding these parameters is crucial for effective policy implementation.

- **Circuit Breakers**:
  - `maxConnections`: Limits the number of concurrent connections.
  - `http1MaxPendingRequests`: Caps the number of pending HTTP requests.
  - `maxRequestsPerConnection`: Sets the maximum number of requests per connection.
  - `consecutive5xxErrors`: Number of consecutive 5xx errors before ejecting a host.
  - `interval`: Time interval between ejection evaluations.
  - `baseEjectionTime`: Duration a host remains ejected.
  - `maxEjectionPercent`: Maximum percentage of hosts that can be ejected.

- **Rate Limiting**:
  - `domain`: Namespace for rate limiting rules.
  - `failure_mode_deny`: Deny requests if the rate limit service is unavailable.
  - `rate_limit_service`: Configuration for the external rate limit service.
    - `grpc_service.cluster_name`: Name of the gRPC cluster for the rate limit service.
    - `timeout`: Timeout for rate limit service responses.

- **Fault Injection**:
  - `fault.delay.percentage.value`: Percentage of requests to delay.
  - `fault.delay.fixedDelay`: Duration of the delay.
  - `fault.abort.percentage.value`: Percentage of requests to abort.
  - `fault.abort.httpStatus`: HTTP status code to return upon aborting.

- **Retries and Timeouts**:
  - `retries.attempts`: Number of retry attempts.
  - `retries.perTryTimeout`: Timeout for each retry attempt.
  - `retries.retryOn`: Conditions under which retries should occur.
  - `connectionPool.http.http1MaxPendingRequests`: Maximum number of pending HTTP requests.
  - `connectionPool.http.maxRequestsPerConnection`: Maximum number of requests per connection.
  - `loadBalancer.simple`: Load balancing strategy (`ROUND_ROBIN`, `LEAST_CONN`, etc.).

- **Mirror Traffic**:
  - `route.destination.host`: Primary service host.
  - `mirror.host`: Secondary service host for mirroring.
  - `mirror.subset`: Subset of the secondary service to receive mirrored traffic.

**Example Circuit Breakers Configuration**:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: circuit-breaker
  namespace: laboratory-swarm
spec:
  host: aggregator-api-service.laboratory-swarm.svc.cluster.local
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 1000
        maxRequestsPerConnection: 100
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 1s
      baseEjectionTime: 30s
      maxEjectionPercent: 100
```

## Monitoring

Policies significantly impact how traffic behaves within the service mesh. Monitoring these policies ensures they function as intended and helps in identifying and resolving issues promptly.

### Metrics and Telemetry

Istio Policies emit various metrics that can be collected and visualized using Prometheus and Grafana:

- **Circuit Breakers**:
  - `istio_requests_total`: Total number of requests.
  - `istio_requests_duration_seconds`: Duration of requests.
  - `istio_tcp_connections_opened_total`: Number of open TCP connections.
  - `istio_tcp_connections_closed_total`: Number of closed TCP connections.

- **Rate Limiting**:
  - `envoy_cluster_rate_limit_service`: Metrics related to rate limit service responses.
  - `istio_requests_total`: Monitors the number of requests being rate limited.

- **Fault Injection**:
  - `istio_requests_total`: Total number of requests, including those affected by fault injection.
  - `istio_requests_duration_seconds`: Duration of requests with induced delays.

- **Retries and Timeouts**:
  - `istio_retries_total`: Total number of retry attempts.
  - `istio_request_duration_seconds`: Duration of requests, including retries.

- **Mirror Traffic**:
  - `istio_requests_total`: Monitors mirrored traffic alongside primary traffic.
  - `istio_requests_mirror_total`: Specific metrics for mirrored requests.

**Grafana Dashboards**:

- **Circuit Breaker Dashboard**: Visualizes connection pool metrics and outlier detection events.
- **Rate Limiting Dashboard**: Shows the rate of incoming requests and rate-limited requests.
- **Fault Injection Dashboard**: Displays the impact of injected faults on request durations and error rates.
- **Retries Dashboard**: Monitors retry attempts and their success rates.
- **Mirror Traffic Dashboard**: Compares primary and mirrored traffic flows.

Ensure that Prometheus is configured to scrape these metrics and that Grafana dashboards are set up to visualize them effectively.

## Security

Policies contribute to the overall security and reliability of the service mesh by enforcing traffic management rules and preventing abuse.

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

Policies work in tandem with Kubernetes RBAC to ensure that only authorized entities can modify traffic management rules and access sensitive services.

- **Least Privilege**: Grant only necessary permissions to service accounts managing policies.
- **Audit Trails**: Implement auditing to track changes to policy configurations for compliance and security reviews.

## Troubleshooting

### Common Issues

1. **Policy Not Enforcing as Expected**:
   - **Symptoms**: Traffic is not being managed according to the defined policies.
   - **Solutions**:
     - Verify that the policies are correctly applied using `kubectl get destinationrules -n laboratory-swarm`.
     - Check for typos or syntax errors in the YAML manifests.
     - Use Istio’s diagnostic tools to analyze configurations:
       
       ```bash
       istioctl analyze
       ```

2. **Circuit Breaker Not Ejecting Unhealthy Hosts**:
   - **Symptoms**: Hosts continue to receive traffic despite failures.
   - **Solutions**:
     - Ensure that Prometheus is collecting the necessary metrics.
     - Confirm that outlier detection parameters are correctly set.
     - Inspect Istio sidecar proxy logs for outlier detection events.

3. **Rate Limiting Not Applying Correctly**:
   - **Symptoms**: Requests are not being limited as defined.
   - **Solutions**:
     - Verify that the rate limiting service is operational and reachable.
     - Check the `EnvoyFilter` configurations for correctness.
     - Ensure that the `domain` in the rate limiting configuration matches the rate limit service setup.

4. **Fault Injection Causing Unexpected Behavior**:
   - **Symptoms**: Services experiencing unintended delays or aborts.
   - **Solutions**:
     - Review the fault injection configuration for correct percentages and conditions.
     - Monitor the impacted services to ensure that fault injection is only affecting intended traffic.
     - Disable fault injection temporarily to isolate the issue.

5. **Retries Leading to Increased Load**:
   - **Symptoms**: Higher-than-expected traffic due to retries.
   - **Solutions**:
     - Adjust retry parameters to prevent excessive retries.
     - Implement exponential backoff strategies.
     - Monitor retry metrics to identify patterns and optimize configurations.

### Debugging Steps

1. **Inspect Policy Configurations**:
   - Retrieve and review the current policy configurations to ensure they are correctly defined.
     
     ```bash
     kubectl get destinationrule circuit-breaker -n laboratory-swarm -o yaml
     kubectl get envoyfilter rate-limit-filter -n laboratory-swarm -o yaml
     kubectl get virtualservice fault-injection -n laboratory-swarm -o yaml
     kubectl get virtualservice mirror-traffic -n laboratory-swarm -o yaml
     ```

2. **Check Pod Status and Logs**:
   - Verify that all policy-related pods (e.g., rate limit service) are running without errors.
     
     ```bash
     kubectl get pods -n laboratory-swarm
     kubectl logs <pod-name> -n laboratory-swarm
     ```

3. **Validate Metrics Collection**:
   - Ensure that Prometheus is scraping the necessary metrics to support policy evaluations.
   - Use Prometheus' expression browser to query relevant metrics.

4. **Use Istio’s Diagnostic Tools**:
   - Analyze the overall Istio configuration for inconsistencies or conflicts.
     
     ```bash
     istioctl analyze
     ```

5. **Test Policy Effects**:
   - Simulate traffic patterns to observe how policies like rate limiting and circuit breakers respond.
   - Use tools like `curl`, `hey`, or `fortio` to generate test traffic.

6. **Review Alertmanager Notifications**:
   - Ensure that alerts related to policies (e.g., high error rates) are being correctly triggered and routed.
   - Check Alertmanager logs and receiver configurations.

## Further Reading

- [Istio Policies Documentation](https://istio.io/latest/docs/concepts/policy-and-telemetry/)
- [Prometheus Rate Limiting](https://istio.io/latest/docs/tasks/policy-enforcement/rate-limiting/)
- [Istio Circuit Breakers](https://istio.io/latest/docs/concepts/policy-and-telemetry/#circuit-breakers)
- [Fault Injection in Istio](https://istio.io/latest/docs/tasks/traffic-management/fault-injection/)
- [Retries and Timeouts in Istio](https://istio.io/latest/docs/tasks/traffic-management/retries-timeouts/)
- [Mirroring Traffic in Istio](https://istio.io/latest/docs/tasks/traffic-management/mirroring/)
- [Istio EnvoyFilter Documentation](https://istio.io/latest/docs/reference/config/networking/envoy-filter/)
- [Kubernetes RBAC Documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

## Links

- [Istio Configuration Documentation](../README.md)
- [Alert Rules Documentation](../alertrules/README.md)
- [Destination Rules Documentation](../destinationrules/README.md)
- [Gateways Documentation](../gateways/README.md)
- [Virtual Services Documentation](../virtualservices/README.md)
- [Kubernetes Monitoring Tools Documentation](../../kubernetes/README.md)
- [StatefulSets Documentation](../../statefulset/README.md)

---

If you encounter any issues or have questions regarding the Policies component, please refer to the [Troubleshooting](#troubleshooting) section or reach out to the project maintainers.