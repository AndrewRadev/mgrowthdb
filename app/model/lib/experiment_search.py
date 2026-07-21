import re

import sqlalchemy as sql

from app.model.orm import Experiment


class ExperimentSearch:
    def __init__(
        self,
        db_session,
        study,
        query=None,
        sql_options=(),
    ):
        self.db_session  = db_session
        self.study       = study
        self.query       = (query or '').strip().lower()
        self.sql_options = sql_options

        self.query_words = []

    def fetch_results(self):
        db_query = (
            sql.select(Experiment)
            .where(Experiment.studyId == self.study.publicId)
            .options(*self.sql_options)
        )

        if len(self.query):
            query = _replace_public_id_references(self.query)
            self.query_words = query.split()

            like_expr = '%' + '%'.join(self.query_words) + '%'

            query_clause = sql.or_(
                Experiment.name.ilike(like_expr),
                Experiment.description.ilike(like_expr),
                Experiment.publicId.in_(self.query_words),
            )

            db_query = db_query.where(query_clause)
        else:
            self.query_words = []

        db_query = db_query.order_by(Experiment.publicId)

        results = self.db_session.scalars(db_query).all()

        return results


def _replace_public_id_references(text):
    return re.sub(r'\bEMGDB0*(\d+)', _replace_experiment_reference, text, flags=re.IGNORECASE)


def _replace_experiment_reference(m):
    return f"EMGDB{int(m[1]):09d}"
