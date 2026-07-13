import tests.init  # noqa: F401

import unittest
from types import SimpleNamespace

import app.model.lib.util as util


class TestUtil(unittest.TestCase):
    def test_group_by_unique_name(self):
        foo = SimpleNamespace(name="foo")
        bar = SimpleNamespace(name="bar")
        baz = SimpleNamespace(name="baz")

        self.assertEqual(
            util.group_by_unique_name([foo, bar]),
            {"foo": foo, "bar": bar},
        )
        self.assertEqual(
            util.group_by_unique_name([bar, baz]),
            {"bar": bar, "baz": baz},
        )

        with self.assertRaises(ValueError):
            util.group_by_unique_name([foo, bar, bar, baz])

    def test_parse_comma_separated_request_ids(self):
        ids = util.parse_comma_separated_request_ids('ids', {'ids': '1,2,30'})
        self.assertEqual(ids, [1, 2, 30])

        ids = util.parse_comma_separated_request_ids('ids', {'ids': '42'})
        self.assertEqual(ids, [42])

        # Ignore non-digit values:
        ids = util.parse_comma_separated_request_ids('ids', {'ids': '2,abc,3'})
        self.assertEqual(ids, [2, 3])

        # Ignore non-digit parts (e.g. due to accidental copy-paste:
        ids = util.parse_comma_separated_request_ids('ids', {'ids': '15,87"'})
        self.assertEqual(ids, [15, 87])


if __name__ == '__main__':
    unittest.main()
