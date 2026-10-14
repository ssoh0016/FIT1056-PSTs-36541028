# tests/test_admin_utils.py
import logging
import os

import pytest
from app.admin_utils import init_logger, backup_data


@pytest.fixture
def clean_root_logger():
    """Lets a test configure logging, then removes whatever it added (and closes the
    log file, which matters on Windows) so tests can't affect each other."""
    root = logging.getLogger()
    old_handlers = list(root.handlers)
    old_level = root.level
    yield root
    for handler in list(root.handlers):
        if handler not in old_handlers:
            root.removeHandler(handler)
            handler.close()
    root.setLevel(old_level)


@pytest.fixture
def data_file(tmp_path):
    path = tmp_path / "msms.json"
    path.write_text('{"students": []}')
    return path


# ----------------------------------------------------------------------
# backup_data
# ----------------------------------------------------------------------
def test_backup_data_creates_a_timestamped_copy(data_file, tmp_path):
    backup_dir = tmp_path / "backups"
    result = backup_data(str(data_file), str(backup_dir))
    files = os.listdir(backup_dir)
    assert result is True
    assert len(files) == 1
    assert files[0].startswith("msms_backup_") and files[0].endswith(".json")
    assert (backup_dir / files[0]).read_text() == '{"students": []}'


def test_backup_data_creates_the_backup_folder_if_missing(data_file, tmp_path):
    backup_dir = tmp_path / "does" / "not" / "exist"
    assert backup_data(str(data_file), str(backup_dir)) is True
    assert backup_dir.is_dir()


def test_backup_data_with_missing_source_returns_false(tmp_path):
    backup_dir = tmp_path / "backups"
    assert backup_data(str(tmp_path / "nothing_here.json"), str(backup_dir)) is False
    assert not backup_dir.exists()


# ----------------------------------------------------------------------
# init_logger
# ----------------------------------------------------------------------
def test_init_logger_writes_formatted_lines_to_the_file(tmp_path, clean_root_logger):
    log_file = tmp_path / "test.log"
    init_logger(str(log_file))
    logging.info("hello backup")
    text = log_file.read_text()
    assert "INFO" in text           # level name
    assert "hello backup" in text   # message
    assert " - " in text            # timestamp - level - message format


def test_init_logger_ignores_debug_messages(tmp_path, clean_root_logger):
    log_file = tmp_path / "test.log"
    init_logger(str(log_file))
    logging.debug("too detailed to keep")
    assert "too detailed to keep" not in log_file.read_text()


def test_init_logger_called_twice_does_not_duplicate_lines(tmp_path, clean_root_logger):
    log_file = tmp_path / "test.log"
    init_logger(str(log_file))
    init_logger(str(log_file))   # Streamlit re-runs scripts, so this really happens
    logging.info("only once please")
    assert log_file.read_text().count("only once please") == 1
