import sqlalchemy as sql

from db import get_session
from app.model.orm import Study

with get_session() as db_session:
    studies = db_session.scalars(
        sql.select(Study)
        .order_by(Study.publicId)
    ).all()

    for study in studies:
        submission = study.find_last_submission(db_session)

        study.lastSubmission = submission
        db_session.add(study)

        if study.isPublished:
            submission.publishedAt = study.publishedAt
            db_session.add(submission)

    db_session.commit()
