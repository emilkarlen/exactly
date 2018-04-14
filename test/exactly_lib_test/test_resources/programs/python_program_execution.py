import os
import pathlib
import sys
import unittest
from typing import List

from exactly_lib.util.process_execution.execution_elements import ProgramAndArguments
from exactly_lib_test.test_resources import string_formatting
from exactly_lib_test.test_resources.files.executable_files import make_executable_by_os

PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE = '-c'


def args_for_executing_source_on_command_line(source_str: str) -> List[str]:
    return [sys.executable,
            PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE,
            source_str]


def interpreter_that_executes_argument() -> str:
    return ' '.join([sys.executable,
                     PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE])


def command_line_for_executing_program_via_command_line(command_argument: str,
                                                        args_directly_after_interpreter: str = '') -> str:
    return '"{}" {} {} "{}"'.format(sys.executable,
                                    args_directly_after_interpreter,
                                    PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE,
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


def args_for_interpreting2(python_source_file,
                           arguments: iter = ()) -> ProgramAndArguments:
    return ProgramAndArguments(sys.executable,
                               [str(python_source_file)] + _str_elements(arguments))


def non_shell_args_for_that_executes_source_on_command_line(python_source: str) -> list:
    return [sys.executable, PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE, python_source]


def args_for_running_with_arguments(arguments: list) -> list:
    return [sys.executable] + _str_elements(arguments)


def assert_interpreter_is_available(puc: unittest.TestCase):
    if not sys.executable:
        puc.fail('Cannot execute test since the name of the Python 3 interpreter is not found in sys.executable.')


def abs_path_to_interpreter_quoted_for_exactly() -> str:
    return string_formatting.file_name(sys.executable)


def abs_path_to_interpreter() -> str:
    return sys.executable


def file_name_of_interpreter() -> str:
    return pathlib.Path(sys.executable).name


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
