"""A module created to allow similar functionality to the builtin functools, but addressing a few limitations."""
from __future__ import annotations

import functools
import types
import typing
from abc import ABC, abstractmethod
from inspect import getfullargspec
from threading import RLock
from typing import get_type_hints, Dict, Callable, Tuple, Union, Set, List
from util.mro_tool import mro


class ArgParsingError(RuntimeError):
    """An error to be raised if an match cannot be found when processing arguments"""

    def __init__(self, msg=None):
        super().__init__(msg if msg is not None else "Failed to parse args.")


def _handle_args(registry, args, kw, is_method, is_static):
    """process the arguments passed during call so the correct registered function
    can be found by the first positional argument."""

    # Figure out the correct first non-self/non-cls argument index.
    start_index = 1 if is_method and not is_static else 0

    # Handle the case where a call had no arguments.
    if start_index == len(args) and not kw:
        return (args, '')

    # Handle any kw argument matches (kwarg name and type match a registered function's first argument).
    #   Matches are made in mro sequence so more specific matches will be made before more general matches.
    if kw:
        kw_list = [(k, mro(v), v) for k, v in kw.items()]
        max_mro_depth = max([len(mro_val) for _, mro_val, _ in kw_list])
        depth_range = range(0, max_mro_depth)
        for i in depth_range:
            for (name, t), v in registry.items():
                for kw_key, kw_mro, kw_val in kw_list:
                    if kw_key == name and kw_mro[i] == t:
                        args = (args[0], kw_val, *args[1:]) if is_method and not is_static else (kw_val, *args)
                        del kw[kw_key]
                        return (args, name)

    # Handle positional arguments if no kwarg match was found.
    elif start_index < len(args):
        arg = args[start_index]
        arg_mro = mro(arg) if arg is not None else (type(None),)
        max_mro_depth = len(arg_mro)
        depth_range = range(0, max_mro_depth)
        for i in depth_range:
            for (name, t), v in registry.items():
                if name and arg_mro[i] == t:
                    return (args, name)

    # If we have not found a match and returned we'll raise an error
    raise ArgParsingError


def _get_args(func: Callable, is_method: bool, is_static: bool) -> Tuple[Tuple[str, Set[type]]]:
    """ Gets the formal arguments of a function or method

    Returns:
        A collection of arguments stored in a tuple of tuples where the elements have the form (arg_name, set_of_types)
        where arg_name is a str and set_of_types is a set with type elements.

    """

    def __handle_type_hint_args(cls_set: Set[type]) -> Set[type]:
        for cls in cls_set.copy():
            cls_str = str(cls)
            if cls_str.startswith('typing.Optional') \
                    or cls_str.startswith('typing.Union'):
                cls_set.remove(cls)
                cls_set.update(__handle_type_hint_args(set(typing.get_args(cls))))
            elif cls_str.startswith('typing.Any'):
                cls_set.remove(cls)
                cls_set.update({object, type(None)})
            elif cls_str.startswith('typing.'):

                tmp = typing.get_origin(cls)
                if tmp is not None:
                    cls_set.remove(cls)
                    cls_set.update({tmp})

        return cls_set

    return_list: List[Tuple[str, Set[type]]] = []
    spec = getfullargspec(func)
    arg_names = spec.args[1 if is_method and not is_static else 0:]
    try:
        hints = get_type_hints(func)
    except NameError:
        # This happens when a method tries to use its self type as an argument. We want to allow future annotations.
        #   We'll just store the annotation as a str
        hints = spec.annotations

    for arg_name in arg_names:
        if arg_name in hints.keys():
            t: Set[type] = __handle_type_hint_args({hints[arg_name]})
        else:
            t: Set[type] = {object, type(None)}

        return_list.append((arg_name, t))
    return tuple(return_list)


def _find_impl(arg_name, cls, registry):
    """Finds the correct implementation from the registry"""
    for c in mro(cls):

        try:
            try:
                return registry[arg_name, c]
            except KeyError:
                t = c.__name__
                v = registry[arg_name, t]
                registry[arg_name, c] = v
                del registry[arg_name, t]
                return v
        except KeyError:
            ...  # try next


class IllegalRegistryError(TypeError, ABC):
    """An error that occurs if a function is registered that conflicts with a previously registered function."""

    def __init__(self, msg):
        super().__init__(msg)


