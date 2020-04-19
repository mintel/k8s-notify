# k8s-notify

Watches for Kubernetes Deployments and posts status updates to one or more Flowdock chat rooms based on team.

Teams are identified by reading `app.mintel.com/k8s-notify` annotations from the deployment, and to the desired flowdock room based on configuration.

## Usage

```
pipenv install
pipenv run python k8s-notify.py --config <path-to-config.yml>
```

## Configuration

See the [example-config](./hack/config.example.yml) 
```yaml
---
cluster_name: "Kubernetes Cluster"
receivers:
  flowdock:
    cluster_ops:
      token: "{FLOWDOCK_TOKEN_CLUSTER_OPS}"
    sre:
      token: "{FLOWDOCK_TOKEN_SRE}"
```

You can specify multiple teams if required.

Notifications will be sent to all matching routes.

Note that environment variables are supported in the config (as in the above example).

### Annotations

Enabling notifications for deployments is done through the use of annotations.

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
