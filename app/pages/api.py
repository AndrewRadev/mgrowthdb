import re
import json

from flask import (
    g,
    request,
    url_for,
)
from werkzeug.exceptions import BadRequest, Forbidden, NotFound
import sqlalchemy as sql

from app.model.lib.conversion import (
    convert_df_units,
    CELL_COUNT_UNITS,
    CFU_COUNT_UNITS,
    METABOLITE_UNITS,
)
from app.model.orm import (
    Bioreplicate,
    Experiment,
    Measurement,
    MeasurementContext,
    Metabolite,
    ModelingResult,
    Project,
    Study,
    StudyStrain,
    User,
    Workspace,
    WorkspaceEntry,
)
from app.model.lib.errors import ClientError


def project_json(publicId):
    project = g.db_session.get_one(Project, publicId)

    return {
        'id': project.publicId,
        'name': project.name,
        'description': project.description,
        'studies': [
            {'id': s.publicId, 'name': s.name}
            for s in project.studies
        ]
    }


def study_json(publicId):
    study = g.db_session.get_one(Study, publicId)

    data = {
        'id':        study.publicId,
        'name':      study.name,
        'projectId': study.project.publicId,
    }

    if study.isPublished:
        data.update({
            'description': study.description,
            'url':         study.url,
            'uploadedAt':  study.createdAt.isoformat(),
            'publishedAt': study.publishedAt.isoformat(),
            'experiments': [
                {'id': e.publicId, 'name': e.name}
                for e in study.experiments
            ]
        })

    return data


def experiment_json(publicId):
    experiment = g.db_session.get_one(Experiment, publicId)

    if not experiment.study.isPublished:
        raise NotFound

    if experiment.community:
        community_strains = experiment.community.strains
    else:
        community_strains = []

    return {
        'id':              experiment.publicId,
        'name':            experiment.name,
        'description':     experiment.description,
        'studyId':         experiment.study.publicId,
        'cultivationMode': experiment.cultivationMode,

        'communityStrains': [
            {
                'id':     s.id,
                'NCBId':  s.ncbiId,
                'custom': not s.defined,
                'name':   s.name,
            } for s in community_strains
        ],

        'compartments': [
            {
                'name':                  c.name,
                'volume':                c.volume,
                'pressure':              c.pressure,
                'stirringSpeed':         c.stirringSpeed,
                'stirringMode':          c.stirringMode,
                'O2':                    c.O2,
                'CO2':                   c.CO2,
                'H2':                    c.H2,
                'N2':                    c.N2,
                'inoculumConcentration': c.inoculumConcentration,
                'inoculumVolume':        c.inoculumVolume,
                'initialPh':             c.initialPh,
                'dilutionRate':          c.dilutionRate,
                'initialTemperature':    c.initialTemperature,
                'mediumName':            c.mediumName,
                'mediumUrl':             c.mediumUrl,
            }
            for c in experiment.compartments
        ],

        'bioreplicates': [
            {
                'id':                  b.id,
                'name':                b.name,
                'biosampleUrl':        b.biosampleUrl,
                'isAverage':           b.calculationType == 'average',
                'measurementContexts': [
                    {
                        'id': mc.id,
                        **_measurement_technique_fields(mc),
                        **_measurement_subject_fields(mc)
                    }
                    for mc in b.measurementContexts
                ]
            }
            for b in experiment.bioreplicates
        ]
    }


def experiment_csv(publicId):
    experiment = g.db_session.get(Experiment, publicId)
    if not experiment or not experiment.study.isPublished:
        raise NotFound

    df = experiment.get_df(g.db_session)

    return df.to_csv(index=False)


def measurement_context_json(id):
    measurement_context = g.db_session.get(MeasurementContext, id)
    if not measurement_context or not measurement_context.study.isPublished:
        raise NotFound

    measurement_count = g.db_session.scalars(
        sql.select(sql.func.count(Measurement.id))
        .where(Measurement.contextId == measurement_context.id)
    ).one()

    return {
        'id':                   measurement_context.id,
        'experimentId':         measurement_context.bioreplicate.experimentId,
        'studyId':              measurement_context.studyId,
        'bioreplicateId':       measurement_context.bioreplicate.id,
        'bioreplicateName':     measurement_context.bioreplicate.name,
        'measurementCount':     measurement_count,
        'measurementTimeUnits': 'h',
        'modelPredictionIds':   [mr.id for mr in measurement_context.modelingResults],
        **_measurement_technique_fields(measurement_context),
        **_measurement_subject_fields(measurement_context),
    }


