from celery import shared_task

from db import FLASK_DB
from app.model.orm import Submission


@shared_task
def export_submission_data(submission_id):
    db_session = FLASK_DB.session
    _export_submission_data(db_session, submission_id)


def _export_submission_data(db_session, submission_id):
    submission = db_session.get(Submission, submission_id)
    message = "Study update."

    if submission.changelogText:
        changelog_text = " ".join(submission.changelogText.splitlines())
        message += f" Changes: {changelog_text}"

    submission.export_data(message=message)
