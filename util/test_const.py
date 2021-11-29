#!/usr/bin/env python3
import unittest

from util.const import ConstContainer
from util.testing import EnhancedTestCase

if __name__ == '__main__':
    unittest.main()


class TestConstContainerClass(EnhancedTestCase):

    def test_string_contents_only(self):
        expected_dict = dict(U_BAD_FRIENDS_LIST_PROVIDED='Unexpected Error - There was a problem reading friends list',
                             U_ACCOUNT_DATA_NOT_FOUND='Unexpected Error - Account data was not provided by server.',
                             U_UNSPECIFIED='Unexpected Error - unspecified',
                             U_USER_STATS_COULD_NOT_BE_FOUND='Unexpected Error - User stats could not be found',
                             U_NO_FRIENDS_LIST_PROVIDED_BY_SERVER='Unexpected Error - No friends list provided by '
                                                                  'server',
                             U_NO_RESPONSE_SET_BY_SERVER='Unexpected Error - No response set by server')

        class ClassUnderTest(ConstContainer):
            U_BAD_FRIENDS_LIST_PROVIDED = 'Unexpected Error - There was a problem reading friends list'
            U_ACCOUNT_DATA_NOT_FOUND = 'Unexpected Error - Account data was not provided by server.'
            U_UNSPECIFIED = 'Unexpected Error - unspecified'
            U_USER_STATS_COULD_NOT_BE_FOUND = 'Unexpected Error - User stats could not be found'
            U_NO_FRIENDS_LIST_PROVIDED_BY_SERVER = 'Unexpected Error - No friends list provided by server'
            U_NO_RESPONSE_SET_BY_SERVER = 'Unexpected Error - No response set by server'

        @self.inplace_subtest('test_class_is_subclass_ConstContainerClass')
        def subtest():
            self.assertTrue(issubclass(ClassUnderTest, ConstContainer))

        @self.inplace_subtest('test_values_match')
        def subtest():
            self.assertEqual(len(expected_dict), len(ClassUnderTest.values()))

            for v in expected_dict.values():
                self.assertIn(v, ClassUnderTest.values())

        @self.inplace_subtest('test_items_match')
        def subtest():
            self.assertEqual(len(expected_dict), len(ClassUnderTest.items()))

            for k, v in expected_dict.items():
                self.assertEqual(v, getattr(ClassUnderTest, k))

        @self.inplace_subtest('test_keys_match')
        def subtest():
            self.assertEqual(len(expected_dict), len(ClassUnderTest.keys()))

            for k in expected_dict.keys():
                self.assertIn(k, ClassUnderTest.keys())