def measurement_context_csv(id):
    measurement_context = g.db_session.get(MeasurementContext, id)
    if not measurement_context or not measurement_context.study.isPublished:
        raise NotFound

    df           = measurement_context.get_df(g.db_session)
    source_units = measurement_context.technique.units

    metabolite_mass = _get_metabolite_mass(measurement_context)
    _convert_to_requested_units(df, source_units, metabolite_mass)

    if request.args.get('withLabel'):
        html_label = measurement_context.get_chart_label()
        plain_label = re.sub(r'</?(b|sub)>', '', html_label)

        df.rename(columns={'value': plain_label}, inplace=True)

    return df.to_csv(index=False)


def model_prediction_json(id):
    modeling_result = g.db_session.get(ModelingResult, id)
    if not modeling_result or not modeling_result.study.isPublished:
        raise NotFound

    return {
        'id':                   modeling_result.id,
        'measurementContextId': modeling_result.measurementContextId,
        'studyId':              modeling_result.study.publicId,
        'type':                 modeling_result.type,
        'params':               modeling_result.params,
        'calculatedAt':         modeling_result.calculatedAt,
    }


def model_prediction_csv(id):
    modeling_result = g.db_session.get(ModelingResult, id)
    if not modeling_result:
        raise NotFound

    current_user = _get_current_user()
    if not modeling_result.visible_to_user(current_user):
        raise NotFound

    if modeling_result.measurementContext:
        measurements_df = modeling_result.measurementContext.get_df(g.db_session)
    else:
        measurements_df = modeling_result.workspaceEntry.get_df()

    df = modeling_result.generate_chart_df(measurements_df)

    return df.to_csv(index=False)


def bioreplicate_json(id):
    bioreplicate = g.db_session.get(Bioreplicate, id)
    if not bioreplicate or not bioreplicate.study.isPublished:
        raise NotFound

    return {
        'id':                   bioreplicate.id,
        'experimentId':         bioreplicate.experiment.publicId,
        'studyId':              bioreplicate.experiment.studyId,
        'name':                 bioreplicate.name,
        'biosampleUrl':         bioreplicate.biosampleUrl,
        'isAverage':            bioreplicate.calculationType == 'average',
        'measurementTimeUnits': 'h',
        'measurementContexts': [
            {
                'id': mc.id,
                **_measurement_technique_fields(mc),
                **_measurement_subject_fields(mc),
            }
            for mc in bioreplicate.measurementContexts
        ]
    }


def bioreplicate_csv(id):
    bioreplicate = g.db_session.get(Bioreplicate, id)
    if not bioreplicate or not bioreplicate.study.isPublished:
        raise NotFound

    df = bioreplicate.get_df(g.db_session)

    measurement_contexts = g.db_session.scalars(
        sql.select(MeasurementContext)
        .where(MeasurementContext.id.in_([mc.id for mc in bioreplicate.measurementContexts]))
        .options(sql.orm.selectinload(MeasurementContext.technique))
    )

    # Convert units for each individual measurement context:
    for mc in measurement_contexts:
        mc_df = df[df['measurementContextId'] == mc.id].copy()
        _convert_to_requested_units(mc_df, mc.technique.units, _get_metabolite_mass(mc))
        df.loc[df['measurementContextId'] == mc.id] = mc_df

    return df.to_csv(index=False)


