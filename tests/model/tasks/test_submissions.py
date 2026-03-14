import tests.init  # noqa: F401

import json
import unittest
from datetime import datetime, timedelta, UTC

from freezegun import freeze_time
import sqlalchemy as sql

from tests.database_test import DatabaseTest
from app.model.tasks.submissions import _publish_eligible_studies


class TestSubmissions(DatabaseTest):
    def test_auto_publish_studies(self):
        with freeze_time(datetime.now(UTC)) as frozen_time:
            deadline = datetime.now(UTC) + timedelta(days=2)
            tomorrow = datetime.now(UTC) + timedelta(days=1)

            s1 = self.create_study(embargoExpiresAt=deadline)
            s2 = self.create_study(embargoExpiresAt=None, publishableAt=tomorrow)

            # After 1 day and a bit, the embargoed study does not become
            # published yet:
            frozen_time.tick(delta=timedelta(days=1, hours=1))
            _publish_eligible_studies(self.db_session)

            self.db_session.refresh(s1)
            self.db_session.refresh(s2)

            self.assertFalse(s1.isPublishable)
            self.assertTrue(s2.isPublishable)

            self.assertFalse(s1.isPublished)
            self.assertFalse(s2.isPublished)

            # After 1 more day and a bit, it becomes published, the other one
            # does not:
            frozen_time.tick(delta=timedelta(days=1, hours=1))
            _publish_eligible_studies(self.db_session)

            self.db_session.refresh(s1)
            self.db_session.refresh(s2)

            self.assertTrue(s1.isPublishable)
            self.assertTrue(s2.isPublishable)

            self.assertTrue(s1.isPublished)
            self.assertFalse(s2.isPublished)


if __name__ == '__main__':
    unittest.main()
