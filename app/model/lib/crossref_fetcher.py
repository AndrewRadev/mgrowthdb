import json
import requests


class CrossrefFetcher:
    def __init__(self, doi):
        self.doi = doi

        self.authors      = []
        self.author_cache = ''

    def make_request(self):
        # Author records for linking and searching:
        crossref_url = f"https://api.crossref.org/works/{self.doi}"
        response = requests.get(crossref_url)

        if response.status_code == 404:
            raise ValueError(f"Couldn't find publication")
        if response.status_code != 200:
            raise ValueError(f"Couldn't reach Crossref API (Status {response.status_code})")

        response_json = response.json()

        if response_json["status"] != "ok":
            raise ValueError(f"The Crossref API didn't return a successful result")

        message_field = response_json.get("message", {})
        title_field   = message_field.get("title", [])

        if canonical_doi := message_field.get("DOI"):
            self.doi = f"https://doi.org/{canonical_doi}"

        self.title        = title_field[0] if len(title_field) else ''
        self.authors      = message_field.get("author", [])
        self.author_cache = ', '.join([a['family'].lower() for a in self.authors])
