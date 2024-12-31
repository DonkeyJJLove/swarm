# Server Documentation

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
  - [API Service](#api-service)
  - [Authentication Service](#authentication-service)
  - [Data Processing Service](#data-processing-service)
- [Deployment](#deployment)
  - [Prerequisites](#prerequisites)
  - [Deploying the Server](#deploying-the-server)
    - [Using Kubernetes Manifests](#using-kubernetes-manifests)
    - [Using Helm](#using-helm)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Configuration Files](#configuration-files)
  - [Secrets Management](#secrets-management)
- [Monitoring](#monitoring)
  - [Metrics Collection](#metrics-collection)
  - [Logging](#logging)
- [Security](#security)
  - [Authentication and Authorization](#authentication-and-authorization)
  - [Data Encryption](#data-encryption)
  - [Input Validation](#input-validation)
- [Scalability and Performance](#scalability-and-performance)
  - [Auto-Scaling](#auto-scaling)
  - [Load Balancing](#load-balancing)
  - [Caching Strategies](#caching-strategies)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Debugging Steps](#debugging-steps)
- [Testing](#testing)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests)
  - [End-to-End Tests](#end-to-end-tests)
- [CI/CD Integration](#ci-cd-integration)
- [Best Practices](#best-practices)
- [Further Reading](#further-reading)
- [Links](#links)

---

## Overview

The **Server** component of the Laboratory Swarm Application serves as the backbone for handling drone telemetry data, managing API endpoints, authenticating users, and processing data to provide actionable insights. This documentation provides a comprehensive guide to deploying, configuring, securing, and maintaining the server-side services to ensure optimal performance and reliability.

## Architecture

![Server Architecture](./architecture.png)

*Figure: High-level architecture of the Server component.*

The server architecture comprises multiple microservices, each responsible for specific functionalities:

- **API Service**: Exposes RESTful endpoints for data ingestion and retrieval.
- **Authentication Service**: Manages user authentication and authorization.
- **Data Processing Service**: Processes incoming telemetry data and stores it in the database.

These services communicate with each other and other infrastructure components like PostgreSQL and Istio Service Mesh to ensure seamless data flow and security.

## Components

### API Service

The **API Service** is responsible for handling HTTP requests from clients, validating input data, and forwarding telemetry data to the Data Processing Service.

- **Technology Stack**:
  - **Language**: Go
  - **Framework**: Gin
  - **Database**: PostgreSQL
- **Key Features**:
  - RESTful API endpoints for data ingestion.
  - Input validation and error handling.
  - Integration with Authentication Service for secure access.

### Authentication Service

The **Authentication Service** manages user authentication, issuing JWT tokens, and enforcing authorization policies.

- **Technology Stack**:
  - **Language**: Node.js
  - **Framework**: Express
  - **Authentication**: JWT (JSON Web Tokens)
- **Key Features**:
  - User registration and login.
  - Token generation and validation.
  - Role-based access control integration.

### Data Processing Service

The **Data Processing Service** handles the processing and storage of telemetry data received from drones.

- **Technology Stack**:
  - **Language**: Python
  - **Framework**: FastAPI
  - **Database**: PostgreSQL
- **Key Features**:
  - Data validation and transformation.
  - Batch processing and real-time analytics.
  - Interaction with PostgreSQL for data persistence.

## Deployment

### Prerequisites

Before deploying the Server component, ensure the following prerequisites are met:

- **Kubernetes Cluster**: A functional Kubernetes cluster (v1.18+).
- **Istio Service Mesh**: Installed and configured on the cluster.
- **Kubectl**: The Kubernetes command-line tool is installed and configured.
- **Helm**: (Optional) Helm package manager installed for easier deployment.
- **Namespace Labels**: Ensure that the `server` namespace is labeled for Istio injection if automatic sidecar injection is enabled.

  ```bash
  kubectl label namespace server istio-injection=enabled
  ```

- **TLS Certificates**: Create Kubernetes Secrets containing TLS certificates for secure communication.

  **Example**:

  ```bash
  kubectl create -n server secret tls api-service-cert --key=path/to/api.key --cert=path/to/api.crt
  kubectl create -n server secret tls auth-service-cert --key=path/to/auth.key --cert=path/to/auth.crt
  kubectl create -n server secret tls data-processing-cert --key=path/to/data.key --cert=path/to/data.crt
  ```

### Deploying the Server

You can deploy the Server component using **Kubernetes Manifests** or **Helm Charts**. Below are the steps for both methods.

#### Using Kubernetes Manifests

1. **Navigate to the Server Configuration Directory**:

   ```bash
   cd infrastructure/server/manifests
   ```

2. **Apply the API Service Manifest**:

   ```bash
   kubectl apply -f api-service.yaml
   ```

3. **Apply the Authentication Service Manifest**:

   ```bash
   kubectl apply -f auth-service.yaml
   ```

4. **Apply the Data Processing Service Manifest**:

   ```bash
   kubectl apply -f data-processing-service.yaml
   ```

5. **Verify the Deployment**:

   ```bash
   kubectl get pods -n server
   kubectl get services -n server
   ```

   *Ensure that all Server pods are running without errors and that services are correctly exposed.*

#### Using Helm

1. **Add the Server Helm Repository**:

   *(Assuming a custom Helm repository is set up)*

   ```bash
   helm repo add server-repo https://charts.labswarm.example.com
   helm repo update
   ```

2. **Install the API Service**:

   ```bash
   helm install api-service server-repo/api-service \
     --namespace server \
     --create-namespace \
     --set image.repository=registry.labswarm.example.com/api-service \
     --set image.tag=v1.0.0 \
     --set replicaCount=3
   ```

3. **Install the Authentication Service**:

   ```bash
   helm install auth-service server-repo/auth-service \
     --namespace server \
     --set image.repository=registry.labswarm.example.com/auth-service \
     --set image.tag=v1.0.0 \
     --set replicaCount=2
   ```

4. **Install the Data Processing Service**:

   ```bash
   helm install data-processing-service server-repo/data-processing-service \
     --namespace server \
     --set image.repository=registry.labswarm.example.com/data-processing-service \
     --set image.tag=v1.0.0 \
     --set replicaCount=2
   ```

5. **Verify the Deployment**:

   ```bash
   kubectl get pods -n server
   kubectl get services -n server
   ```

   *Ensure that all Server pods are running without errors and that services are correctly exposed.*

## Configuration

### Environment Variables

Each service requires specific environment variables for configuration. These are typically sourced from Kubernetes Secrets for security.

**API Service Environment Variables:**

```yaml
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: postgresql-secret
        key: database-url
  - name: AUTH_SERVICE_URL
    value: "https://auth-service.server.svc.cluster.local"
  - name: JWT_SECRET
    valueFrom:
      secretKeyRef:
        name: auth-service-secret
        key: jwt-secret
```

**Authentication Service Environment Variables:**

```yaml
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: postgresql-secret
        key: database-url
  - name: JWT_SECRET
    valueFrom:
      secretKeyRef:
        name: auth-service-secret
        key: jwt-secret
  - name: TOKEN_EXPIRY
    value: "3600" # in seconds
```

**Data Processing Service Environment Variables:**

```yaml
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: postgresql-secret
        key: database-url
  - name: DATA_STORAGE_PATH
    value: "/data/storage"
  - name: PROCESSING_THREADS
    value: "4"
```

### Configuration Files

Configuration files define the behavior and settings for each service. These files should be version-controlled and managed securely.

**API Service Configuration (`api-config.yaml`):**

```yaml
server:
  port: 8080
  readTimeout: 10s
  writeTimeout: 10s
logging:
  level: INFO
  format: json
```

**Authentication Service Configuration (`auth-config.yaml`):**

```yaml
server:
  port: 9090
  readTimeout: 5s
  writeTimeout: 5s
logging:
  level: DEBUG
  format: text
jwt:
  issuer: "labswarm"
  expiry: 3600 # in seconds
```

**Data Processing Service Configuration (`data-processing-config.yaml`):**

```yaml
server:
  port: 7070
  readTimeout: 15s
  writeTimeout: 15s
logging:
  level: INFO
  format: json
processing:
  batchSize: 100
  enableRealTime: true
```

### Secrets Management

Sensitive information such as database credentials, JWT secrets, and TLS certificates should be stored securely using Kubernetes Secrets.

**Creating a Secret:**

```bash
kubectl create secret generic postgresql-secret \
  --from-literal=database-url="postgres://postgres:YourSecurePassword@postgresql.server.svc.cluster.local:5432/laboratory_swarm" \
  -n server
```

**Accessing Secrets in Pods:**

```yaml
volumeMounts:
  - name: postgresql-secret
    mountPath: /etc/secrets
    readOnly: true
volumes:
  - name: postgresql-secret
    secret:
      secretName: postgresql-secret
```

## Monitoring

Effective monitoring ensures the Server component operates reliably and efficiently.

### Metrics Collection

Metrics are collected using Prometheus to monitor the health and performance of each service.

- **API Service Metrics**:
  - Request rates
  - Response times
  - Error rates

- **Authentication Service Metrics**:
  - Authentication success/failure rates
  - Token issuance rates

- **Data Processing Service Metrics**:
  - Processing throughput
  - Queue lengths
  - Resource utilization

**Prometheus Configuration Example:**

```yaml
scrape_configs:
  - job_name: 'api-service'
    static_configs:
      - targets: ['api-service.server.svc.cluster.local:8080']
  
  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth-service.server.svc.cluster.local:9090']
  
  - job_name: 'data-processing-service'
    static_configs:
      - targets: ['data-processing-service.server.svc.cluster.local:7070']
```

### Logging

Centralized logging is implemented using Fluentd to aggregate logs from all server services.

- **Log Aggregation**:
  - Collect logs from API, Authentication, and Data Processing services.
  - Forward logs to a centralized logging system like Elasticsearch or Loki.

**Fluentd Configuration Example:**

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

## Security

Ensuring the security of the Server component is critical to protect sensitive data and maintain system integrity.

### Authentication and Authorization

- **API Service**:
  - Requires JWT tokens for accessing protected endpoints.
  - Integrates with the Authentication Service to validate tokens.

- **Authentication Service**:
  - Manages user credentials and token issuance.
  - Implements role-based access controls to restrict access to sensitive operations.

- **Data Processing Service**:
  - Restricts access to authorized services and users.
  - Validates data integrity before processing.

**Example Authorization Middleware (API Service):**

```go
func AuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        tokenString := c.GetHeader("Authorization")
        if tokenString == "" {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Authorization header missing"})
            return
        }
        token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
            return []byte(os.Getenv("JWT_SECRET")), nil
        })
        if err != nil || !token.Valid {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
            return
        }
        c.Next()
    }
}
```

### Data Encryption

- **Encryption at Rest**:
  - PostgreSQL data is stored on encrypted PersistentVolumes.
  - Use storage classes that support encryption provided by the cloud provider or storage backend.

- **Encryption in Transit**:
  - All inter-service communication is secured using TLS.
  - Services are configured to use HTTPS for external communications.

**Example PostgreSQL TLS Configuration:**

```yaml
env:
  - name: POSTGRES_SSLMODE
    value: "verify-full"
  - name: POSTGRES_SSLROOTCERT
    value: "/var/lib/postgresql/server.crt"
volumeMounts:
  - name: postgresql-tls
    mountPath: /var/lib/postgresql/
    readOnly: true
volumes:
  - name: postgresql-tls
    secret:
      secretName: postgresql-tls
```

### Input Validation

- **API Service**:
  - Implements strict input validation to prevent injection attacks and ensure data integrity.
  
**Example Input Validation (API Service):**

```go
func CreateTelemetry(c *gin.Context) {
    var telemetry Telemetry
    if err := c.ShouldBindJSON(&telemetry); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }
    // Additional validation logic
    // ...
}
```

## Scalability and Performance

Ensuring that the Server component can scale to handle increasing loads is essential for maintaining performance.

### Auto-Scaling

Implement Horizontal Pod Autoscalers (HPA) to automatically scale the number of pod replicas based on CPU utilization or custom metrics.

**Example HPA Configuration:**

```yaml
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: api-service-hpa
  namespace: server
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Load Balancing

Use Istio's built-in load balancing capabilities to distribute traffic evenly across service replicas, ensuring high availability and optimal resource utilization.

**Example Virtual Service for Load Balancing:**

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: api-service
  namespace: server
spec:
  hosts:
    - "api.server.labswarm.example.com"
  gateways:
    - ingress-gateway.server
  http:
    - route:
        - destination:
            host: api-service.server.svc.cluster.local
            port:
              number: 8080
          weight: 100
```

### Caching Strategies

Implement caching mechanisms to reduce latency and improve response times.

- **In-Memory Caching**: Use Redis or Memcached for frequently accessed data.
- **HTTP Caching**: Leverage HTTP cache headers to allow clients and proxies to cache responses.

**Example Redis Deployment for Caching:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:6-alpine
          ports:
            - containerPort: 6379
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "200m"
```

## Troubleshooting

### Common Issues

1. **Service Unavailability**
   - **Symptoms**: API endpoints return 503 errors or are unreachable.
   - **Solutions**:
     - Check the status of service pods.
       ```bash
       kubectl get pods -n server
       ```
     - Inspect service logs for errors.
       ```bash
       kubectl logs <pod-name> -n server
       ```
     - Verify Istio Virtual Service and Gateway configurations.

2. **Authentication Failures**
   - **Symptoms**: Users receive unauthorized errors despite valid credentials.
   - **Solutions**:
     - Ensure JWT tokens are correctly issued and included in requests.
     - Verify the Authentication Service is operational.
     - Check JWT secret configurations.

3. **Data Processing Delays**
   - **Symptoms**: Telemetry data is not processed in a timely manner.
   - **Solutions**:
     - Monitor Data Processing Service metrics for bottlenecks.
     - Scale the Data Processing Service if necessary.
     - Inspect logs for processing errors.

4. **High CPU or Memory Usage**
   - **Symptoms**: Server pods consume excessive resources, leading to performance degradation.
   - **Solutions**:
     - Analyze resource requests and limits.
       ```bash
       kubectl describe deployment api-service -n server
       ```
     - Optimize application code to reduce resource consumption.
     - Implement Horizontal Pod Autoscaling.

### Debugging Steps

1. **Inspect Pod Status and Logs**
   - Check if all server pods are running.
     ```bash
     kubectl get pods -n server
     ```
   - View logs for a specific pod.
     ```bash
     kubectl logs <pod-name> -n server
     ```

2. **Validate Configuration Files**
   - Ensure that all configuration files are correctly applied.
     ```bash
     kubectl get deployment api-service -n server -o yaml
     kubectl get deployment auth-service -n server -o yaml
     kubectl get deployment data-processing-service -n server -o yaml
     ```

3. **Check Network Policies and RBAC**
   - Verify that Network Policies are not blocking necessary traffic.
     ```bash
     kubectl get networkpolicy -n server
     ```
   - Ensure RBAC permissions are correctly set.
     ```bash
     kubectl get rolebinding -n server
     kubectl get clusterrolebinding
     ```

4. **Use Istio Diagnostics**
   - Analyze Istio configurations for issues.
     ```bash
     istioctl analyze
     ```

5. **Monitor Metrics and Alerts**
   - Use Grafana dashboards to identify anomalies.
   - Check Prometheus for alerting rules that may have been triggered.

6. **Test Service Endpoints**
   - Use tools like `curl` or `Postman` to send requests to API endpoints and verify responses.
     ```bash
     curl -X GET https://api.server.labswarm.example.com/api/v1/status -H "Authorization: Bearer <token>"
     ```

## Testing

### Unit Tests

- **Purpose**: Validate individual components and functions within each service.
- **Tools**: Go's `testing` package for API Service, Jest for Authentication Service, PyTest for Data Processing Service.
- **Best Practices**:
  - Achieve high test coverage.
  - Mock external dependencies.
  - Automate test execution in CI pipelines.

### Integration Tests

- **Purpose**: Test interactions between multiple services to ensure they work together as expected.
- **Tools**: Postman Collections, Kubernetes Test Environments.
- **Best Practices**:
  - Use realistic data sets.
  - Isolate tests to prevent interference.
  - Automate within CI/CD workflows.

### End-to-End Tests

- **Purpose**: Validate the entire workflow from data ingestion to processing and retrieval.
- **Tools**: Selenium for UI interactions, custom scripts for API workflows.
- **Best Practices**:
  - Simulate real-world scenarios.
  - Include security and performance tests.
  - Maintain tests alongside application code.

## CI/CD Integration

Automate the build, testing, and deployment processes to ensure rapid and reliable releases.

### Continuous Integration (CI)

- **Pipeline Steps**:
  1. **Code Checkout**: Retrieve code from the repository.
  2. **Build**: Compile and build Docker images for each service.
  3. **Unit Testing**: Run unit tests to validate code changes.
  4. **Static Analysis**: Perform code quality and security scans.
  5. **Push Images**: Push Docker images to a container registry.

### Continuous Deployment (CD)

- **Pipeline Steps**:
  1. **Deploy to Staging**: Apply Kubernetes manifests or Helm charts to a staging environment.
  2. **Integration Testing**: Execute integration and end-to-end tests.
  3. **Manual Approval**: Require manual approval for production deployments.
  4. **Deploy to Production**: Apply Kubernetes manifests or Helm charts to the production environment.
  5. **Monitor Deployment**: Track deployment metrics and roll back if necessary.

**Example GitHub Actions Workflow:**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v2
      
      - name: Set up Go
        uses: actions/setup-go@v2
        with:
          go-version: '1.16'
      
      - name: Build API Service
        run: |
          cd api-service
          go build -o api-service
      
      - name: Run Unit Tests
        run: |
          cd api-service
          go test ./...
      
      - name: Build Docker Image
        run: |
          docker build -t registry.labswarm.example.com/api-service:${{ github.sha }} .
          docker push registry.labswarm.example.com/api-service:${{ github.sha }}
      
      - name: Deploy to Kubernetes
        uses: azure/k8s-deploy@v3
        with:
          manifests: |
            manifests/api-service.yaml
          images: |
            registry.labswarm.example.com/api-service:${{ github.sha }}
          kubectl-version: '1.20.0'
          namespace: server
```

## Best Practices

- **Version Control**: Maintain all configuration files, manifests, and scripts in version control systems like Git.
- **Immutable Infrastructure**: Treat deployments as immutable, avoiding in-place updates to minimize configuration drift.
- **Secrets Management**: Always store sensitive information in Kubernetes Secrets and avoid hardcoding credentials.
- **Automated Testing**: Implement comprehensive automated testing to catch issues early in the development cycle.
- **Resource Optimization**: Monitor and optimize resource allocations to ensure cost-effectiveness and performance.
- **Documentation**: Keep all documentation up-to-date to facilitate onboarding and maintenance.

## Further Reading

- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
- [Istio Service Mesh Documentation](https://istio.io/latest/docs/)
- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [Go Gin Framework Documentation](https://github.com/gin-gonic/gin)
- [Node.js Express Framework Documentation](https://expressjs.com/)
- [Python FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Helm Documentation](https://helm.sh/docs/)
- [Prometheus Monitoring Documentation](https://prometheus.io/docs/introduction/overview/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jaeger Tracing Documentation](https://www.jaegertracing.io/docs/)

## Links

- [Root Documentation](../../README.md)
- [Infrastructure Documentation](../README.md)
- [Security Documentation](../security/README.md)
- [Kubernetes Monitoring Tools Documentation](../kubernetes/README.md)
- [Istio Configuration Documentation](../istio/README.md)
- [Policies Documentation](../istio/policies/README.md)
- [Virtual Services Documentation](../istio/virtualservices/README.md)
- [StatefulSets Documentation](../statefulset/README.md)
- [API Service Documentation](api-service/README.md)
- [Authentication Service Documentation](auth-service/README.md)
- [Data Processing Service Documentation](data-processing-service/README.md)

---

If you encounter any issues or have questions regarding the Server component, please refer to the [Troubleshooting](#troubleshooting) section or reach out to the project maintainers.