import sqlalchemy as sql

from db import get_session
from app.model.lib.mediadive_fetcher import MediadiveFetcher
from app.model.orm import Study, Medium, MediumComponent

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
            medium_data.add((compartment.mediumName.strip(), compartment.mediumUrl.strip()))

        for medium_name, medium_url in medium_data:
            mediadive_fetcher = MediadiveFetcher.from_url(medium_url)

            if mediadive_fetcher:
                mediadive_fetcher.make_request()

                medium = Medium(
                    name=(medium_name or mediadive_fetcher.medium_name),
                    url=f"https://mediadive.dsmz.de/medium/{mediadive_fetcher.mediadive_id}",
                    study=study,
                    mediadiveId=mediadive_fetcher.mediadive_id,
                )
                db_session.add(medium)

                for i, entry in enumerate(mediadive_fetcher.component_data):
                    medium_component = MediumComponent(
                        medium=medium,
                        name=entry['name'],
                        mediadiveId=entry['mediadiveId'],
                        massConcentration=entry.get('massConcentration'),
                        molarConcentration=entry.get('molarConcentration'),
                        optional=entry.get('optional', False),
                        position=i + 1,
                    )
                    db_session.add(medium_component)
            else:
                db_session.add(Medium(name=medium_name, study=study))

    db_session.commit()