class IllegalRegistryKeyError(IllegalRegistryError):
    """An error that occurs if a function is registered that could lead to a keyword argument conflict."""

    def __init__(self, dispatch_func: Callable, arg_name: str, arg_type: Union[str, type], is_method: bool, msg=None):
        self.func = dispatch_func
        self.arg_name = arg_name
        self.arg_type = arg_type
        self.is_method = is_method
        self.msg = msg

        func_name = self.func.__name__
        if not isinstance(arg_type, str):
            arg_type = arg_type.__name__
        if msg is None:
            msg = f"{func_name} already has a registered {'method' if is_method else 'function'} with " \
                  f"a{'n' if arg_type.capitalize().startswith(('A', 'E', 'I', 'O', 'U')) else ''} " \
                  f"{arg_type} argument named {arg_name!r}"
        super().__init__(msg)


class IllegalRegistryPositionalTypeError(IllegalRegistryError):
    """An error that occurs if a function is registered that could cause a conflict with positional argument parsing."""

    def __init__(self,
                 dispatch_func: Callable,
                 func_being_registered: Callable,
                 arg_name_being_registered: str, arg_name_previously_registered: str,
                 arg_type: Union[str, type], is_method: bool, msg=None):

        self.dispatch_func = dispatch_func
        """The function that is acting as the dispatcher."""

        self.func_being_registered = func_being_registered
        """The function that was being registered when the error occurred."""

        self.arg_name_being_registered = arg_name_being_registered
        """The name of the argument that was being registered when the error occurred."""

        self.arg_name_previously_registered = arg_name_previously_registered
        """The name of the argument from the previously registered function that is in conflict."""

        self.arg_type = arg_type
        """The type of the arguments that conflict."""

        self.is_method = is_method
        """True if it is a method, false if it is a function."""

        self.msg = msg

        func_name = self.dispatch_func.__name__
        if not isinstance(arg_type, str):
            arg_type = arg_type.__name__
        if msg is None:
            msg = f"{func_name} already has a registered {'method' if is_method else 'function'} with " \
                  f"a{'n' if arg_type.capitalize().startswith(('A', 'E', 'I', 'O', 'U')) else ''} " \
                  f"{arg_type} argument named {self.arg_name_previously_registered!r} that would conflict with the " \
                  f"{self.arg_name_being_registered!r} argument in the {'method' if is_method else 'function'} " \
                  f"being registered."
        super().__init__(msg)


class MismatchError(TypeError, ABC):
    """An error that is raised when two values don't _evaluate to be equal given a evaluation function."""

    @classmethod
    def raise_if_mismatch(cls, value0, value1, *args):
        """Checks to see if two values match given the evaluation method and raises an error if they do not."""
        if cls._evaluate(value0) != cls._evaluate(value1):
            raise cls(value0, value1, *args)

    @classmethod
    @abstractmethod
    def _evaluate(cls, value):
        raise NotImplementedError


class ClassMethodMismatchError(MismatchError):
    """An error that occurs if one but not both the registering and delegating methods are classmethods"""

    def __init__(self, obj0, obj1):
        def __get_str(o):
            return '.'.join(str(o).split('.')[-2:]).split(' ')[0] if isinstance(o, Callable) else repr(o)

        s0 = __get_str(obj0)
        s1 = __get_str(obj1)

        super().__init__(f"{s0} is {'' if self._evaluate(obj0) else 'not '}a classmethod, "
                         f"but {s1} is {'' if self._evaluate(obj1) else 'not '}a classmethod.")

    @classmethod
    def _evaluate(cls, value):
        return isinstance(value, classmethod)


class StaticMethodMismatchError(MismatchError):
    """An error that occurs if one but not both the registering and delegating methods are staticmethods"""

    def __init__(self, obj0, obj1):
        def __get_str(o):
            return '.'.join(str(o).split('.')[-2:]).split(' ')[0] if isinstance(o, Callable) else repr(o)

        s0 = __get_str(obj0)
        s1 = __get_str(obj1)

        super().__init__(f"{s0} is {'' if self._evaluate(obj0) else 'not '}a staticmethod, "
                         f"but {s1} is {'' if self._evaluate(obj1) else 'not '}a staticmethod.")

    @classmethod
    def _evaluate(cls, value):
        return isinstance(value, staticmethod)


