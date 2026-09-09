"""The purpose of storage.py is to handle disk read and write operations for the tasks entered by the user."""

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from taskr.errors import CorruptStorageError
from taskr.models import Priority, Status, Task

TASKR_FOLDER = Path.home() / ".taskr"
TASKR_FILE = TASKR_FOLDER / "tasks.json"

@dataclass
class TaskData:
    tasks: list[Task]
    last_id: int

def ensure_folder(taskr_file: Path = TASKR_FILE) -> None:
    taskr_file.parent.mkdir(parents=True, exist_ok=True)


def task_to_dict(task: Task) -> dict[str, Any]:
    return asdict(task)


def json_serialize(data: Any) -> str:
    if isinstance(data, datetime):
        return data.isoformat()
    if isinstance(data, date):
        return data.isoformat()
    if isinstance(data, Enum):
        value = data.value
        if isinstance(value, str):
            return value
        raise TypeError(f"Object of type {type(value).__name__} have to be str.")
    raise TypeError(f"Object of type {type(data).__name__} is not JSON serializable")


def save(data: TaskData, taskr_file: Path = TASKR_FILE) -> None:
    ensure_folder(taskr_file)
    tasks_data = [task_to_dict(t) for t in data.tasks]
    id_data = data.last_id
    tasks_dict = {"tasks": tasks_data, "last_id": id_data}
    with open(taskr_file, "w", encoding="utf-8") as file:
        json.dump(task_data, file, default=json_serialize, indent=2, ensure_ascii=False)


def dict_to_task(dictionary: dict[str, Any]) -> Task:
    task_id = dictionary["id"]
    title = dictionary["title"]
    if dictionary["due_date"] is None:
        due_date = None
    else:
        due_date = date.fromisoformat(dictionary["due_date"])
    if dictionary["completed_at"] is None:
        completed_at = None
    else:
        completed_at = datetime.fromisoformat(dictionary["completed_at"])
    priority = Priority(dictionary["priority"])
    status = Status(dictionary["status"])
    created_at = datetime.fromisoformat(dictionary["created_at"])

    return Task(
        id=task_id,
        title=title,
        due_date=due_date,
        completed_at=completed_at,
        priority=priority,
        status=status,
        created_at=created_at,
    )


def load(taskr_file: Path = TASKR_FILE) -> TaskData:
    if not taskr_file.exists():
        return TaskData([], 0)
    try:
        with open(taskr_file, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        raise CorruptStorageError(taskr_file) from e
    task_data = [dict_to_task(d) for d in data["tasks"]]
    return TaskData(task_data, data["last_id"])
