import tests.init  # noqa: F401

import unittest
from io import StringIO

import pandas as pd

from tests.page_test import PageTest
from app.pages.workspaces import _process_upload


class TestWorkspaces(PageTest):
    def test_numeric_column_filtering(self):
        df = pd.DataFrame.from_dict({
            'Strings 1': ['a', 'b', 'c'],
            'Time': [1, 2, 3],
            'Strings 2': ['100', '200', 'abc'],
            'Value': [100, 200, 300],
        })

        df, errors, warnings = _process_upload(StringIO(df.to_csv(index=False)))

        self.assertEqual(df.columns.tolist(), ['Time', 'Value'])
        self.assertEqual(warnings, ['Ignoring non-numeric columns: Strings 1, Strings 2'])
        self.assertEqual(errors, [])

    def test_columns_and_row_counts(self):
        df = pd.DataFrame.from_dict({'Time': []})
        df, errors, warnings = _process_upload(StringIO(df.to_csv(index=False)))

        self.assertEqual(warnings, [])
        self.assertEqual(errors, ['No data rows were found'])

        df = pd.DataFrame.from_dict({'Time': [1]})
        df, errors, warnings = _process_upload(StringIO(df.to_csv(index=False)))

        self.assertEqual(warnings, [])
        self.assertEqual(errors, ['At least 2 columns are expected, 1 were found'])

    def test_unique_time_column(self):
        df = pd.DataFrame.from_dict({
            'Time': [1, 1, 2, 3],
            'Value': [100] * 4,
        })
        df, errors, warnings = _process_upload(StringIO(df.to_csv(index=False)))

        self.assertEqual(warnings, [])
        self.assertEqual(errors, ['Duplicated time values: 1'])

        df = pd.DataFrame.from_dict({
            'Time': [1, 2, 1, 3, 4, 3, 4],
            'Value': [100] * 7,
        })
        df, errors, warnings = _process_upload(StringIO(df.to_csv(index=False)))

        self.assertEqual(warnings, [])
        self.assertEqual(errors, [
            'Duplicated time values: 1, 3, 4',
            'Time values are not monotonic, are there multiple measurement targets in a single data file?',
        ])


if __name__ == '__main__':
    unittest.main()