def single_dispatch_function(dispatch_func, is_method=False):
    """A function that allows for multiple registered implementations.

    The implementation that will be used is determined by the first parameter of registered functions."""

    lock = RLock()
    with lock:
        d_raw_func_arg = dispatch_func
        is_static = False
        if isinstance(dispatch_func, classmethod):
            dispatch_func = dispatch_func.__func__
        elif isinstance(dispatch_func, staticmethod):
            is_static = True
            dispatch_func = dispatch_func.__func__
        registry: Dict[Tuple[str, Union[type, str]], Callable] = {}
        """keys are tuples in the form (arg_name, type) and the values are the functions to be called if matched """

        set_of_other_used_arguments = set()

        def dispatch(arg_name, cls):

            """ Finds the best registered function given an argument name and type
                Raises:
                    RuntimeError: If a registered function cannot be found.
            """
            with lock:
                impl = _find_impl(arg_name, cls, registry)
                return impl

        def register(cls, func=None):
            """Registers a function with the dispatcher.

            Raises:
                IllegalRegistryError: if the first non-self/non-cls argument name-type combination is
                already registered.

            """

            with lock:
                if func is None:
                    if isinstance(cls, type):
                        return lambda f: register(cls, f)
                    func = cls

                if func is not dispatch_func:
                    ClassMethodMismatchError.raise_if_mismatch(d_raw_func_arg, func)
                    StaticMethodMismatchError.raise_if_mismatch(d_raw_func_arg, func)
                    if isinstance(func, classmethod):
                        func = func.__func__
                    elif isinstance(func, staticmethod):
                        func = func.__func__

                args = _get_args(func, is_method, is_static=is_static)
                if args:
                    arg_name = args[0][0]
                    arg_types = args[0][1]
                else:
                    arg_name = ''
                    arg_types = {type(None)}
                for arg_type in arg_types:
                    key = (arg_name, arg_type)

                    # Check for positional argument conflicts (type must not be in registry).
                    #   Note that we use mro to determine order so only exact matches are considered conflicts.
                    for n, t in list(registry.keys()):
                        if n:
                            if arg_type == t:
                                raise IllegalRegistryPositionalTypeError(dispatch_func,
                                                                         func,
                                                                         arg_name,
                                                                         n,
                                                                         arg_type,
                                                                         is_method)

                    # Check for conflicting keys (same name and type).
                    #   Note that we use mro to determine order so only exact matches are considered conflicts.
                    if key in registry.keys() or key in set_of_other_used_arguments:
                        raise IllegalRegistryKeyError(dispatch_func, arg_name, arg_type, is_method)
                    for n, ts in args[1:]:
                        for t in ts:
                            k = n, t
                            if k in registry.keys():
                                raise IllegalRegistryKeyError(dispatch_func, n, t, is_method)

                    # register it
                    registry[key] = func
                    for k in [[(name, t) for t in t_set] for (name, t_set) in args[1:]]:
                        set_of_other_used_arguments.update(k)

                return func

        def _wrapper(*args, **kw):

            with lock:
                start_index = 1 if is_method and not is_static else 0
                args, arg_name = _handle_args(registry, args, kw, is_method, is_static)

                f = dispatch(arg_name, args[start_index].__class__) if (start_index) < len(args) else dispatch('', type(
                    None))
                if f is None:
                    f = registry['', type(None)]

                return f(*args, **kw)

        register(dispatch_func)
        _wrapper.register = register
        _wrapper.dispatch = dispatch
        _wrapper.registry = types.MappingProxyType(registry)
        functools.update_wrapper(_wrapper, dispatch_func)
        return _wrapper


class __SingleDispatchClassMethod(classmethod):
    def __init__(self, func):
        super().__init__(single_dispatch_function(func, True))

    def register(self, func):
        """Registers a new function for the delegator to access."""
        # noinspection PyUnresolvedReferences
        self.__func__.register(func)


class __SingleDispatchStaticMethod(staticmethod):
    def __init__(self, func):
        super().__init__(single_dispatch_function(func, True))

    def register(self, func):
        """Registers a new function for the delegator to access."""
        # noinspection PyUnresolvedReferences
        self.__func__.register(func)


def single_dispatch_method(func: Union[Callable, classmethod, staticmethod]):
    """A method that allows for multiple registered implementations.

    The implementation that will be used is determined by the first parameter of registered methods."""
    if isinstance(func, classmethod):

        return __SingleDispatchClassMethod(func)

    elif isinstance(func, staticmethod):
        return __SingleDispatchStaticMethod(func)

    else:
        return single_dispatch_function(func, True)
