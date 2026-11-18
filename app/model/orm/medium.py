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

    def get_components_description_html(self):
        from markupsafe import Markup

        description_parts = []

        for component in self.components:
            massPart = None
            molarPart = None

            if component.massConcentration:
                massPart = f"{component.massConcentration:.3f} g/L"
            if component.molarConcentration:
                massPart = f"{component.molarConcentration:.3f} mmol/L"

            if massPart and molarPart:
                measurement = f"{massPart} ({molarPart})"
            elif massPart:
                measurement = massPart
            elif molarPart:
                measurement = molarPart

            description_parts.append(f"{measurement} <strong>{component.name}</strong>")

        return Markup(', '.join(description_parts))
