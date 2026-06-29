import itertools
from io import BytesIO
from datetime import datetime
from typing import List, Literal

import pandas as pd
import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy_utc.sqltypes import UtcDateTime

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

    sourceType: Mapped[Literal[
        'upload',
        'api',
    ]] = mapped_column(sql.String(100))

    dataType: Mapped[Literal[
        'measurement',
        'model',
        'other',
    ]] = mapped_column(sql.String(100))

    subjectType: Mapped[Literal[
        'community',
        'strain',
        'metabolite',
    ]] = mapped_column(sql.String(100))

    subjectId:   Mapped[int] = mapped_column(sql.Integer)
    units:       Mapped[str] = mapped_column(sql.String(100))

    workspaceId: Mapped[int] = mapped_column(sql.ForeignKey('Workspaces.id'), nullable=False)
    workspace: Mapped['Workspace'] = relationship(back_populates="entries")

    user: Mapped['User'] = relationship(secondary='Workspaces', viewonly=True)

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    updatedAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())

    modelingResults: Mapped[List['ModelingResult']] = relationship(
        back_populates='workspaceEntry',
        cascade='all, delete-orphan',
    )

    @classmethod
    def from_upload(Self, df, workspace, metadata={}, include_error=False):
        """
        Construct workspace entry records from the data in a CSV file.

        The first column will be parsed as time values, every other column will
        be considered to represent measurements. If `include_error` is truthy,
        columns will be parsed as pairs of value and error measurements.
        """
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
                workspace=workspace,
                data=csv_data,
                sourceType='upload',
                **metadata,
            ))

        return entries

    @property
    def isGrowth(self):
        return self.subjectType in ('community', 'strain')

    @property
    def canBeModeled(self):
        return self.sourceType in ('upload', 'api') and self.dataType == 'measurement' and self.isGrowth

    @property
    def readyModelingResults(self):
        return [mr for mr in self.modelingResults if mr.state == 'ready']

    def get_df(self, db_session=None):
        # The `db_session` parameter is provided for compatibility with other
        # types of records
        return pd.read_csv(BytesIO(self.data.encode('utf-8')))

    def get_chart_label(self, model_name=None):
        from markupsafe import escape

        if model_name:
            return f"{self.label} ({escape(model_name)} fit)"
        else:
            return self.label
