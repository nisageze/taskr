# taskr

A command-line task manager written in Python. It lets you add, list, remove and mark tasks as done.

## Requirements

- Python 3.12 or newer
- uv

## Installation

Install as a command-line tool:

```
uv tool install git+https://github.com/nisageze/taskr
```

To uninstall:

```
uv tool uninstall taskr
```

Or run from source:

```
git clone https://github.com/nisageze/taskr.git
cd taskr
uv sync
uv run taskr --help
```

When running from source, prefix commands with `uv run`.

## Usage

### Add a task

```
$ taskr add "Read a book"
Task 1 added.

$ taskr add "Pay the bills" --priority high --due 2026-12-01
Task 2 added.
```

Options:

- `--priority`: `low`, `medium` or `high` (default: `medium`)
- `--due`: due date in `YYYY-MM-DD` format

### List tasks

```
$ taskr list
ID PRIORITY STATUS  DUE         TITLE
-- -------- ------- ----------- -----------------------
1  medium   pending -           Read a book
2  high     pending 2026-12-01  Pay the bills
3  medium   pending 2026-09-01  ! Submit the report
```

`!` marks a pending task whose due date has passed. When there are no tasks, `taskr list` prints `No tasks yet.`

### Mark a task as done

```
$ taskr done 1
Task 1 completed.

$ taskr done 1
Task 1 is already completed.
```

### Remove a task

```
$ taskr rm 2
Task 2 removed.
```

Removed IDs are not reused.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | taskr error, for example an unknown task ID, an invalid date, or running `taskr` without a command |
| 2 | Usage error, for example an unknown command or a missing argument |

```
$ taskr done 99
Error: Task 99 not found.

$ taskr add "Test" --due 01-12-2026
Error: Invalid date format. Expected YYYY-MM-DD.
```

`taskr` and `python -m taskr` return the same exit codes.

## Data storage

Tasks are stored as JSON in `~/.taskr/tasks.json`. The `~/.taskr` folder is created automatically when the first task is added.

If the file is corrupted, taskr exits with code 1 and leaves the file untouched:

```
$ taskr list
Error: Task file is corrupted (/home/user/.taskr/tasks.json).
```

## Development

From a clone, install the dependencies:

```
uv sync
```

Run the tests:

```
uv run pytest
```

Run all checks before committing:

```
./check.sh
```

`check.sh` runs type checking (mypy in strict mode), linting and format checks (ruff), and the test suite. It stops at the first failure.

## Project structure

- `src/taskr/`
  - `cli.py`: parses arguments, dispatches commands, prints output
  - `errors.py`: defines the exception hierarchy
  - `models.py`: Task dataclass, Priority and Status, overdue check
  - `storage.py`: reads and writes the tasks file as JSON
  - `__main__.py`: entry point for `python -m taskr`
- `tests/`: pytest test suite

## Design decisions

- **Strict layers.** `models.py` knows nothing about files or the terminal, `storage.py` never prints, and cli.py never reads or writes the file itself. For example, whether a task is overdue is computed by the `Task` itself and never stored.
- **One error path.** All taskr errors share a `TaskrError` base class. `cli.py` catches it once, prints an `Error:` line to stderr and exits with code 1, so users never see a traceback.
- **Safe writes.** Tasks are written to a temporary file first and then moved into place with `os.replace`, so the task file is never left half-written.
- **IDs are never reused.** The last assigned ID is stored in `tasks.json` together with the tasks, so both are always written in the same operation.

See [DECISIONS.md](DECISIONS.md) for the full decision log (in Turkish).

## Limitations

- The task file location is fixed to `~/.taskr/tasks.json` and cannot be configured.
- There is no `stats` command and `list` has no filters. Both were planned but left out of v0.1.0.
- Tasks are listed in the order they were added; there is no sorting.
- taskr is a single-user tool. Running two taskr commands at the same time is not supported.

## License

MIT. See [LICENSE](LICENSE).
