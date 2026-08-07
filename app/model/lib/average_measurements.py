import itertools
import sqlalchemy as sql

from app.model.orm import (
    Bioreplicate,
    Measurement,
    MeasurementContext,
)


def create_average_measurements(db_session, study, experiment):
    """
    Triggered by a background job in app.model.tasks.submissions
    """
    bioreplicate_ids = [b.id for b in experiment.bioreplicates if not b.calculationType]

    # The averaged measurements will be parented by a custom-generated bioreplicate:
    average_bioreplicate = Bioreplicate(
        name=f"Average({experiment.name})",
        calculationType='average',
        experiment=experiment,
    )
    db_session.add(average_bioreplicate)

    has_measurements = False

    for technique in study.measurementTechniques:
        for compartment in experiment.compartments:
            # We'll average values separately over techniques and compartments:
            measurement_contexts = db_session.scalars(
                sql.select(MeasurementContext)
                .distinct()
                .join(Measurement)
                .where(
                    MeasurementContext.compartmentId == compartment.id,
                    MeasurementContext.bioreplicateId.in_(bioreplicate_ids),
                    MeasurementContext.techniqueId == technique.id,
                    Measurement.value.is_not(None),
                )
                .order_by(MeasurementContext.subjectType, MeasurementContext.subjectId)
            ).all()

            # If there is a single context for this cluster of measurements, there is nothing to average:
            if len(measurement_contexts) <= 1:
                continue

            # Only average the shared time points, if any
            common_time_points = None
            max_time_point_count = 0

            for measurement_context in measurement_contexts:
                time_points = [m.timeInSeconds for m in measurement_context.measurements]
                if len(time_points) > max_time_point_count:
                    max_time_point_count = len(time_points)

                if common_time_points is None:
                    common_time_points = frozenset(time_points)
                else:
                    common_time_points = common_time_points.intersection(time_points)

            if common_time_points is None or len(common_time_points) <= (max_time_point_count // 2):
                continue

            if technique.subjectType == 'bioreplicate':
                # A single context for a group of bioreplicates
                _create_average_measurement_context(
                    db_session,
                    common_time_points=common_time_points,
                    parent_records=(study, technique, compartment),
                    measurement_contexts=measurement_contexts,
                    average_bioreplicate=average_bioreplicate,
                    subject_id=average_bioreplicate.id,
                    subject_type='bioreplicate',
                    subject_name=average_bioreplicate.name,
                    subject_external_id=None,
                )
                has_measurements = True
            else:
                grouped_contexts = itertools.groupby(
                    measurement_contexts,
                    lambda mc: (mc.subjectId, mc.subjectType, mc.subjectName, mc.subjectExternalId),
                )

                for key, subject_contexts in grouped_contexts:
                    subject_contexts = list(subject_contexts)
                    (
                        subject_id,
                        subject_type,
                        subject_name,
                        subject_external_id,
                    ) = key

                    # If there is a single context for this cluster of
                    # measurements, there is nothing to average:
                    if len(subject_contexts) <= 1:
                        continue

                    # One context for each subject:
                    _create_average_measurement_context(
                        db_session,
                        common_time_points=common_time_points,
                        parent_records=(study, technique, compartment),
                        measurement_contexts=list(subject_contexts),
                        average_bioreplicate=average_bioreplicate,
                        subject_id=subject_id,
                        subject_type=subject_type,
                        subject_name=subject_name,
                        subject_external_id=subject_external_id,
                    )
                    has_measurements = True

    if not has_measurements:
        db_session.delete(average_bioreplicate)


def _create_average_measurement_context(
    db_session,
    common_time_points,
    parent_records,
    measurement_contexts,
    average_bioreplicate,
    subject_id,
    subject_type,
    subject_name,
    subject_external_id=None,
):
    (study, technique, compartment) = parent_records

    # Collect average measurement values for the given contexts:
    measurement_rows = db_session.execute(
        sql.select(
            Measurement.timeInSeconds,
            sql.func.avg(Measurement.value),
            sql.func.std(Measurement.value),
        )
        .where(
            Measurement.contextId.in_([mc.id for mc in measurement_contexts]),
            Measurement.timeInSeconds.in_(common_time_points),
        )
        .group_by(Measurement.timeInSeconds)
        .order_by(Measurement.timeInSeconds)
    ).all()

    if len(measurement_rows) == 0:
        # We do not want to create unnecessary contexts
        return

    # Create a parent context for the individual measurements:
    average_context = MeasurementContext(
        study=study,
        bioreplicate=average_bioreplicate,
        compartment=compartment,
        subjectId=subject_id,
        subjectType=subject_type,
        subjectName=subject_name,
        subjectExternalId=subject_external_id,
        technique=technique,
        calculationType='average',
    )
    db_session.add(average_context)

    # Create individual measurements
    for (t, value, std) in measurement_rows:
        measurement = Measurement(
            timeInSeconds=t,
            value=value,
            std=std,
            context=average_context,
            study=study,
        )
        db_session.add(measurement)
