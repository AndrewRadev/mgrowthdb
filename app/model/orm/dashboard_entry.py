from io import BytesIO

import pandas as pd
import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.orm.orm_base import OrmBase


class DashboardEntry(OrmBase):
    """
    Data uploaded by a user that is not linked to a study.

    This data is meant to be shown on a user's dashboard, or attached to a
    study post-upload. It could be observational measurements, or it could be
    modeling results.
    """

    __tablename__ = 'DashboardEntries'

    id:     Mapped[int] = mapped_column(primary_key=True)
    label:  Mapped[str] = mapped_column(sql.String(255), nullable=False)
    data:   Mapped[str] = mapped_column(sql.String, nullable=False)
    userId: Mapped[int] = mapped_column(sql.ForeignKey('Users.id'), nullable=False)

    user: Mapped['User'] = relationship(back_populates="dashboardEntries")

    def get_df(self):
        return pd.read_csv(BytesIO(self.data.encode('utf-8')))
