class TaskrError(Exception):
    pass

class TaskNotFoundError(TaskrError):
    def __init__(self, task_id):
        self.wrong_id = task_id
        super().__init__(f"{task_id} could not be found.")

class InvalidDateError(TaskrError):
    def __init__(self, invalid_date):
        self.wrong_date = invalid_date
        super().__init__(f"{invalid_date} is wrong. Expected YYYY-MM-DD.")

class CorruptStorageError(TaskrError):
    def __init__(self, invalid_file):
        self.wrong_path = invalid_file
        super().__init__(f"{invalid_file} could not be read.")

try:
    raise TaskNotFoundError(1)
except TaskrError as e:
    print(e)

try:
    raise InvalidDateError("12.08.2026")
except TaskrError as e:
    print(e)

try:
    raise CorruptStorageError("~/.taskr/tasks.json")
except TaskrError as e:
    print(e)
