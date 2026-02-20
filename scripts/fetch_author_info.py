import sqlalchemy as sql
import requests
import json

from app.model.lib.crossref_fetcher import CrossrefFetcher
from app.model.orm import Study
from main import create_app
from db import FLASK_DB

app = create_app()

with app.app_context():
    db_session = FLASK_DB.session
    studies = db_session.scalars(
        sql.select(Study)
        .where(
            Study.url.is_not(None),
            Study.url != '',
        )
    )

    for study in studies:
        print(f"Study: [{study.publicId}] {study.name}")

        doi = study.url
        fetcher = CrossrefFetcher(doi)

        fetcher.make_request()

        study.authors = fetcher.authors
        study.authorCache = fetcher.author_cache

        print(f" > Author cache: {study.authorCache}")

        db_session.add(study)

    db_session.commit()
