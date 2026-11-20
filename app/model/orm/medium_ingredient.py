from decimal import Decimal

import sqlalchemy as sql
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
)

from app.model.orm.orm_base import OrmBase


class MediumIngredient(OrmBase):
    """
    A chemical ingredient that goes into a medium.

    These are imported from MediaDive, though in theory, we could create
    additional ones without an external link if it is necessary.
    """

    __tablename__ = "MediumIngredients"

    id:   Mapped[int]     = mapped_column(primary_key=True)
    name: Mapped[str]     = mapped_column(sql.String(255), nullable=False)
    mass: Mapped[Decimal] = mapped_column(sql.Numeric(10, 5))

    chebiId:     Mapped[str] = mapped_column(sql.String(100))
    mediadiveId: Mapped[int] = mapped_column(sql.Integer)
