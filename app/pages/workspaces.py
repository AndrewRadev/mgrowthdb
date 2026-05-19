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
import app.model.lib.util as util


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
    workspace = _find_workspace(orcidId, name)

    left_axis_workspace_ids  = util.parse_comma_separated_request_ids('l')
    right_axis_workspace_ids = util.parse_comma_separated_request_ids('r')

    chart_form = ComparativeChartForm(
        g.db_session,
        left_axis_workspace_ids=left_axis_workspace_ids,
        right_axis_workspace_ids=right_axis_workspace_ids,
    )

    return render_template(
        "pages/workspaces/visualize.html",
        workspace=workspace,
        chart_form=chart_form,
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


def workspaces_chart_fragment(orcidId, name="default"):
    workspace = _find_workspace(orcidId, name)
    args = request.form.to_dict()

    width = args.get('width', None)

    chart_form = ComparativeChartForm(
        g.db_session,
        show_std=args.get('showStd', None) is not None,
    )
    chart = chart_form.build_chart(args, width, user=g.current_user)

    return render_template(
        'pages/workspaces/_chart.html',
        chart_form=chart_form,
        chart=chart,
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