def search_json():
    request_args = request.args.to_dict()
    if len(request_args) == 0:
        return {"error": "No search query parameters"}, 400

    results = set()

    for (key, value) in request_args.items():
        if key == 'strainNcbiIds':
            values = value.split(',')
            study_strain_ids = g.db_session.scalars(
                sql.select(StudyStrain.id)
                .where(StudyStrain.ncbiId.in_(values)),
            ).all()
            results.update(_contexts_by_subject('strain', study_strain_ids))

        elif key == 'metaboliteChebiIds':
            values = [f"CHEBI:{v}" for v in value.split(',')]

            metabolite_ids = g.db_session.scalars(
                sql.select(Metabolite.id)
                .where(Metabolite.chebiId.in_(values)),
            ).all()
            results.update(_contexts_by_subject('metabolite', metabolite_ids))

        else:
            return {"error": f"Unknown search parameter: {key}"}, 400

    measurement_contexts = list(results)

    experiment_ids = sorted({mc.experiment.publicId for mc in measurement_contexts})
    study_ids      = sorted({mc.experiment.studyId for mc in measurement_contexts})

    return {
        'studies':              study_ids,
        'experiments':          experiment_ids,
        'measurementTimeUnits': 'h',
        'measurementContexts': [
            {
                'id':               mc.id,
                'experimentId':     mc.experiment.publicId,
                'studyId':          mc.studyId,
                'bioreplicateId':   mc.bioreplicate.id,
                'bioreplicateName': mc.bioreplicate.name,
                **_measurement_technique_fields(mc),
                **_measurement_subject_fields(mc),
            }
            for mc in measurement_contexts
        ]
    }


def workspace_json(orcidId, name="default"):
    current_user = _get_current_user()
    workspace = _get_workspace(orcidId, name, current_user)

    return {
        "name": workspace.name,
        "entries": [{
            "id": entry.id,
            "label": entry.label,
        } for entry in workspace.entries],
    }


def workspace_update_json(orcidId, name="default"):
    request_json = json.loads(request.data)

    if 'apiKey' not in request_json:
        raise Forbidden
    if 'entries' not in request_json:
        raise BadRequest

    current_user = _get_current_user(request_json['apiKey'])
    workspace = _get_workspace(orcidId, name, current_user)

    # Clear out existing "api" entries:
    for entry in workspace.entries:
        if entry.sourceType == 'api':
            g.db_session.delete(entry)

    # Recreate "api" entries
    for entry in request_json['entries']:
        workspace_entry = WorkspaceEntry(
            workspace=workspace,
            sourceType="api",
            label=entry['label'],
            data=entry['data'],
        )
        g.db_session.add(workspace_entry)

    g.db_session.commit()

    workspace_url = url_for('workspaces_index_page', orcidId=workspace.user.orcidId, name=workspace.name)

    return {
        'workspaceUrl': workspace_url,
        'workspaceEntryId': workspace_entry.id,
    }


def workspace_entry_json(id):
    workspace_entry = g.db_session.get(WorkspaceEntry, id)
    current_user = _get_current_user()

    if not workspace_entry:
        raise NotFound
    if not workspace_entry.workspace.isPublished and workspace_entry.user != current_user:
        raise NotFound

    return {
        "id":          workspace_entry.id,
        "label":       workspace_entry.label,
        "units":       workspace_entry.units,
        "sourceType":  workspace_entry.sourceType,
        "dataType":    workspace_entry.dataType,
        "subjectType": workspace_entry.subjectType,
        "subjectId":   workspace_entry.subjectId,
    }


def workspace_entry_csv(id):
    workspace_entry = g.db_session.get(WorkspaceEntry, id)
    current_user = _get_current_user()

    if not workspace_entry:
        raise NotFound
    if not workspace_entry.workspace.isPublished and workspace_entry.user != current_user:
        raise NotFound

    df = workspace_entry.get_df()

    source_units = workspace_entry.units
    # TODO (2026-05-25) Allow assigning subjects to workspace entries
    # metabolite_mass = _get_metabolite_mass(workspace_entry)
    _convert_to_requested_units(df, source_units)

    if request.args.get('withLabel'):
        df.rename(columns={
            'value': workspace_entry.label,
            'error': workspace_entry.label + ' error',
        }, inplace=True)

    return df.to_csv(index=False)


def _get_current_user(api_key=None):
    if api_key is None:
        api_key = request.args.get('apiKey')

    if api_key is None:
        return g.current_user

    user = g.db_session.scalars(
        sql.select(User)
        .where(User.apiKey == api_key)
        .limit(1)
    ).one_or_none()

    if user is None:
        raise ClientError("Given API key did not correspond to an active user")

    return user


