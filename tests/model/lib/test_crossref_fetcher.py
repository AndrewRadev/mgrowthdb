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

    def test_fetching_publication_type(self):
        type_mapping = [
            ("https://www.nature.com/articles/s41467-025-56012-8",                'publication'),
            ("https://www.frontiersin.org/article/10.3389/fmicb.2019.02449/full", 'publication'),
            ("https://www.biorxiv.org/content/10.1101/2024.11.28.625814v1",       'preprint'),
            ("https://biorxiv.org/content/10.1101/2024.11.28.625814v1",           'preprint'),
            ("http://biorxiv.org/content/10.1101/2024.11.28.625814v1",            'preprint'),
        ]

        for url, expected_type in type_mapping:
            with requests_mock.Mocker() as m:
                m.get('https://api.crossref.org/works/abc', json={
                    "status": "ok",
                    "message": {"resource": {"primary": {"URL": url}}}
                })
                fetcher = CrossrefFetcher(doi='abc')
                fetcher.make_request()
                self.assertEqual(fetcher.publication_type, expected_type)

        with requests_mock.Mocker() as m:
            m.get('https://api.crossref.org/works/abc', json={
                "status": "ok",
                "message": {}
            })
            fetcher = CrossrefFetcher(doi='abc')
            fetcher.make_request()
            self.assertEqual(fetcher.publication_type, 'dataset')

    def test_fetching_publication_date(self):
        with requests_mock.Mocker() as m:
            m.get('https://api.crossref.org/works/abc', json={
                "status": "ok",
                "message": {
                    "published-online": {"date-parts": [[2024, 2, 5]]},
                }
            })
            m.get('https://api.crossref.org/works/def', json={
                "status": "ok",
                "message": {
                    "published-online": {"date-parts": [[2023]]},
                    "published-print": {"date-parts": [[2023, 10]]},
                }
            })
            m.get('https://api.crossref.org/works/ghi', json={
                "status": "ok",
                "message": {
                    "published-print": {"date-parts": [[2023, 10]]},
                }
            })

            fetcher = CrossrefFetcher(doi='abc')
            fetcher.make_request()
            self.assertEqual(fetcher.publication_date, '2024-02-05')

            fetcher = CrossrefFetcher(doi='def')
            fetcher.make_request()
            self.assertEqual(fetcher.publication_date, '2023')

            fetcher = CrossrefFetcher(doi='ghi')
            fetcher.make_request()
            self.assertEqual(fetcher.publication_date, '2023-10')

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
