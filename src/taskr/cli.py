import argparse
import sys
from collections.abc import Callable
from datetime import date, datetime

from taskr.errors import InvalidDateError, TaskrError
from taskr.models import Task
from taskr.storage import load, save


def main() -> int:
    parser = argparse.ArgumentParser(prog="taskr", description="task managing program")

    subparsers = parser.add_subparsers(help="choose one command")

    add_arg = subparsers.add_parser("add", help="add tasks")
    add_arg.set_defaults(func=add_func)
    add_arg.add_argument("title", help="task title")
    add_arg.add_argument("--due", help="due date for task", type=date_format_check)
    add_arg.add_argument("--priority", help="high, medium, low priority", choices=["high", "medium", "low"])

    list_arg = subparsers.add_parser("list", help="list tasks")
    list_arg.set_defaults(func=list_func)
    subparsers.add_parser("done", help="mark a task as done")
    subparsers.add_parser("rm", help="remove task")
    subparsers.add_parser("stats", help="list stats")

    try:
        args = parser.parse_args()

        if not hasattr(args, "func"):
            parser.print_help()
            return 1

        handler: Callable[[argparse.Namespace], None] = args.func
        handler(args)
        return 0

    except TaskrError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

def date_format_check(d: str) -> date:
    try:
        return datetime.strptime(d, "%Y-%m-%d").date() # noqa: DTZ007
    except ValueError as e:
        raise InvalidDateError(d) from e

def add_func(args: argparse.Namespace) -> None:
    task_data = load()

    max_id = 0
    if not task_data.tasks:
        new_id = 1
    else:
        for task in task_data.tasks:
            max_id = max(max_id, task.id)
        new_id = max_id + 1

    if args.priority is None:
        new_task = Task(id=new_id, title=args.title,  due_date=args.due)
    else:
        new_task = Task(id=new_id, title=args.title, priority=args.priority, due_date=args.due)


    task_data.tasks.append(new_task)
    save(task_data)



def list_func(args: argparse.Namespace) -> None:
    task_data = load()

    if not task_data.tasks:
        print("No tasks yet.")
        return

    print(f"{"ID":<3}{"PRIORITY":<9}{"STATUS":<8}{"DUE":<12}{"TITLE"}")
    print(f"{"--":<3}{"--------":<9}{"-------":<8}{"-----------":<12}{"-----------------------"}")

    for task in task_data.tasks:
        due_date = task.due_date.isoformat() if task.due_date is not None else "-"
        mark = "! " if task.is_overdue() else ""

        print(f"{task.id:<3}{task.priority.value:<9}{task.status.value:<8}{due_date:<12}{mark}{task.title}")
