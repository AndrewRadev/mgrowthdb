from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    mapped_column,
    relationship,
    Mapped,
)

from app.model.orm.orm_base import OrmBase


class Medium(OrmBase):
    """
    A medium definition for a particular study.

    Could be linked to an external URL where more information can be found. If
    external URL is a mediadive one, then it should also have `MediumComponent`
    records taken from their API. Components can also be added directly.
    """

    __tablename__ = "Media"

    id:          Mapped[int] = mapped_column(primary_key=True)
    name:        Mapped[str] = mapped_column(sql.String(255), nullable=False)
    url:         Mapped[str] = mapped_column(sql.String(255))
    description: Mapped[str] = mapped_column(sql.String)
    mediadiveId: Mapped[str] = mapped_column(sql.String(100))

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.publicId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='media')

    components: Mapped[List['MediumComponent']] = relationship(
        back_populates='medium',
        order_by='MediumComponent.position',
        cascade='all, delete-orphan',
    )

    def get_components_description(self):
        description_parts = []

        for component in self.components:
            if component.massConcentration and component.molarConcentration:
                measurement = f"{component.massConcentration:.3f} g/L ({component.molarConcentration:.3f} mmol/L) "
            elif component.massConcentration:
                measurement = f"{component.massConcentration:.3f} g/L"
            elif component.molarConcentration:
                measurement = f"{component.molarConcentration:.3f} mmol/L"

            description_parts.append(f"{measurement} {component.name}")

        return ', '.join(description_parts)
