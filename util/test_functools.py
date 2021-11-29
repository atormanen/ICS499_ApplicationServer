from __future__ import annotations

import unittest
from typing import Callable, Union, Optional, Any, Dict

from util.functools import single_dispatch_function, single_dispatch_method, IllegalRegistryError, \
    StaticMethodMismatchError, MismatchError, ClassMethodMismatchError
from util.testing import EnhancedTestCase


# noinspection PyPep8Naming
class Test_single_dispatch_method(EnhancedTestCase):
    def test_register(self):
        @self.inplace_subtest('basic')
        def _():
            class A0(RuntimeError):
                ...

            class B0(A0):
                ...

            class C0(B0):
                ...

            class A1:
                ...

            class B1(A1):
                ...

            class D2(C0, B0):
                ...

            class E(RuntimeError):
                ...

            class C1:

                @single_dispatch_method
                def get_val(self, *args, **kwargs):
                    ...

                @get_val.register
                def _(self, c: Exception):
                    return 'Exception'

                @get_val.register
                def _(self, c: int):
                    return 'int'

                @get_val.register
                def _(self, c: C0):
                    return 'C0'

                @get_val.register
                def _(self, c: C1):
                    return 'C1'

                @get_val.register
                def _(self, c: object):
                    return 'object'

            c0 = C0()
            c1 = C1()

            self.assertIsInstance(c1.get_val, Callable, 'c1.get_val is not callable')
            self.assertEqual('int', c1.get_val(1), 'int positional arg failed')
            self.assertEqual('C0', c1.get_val(c0), 'C0 positional arg failed')
            self.assertEqual('C1', c1.get_val(c1), 'C1 positional arg failed')
            self.assertEqual('object', c1.get_val(C1), 'class positional arg failed')
            self.assertEqual('int', c1.get_val(c=1), 'int kwarg failed')
            self.assertEqual('C0', c1.get_val(c=c0), 'C0 kwarg failed')
            self.assertEqual('C1', c1.get_val(c=c1), 'C1 kwarg failed')
            self.assertEqual('object', c1.get_val(c=C1), 'class kwarg failed')

        @self.inplace_subtest('check mro')
        def _():
            class A(TypeError):
                ...

            class B:
                ...

            class C(A, B):
                ...

            class D:
                ...

            class E(D):
                ...

            class F(C, E):
                ...

            class G(E, C):
                ...

            class H(B):
                ...

            class I(H, D):
                ...

            class J(B):
                ...

            class Checker:
                @single_dispatch_method
                def get_val(self, *args, **kwargs):
                    ...

                @get_val.register
                def _(self, c: Exception):
                    return 'Exception'

                @get_val.register
                def _(self, c: D):
                    return 'D'

                @get_val.register
                def _(self, c: object):
                    return 'object'

            checker = Checker()
            self.assertEqual('Exception', checker.get_val(c=F()), 'check inheritance order C, E')
            self.assertEqual('D', checker.get_val(c=G()), 'check inheritance order E, C')
            self.assertEqual('D', checker.get_val(c=I()), 'makes sure object is last match')
            self.assertEqual('object', checker.get_val(c=J()), 'checks that object is matched')

        @self.inplace_subtest('no arg check')
        def _():
            class C:
                @single_dispatch_method
                def get_val(self):
                    return 'empty'

                @get_val.register
                def _(self, c: object):
                    return 'object'

            c = C()
            self.assertEqual('object', c.get_val(c=1), 'check with kwarg')
            self.assertEqual('object', c.get_val(1), 'check with arg')
            self.assertEqual('empty', c.get_val(), 'check without arg')

        @self.inplace_subtest('recursive')
        def _():
            class C:
                @single_dispatch_method
                def get_val(self):
                    return 'empty'

                @get_val.register
                def _(self, c: object):
                    print(f'self: {self!r}')
                    print(f'type(self): {type(self)!r}')

                    return self.get_val()

            c = C()
            self.assertEqual('empty', c.get_val(1), 'check with arg')
            self.assertEqual('empty', c.get_val(), 'check without arg')

        @self.inplace_subtest('Union type hint')
        def _():
            class A:
                @single_dispatch_method
                def f(self):
                    return 'f'

                @f.register
                def _(self, a: object):
                    return 'object'

                @f.register
                def _(self, b: Union[int, str]):
                    return 'Union[int, str]'

            a = A()
            self.assertEqual('Union[int, str]', a.f(1))
            self.assertEqual('Union[int, str]', a.f('a'))
            self.assertEqual('object', a.f(3.14))
            self.assertEqual('f', a.f())

        @self.inplace_subtest('Optional type hint')
        def _():
            class A:
                @single_dispatch_method
                def f(self):
                    return 'f'

                @f.register
                def _(self, a: object):
                    return 'object'

                @f.register
                def _(self, b: Optional[str]):
                    return 'Optional[str]'

            a = A()
            self.assertEqual('Optional[str]', a.f(b='a'))
            self.assertEqual('Optional[str]', a.f(b=None))
            self.assertEqual('Optional[str]', a.f('a'))
            self.assertEqual('Optional[str]', a.f(None))
            self.assertEqual('f', a.f())
            self.assertEqual('object', a.f(3.14))
            self.assertEqual('f', a.f())

        @self.inplace_subtest('Any type hint')
        def _():
            class A:
                @single_dispatch_method
                def f(self):
                    return 'f'

                @f.register
                def _(self, b: Any):
                    return 'Any'

            a = A()
            self.assertEqual('Any', a.f(b='a'))
            self.assertEqual('Any', a.f(b=None))
            self.assertEqual('Any', a.f(b=3.14))
            self.assertEqual('Any', a.f('a'))
            self.assertEqual('Any', a.f(None))
            self.assertEqual('Any', a.f(3.14))
            self.assertEqual('f', a.f())

        @self.inplace_subtest('Dict type hint')
        def _():
            class A:
                @single_dispatch_method
                def f(self):
                    return 'f'

                @f.register
                def _(self, b: object):
                    return 'object'

                @f.register
                def _(self, c: Dict[str, int]):
                    return 'Dict'

            a = A()
            self.assertEqual('object', a.f(b='a'))
            self.assertEqual('object', a.f(b=None))
            self.assertEqual('object', a.f(b=3.14))
            self.assertEqual('object', a.f(b={'a': 1}))
            self.assertEqual('Dict', a.f(c={'a': 1}))
            self.assertEqual('Dict', a.f({'a': 1}))
            self.assertEqual('f', a.f())

        @self.inplace_subtest('unacceptable repetition')
        def _():
            expected_exception_type = IllegalRegistryError
            with self.assertRaises(expected_exception_type,
                                   msg='a starting argument name-type combo was previously used as a '
                                       'non-starting argument'):
                class A:
                    @single_dispatch_method
                    def get_val(self, *args, **kwargs):
                        ...

                    @get_val.register
                    def _(self, a: int, b: str):
                        return 'empty'

                    @get_val.register
                    def _(self, b: str, c: int):  # repeat b
                        return 'empty'

            with self.assertRaises(expected_exception_type,
                                   msg='a registered argument name-type combo is repeated as a non-starting '
                                       'argument later'):
                class B:
                    @single_dispatch_method
                    def get_val(self, *args, **kwargs):
                        ...

                    @get_val.register
                    def _(self, a: int, c: int):
                        return 'empty'

                    @get_val.register
                    def _(self, b: str, a: int):  # repeat a
                        return 'empty'

            with self.assertRaises(expected_exception_type, msg='repeat starting argument type'):
                class C:
                    @single_dispatch_method
                    def get_val(self, a: int):
                        ...

                    @get_val.register
                    def _(self, b: int, c: int):
                        return 'empty'

        @self.inplace_subtest('acceptable repetition')
        def _():
            class A:
                @single_dispatch_method
                def get_val(self, *args, **kwargs):
                    ...

                @get_val.register
                def _(self, a: int, b: str):
                    return 'empty'

                @get_val.register
                def _(self, c: str, b: str):  # repeat b, but it should be allowed
                    return 'empty'

        @self.inplace_subtest('class method')
        def _():
            class A:

                @single_dispatch_method
                @classmethod
                def get_val(cls):
                    return ''

                @get_val.register
                @classmethod
                def _(cls, a: int):
                    return 'int'

            self.assertEqual('int', A.get_val(3))

        @self.inplace_subtest('static method')
        def _():
            class A:

                @single_dispatch_method
                @staticmethod
                def get_val():
                    return ''

                @get_val.register
                @staticmethod
                def _(a: int):
                    return 'int'

            self.assertEqual('int', A.get_val(3))

            with self.assertRaises(ClassMethodMismatchError, msg='non-classmethod dispatcher, classmethod register'):
                class A:

                    @single_dispatch_method
                    def get_val(self):
                        return ''

                    @get_val.register
                    @classmethod
                    def _(cls, a: int):
                        return 'int'

            with self.assertRaises(ClassMethodMismatchError, msg='classmethod dispatcher, non-classmethod register'):
                class A:

                    @single_dispatch_method
                    @classmethod
                    def get_val(cls):
                        return ''

                    @get_val.register
                    def _(self, a: int):
                        return 'int'

            with self.assertRaises(StaticMethodMismatchError, msg='non-static dispatcher, static register'):
                class A:

                    @single_dispatch_method
                    def get_val(self):
                        return ''

                    @get_val.register
                    @staticmethod
                    def _(a: int):
                        return 'int'

            with self.assertRaises(StaticMethodMismatchError, msg='static dispatcher, non-static register'):
                class A:

                    @single_dispatch_method
                    @staticmethod
                    def get_val():
                        return ''

                    @get_val.register
                    def _(self, a: int):
                        return 'int'

            with self.assertRaises(MismatchError, msg='classmethod dispatcher, static register'):
                class A:

                    @single_dispatch_method
                    @classmethod
                    def get_val(cls):
                        return ''

                    @get_val.register
                    @staticmethod
                    def _(a: int):
                        return 'int'

            with self.assertRaises(MismatchError, msg='static dispatcher, classmethod register'):
                class A:

                    @single_dispatch_method
                    @staticmethod
                    def get_val():
                        return ''

                    @get_val.register
                    @classmethod
                    def _(cls, a: int):
                        return 'int'


