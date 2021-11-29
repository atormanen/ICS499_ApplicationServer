import unittest

from util.strings import cslist
from util.testing import EnhancedTestCase


class Test(EnhancedTestCase):
    def test_cslist(self):
        class _TestData:
            def __init__(self, label, expected_return_value, /, *args, **kwargs):
                self.label = label
                self.expected_return_value = expected_return_value
                self.actual_value = cslist(*args, **kwargs)

            def __str__(self):
                return str(self.label)

            def __repr__(self):
                return str(self.label)

        data_list = [_TestData('string argument', 'a b, c d', ['a b, c d']),
                     _TestData('single element list of strings', 'a', ['a']),
                     _TestData('single element non-oxford', 'a', ['a'], use_oxford_comma=False),
                     _TestData('single element or conjunction', 'a', ['a'], conjunction='or'),
                     _TestData('two element list of strings', 'a and b', ['a', 'b']),
                     _TestData('two element non-oxford comma', 'a and b', ['a', 'b'], use_oxford_comma=False),
                     _TestData('two element or conjunction', 'a or b', ['a', 'b'], conjunction='or'),
                     _TestData('three element list of strings', 'a, b, and c', ['a', 'b', 'c']),
                     _TestData('three element non-oxford comma', 'a, b and c', ['a', 'b', 'c'], use_oxford_comma=False),
                     _TestData('three element or conjunction', 'a, b, or c', ['a', 'b', 'c'], conjunction='or')]

        for data in data_list:
            @self.inplace_subtest(data.label)
            def _():
                self.assertEqual(data.expected_return_value, data.actual_value)


if __name__ == '__main__':
    unittest.main()
