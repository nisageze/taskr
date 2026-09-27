import argparse
import sys
from collections.abc import Callable
from datetime import date, datetime

from taskr.errors import InvalidDateError, InvalidTitleError, TaskrError
from taskr.models import Priority, Status, Task, find_task
from taskr.storage import load, save


def main() -> int:
    parser = argparse.ArgumentParser(prog="taskr", description="task managing program")

    subparsers = parser.add_subparsers(help="choose one command")

    add_arg = subparsers.add_parser("add", help="add tasks")
    add_arg.set_defaults(func=add_func)
    add_arg.add_argument("title", help="task title")
    add_arg.add_argument("--due", help="due date for task", type=date_format_check)
    add_arg.add_argument(
        "--priority", help="task priority", choices=[p.value for p in Priority]
    )

    list_arg = subparsers.add_parser("list", help="list tasks")
    list_arg.set_defaults(func=list_func)

    done_arg = subparsers.add_parser("done", help="mark a task as done")
    done_arg.set_defaults(func=done_func)
    done_arg.add_argument("id", help="task id", type=int)

    rm_arg = subparsers.add_parser("rm", help="remove task")
    rm_arg.set_defaults(func=rm_func)
    rm_arg.add_argument("id", help="task id", type=int)

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
        return datetime.strptime(d, "%Y-%m-%d").date()  # noqa: DTZ007
    except ValueError as e:
        raise InvalidDateError(d) from e


def add_func(args: argparse.Namespace) -> None:

    if not args.title.strip():
        raise InvalidTitleError(args.title)

    task_data = load()

    new_id = task_data.last_id + 1
    task_data.last_id = new_id

    if args.priority is None:
        new_task = Task(id=new_id, title=args.title, due_date=args.due)
    else:
        new_task = Task(
            id=new_id,
            title=args.title,
            priority=Priority(args.priority),
            due_date=args.due,
        )

    task_data.tasks.append(new_task)
    save(task_data)
    print(f"Task {new_task.id} added.")


def list_func(args: argparse.Namespace) -> None:
    task_data = load()

    if not task_data.tasks:
        print("No tasks yet.")
        return

    print(f"{'ID':<3}{'PRIORITY':<9}{'STATUS':<8}{'DUE':<12}{'TITLE'}")
    print(
        f"{'--':<3}{'--------':<9}{'-------':<8}{'-----------':<12}{'-----------------------'}"
    )

    for task in task_data.tasks:
        due_date = task.due_date.isoformat() if task.due_date is not None else "-"
        mark = "! " if task.is_overdue() else ""

        print(
            f"{task.id:<3}{task.priority.value:<9}{task.status.value:<8}{due_date:<12}{mark}{task.title}"
        )


def done_func(args: argparse.Namespace) -> None:
    task_data = load()
    task = find_task(task_data.tasks, args.id)

    if task.status == Status.DONE:
        print(f"Task {task.id} is already completed.")
    else:
        task.mark_done()
        save(task_data)
        print(f"Task {task.id} completed.")


def rm_func(args: argparse.Namespace) -> None:
    task_data = load()
    task = find_task(task_data.tasks, args.id)

    task_data.tasks.remove(task)
    save(task_data)
    print(f"Task {task.id} removed.")
