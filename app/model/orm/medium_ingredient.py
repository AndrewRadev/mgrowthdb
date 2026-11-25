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

    mediadiveId: Mapped[int] = mapped_column(sql.Integer)
    chebiId:     Mapped[str] = mapped_column(sql.String(100))

    @classmethod
    def fetch_name(Self, db_session, mediadive_id):
        medium_ingredient = db_session.scalars(
            sql.select(Self)
            .where(Self.mediadiveId == mediadive_id)
        ).one_or_none()

        if medium_ingredient:
            return medium_ingredient.name
        else:
            return None

    @staticmethod
    def search_by_name(db_session, term, page=1, per_page=10):
        term = term.lower().strip()
        if len(term) <= 0:
            return [], 0

        limit  = per_page
        offset = (page - 1) * per_page

        term_pattern = '%' + '%'.join(term.split()) + '%'
        first_word = term.split()[0]

        results = db_session.execute(
            sql.select(
                MediumIngredient.mediadiveId,
                MediumIngredient.name,
            )
            .where(sql.func.lower(MediumIngredient.name).like(term_pattern))
            .order_by(
                sql.func.locate(first_word, sql.func.lower(MediumIngredient.name)).asc(),
                sql.func.lower(MediumIngredient.name).asc()
            )
            .limit(limit)
            .offset(offset)
        ).all()

        results = [{'id': row[0], 'text': row[1]} for row in results]

        total_count = db_session.scalars(
            sql.select(sql.func.count(MediumIngredient.mediadiveId))
            .where(sql.func.lower(MediumIngredient.name).like(term_pattern))
        ).one()
        has_more = (page * per_page < total_count)

        return results, has_more
