import sqlalchemy as sql
from celery import shared_task
from celery.utils.log import get_task_logger

from db import FLASK_DB
from app.model.orm import Submission, Study

_LOGGER = get_task_logger(__name__)


@shared_task
def export_submission_data(submission_id):
    db_session = FLASK_DB.session
    _export_submission_data(db_session, submission_id)


@shared_task
def publish_eligible_studies():
    db_session = FLASK_DB.session
    _publish_eligible_studies(db_session)


def _export_submission_data(db_session, submission_id):
    submission = db_session.get(Submission, submission_id)
    message = "Study update."

    if submission.changelogText:
        changelog_text = " ".join(submission.changelogText.splitlines())
        message += f" Changes: {changelog_text}"

    submission.export_data(message=message)


def _publish_eligible_studies(db_session):
    unpublished_studies = db_session.scalars(
        sql.select(Study)
        .where(Study.embargoExpiresAt.is_not(None))
    ).all()

    for study in unpublished_studies:
        if study.isPublishable:
            _LOGGER.info(f"Publishing study: {study.publicId}")
            study.publish()
            db_session.add(study)

            if submission := study.lastSubmission:
                _LOGGER.info(f"Exporting data for study: {study.publicId}")
                submission.export_data(message="Study published")

    db_session.commit()
