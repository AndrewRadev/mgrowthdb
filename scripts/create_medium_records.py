import sqlalchemy as sql

from db import get_session
from app.model.lib.mediadive_fetcher import MediadiveFetcher
from app.model.orm import Study, Medium

with get_session() as db_session:
    studies = db_session.scalars(
        sql.select(Study)
        .order_by(Study.publicId)
    ).all()

    for study in studies:
        study.media = []
        print(f"> Working on study: {study.publicId}")

        medium_data = set()
        for compartment in study.compartments:
            if compartment.mediumUrl is None:
                continue

            print(f"  > Compartment: {compartment.name}, URL: {compartment.mediumUrl}")
            medium_data.add((compartment.mediumName, compartment.mediumUrl))

        for medium_name, medium_url in medium_data:
            mediadive_fetcher = MediadiveFetcher.from_url(medium_url)

            if mediadive_fetcher:
                mediadive_fetcher.make_request()
                mediadive_fetcher.create_study_records(
                    db_session,
                    study,
                    medium_name=medium_name,
                )
            else:
                db_session.add(Medium(name=medium_name, study=study))

    db_session.commit()
