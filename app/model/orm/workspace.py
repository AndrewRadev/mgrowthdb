from typing import List
from datetime import datetime

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase


class Workspace(OrmBase):
    """
    A space where users can upload data that is not linked to a study.

    The actual data instances are in `WorkspaceEntry` records. This is a
    container for them that is linked to a specific user with a specific name.
    It can be made public or kept private (the default).
    """

    __tablename__ = 'Workspaces'

    id:   Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sql.String(255), nullable=False, default="default")

    userId: Mapped[int] = mapped_column(sql.ForeignKey('Users.id'), nullable=False)
    user: Mapped['User'] = relationship(back_populates="workspaces")

    entries: Mapped[List['WorkspaceEntry']] = relationship(
        back_populates="workspace",
        cascade='all, delete-orphan',
        order_by='WorkspaceEntry.id',
    )
    modelingResults: Mapped[List['ModelingResult']] = relationship(
        secondary='WorkspaceEntries',
        viewonly=True,
    )

    createdAt:   Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    updatedAt:   Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    publishedAt: Mapped[datetime] = mapped_column(UtcDateTime, nullable=True)

    @hybrid_property
    def isPublished(self):
        return self.publishedAt != None

    def visible_to_user(self, user):
        return self.isPublished or self.user == user
