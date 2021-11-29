import unittest

import global_logger
from global_logger import logged_function, logged_class_method, deprecated, logged_method
from util.testing import EnhancedTestCase


class TestGlobalLogger(EnhancedTestCase):
    def test_logged_class_method(self):

        class Button:
            # noinspection PyMethodParameters,PyMissingOrEmptyDocstring
            @logged_class_method
            def push(cls, times_pressed=1) -> str:
                tmp_str = f' {times_pressed} times' if times_pressed > 1 else ''
                return f'Someone pushed the button{tmp_str}'

        with self.subTest('kwargs'):

            global_logger._SINGLE_LINE_MODE = True

            expected_return_value_string = 'Someone pushed the button 3 times'

            length = []
            # noinspection PyUnusedLocal
            actual_added_lines = []
            with open('./logs/app_server.log', 'r') as f:
                lines = f.read().splitlines()
                length.append(len(lines))

            actual_return_value_string = Button.push(times_pressed=3)
            self.assertEqual(expected_return_value_string, actual_return_value_string,
                             f'The returned string "{actual_return_value_string}" did not match \
                             "{expected_return_value_string}" when pushing button.')

            with open('./logs/app_server.log', 'r') as f:
                lines = f.read().splitlines()
                length.append(len(lines))
                actual_added_lines = lines[length[0]:]
                added_msg = '\n'.join(actual_added_lines)

            # check that the line has the correct function
            list_that_must_be_in_actual = ["CALL Button.push",
                                           "'kwargs': {'times_pressed': 3}",
                                           "'args': ()",
                                           "'return_value': 'Someone pushed the button 3 times'"]

            for str_to_find in list_that_must_be_in_actual:
                self.assertTrue(str_to_find in added_msg,
                                f'"{str_to_find}" was not found in "{added_msg}"')

        with self.subTest('positional_args'):
            expected_return_value_string = 'Someone pushed the button 3 times'

            length = []
            # noinspection PyUnusedLocal
            actual_added_lines = []
            with open('./logs/app_server.log', 'r') as f:
                lines = f.read().splitlines()
                length.append(len(lines))

            # noinspection PyTypeChecker
            actual_return_value_string = Button.push(3)
            self.assertEqual(expected_return_value_string, actual_return_value_string,
                             f'The returned string "{actual_return_value_string}" did not match \
                             "{expected_return_value_string}" when pushing button.')

            with open('./logs/app_server.log', 'r') as f:
                lines = f.read().splitlines()
                length.append(len(lines))
                actual_added_lines = lines[length[0]:]
                added_msg = '\n'.join(actual_added_lines)

            # check that the line has the correct function
            list_that_must_be_in_actual = ["CALL Button.push",
                                           "'args': (3,)",
                                           "'kwargs': {}",
                                           "'return_value': 'Someone pushed the button 3 times'"]

            for str_to_find in list_that_must_be_in_actual:
                self.assertTrue(str_to_find in added_msg,
                                f'"{str_to_find}" was not found in "{added_msg}"')

    def test_logged_class_method_on_levels(self):

        for level_name, level in global_logger.LogLevels.items():
            # noinspection PyMissingOrEmptyDocstring
            class A:
                # noinspection PyMethodParameters
                @logged_class_method(level=level)
                def push(cls, times_pressed=1) -> str:
                    tmp_str = f' {times_pressed} times' if times_pressed > 1 else ''
                    return f'Someone pushed the button{tmp_str}'

            with self.subTest(f'level: {level_name}'):

                global_logger._SINGLE_LINE_MODE = True

                expected_return_value_string = 'Someone pushed the button 3 times'

                length = []
                # noinspection PyUnusedLocal
                actual_added_lines = []
                with open('./logs/app_server.log', 'r') as f:
                    lines = f.read().splitlines()
                    length.append(len(lines))

                actual_return_value_string = A.push(times_pressed=3)
                self.assertEqual(expected_return_value_string, actual_return_value_string,
                                 f'The returned string "{actual_return_value_string}" did not match \
                                 "{expected_return_value_string}" when pushing button.')

                with open('./logs/app_server.log', 'r') as f:
                    lines = f.read().splitlines()
                    length.append(len(lines))
                    actual_added_lines = lines[length[0]:]
                    added_msg = '\n'.join(actual_added_lines)

                for line in actual_added_lines:
                    self.assertTrue(line.startswith(level_name), f'{line!r} does not start with {level_name!r}')

                # check that the line has the correct function
                list_that_must_be_in_actual = ["CALL A.push",
                                               "'kwargs': {'times_pressed': 3}",
                                               "'args': ()",
                                               "'return_value': 'Someone pushed the button 3 times'"]

                for str_to_find in list_that_must_be_in_actual:
                    self.assertTrue(str_to_find in added_msg,
                                    f'{str_to_find!r} was not found in {added_msg!r}')

    def test_logged_method(self):

        class Button:
            @logged_method
            def push(self, times_pressed=1) -> str:
                tmp_str = f' {times_pressed} times' if times_pressed > 1 else ''
                return f'Someone pushed the button{tmp_str}'

            def __repr__(self):
                return 'A simple button'

        with self.subTest('kwargs'):

            global_logger._SINGLE_LINE_MODE = True

            expected_return_value_string = 'Someone pushed the button 3 times'

            button = Button()
            length = []
            # noinspection PyUnusedLocal
            actual_added_lines = []
            with open('./logs/app_server.log', 'r') as f:
                lines = f.read().splitlines()
                length.append(len(lines))

            actual_return_value_string = button.push(times_pressed=3)
            self.assertEqual(expected_return_value_string, actual_return_value_string,
                             f'The returned string "{actual_return_value_string}" did not match \
                             "{expected_return_value_string}" when pushing button.')

            with open('./logs/app_server.log', 'r') as f:
                lines = f.read().splitlines()
                length.append(len(lines))
                actual_added_lines = lines[length[0]:]
                added_msg = '\n'.join(actual_added_lines)

            # check that the line has the correct function
            list_that_must_be_in_actual = ["CALL Button.push",
                                           "'kwargs': {'times_pressed': 3}",
                                           "'args': ()",
                                           "'return_value': 'Someone pushed the button 3 times'"]

            for str_to_find in list_that_must_be_in_actual:
                self.assertTrue(str_to_find in added_msg,
                                f'"{str_to_find}" was not found in "{added_msg}"')

        with self.subTest('positional_args'):
            expected_return_value_string = 'Someone pushed the button 3 times'

            button = Button()
            length = []
            # noinspection PyUnusedLocal
            actual_added_lines = []
            with open('./logs/app_server.log', 'r') as f:
                lines = f.read().splitlines()
                length.append(len(lines))

            actual_return_value_string = button.push(3)
            self.assertEqual(expected_return_value_string, actual_return_value_string,
                             f'The returned string "{actual_return_value_string}" did not match \
                             "{expected_return_value_string}" when pushing button.')

            with open('./logs/app_server.log', 'r') as f:
                lines = f.read().splitlines()
                length.append(len(lines))
                actual_added_lines = lines[length[0]:]
                added_msg = '\n'.join(actual_added_lines)

            # check that the line has the correct function
            list_that_must_be_in_actual = ["CALL Button.push",
                                           "'args': (3,)",
                                           "'kwargs': {}",
                                           "'return_value': 'Someone pushed the button 3 times'"]

            for str_to_find in list_that_must_be_in_actual:
                self.assertTrue(str_to_find in added_msg,
                                f'"{str_to_find}" was not found in "{added_msg}"')

    def test_logged_method_on_levels(self):

        for level_name, level in global_logger.LogLevels.items():
            class A:
                @logged_method(level=level)
                def push(self, times_pressed=1) -> str:
                    tmp_str = f' {times_pressed} times' if times_pressed > 1 else ''
                    return f'Someone pushed the button{tmp_str}'

            with self.subTest(f'level: {level_name}'):

                global_logger._SINGLE_LINE_MODE = True

                expected_return_value_string = 'Someone pushed the button 3 times'

                length = []
                # noinspection PyUnusedLocal
                actual_added_lines = []
                with open('./logs/app_server.log', 'r') as f:
                    lines = f.read().splitlines()
                    length.append(len(lines))

                actual_return_value_string = A().push(times_pressed=3)
                self.assertEqual(expected_return_value_string, actual_return_value_string,
                                 f'The returned string "{actual_return_value_string}" did not match \
                                 "{expected_return_value_string}" when pushing button.')

                with open('./logs/app_server.log', 'r') as f:
                    lines = f.read().splitlines()
                    length.append(len(lines))
                    actual_added_lines = lines[length[0]:]
                    added_msg = '\n'.join(actual_added_lines)

                for line in actual_added_lines:
                    self.assertTrue(line.startswith(level_name), f'{line!r} does not start with {level_name!r}')

                # check that the line has the correct function
                list_that_must_be_in_actual = ["CALL A.push",
                                               "'kwargs': {'times_pressed': 3}",
                                               "'args': ()",
                                               "'return_value': 'Someone pushed the button 3 times'"]

                for str_to_find in list_that_must_be_in_actual:
                    self.assertTrue(str_to_find in added_msg,
                                    f'{str_to_find!r} was not found in {added_msg!r}')

    def test_logged_function(self):

        @logged_function
        def push(times_pressed=1) -> str:
            tmp_str = f' {times_pressed} times' if times_pressed > 1 else ''
            return f'Someone pushed the button{tmp_str}'

        with self.subTest('kwargs'):

            global_logger._SINGLE_LINE_MODE = True

            expected_return_value_string = 'Someone pushed the button 3 times'

            length = []
            # noinspection PyUnusedLocal
            actual_added_lines = []
            with open('./logs/app_server.log', 'r') as f:
                lines = f.read().splitlines()
                length.append(len(lines))

            actual_return_value_string = push(times_pressed=3)
            self.assertEqual(expected_return_value_string, actual_return_value_string,
                             f'The returned string "{actual_return_value_string}" did not match \
                             "{expected_return_value_string}" when pushing button.')

            with open('./logs/app_server.log', 'r') as f:
                lines = f.read().splitlines()
                length.append(len(lines))
                actual_added_lines = lines[length[0]:]
                added_msg = '\n'.join(actual_added_lines)

            # check that the line has the correct function
            list_that_must_be_in_actual = ["CALL push",
                                           "'kwargs': {'times_pressed': 3}",
                                           "'args': ()",
                                           "'return_value': 'Someone pushed the button 3 times'"]

            for str_to_find in list_that_must_be_in_actual:
                self.assertTrue(str_to_find in added_msg,
                                f'"{str_to_find}" was not found in "{added_msg}"')

        with self.subTest('positional_args'):
            expected_return_value_string = 'Someone pushed the button 3 times'

            length = []
            # noinspection PyUnusedLocal
            actual_added_lines = []
            with open('./logs/app_server.log', 'r') as f:
                lines = f.read().splitlines()
                length.append(len(lines))

            actual_return_value_string = push(3)
            self.assertEqual(expected_return_value_string, actual_return_value_string,
                             f'The returned string "{actual_return_value_string}" did not match \
                             "{expected_return_value_string}" when pushing button.')

            with open('./logs/app_server.log', 'r') as f:
                lines = f.read().splitlines()
                length.append(len(lines))
                actual_added_lines = lines[length[0]:]
                added_msg = '\n'.join(actual_added_lines)

            # check that the line has the correct function
            list_that_must_be_in_actual = ["CALL push",
                                           "'args': (3,)",
                                           "'kwargs': {}",
                                           "'return_value': 'Someone pushed the button 3 times'"]

            for str_to_find in list_that_must_be_in_actual:
                self.assertTrue(str_to_find in added_msg,
                                f'"{str_to_find}" was not found in "{added_msg}"')

    def test_logged_function_on_levels(self):

        for level_name, level in global_logger.LogLevels.items():

            @logged_function(level=level)
            def push(times_pressed=1) -> str:
                tmp_str = f' {times_pressed} times' if times_pressed > 1 else ''
                return f'Someone pushed the button{tmp_str}'

            with self.subTest(f'level: {level_name}'):

                global_logger._SINGLE_LINE_MODE = True

                expected_return_value_string = 'Someone pushed the button 3 times'

                length = []
                # noinspection PyUnusedLocal
                actual_added_lines = []
                with open('./logs/app_server.log', 'r') as f:
                    lines = f.read().splitlines()
                    length.append(len(lines))

                actual_return_value_string = push(times_pressed=3)
                self.assertEqual(expected_return_value_string, actual_return_value_string,
                                 f'The returned string "{actual_return_value_string}" did not match \
                                 "{expected_return_value_string}" when pushing button.')

                with open('./logs/app_server.log', 'r') as f:
                    lines = f.read().splitlines()
                    length.append(len(lines))
                    actual_added_lines = lines[length[0]:]
                    added_msg = '\n'.join(actual_added_lines)

                for line in actual_added_lines:
                    self.assertTrue(line.startswith(level_name), f'{line!r} does not start with {level_name!r}')

                # check that the line has the correct function
                list_that_must_be_in_actual = ["CALL push",
                                               "'kwargs': {'times_pressed': 3}",
                                               "'args': ()",
                                               "'return_value': 'Someone pushed the button 3 times'"]

                for str_to_find in list_that_must_be_in_actual:
                    self.assertTrue(str_to_find in added_msg,
                                    f'{str_to_find!r} was not found in {added_msg!r}')


