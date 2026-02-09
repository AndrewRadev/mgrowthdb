from datetime import datetime

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase


class PageError(OrmBase):
    """
    A record of an error that occurred on a particular page, used for tracking
    unseen problems in the application in production.
    """
    __tablename__ = 'PageErrors'

    id: Mapped[int] = mapped_column(primary_key=True)

    fullPath: Mapped[str] = mapped_column(sql.String(255))
    uuid:     Mapped[str] = mapped_column(sql.String(36))
    userId:   Mapped[int] = mapped_column(sql.Integer)

    traceback: Mapped[str] = mapped_column(sql.String)

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
