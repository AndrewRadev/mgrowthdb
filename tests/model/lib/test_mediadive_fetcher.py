import tests.init  # noqa: F401

import unittest
import requests_mock

from app.model.lib.mediadive_fetcher import MediadiveFetcher
from tests.database_test import DatabaseTest


class TestMediadiveFetcher(DatabaseTest):
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
        component_data = [
            {"id": 1, "name": "dehydrated Wilkins-Chalgren medium", "g_l": 33,     "mmol_l": None},
            {"id": 2, "name": "L-Cysteine HCl",                     "g_l": 0.3,    "mmol_l": 1.90331},
            {"id": 3, "name": "Sodium resazurin",                   "g_l": 0.0005, "mmol_l": 0.00199068},
            {"id": 4, "name": "Distilled water",                    "g_l": None,   "mmol_l": None}
        ]
        expected_payload = {
            "status": 200,
            "count": 5,
            "data": component_data
        }

        with requests_mock.Mocker() as m:
            m.get(
                'https://mediadive.dsmz.de/rest/medium/339',
                json={'data': {'medium': {'id': 339, 'name': 'WC anaerobe broth'}}},
            )
            m.get(
                'https://mediadive.dsmz.de/rest/medium-composition/339',
                json=expected_payload,
            )
            fetcher = MediadiveFetcher('339')

            # Request is successful, ingredients are extracted:
            self.assertTrue(fetcher.make_request())
            self.assertEqual(fetcher.component_data, component_data)

    def test_fetching_media_with_no_composition(self):
        expected_payload = {
            "status": 404,
            "count": 0,
            "error": "DataNotFound",
            "msg": "Medium does not exist"
        }

        with requests_mock.Mocker() as m:
            m.get(
                'https://mediadive.dsmz.de/rest/medium/P1',
                json={'data': {'medium': {'id': 'P1', 'name': 'HaHa agar'}}},
            )
            m.get(
                'https://mediadive.dsmz.de/rest/medium-composition/P1',
                status_code=404,
                json=expected_payload,
            )
            fetcher = MediadiveFetcher('P1')

            # Request is successful, but no ingredients:
            self.assertTrue(fetcher.make_request())
            self.assertEqual(fetcher.component_data, [])

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
            self.assertEqual(fetcher.component_data, None)

    def test_creating_study_records(self):
        study = self.create_study()
        fetcher = MediadiveFetcher('339')

        component_data = [
            {"id": 1, "name": "dehydrated WC medium", "g_l": 33,     "mmol_l": None},
            {"id": 2, "name": "L-Cysteine HCl",       "g_l": 0.3,    "mmol_l": 1.90331},
            {"id": 3, "name": "Sodium resazurin",     "g_l": 0.0005, "mmol_l": 0.00199068},
            {"id": 4, "name": "Distilled water",      "g_l": None,   "mmol_l": None}
        ]

        with requests_mock.Mocker() as m:
            m.get(
                'https://mediadive.dsmz.de/rest/medium/339',
                json={'data': {'medium': {'id': 339, 'name': 'WC anaerobe broth'}}},
            )
            m.get(
                'https://mediadive.dsmz.de/rest/medium-composition/339',
                json={"status": 200, "count": 5, "data": component_data},
            )
            fetcher = MediadiveFetcher('339')

            self.assertTrue(fetcher.make_request())

            fetcher.create_study_records(self.db_session, study)

        self.assertEqual(len(study.media), 1)
        medium = study.media[0]

        self.assertEqual(medium.name, 'WC anaerobe broth')
        self.assertEqual(medium.mediadiveId, '339')

        self.assertEqual([mc.name for mc in medium.components], [
            "dehydrated WC medium",
            "L-Cysteine HCl",
            "Sodium resazurin",
            "Distilled water",
        ])
