# StatefulSets Documentation

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
  - [PostgreSQL StatefulSet](#postgresql-statefulset)
  - [Other Stateful Applications](#other-stateful-applications)
- [Deployment](#deployment)
  - [Prerequisites](#prerequisites)
  - [Deploy StatefulSets](#deploy-statefulsets)
    - [Using Kubernetes Manifests](#using-kubernetes-manifests)
    - [Using Helm](#using-helm)
- [Configuration](#configuration)
  - [StatefulSet Parameters](#statefulset-parameters)
  - [Persistent Volume Claims](#persistent-volume-claims)
  - [Headless Services](#headless-services)
- [Monitoring](#monitoring)
  - [Metrics Collection](#metrics-collection)
  - [Logging](#logging)
- [Security](#security)
  - [Access Control](#access-control)
  - [Data Encryption](#data-encryption)
  - [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Debugging Steps](#debugging-steps)
- [Further Reading](#further-reading)
- [Links](#links)

---

## Overview

The **StatefulSets** component within the Infrastructure of the Laboratory Swarm Application manages stateful applications that require stable and unique network identifiers, persistent storage, and ordered deployment and scaling. Unlike Deployments, StatefulSets are specifically designed for applications like databases, where maintaining state across pod restarts and rescheduling is crucial. This documentation focuses primarily on deploying and managing PostgreSQL using StatefulSets, ensuring data persistence and reliability.

## Architecture

![StatefulSets Architecture](./architecture.png)

*Figure: High-level architecture of the StatefulSets component.*

StatefulSets operate alongside other Kubernetes resources such as Services and PersistentVolumeClaims (PVCs) to provide a robust framework for running stateful applications. In the Laboratory Swarm Application, PostgreSQL is deployed using a StatefulSet to ensure data persistence and reliable network identities, facilitating seamless interactions with other components like the Aggregator and Drones.

## Components

### PostgreSQL StatefulSet

The **PostgreSQL StatefulSet** manages the lifecycle of PostgreSQL pods, ensuring that each pod maintains a consistent identity and storage across reschedules and updates. This setup is essential for data integrity and availability in the Laboratory Swarm Application.

- **File**: `statefulset/postgresql-statefulset.yaml`

  #### Configuration

  ```yaml
  apiVersion: apps/v1
  kind: StatefulSet
  metadata:
    name: postgresql
    namespace: laboratory-swarm
  spec:
    serviceName: "postgresql"
    replicas: 3
    selector:
      matchLabels:
        app: postgresql
    template:
      metadata:
        labels:
          app: postgresql
      spec:
        containers:
          - name: postgresql
            image: postgres:13-alpine
            ports:
              - containerPort: 5432
                name: postgres
            env:
              - name: POSTGRES_USER
                valueFrom:
                  secretKeyRef:
                    name: postgresql-secret
                    key: username
              - name: POSTGRES_PASSWORD
                valueFrom:
                  secretKeyRef:
                    name: postgresql-secret
                    key: password
              - name: POSTGRES_DB
                value: "laboratory_swarm"
            volumeMounts:
              - name: postgresql-data
                mountPath: /var/lib/postgresql/data
        terminationGracePeriodSeconds: 10
    volumeClaimTemplates:
      - metadata:
          name: postgresql-data
        spec:
          accessModes: [ "ReadWriteOnce" ]
          storageClassName: "standard"
          resources:
            requests:
              storage: 10Gi
  ```

  #### Parameters

  - `serviceName`: Defines the headless service governing the StatefulSet.
  - `replicas`: Number of PostgreSQL instances to deploy.
  - `selector`: Labels to identify the pods managed by the StatefulSet.
  - `template`: Pod template defining containers, environment variables, ports, and volume mounts.
    - `env`: Environment variables for PostgreSQL configuration, sourced from Kubernetes Secrets for security.
    - `volumeMounts`: Mount points for persistent storage.
  - `volumeClaimTemplates`: Template for PersistentVolumeClaims ensuring each pod has its own storage.

### Other Stateful Applications

While PostgreSQL is the primary focus, the StatefulSets component can manage other stateful applications within the Laboratory Swarm Application that require persistent storage and stable identities. Examples include caching systems, message brokers, or other databases.

- **Example File**: `statefulset/other-statefulapp-statefulset.yaml`

  *(Detailed configurations for additional stateful applications can be added here as needed.)*

## Deployment

### Prerequisites

Before deploying StatefulSets, ensure the following prerequisites are met:

- **Kubernetes Cluster**: A functional Kubernetes cluster (v1.18+).
- **Kubectl**: The Kubernetes command-line tool is installed and configured.
- **Storage Class**: Ensure that a `StorageClass` named `standard` (or as defined in `storageClassName`) exists for dynamic provisioning of PersistentVolumes.
  
  ```bash
  kubectl get storageclass
  ```

- **Secrets**: Create Kubernetes Secrets to store sensitive PostgreSQL credentials.
  
  ```bash
  kubectl create secret generic postgresql-secret \
    --from-literal=username=postgres \
    --from-literal=password=YourSecurePassword \
    -n laboratory-swarm
  ```

### Deploy StatefulSets

#### Using Kubernetes Manifests

1. **Navigate to the StatefulSets Configuration Directory**:

   ```bash
   cd infrastructure/statefulset
   ```

2. **Apply the PostgreSQL StatefulSet Manifest**:

   ```bash
   kubectl apply -f postgresql-statefulset.yaml
   ```

3. **Verify the Deployment**:

   ```bash
   kubectl get statefulsets -n laboratory-swarm
   kubectl get pods -n laboratory-swarm -l app=postgresql
   kubectl get pvc -n laboratory-swarm
   ```

   *Ensure that all PostgreSQL pods are running and that their PersistentVolumeClaims are bound.*

#### Using Helm

*(Optional)* If you prefer using Helm for deployment, you can leverage community charts or create a custom Helm chart for PostgreSQL.

1. **Add the Bitnami Helm Repository**:

   ```bash
   helm repo add bitnami https://charts.bitnami.com/bitnami
   helm repo update
   ```

2. **Install PostgreSQL Using Helm**:

   ```bash
   helm install postgresql bitnami/postgresql \
     --namespace laboratory-swarm \
     --create-namespace \
     --set global.storageClass=standard \
     --set postgresqlUsername=postgres \
     --set postgresqlPassword=YourSecurePassword \
     --set postgresqlDatabase=laboratory_swarm \
     --set replicaCount=3
   ```

3. **Verify the Deployment**:

   ```bash
   kubectl get statefulsets -n laboratory-swarm
   kubectl get pods -n laboratory-swarm -l app.kubernetes.io/name=postgresql
   kubectl get pvc -n laboratory-swarm
   ```

   *Ensure that all PostgreSQL pods are running and that their PersistentVolumeClaims are bound.*

## Configuration

### StatefulSet Parameters

Understanding the key parameters in the StatefulSet configuration is essential for customizing deployments to meet specific requirements.

- **serviceName**: Defines the headless service that governs the StatefulSet. It must be created before the StatefulSet is deployed.
  
  ```yaml
  serviceName: "postgresql"
  ```

- **replicas**: Number of desired pod replicas. For PostgreSQL, a higher number can improve availability but may require additional configuration for clustering.
  
  ```yaml
  replicas: 3
  ```

- **selector**: Labels used to identify the pods managed by the StatefulSet. Must match the labels defined in the pod template.
  
  ```yaml
  selector:
    matchLabels:
      app: postgresql
  ```

- **template**: Pod template defining the container specifications, environment variables, ports, and volume mounts.
  
  - **containers**: Defines the container images, ports, environment variables, and volume mounts.
  
  - **env**: Environment variables for PostgreSQL configuration. Sensitive information like usernames and passwords should be sourced from Kubernetes Secrets.
    
    ```yaml
    env:
      - name: POSTGRES_USER
        valueFrom:
          secretKeyRef:
            name: postgresql-secret
            key: username
      - name: POSTGRES_PASSWORD
        valueFrom:
          secretKeyRef:
            name: postgresql-secret
            key: password
      - name: POSTGRES_DB
        value: "laboratory_swarm"
    ```

  - **volumeMounts**: Mount points for persistent storage.
    
    ```yaml
    volumeMounts:
      - name: postgresql-data
        mountPath: /var/lib/postgresql/data
    ```

- **volumeClaimTemplates**: Templates for PersistentVolumeClaims ensuring each pod has its own storage.
  
  ```yaml
  volumeClaimTemplates:
    - metadata:
        name: postgresql-data
      spec:
        accessModes: [ "ReadWriteOnce" ]
        storageClassName: "standard"
        resources:
          requests:
            storage: 10Gi
  ```

### Persistent Volume Claims

PersistentVolumeClaims (PVCs) are used to request storage resources dynamically. Each pod in a StatefulSet gets its own PVC based on the `volumeClaimTemplates`.

- **Access Modes**:
  - `ReadWriteOnce`: The volume can be mounted as read-write by a single node.

- **Storage Class**:
  - Defines the type of storage provisioned. Ensure that the specified `storageClassName` exists and is suitable for your performance and durability requirements.

### Headless Services

A headless service is required for StatefulSets to manage the network identities of pods.

- **File**: `statefulset/postgresql-service.yaml`

  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: postgresql
    namespace: laboratory-swarm
  spec:
    ports:
      - port: 5432
        name: postgres
    clusterIP: None
    selector:
      app: postgresql
  ```

  #### Parameters

  - `clusterIP: None`: Creates a headless service, enabling direct DNS resolution for each pod.
  - `selector`: Matches the labels defined in the StatefulSet's pod template.

## Monitoring

### Metrics Collection

Monitoring StatefulSets, especially databases like PostgreSQL, is critical for ensuring performance and availability.

- **Prometheus**: Scrapes metrics from PostgreSQL using exporters.
  
  - **PostgreSQL Exporter**: Deploy an exporter to expose PostgreSQL metrics to Prometheus.
    
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: postgres-exporter
      namespace: laboratory-swarm
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: postgres-exporter
      template:
        metadata:
          labels:
            app: postgres-exporter
        spec:
          containers:
            - name: postgres-exporter
              image: prometheuscommunity/postgres-exporter:latest
              ports:
                - containerPort: 9187
              env:
                - name: DATA_SOURCE_NAME
                  valueFrom:
                    secretKeyRef:
                      name: postgresql-secret
                      key: datasource
              args:
                - "--extend.query-path=/etc/postgres_exporter/queries.yaml"
              volumeMounts:
                - name: queries
                  mountPath: /etc/postgres_exporter
          volumes:
            - name: queries
              configMap:
                name: postgres-queries
    ```

  - **Configuration**: Define custom queries and metrics as needed.

- **Grafana**: Visualizes PostgreSQL metrics through dashboards.
  
  - **Dashboard Setup**: Import or create dashboards tailored to monitor PostgreSQL performance metrics such as connection counts, query durations, cache hits, and more.

### Logging

Centralized logging is essential for troubleshooting and performance analysis.

- **Fluentd/Elastic Stack**: Aggregate logs from PostgreSQL pods.
  
  - **Configuration**: Set up log collectors to capture PostgreSQL logs and forward them to a centralized logging system like Elasticsearch or Loki.
  
  - **Example**:
    
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

### Access Control

Secure access to StatefulSets and their data is paramount.

- **Kubernetes RBAC**: Define roles and role bindings to restrict access to StatefulSet resources and PersistentVolumeClaims.
  
  **Example RBAC Configuration**:

  ```yaml
  apiVersion: rbac.authorization.k8s.io/v1
  kind: Role
  metadata:
    namespace: laboratory-swarm
    name: statefulset-manager
  rules:
    - apiGroups: ["apps"]
      resources: ["statefulsets"]
      verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
    - apiGroups: [""]
      resources: ["pods", "services", "persistentvolumeclaims"]
      verbs: ["get", "list", "watch"]
  ---
  apiVersion: rbac.authorization.k8s.io/v1
  kind: RoleBinding
  metadata:
    name: statefulset-manager-binding
    namespace: laboratory-swarm
  subjects:
    - kind: User
      name: "postgres-admin"
      apiGroup: rbac.authorization.k8s.io
  roleRef:
    kind: Role
    name: statefulset-manager
    apiGroup: rbac.authorization.k8s.io
  ```

### Data Encryption

Protect data at rest and in transit to ensure confidentiality and integrity.

- **Encryption at Rest**:
  
  - **Persistent Volumes**: Use encrypted storage backends or enable encryption features provided by the storage class.
  
  - **PostgreSQL Encryption**: Implement PostgreSQL's native encryption features, such as Transparent Data Encryption (TDE), if required.
  
- **Encryption in Transit**:
  
  - **TLS**: Ensure that connections to PostgreSQL are encrypted using TLS.
  
    - **Configuration**: Update PostgreSQL configuration to enable SSL and provide necessary certificates.
    
      ```yaml
      env:
        - name: POSTGRES_SSLMODE
          value: "verify-full"
        - name: POSTGRES_SSLROOTCERT
          value: "/var/lib/postgresql/server.crt"
      ```

### Backup and Recovery

Implement robust backup and recovery strategies to prevent data loss.

- **Automated Backups**:
  
  - Use tools like `pgBackRest` or `wal-e` to automate PostgreSQL backups.
  
  - **Example Backup Job**:
    
    ```yaml
    apiVersion: batch/v1
    kind: CronJob
    metadata:
      name: postgres-backup
      namespace: laboratory-swarm
    spec:
      schedule: "0 2 * * *" # Daily at 2 AM
      jobTemplate:
        spec:
          template:
            spec:
              containers:
                - name: backup
                  image: postgres:13-alpine
                  env:
                    - name: PGPASSWORD
                      valueFrom:
                        secretKeyRef:
                          name: postgresql-secret
                          key: password
                  command: ["/bin/sh", "-c"]
                  args:
                    - pg_dump -U postgres -h postgresql-0.postgresql.laboratory-swarm.svc.cluster.local laboratory_swarm > /backup/laboratory_swarm_$(date +\%F).sql
                  volumeMounts:
                    - name: backup-storage
                      mountPath: /backup
              restartPolicy: OnFailure
              volumes:
                - name: backup-storage
                  persistentVolumeClaim:
                    claimName: postgres-backup-pvc
    ```

- **Disaster Recovery**:
  
  - Regularly test backup restoration procedures to ensure data can be recovered in case of failures.
  
  - Maintain offsite backups to protect against cluster-wide disasters.

## Troubleshooting

### Common Issues

1. **Pod Not Starting**

   - **Symptoms**: PostgreSQL pods are in `Pending` or `CrashLoopBackOff` state.
   - **Solutions**:
     - **Pending**: Check if PersistentVolumes are available and correctly bound.
       
       ```bash
       kubectl get pvc -n laboratory-swarm
       ```
     
     - **CrashLoopBackOff**: Inspect pod logs for errors.
       
       ```bash
       kubectl logs postgresql-0 -n laboratory-swarm
       ```

2. **Data Persistence Issues**

   - **Symptoms**: Data loss after pod restarts or rescheduling.
   - **Solutions**:
     - Verify that PersistentVolumeClaims are correctly bound to PersistentVolumes.
     - Ensure that the storage backend is reliable and properly configured.
     - Check PostgreSQL configurations to confirm data directories are correctly mounted.

3. **Connection Failures**

   - **Symptoms**: Applications cannot connect to PostgreSQL.
   - **Solutions**:
     - Ensure that the PostgreSQL service is correctly exposing port `5432`.
       
       ```bash
       kubectl get svc postgresql -n laboratory-swarm
       ```
     
     - Verify network policies allow traffic between services.
     - Check PostgreSQL credentials and environment variables.

4. **High Resource Consumption**

   - **Symptoms**: PostgreSQL pods are consuming excessive CPU or memory.
   - **Solutions**:
     - Review resource requests and limits in the StatefulSet configuration.
     - Optimize PostgreSQL configurations for performance.
     - Monitor running queries to identify and optimize inefficient operations.

5. **Backup Failures**

   - **Symptoms**: Backup jobs failing or incomplete backups.
   - **Solutions**:
     - Check backup job logs for error messages.
       
       ```bash
       kubectl logs <backup-job-pod-name> -n laboratory-swarm
       ```
     
     - Ensure that backup storage is accessible and has sufficient space.
     - Validate backup scripts and configurations.

### Debugging Steps

1. **Inspect Pod Status and Logs**

   - Retrieve the status of StatefulSet pods.
     
     ```bash
     kubectl get pods -n laboratory-swarm -l app=postgresql
     ```
   
   - View logs for a specific pod to identify errors.
     
     ```bash
     kubectl logs postgresql-0 -n laboratory-swarm
     ```

2. **Check PersistentVolumeClaims**

   - Ensure that all PVCs are bound to PersistentVolumes.
     
     ```bash
     kubectl get pvc -n laboratory-swarm
     ```

3. **Validate StatefulSet Configuration**

   - Retrieve and review the StatefulSet YAML to ensure correct configurations.
     
     ```bash
     kubectl get statefulset postgresql -n laboratory-swarm -o yaml
     ```

4. **Test Connectivity**

   - From another pod within the cluster, attempt to connect to PostgreSQL.
     
     ```bash
     kubectl exec -it <app-pod-name> -n laboratory-swarm -- psql -h postgresql -U postgres -d laboratory_swarm
     ```

5. **Review Event Logs**

   - Check Kubernetes events for any issues related to StatefulSet or pods.
     
     ```bash
     kubectl get events -n laboratory-swarm --sort-by='.lastTimestamp'
     ```

6. **Use Diagnostic Tools**

   - Utilize tools like `kubectl describe` to get detailed information about resources.
     
     ```bash
     kubectl describe statefulset postgresql -n laboratory-swarm
     kubectl describe pod postgresql-0 -n laboratory-swarm
     ```

## Further Reading

- [Kubernetes StatefulSets Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [Prometheus PostgreSQL Exporter](https://github.com/prometheus-community/postgres_exporter)
- [Helm Charts for PostgreSQL](https://github.com/bitnami/charts/tree/master/bitnami/postgresql)
- [Kubernetes Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Securing PostgreSQL on Kubernetes](https://www.postgresql.org/docs/current/security.html)
- [Backup Strategies for Kubernetes](https://kubernetes.io/docs/concepts/storage/volume-pvc/#backup-and-restore)

## Links

- [Root Documentation](../../README.md)
- [Istio Configuration Documentation](../../istio/README.md)
- [Kubernetes Monitoring Tools Documentation](../kubernetes/README.md)
- [Prometheus Documentation](https://prometheus.io/docs/introduction/overview/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Kubernetes StatefulSets Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Helm Documentation](https://helm.sh/docs/)

---

If you encounter any issues or have questions regarding the StatefulSets component, please refer to the [Troubleshooting](#troubleshooting) section or reach out to the project maintainers.