import tests.init  # noqa: F401

import unittest

from tests.database_test import DatabaseTest
from app.model.orm import MeasurementContext


class TestMeasurementContext(DatabaseTest):
    def test_auc(self):
        mc = self.create_measurement_context()
        self.assertEqual(mc.calculate_auc(), 0)

        self.create_measurement(contextId=mc.id, timeInSeconds=1, value=10)
        self.create_measurement(contextId=mc.id, timeInSeconds=2, value=10)

        self.db_session.refresh(mc)
        self.assertEqual(mc.calculate_auc(), 10)

        self.create_measurement(contextId=mc.id, timeInSeconds=4, value=10)

        self.db_session.refresh(mc)
        self.assertEqual(mc.calculate_auc(), 30)

        self.create_measurement(contextId=mc.id, timeInSeconds=5, value=20)

        self.db_session.refresh(mc)
        self.assertEqual(mc.calculate_auc(), 45)
