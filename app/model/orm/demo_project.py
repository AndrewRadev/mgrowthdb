from datetime import datetime

import sqlalchemy as sql
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
)
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase


class DemoProject(OrmBase):
    "A project that uses mGrowthDB's API listed as a demonstration in the site"

    __tablename__ = "DemoProjects"

    id: Mapped[int] = mapped_column(primary_key=True)

    name:        Mapped[str] = mapped_column(sql.String(100), nullable=False)
    url:         Mapped[str] = mapped_column(sql.String(255), nullable=False)
    description: Mapped[str] = mapped_column(sql.String,      nullable=False)

    position:       Mapped[int]  = mapped_column(sql.Integer, nullable=False, default=0)
    showOnHomepage: Mapped[bool] = mapped_column(sql.Boolean, default=True)

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    updatedAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