class TestDepreciated(EnhancedTestCase):
    def test_deprecated(self):

        @deprecated
        def push(times_pressed=1) -> str:
            tmp_str = f' {times_pressed} times' if times_pressed > 1 else ''
            return f'Someone pushed the button{tmp_str}'

        expected_return_value_string = 'Someone pushed the button 3 times'

        length = []
        # noinspection PyUnusedLocal
        actual_added_lines = []
        with open('./logs/app_server.log', 'r') as f:
            lines = f.read().splitlines()
            length.append(len(lines))

        actual_return_value_string = push(3)

        with open('./logs/app_server.log', 'r') as f:
            lines = f.read().splitlines()
            length.append(len(lines))
            actual_added_lines = lines[length[0]:]

        # make sure only one line was added
        self.assertEqual(1, length[1] - length[0], "The number of lines added was not 1")

        # check that the expected result was returned
        self.assertEqual(expected_return_value_string, actual_return_value_string,
                         f'The returned string "{actual_return_value_string}" did not match \
                         "{expected_return_value_string}" when pushing button.')

        # check that the expected content was logged
        list_that_must_be_in_actual = ['push is deprecated.']
        for str_to_find in list_that_must_be_in_actual:
            self.assertTrue(str_to_find in actual_added_lines[-1],
                            f'"{str_to_find}" was not found in "{actual_added_lines[-1]}"')

    def test_deprecated_with_alternatives(self):

        def push_a():
            ...

        def push_b():
            ...

        def push_c():
            ...

        class _TestData:
            def __init__(self, label, expected_str, alts):
                self.label = label
                self.expected_str = expected_str
                self.alts = alts

        data_list = [_TestData('push_a alt', 'push is deprecated, consider using push_a.', push_a),
                     _TestData('(push_a, push_b) alt', 'push is deprecated, consider using push_a or push_b.',
                               (push_a, push_b)),
                     _TestData('[push_a, push_b, push_c] alt', 'push is deprecated, consider using push_a, '
                                                               'push_b, or push_c.', [push_a, push_b, push_c])]
        for data in data_list:

            @self.inplace_subtest(data.label)
            def _():

                @deprecated(alternatives=data.alts)
                def push(times_pressed=1) -> str:
                    tmp_str = f' {times_pressed} times' if times_pressed > 1 else ''
                    return f'Someone pushed the button{tmp_str}'

                expected_return_value_string = 'Someone pushed the button 3 times'

                length = []
                # noinspection PyUnusedLocal
                actual_added_lines = []
                with open('./logs/app_server.log', 'r') as f:
                    lines = f.read().splitlines()
                    length.append(len(lines))

                actual_return_value_string = push(3)

                # check that the correct value was returned
                self.assertEqual(expected_return_value_string, actual_return_value_string,
                                 f'The returned string "{actual_return_value_string}" did not match \
                                 "{expected_return_value_string}" when pushing button.')

                with open('./logs/app_server.log', 'r') as f:
                    lines = f.read().splitlines()
                    length.append(len(lines))
                    actual_added_lines = lines[length[0]:]

                # make sure only one line was added
                self.assertEqual(1, length[1] - length[0])

                # check that the correct content was logged
                list_that_must_be_in_actual = [data.expected_str]
                for str_to_find in list_that_must_be_in_actual:
                    self.assertTrue(str_to_find in actual_added_lines[-1],
                                    f'"{str_to_find}" was not found in "{actual_added_lines[-1]}"')


if __name__ == '__main__':
    unittest.main()
