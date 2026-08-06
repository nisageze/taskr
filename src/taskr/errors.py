class TaskrError(Exception):
    pass

class TaskNotFoundError(TaskrError):
    def __init__(self, task_id):
        self.task_id = task_id
        super().__init__(f"{task_id} could not be found.")

class InvalidDateError(TaskrError):
    def __init__(self, invalid_date):
        self.invalid_date = invalid_date
        super().__init__(f"{invalid_date} is wrong. Expected YYYY-MM-DD.")

class CorruptStorageError(TaskrError):
    def __init__(self, invalid_file):
        self.invalid_file = invalid_file
        super().__init__(f"{invalid_file} could not be read.")
