import tests.init  # noqa: F401

import tempfile
import unittest
from pathlib import Path

from app.model.lib.backups import (
    create_backup,
    clean_backups,
)


class TestBackups(unittest.TestCase):
    def setUp(self):
        self.root_dir  = tempfile.TemporaryDirectory()
        self.root_path = Path(self.root_dir.name)

    def tearDown(self):
        self.root_dir.cleanup()

    def test_create_backup(self):
        self.assertEqual(list(self.root_path.iterdir()), [])

        create_backup(self.root_path / 'b1.sql')
        self.assertEqual(self._filenames_in_root_dir(), ['b1.sql'])

        create_backup(self.root_path / 'b2.sql')
        self.assertEqual(self._filenames_in_root_dir(), ['b1.sql', 'b2.sql'])

    def test_clean_backups(self):
        # Noop if there are no files:
        self.assertEqual(self._filenames_in_root_dir(), [])
        clean_backups(str(self.root_path), max_count=3)
        self.assertEqual(self._filenames_in_root_dir(), [])

        for i in range(5):
            (self.root_path / f"b{i + 1}.sql").touch()

        self.assertEqual(self._filenames_in_root_dir(), ['b1.sql', 'b2.sql', 'b3.sql', 'b4.sql', 'b5.sql'])

        clean_backups(str(self.root_path), max_count=3)
        self.assertEqual(self._filenames_in_root_dir(), ['b3.sql', 'b4.sql', 'b5.sql'])

        clean_backups(str(self.root_path), max_count=2)
        self.assertEqual(self._filenames_in_root_dir(), ['b4.sql', 'b5.sql'])

        # Ignore non-sql files:
        (self.root_path / 'test.txt').touch()
        (self.root_path / '.keep').touch()

        clean_backups(str(self.root_path), max_count=2)
        self.assertEqual(self._filenames_in_root_dir(), ['.keep', 'b4.sql', 'b5.sql', 'test.txt'])

    def _filenames_in_root_dir(self):
        return [p.name for p in sorted(self.root_path.iterdir())]


if __name__ == '__main__':
    unittest.main()