def _get_workspace(orcidId, name, current_user):
    workspace = g.db_session.scalars(
        sql.select(Workspace)
        .join(User)
        .where(
            User.orcidId == orcidId,
            Workspace.userId == User.id,
            Workspace.name == name,
        )
        .limit(1)
    ).one()

    if not workspace.isPublished and workspace.user != current_user:
        raise Forbidden

    return workspace


def _measurement_technique_fields(measurement_context):
    measurement_technique = measurement_context.technique

    metabolite_mass = _get_metabolite_mass(measurement_context)
    requested_units = _convert_unit_label_to_requested(measurement_technique.units, metabolite_mass)

    fields = {
        'techniqueType':          measurement_technique.type,
        'techniqueOriginalUnits': measurement_technique.units,
        'techniqueUnits':         requested_units,
    }
    if cell_type := measurement_technique.cellType:
        fields['techniqueCellType'] = cell_type

    return fields


def _measurement_subject_fields(measurement_context):
    subject_type = measurement_context.subjectType
    subject_name = measurement_context.subjectName
    extra_data = {}

    if measurement_context.subjectExternalId:
        if subject_type == 'strain':
            external_id = int(measurement_context.subjectExternalId.removeprefix('NCBI:'))
            extra_data = {'NCBId': external_id}
        elif subject_type == 'metabolite':
            external_id = int(measurement_context.subjectExternalId.removeprefix('CHEBI:'))
            extra_data = {'chebiId': external_id}

    return {
        'subject': {
            'type': subject_type,
            'name': subject_name,
            **extra_data,
        }
    }


def _contexts_by_subject(subject_type, subject_id):
    sql_options = (
        sql.orm.joinedload(MeasurementContext.technique),
        sql.orm.joinedload(MeasurementContext.experiment),
    )

    if isinstance(subject_id, list):
        return g.db_session.scalars(
            sql.select(MeasurementContext)
            .where(
                MeasurementContext.subjectType == subject_type,
                MeasurementContext.subjectId.in_(subject_id),
            )
            .options(*sql_options)
        ).all()
    else:
        return g.db_session.scalars(
            sql.select(MeasurementContext)
            .where(
                MeasurementContext.subjectType == subject_type,
                MeasurementContext.subjectId == subject_id,
            )
            .options(*sql_options)
        ).all()


def _get_metabolite_mass(measurement_context):
    if measurement_context.subjectType != 'metabolite':
        return None

    return measurement_context.get_subject(g.db_session).averageMass


def _convert_unit_label_to_requested(source_units, metabolite_mass=None):
    if source_units in CELL_COUNT_UNITS:
        return request.args.get('cellCountUnits', 'Cells/mL')
    elif source_units in CFU_COUNT_UNITS:
        return request.args.get('cfuCountUnits', 'CFUs/mL')
    elif source_units in METABOLITE_UNITS and metabolite_mass:
        return request.args.get('metaboliteUnits', 'mM')
    else:
        return source_units


def _convert_to_requested_units(df, source_units, metabolite_mass=None):
    if source_units in CELL_COUNT_UNITS:
        target_units = request.args.get('cellCountUnits', 'Cells/mL')
        if target_units not in CELL_COUNT_UNITS:
            raise ClientError(f"Unexpected cell count units requested: {target_units}")

        convert_df_units(df, source_units, target_units)

    elif source_units in CFU_COUNT_UNITS:
        target_units  = request.args.get('cfuCountUnits', 'CFUs/mL')
        if target_units not in CFU_COUNT_UNITS:
            raise ClientError(f"Unexpected CFU count units requested: {target_units}")

        convert_df_units(df, source_units, target_units)

    elif source_units in METABOLITE_UNITS and metabolite_mass:
        target_units = request.args.get('metaboliteUnits', 'mM')
        if target_units not in METABOLITE_UNITS:
            raise ClientError(f"Unexpected metabolite count units requested: {target_units}")

        convert_df_units(df, source_units, target_units, metabolite_mass)
