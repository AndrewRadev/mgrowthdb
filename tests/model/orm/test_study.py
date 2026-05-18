import tests.init  # noqa: F401

import unittest
from datetime import datetime, timedelta, UTC
from types import SimpleNamespace

import sqlalchemy as sql

from app.model.orm import Study
from tests.database_test import DatabaseTest


class TestStudy(DatabaseTest):
    def test_user_visibility(self):
        study = self.create_study(publishedAt=None, publishableAt=datetime.now(UTC))
        self.create_study_user(studyUniqueID=study.uuid, userUniqueID='user1')
        self.create_study_user(studyUniqueID=study.uuid, userUniqueID='user2')
        self.db_session.flush()

        # Unpublished: only visible to linked users or admins:
        self.assertFalse(study.visible_to_user(None))
        self.assertFalse(study.visible_to_user(SimpleNamespace(uuid='user3', isAdmin=False)))

        self.assertTrue(study.visible_to_user(SimpleNamespace(uuid='user1', isAdmin=False)))
        self.assertTrue(study.visible_to_user(SimpleNamespace(uuid='user2', isAdmin=False)))
        self.assertTrue(study.visible_to_user(SimpleNamespace(uuid='user3', isAdmin=True)))

        self.assertTrue(study.publish(self.db_session))

        # Published: visible to all users:
        self.assertTrue(study.visible_to_user(None))
        self.assertTrue(study.visible_to_user(SimpleNamespace(uuid='user3')))
        self.assertTrue(study.visible_to_user(SimpleNamespace(uuid='user1')))
        self.assertTrue(study.visible_to_user(SimpleNamespace(uuid='user2')))

    def test_generating_available_id(self):
        # The first ID in an empty database should be 001:
        public_id = Study.generate_public_id(self.db_session)
        self.assertEqual(public_id, "SMGDB00000001")

        self.create_study(publicId="SMGDB00000001")

        public_id = Study.generate_public_id(self.db_session)
        self.assertEqual(public_id, "SMGDB00000002")

        self.create_study(publicId="SMGDB00000002")
        self.create_study(publicId="SMGDB00000003")

        # Deleting a project should not generate duplicate ids:
        self.db_session.execute(
            sql.delete(Study)
            .where(Study.publicId == "SMGDB00000002")
        )

        public_id = Study.generate_public_id(self.db_session)
        self.assertEqual(public_id, "SMGDB00000004")

    def test_find_last_submission(self):
        study = self.create_study()

        self.assertIsNone(study.find_last_submission(self.db_session))

        _s1 = self.create_submission(studyUniqueID=study.uuid, updatedAt=(datetime.now(UTC) - timedelta(hours=24)))
        s2  = self.create_submission(studyUniqueID=study.uuid, updatedAt=(datetime.now(UTC) - timedelta(hours=12)))
        _s3 = self.create_submission(studyUniqueID=study.uuid, updatedAt=(datetime.now(UTC) - timedelta(hours=48)))

        self.assertEqual(study.find_last_submission(self.db_session), s2)
        s4 = self.create_submission(studyUniqueID=study.uuid, updatedAt=(datetime.now(UTC) - timedelta(hours=6)))

        self.assertEqual(study.find_last_submission(self.db_session), s4)

    def test_fetch_grouped_measurement_subjects(self):
        study = self.create_study()

        st1 = self.create_study_technique(subjectType="bioreplicate", studyId=study.publicId)
        st2 = self.create_study_technique(subjectType="strain", studyId=study.publicId)
        st3 = self.create_study_technique(subjectType="metaboilte", studyId=study.publicId)

        mt1 = self.create_measurement_technique(studyTechniqueId=st1.id, subjectType="bioreplicate")
        mt2 = self.create_measurement_technique(studyTechniqueId=st2.id, subjectType="strain")
        mt3 = self.create_measurement_technique(studyTechniqueId=st3.id, subjectType="metabolite")

        self.create_measurement_context(techniqueId=mt1.id, subjectId=3, subjectName="br1",       subjectType="bioreplicate")
        self.create_measurement_context(techniqueId=mt1.id, subjectId=4, subjectName="br2",       subjectType="bioreplicate")
        self.create_measurement_context(techniqueId=mt2.id, subjectId=1, subjectName="Blautia",   subjectType="strain")
        self.create_measurement_context(techniqueId=mt2.id, subjectId=2, subjectName="Roseburia", subjectType="strain")
        self.create_measurement_context(techniqueId=mt3.id, subjectId=2, subjectName="glucose",   subjectType="metabolite")
        self.create_measurement_context(techniqueId=mt3.id, subjectId=1, subjectName="trehalose", subjectType="metabolite")
        # Duplicated, ignored:
        self.create_measurement_context(techniqueId=mt1.id, subjectId=3, subjectName="br1",       subjectType="bioreplicate")
        self.create_measurement_context(techniqueId=mt2.id, subjectId=1, subjectName="Blautia",   subjectType="strain")
        self.create_measurement_context(techniqueId=mt3.id, subjectId=1, subjectName="trehalose", subjectType="metabolite")
        # Different study, ignored:
        self.create_measurement_context(subjectId=10, subjectName="br3", subjectType="bioreplicate")

        subjects = study.fetch_grouped_measurement_subjects(self.db_session)

        # Grouped, ordered by type, then ID:
        self.assertEqual(
            subjects,
            [
                ('bioreplicate', [(3, 'br1'),       (4, 'br2')]),
                ('strain',       [(1, 'Blautia'),   (2, 'Roseburia')]),
                ('metabolite',   [(1, 'trehalose'), (2, 'glucose')]),
            ]
        )

    def test_fetch_experiment_ids_by_subject(self):
        study = self.create_study()

        e1 = self.create_experiment(studyId=study.publicId)
        e2 = self.create_experiment(studyId=study.publicId)
        b1 = self.create_bioreplicate(experimentId=e1.publicId)
        b2 = self.create_bioreplicate(experimentId=e2.publicId)

        self.create_measurement_context(bioreplicateId=b1.id, subjectId=4, subjectType="strain")
        self.create_measurement_context(bioreplicateId=b1.id, subjectId=b1.id, subjectType="bioreplicate")
        self.create_measurement_context(bioreplicateId=b2.id, subjectId=b2.id, subjectType="bioreplicate")
        self.create_measurement_context(bioreplicateId=b2.id, subjectId=4, subjectType="strain")
        self.create_measurement_context(bioreplicateId=b2.id, subjectId=5, subjectType="strain")

        experiments = study.fetch_experiment_ids_by_measurement_subject(self.db_session)

        self.assertEqual(experiments, {
            ('bioreplicate', b1.id): [e1.publicId],
            ('bioreplicate', b2.id): [e2.publicId],
            ('strain', 4): [e1.publicId, e2.publicId],
            ('strain', 5): [e2.publicId],
        })


if __name__ == '__main__':
    unittest.main()
