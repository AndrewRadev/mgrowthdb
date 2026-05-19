import pandas as pd
import sqlalchemy as sql
from flask import (
    g,
    render_template,
    redirect,
    request,
)
from werkzeug.exceptions import Forbidden

from app.model.lib.chart import Chart
from app.model.lib.errors import LoginRequired
from app.view.forms.comparative_chart_form import ComparativeChartForm
from app.model.orm import (
    User,
    Workspace,
    WorkspaceEntry,
)


def workspaces_index_page(orcidId, name="default"):
    errors = {}
    workspace = _find_workspace(orcidId, name)

    if request.method == 'POST':
        file = request.files['data']

        new_entries = WorkspaceEntry.from_csv(
            file,
            g.current_user,
            include_error=request.form.get('includeError', False),
            metadata={
                'dataType':    request.form.get('dataType'),
                'subjectType': request.form.get('subjectType'),
                'units':       request.form.get('units'),
            }
        )
        g.db_session.add_all(new_entries)
        g.db_session.commit()

    return render_template(
        "pages/workspaces/index.html",
        workspace=workspace,
        errors=errors,
    )


def workspaces_visualize_page(orcidId, name="default"):
    chart = Chart(time_units='h')
    chart_form = ComparativeChartForm(g.db_session)
    errors = {}
    workspace = _find_workspace(orcidId, name)

    return render_template(
        "pages/workspaces/visualize.html",
        workspace=workspace,
        chart_form=chart_form,
        chart=chart,
        errors=errors,
    )


def workspaces_data_preview_fragment():
    file = request.files['file']
    df = pd.read_csv(file)

    # TODO (2026-05-14) Error handling
    errors = []

    return render_template(
        "pages/workspaces/_data_preview.html",
        df=df,
        errors=errors,
    )


def _find_workspace(orcidId, name):
    workspace = g.db_session.scalars(
        sql.select(Workspace)
        .join(User)
        .where(User.orcidId == orcidId)
        .where(Workspace.name == name)
        .limit(1)
    ).one()

    if g.current_user != workspace.user and not workspace.isPublished:
        raise Forbidden

    return workspace
