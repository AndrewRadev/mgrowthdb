import re

import sqlalchemy as sql

from app.model.orm import (
    Experiment,
    Metabolite,
    Project,
    Study,
    StudyMetabolite,
    StudyStrain,
    StudyUser,
    Taxon,
)


class StudySearch:
    def __init__(
        self,
        db_session,
        user=None,
        query=None,
        ncbiIds=None,
        chebiIds=None,
        sort_order='uploadDate_desc',
        publication_type='',
        per_page=10,
        offset=0,
    ):
        self.db_session       = db_session
        self.user             = user
        self.query            = (query or '').strip().lower()
        self.per_page         = per_page
        self.ncbiIds          = [int(n) for n in (ncbiIds or [])]
        self.chebiIds         = chebiIds or []
        self.offset           = offset
        self.sort_order       = sort_order
        self.publication_type = publication_type

        self.query_words = []
        self.has_more = False

    def fetch_results(self):
        publish_clause          = self._build_publish_clause()
        publication_type_clause = self._build_publication_type_clause()

        if self.sort_order == 'publicationDate_asc':
            order_clauses = (Study.publicationDate.asc(),)
        elif self.sort_order == 'publicationDate_desc':
            order_clauses = (Study.publicationDate.desc(),)
        elif self.sort_order == 'uploadDate_asc':
            order_clauses = (Study.publicId.asc(),)
        else:
            order_clauses = (Study.publicId.desc(),)

        db_query = (
            sql.select(Study)
            .join(StudyUser, isouter=True)
            .group_by(Study.publicId)
            .where(publish_clause, publication_type_clause)
            .limit(self.per_page)
            .offset(self.offset)
        )
        db_count_query = (
            sql.select(sql.func.count(Study.publicId.distinct()))
            .join(StudyUser, isouter=True)
            .where(publish_clause, publication_type_clause)
        )

        if len(self.query):
            query = _replace_public_id_references(self.query)
            self.query_words = query.split()

            # Note: this looks for the entire combination in each of the
            # fields, so searching for e.g. "Garza batch" will not find a good
            # result if "Garza" is an author, and "batch" is part of the title.
            #
            like_expr = '%' + '%'.join(self.query_words) + '%'

            db_query       = db_query.join(Experiment, isouter=True).join(Project)
            db_count_query = db_count_query.join(Experiment, isouter=True).join(Project)

            query_clause = sql.or_(
                Study.name.ilike(like_expr),
                Study.authorCache.like(like_expr),
                Study.description.ilike(like_expr),
                Study.publicId.in_(self.query_words),
                Experiment.publicId.in_(self.query_words),
                Project.publicId.in_(self.query_words),
            )

            db_query       = db_query.where(query_clause)
            db_count_query = db_count_query.where(query_clause)
        else:
            self.query_words = []

        if self.chebiIds:
            db_query       = db_query.join(StudyMetabolite).where(StudyMetabolite.chebiId.in_(self.chebiIds))
            db_count_query = db_count_query.join(StudyMetabolite).where(StudyMetabolite.chebiId.in_(self.chebiIds))

            order_clauses = (sql.func.count(StudyMetabolite.id.distinct()).desc(), *order_clauses)

        if self.ncbiIds:
            db_query       = db_query.join(StudyStrain).where(StudyStrain.ncbiId.in_(self.ncbiIds))
            db_count_query = db_count_query.join(StudyStrain).where(StudyStrain.ncbiId.in_(self.ncbiIds))

            order_clauses = (sql.func.count(StudyStrain.ncbiId.distinct()).desc(), *order_clauses)

        db_query = db_query.order_by(*order_clauses)

        results = self.db_session.scalars(db_query).all()
        count   = self.db_session.scalars(db_count_query).one()

        if count > self.offset + len(results):
            self.has_more = True

        return results

    def fetch_taxa(self):
        return self.db_session.scalars(
            sql.select(Taxon)
            .where(Taxon.ncbiId.in_(self.ncbiIds))
        ).all()

    def fetch_metabolites(self):
        return self.db_session.scalars(
            sql.select(Metabolite)
            .where(Metabolite.chebiId.in_(self.chebiIds))
        ).all()

    def _build_publish_clause(self):
        if self.user and self.user.isAdmin:
            # Noop, show everything
            return Study.publicId.isnot(None)
        elif self.user:
            return sql.or_(
                Study.isPublished,
                Study.ownerUuid == self.user.uuid,
                StudyUser.userUniqueID == self.user.uuid,
            )
        else:
            return Study.isPublished

    def _build_publication_type_clause(self):
        if self.publication_type in ('publication', 'preprint', 'dataset'):
            return Study.publicationType == self.publication_type
        else:
            # Noop, show everything
            return Study.publicId.isnot(None)


def _replace_public_id_references(text):
    replacements = [
        (r'\bSMGDB0*(\d+)', _replace_study_reference),
        (r'\bEMGDB0*(\d+)', _replace_experiment_reference),
        (r'\bPMGDB0*(\d+)', _replace_project_reference),
    ]

    for regex, callback in replacements:
        text = re.sub(regex, callback, text, flags=re.IGNORECASE)

    return text


def _replace_study_reference(m):
    return f"SMGDB{int(m[1]):08d}"


def _replace_experiment_reference(m):
    return f"EMGDB{int(m[1]):09d}"


def _replace_project_reference(m):
    return f"PMGDB{int(m[1]):06d}"
