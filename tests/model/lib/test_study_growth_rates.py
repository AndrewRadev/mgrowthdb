import tests.init  # noqa: F401

from decimal import Decimal

from tests.database_test import DatabaseTest
from app.model.lib.study_growth_rates import calculate_growth_rate


class TestStudyGrowthRates(DatabaseTest):
    def setUp(self):
        super().setUp()

        self.data = [
            (0, 2252333),
            (4, 27694667),
            (8, 365293333),
            (12, 1125370000),
            (16, 1451296667),
            (20, 1310296667),
        ]

    def test_no_calculation_for_non_batch_experiments(self):
        for mode in ('fed-batch', 'chemostat', 'other'):
            e = self.create_experiment(cultivationMode=mode)
            b = self.create_bioreplicate(experimentId=e.publicId)
            mc = self.create_measurement_context(bioreplicateId=b.id, growthRate=None)

            self.assertFalse(calculate_growth_rate(self.db_session, e, mc))

            self.db_session.refresh(mc)
            self.assertIsNone(mc.growthRate)

    def test_no_calculation_for_metabolite_measurements_or_ph(self):
        e = self.create_experiment(cultivationMode='batch')
        b = self.create_bioreplicate(experimentId=e.publicId)
        mc1 = self.create_measurement_context(
            bioreplicateId=b.id,
            growthRate=None,
            subjectType='metabolite',
            subjectId=self.create_metabolite().id,
        )
        mc2 = self.create_measurement_context(
            bioreplicateId=b.id,
            growthRate=None,
            subjectType='bioreplicate',
            subjectId=b.id,
            techniqueId=self.create_measurement_technique(type='ph').id,
        )
        for time, value in self.data:
            self.create_measurement(contextId=mc1.id, timeInSeconds=(time * 3600), value=value)
            self.create_measurement(contextId=mc2.id, timeInSeconds=(time * 3600), value=value)

        for mc in [mc1, mc2]:
            self.assertFalse(calculate_growth_rate(self.db_session, e, mc))
            self.db_session.refresh(mc)
            self.assertIsNone(mc.growthRate)

    def test_growth_rate_calculation(self):
        e = self.create_experiment(cultivationMode='batch')
        b = self.create_bioreplicate(experimentId=e.publicId)
        mc = self.create_measurement_context(
            bioreplicateId=b.id,
            subjectType='bioreplicate',
            subjectId=b.id,
            growthRate=None,
        )
        for time, value in self.data:
            self.create_measurement(contextId=mc.id, timeInSeconds=(time * 3600), value=value)

        self.assertTrue(calculate_growth_rate(self.db_session, e, mc))

        self.db_session.refresh(mc)
        self.assertEqual(mc.growthRate, Decimal('0.416'))

        # A minimum of 6 points are required:
        mc2 = self.create_measurement_context(
            bioreplicateId=b.id,
            subjectType='bioreplicate',
            subjectId=b.id,
            growthRate=None,
        )
        small_data = self.data[0:-2]
        for time, value in small_data:
            self.create_measurement(contextId=mc2.id, timeInSeconds=(time * 3600), value=value)

        self.assertFalse(calculate_growth_rate(self.db_session, e, mc2))
        self.db_session.refresh(mc2)
        self.assertIsNone(mc2.growthRate)
