from flask import (
    g,
    session,
    redirect,
    url_for,
    request,
)
import sqlalchemy as sql
from werkzeug.exceptions import Forbidden

from app.model.orm import Submission
from app.model.lib.errors import LoginRequired
from app.view.forms.submission_form import SubmissionForm


def edit_submission_action(id):
    session['submission_id'] = id

    return redirect(url_for('upload_status_page'))


def delete_submission_action(id):
    if not g.current_user:
        raise Forbidden

    submission = g.db_session.get(Submission, id)

    if submission.userUniqueID != g.current_user.uuid:
        raise Forbidden

    if 'submission_id' in session and session['submission_id'] == id:
        del session['submission_id']

    g.db_session.execute(sql.delete(Submission).where(Submission.id == id))
    g.db_session.commit()

    return redirect(url_for('upload_status_page'))
