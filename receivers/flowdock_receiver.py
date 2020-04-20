from copy import copy
import flowdock

from .receiver import Receiver


class FlowdockReceiver(Receiver):

    NAME = "flowdock"

    template = {
        "author": {"name": "k8s-notify"},
        "title": "Title",
        "external_thread_id": "Item-1",
        "thread": {
            "title": "thread-title",
            "body": "body-html",
            "external_url": "",
            "status": {"value": "Deploying...", "color": "red"},
        },
    }

    def __init__(self, cluster_name, team, flowdock_token):
        super().__init__(cluster_name, team)
        self.flowdock_client = None
        self.flowdock_token = flowdock_token

        print("configured flow-receiver for %s" % (self.team))

    def _send_message(self, data, message_id=None):
        item_id = data.get("item_id")
        author = data.get("author")
        title = "deployment monitor"
        item = data.get("thread")
        data["external_thread_id"] = item_id

        if self.flowdock_client is None:
            self.flowdock_client = flowdock.connect(flow_token=self.flowdock_token)

        if message_id is None:
            # Send a new message
            self.flowdock_client.present(
                item_id, author=author, title=title, body=item["body"], thread=item,
            )
            return item_id, item_id

        # Update exiting message
        self.flowdock_client.present(
            item_id, author=author, title=title, body=item["body"], thread=item
        )

        return item_id, item_id

    def _generate_deployment_message(
        self,
        item_id,
        deployment,
        rollout_status,
        message_reason,
        message_status,
        message_summary,
        message_completion,
        num_replicas_ready,
        num_replicas_desired,
    ):

        annotations = deployment.metadata.annotations

        flow_header = (
            f"[{num_replicas_ready}/{num_replicas_desired}] "
            f"[{self.cluster_name.upper()}] "
            f"[{deployment.metadata.namespace}/{deployment.metadata.name}]"
        )

        flow_message = (
            f"{message_status}</br>{message_reason}"
            f"</br></br>"
            f"{message_summary}"
            f"</br></br>"
        )

        for container in deployment.spec.template.spec.containers:
            flow_message += (
                f"  &#x25AB;Container '{container.name}' has image "
                f"{container.image}</br>"
            )

        if self.rollout_complete(rollout_status):
            links = [
                ("Public URL", self.public_url(annotations)),
                ("Monitoring URL", self.monitoring_url(annotations)),
                ("Health Status URL", self.health_status_url(annotations)),
                ("VCS URL", self.vcs_url(annotations)),
            ]
            flow_message += "</br>"

            for link in links:
                name, href = link
                if href:
                    flow_message += f'  &#x25AB;<a href="{href}">{name}</a></br>'

        blocks = copy(self.template)

        blocks["thread"]["title"] = flow_header
        blocks["thread"]["body"] = flow_message
        blocks["thread"]["external_url"] = self.vcs_url(annotations)

        if self.rollout_complete(rollout_status):
            blocks["thread"]["status"]["value"] = "DEPLOYED"
            blocks["thread"]["status"]["color"] = "green"
        elif self.rollout_degraded(rollout_status):
            blocks["thread"]["status"]["value"] = "DEGRADED"
            blocks["thread"]["status"]["color"] = "orange"
        elif self.rollout_failed(rollout_status):
            blocks["thread"]["status"]["value"] = "FAILED"
            blocks["thread"]["status"]["color"] = "red"
        elif self.rollout_outage(rollout_status):
            blocks["thread"]["status"]["value"] = "OUTAGE"
            blocks["thread"]["status"]["color"] = "red"
        elif self.rollout_progressing(rollout_status):
            blocks["thread"]["status"]["value"] = "PROGRESSING"
            blocks["thread"]["status"]["color"] = "blue"
        else:
            blocks["thread"]["status"]["value"] = "UNKNOWN"
            blocks["thread"]["status"]["color"] = "red"

        blocks["item_id"] = item_id

        return blocks
