import tests.init  # noqa: F401

import unittest

from app.model.lib.experiment_search import ExperimentSearch
from tests.database_test import DatabaseTest


class TestExperimentSearch(DatabaseTest):
    def test_text_query(self):
        s1 = self.create_study()
        e1 = self.create_experiment(studyId=s1.publicId, name="Foo")
        e2 = self.create_experiment(studyId=s1.publicId, name="Bar")
        e3 = self.create_experiment(studyId=s1.publicId, name="FooBar")
        e4 = self.create_experiment(studyId=s1.publicId, name="Test", description="Bar")

        s2 = self.create_study()
        e5 = self.create_experiment(studyId=s2.publicId, name="Foo")

        search = ExperimentSearch(self.db_session, study=s1, query="foo")
        self._assertEqualPublicIds(search.fetch_results(), [e1, e3])

        search = ExperimentSearch(self.db_session, study=s2, query="foo")
        self._assertEqualPublicIds(search.fetch_results(), [e5])

        search = ExperimentSearch(self.db_session, study=s1, query="BAR")
        self._assertEqualPublicIds(search.fetch_results(), [e2, e3, e4])

        search = ExperimentSearch(self.db_session, study=s1, query="foobar")
        self._assertEqualPublicIds(search.fetch_results(), [e3])

    def test_public_id_query(self):
        s = self.create_study()

        e1  = self.create_experiment(publicId="EMGDB000000001", studyId=s.publicId)
        e2  = self.create_experiment(publicId="EMGDB000000002", studyId=s.publicId)
        e30 = self.create_experiment(publicId="EMGDB000000030", studyId=s.publicId)

        search = ExperimentSearch(self.db_session, study=s, query="EMGDB000000001")
        self._assertEqualPublicIds(search.fetch_results(), [e1])

        search = ExperimentSearch(self.db_session, study=s, query="emgdb2")
        self._assertEqualPublicIds(search.fetch_results(), [e2])

        search = ExperimentSearch(self.db_session, study=s, query="EMGDB30")
        self._assertEqualPublicIds(search.fetch_results(), [e30])

        search = ExperimentSearch(self.db_session, study=s, query="emgdb000000000000000001")
        self._assertEqualPublicIds(search.fetch_results(), [e1])

    def _assertEqualPublicIds(self, list1, list2):
        get_public_id = lambda s: s.publicId
        self.assertEqual(
            list(map(get_public_id, list1)),
            list(map(get_public_id, list2)),
        )


if __name__ == '__main__':
    unittest.main()
