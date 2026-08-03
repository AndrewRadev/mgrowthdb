import sqlalchemy as sql
from long_task_printer import print_with_time, LongTask

from db import get_session
from app.model.orm import Study
from app.model.lib.batch_growth_rates import growth_can_be_estimated, calculate_growth_rate

with get_session() as db_session:
    studies = db_session.scalars(
        sql.select(Study)
        .order_by(Study.publicId)
    ).all()

    for study in studies:
        with print_with_time(f"> Estimating growth rates for {study.publicId}"):
            targets = []

            for experiment in study.experiments:
                for measurement_context in experiment.measurementContexts:
                    if growth_can_be_estimated(experiment, measurement_context):
                        targets.append((experiment, measurement_context))

            long_task = LongTask(total_count=len(targets))

            for (experiment, measurement_context) in targets:
                with long_task.measure() as progress:
                    print(f"  [{progress}] {measurement_context.get_chart_label()}")
                    calculate_growth_rate(db_session, experiment, measurement_context)
