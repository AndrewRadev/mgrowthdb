import tests.init  # noqa: F401

import unittest
import requests_mock

from app.model.lib.crossref_fetcher import CrossrefFetcher


class TestCrossrefFetcher(unittest.TestCase):
    def test_fetching_authors(self):
        expected_authors = [{
            "ORCID": "https://orcid.org/0000-0001-8394-3802",
            "given": "Eric W",
            "family": "Sayers",
            "sequence": "first",
        }, {
            "given": "Jeffrey",
            "family": "Beck",
            "sequence": "additional",
        }]

        with requests_mock.Mocker() as m:
            m.get('https://api.crossref.org/works/abc', json={
                "status": "ok",
                "message": {"author": expected_authors}
            })

            fetcher = CrossrefFetcher(doi='abc')
            fetcher.make_request()

            self.assertEqual(fetcher.authors, expected_authors)
            self.assertEqual(fetcher.author_cache, 'sayers, beck')
            self.assertEqual(fetcher.title, '')

            m.get('https://api.crossref.org/works/nonexistent', status_code=404)

            fetcher = CrossrefFetcher(doi='abc')
            with self.assertRaises(ValueError):
                fetcher = CrossrefFetcher(doi='nonexistent')
                fetcher.make_request()

    def test_fetching_study_title(self):
        expected_authors = []

        with requests_mock.Mocker() as m:
            m.get('https://api.crossref.org/works/abc', json={
                "status": "ok",
                "message": {"title": ["Test study"], "author": []}
            })

            fetcher = CrossrefFetcher(doi='abc')
            fetcher.make_request()

            self.assertEqual(fetcher.authors, [])
            self.assertEqual(fetcher.author_cache, '')
            self.assertEqual(fetcher.title, 'Test study')

    def test_error_handling(self):
        with requests_mock.Mocker() as m:
            m.get('https://api.crossref.org/works/doi1', status_code=404)
            with self.assertRaises(ValueError) as e:
                fetcher = CrossrefFetcher(doi='doi1')
                fetcher.make_request()
                self.assertEqual(str(e), "Couldn't find publication")

            m.get('https://api.crossref.org/works/doi2', status_code=500)
            with self.assertRaises(ValueError) as e:
                fetcher = CrossrefFetcher(doi='doi2')
                fetcher.make_request()
                self.assertEqual(str(e), "Couldn't reach Crossref API (Status 500)")

            m.get('https://api.crossref.org/works/doi3', status_code=200, json={"status": "error"})
            with self.assertRaises(ValueError) as e:
                fetcher = CrossrefFetcher(doi='doi3')
                fetcher.make_request()
                self.assertEqual(str(e), "The Crossref API didn't return a successful result")


if __name__ == '__main__':
    unittest.main()
