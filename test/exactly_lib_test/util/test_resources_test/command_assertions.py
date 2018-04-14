import pathlib
import unittest

from exactly_lib.util.process_execution.commands import ExecutableFileCommand, executable_program_command, \
    executable_file_command, shell_command
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.util.test_resources import command_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestExecutableFile),
        unittest.makeSuite(TestExecutableProgram),
        unittest.makeSuite(TestShell),
    ])


class TestExecutableFile(unittest.TestCase):
    def test_equals(self):
        path = pathlib.Path('here')
        cases = [
            NEA('without arguments',
                expected=
                ExecutableFileCommand(path,
                                      []),
                actual=
                ExecutableFileCommand(path,
                                      []),
                ),
            NEA('with arguments',
                expected=
                ExecutableFileCommand(path,
                                      ['arg']),
                actual=
                ExecutableFileCommand(path,
                                      ['arg']),
                ),
        ]
        for case in cases:
            assertion = sut.equals_executable_file_command(case.expected)
            with self.subTest(case.name):
                assertion.apply_without_message(self, case.actual)

    def test_not_equals(self):
        path = pathlib.Path('here')
        cases = [
            NEA('unexpected path',
                expected=
                ExecutableFileCommand(path,
                                      []),
                actual=
                ExecutableFileCommand(path / 'unexpected',
                                      []),
                ),
            NEA('unexpected arguments',
                expected=
                ExecutableFileCommand(path,
                                      ['expected']),
                actual=
                ExecutableFileCommand(path,
                                      ['expected', 'unexpected']),
                ),
            NEA('unexpected command type',
                expected=
                ExecutableFileCommand(path,
                                      ['expected']),
                actual=
                executable_program_command(path.name,
                                           ['expected']),
                ),
        ]
        for case in cases:
            assertion = sut.equals_executable_file_command(case.expected)
            with self.subTest(case.name):
                assert_that_assertion_fails(assertion, case.actual)


class TestExecutableProgram(unittest.TestCase):
    def test_equals(self):
        cases = [
            NEA('without arguments',
                expected=
                executable_program_command('expected program',
                                           []),
                actual=
                executable_program_command('expected program',
                                           []),
                ),
            NEA('without arguments',
                expected=
                executable_program_command('expected program',
                                           ['expected arg']),
                actual=
                executable_program_command('expected program',
                                           ['expected arg']),
                ),
        ]
        for case in cases:
            assertion = sut.equals_executable_program_command(case.expected)
            with self.subTest(case.name):
                assertion.apply_without_message(self, case.actual)

    def test_not_equals(self):
        cases = [
            NEA('unexpected program',
                expected=
                executable_program_command('expected program',
                                           []),
                actual=
                executable_program_command('actual program',
                                           []),
                ),
            NEA('unexpected arguments',
                expected=
                executable_program_command('expected program',
                                           ['expected arg']),
                actual=
                executable_program_command('expected program',
                                           ['actual arg']),
                ),
            NEA('unexpected number of arguments',
                expected=
                executable_program_command('expected program',
                                           ['', '']),
                actual=
                executable_program_command('expected program',
                                           ['']),
                ),
            NEA('unexpected command type',
                expected=
                executable_program_command('expected',
                                           []),
                actual=
                executable_file_command(pathlib.Path('expected'),
                                        []),
                ),
        ]
        for case in cases:
            assertion = sut.equals_executable_program_command(case.expected)
            with self.subTest(case.name):
                assert_that_assertion_fails(assertion, case.actual)


class TestShell(unittest.TestCase):
    def test_equals(self):
        cases = [
            NEA('single string',
                expected=
                shell_command('expected'),
                actual=
                shell_command('expected'),
                ),
            NEA('multiple strings',
                expected=
                shell_command('expected arg'),
                actual=
                shell_command('expected arg'),
                ),
        ]
        for case in cases:
            assertion = sut.equals_shell_command(case.expected)
            with self.subTest(case.name):
                assertion.apply_without_message(self, case.actual)

    def test_not_equals(self):
        cases = [
            NEA('unexpected command string',
                expected=
                shell_command('expected'),
                actual=
                shell_command('actual'),
                ),
            NEA('unexpected command type',
                expected=
                shell_command('expected'),
                actual=
                executable_program_command('expected', []),
                ),
        ]
        for case in cases:
            assertion = sut.equals_shell_command(case.expected)
            with self.subTest(case.name):
                assert_that_assertion_fails(assertion, case.actual)
