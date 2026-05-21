import itertools

import sqlalchemy as sql

from app.model.lib.db import execute_into_df
from app.model.lib.chart import Chart
from app.model.orm import (
    Bioreplicate,
    Experiment,
    Measurement,
    MeasurementContext,
    ModelingResult,
    Perturbation,
    Workspace,
    WorkspaceEntry,
)
from app.model.lib.conversion import (
    CELL_COUNT_UNITS,
    CFU_COUNT_UNITS,
    METABOLITE_UNITS,
)


class ComparativeChartForm:
    def __init__(
        self,
        db_session,
        time_units='h',
        left_axis_ids=[],
        right_axis_ids=[],
        left_axis_model_ids=[],
        right_axis_model_ids=[],
        left_axis_workspace_ids=[],
        right_axis_workspace_ids=[],
        show_std=True,
        show_perturbations=True,
    ):
        self.db_session         = db_session
        self.time_units         = time_units
        self.show_std           = show_std
        self.show_perturbations = show_perturbations

        self.left_axis_ids  = set(left_axis_ids)
        self.right_axis_ids = set(right_axis_ids)
        self.no_axis_ids    = set()

        self.left_axis_model_ids  = set(left_axis_model_ids)
        self.right_axis_model_ids = set(right_axis_model_ids)
        self.no_axis_model_ids    = set()

        self.left_axis_workspace_ids  = set(left_axis_workspace_ids)
        self.right_axis_workspace_ids = set(right_axis_workspace_ids)
        self.no_axis_workspace_ids    = set()

        self.measurement_context_ids = list(self.left_axis_ids) + list(self.right_axis_ids)
        self.measurement_contexts = []

        self.modeling_result_ids = list(self.left_axis_model_ids) + list(self.right_axis_model_ids)
        self.modeling_results = []

        self.workspace_entry_ids = list(self.left_axis_workspace_ids) + list(self.right_axis_workspace_ids)
        self.workspace_entries  = []

        self.cell_count_units = 'Cells/mL'
        self.cfu_count_units  = 'CFUs/mL'
        self.metabolite_units = 'mM'

        self.log_left  = False
        self.log_right = False

    def build_chart(self, args=None, width=None, clamp_x_data=False, user=None):
        if args:
            self._extract_args(args)

        chart = Chart(
            time_units=self.time_units,
            cell_count_units=self.cell_count_units,
            cfu_count_units=self.cfu_count_units,
            metabolite_units=self.metabolite_units,
            log_left=self.log_left,
            log_right=self.log_right,
            width=width,
            clamp_x_data=clamp_x_data,
            show_std=self.show_std,
        )

        self.measurement_contexts = self.db_session.scalars(
            sql.select(MeasurementContext)
            .where(MeasurementContext.id.in_(self.measurement_context_ids))
            .options(
                sql.orm.selectinload(MeasurementContext.technique),
                sql.orm.selectinload(MeasurementContext.bioreplicate),
            )
        ).all()

        self.modeling_results = self.db_session.scalars(
            sql.select(ModelingResult)
            .where(ModelingResult.id.in_(self.modeling_result_ids))
            .options(
                sql.orm.selectinload(ModelingResult.measurementContext),
                sql.orm.selectinload(ModelingResult.measurementContext, MeasurementContext.technique),
            )
        ).all()

        userId = getattr(user, 'id', None)
        self.workspace_entries = self.db_session.scalars(
            sql.select(WorkspaceEntry)
            .join(Workspace)
            .where(WorkspaceEntry.id.in_(self.workspace_entry_ids))
            .where(sql.or_(
                Workspace.isPublished,
                Workspace.userId == userId,
            ))
        ).all()

        measurements_df = self.get_measurements_df(self.measurement_context_ids)

        for measurement_context in self.measurement_contexts:
            technique = measurement_context.technique

            if measurement_context.id in self.left_axis_ids:
                axis = 'left'
                log_transform = self.log_left
            elif measurement_context.id in self.right_axis_ids:
                axis = 'right'
                log_transform = self.log_right
            else:
                continue

            measurement_df = measurements_df[measurements_df['contextId'] == measurement_context.id]
            label = measurement_context.get_chart_label()

            if technique.subjectType == 'metabolite':
                subject = measurement_context.get_subject(self.db_session)
                metabolite_mass = subject.averageMass
            else:
                metabolite_mass = None

            if technique.units == '':
                units = technique.short_name
            else:
                units = technique.units

            chart.add_df(
                measurement_df,
                units=units,
                label=label,
                axis=axis,
                metabolite_mass=metabolite_mass,
            )

        for modeling_result in self.modeling_results:
            measurement_context = modeling_result.measurementContext
            technique = measurement_context.technique

            if modeling_result.id in self.left_axis_model_ids:
                axis = 'left'
                log_transform = self.log_left
            elif modeling_result.id in self.right_axis_model_ids:
                axis = 'right'
                log_transform = self.log_right
            else:
                continue

            measurement_df = measurements_df[measurements_df['contextId'] == measurement_context.id]
            if measurement_df.empty:
                # Could happen if we're just rendering the model without the parent measurement:
                measurement_df = measurement_context.get_df(self.db_session)

            model_df = modeling_result.generate_chart_df(measurement_df)
            label    = modeling_result.get_chart_label()

            if technique.units == '':
                units = technique.short_name
            else:
                units = technique.units

            chart.add_model_df(
                model_df,
                units=units,
                label=label,
                axis=axis,
            )

        for workspace_entry in self.workspace_entries:
            if workspace_entry.id in self.left_axis_workspace_ids:
                axis = 'left'
                log_transform = self.log_left
            elif workspace_entry.id in self.right_axis_workspace_ids:
                axis = 'right'
                log_transform = self.log_right
            else:
                continue

            df = workspace_entry.get_df()
            # TODO (2026-05-19) "Error" is the more generic name, we should use
            # that as the default
            df.rename(columns={'error': 'std'}, inplace=True)

            metadata = dict(
                units=workspace_entry.units,
                label=workspace_entry.label,
                axis=axis,
            )

            if workspace_entry.dataType == 'model':
                chart.add_model_df(df, **metadata)
            else:
                chart.add_df(df, **metadata)

        if self.show_perturbations:
            perturbations = self.db_session.scalars(
                sql.select(Perturbation)
                .distinct()
                .join(Experiment)
                .join(Bioreplicate)
                .join(MeasurementContext)
                .where(MeasurementContext.id.in_(self.measurement_context_ids))
                .order_by(Perturbation.startTimeInSeconds)
            ).all()

            for i, perturbation in enumerate(perturbations):
                chart.add_region(
                    start_time=perturbation.startTimeInHours,
                    end_time=perturbation.endTimeInHours,
                    label=f"Perturbation {i + 1} (<b>{perturbation.experiment.name}</b>)",
                    text=perturbation.description,
                )

        return chart

    @property
    def permalink_query(self):
        if len(self.measurement_contexts):
            experiment_id = self.measurement_contexts[0].bioreplicate.experimentId
            technique_id  = self.measurement_contexts[0].techniqueId
        elif len(self.modeling_results):
            experiment_id = self.modeling_results[0].measurementContext.bioreplicate.experimentId
            technique_id  = self.modeling_results[0].measurementContext.techniqueId
        else:
            experiment_id = ''
            technique_id = ''

        parts = {
            'l':  ','.join([str(i) for i in sorted(self.left_axis_ids)]),
            'r':  ','.join([str(i) for i in sorted(self.right_axis_ids)]),
            'lm': ','.join([str(i) for i in sorted(self.left_axis_model_ids)]),
            'rm': ','.join([str(i) for i in sorted(self.right_axis_model_ids)]),

            'selectedExperimentId': str(experiment_id),
            'selectedTechniqueId':  str(technique_id),
        }

        return '&'.join([f"{k}={v}" for k, v in parts.items() if v != ''])

    def group_records_by_units(self):
        records = [
            *self.measurement_contexts,
            *self.modeling_results,
            *self.workspace_entries,
        ]

        sorted_contexts = sorted(records, key=self._converted_unit_sort)

        groups = [
            (group, list(items))
            for group, items in itertools.groupby(sorted_contexts, self._converted_units)
        ]
        should_group = False

        if len(groups) <= 1:
            # If we only have 1 group, there's no need to:
            should_group = False
        else:
            # If at least one group has more than 1 items, we should group:
            for _, measurement_contexts in groups:
                if len(measurement_contexts) > 1:
                    should_group = True
                    break

        if should_group:
            return groups
        else:
            return [("__ungrouped__", records)]

    def _converted_units(self, record):
        units = record.units

        if units in CELL_COUNT_UNITS:
            return self.cell_count_units
        elif units in CFU_COUNT_UNITS:
            return self.cfu_count_units
        elif units in METABOLITE_UNITS:
            return self.metabolite_units
        else:
            return units

    def _converted_unit_sort(self, record):
        units = record.units

        if units in CELL_COUNT_UNITS:
            return 1
        elif units in CFU_COUNT_UNITS:
            return 2
        elif units in METABOLITE_UNITS:
            return 3
        elif units != '':
            return 4
        else:
            return 5

    def _extract_args(self, args):
        self.left_axis_ids  = set()
        self.right_axis_ids = set()
        self.no_axis_ids    = set()

        self.left_axis_model_ids  = set()
        self.right_axis_model_ids = set()
        self.no_axis_model_ids    = set()

        self.left_axis_workspace_ids  = set()
        self.right_axis_workspace_ids = set()
        self.no_axis_workspace_ids    = set()

        self.log_left  = False
        self.log_right = False

        for arg, value in args.items():
            if arg.startswith('measurementContext|'):
                context_id = int(arg.removeprefix('measurementContext|'))
                self.measurement_context_ids.append(context_id)
                self.left_axis_ids.add(context_id)

            elif arg.startswith('modelingResult|'):
                modeling_result_id = int(arg.removeprefix('modelingResult|'))
                self.modeling_result_ids.append(modeling_result_id)
                self.left_axis_model_ids.add(modeling_result_id)

            elif arg.startswith('workspaceEntry|'):
                workspace_entry_id = int(arg.removeprefix('workspaceEntry|'))
                self.workspace_entry_ids.append(workspace_entry_id)
                self.left_axis_workspace_ids.add(workspace_entry_id)

            elif arg.startswith('axis|'):
                record_type, record_id = arg.removeprefix('axis|').split('|')
                record_id = int(record_id)

                left_axis  = None
                right_axis = None
                no_axis    = None

                if record_type == 'measurementContext':
                    left_axis  = self.left_axis_ids
                    right_axis = self.right_axis_ids
                    no_axis    = self.no_axis_ids
                elif record_type == 'modelingResult':
                    left_axis  = self.left_axis_model_ids
                    right_axis = self.right_axis_model_ids
                    no_axis    = self.no_axis_model_ids
                elif record_type == 'workspaceEntry':
                    left_axis  = self.left_axis_workspace_ids
                    right_axis = self.right_axis_workspace_ids
                    no_axis    = self.no_axis_workspace_ids
                else:
                    raise ValueError(f"Unexpected record type: {record_type}")

                if value == 'left':
                    # Left axis by default
                    pass
                elif value == 'right':
                    left_axis.discard(record_id)
                    right_axis.add(record_id)
                elif value == 'blank':
                    # Special case, hidden "blank" checkbox was activated, remove from both:
                    left_axis.discard(record_id)
                    right_axis.discard(record_id)
                    no_axis.add(record_id)
                else:
                    raise ValueError(f"Unexpected axis: {value}")

            elif arg == 'log-left':
                self.log_left = True
            elif arg == 'log-right':
                self.log_right = True

            elif arg == 'cellCountUnits':
                self.cell_count_units = value
            elif arg == 'cfuCountUnits':
                self.cfu_count_units = value
            elif arg == 'metaboliteUnits':
                self.metabolite_units = value

    def get_measurements_df(self, measurement_context_ids):
        query = (
            sql.select(
                Measurement.contextId,
                Measurement.timeInHours.label("time"),
                Measurement.value,
                Measurement.std,
            )
            .select_from(Measurement)
            .where(
                Measurement.contextId.in_(measurement_context_ids),
                Measurement.value.is_not(None),
            )
            .order_by(Measurement.contextId, Measurement.timeInSeconds)
        )

        return execute_into_df(self.db_session, query)
