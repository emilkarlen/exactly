import sys
import unittest


def interpreter_that_executes_argument() -> str:
    return '{} -c'.format(sys.executable)


def command_line_for_executing_program_via_command_line(command_argument: str,
                                                        args_directly_after_interpreter: str = '') -> str:
    return '"{}" {} -c "{}"'.format(sys.executable,
                                    args_directly_after_interpreter,
                                    command_argument)


def command_line_for_interpreting(python_source_file,
                                  arguments: iter = ()) -> str:
    str_arguments = _str_elements(arguments)
    arguments_string = '' if not str_arguments else ' ' + ' '.join(str_arguments)
    return '"{}" "{}"{}'.format(sys.executable,
                                python_source_file,
                                arguments_string)


def shell_command_line_for_interpreting(python_source_file,
                                        arguments: iter = ()) -> str:
    """Introduced for Windows port. May be removed."""
    str_arguments = _str_elements(arguments)
    arguments_string = '' if not str_arguments else ' ' + ' '.join(str_arguments)
    return '"{}" {}{}'.format(sys.executable, python_source_file, arguments_string)


def command_line_for_arguments(arguments: iter) -> str:
    str_arguments = _str_elements(arguments)
    arguments_string = '' if not str_arguments else ' ' + ' '.join(str_arguments)
    return '"{}"{}'.format(sys.executable, arguments_string)


def args_for_interpreting(python_source_file,
                          arguments: iter = ()) -> list:
    return [sys.executable, str(python_source_file)] + _str_elements(arguments)


def args_for_running_with_arguments(arguments: list) -> list:
    return [sys.executable] + _str_elements(arguments)


def assert_interpreter_is_available(puc: unittest.TestCase):
    if not sys.executable:
        puc.fail('Cannot execute test since the name of the Python 3 interpreter is not found in sys.executable.')


def abs_path_to_interpreter_quoted_for_exactly() -> str:
    return '"' + sys.executable + '"'


def abs_path_to_interpreter() -> str:
    return sys.executable


def _str_elements(elements: iter) -> list:
    return [str(x) for x in elements]
