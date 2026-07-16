import re
from typing import List, Dict, Tuple

from .git_integration import GitIntegration


class ConsistencyChecker:
    SHA_PATTERN = r"@([a-f0-9]{7,40})\b"

    def __init__(self, event_store, git_integration: GitIntegration):
        self.event_store = event_store
        self.git = git_integration

    def check_all_references(self) -> List[Dict[str, str]]:
        all_events = self.event_store.get_all_events()
        issues = []

        for event in all_events:
            payload = event.payload
            payload_str = str(payload)
            matches = re.findall(self.SHA_PATTERN, payload_str)

            for sha in matches:
                if not self.git.verify_sha_exists(sha):
                    issues.append({
                        "event_id": str(event.event_id),
                        "event_type": event.event_type,
                        "sha": sha,
                        "issue": "dangling_reference",
                        "description": f"SHA {sha} not found in Git"
                    })

        return issues

    def check_artifact_consistency(self, artifact_id: str) -> Dict[str, any]:
        artifact_events = self.event_store.get_events_by_type("Artifact.Created")
        artifact_events += self.event_store.get_events_by_type("Artifact.Updated")

        artifact_events = [
            e for e in artifact_events
            if e.payload.get("id") == artifact_id
        ]

        if not artifact_events:
            return {"status": "error", "message": "No artifact events found"}

        last_event = artifact_events[-1]
        event_sha = last_event.payload.get("current_sha") or last_event.payload.get("new_sha") or last_event.payload.get("initial_sha")

        if not event_sha:
            return {"status": "error", "message": "No SHA in event"}

        artifact_path = last_event.payload.get("path", artifact_id)
        latest_commit_sha = self.git.get_latest_sha()

        is_reachable = self.git.verify_sha_exists(event_sha)

        return {
            "status": "consistent" if is_reachable else "inconsistent",
            "event_sha": event_sha,
            "latest_commit_sha": latest_commit_sha,
            "artifact_id": artifact_id,
            "artifact_path": artifact_path,
            "last_event": last_event.event_type,
            "sha_reachable": is_reachable
        }

    def check_review_targets(self) -> List[Dict[str, str]]:
        review_events = self.event_store.get_events_by_type("Review.Submitted")
        issues = []

        for event in review_events:
            target_version = event.payload.get("target_version", "")
            matches = re.findall(self.SHA_PATTERN, target_version)

            for sha in matches:
                if not self.git.verify_sha_exists(sha):
                    issues.append({
                        "event_id": str(event.event_id),
                        "review_id": event.payload.get("id"),
                        "target_version": target_version,
                        "issue": "stale_review",
                        "description": f"Review target SHA {sha} not found in Git"
                    })

        return issues

    def get_stale_references(self) -> List[Dict[str, any]]:
        return self.check_all_references() + self.check_review_targets()