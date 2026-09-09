from taskr.storage import load


def test_load_returns_empty_when_file_missing(tmp_path):
    d = tmp_path / "test_task.json"
    test_data = load(d)
    assert test_data.tasks == []
