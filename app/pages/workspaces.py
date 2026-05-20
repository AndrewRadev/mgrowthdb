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

        df, errors = _process_upload(file)
        if df is not None:
            new_entries = WorkspaceEntry.from_upload(
                df,
                workspace,
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
    include_error = request.form.get('includeError', 'false') == 'true'

    df, errors = _process_upload(file)

    return render_template(
        "pages/workspaces/_data_preview.html",
        df=df,
        include_error=include_error,
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


def _process_upload(file):
    errors = []

    try:
        df = pd.read_csv(file)
    except RuntimeError:
        errors.append(f"Could not process file {file.filename}")
        return None, errors

    column_count = len(df.columns)
    if column_count <= 2:
        errors.append(f"At least 2 columns are expected, {column_count} were found")

    row_count = df.shape[0]
    if row_count <= 0:
        errors.append("No data rows were found")

    return df, errors
