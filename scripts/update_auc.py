import sqlalchemy as sql

from db import get_session
from app.model.orm import MeasurementContext

with get_session() as db_session:
    measurement_contexts = db_session.scalars(sql.select(MeasurementContext)).all()

    for measurement_context in measurement_contexts:
        measurement_context.auc = measurement_context.calculate_auc()
        db_session.add(measurement_context)

    db_session.commit()
