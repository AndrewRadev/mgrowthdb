import requests
import re


class MediadiveFetcher:
    @classmethod
    def from_url(Self, mediadive_url):
        if id_match := re.search(r'mediadive\.dsmz\.de/medium/([0-9a-zA-Z]+)', mediadive_url):
            return Self(id_match[1])
        else:
            return None

    def __init__(self, mediadive_id):
        self.mediadive_id = mediadive_id
        self._response_json = None

    def make_request(self):
        medium_url = f"https://mediadive.dsmz.de/rest/medium/{self.mediadive_id}"
        response = requests.get(medium_url)
        if response.status_code != 200:
            self._response_json = None
            return False

        composition_url = f"https://mediadive.dsmz.de/rest/medium-composition/{self.mediadive_id}"
        response = requests.get(composition_url)

        try:
            response_json = response.json()
            self._response_json = response_json
        except requests.exceptions.JSONDecodeError:
            self._response_json = {}

        return True
