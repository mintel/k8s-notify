from utils import (
    ANNOTATION_PUBLIC_URL,
    ANNOTATION_MONITORING_URL,
    ANNOTATION_HEALTH_STATUS_URL,
    ANNOTATION_VCS_URL,
)


class Receiver(object):

    NAME = "receiver"

    def __init__(self, cluster_name, team):

        self.cluster_name = cluster_name
        self.team = team

        self.rollouts = {}
        self.rollouts_previous_generation = {}

        self._ROLLOUT_COMPLETE = 1
        self._ROLLOUT_PROGRESSING = 2
        self._ROLLOUT_DEGRADED = 3
        self._ROLLOUT_FAILED = 4
        self._ROLLOUT_OUTAGE = 5
        self._ROLLOUT_UNKNOWN = 6

    def rollout_complete(self, status):
        return status == self._ROLLOUT_COMPLETE

    def rollout_progressing(self, status):
        return status == self._ROLLOUT_PROGRESSING

    def rollout_degraded(self, status):
        return status == self._ROLLOUT_DEGRADED

    def rollout_failed(self, status):
        return status == self._ROLLOUT_FAILED

    def rollout_outage(self, status):
        return status == self._ROLLOUT_OUTAGE

    def rollout_unknown(self, status):
        return status == self._ROLLOUT_UNKNOWN

    def public_url(self, annotations):
        return annotations.get(ANNOTATION_PUBLIC_URL)

    def monitoring_url(self, annotations):
        return annotations.get(ANNOTATION_MONITORING_URL)

    def health_status_url(self, annotations):
        return annotations.get(ANNOTATION_HEALTH_STATUS_URL)

    def vcs_url(self, annotations):
        return annotations.get(ANNOTATION_VCS_URL)

    def _rollout_status(
        self,
        condition,
        num_replicas_desired,
        num_replicas_updated,
        num_replicas_ready,
        num_replicas_current,
        num_replicas_unavailable,
    ):

        if not condition:
            return self._ROLLOUT_UNKNOWN, "", ""

        if num_replicas_current == 0 or num_replicas_ready == 0:
            return self._ROLLOUT_OUTAGE

        if condition.reason == "ReplicaFailure":
            return self._ROLLOUT_FAILED

        if num_replicas_desired == num_replicas_ready:
            return self._ROLLOUT_COMPLETE

        if (
            num_replicas_unavailable > 0
            and num_replicas_current != num_replicas_updated
        ):
            return self._ROLLOUT_DEGRADED

        return self._ROLLOUT_PROGRESSING

    def _handle_deployment_change(self, deployment):
        metadata = deployment.metadata
        status = deployment.status
        deployment_key = (
            f"{status.observed_generation}/" f"{metadata.namespace}/" f"{metadata.name}"
        )

        previous_generation = self.rollouts_previous_generation.get(deployment_key, 0)
        if (
            previous_generation > 0
            and status.observed_generation == previous_generation
        ):
            return

        if not deployment.status.conditions:
            return

        num_replicas_desired = deployment.spec.replicas or 0
        num_replicas_ready = status.ready_replicas or 0
        num_replicas_updated = status.updated_replicas or 0
        num_replicas_current = status.replicas or 0
        num_replicas_available = status.available_replicas or 0
        num_replicas_unavailable = status.unavailable_replicas or 0

        last_condition = deployment.status.conditions[-1]

        message_status = f"{last_condition.type} {last_condition.reason}"
        message_reason = f"{last_condition.message} ({last_condition.last_update_time})"

        message_summary = (
            "Desired:%s, Ready:%s, Updated:%s, Available:%s, Unavailable:%s"
            % (
                num_replicas_desired,
                num_replicas_ready,
                num_replicas_updated,
                num_replicas_available,
                num_replicas_unavailable,
            )
        )

        message_completion = "%d/%d (%d %%)" % (
            num_replicas_updated,
            num_replicas_desired,
            int(100 * num_replicas_updated / num_replicas_desired),
        )

        rollout_status = self._rollout_status(
            last_condition,
            num_replicas_desired,
            num_replicas_updated,
            num_replicas_ready,
            num_replicas_current,
            num_replicas_unavailable,
        )

        if self.rollout_unknown(rollout_status):
            return

        blocks = self._generate_deployment_message(
            deployment_key,
            deployment,
            rollout_status,
            message_reason,
            message_status,
            message_summary,
            message_completion,
            num_replicas_ready,
            num_replicas_desired,
        )

        if deployment_key not in self.rollouts:
            self.rollouts[deployment_key] = self._send_message(data=blocks)
        else:
            self._send_message(message_id=self.rollouts[deployment_key][0], data=blocks)

        if self.rollout_complete(rollout_status):
            if deployment_key in self.rollouts:
                self.rollouts.pop(deployment_key)

            self.rollouts_previous_generation[
                deployment_key
            ] = status.observed_generation

    def _should_handle(self, team, receiver):
        return True if self.team == team and self.NAME == receiver else False

    def handle_event(self, team, receiver, deployment):
        if self._should_handle(team, receiver):
            self._handle_deployment_change(deployment)
