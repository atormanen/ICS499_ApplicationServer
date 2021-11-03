import logging.handlers
import os
import time
from enum import auto, Enum
from functools import wraps
from typing import Optional

# Set up logging level constants
CRITICAL = logging.CRITICAL  # 50
ERROR = logging.ERROR  # 40
WARNING = logging.WARNING  # 30
INFO = logging.INFO  # 20
VERBOSE = 15
DEBUG = logging.DEBUG  # 10

# Setup internal vars
_verbose_level_name = 'VERBOSE'
_log_file = './logs/app_server.log'

# noinspection SpellCheckingInspection
_log_formatter = logging.Formatter(
    "%(levelname)-7.7s %(process)-12.12d %(processName)-12.12s %(threadName)-12.12s %(asctime)s: %(message)s")
logger = logging.getLogger()
logging.addLevelName(VERBOSE, _verbose_level_name)

# Make directory (if it doesn't exist)
os.makedirs(os.path.dirname(_log_file), exist_ok=True)

# Setup handlers
file_handler = logging.handlers.WatchedFileHandler(filename=os.environ.get('LOGFILE', _log_file), mode='a+')
file_handler.setFormatter(_log_formatter)
console_handler = logging.StreamHandler()
console_handler.setFormatter(_log_formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


class _WrapperType(Enum):
    FUNCTION = auto()
    NORMAL_METHOD = auto()
    CLASS_METHOD = auto()

    def build_wrapper(self, __wrapped, __level: Optional[int] = None):
        """ Builds a wrapper function

        :param __wrapped: The function or method to be wrapped
        :param __level: The logging level. Use one of these constants from the global_logger module:
        CRITICAL, ERROR, WARNING, INFO, VERBOSE, or DEBUG
        :return: a function that wraps a function/method
        """

        @wraps(__wrapped)
        def _wrapper(*args, **kwargs):

            cls = None
            self_obj = None
            exception = None
            return_value = None

            # extract the class or self arguments if needed
            if self is _WrapperType.NORMAL_METHOD:
                if args:
                    self_obj = args[0]
                    args = tuple(args[1:]) if len(args) > 1 else ()
                else:
                    raise TypeError("self must not be None for methods.")
            if self is _WrapperType.CLASS_METHOD:
                if args:
                    cls = args[0]
                    args = tuple(args[1:]) if len(args) > 1 else ()
                else:
                    raise TypeError("cls must not be None for class methods.")

            # time the execution of the function/method
            start_time_seconds = time.perf_counter()
            try:
                if self is _WrapperType.FUNCTION:
                    return_value = __wrapped(*args, **kwargs)
                elif self is _WrapperType.NORMAL_METHOD:
                    return_value = __wrapped(self_obj, *args, **kwargs)
                elif self is _WrapperType.CLASS_METHOD:
                    return_value = __wrapped(cls, *args, **kwargs)
            except Exception as e:
                exception = e
            end_time_seconds = time.perf_counter()
            run_time_seconds = end_time_seconds - start_time_seconds

            # build the dictionary that will hold the logged information

            #   Start with empty dictionary
            log_dict: dict = {}

            #   Add the function/method name
            if self is _WrapperType.FUNCTION:
                log_dict.update(function=__wrapped.__name__)
            elif self is _WrapperType.NORMAL_METHOD:
                log_dict.update(method=f'{type(self_obj).__name__}.{__wrapped.__name__}')
            elif self is _WrapperType.CLASS_METHOD:
                log_dict.update(method=f'{cls.__name__}.{__wrapped.__name__}')
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
            if self is _WrapperType.NORMAL_METHOD:
                log_dict.update(self_object=self_obj.__repr__())

            # build the message
            log_msg = f'CALL: {log_dict!r}'

            # log the message
            if __level:
                logger.log(__level, log_msg)
            else:
                logger.debug(log_msg)

            # return the return value or raise the exception to finish
            if exception:
                raise exception
            else:
                return return_value

        return classmethod(_wrapper) if self is _WrapperType.CLASS_METHOD else _wrapper


def logged_function(wrapped, level: Optional[int] = None):
    """An annotation that allows the annotated function to be logged when called.

        :param wrapped: The function to be wrapped
        :param level: The logging level. Use one of these constants from the global_logger module:
        CRITICAL, ERROR, WARNING, INFO, VERBOSE, or DEBUG
        """

    return _WrapperType.FUNCTION.build_wrapper(wrapped, level)


def logged_method(wrapped, level: Optional[int] = None):
    """An annotation that allows the annotated method to be logged when called.

        :param wrapped: The method to be wrapped
        :param level: The logging level. Use one of these constants from the global_logger module:
        CRITICAL, ERROR, WARNING, INFO, VERBOSE, or DEBUG
        """

    return _WrapperType.NORMAL_METHOD.build_wrapper(wrapped, level)


def logged_class_method(wrapped, level: Optional[int] = None) -> classmethod:
    """An annotation that allows the annotated class method to be logged when called.

        :param wrapped: The method to be wrapped
        :param level: The logging level. Use one of these constants from the global_logger module:
        CRITICAL, ERROR, WARNING, INFO, VERBOSE, or DEBUG
        """

    return _WrapperType.CLASS_METHOD.build_wrapper(wrapped, level)


def log(msg='', *, label='generic_log_msg', level=DEBUG, **kwargs) -> None:
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
    logger.log(level, msg, **kwargs)

