import itertools

import pandas as pd
import sqlalchemy as sql
from flask import (
    g,
    render_template,
    redirect,
    request,
    url_for,
    session,
)
from werkzeug.exceptions import Forbidden

from app.model.lib.chart import Chart
from app.model.lib.errors import LoginRequired
from app.view.forms.comparative_chart_form import ComparativeChartForm
from app.model.orm import (
    MeasurementContext,
    ModelingResult,
    User,
    Workspace,
    WorkspaceEntry,
)
from app.model.lib.compare import init_compare_data
import app.model.lib.util as util


def workspaces_index_page(orcidId, name="default"):
    errors = {}
    workspace = _find_workspace(orcidId, name)

    if request.method == 'POST':
        file = request.files['data']

        df, errors = _process_upload(file)
        if df is not None:
            metadata = _extract_entry_metadata()

            new_entries = WorkspaceEntry.from_upload(
                df,
                workspace,
                include_error=request.form.get('includeError', False),
                metadata=metadata,
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

    compare_data = init_compare_data(session)

    comparable_measurement_contexts = g.db_session.scalars(
        sql.select(MeasurementContext)
        .where(MeasurementContext.id.in_(compare_data['contexts']))
    ).all()

    comparable_modeling_results = g.db_session.scalars(
        sql.select(ModelingResult)
        .where(ModelingResult.id.in_(compare_data['models']))
    ).all()

    comparable_records_by_study = {}

    for study, measurement_context_group in itertools.groupby(comparable_measurement_contexts, lambda mc: mc.study):
        if study not in comparable_records_by_study:
            comparable_records_by_study[study] = {'measurement_contexts': [], 'modeling_results': []}
        comparable_records_by_study[study]['measurement_contexts'] = list(measurement_context_group)

    for study, modeling_result_group in itertools.groupby(comparable_modeling_results, lambda mc: mc.study):
        if study not in comparable_records_by_study:
            comparable_records_by_study[study] = {'measurement_contexts': [], 'modeling_results': []}
        comparable_records_by_study[study]['modeling_results'] = list(modeling_result_group)

    left_axis_workspace_ids  = util.parse_comma_separated_request_ids('lw')
    right_axis_workspace_ids = util.parse_comma_separated_request_ids('rw')

    chart_form = ComparativeChartForm(
        g.db_session,
        left_axis_workspace_ids=left_axis_workspace_ids,
        right_axis_workspace_ids=right_axis_workspace_ids,
    )

    return render_template(
        "pages/workspaces/visualize.html",
        workspace=workspace,
        chart_form=chart_form,
        comparable_records_by_study=comparable_records_by_study,
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
        'pages/workspaces/visualize/_chart.html',
        chart_form=chart_form,
        chart=chart,
    )


def workspaces_update_entry_action(id):
    workspace_entry = g.db_session.get(WorkspaceEntry, id)
    workspace = workspace_entry.workspace

    if workspace.user != g.current_user:
        raise Forbidden

    metadata = _extract_entry_metadata()
    workspace_entry.update(**metadata)

    g.db_session.add(workspace_entry)
    g.db_session.commit()

    return render_template('pages/workspaces/update.html', workspace_entry=workspace_entry)


def workspaces_delete_entry_action(id):
    workspace_entry = g.db_session.get(WorkspaceEntry, id)
    workspace = workspace_entry.workspace

    if workspace.user != g.current_user:
        raise Forbidden

    g.db_session.delete(workspace_entry)
    g.db_session.commit()

    return {'status': 'ok'}


def workspaces_delete_all_action(id):
    workspace = g.db_session.get(Workspace, id)
    if workspace.user != g.current_user:
        raise Forbidden

    workspace.entries.clear()

    g.db_session.add(workspace)
    g.db_session.commit()

    return {'status': 'ok'}


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
    if column_count < 2:
        errors.append(f"At least 2 columns are expected, {column_count} were found")

    row_count = df.shape[0]
    if row_count <= 0:
        errors.append("No data rows were found")

    return df, errors

def _extract_entry_metadata():
    subject_type = request.form.get('subjectType')

    if subject_type in ('community', 'strain'):
        units = request.form.get('growthUnits')
    elif subject_type == 'metabolite':
        units = request.form.get('metaboliteUnits')
    else:
        units = None

    metadata = {
        'dataType':    request.form.get('dataType'),
        'subjectType': subject_type,
        'units':       units,
    }

    if label := request.form.get('label'):
        metadata['label'] = label

    return metadata
