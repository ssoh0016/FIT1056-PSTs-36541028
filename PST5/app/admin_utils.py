# app/admin_utils.py
import logging
import shutil
import datetime
import os

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'


def init_logger(log_file="msms.log"):
    """Configures the root logger to write INFO-and-above messages to a file.

    Safe to call more than once (Streamlit re-runs the app script on every click):
    if the root logger already writes to this file, nothing is added a second time,
    so log lines are never duplicated.
    """
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    target = os.path.abspath(log_file)
    for handler in root.handlers:
        if isinstance(handler, logging.FileHandler) and handler.baseFilename == target:
            return  # already configured for this file

    file_handler = logging.FileHandler(log_file, mode='a')   # append to the log file
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(file_handler)
    print(f"Logging configured. Outputting to {log_file}")


def backup_data(data_path="data/msms.json", backup_dir="data/backups"):
    """Creates a timestamped backup of the main data file. Returns True on success."""
    # Nothing to back up on a brand-new install: that's not an error worth crashing over.
    if not os.path.exists(data_path):
        logging.warning(f"Backup skipped: {data_path} does not exist yet.")
        return False

    try:
        # Create the backup directory if it doesn't exist.
        os.makedirs(backup_dir, exist_ok=True)

        # Timestamp string, e.g. 2026-10-14_09-30-00
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filepath = os.path.join(backup_dir, f"msms_backup_{timestamp}.json")

        shutil.copy(data_path, backup_filepath)
        logging.info(f"Data successfully backed up to {backup_filepath}")
        return True
    except Exception as e:
        # Log any errors that occur during the backup process.
        logging.error(f"Failed to create backup: {e}")
        return False
