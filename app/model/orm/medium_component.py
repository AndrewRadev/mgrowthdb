from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    mapped_column,
    relationship,
    Mapped,
)

from app.model.orm.orm_base import OrmBase


class MediumComponent(OrmBase):
    """
    A single compound in a media definition.

    Could be linked to a mediadive ID or created manually. Both mass
    concentration in g/L and molar concentration in mmol/L are possible.
    """

    __tablename__ = "MediumComponents"

    id:          Mapped[int] = mapped_column(primary_key=True)
    name:        Mapped[str] = mapped_column(sql.String(255), nullable=False)
    mediadiveId: Mapped[str] = mapped_column(sql.Integer)

    massConcentration:  Mapped[float] = mapped_column(sql.Float)
    molarConcentration: Mapped[float] = mapped_column(sql.Float)

    mediumId: Mapped[str] = mapped_column(sql.ForeignKey('Media.id'), nullable=False)
    medium: Mapped['Medium'] = relationship(back_populates='components')
