import re

import sqlalchemy as sql

from app.model.orm import (
    Bioreplicate,
    Community,
    CommunityStrain,
    Experiment,
    MeasurementContext,
    ModelingResult,
    StudyStrain,
)


class ExperimentSearch:
    def __init__(
        self,
        db_session,
        study,
        query=None,
        strain_ids=None,
        metabolite_ids=None,
        modeling_types=None,
        sql_options=None,
    ):
        self.db_session = db_session
        self.study      = study

        self.query          = (query or '').strip().lower()
        self.strain_ids     = [int(n) for n in (strain_ids or [])]
        self.metabolite_ids = [int(n) for n in (metabolite_ids or [])]
        self.modeling_types = modeling_types or []

        self.sql_options = sql_options or ()

        self.query_words = []

    def fetch_results(self):
        db_query = (
            sql.select(Experiment)
            .group_by(Experiment.publicId)
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

        if self.strain_ids or self.metabolite_ids or self.modeling_types:
            # Hack: We use left joins to avoid problems in tests where the
            # entire hierarchy of data is not quite created consistently
            db_query = db_query.join(Bioreplicate, isouter=True).join(MeasurementContext, isouter=True)

            if self.strain_ids:
                db_query = (
                    db_query
                    .join(Community, isouter=True)
                    .join(CommunityStrain, isouter=True)
                    .join(StudyStrain, isouter=True)
                )

            if self.modeling_types:
                db_query = db_query.join(ModelingResult, isouter=True)

            strain_clause = sql.or_(
                StudyStrain.id.in_(self.strain_ids),
                sql.and_(
                    MeasurementContext.subjectId.in_(self.strain_ids),
                    MeasurementContext.subjectType == 'strain',
                )
            )
            metabolite_clause = sql.and_(
                MeasurementContext.subjectId.in_(self.metabolite_ids),
                MeasurementContext.subjectType == 'metabolite',
            )

        if self.strain_ids and self.metabolite_ids:
            db_query = db_query.where(sql.or_(strain_clause, metabolite_clause))
        elif self.strain_ids:
            db_query = db_query.where(strain_clause)
        elif self.metabolite_ids:
            db_query = db_query.where(metabolite_clause)

        if self.modeling_types:
            db_query = db_query.where(ModelingResult.type.in_(self.modeling_types))

        db_query = db_query.order_by(Experiment.publicId)

        results = self.db_session.scalars(db_query).all()

        return results


def _replace_public_id_references(text):
    return re.sub(r'\bEMGDB0*(\d+)', _replace_experiment_reference, text, flags=re.IGNORECASE)


def _replace_experiment_reference(m):
    return f"EMGDB{int(m[1]):09d}"
