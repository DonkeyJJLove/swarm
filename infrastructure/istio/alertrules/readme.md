# Alert Rules Documentation

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
  - [PrometheusRule Configuration](#prometheusrule-configuration)
    - [SerwerHighErrorRate](#serwerhigherrorrate)
    - [SerwerHighLatency](#serwerhighlatency)
- [Deployment](#deployment)
  - [Prerequisites](#prerequisites)
  - [Apply Alert Rules](#apply-alert-rules)
- [Configuration](#configuration)
  - [Alert Rule Parameters](#alert-rule-parameters)
- [Monitoring](#monitoring)
  - [Alertmanager Integration](#alertmanager-integration)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Further Reading](#further-reading)
- [Links](#links)

---

## Overview

The **Alert Rules** component is integral to the Laboratory Swarm Application's monitoring strategy. It defines specific conditions under which alerts are triggered, ensuring that the system's health and performance are continuously monitored. These alert rules are implemented using Prometheus' `PrometheusRule` custom resources and are designed to detect high error rates and latency issues within server applications.

## Architecture

![Alert Rules Architecture](./architecture.png)

*Figure: High-level architecture of the Alert Rules component.*

The Alert Rules operate within the `laboratory-swarm` namespace in the Kubernetes cluster. They integrate with Prometheus to evaluate defined metrics and trigger alerts via Alertmanager when certain thresholds are exceeded. This setup ensures proactive identification and resolution of potential issues affecting the application's reliability and user experience.

## Components

### PrometheusRule Configuration

The Alert Rules are defined using Prometheus' `PrometheusRule` custom resource. These rules specify the conditions under which alerts should be fired based on the collected metrics.

- **File**: `alertrules/serwer-alerts.yaml`

#### SerwerHighErrorRate

- **Description**: Triggers an alert when the rate of HTTP 5xx errors exceeds 5% over a 5-minute window for more than 2 minutes.

- **Configuration**:

  ```yaml
  - alert: SerwerHighErrorRate
    expr: rate(http_requests_total{response_code=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Wysoki wskaźnik błędów serwera"
      description: "Serwer {{ $labels.app }} ma więcej niż 5% błędów 5xx przez ostatnie 2 minuty."
  ```

- **Parameters**:
  - `alert`: Name of the alert.
  - `expr`: PromQL expression to evaluate the error rate.
  - `for`: Duration for which the condition must hold true before firing the alert.
  - `labels`: Metadata labels for the alert, including severity.
  - `annotations`: Additional information about the alert, including a summary and description.

#### SerwerHighLatency

- **Description**: Triggers an alert when the 99th percentile latency exceeds 1 second over a 5-minute window for more than 2 minutes.

- **Configuration**:

  ```yaml
  - alert: SerwerHighLatency
    expr: histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Wysoka latencja na serwerze"
      description: "99. percentyl latencji przekracza 1 sekundę przez ostatnie 2 minuty."
  ```

- **Parameters**:
  - `alert`: Name of the alert.
  - `expr`: PromQL expression to evaluate the latency.
  - `for`: Duration for which the condition must hold true before firing the alert.
  - `labels`: Metadata labels for the alert, including severity.
  - `annotations`: Additional information about the alert, including a summary and description.

**Note**: The annotations are written in Polish. Ensure that the alert messages are understandable by all stakeholders or consider translating them to the preferred language.

## Deployment

### Prerequisites

Before deploying the Alert Rules, ensure the following prerequisites are met:

- **Kubernetes Cluster**: A functional Kubernetes cluster (v1.18+).
- **Prometheus Operator**: Installed and configured to manage `PrometheusRule` resources.
- **Namespace**: The `laboratory-swarm` namespace exists. If not, create it:

  ```bash
  kubectl create namespace laboratory-swarm
  ```

### Apply Alert Rules

Deploy the Alert Rules by applying the `serwer-alerts.yaml` manifest.

1. **Navigate to the Alert Rules Directory**:

   ```bash
   cd infrastructure/istio/alertrules
   ```

2. **Apply the Alert Rules Manifest**:

   ```bash
   kubectl apply -f serwer-alerts.yaml
   ```

3. **Verify the Deployment**:

   ```bash
   kubectl get prometheusrules -n laboratory-swarm
   ```

   You should see the `serwer-alerts` rule listed among the PrometheusRules.

## Configuration

### Alert Rule Parameters

Each alert rule consists of several key parameters that define its behavior:

- **PromQL Expression (`expr`)**: Determines the condition under which the alert should be triggered.
- **Duration (`for`)**: Specifies how long the condition must persist before the alert is fired.
- **Labels (`labels`)**: Provide metadata for the alert, such as severity levels.
- **Annotations (`annotations`)**: Offer additional context and information about the alert, aiding in quicker resolution.

**Example**:

```yaml
- alert: SerwerHighErrorRate
  expr: rate(http_requests_total{response_code=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "Wysoki wskaźnik błędów serwera"
    description: "Serwer {{ $labels.app }} ma więcej niż 5% błędów 5xx przez ostatnie 2 minuty."
```

## Monitoring

The Alert Rules integrate with the following monitoring tools to ensure comprehensive observability:

- **Prometheus**: Evaluates the defined alert rules against the collected metrics.
- **Alertmanager**: Receives alerts from Prometheus and manages their routing and notification.

### Alertmanager Integration

Ensure that Alertmanager is configured to handle alerts generated by these rules. Typical configurations include routing alerts to communication channels like Slack, email, or PagerDuty.

**Example Alertmanager Configuration**:

```yaml
receivers:
  - name: 'slack-notifications'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
        channel: '#alerts'
```

Associate the alert rules with the appropriate receiver in Alertmanager to ensure timely notifications.

## Security

Security considerations for Alert Rules involve ensuring that only authorized personnel can modify alert configurations and that alert data is transmitted securely.

- **Access Control**: Use Kubernetes RBAC to restrict access to `PrometheusRule` resources. Only authorized service accounts or users should have permissions to create, update, or delete alert rules.
  
  **Example RBAC Configuration**:

  ```yaml
  apiVersion: rbac.authorization.k8s.io/v1
  kind: Role
  metadata:
    namespace: laboratory-swarm
    name: prometheus-alerts-role
  rules:
    - apiGroups: ["monitoring.coreos.com"]
      resources: ["prometheusrules"]
      verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  ---
  apiVersion: rbac.authorization.k8s.io/v1
  kind: RoleBinding
  metadata:
    name: prometheus-alerts-rolebinding
    namespace: laboratory-swarm
  subjects:
    - kind: User
      name: "alert-manager"
      apiGroup: rbac.authorization.k8s.io
  roleRef:
    kind: Role
    name: prometheus-alerts-role
    apiGroup: rbac.authorization.k8s.io
  ```

- **Secure Transmission**: Ensure that Prometheus and Alertmanager communicate over secure channels, preferably using mutual TLS provided by Istio's service mesh.

## Troubleshooting

### Common Issues

1. **Alerts Not Firing as Expected**:
   - **Possible Causes**:
     - Incorrect PromQL expressions.
     - Metrics not being scraped by Prometheus.
     - Alertmanager not properly configured to receive alerts.
   - **Solutions**:
     - Validate PromQL expressions using Prometheus' expression browser.
     - Ensure that the relevant metrics are available and being scraped.
     - Check Alertmanager logs and configurations to confirm proper setup.

2. **Alertmanager Not Receiving Alerts**:
   - **Possible Causes**:
     - Network issues between Prometheus and Alertmanager.
     - Misconfigured Alertmanager endpoints in Prometheus.
   - **Solutions**:
     - Verify network connectivity between Prometheus and Alertmanager pods.
     - Check Prometheus configuration for Alertmanager endpoints.

3. **High False Positive Alert Rates**:
   - **Possible Causes**:
     - Thresholds set too low.
     - Metrics noise or spikes causing frequent alerts.
   - **Solutions**:
     - Adjust alert thresholds to more appropriate levels.
     - Implement additional conditions or use `for` clauses to reduce false positives.

4. **Localization Issues with Alert Annotations**:
   - **Possible Causes**:
     - Annotations written in a language not understood by all team members.
   - **Solutions**:
     - Translate annotations to a common language.
     - Use multilingual annotations if necessary.

### Debugging Steps

1. **Verify Prometheus Metrics**:
   - Use Prometheus' web UI to query and confirm that the metrics used in alert rules are being collected and have the expected values.
   
   **Example**:
   
   ```promql
   rate(http_requests_total{response_code=~"5.."}[5m]) / rate(http_requests_total[5m])
   ```

2. **Check Alert Rule Evaluation**:
   - Ensure that Prometheus is correctly evaluating the alert rules.
   - Review the Prometheus server logs for any errors related to rule evaluation.

3. **Inspect Alertmanager Logs**:
   - Look for any errors or warnings in Alertmanager logs that might indicate issues with receiving or routing alerts.
   
   ```bash
   kubectl logs <alertmanager-pod-name> -n monitoring
   ```

4. **Validate RBAC Configurations**:
   - Ensure that the service accounts used by Prometheus and Alertmanager have the necessary permissions to read metrics and manage alerts.

## Further Reading

- [Prometheus Alerting Overview](https://prometheus.io/docs/alerting/latest/overview/)
- [PrometheusRule Documentation](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#prometheusrule)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Istio Security Best Practices](https://istio.io/latest/docs/concepts/security/)
- [Kubernetes RBAC Documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [PromQL Language Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/)

---

## Links

- [Istio Configuration Documentation](../README.md)
- [Prometheus Monitoring Documentation](../../kubernetes/README.md)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [PrometheusRule Specification](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#prometheusrule)

---

If you encounter any issues or have questions regarding the Alert Rules component, please refer to the [Troubleshooting](#troubleshooting) section or reach out to the project maintainers.