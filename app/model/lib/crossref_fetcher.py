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

        if response.status_code != 200:
            raise ValueError(f"Response was unsuccessful: Status {response.status_code}")

        response_json = response.json()

        if response_json["status"] != "ok":
            raise ValueError(f"Response was unsuccessful:\n{json.dumps(response_json, indent=2)}")

        self.authors      = response_json.get("message", {}).get("author", [])
        self.author_cache = ', '.join([a['family'].lower() for a in self.authors])
