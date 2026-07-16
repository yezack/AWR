from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Event:
    event_id: UUID
    event_type: str
    timestamp: datetime
    actor: str
    payload: dict
