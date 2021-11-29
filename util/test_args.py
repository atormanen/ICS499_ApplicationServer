#!/usr/bin/env python3
import unittest

from util.args import *
from util.testing import EnhancedTestCase


class TestCommandDict(EnhancedTestCase):
    def test_add(self):
        @self.inplace_subtest('add and subtract')
        def subtest():
            commands: CommandDict = CommandDict()

            @commands.add(description='add two values')
            def add(x, y):
                return x + y

            @commands.add(description='subtract two values')
            def subtract(x, y):
                return x - y

            self.assertEqual(2, len(commands))

            self.assertEqual('add', commands['add'].name)
            self.assertEqual('add two values', commands['add'].description)
            self.assertEqual(12, commands['add'].action(9, 3))

            self.assertEqual('subtract', commands['subtract'].name)
            self.assertEqual('subtract two values', commands['subtract'].description)
            self.assertEqual(6, commands['subtract'].action(9, 3))


if __name__ == '__main__':
    unittest.main()
