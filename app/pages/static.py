"""
Static pages: home, about
"""

from pathlib import Path
from datetime import datetime

from flask import (
    g,
    render_template,
    current_app,
)
import sqlalchemy as sql

from app.model.orm import (
    Experiment,
    MeasurementContext,
    Metabolite,
    Study,
    StudyMetabolite,
    StudyStrain,
    Taxon,
)
from app.model.lib.util import read_timestamp_date
from app.pages.help import HELP_TOPICS


def static_home_page():
    HELP_TOPICS.process_once(debug=current_app.config["DEBUG"])
    help_topic_words = HELP_TOPICS.word_count

    experiment_count = g.db_session.scalars(
        sql.select(sql.func.count(sql.distinct(Experiment.publicId)))
        .join(Study)
        .where(Study.isPublished)
    ).one()

    measurement_context_count = g.db_session.scalars(
        sql.select(sql.func.count(sql.distinct(MeasurementContext.id)))
        .join(Study)
        .where(Study.isPublished)
    ).one()

    taxa_count       = g.db_session.scalars(sql.select(sql.func.count(Taxon.id))).one()
    metabolite_count = g.db_session.scalars(sql.select(sql.func.count(Metabolite.id))).one()

    study_strain_count = g.db_session.scalars(
        sql.select(sql.func.count(sql.distinct(StudyStrain.name)))
        .join(Study)
        .where(Study.isPublished)
        .where(StudyStrain.notUnknown)
    ).one()

    study_metabolite_count = g.db_session.scalars(
        sql.select(sql.func.count(sql.distinct(StudyMetabolite.chebiId)))
        .join(Study)
        .where(Study.isPublished)
    ).one()

    last_ncbi_update = read_timestamp_date('var/external_data/last_ncbi_update.txt')
    last_chebi_update = read_timestamp_date('var/external_data/last_chebi_update.txt')

    return render_template(
        "pages/static/home.html",
        experiment_count=experiment_count,
        measurement_context_count=measurement_context_count,
        metabolite_count=metabolite_count,
        study_metabolite_count=study_metabolite_count,
        taxa_count=taxa_count,
        study_strain_count=study_strain_count,
        last_ncbi_update=last_ncbi_update,
        last_chebi_update=last_chebi_update,
        help_topic_words=help_topic_words,
    )


def static_about_page():
    return render_template("pages/static/about.html")
