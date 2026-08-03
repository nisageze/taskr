from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    DONE = "done"

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass

class Task:
    id: int
    title: str
    due_date: date | None = None
    completed_at: datetime | None = None
    priority: Priority = Priority.MEDIUM
    status: Status = Status.PENDING
    created_at: datetime = field(default_factory=datetime.now)
