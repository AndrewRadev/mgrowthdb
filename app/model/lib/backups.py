import os
import subprocess
from datetime import datetime
from pathlib import Path

from db import get_cli_connection_params


def generate_backup_filename():
    timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    return f"{timestamp}_backup.sql"


def create_backup(full_path):
    print(f"Creating backup: {full_path}")
    connection_params = get_cli_connection_params()

    result = subprocess.run([
        '/usr/bin/mysqldump',
        *connection_params,
        '-u', 'root',
        '--result-file', full_path
    ])
    result.check_returncode()


def clean_backups(backup_dir, max_count):
    backup_dir_path = Path(backup_dir)
    files = list(reversed(sorted(backup_dir_path.glob('*.sql'))))

    deletable_files = files[max_count:]

    if deletable_files:
        print(f"Deleting {len(deletable_files)} older files")
        for file in deletable_files:
            os.unlink(file)
