# Network Policies and RBAC Documentation

## Table of Contents

- [Overview](#overview)
- [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
  - [Introduction to RBAC](#introduction-to-rbac)
  - [RBAC Components](#rbac-components)
    - [Roles and ClusterRoles](#roles-and-clusterroles)
    - [RoleBindings and ClusterRoleBindings](#rolebindings-and-clusterrolebindings)
  - [Best Practices](#best-practices)
  - [Example Configurations](#example-configurations)
    - [Creating a Role](#creating-a-role)
    - [Creating a RoleBinding](#creating-a-rolebinding)
    - [Creating a ClusterRole](#creating-a-clusterrole)
    - [Creating a ClusterRoleBinding](#creating-a-clusterrolebinding)
- [Network Policies](#network-policies)
  - [Introduction to Network Policies](#introduction-to-network-policies)
  - [Network Policy Components](#network-policy-components)
    - [Pod Selector](#pod-selector)
    - [Ingress Rules](#ingress-rules)
    - [Egress Rules](#egress-rules)
    - [Policy Types](#policy-types)
  - [Best Practices](#best-practices-1)
  - [Example Configurations](#example-configurations-1)
    - [Default Deny All](#default-deny-all)
    - [Allow Specific Ingress](#allow-specific-ingress)
    - [Allow Specific Egress](#allow-specific-egress)
    - [Combined Ingress and Egress](#combined-ingress-and-egress)
- [Integration of RBAC and Network Policies](#integration-of-rbac-and-network-policies)
- [Troubleshooting](#troubleshooting)
  - [Common RBAC Issues](#common-rbac-issues)
  - [Common Network Policies Issues](#common-network-policies-issues)
- [Tools and Utilities](#tools-and-utilities)
- [Further Reading](#further-reading)
- [Links](#links)

---

## Overview

Effective security in Kubernetes clusters is paramount to protect applications and data from unauthorized access and potential threats. Two critical components in achieving this security are **Role-Based Access Control (RBAC)** and **Network Policies**. 

- **RBAC** manages permissions and ensures that users and services have the minimum necessary access to perform their functions.
- **Network Policies** control the traffic flow between pods, enforcing network segmentation and restricting communication to only what is necessary.

This documentation provides a comprehensive guide to implementing RBAC and Network Policies within the Laboratory Swarm Application, ensuring a secure and resilient infrastructure.

## Role-Based Access Control (RBAC)

### Introduction to RBAC

**Role-Based Access Control (RBAC)** is a method of regulating access to computer or network resources based on the roles of individual users within an organization. In Kubernetes, RBAC is used to define and enforce permissions for users and service accounts, ensuring that entities have only the access they need to perform their tasks.

### RBAC Components

RBAC in Kubernetes consists of several key components:

#### Roles and ClusterRoles

- **Role**: Defines a set of permissions within a specific namespace.
- **ClusterRole**: Defines a set of permissions cluster-wide, not limited to any namespace.

**Permissions** are specified using **verbs** (e.g., `get`, `list`, `create`, `update`, `delete`) on **resources** (e.g., `pods`, `services`, `deployments`).

**Example:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: laboratory-swarm
  name: pod-reader
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "watch", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-admin
rules:
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["*"]
```

#### RoleBindings and ClusterRoleBindings

- **RoleBinding**: Grants the permissions defined in a Role or ClusterRole to a user or set of users within a specific namespace.
- **ClusterRoleBinding**: Grants the permissions defined in a ClusterRole to a user or set of users across the entire cluster.

**Example:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: laboratory-swarm
subjects:
  - kind: User
    name: jane.doe@example.com
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-binding
subjects:
  - kind: User
    name: admin@example.com
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
```

### Best Practices

- **Least Privilege**: Grant only the permissions necessary for users or service accounts to perform their tasks.
- **Separate Roles by Function**: Define distinct roles for different functions to minimize the risk of privilege escalation.
- **Regular Audits**: Periodically review RBAC policies to ensure they comply with security requirements.
- **Use Namespaces**: Leverage namespaces to scope roles and reduce the complexity of permissions.
- **Avoid Wildcards**: Refrain from using wildcards (`*`) in verbs and resources unless absolutely necessary.

### Example Configurations

#### Creating a Role

**Purpose**: Allow users to read pods within the `laboratory-swarm` namespace.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: laboratory-swarm
  name: pod-reader
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "watch", "list"]
```

#### Creating a RoleBinding

**Purpose**: Bind the `pod-reader` role to a specific user.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods-binding
  namespace: laboratory-swarm
subjects:
  - kind: User
    name: jane.doe@example.com
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

#### Creating a ClusterRole

**Purpose**: Grant cluster-wide administrative privileges.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-admin
rules:
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["*"]
```

#### Creating a ClusterRoleBinding

**Purpose**: Bind the `cluster-admin` ClusterRole to an administrator user.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-binding
subjects:
  - kind: User
    name: admin@example.com
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
```

## Network Policies

### Introduction to Network Policies

**Network Policies** in Kubernetes are used to control the traffic flow between pods and services. They provide a way to implement network segmentation, ensuring that only authorized traffic is allowed within the cluster. By defining **allow rules**, administrators can specify which connections are permitted, enhancing the security posture of the Kubernetes environment.

### Network Policy Components

Network Policies consist of several key components that define how traffic is managed within the cluster.

#### Pod Selector

The **Pod Selector** specifies the group of pods to which the Network Policy applies. It uses label selectors to identify target pods.

**Example:**

```yaml
podSelector:
  matchLabels:
    app: aggregator-api
```

#### Ingress Rules

**Ingress Rules** define the allowed incoming traffic to the selected pods. They can specify sources based on pod selectors, namespace selectors, IP blocks, and ports.

**Example:**

```yaml
ingress:
  - from:
      - podSelector:
          matchLabels:
            role: frontend
    ports:
      - protocol: TCP
        port: 8080
```

#### Egress Rules

**Egress Rules** define the allowed outgoing traffic from the selected pods. Similar to ingress rules, they can specify destinations based on pod selectors, namespace selectors, IP blocks, and ports.

**Example:**

```yaml
egress:
  - to:
      - podSelector:
          matchLabels:
            app: database
    ports:
      - protocol: TCP
        port: 5432
```

#### Policy Types

- **Ingress**: Controls incoming traffic to pods.
- **Egress**: Controls outgoing traffic from pods.
- **Both**: A policy can define both ingress and egress rules.

### Best Practices

- **Default Deny**: Start with a default deny-all policy and explicitly allow necessary traffic.
- **Least Privilege**: Only allow the minimum required traffic between pods.
- **Use Namespaces**: Leverage namespace selectors to simplify policy definitions.
- **Label Strategically**: Use consistent and meaningful labels to manage selectors effectively.
- **Monitor and Audit**: Continuously monitor network traffic and audit policies for compliance and security.

### Example Configurations

#### Default Deny All

**Purpose**: Deny all ingress and egress traffic to pods labeled `app: aggregator-api` unless explicitly allowed.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: laboratory-swarm
spec:
  podSelector:
    matchLabels:
      app: aggregator-api
  policyTypes:
    - Ingress
    - Egress
```

#### Allow Specific Ingress

**Purpose**: Allow pods labeled `role: frontend` to send TCP traffic on port `8080` to pods labeled `app: aggregator-api`.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-ingress
  namespace: laboratory-swarm
spec:
  podSelector:
    matchLabels:
      app: aggregator-api
  ingress:
    - from:
        - podSelector:
            matchLabels:
              role: frontend
      ports:
        - protocol: TCP
          port: 8080
```

#### Allow Specific Egress

**Purpose**: Allow pods labeled `app: aggregator-api` to communicate with pods labeled `app: database` on port `5432`.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-db-egress
  namespace: laboratory-swarm
spec:
  podSelector:
    matchLabels:
      app: aggregator-api
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: database
      ports:
        - protocol: TCP
          port: 5432
```

#### Combined Ingress and Egress

**Purpose**: Allow pods labeled `app: aggregator-api` to receive traffic from `role: frontend` on port `8080` and communicate with `app: database` on port `5432`.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: aggregator-api-policy
  namespace: laboratory-swarm
spec:
  podSelector:
    matchLabels:
      app: aggregator-api
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              role: frontend
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: database
      ports:
        - protocol: TCP
          port: 5432
```

## Integration of RBAC and Network Policies

While **RBAC** controls *who* can perform actions within the Kubernetes cluster, **Network Policies** control *how* pods communicate with each other. Integrating both ensures a robust security posture by restricting both access and communication pathways.

**Example Scenario**:

- **RBAC**: A developer is granted read-only access to view pod statuses in the `laboratory-swarm` namespace.
- **Network Policies**: The `aggregator-api` pod is only accessible by pods labeled `role: frontend`, preventing unauthorized services from communicating with it.

This combination ensures that only authorized users can access certain resources and that only trusted services can communicate with critical components.

## Troubleshooting

### Common RBAC Issues

1. **Permission Denied Errors**
   - **Symptoms**: Users receive "forbidden" errors when attempting to perform actions.
   - **Solutions**:
     - Verify that the user has the necessary Role or ClusterRole bindings.
     - Check for typos in role or binding names.
     - Ensure that the correct namespace is specified in RoleBindings.

2. **Unexpected Access**
   - **Symptoms**: Users can perform actions they shouldn't be able to.
   - **Solutions**:
     - Review ClusterRoles and ClusterRoleBindings for overly permissive rules.
     - Implement the principle of least privilege by refining roles.
     - Use tools like `kubectl auth can-i` to diagnose access.

**Example Diagnostic Command**:

```bash
kubectl auth can-i create pods --as=jane.doe@example.com -n laboratory-swarm
```

### Common Network Policies Issues

1. **Pods Cannot Communicate**
   - **Symptoms**: Services cannot reach each other, resulting in connection timeouts.
   - **Solutions**:
     - Ensure that appropriate Network Policies are in place to allow necessary traffic.
     - Verify that pods have the correct labels matching the policy selectors.
     - Check for conflicting policies that may inadvertently block traffic.

2. **Unexpected Traffic Blocks**
   - **Symptoms**: Legitimate traffic is being blocked despite policies allowing it.
   - **Solutions**:
     - Review ingress and egress rules for accuracy.
     - Confirm that policies are applied to the correct namespaces and pods.
     - Use tools like `kubectl describe networkpolicy` to inspect policies.

**Example Diagnostic Command**:

```bash
kubectl describe networkpolicy allow-frontend-ingress -n laboratory-swarm
```

## Tools and Utilities

- **`kubectl`**: The primary command-line tool for interacting with Kubernetes clusters.
- **`kube-no-trouble (kubent)`**: Detects deprecated APIs that might be removed in future Kubernetes releases.
- **`krew` Plugins**: Extend `kubectl` with additional functionalities for RBAC and Network Policy management.
- **`rbac-lookup`**: Helps in identifying which roles have access to specific resources.
- **`calicoctl`**: If using Calico for network policies, this tool provides advanced management capabilities.

## Further Reading

- [Kubernetes RBAC Documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Kubernetes Network Policies Documentation](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Istio RBAC Policies](https://istio.io/latest/docs/reference/config/security/authorization-policy/)
- [Calico Network Policies](https://docs.projectcalico.org/security/kubernetes-network-policy)
- [RBAC Best Practices](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#best-practices)
- [Network Policy Best Practices](https://kubernetes.io/docs/concepts/services-networking/network-policies/#best-practices)

## Links

- [Root Documentation](../../README.md)
- [Security Documentation](../README.md)
- [Kubernetes RBAC Documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Kubernetes Network Policies Documentation](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Istio Security Documentation](../istio/README.md)
- [Prometheus Documentation](https://prometheus.io/docs/introduction/overview/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Kubernetes Pod Security Policies](https://kubernetes.io/docs/concepts/policy/pod-security-policy/)
- [RBAC Tools](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#tools)

---

**Secure Your Cluster! 🛡️**

---

If you encounter any issues or have questions regarding the Network Policies and RBAC component, please refer to the [Troubleshooting](#troubleshooting) section or reach out to the project maintainers.