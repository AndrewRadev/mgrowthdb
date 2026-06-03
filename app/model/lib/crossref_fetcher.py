import requests


class CrossrefFetcher:
    """
    This class encapsulates requests to api.crossref.org to get information
    about a publication based on its DOI. For now, it only fetches the author
    list and the title of a study.
    """
    def __init__(self, doi):
        self.doi = doi

        self.authors      = []
        self.author_cache = ''
        self.license_url  = None

        self._response_json = None

    def make_request(self):
        # Author records for linking and searching:
        crossref_url = f"https://api.crossref.org/works/{self.doi}"
        response = requests.get(crossref_url)

        if response.status_code == 404:
            raise ValueError("Couldn't find publication")
        if response.status_code != 200:
            raise ValueError(f"Couldn't reach Crossref API (Status {response.status_code})")

        self._response_json = response.json()

        if self._response_json["status"] != "ok":
            raise ValueError("The Crossref API didn't return a successful result")

        message_field = self._response_json.get("message", {})
        title_field   = message_field.get("title", [])

        if canonical_doi := message_field.get("DOI"):
            self.doi = f"https://doi.org/{canonical_doi}"

        self.title        = title_field[0] if len(title_field) else ''
        self.authors      = message_field.get("author", [])
        self.author_cache = ', '.join([a['family'].lower() for a in self.authors])

        licenses = message_field.get("license", [])
        if len(licenses):
            self.license_url = licenses[0].get("URL")
