import pytest
import sys
import os
from uuid import uuid4
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.event_store import EventStore
from src.git_integration import GitIntegration
from src.consistency import ConsistencyChecker


class TestDualStorageConsistency:
    def setup_method(self):
        self.event_store = EventStore(":memory:")
        self.git = GitIntegration()
        self.checker = ConsistencyChecker(self.event_store, self.git)

    def teardown_method(self):
        self.event_store.close()
        self.git.cleanup()

    def test_artifact_creation_sync(self):
        sha = self.git.create_commit(
            "docs/design.md",
            "# Design Document\n\nInitial version",
            "Add design document"
        )

        self.event_store.write_event(
            "Artifact.Created",
            "part-traecn-001",
            {
                "id": "art-1",
                "type": "design",
                "path": "docs/design.md",
                "initial_sha": sha
            }
        )

        artifact_events = self.event_store.get_events_by_type("Artifact.Created")
        assert len(artifact_events) == 1
        assert artifact_events[0].payload["initial_sha"] == sha
        assert self.git.verify_sha_exists(sha)

    def test_artifact_update_with_sha_pair(self):
        initial_sha = self.git.create_commit(
            "src/main.py",
            "print('Hello')",
            "Initial commit"
        )

        self.event_store.write_event(
            "Artifact.Created",
            "part-traecn-001",
            {"id": "art-2", "type": "code", "path": "src/main.py", "initial_sha": initial_sha}
        )

        updated_sha = self.git.update_commit(
            "src/main.py",
            "print('Hello, World!')",
            "Update greeting"
        )

        self.event_store.write_event(
            "Artifact.Updated",
            "part-traecn-001",
            {"id": "art-2", "old_sha": initial_sha, "new_sha": updated_sha}
        )

        update_events = self.event_store.get_events_by_type("Artifact.Updated")
        assert len(update_events) == 1
        assert update_events[0].payload["old_sha"] == initial_sha
        assert update_events[0].payload["new_sha"] == updated_sha
        assert self.git.verify_sha_exists(initial_sha)
        assert self.git.verify_sha_exists(updated_sha)

    def test_review_target_version_reference(self):
        sha = self.git.create_commit(
            "docs/api.md",
            "# API Spec\n\nv1.0",
            "Add API spec"
        )

        self.event_store.write_event(
            "Artifact.Created",
            "part-traecn-001",
            {"id": "art-3", "type": "api_spec", "path": "docs/api.md", "initial_sha": sha}
        )

        self.event_store.write_event(
            "Review.Submitted",
            "part-human-001",
            {
                "id": "rev-1",
                "target_type": "Artifact",
                "target_id": "art-3",
                "target_version": f"art-3@{sha[:7]}",
                "verdict": "approve"
            }
        )

        issues = self.checker.check_review_targets()
        assert len(issues) == 0, f"Found issues: {issues}"

    def test_consistency_checker_detects_dangling_reference(self):
        self.event_store.write_event(
            "Review.Submitted",
            "part-human-001",
            {
                "id": "rev-2",
                "target_type": "Artifact",
                "target_id": "art-999",
                "target_version": "art-999@deadbeef",
                "verdict": "approve"
            }
        )

        issues = self.checker.check_all_references()
        assert len(issues) == 1
        assert issues[0]["issue"] == "dangling_reference"
        assert issues[0]["sha"] == "deadbeef"

    def test_force_push_does_not_break_old_references(self):
        sha1 = self.git.create_commit(
            "src/utils.py",
            "def foo(): return 1",
            "First commit"
        )

        self.event_store.write_event(
            "Artifact.Created",
            "part-traecn-001",
            {"id": "art-4", "type": "code", "path": "src/utils.py", "initial_sha": sha1}
        )

        self.event_store.write_event(
            "Review.Submitted",
            "part-human-001",
            {
                "id": "rev-3",
                "target_type": "Artifact",
                "target_id": "art-4",
                "target_version": f"art-4@{sha1[:7]}",
                "verdict": "approve"
            }
        )

        sha2 = self.git.update_commit(
            "src/utils.py",
            "def foo(): return 2",
            "Second commit"
        )

        self.event_store.write_event(
            "Artifact.Updated",
            "part-traecn-001",
            {"id": "art-4", "old_sha": sha1, "new_sha": sha2}
        )

        sha3 = self.git.force_push(
            "src/utils.py",
            "def foo(): return 3"
        )

        assert self.git.verify_sha_exists(sha1)
        assert self.git.verify_sha_exists(sha2)
        assert self.git.verify_sha_exists(sha3)

        issues = self.checker.check_review_targets()
        assert len(issues) == 0, f"Old references should still be valid: {issues}"

    def test_artifact_consistency_check(self):
        sha = self.git.create_commit(
            "docs/readme.md",
            "# Project\n\nDescription",
            "Create readme"
        )

        self.event_store.write_event(
            "Artifact.Created",
            "part-traecn-001",
            {"id": "art-5", "type": "document", "path": "docs/readme.md", "initial_sha": sha}
        )

        result = self.checker.check_artifact_consistency("art-5")
        assert result["status"] == "consistent"
        assert result["event_sha"] == sha

    def test_cross_reference_validation(self):
        prop_sha = self.git.create_commit(
            "proposals/prop-1.md",
            "# Proposal 1\n\nDescription",
            "Create proposal"
        )

        self.event_store.write_event(
            "Proposal.Created",
            "part-traecn-001",
            {"id": "prop-1", "title": "Test Proposal", "version": "v1", "sha": prop_sha}
        )

        self.event_store.write_event(
            "Decision.Recorded",
            "part-human-001",
            {
                "id": "dec-1",
                "claim_id": "claim-1",
                "references": [f"prop-1@{prop_sha[:7]}"]
            }
        )

        issues = self.checker.check_all_references()
        assert len(issues) == 0, f"Cross-reference validation failed: {issues}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])