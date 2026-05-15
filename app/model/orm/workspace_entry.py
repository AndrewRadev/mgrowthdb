from io import BytesIO
import itertools

import pandas as pd
import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.orm.orm_base import OrmBase


class WorkspaceEntry(OrmBase):
    """
    Data uploaded by a user that is not linked to a study.

    This data is meant to be shown on a user's dashboard, or attached to a
    study post-upload. It could be observational measurements, or it could be
    modeling results.
    """

    __tablename__ = 'WorkspaceEntries'

    id:     Mapped[int] = mapped_column(primary_key=True)
    label:  Mapped[str] = mapped_column(sql.String(255), nullable=False)
    data:   Mapped[str] = mapped_column(sql.String, nullable=False)

    dataType:    Mapped[str] = mapped_column(sql.String(100))
    subjectType: Mapped[str] = mapped_column(sql.String(100))
    subjectId:   Mapped[int] = mapped_column(sql.Integer)
    units:       Mapped[str] = mapped_column(sql.String(100))

    userId: Mapped[int] = mapped_column(sql.ForeignKey('Users.id'), nullable=False)
    user: Mapped['User'] = relationship(back_populates="workspaceEntries")

    @classmethod
    def from_csv(Self, file, user, metadata={}, include_error=False):
        """
        Construct workspace entry records from the data in a CSV file.

        The first column will be parsed as time values, every other column will
        be considered to represent measurements. If `include_error` is truthy,
        columns will be parsed as pairs of value and error measurements.
        """
        df = pd.read_csv(file)
        time_col = df.columns[0]

        if include_error:
            value_and_error_columns = list(itertools.batched(df.columns[1:], 2))
        else:
            value_and_error_columns = [(c, None) for c in df.columns[1:]]

        entries = []

        for (value_column, error_column) in value_and_error_columns:
            if error_column is None:
                subset = [time_col, value_column]
            else:
                subset = [time_col, value_column, error_column]

            csv_data = df[subset].rename(columns={
                time_col: 'time',
                value_column: 'value',
                error_column: 'error',
            }).to_csv(index=False)

            entries.append(Self(
                label=value_column,
                user=user,
                data=csv_data,
                **metadata,
            ))

        return entries

    def get_df(self):
        return pd.read_csv(BytesIO(self.data.encode('utf-8')))
