
# noinspection PyPep8Naming
from abc import ABC
from typing import Callable
from unittest import TestCase


class EnhancedTestCase(TestCase):
    def inplace_subtest(self, msg, **params):
        def wrapper(func):
            with self.subTest(msg, **params):
                func()
        return wrapper


class TestTemplate(ABC):

    def __init__(self, test_case: TestCase):
        self._test_case = test_case

    def __call__(self) -> None:
        """Runs all tests in template"""
        test_methods = [(name, getattr(self, name)) for name in dir(self) if
                        isinstance(getattr(self, name), Callable) and name.startswith('test')]
        for name, test in test_methods:
            label = name
            if name not in ['test', 'test_']:
                label = name[4:].lstrip('_')
            with self._test_case.subTest(label):
                test()
