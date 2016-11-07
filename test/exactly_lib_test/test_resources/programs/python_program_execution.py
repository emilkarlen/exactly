import os
import pathlib
import sys
import unittest

from exactly_lib_test.test_resources.files.executable_files import make_executable_by_os


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


def non_shell_args_for_that_executes_source_on_command_line(python_source: str) -> list:
    return [sys.executable, '-c', python_source]


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


def write_executable_file_with_python_source(executable_file_name_for_invokation_at_command_line: pathlib.Path,
                                             python_source_code: str = ''):
    if sys.platform == 'win32':
        _write_windows_python_executable(executable_file_name_for_invokation_at_command_line, python_source_code)
    else:
        _write_unix_python_executable(executable_file_name_for_invokation_at_command_line, python_source_code)


def _write_unix_python_executable(executable_file_name_for_invokation_at_command_line: pathlib.Path,
                                  python_source_code: str = ''):
    with open(str(executable_file_name_for_invokation_at_command_line), 'w') as f:
        f.write(_unix_interpreter_specification())
        f.write(python_source_code)
    make_executable_by_os(executable_file_name_for_invokation_at_command_line)


def _write_windows_python_executable(executable_file_name_for_invokation_at_command_line: pathlib.Path,
                                     python_source_code: str = ''):
    raise NotImplementedError("Not implemented ")


def _unix_interpreter_specification() -> str:
    return '#! ' + sys.executable + os.linesep
