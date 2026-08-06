from taskr.models import Task
from taskr.errors import TaskrError

def main():
    task1 = Task(id=1,title="import deneme")
    print(task1)
