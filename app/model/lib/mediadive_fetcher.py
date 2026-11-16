import requests
import re


class MediadiveFetcher:
    def __init__(self, mediadive_url):
        self.mediadive_url = mediadive_url
        self._response_json = None

    def make_request(self):
        if id_match := re.search(r'mediadive\.dsmz\.de/medium/([0-9a-zA-Z]+)', self.mediadive_url):
            medium_id = id_match[1]
        else:
            return False

        medium_url = f"https://mediadive.dsmz.de/rest/medium/{medium_id}"
        response = requests.get(medium_url)
        if response.status_code != 200:
            self._response_json = None
            return False

        composition_url = f"https://mediadive.dsmz.de/download/composition/{medium_id}/json"
        response = requests.get(composition_url)

        try:
            response_json = response.json()
            self._response_json = response_json
        except requests.exceptions.JSONDecodeError:
            self._response_json = []

        return True
