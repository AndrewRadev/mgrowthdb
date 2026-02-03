import tests.init  # noqa: F401

import unittest

from app.view.filters.urls import author_link_list

class TestText(unittest.TestCase):
    def test_authors_link_list_renders_correctly(self):
        authors = [{
            'ORCID': 'https://orcid.org/0000-0001-7280-9915',
            'given': 'Sudarshan A',
            'family': 'Shetty',
            'sequence': 'first',
        }, {
            'given': 'Ioannis',
            'family': 'Kostopoulos',
            'sequence': 'additional',
        }, {
            'given': 'Sharon Y',
            'family': 'Geerlings',
            'sequence': 'additional',
        }]

        link_list = author_link_list(authors)

        self.assertIn("Shetty, S. A.", link_list)
        self.assertIn("Kostopoulos, I.", link_list)
        self.assertIn("Geerlings, S. Y.", link_list)

        # The first name is rendered as an URL:
        self.assertIn('href="https://orcid.org/0000-0001-7280-9915"', link_list)

        # Given words in order are highlighted, case-insensitively:
        link_list = author_link_list(authors, query_words=["kost", "los"])

        self.assertIn(
            """<span class="highlight">Kost</span>opou<span class="highlight">los</span>, I.""",
            link_list,
        )

    def test_authors_link_list_truncates(self):
        # Note: also handles special whitespace
        authors = [{
            'given': 'Eric\xa0W',
            'family': 'Sayers',
            'sequence': 'first',
        }, {
            'given': 'Jeffrey',
            'family': 'Beck',
            'sequence': 'first',
        }, {
            'given': 'Evan\xa0E',
            'family': 'Bolton',
            'sequence': 'additional',
        }, {
            'given': 'J\xa0Rodney',
            'family': 'Brister',
            'sequence': 'additional',
        }, {
            'given': 'Jessica',
            'family': 'Chan',
            'sequence': 'additional',
        }]

        link_list = author_link_list(authors, limit=3)
        self.assertEqual(link_list.split(', '), [
            'Sayers', 'E. W.',
            'Beck', 'J.',
            'Bolton', 'E. E.',
            'and 2 more',
        ])

        # Authors marked as "first" are always rendered:
        link_list = author_link_list(authors, limit=2)
        self.assertEqual(link_list.split(', '), [
            'Sayers', 'E. W.',
            'Beck', 'J.',
            'and 3 more',
        ])

        link_list = author_link_list(authors, limit=1)
        self.assertEqual(link_list.split(', '), [
            'Sayers', 'E. W.',
            'Beck', 'J.',
            'and 3 more',
        ])

        # If a searched-for user is matched, show them before the "and N more" part:
        link_list = author_link_list(authors, limit=1, query_words=['Chan'])
        self.assertEqual(link_list.split(', '), [
            'Sayers', 'E. W.',
            'Beck', 'J.',
            '<span class="highlight">Chan</span>', 'J.',
            'and 2 more',
        ])
