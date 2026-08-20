"""The purpose of storage.py is to handle disk read and write operations for the tasks entered by the user."""
import json
from dataclasses import asdict
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from taskr.errors import CorruptStorageError
from taskr.models import Priority, Status, Task

HOME_FOLDER = Path.home() / ".taskr"
HOME_FILE =  HOME_FOLDER / "tasks.json"

def ensure_folder() -> None:
    HOME_FOLDER.mkdir(parents = True,exist_ok=True)

def task_to_dict(task:Task) -> dict[str,Any]:
    return asdict(task)

def type_conversion(data:Any) -> str:
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



def save(tasks: list[Task]) -> None:
    ensure_folder()
    data = [task_to_dict(t) for t in tasks]
    with open(HOME_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, default=type_conversion, indent=2, ensure_ascii=False)

def dict_to_task(dictionary: dict[str,Any]) -> Task:
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

    return Task(id=task_id,title=title,due_date=due_date,completed_at=completed_at,priority=priority,status=status,created_at=created_at)


def load() -> list[Task]:
    if not HOME_FILE.exists(): return []
    try:
        with open(HOME_FILE, "r", encoding="utf-8") as file:
            data = [dict_to_task(d) for d in json.load(file)]
        return data
    except json.JSONDecodeError as e:
        raise CorruptStorageError(HOME_FILE) from e
