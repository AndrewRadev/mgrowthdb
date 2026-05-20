import tests.init  # noqa: F401

import unittest

import pandas as pd

from app.model.orm import WorkspaceEntry
from tests.database_test import DatabaseTest


class TestWorkspaceEntry(DatabaseTest):
    def test_create_from_csv(self):
        workspace = self.create_workspace()

        # Without error columns:
        df = pd.DataFrame.from_dict({
            'Time': [1, 2, 3],
            'Roseburia': [1e6, 1e7, 1e8],
            'Blautia': [1e6, 1e7, 1e8],
        })
        entries = WorkspaceEntry.from_upload(df, workspace)

        self.assertEqual([e.label for e in entries], ['Roseburia', 'Blautia'])
        self.assertEqual(entries[0].workspace, workspace)
        self.assertEqual(entries[0].get_df().columns.tolist(), ['time', 'value'])

        # With error columns:
        df = pd.DataFrame.from_dict({
            'time': [1, 2, 3],
            'glucose': [10, 9, 8],
            'glucose STD': [0.1, 0.1, 0.1],
            'trehalose': [10, 9, 8],
            'trehalose STD': [0.1, 0.1, 0.1],
        })
        entries = WorkspaceEntry.from_upload(df, workspace, include_error=True)

        self.assertEqual([e.label for e in entries], ['glucose', 'trehalose'])
        self.assertEqual(entries[0].workspace, workspace)
        self.assertEqual(entries[0].get_df().columns.tolist(), ['time', 'value', 'error'])

        # With additional metadata
        df = pd.DataFrame.from_dict({
            'time': [1, 2, 3],
            'glucose': [10, 9, 8],
            'trehalose': [10, 9, 8],
        })
        entries = WorkspaceEntry.from_upload(
            df,
            workspace,
            metadata={
                'dataType': 'measurement',
                'subjectType': 'metabolite',
                'units': 'mM',
            }
        )

        self.assertEqual([e.dataType for e in entries], ['measurement', 'measurement'])
        self.assertEqual([e.subjectType for e in entries], ['metabolite', 'metabolite'])
        self.assertEqual([e.units for e in entries], ['mM', 'mM'])


if __name__ == '__main__':
    unittest.main()
