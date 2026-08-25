import argparse


def main() -> int:
    parser = argparse.ArgumentParser(prog='taskr', description='task list program')

    subparsers = parser.add_subparsers(help='subcommand help')

    subparsers.add_parser('add', help='add tasks')
    subparsers.add_parser('list', help='list tasks')
    subparsers.add_parser('done', help='done task')
    subparsers.add_parser('rm', help='deleting task')
    subparsers.add_parser('stats', help='list stats')

    parser.parse_args()

    return 0
