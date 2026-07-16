import pytest
import sys
import os
from uuid import uuid4
from datetime import datetime
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.event_store import EventStore


class TestEventStore:
    def setup_method(self):
        self.store = EventStore(":memory:")

    def teardown_method(self):
        self.store.close()

    def test_write_event(self):
        event = self.store.write_event(
            "Goal.Created",
            "part-traecn-001",
            {"id": "goal-1", "title": "Test Goal"}
        )

        assert event.event_id is not None
        assert event.event_type == "Goal.Created"
        assert event.actor == "part-traecn-001"
        assert event.payload == {"id": "goal-1", "title": "Test Goal"}

    def test_get_event(self):
        event = self.store.write_event(
            "Proposal.Created",
            "part-test-001",
            {"id": "prop-1", "title": "Test Proposal"}
        )

        retrieved = self.store.get_event(event.event_id)
        assert retrieved is not None
        assert retrieved.event_id == event.event_id
        assert retrieved.event_type == "Proposal.Created"

    def test_get_events_by_type(self):
        self.store.write_event("Goal.Created", "actor1", {"id": "goal-1"})
        self.store.write_event("Goal.Created", "actor1", {"id": "goal-2"})
        self.store.write_event("Proposal.Created", "actor2", {"id": "prop-1"})

        goals = self.store.get_events_by_type("Goal.Created")
        assert len(goals) == 2
        assert all(g.event_type == "Goal.Created" for g in goals)

    def test_get_events_by_actor(self):
        self.store.write_event("Goal.Created", "actor1", {"id": "goal-1"})
        self.store.write_event("Proposal.Created", "actor1", {"id": "prop-1"})
        self.store.write_event("Goal.Created", "actor2", {"id": "goal-2"})

        actor1_events = self.store.get_events_by_actor("actor1")
        assert len(actor1_events) == 2
        assert all(e.actor == "actor1" for e in actor1_events)

    def test_get_all_events_ordered(self):
        event1 = self.store.write_event("Type.A", "actor", {"id": "1"})
        event2 = self.store.write_event("Type.B", "actor", {"id": "2"})

        all_events = self.store.get_all_events()
        assert len(all_events) == 2
        assert all_events[0].event_id == event1.event_id
        assert all_events[1].event_id == event2.event_id

    def test_materialize_object(self):
        self.store.write_event(
            "Goal.Created",
            "part-traecn-001",
            {"id": "goal-1", "title": "Test Goal", "status": "open"}
        )
        self.store.write_event(
            "Goal.StatusChanged",
            "part-human-001",
            {"id": "goal-1", "from": "open", "to": "addressed"}
        )
        self.store.write_event(
            "Goal.Created",
            "part-traecn-001",
            {"id": "goal-2", "title": "Another Goal", "status": "open"}
        )

        state = self.store.materialize_object("goal-1")
        assert state["id"] == "goal-1"
        assert state["title"] == "Test Goal"
        assert state["status"] == "addressed"
        assert len(state["events"]) == 2

    def test_content_addressing_reference(self):
        self.store.write_event(
            "Artifact.Created",
            "part-traecn-001",
            {"id": "art-1", "path": "docs/design.md", "initial_sha": "abc123"}
        )
        self.store.write_event(
            "Review.Submitted",
            "part-human-001",
            {
                "id": "rev-1",
                "target_type": "Artifact",
                "target_id": "art-1",
                "target_version": "art-1@abc123",
                "verdict": "approve"
            }
        )

        reviews = self.store.get_events_by_type("Review.Submitted")
        assert len(reviews) == 1
        assert reviews[0].payload["target_version"] == "art-1@abc123"

    def test_append_only_guarantee(self):
        event = self.store.write_event(
            "Claim.Created",
            "actor",
            {"id": "claim-1", "statement": "Test statement"}
        )

        retrieved = self.store.get_event(event.event_id)
        original_payload = retrieved.payload.copy()

        assert not hasattr(self.store, 'update_event'), "EventStore API should not have update method"
        assert not hasattr(self.store, 'delete_event'), "EventStore API should not have delete method"

        retrieved_after = self.store.get_event(event.event_id)
        assert retrieved_after.payload == original_payload


if __name__ == "__main__":
    pytest.main([__file__, "-v"])