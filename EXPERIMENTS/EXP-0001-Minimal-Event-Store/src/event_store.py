import sqlite3
import json
from datetime import datetime
from uuid import uuid4, UUID
from typing import List, Optional, Dict, Any

from .models import Event


class EventStore:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                actor TEXT NOT NULL,
                payload TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_actor ON events(actor)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)
        """)
        self.conn.commit()

    def write_event(self, event_type: str, actor: str, payload: Dict[str, Any]) -> Event:
        event_id = uuid4()
        timestamp = datetime.utcnow().isoformat()
        payload_json = json.dumps(payload)

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO events (event_id, event_type, timestamp, actor, payload)
            VALUES (?, ?, ?, ?, ?)
        """, (str(event_id), event_type, timestamp, actor, payload_json))
        self.conn.commit()

        return Event(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.fromisoformat(timestamp),
            actor=actor,
            payload=payload
        )

    def get_event(self, event_id: UUID) -> Optional[Event]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT event_id, event_type, timestamp, actor, payload
            FROM events
            WHERE event_id = ?
        """, (str(event_id),))
        row = cursor.fetchone()

        if row:
            return Event(
                event_id=UUID(row[0]),
                event_type=row[1],
                timestamp=datetime.fromisoformat(row[2]),
                actor=row[3],
                payload=json.loads(row[4])
            )
        return None

    def get_events_by_type(self, event_type: str) -> List[Event]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT event_id, event_type, timestamp, actor, payload
            FROM events
            WHERE event_type = ?
            ORDER BY timestamp
        """, (event_type,))
        return self._rows_to_events(cursor.fetchall())

    def get_events_by_actor(self, actor: str) -> List[Event]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT event_id, event_type, timestamp, actor, payload
            FROM events
            WHERE actor = ?
            ORDER BY timestamp
        """, (actor,))
        return self._rows_to_events(cursor.fetchall())

    def get_all_events(self) -> List[Event]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT event_id, event_type, timestamp, actor, payload
            FROM events
            ORDER BY timestamp
        """)
        return self._rows_to_events(cursor.fetchall())

    def materialize_object(self, object_id: str) -> Dict[str, Any]:
        events = self.get_all_events()
        state = {"id": object_id, "events": []}

        for event in events:
            payload = event.payload
            if payload.get("id") == object_id:
                state["events"].append({
                    "type": event.event_type,
                    "timestamp": event.timestamp.isoformat(),
                    "actor": event.actor,
                    **payload
                })

                if event.event_type.endswith(".Created"):
                    state.update(payload)
                elif event.event_type.endswith(".StatusChanged"):
                    state["status"] = payload.get("to")

        return state

    def _rows_to_events(self, rows) -> List[Event]:
        events = []
        for row in rows:
            events.append(Event(
                event_id=UUID(row[0]),
                event_type=row[1],
                timestamp=datetime.fromisoformat(row[2]),
                actor=row[3],
                payload=json.loads(row[4])
            ))
        return events

    def close(self):
        self.conn.close()