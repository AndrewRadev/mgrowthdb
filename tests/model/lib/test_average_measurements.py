import tests.init  # noqa: F401

from tests.database_test import DatabaseTest
from app.model.lib.average_measurements import create_average_measurements


class TestSubmissionProcess(DatabaseTest):
    def test_average_measurement_creation(self):
        experiment = self.create_experiment(name="e1")
        study = experiment.study

        c1 = self.create_compartment()
        self.create_experiment_compartment(compartmentId=c1.id, experimentId=experiment.publicId)

        mt1 = self.create_measurement_technique(
            subjectType='bioreplicate',
            study_technique={'studyId': study.publicId},
        )
        mt2 = self.create_measurement_technique(
            subjectType='metabolite',
            study_technique={'studyId': study.publicId},
        )

        b1 = self.create_bioreplicate(name="b1", experimentId=experiment.publicId)
        mc1 = self.create_measurement_context(
            subjectId=b1.id,
            subjectType='bioreplicate',
            bioreplicateId=b1.id,
            techniqueId=mt1.id,
            compartmentId=c1.id,
        )
        for i, value in enumerate([10, 20, 30]):
            self.create_measurement(timeInSeconds=i, value=value, contextId=mc1.id)

        b2 = self.create_bioreplicate(name="b2", experimentId=experiment.publicId)
        mc2 = self.create_measurement_context(
            subjectId=b2.id,
            subjectType='bioreplicate',
            bioreplicateId=b2.id,
            techniqueId=mt1.id,
            compartmentId=c1.id,
        )
        for i, value in enumerate([20, 40, 60]):
            self.create_measurement(timeInSeconds=i, value=value, contextId=mc2.id)

        self.assertEqual({b.name for b in experiment.bioreplicates}, {"b1", "b2"})
        create_average_measurements(self.db_session, study, experiment)
        self.db_session.refresh(experiment)
        self.assertEqual({b.name for b in experiment.bioreplicates}, {"b1", "b2", "Average(e1)"})

        average_bioreplicate = next(b for b in experiment.bioreplicates if b.name == "Average(e1)")
        self.assertEqual(average_bioreplicate.calculationType, 'average')
        self.assertEqual([int(m.value) for m in average_bioreplicate.measurements], [15, 30, 45])

        # Don't create averages if none of their time points match
        b3 = self.create_bioreplicate(name="b3", experimentId=experiment.publicId)
        mc3 = self.create_measurement_context(
            subjectId=b3.id,
            subjectType='bioreplicate',
            bioreplicateId=b3.id,
            techniqueId=mt1.id,
            compartmentId=c1.id,
            studyId=study.publicId,
        )
        for i, value in enumerate([30, 50, 70]):
            # Time points offset by 3 so there's no overlap:
            self.create_measurement(timeInSeconds=i + 3, value=value, contextId=mc3.id)

        self.db_session.delete(average_bioreplicate)
        self.db_session.flush()

        self.db_session.refresh(experiment)

        # Average bioreplicate doesn't get created:
        self.assertEqual({b.name for b in experiment.bioreplicates}, {"b1", "b2", "b3"})
        create_average_measurements(self.db_session, study, experiment)
        self.db_session.refresh(experiment)
        self.assertEqual({b.name for b in experiment.bioreplicates}, {"b1", "b2", "b3"})

        # Delete b1, b2, b3 to avoid interfering with the next averages:
        self.db_session.delete(b1)
        self.db_session.delete(b2)
        self.db_session.delete(b3)
        self.db_session.flush()

        # Don't create averages if they're one measurement context per subject
        b4 = self.create_bioreplicate(name="b4", experimentId=experiment.publicId)
        m1 = self.create_metabolite()
        m2 = self.create_metabolite()
        mc4 = self.create_measurement_context(
            subjectId=m1.id,
            subjectType='metabolite',
            bioreplicateId=b4.id,
            techniqueId=mt2.id,
            compartmentId=c1.id,
            studyId=study.publicId,
        )
        mc5 = self.create_measurement_context(
            subjectId=m2.id,
            subjectType='metabolite',
            bioreplicateId=b4.id,
            techniqueId=mt2.id,
            compartmentId=c1.id,
            studyId=study.publicId,
        )
        for i, value in enumerate([30, 50, 70]):
            self.create_measurement(timeInSeconds=i, value=value, contextId=mc4.id)
            self.create_measurement(timeInSeconds=i, value=value, contextId=mc5.id)

        self.db_session.flush()
        self.db_session.refresh(experiment)

        # Average bioreplicate doesn't get created:
        self.assertEqual({b.name for b in experiment.bioreplicates}, {"b4"})
        create_average_measurements(self.db_session, study, experiment)
        self.db_session.refresh(experiment)
        self.assertEqual({b.name for b in experiment.bioreplicates}, {"b4"})
