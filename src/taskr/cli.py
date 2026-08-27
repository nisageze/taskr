import argparse
from datetime import date, datetime

from taskr.errors import InvalidDateError
from taskr.models import Task
from taskr.storage import load


def main() -> int:
    parser = argparse.ArgumentParser(prog='taskr', description='task list program')

    subparsers = parser.add_subparsers(help='subcommand help')

    add_arg = subparsers.add_parser('add', help='add tasks')
    add_arg.set_defaults(func=add_func)
    add_arg.add_argument('title', help='task title')
    add_arg.add_argument('--due', help='due date for task', type=date_format_check)
    add_arg.add_argument('--priority', help='HIGH, MEDIUM, LOW priority', choices=['high', 'medium', 'low'])

    subparsers.add_parser('list', help='list tasks')
    subparsers.add_parser('done', help='done task')
    subparsers.add_parser('rm', help='deleting task')
    subparsers.add_parser('stats', help='list stats')

    parser.parse_args()

    return 0

def date_format_check(d: str) -> date:
    try:
        return datetime.strptime(d, "%Y-%m-%d").date() # noqa: DTZ007
    except ValueError as e:
        raise InvalidDateError(f"Error: Invalid date format. {d}") from e

def add_func() -> list[Task]:
    task_list = load()
    return task_list
