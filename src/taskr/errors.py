from pathlib import Path


class TaskrError(Exception):
    pass


class TaskNotFoundError(TaskrError):
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found.")


class InvalidDateError(TaskrError):
    def __init__(self, invalid_date: str) -> None:
        self.invalid_date = invalid_date
        super().__init__("Invalid date format. Expected YYYY-MM-DD.")


class CorruptStorageError(TaskrError):
    def __init__(self, invalid_file: Path) -> None:
        self.invalid_file = invalid_file
        super().__init__(f"Task file is corrupted ({invalid_file}).")
