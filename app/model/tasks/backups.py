import os

from celery import shared_task

from app.model.lib.backups import (
    generate_backup_filename,
    create_backup,
    clean_backups,
)


@shared_task
def create_backups():
    filename = generate_backup_filename()

    os.makedirs('var/backups', exist_ok=True)
    create_backup(f"var/backups/{filename}")
    clean_backups('var/backups', max_count=20)
