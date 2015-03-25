from nose.tools import *

from framework import auth
from website import models
from tests import base
from tests import factories


class UserTestCase(base.OsfTestCase):
    def setUp(self):
        super(UserTestCase, self).setUp()
        self.user = factories.AuthUserFactory()
        self.unregistered = factories.UnregUserFactory()
        self.unconfirmed = factories.UnconfirmedUserFactory()
        self.USERS = (self.user, self.unregistered, self.unconfirmed)

        factories.ProjectFactory(creator=self.user)
        self.project_with_unreg_contrib = factories.ProjectFactory()
        self.project_with_unreg_contrib.add_unregistered_contributor(
            fullname='Unreg',
            email=self.unregistered.username,
            auth=auth.Auth(self.project_with_unreg_contrib.creator)
        )
        self.project_with_unreg_contrib.save()

        self.user.system_tags = ['shared', 'user']
        self.unconfirmed.system_tags = ['shared', 'unconfirmed']

        self.user.aka = ['shared', 'user']
        self.unconfirmed.aka = ['shared', 'unconfirmed']

    def tearDown(self):
        models.Node.remove()
        models.User.remove()
        super(UserTestCase, self).tearDown()

    def test_can_be_merged(self):
        assert_false(self.user.can_be_merged)
        assert_true(self.unregistered.can_be_merged)
        assert_true(self.unconfirmed.can_be_merged)

    def test_merge_unconfirmed(self):
        self.user.merge_user(self.unconfirmed)

        assert_true(self.unconfirmed.is_merged)
        assert_equal(self.unconfirmed.merged_by, self.user)

        assert_true(self.user.is_claimed)
        assert_false(self.user.is_invited)

        # TODO: test profile fields - jobs, schools, social
        # TODO: test security_messages
        # TODO: test mailing_lists

        assert_equal(self.user.system_tags, ['shared', 'user', 'unconfirmed'])
        assert_equal(self.user.aka, ['shared', 'user', 'unconfirmed'])

        # TODO: test emails
        # TODO: test watched
        # TODO: test external_accounts

        # TODO: test api_keys
        assert_equal(self.unconfirmed.email_verifications, {})
        assert_is_none(self.unconfirmed.username)
        assert_is_none(self.unconfirmed.password)
        assert_is_none(self.unconfirmed.verification_key)

    def test_merge_unregistered(self):
        # test only those behaviors that are not tested with unconfirmed users
        self.user.merge_user(self.unregistered)

        assert_true(self.user.is_invited)

        assert_in(self.user, self.project_with_unreg_contrib.contributors)