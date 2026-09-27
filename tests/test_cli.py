import os
import subprocess
import sys


def run_taskr(home, *args):
    env = os.environ.copy()
    env["HOME"] = str(home)
    return subprocess.run(
        [sys.executable, "-m", "taskr", *args],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_add_then_list_shows_task(tmp_path):
    added = run_taskr(tmp_path, "add", "Read Book")
    assert added.returncode == 0

    listed = run_taskr(tmp_path, "list")
    assert listed.returncode == 0
    assert "Read Book" in listed.stdout


def test_done_missing_id_fails(tmp_path):
    done_missing = run_taskr(tmp_path, "done", "99")
    assert done_missing.returncode == 1
    assert "Error:" in done_missing.stderr


def test_add_invalid_date_fails(tmp_path):
    invalid_date = run_taskr(tmp_path, "add", "Read Book", "--due", "2026-13-45")
    assert invalid_date.returncode == 1
    assert "Error:" in invalid_date.stderr


def test_add_empty_title_fails(tmp_path):
    empty_title = run_taskr(tmp_path, "add", "   ")
    assert empty_title.returncode == 1


def test_no_command_fails(tmp_path):
    no_command = run_taskr(tmp_path)
    assert no_command.returncode == 1


def test_unknown_command_exits_2(tmp_path):
    unknown_command = run_taskr(tmp_path, "fly")
    assert unknown_command.returncode == 2


def test_tasks_file_is_isolated(tmp_path):
    run_taskr(tmp_path, "add", "Read Book")
    assert (tmp_path / ".taskr" / "tasks.json").exists()


def test_add_with_priority_shows_in_list(tmp_path):
    priority_high = run_taskr(tmp_path, "add", "Read Book", "--priority", "high")
    assert priority_high.returncode == 0

    listed = run_taskr(tmp_path, "list")
    assert "high" in listed.stdout
