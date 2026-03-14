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
        with self._cd_in_tmpdir():
            study = self.create_study(
                publicId="S1",
                name="Exported submission",
                publishedAt=datetime.now(UTC),
            )
            submission = self.create_submission(studyUniqueID=study.uuid)
            submission.export_data("Initial export")

            self.assertTrue(os.path.exists("static/export/S1.zip"))
            self.assertTrue(os.path.exists("static/export/all_studies.zip"))
            self.assertTrue(os.path.isdir("static/export/S1"))

            changelog = Path('static/export/S1/changes.log').read_text()
            messages = re.sub(r'\[.+?\] ', '[<time>] ', changelog).split("\n")

            self.assertEqual(messages, ["[<time>] Initial export", ""])

            submission.export_data("Minor updates")

            changelog = Path('static/export/S1/changes.log').read_text()
            messages = re.sub(r'\[.+?\] ', '[<time>] ', changelog).split("\n")

            self.assertEqual(messages, ["[<time>] Initial export", "[<time>] Minor updates", ""])

    @contextlib.contextmanager
    def _cd_in_tmpdir(self):
        current_dir = os.getcwd()

        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                os.chdir(tmp_dir)
                yield
        finally:
            os.chdir(current_dir)


if __name__ == '__main__':
    unittest.main()
