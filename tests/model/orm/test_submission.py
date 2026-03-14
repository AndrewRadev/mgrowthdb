import tests.init  # noqa: F401

import re
import os
import tempfile
import unittest
from datetime import datetime, UTC
from pathlib import Path
import contextlib

from tests.database_test import DatabaseTest


class TestStudyTechnique(DatabaseTest):
    def test_export_data(self):
        study = self.create_study(
            publicId="S1",
            name="Exported submission",
            publishedAt=datetime.now(UTC),
        )
        submission = self.create_submission(studyUniqueID=study.uuid)
        submission.export_data("Initial export")

        # Directory used for testing: var/test
        self.assertTrue(os.path.exists("var/test/export/S1.zip"))
        self.assertTrue(os.path.exists("var/test/export/all_studies.zip"))
        self.assertTrue(os.path.isdir("var/test/export/S1"))

        changelog = Path('var/test/export/S1/changes.log').read_text()
        messages = re.sub(r'\[.+?\] ', '[<time>] ', changelog).split("\n")

        self.assertEqual(messages, ["[<time>] Initial export", ""])

        submission.export_data("Minor updates")

        changelog = Path('var/test/export/S1/changes.log').read_text()
        messages = re.sub(r'\[.+?\] ', '[<time>] ', changelog).split("\n")

        self.assertEqual(messages, ["[<time>] Initial export", "[<time>] Minor updates", ""])


if __name__ == '__main__':
    unittest.main()