# noinspection PyPep8Naming
class Test_single_dispatch_function(EnhancedTestCase):
    def test_register(self):
        @self.inplace_subtest('basic')
        def _():
            class A0(RuntimeError):
                ...

            class B0(A0):
                ...

            class C0(B0):
                ...

            class A1:
                ...

            class B1(A1):
                ...

            class D2(C0, B0):
                ...

            class E(RuntimeError):
                ...

            class C1:
                ...

            @single_dispatch_function
            def get_val(*args, **kwargs):
                ...

            @get_val.register
            def _(c: Exception):
                return 'Exception'

            @get_val.register
            def _(c: int):
                return 'int'

            @get_val.register
            def _(c: C0):
                return 'C0'

            @get_val.register
            def _(c: C1):
                return 'C1'

            @get_val.register
            def _(c: object):
                return 'object'

            c0 = C0()
            c1 = C1()
            a1 = A1()
            a0 = A0()
            b0 = B0()
            b1 = B1()
            d2 = D2()
            e = E()

            self.assertIsInstance(get_val, Callable, 'get_val is not callable')
            self.assertEqual('int', get_val(1), 'int positional arg failed')
            self.assertEqual('C0', get_val(c0), 'C0 positional arg failed')
            self.assertEqual('C1', get_val(c1), 'C1 positional arg failed')
            self.assertEqual('object', get_val(C1), 'class positional arg failed')
            self.assertEqual('int', get_val(c=1), 'int kwarg failed')
            self.assertEqual('C0', get_val(c=c0), 'C0 kwarg failed')
            self.assertEqual('C1', get_val(c=c1), 'C1 kwarg failed')
            self.assertEqual('object', get_val(c=C1), 'class kwarg failed')

        @self.inplace_subtest('check mro')
        def _():
            class A(TypeError):
                ...

            class B:
                ...

            class C(A, B):
                ...

            class D:
                ...

            class E(D):
                ...

            class F(C, E):
                ...

            class G(E, C):
                ...

            class H(B):
                ...

            class I(H, D):
                ...

            class J(B):
                ...

            @single_dispatch_function
            def get_val(*args, **kwargs):
                ...

            @get_val.register
            def _(c: Exception):
                return 'Exception'

            @get_val.register
            def _(c: D):
                return 'D'

            @get_val.register
            def _(c: object):
                return 'object'

            self.assertEqual('Exception', get_val(c=F()), 'check inheritance order C, E')
            self.assertEqual('D', get_val(c=G()), 'check inheritance order E, C')
            self.assertEqual('D', get_val(c=I()), 'makes sure object is last match')
            self.assertEqual('object', get_val(c=J()), 'checks that object is matched')

        @self.inplace_subtest('no arg check')
        def _():
            @single_dispatch_function
            def get_val(s: str):
                return 'str'

            @get_val.register
            def _(c: object):
                return 'object'

            @get_val.register
            def _():
                return 'empty'

            self.assertEqual('object', get_val(c=1), 'check with arg')
            self.assertEqual('str', get_val('t'), 'check with arg')
            self.assertEqual('empty', get_val(), 'check without arg')

            @self.inplace_subtest('repeat key')
            def _():
                expected_exception_type = Exception
                with self.assertRaises(expected_exception_type):
                    @single_dispatch_function
                    def get_val(*args, **kwargs):
                        ...

                    @get_val.register
                    def _(a: int, b):
                        return 'empty'

                    @get_val.register
                    def _(b: int, c):  # repeat b
                        return 'empty'

                with self.assertRaises(expected_exception_type):
                    @single_dispatch_function
                    def get_val(*args, **kwargs):
                        ...

                    @get_val.register
                    def _(a: int, c):
                        return 'empty'

                    @get_val.register
                    def _(b: int, a):  # repeat a
                        return 'empty'


if __name__ == '__main__':
    unittest.main()
