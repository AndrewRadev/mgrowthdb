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

    def test_pluralize(self):
        self.assertEqual(util.pluralize(1, 'measurement'), '1 measurement')
        self.assertEqual(util.pluralize(1, 'person'),      '1 person')

        self.assertEqual(util.pluralize(2, 'measurement'), '2 measurements')
        self.assertEqual(util.pluralize(3, 'strain'),      '3 strains')
        self.assertEqual(util.pluralize(0, 'metabolite'),  '0 metabolites')
        self.assertEqual(util.pluralize(5, 'study'),       '5 studies')

        # Irregular words
        self.assertEqual(util.pluralize(2, 'person'), '2 people')
        self.assertEqual(util.pluralize(2, 'medium'), '2 media')

        # Multiple words, use the last one:
        self.assertEqual(util.pluralize(2, 'community-level strain'), '2 community-level strains')
        self.assertEqual(util.pluralize(2, 'bacterial growth medium'), '2 bacterial growth media')


if __name__ == '__main__':
    unittest.main()
