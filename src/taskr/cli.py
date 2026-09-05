import argparse
import sys
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

    subparsers.add_parser("list", help="list tasks")
    subparsers.add_parser("done", help="mark a task as done")
    subparsers.add_parser("rm", help="remove task")
    subparsers.add_parser("stats", help="list stats")

    try:
        args = parser.parse_args()

        if not hasattr(args, "func"):
            parser.print_help()
            return 1

        # TODO: mypy no-any-return — args.func is Any because Namespace has no
        # declared fields. Decision deferred to the block where --due and --priority
        # are bound; both hit the same Any boundary.

        return args.func(args)
    except TaskrError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

def date_format_check(d: str) -> date:
    try:
        return datetime.strptime(d, "%Y-%m-%d").date() # noqa: DTZ007
    except ValueError as e:
        raise InvalidDateError(d) from e

def add_func(args: argparse.Namespace) -> int:
    task_list = load()

    max_id = 0
    if not task_list:
        new_id = 1
    else:
        for task in task_list:
            max_id = max(max_id, task.id)
        new_id = max_id + 1

    if args.priority is None:
        new_task = Task(id=new_id, title=args.title,  due_date=args.due)
    else:
        new_task = Task(id=new_id, title=args.title, priority=args.priority, due_date=args.due)


    task_list.append(new_task)
    save(task_list)

    return 0
