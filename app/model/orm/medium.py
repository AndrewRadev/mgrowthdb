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

    def get_component_descriptions(self):
        parts = []

        for component in self.components:
            massPart = None
            molarPart = None

            if component.massConcentration:
                massPart = f"{component.massConcentration} g/L"
            if component.molarConcentration:
                if component.molarConcentration < 1e-3:
                    massPart = f"{component.molarConcentration:.1e} mM"
                else:
                    massPart = f"{component.molarConcentration:.3f} mM"

            if massPart and molarPart:
                measurement = f"{massPart} ({molarPart})"
            elif massPart:
                measurement = massPart
            elif molarPart:
                measurement = molarPart
            else:
                measurement = ''

            parts.append((component.name, measurement))

        return parts

    def get_component_description_html(self):
        from markupsafe import Markup

        description_parts = []

        for component_name, measurement in self.get_component_descriptions():
            description_parts.append(f"{measurement} <strong>{component_name}</strong>".strip())

        return Markup(', '.join(description_parts))
