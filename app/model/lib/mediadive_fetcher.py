import requests
import re

from app.model.orm import Medium, MediumComponent


class MediadiveFetcher:
    """
    Fetch medium data through the MediaDive API.

    The class can be constructed from a mediadive URL which is how it's used in
    practice. If the URL doesn't look right, the class method returns `None`.

    It's expected to execute `.make_request()`, and then take the fetched
    properties from the object's attributes. If the requests fail, the relevant
    attributes will be left empty.
    """

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

        response_json = response.json()
        self.medium_name = response_json['data']['medium']['name']

        composition_url = f"https://mediadive.dsmz.de/rest/medium-composition/{self.mediadive_id}"
        response = requests.get(composition_url)

        try:
            response_json = response.json()
            self.component_data = [
                {
                    'name':               entry['name'],
                    'mediadiveId':        entry['id'],
                    'massConcentration':  entry['g_l'],
                    'molarConcentration': entry['mmol_l'],
                    'optional':           entry.get('optional', False),
                }
                for entry in response_json.get('data', [])
            ]

        except requests.exceptions.JSONDecodeError:
            self.component_data = []

        return True
