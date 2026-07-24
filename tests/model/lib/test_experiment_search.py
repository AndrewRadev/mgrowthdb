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

    def test_strains_through_community(self):
        s = self.create_study()

        strain1 = self.create_study_strain(studyId=s.publicId)
        strain2 = self.create_study_strain(studyId=s.publicId)

        c1 = self.create_community(studyId=s.publicId)
        self.create_community_strain(strainId=strain1.id, communityId=c1.id)

        c2 = self.create_community(studyId=s.publicId)
        self.create_community_strain(strainId=strain2.id, communityId=c2.id)

        c12 = self.create_community(studyId=s.publicId)
        self.create_community_strain(strainId=strain1.id, communityId=c12.id)
        self.create_community_strain(strainId=strain2.id, communityId=c12.id)

        e1 = self.create_experiment(studyId=s.publicId, communityId=c1.id)
        e2 = self.create_experiment(studyId=s.publicId, communityId=c2.id)
        e3 = self.create_experiment(studyId=s.publicId, communityId=c12.id)

        search = ExperimentSearch(self.db_session, study=s, strain_ids=[strain1.id])
        self._assertEqualPublicIds(search.fetch_results(), [e1, e3])

        search = ExperimentSearch(self.db_session, study=s, strain_ids=[strain2.id])
        self._assertEqualPublicIds(search.fetch_results(), [e2, e3])

    def test_strains_or_metabolites(self):
        s = self.create_study()

        strain1 = self.create_study_strain(studyId=s.publicId)
        strain2 = self.create_study_strain(studyId=s.publicId)
        metabolite = self.create_study_metabolite(studyId=s.publicId)

        e1 = self.create_experiment(studyId=s.publicId)
        b1 = self.create_bioreplicate(experimentId=e1.publicId)
        mc1 = self.create_measurement_context(
            bioreplicateId=b1.id,
            subjectId=strain1.id,
            subjectType='strain',
        )

        e2 = self.create_experiment(studyId=s.publicId)
        b2 = self.create_bioreplicate(experimentId=e2.publicId)
        b3 = self.create_bioreplicate(experimentId=e2.publicId)
        mc2 = self.create_measurement_context(
            bioreplicateId=b2.id,
            subjectId=strain1.id,
            subjectType='strain',
        )
        mc3 = self.create_measurement_context(
            bioreplicateId=b3.id,
            subjectId=strain2.id,
            subjectType='strain',
        )
        mc4 = self.create_measurement_context(
            bioreplicateId=b3.id,
            subjectId=metabolite.id,
            subjectType='metabolite',
        )

        e3 = self.create_experiment(studyId=s.publicId)
        b4 = self.create_bioreplicate(experimentId=e3.publicId)
        mc5 = self.create_measurement_context(
            bioreplicateId=b4.id,
            subjectId=metabolite.id,
            subjectType='metabolite',
        )

        search = ExperimentSearch(self.db_session, study=s, strain_ids=[strain1.id])
        self._assertEqualPublicIds(search.fetch_results(), [e1, e2])

        search = ExperimentSearch(self.db_session, study=s, strain_ids=[strain2.id])
        self._assertEqualPublicIds(search.fetch_results(), [e2])

        search = ExperimentSearch(self.db_session, study=s, metabolite_ids=[metabolite.id])
        self._assertEqualPublicIds(search.fetch_results(), [e2, e3])

        # Searching for both finds experiments with either one:
        search = ExperimentSearch(
            self.db_session,
            study=s,
            strain_ids=[strain2.id],
            metabolite_ids=[metabolite.id],
        )
        self._assertEqualPublicIds(search.fetch_results(), [e2, e3])

    def test_modeling_types(self):
        s = self.create_study()

        e1 = self.create_experiment(studyId=s.publicId)
        b1 = self.create_bioreplicate(experimentId=e1.publicId)
        mc1 = self.create_measurement_context(bioreplicateId=b1.id)
        mr1 = self.create_modeling_result(type='baranyi_roberts', measurementContextId=mc1.id)
        mr2 = self.create_modeling_result(type='custom_1', measurementContextId=mc1.id)

        e2 = self.create_experiment(studyId=s.publicId)
        b2 = self.create_bioreplicate(experimentId=e2.publicId)
        mc2 = self.create_measurement_context(bioreplicateId=b2.id)
        mr3 = self.create_modeling_result(type='baranyi_roberts', measurementContextId=mc2.id)
        mr4 = self.create_modeling_result(type='custom_2', measurementContextId=mc2.id)

        search = ExperimentSearch(self.db_session, study=s, modeling_types=['baranyi_roberts'])
        self._assertEqualPublicIds(search.fetch_results(), [e1, e2])

        search = ExperimentSearch(self.db_session, study=s, modeling_types=['custom_1'])
        self._assertEqualPublicIds(search.fetch_results(), [e1])

        search = ExperimentSearch(self.db_session, study=s, modeling_types=['custom_2'])
        self._assertEqualPublicIds(search.fetch_results(), [e2])

        search = ExperimentSearch(self.db_session, study=s, modeling_types=['custom_1', 'custom_2'])
        self._assertEqualPublicIds(search.fetch_results(), [e1, e2])

    def _assertEqualPublicIds(self, list1, list2):
        get_public_id = lambda s: s.publicId
        self.assertEqual(
            list(map(get_public_id, list1)),
            list(map(get_public_id, list2)),
        )


if __name__ == '__main__':
    unittest.main()
