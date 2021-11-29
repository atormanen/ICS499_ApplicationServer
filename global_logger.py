import logging.handlers
import logging.handlers
import os
import pprint
import time
from enum import auto, Enum
from functools import wraps
from typing import Optional, Union, Callable, Collection
from util.const import ConstContainer

# Set up logging level constants
from util.strings import cslist


class LogLevels(ConstContainer):
    CRITICAL = logging.CRITICAL  # 50
    ERROR = logging.ERROR  # 40
    WARNING = logging.WARNING  # 30
    INFO = logging.INFO  # 20
    VERBOSE = 15
    DEBUG = logging.DEBUG  # 10


CRITICAL = LogLevels.CRITICAL  # 50
ERROR = LogLevels.ERROR  # 40
WARNING = LogLevels.WARNING  # 30
INFO = LogLevels.INFO  # 20
VERBOSE = LogLevels.VERBOSE  # 15
DEBUG = LogLevels.DEBUG  # 10

# Setup internal vars
_verbose_level_name = 'VERBOSE'
_log_file = './logs/app_server.log'

# noinspection SpellCheckingInspection
_old_log_formatter = logging.Formatter(
    "%(levelname)-7.7s %(process)-12.12d %(processName)-12.12s %(threadName)-12.12s %(asctime)s: %(message)s")
_log_formatter = logging.Formatter(
    "%(levelname)-8.8s %(threadName)-12.12s: %(message)s")
_logger = logging.getLogger()
logging.addLevelName(VERBOSE, _verbose_level_name)

# Make directory (if it doesn't exist)
try:
    os.makedirs(os.path.dirname(_log_file), exist_ok=True)
except PermissionError:
    ...  # hope that the directory exists and continue

# Setup handlers
file_handler = logging.handlers.WatchedFileHandler(filename=os.environ.get('LOGFILE', _log_file), mode='a+')
file_handler.setFormatter(_log_formatter)
console_handler = logging.StreamHandler()
console_handler.setFormatter(_log_formatter)
_logger.addHandler(file_handler)
_logger.addHandler(console_handler)
_logger.setLevel(logging.DEBUG)


class _LoggedWrapperType(Enum):
    FUNCTION = auto()
    NORMAL_METHOD = auto()
    CLASS_METHOD = auto()

    def build_wrapper(self, __wrapped, __level: Optional[int] = None):
        """Builds a wrapper function

        Args:
            __wrapped:
                The function or method to be wrapped
            __level:
                The logging level. Use one of these constants from the global_logger module:
                CRITICAL, ERROR, WARNING, INFO, VERBOSE, or DEBUG

        Returns:
            A function that wraps a function/method
        """

        @wraps(__wrapped)
        def _wrapper(*args, **kwargs):

            cls = None
            self_obj = None
            exception = None
            return_value = None

            # extract the class or self arguments if needed
            if self is _LoggedWrapperType.NORMAL_METHOD:
                if args:
                    self_obj = args[0]
                    args = tuple(args[1:]) if len(args) > 1 else ()
                else:
                    raise TypeError("self must not be None for methods.")
            if self is _LoggedWrapperType.CLASS_METHOD:
                if args:
                    cls = args[0]
                    args = tuple(args[1:]) if len(args) > 1 else ()
                else:
                    raise TypeError("cls must not be None for class methods.")

            # time the execution of the function/method
            start_time_seconds = time.perf_counter()
            try:
                if self is _LoggedWrapperType.FUNCTION:
                    return_value = __wrapped(*args, **kwargs)
                elif self is _LoggedWrapperType.NORMAL_METHOD:
                    return_value = __wrapped(self_obj, *args, **kwargs)
                elif self is _LoggedWrapperType.CLASS_METHOD:
                    return_value = __wrapped(cls, *args, **kwargs)
            except Exception as e:
                exception = e
            end_time_seconds = time.perf_counter()
            run_time_seconds = end_time_seconds - start_time_seconds

            # build the dictionary that will hold the logged information

            #   Start with empty dictionary
            log_dict: dict = {}

            #   Add the function/method name
            if self is _LoggedWrapperType.FUNCTION:
                name = f'{__wrapped.__name__}'
            elif self is _LoggedWrapperType.NORMAL_METHOD:
                name = f'{type(self_obj).__name__}.{__wrapped.__name__}'
            elif self is _LoggedWrapperType.CLASS_METHOD:
                name = f'{cls.__name__}.{__wrapped.__name__}'
            else:
                raise ValueError(f'Unsupported _WrapperType: {self}')
            #   Add arguments
            log_dict.update({'args': args,
                             'kwargs': kwargs})

            #   Add exceptions or return values
            if exception:
                log_dict.update({'exception': exception,
                                 'exception_type': type(exception)})
            else:
                log_dict.update({'return_value': return_value,
                                 'return_value_type': type(return_value)})

            #   Add info about the run time
            log_dict.update({'run_time': f'{run_time_seconds:.5f} seconds'})

            #   Add info about the self instance if it is a normal method
            if self is _LoggedWrapperType.NORMAL_METHOD:
                log_dict.update(self_object=self_obj.__repr__())

            # build the message
            label = f'CALL {name} details: '
            log_msg = [f'CALL {name}']
            log_msg.extend([f'{label}{line}' for line in pprint.pformat(log_dict).split('\n')])

            # log the message
            for line in log_msg:
                if __level:
                    _logger.log(__level, line)
                else:
                    log(line)

            # return the return value or raise the exception to finish
            if exception:
                raise exception
            else:
                return return_value

        if __wrapped is None:
            def _outer_wrapper(func):
                return self.build_wrapper(func, __level)

            return _outer_wrapper
        else:
            return classmethod(_wrapper) if self is _LoggedWrapperType.CLASS_METHOD else _wrapper


