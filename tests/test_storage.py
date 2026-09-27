from datetime import date, datetime

import pytest

from taskr.errors import CorruptStorageError
from taskr.models import Priority, Status, Task
from taskr.storage import TaskData, load, save


def test_load_returns_empty_when_file_missing(tmp_path):
    d = tmp_path / "test_task.json"
    test_data = load(d)
    assert test_data.tasks == []


def test_save_load_equality(tmp_path):
    task = Task(
        id=3,
        title="Read Book",
        due_date=date(2026, 8, 1),
        completed_at=datetime(2026, 8, 3),  # noqa: DTZ001
        priority=Priority.HIGH,
        status=Status.DONE,
        created_at=datetime(2026, 8, 1, 15, 47, 42, 809378),  # noqa: DTZ001
    )
    data = TaskData([task], 3)

    d = tmp_path / "test_task.json"
    save(data, d)
    test_data = load(d)

    assert test_data == data


def test_load_raises_on_invalid_json(tmp_path):
    d = tmp_path / "test_task.json"
    d.write_text("test", encoding="utf-8")
    with pytest.raises(CorruptStorageError):
        load(d)


def test_load_raises_on_wrong_structure(tmp_path):
    d = tmp_path / "test_task.json"
    d.write_text('{"last_id": 0}', encoding="utf-8")
    with pytest.raises(CorruptStorageError):
        load(d)


def test_load_raises_on_invalid_task_fields(tmp_path):
    d = tmp_path / "test_task.json"
    d.write_text('{"tasks": [{"id": 1}], "last_id": 1}', encoding="utf-8")
    with pytest.raises(CorruptStorageError):
        load(d)
