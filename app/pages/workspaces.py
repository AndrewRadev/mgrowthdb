import itertools
from datetime import datetime, UTC

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

from app.view.forms.comparative_chart_form import ComparativeChartForm
from app.model.lib.chart import Chart
from app.model.lib.compare import init_compare_data
import app.model.lib.util as util
from app.model.tasks.modeling import process_modeling_request
from app.model.orm import (
    MeasurementContext,
    ModelingResult,
    User,
    Workspace,
    WorkspaceEntry,
)


def workspaces_root_page():
    if g.current_user:
        return redirect(url_for('workspaces_index_page', orcidId=g.current_user.orcidId, name="default"))
    else:
        return render_template('pages/workspaces/no_user.html')


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


def workspaces_create_action():
    if g.current_user is None:
        raise Forbidden

    name = request.form["name"]
    existing_workspace = g.db_session.scalars(
        sql.select(Workspace)
        .where(Workspace.userId == g.current_user.id, Workspace.name == name)
        .limit(1)
    ).one_or_none()

    if existing_workspace is None:
        g.db_session.add(Workspace(userId=g.current_user.id, name=name))
        g.db_session.commit()

    return redirect(url_for('workspaces_index_page', orcidId=g.current_user.orcidId, name=name))


def workspaces_delete_action(id):
    workspace = g.db_session.get(Workspace, id)
    if g.current_user is None or g.current_user.user != workspace.user:
        raise Forbidden

    g.db_session.delete(workspace)
    g.db_session.commit()

    return {
        'url': url_for('workspaces_index_page', orcidId=g.current_user.orcidId, name="default"),
    }


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
    left_axis_model_ids  = util.parse_comma_separated_request_ids('lm')
    right_axis_model_ids = util.parse_comma_separated_request_ids('rm')

    chart_form = ComparativeChartForm(
        g.db_session,
        left_axis_workspace_ids=left_axis_workspace_ids,
        right_axis_workspace_ids=right_axis_workspace_ids,
        left_axis_model_ids=left_axis_model_ids,
        right_axis_model_ids=right_axis_model_ids,
    )

    return render_template(
        "pages/workspaces/visualize.html",
        workspace=workspace,
        chart_form=chart_form,
        comparable_records_by_study=comparable_records_by_study,
    )


def workspaces_chart_fragment(orcidId, name="default"):
    # Invoked in order to check permissions:
    _workspace = _find_workspace(orcidId, name)

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


def workspaces_toggle_published_action(id):
    workspace = g.db_session.get(Workspace, id)
    if workspace.user != g.current_user:
        raise Forbidden

    if workspace.isPublished:
        workspace.publishedAt = None
    else:
        workspace.publishedAt = datetime.now(UTC)

    g.db_session.add(workspace)
    g.db_session.commit()

    return {'status': 'ok'}


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


def workspaces_modeling_page(orcidId, name="default"):
    workspace = _find_workspace(orcidId, name, public=False)

    return render_template(
        "pages/workspaces/modeling.html",
        workspace=workspace,
    )


def workspaces_modeling_chart_fragment(orcidId, name):
    workspace = _find_workspace(orcidId, name, public=False)
    args = request.args.to_dict()

    modeling_type = args.pop('modelingType')
    log_transform = args.pop('logTransform', 'false') == 'true'

    workspace_entry = g.db_session.get(WorkspaceEntry, args['workspaceEntryId'])
    measurement_df  = workspace_entry.get_df(g.db_session)

    chart = Chart(
        time_units='h',
        log_left=log_transform,
    )

    units = workspace_entry.units

    chart.add_df(
        measurement_df,
        units=units,
        label=workspace_entry.label,
    )

    modeling_record = g.db_session.scalars(
        sql.select(ModelingResult)
        .where(
            ModelingResult.type == modeling_type,
            ModelingResult.workspaceEntryId == workspace_entry.id,
            ModelingResult.state == 'ready',
        )
    ).one_or_none()

    if modeling_record:
        df = modeling_record.generate_chart_df(measurement_df)

        label = modeling_record.model_name
        chart.add_model_df(df, units=units, label=label)

        model_params = modeling_record.params
        r_summary    = modeling_record.rSummary
    else:
        model_params = ModelingResult.empty_params(modeling_type)
        r_summary    = None

    return render_template(
        'pages/workspaces/modeling/_chart.html',
        workspace=workspace,
        chart=chart,
        modeling_record=modeling_record,
        model_params=model_params,
        r_summary=r_summary,
        units=units,
        log_transform=log_transform,
    )


def workspaces_modeling_submit_action(orcidId, name="default"):
    # Invoked in order to check permissions:
    _workspace = _find_workspace(orcidId, name, public=False)
    args = request.form.to_dict()

    modeling_type = args.pop('modelingType')
    workspace_entry_id = int(args.pop('selectedEntry').removeprefix('workspaceEntry|'))

    modeling_result = g.db_session.scalars(
        sql.select(ModelingResult)
        .where(
            ModelingResult.type == modeling_type,
            ModelingResult.workspaceEntryId == workspace_entry_id,
        )
    ).one_or_none()

    if modeling_result is None:
        modeling_result = ModelingResult(
            type=modeling_type,
            workspaceEntryId=workspace_entry_id,
        )

    modeling_result.state = 'pending'
    g.db_session.add(modeling_result)
    g.db_session.commit()

    process_modeling_request.delay(
        modeling_result.id,
        target_type='WorkspaceEntry',
        target_id=workspace_entry_id,
        args=args,
    )

    return {'modelingResultId': modeling_result.id}


def workspaces_modeling_check_json(orcidId, name):
    workspace = _find_workspace(orcidId, name, public=False)

    result_states = {}

    for modeling_result in workspace.modelingResults:
        result_states[modeling_result.id] = modeling_result.state

    return result_states


def _find_workspace(orcidId, name, public=True):
    workspace = g.db_session.scalars(
        sql.select(Workspace)
        .join(User)
        .where(User.orcidId == orcidId)
        .where(Workspace.name == name)
        .limit(1)
    ).one()

    if public:
        if g.current_user != workspace.user and not workspace.isPublished:
            raise Forbidden
    else:
        if g.current_user != workspace.user:
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
