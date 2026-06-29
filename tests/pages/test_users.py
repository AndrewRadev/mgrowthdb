import tests.init  # noqa: F401

import unittest

from tests.page_test import PageTest
from app.pages.users import _find_or_create_user


class TestUsers(PageTest):
    def test_finding_an_existing_user(self):
        u1 = self.create_user(orcidId='user-1-orcid', uuid='user-1-uuid', name='User 1')
        u2 = self.create_user(orcidId='user-2-orcid', uuid='user-2-uuid', lastLoginAt=None)

        # Last login is updated after finding:
        self.assertIsNone(u2.lastLoginAt)

        user_data1 = {'name': 'User 1', 'access_token': 'abc1', 'orcid': 'user-1-orcid'}
        user_data2 = {'name': 'User 2', 'access_token': 'abc2', 'orcid': 'user-2-orcid'}

        # UUID does not matter for finding
        user = _find_or_create_user(self.db_session, user_data1, 'user-1-uuid')
        self.assertEqual(user, u1)
        user = _find_or_create_user(self.db_session, user_data1, 'user-2-uuid')
        self.assertEqual(user, u1)
        user = _find_or_create_user(self.db_session, user_data2, 'user-2-uuid')
        self.assertEqual(user, u2)

        # Last login is updated after finding:
        self.assertIsNotNone(u2.lastLoginAt)

        # Name gets updated if different:
        self.assertEqual(u1.name, 'User 1')
        user = _find_or_create_user(self.db_session, {**user_data1, 'name': 'U1 (updated)'}, 'user-1-uuid')
        self.assertEqual(u1.name, 'U1 (updated)')

    def test_creating_a_user(self):
        user_data1 = {'name': 'User 1', 'access_token': 'abc1', 'orcid': 'user-1-orcid'}

        # UUID gets set on the created user:
        user = _find_or_create_user(self.db_session, user_data1, 'user-1-uuid')
        self.assertEqual(user.name, 'User 1')
        self.assertEqual(user.uuid, 'user-1-uuid')

        # An API key is set automatically
        self.assertIsNotNone(user.apiKey)

        # A private "default" workspace is created automatically:
        self.assertEqual(len(user.workspaces), 1)
        self.assertEqual(user.workspaces[0].name, 'default')
        self.assertFalse(user.workspaces[0].isPublished)


if __name__ == '__main__':
    unittest.main()
