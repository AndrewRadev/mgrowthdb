import tests.init  # noqa: F401

import unittest
import requests_mock

from app.model.lib.mediadive_fetcher import MediadiveFetcher


class TestMediadiveFetcher(unittest.TestCase):
    def test_parsing_url(self):
        fetcher = MediadiveFetcher.from_url("https://mediadive.dsmz.de/medium/339")
        self.assertEqual(fetcher.mediadive_id, '339')

        fetcher = MediadiveFetcher.from_url("https://mediadive.dsmz.de/medium/P1")
        self.assertEqual(fetcher.mediadive_id, 'P1')

        fetcher = MediadiveFetcher.from_url("http://mediadive.dsmz.de/medium/1a?moreParams")
        self.assertEqual(fetcher.mediadive_id, '1a')

        fetcher = MediadiveFetcher.from_url("http://mediadive.fake.de/medium/1")
        self.assertIsNone(fetcher)

    def test_fetching_media_from_url(self):
        expected_payload = {
            "status": 200,
            "count": 5,
            "data": [
                {"id": 1, "name": "dehydrated Wilkins-Chalgren medium", "g_l": 33,     "mmol_l": None},
                {"id": 2, "name": "L-Cysteine HCl",                     "g_l": 0.3,    "mmol_l": 1.90331},
                {"id": 3, "name": "Sodium resazurin",                   "g_l": 0.0005, "mmol_l": 0.00199068},
                {"id": 4, "name": "Distilled water",                    "g_l": None,   "mmol_l": None}
            ]
        }

        with requests_mock.Mocker() as m:
            m.get('https://mediadive.dsmz.de/rest/medium/339', status_code=200)
            m.get(
                'https://mediadive.dsmz.de/rest/medium-composition/339',
                json=expected_payload,
            )
            fetcher = MediadiveFetcher('339')

            # Request is successful, ingredients are extracted:
            self.assertTrue(fetcher.make_request())
            self.assertEqual(fetcher._response_json, expected_payload)

    def test_fetching_media_with_no_composition(self):
        expected_payload = {
            "status": 404,
            "count": 0,
            "error": "DataNotFound",
            "msg": "Medium does not exist"
        }

        with requests_mock.Mocker() as m:
            m.get('https://mediadive.dsmz.de/rest/medium/P1', status_code=200)
            m.get(
                'https://mediadive.dsmz.de/rest/medium-composition/P1',
                status_code=404,
                json=expected_payload,
            )
            fetcher = MediadiveFetcher('P1')

            # Request is successful, but no ingredients:
            self.assertTrue(fetcher.make_request())
            self.assertEqual(fetcher._response_json, expected_payload)

    def test_fetching_missing_media(self):
        with requests_mock.Mocker() as m:
            m.get(
                'https://mediadive.dsmz.de/rest/medium/9999',
                status_code=404,
                json={'status': 404, 'count': 0, 'error': 'DataNotFound', 'msg': 'Medium does not exist'},
            )
            fetcher = MediadiveFetcher('9999')

            # Request is a failure:
            self.assertFalse(fetcher.make_request())
            self.assertEqual(fetcher._response_json, None)
