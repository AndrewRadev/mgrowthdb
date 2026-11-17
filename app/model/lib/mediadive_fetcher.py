import requests
import re

from app.model.orm import Medium, MediumComponent


class MediadiveFetcher:
    @classmethod
    def from_url(Self, mediadive_url):
        if id_match := re.search(r'mediadive\.dsmz\.de/medium/([0-9a-zA-Z]+)', mediadive_url):
            return Self(id_match[1])
        else:
            return None

    def __init__(self, mediadive_id):
        self.mediadive_id = mediadive_id

        self.medium_name = None
        self.component_data = None

    def make_request(self):
        medium_url = f"https://mediadive.dsmz.de/rest/medium/{self.mediadive_id}"
        response = requests.get(medium_url)
        if response.status_code != 200:
            self.medium_name = None
            self.component_data = None
            return False

        self.medium_name = response.json()['medium']['name']

        composition_url = f"https://mediadive.dsmz.de/rest/medium-composition/{self.mediadive_id}"
        response = requests.get(composition_url)

        try:
            response_json = response.json()
            self.component_data = response_json.get('data', [])
        except requests.exceptions.JSONDecodeError:
            self.component_data = []

        return True

    def create_study_records(self, db_session, study):
        assert(self.medium_name is not None)
        assert(self.component_data is not None)

        medium = Medium(
            name=self.medium_name,
            study=study,
            mediadiveId=self.mediadive_id,
        )
        db_session.add(medium)

        for i, entry in enumerate(self.component_data):
            medium_component = MediumComponent(
                medium=medium,
                name=entry['name'],
                mediadiveId=entry['id'],
                massConcentration=entry.get('g_l'),
                molarConcentration=entry.get('mmol_l'),
                optional=entry.get('optional', False),
                position=i + 1,
            )
            db_session.add(medium_component)
