# k8s-notify

Watches for Kubernetes Deployments and posts status updates to one or more Flowdock chat rooms.

Notifications are controlled by adding annotations to Deployments.

- Supports notifications on specific deployments
- Supports notifications to different flows based on team

## Usage

```
pipenv install
pipenv run python k8s-notify.py --config <path-to-config.yml>
```

### Kubernetes

`k8s-notify` is intended to be deployed inside a Kubernetes Cluster.

Example manifests can be found [here](./deploy/)

## Configuration

See the example-config [here](./hack/config.example.yml) 

```yaml
cluster_name: "Kubernetes Cluster"
receivers:
  flowdock:
    cluster_ops:
      token: "{FLOWDOCK_TOKEN_CLUSTER_OPS}"
    sre:
      token: "{FLOWDOCK_TOKEN_SRE}"
```

This example defines a `flowdock` receiver (currently the only type supported), and two teams *cluster_ops* and *sre*.

Annotations on the deployment matching the teams will be routed to the flowdock room identified by the injected flowdock-token.

Environment variables are supported in the config (see above example).

### Annotations

Enabling notifications for Deployments is managed through the use of annotations.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  annotations: 
    app.mintel.com/k8s-notify.enabled: "true"
    app.mintel.com/k8s-notify.team: sre
    app.mintel.com/k8s-notify.receiver: flowdock
    app.mintel.com/k8s-notify.vcs-url: https://vcs-url
    app.mintel.com/k8s-notify.public-url: https://public-facing-url
    app.mintel.com/k8s-notify.monitoring-url: https://monitoring-url
    app.mintel.com/k8s-notify.health-status-url: https://heatlh-status-url
```

The `-url` annotations are optional. If specified, they will be included in the notification.
