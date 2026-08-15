"""The purpose of storage.py is to handle disk read and write operations for the tasks entered by the user."""
from dataclasses import asdict
from enum import Enum
import json
from datetime import date, datetime
from pathlib import Path


HOME_FOLDER = Path.home() / ".taskr"
HOME_FILE =  HOME_FOLDER / "tasks.json"
def load():
    ...

def ensure_folder():
    HOME_FOLDER.mkdir(parents = True,exist_ok=True)

def task_to_dict(task):
    return asdict(task)

def type_conversion(data):
    if isinstance(data, datetime):
        return data.isoformat()
    if isinstance(data, date):
        return data.isoformat()
    if isinstance(data, Enum):
        return data.value
    raise TypeError(f"Object of type {type(data).__name__} is not JSON serializable")



def save(tasks):
    ensure_folder()
    data = [task_to_dict(t) for t in tasks]
    with open(HOME_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, default=type_conversion, indent=2, ensure_ascii=False)
