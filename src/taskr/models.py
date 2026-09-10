from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum

from taskr.errors import TaskNotFoundError


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

    def is_overdue(self) -> bool:
        if self.due_date is None:
            return False
        else:
            # taskr is a single-user local CLI;
            # overdue status is intentionally evaluated in the user's local timezone.
            return self.due_date < date.today()  # noqa: DTZ011

    def mark_done(self) -> None:
        self.status = Status.DONE
        self.completed_at = datetime.now() # noqa: DTZ005



def find_task(tasks:list[Task], task_id: int) -> Task:
    for task in tasks:
        if task.id == task_id:
            return task
    raise TaskNotFoundError(task_id)
