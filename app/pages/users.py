import os
from uuid import uuid4
from datetime import datetime, UTC

from flask import (
    g,
    render_template,
    redirect,
    request,
    session,
    flash,
    current_app,
    url_for,
)
import sqlalchemy as sql
from werkzeug.exceptions import NotFound

from app.model.orm import (
    Project,
    ProjectUser,
    Study,
    StudyStrain,
    StudyUser,
    User,
    Workspace,
)
from app.model.lib import orcid
from app.model.lib.errors import LoginRequired


def user_show_page():
    if not g.current_user:
        raise LoginRequired()

    custom_strains = g.db_session.scalars(
        sql.select(StudyStrain)
        .where(
            StudyStrain.userUniqueID == g.current_user.uuid,
            StudyStrain.defined.is_(False),
            StudyStrain.notUnknown,
        )
        .order_by(StudyStrain.name.desc())
    ).all()

    return render_template(
        'pages/users/show.html',
        custom_strains=custom_strains,
    )


def user_login_page():
    orcid_client_id = current_app.config["ORCID_CLIENT_ID"]

    if 'code' in request.args:
        user_data = orcid.authenticate_user(
            code=request.args['code'],
            client_id=orcid_client_id,
            client_secret=current_app.config["ORCID_SECRET"],
            app_host=request.host,
        )

        user = _find_or_create_user(g.db_session, user_data, session['user_uuid'])
        session['user_uuid'] = user.uuid

        return redirect(url_for('user_show_page'))
    else:
        orcid_url = orcid.get_login_url(orcid_client_id, request.host)

        return render_template(
            "pages/users/login.html",
            orcid_url=orcid_url,
        )


def user_backdoor_page():
    app_env = os.getenv('APP_ENV', 'development')
    if app_env not in ('development', 'test'):
        raise NotFound()

    if request.method == 'POST':
        session['user_uuid'] = request.form['user_uuid'].strip()
        return redirect(url_for('static_home_page'))
    else:
        return render_template("pages/users/backdoor.html")


def user_claim_project_action():
    if not g.current_user:
        raise LoginRequired()

    project_uuid = request.form['uuid'].strip()
    user_uuid    = g.current_user.uuid

    project = g.db_session.scalars(
        sql.select(Project)
        .where(Project.uuid == project_uuid)
        .limit(1)
    ).one_or_none()

    if not project:
        flash(f"A project with this UUID couldn't be found: {repr(project_uuid)}", 'error')
        return redirect(request.referrer)

    # Check for link existence:
    project_user = g.db_session.scalars(
        sql.select(ProjectUser)
        .where(
            ProjectUser.userUniqueID == user_uuid,
            ProjectUser.projectUniqueID == project_uuid,
        )
        .limit(1)
    ).one_or_none()

    if project_user:
        flash(f"You already have access to this project: [{project.publicId}] {project.name}", "error")
    else:
        # Create link:
        g.db_session.add(ProjectUser(userUniqueID=user_uuid, projectUniqueID=project_uuid))
        g.db_session.commit()

    return redirect(request.referrer)


def user_claim_study_action():
    if not g.current_user:
        raise LoginRequired()

    study_uuid = request.form['uuid'].strip()
    user_uuid  = g.current_user.uuid

    study = g.db_session.scalars(
        sql.select(Study)
        .where(Study.uuid == study_uuid)
        .limit(1)
    ).one_or_none()

    if not study:
        flash(f"A study with this UUID couldn't be found: {repr(study_uuid)}", 'error')
        return redirect(request.referrer)

    # Check for link existence:
    study_user = g.db_session.scalars(
        sql.select(StudyUser)
        .where(
            StudyUser.userUniqueID == user_uuid,
            StudyUser.studyUniqueID == study_uuid,
        )
        .limit(1)
    ).one_or_none()

    if study_user:
        flash(f"You already have access to this study: [{study.publicId}] {study.name}", "error")
    else:
        # Create link to study:
        g.db_session.add(StudyUser(userUniqueID=user_uuid, studyUniqueID=study_uuid))
        g.db_session.commit()

    # Check for project link existence:
    project_user = g.db_session.scalars(
        sql.select(ProjectUser)
        .where(
            ProjectUser.userUniqueID == user_uuid,
            ProjectUser.projectUniqueID == study.projectUuid,
        )
        .limit(1)
    ).one_or_none()

    if not project_user:
        # Create link to project:
        g.db_session.add(ProjectUser(userUniqueID=user_uuid, projectUniqueID=study.projectUuid))
        g.db_session.commit()

    return redirect(request.referrer)


def user_logout_action():
    if 'user_uuid' in session:
        del session['user_uuid']
    if 'submission_id' in session:
        del session['submission_id']

    return redirect(url_for('static_home_page'))


def user_reset_api_key_action():
    g.current_user.apiKey = str(uuid4())

    g.db_session.add(g.current_user)
    g.db_session.commit()

    return redirect(url_for('user_show_page'))


def _find_or_create_user(db_session, user_data, user_uuid):
    user = db_session.scalars(
        sql.select(User)
        .where(User.orcidId == user_data['orcid'])
        .limit(1)
    ).one_or_none()

    if not user:
        user = User(
            uuid=user_uuid,
            orcidId=user_data['orcid'],
            apiKey=str(uuid4),
        )
        workspace = Workspace(name="default", user=user)

    user.name        = user_data['name']
    user.orcidToken  = user_data['access_token']
    user.lastLoginAt = datetime.now(UTC)

    db_session.add(user)
    db_session.commit()

    return user
