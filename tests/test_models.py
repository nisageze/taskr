from datetime import date, datetime, timedelta

from taskr.models import Status, Task


def test_task_without_due_date_is_not_overdue():
    task = Task(
            id=4,
            title="Read Book"
        )
    assert not task.is_overdue()


def test_past_due_date_is_overdue():
    task = Task(
            id=4,
            title="Read Book",
            due_date=date.today() - timedelta(days=1), # noqa: DTZ011
        )
    assert task.is_overdue()

def test_future_due_date_is_not_overdue():
    task = Task(
            id=4,
            title="Read Book",
            due_date=date.today() + timedelta(days=1),  # noqa: DTZ011
        )
    assert not task.is_overdue()

def test_due_today_is_not_overdue():
    task = Task(
            id=4,
            title="Read Book",
            due_date=date.today(), # noqa: DTZ011
        )
    assert not task.is_overdue()

def test_completed_task_is_never_overdue():
    task = Task(
            id=4,
            title="Read Book",
            due_date=date.today() - timedelta(days=3),  # noqa: DTZ011
            completed_at=datetime.today(), # noqa: DTZ002
            status=Status.DONE,
        )
    assert not task.is_overdue()