def logged_function(wrapped=None, level: Optional[int] = None):
    """An annotation that allows the annotated function to be logged when called.

    Args:
        wrapped:
            The function to be wrapped.
        level:
            The logging level. Use one of these constants from the global_logger module:
            CRITICAL, ERROR, WARNING, INFO, VERBOSE, or DEBUG

    Returns:
        A function that wraps a function

    """

    return _LoggedWrapperType.FUNCTION.build_wrapper(wrapped, level)


def deprecated(wrapped=None, alternatives: Optional[Union[Callable, Collection[Callable]]] = None) -> Callable:
    """An annotation that logs a warning that the method/function is deprecated.

    Args:
        wrapped:
            The function to be wrapped.
        alternatives:
            The function(s) that should be used instead

    Returns:
        A function that wraps a function

    """

    def _outer_wrapper(func):
        alts = None
        if alternatives:
            if isinstance(alternatives, Collection):
                alts = [f.__name__ for f in alternatives]
            else:
                alts = (alternatives.__name__,)

        deprecated_name = func.__name__
        alt_part_of_msg = '.' if not alts else f", consider using {cslist(alts, conjunction='or')}."
        msg = f'{deprecated_name} is deprecated{alt_part_of_msg}'

        def _wrapper(*args, **kwargs):
            _logger.warning(msg)
            return func(*args, **kwargs)

        return classmethod(_wrapper) if isinstance(func, classmethod) \
            else staticmethod(_wrapper) if isinstance(func, staticmethod) \
            else _wrapper

    if wrapped is None:
        return _outer_wrapper
    else:
        return _outer_wrapper(wrapped)


def logged_method(wrapped=None, level: Optional[int] = None):
    """An annotation that allows the annotated method to be logged when called.

    Args:
        wrapped:
            The method to be wrapped.
        level:
            The logging level. Use one of these constants from the global_logger module:
            CRITICAL, ERROR, WARNING, INFO, VERBOSE, or DEBUG

    Returns:
        A function that wraps a method

    """

    return _LoggedWrapperType.NORMAL_METHOD.build_wrapper(wrapped, level)


def logged_class_method(wrapped=None, level: Optional[int] = None) -> classmethod:
    """An annotation that allows the annotated class method to be logged when called.

    Args:
        wrapped:
            The class method to be wrapped
        level:
            The logging level. Use one of these constants from the global_logger module:
            CRITICAL, ERROR, WARNING, INFO, VERBOSE, or DEBUG

    Returns:
        A function that wraps a class method
    """

    return _LoggedWrapperType.CLASS_METHOD.build_wrapper(wrapped, level)


def log_error(e: Exception, msg=''):
    import traceback
    tb = traceback.format_tb(e.__traceback__)
    tb_lines = []
    for item in tb:
        tb_lines.extend(item.split('\n'))
    _logger.error(f'{msg} - {e!r}' if msg else repr(e))
    for line in tb_lines:
        _logger.error(f'{e!r} traceback: {line}')


def log(msg='', *, label='', level=DEBUG, **kwargs) -> None:
    """Logs a message

    Args:
        msg:
            The message to be logged.
        label:
            A label for the logged message
        level:
            A log level that the message should be logged as (default is DEBUG).
            Use one of these constants from the global_logger module:
            CRITICAL, ERROR, WARNING, INFO, VERBOSE, or DEBUG
        **kwargs:
            Any

    Returns:

    """
    msg = f'{label} - {msg}' if label else msg
    _logger.log(level, msg, **kwargs)
