import pathlib
import unittest

from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.type_system.logic.program.process_execution.commands import CommandDriverForSystemProgram, \
    CommandDriverForExecutableFile, \
    CommandDriverForShell
from exactly_lib_test.type_system.logic.test_resources import command_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.data.test_resources.described_path import new_primitive


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestExecutableFileDriver),
        unittest.makeSuite(TestSystemProgramDriver),
        unittest.makeSuite(TestShellDriver),
        unittest.makeSuite(TestCommand),
        unittest.makeSuite(TestExecutableFile),
        unittest.makeSuite(TestSystemProgram),
        unittest.makeSuite(TestShell),
    ])


class TestExecutableFileDriver(unittest.TestCase):
    def test_equals(self):
        path = pathlib.Path('here')
        cases = [
            NEA('without arguments',
                expected=
                CommandDriverForExecutableFile(new_primitive(path)),
                actual=
                CommandDriverForExecutableFile(new_primitive(path)),
                ),
        ]
        for case in cases:
            assertion = sut.equals_executable_file_command_driver(case.expected)
            with self.subTest(case.name):
                assertion.apply_without_message(self, case.actual)

    def test_not_equals(self):
        path = pathlib.Path('here')
        cases = [
            NEA('unexpected path',
                expected=
                CommandDriverForExecutableFile(new_primitive(path)),
                actual=
                CommandDriverForExecutableFile(new_primitive(path / 'unexpected')),
                ),
            NEA('unexpected command type',
                expected=
                CommandDriverForExecutableFile(new_primitive(path)),
                actual=
                CommandDriverForSystemProgram(path.name),
                ),
        ]
        for case in cases:
            assertion = sut.equals_executable_file_command_driver(case.expected)
            with self.subTest(case.name):
                assert_that_assertion_fails(assertion, case.actual)


class TestSystemProgramDriver(unittest.TestCase):
    def test_equals(self):
        cases = [
            NEA('without arguments',
                expected=
                CommandDriverForSystemProgram('expected program'),
                actual=
                CommandDriverForSystemProgram('expected program'),
                ),
        ]
        for case in cases:
            assertion = sut.equals_system_program_command_driver(case.expected)
            with self.subTest(case.name):
                assertion.apply_without_message(self, case.actual)

    def test_not_equals(self):
        cases = [
            NEA('unexpected program',
                expected=
                CommandDriverForSystemProgram('expected program'),
                actual=
                CommandDriverForSystemProgram('actual program'),
                ),
            NEA('unexpected command type',
                expected=
                CommandDriverForSystemProgram('expected'),
                actual=
                CommandDriverForExecutableFile(new_primitive(pathlib.Path('expected'))),
                ),
        ]
        for case in cases:
            assertion = sut.equals_system_program_command_driver(case.expected)
            with self.subTest(case.name):
                assert_that_assertion_fails(assertion, case.actual)


class TestShellDriver(unittest.TestCase):
    def test_equals(self):
        cases = [
            NEA('single string',
                expected=
                CommandDriverForShell('expected'),
                actual=
                CommandDriverForShell('expected'),
                ),
        ]
        for case in cases:
            assertion = sut.equals_shell_command_driver(case.expected)
            with self.subTest(case.name):
                assertion.apply_without_message(self, case.actual)

    def test_not_equals(self):
        cases = [
            NEA('unexpected command string',
                expected=
                CommandDriverForShell('expected'),
                actual=
                CommandDriverForShell('actual'),
                ),
            NEA('unexpected command type',
                expected=
                CommandDriverForShell('expected'),
                actual=
                CommandDriverForSystemProgram('expected'),
                ),
        ]
        for case in cases:
            assertion = sut.equals_shell_command_driver(case.expected)
            with self.subTest(case.name):
                assert_that_assertion_fails(assertion, case.actual)


class TestCommand(unittest.TestCase):
    def test_equals(self):
        cases = [
            NEA('shell',
                expected=
                sut.matches_command(sut.equals_shell_command_driver(CommandDriverForShell('command line')),
                                    asrt.equals(['arg'])),
                actual=
                Command(CommandDriverForShell('command line'), ['arg']),
                ),
            NEA('without arguments',
                expected=
                sut.matches_command(sut.equals_system_program_command_driver(CommandDriverForSystemProgram('program')),
                                    asrt.equals([])),
                actual=
                Command(CommandDriverForSystemProgram('program'),
                        []),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_equals(self):
        cases = [
            NEA('unexpected driver type',
                expected=
                sut.matches_command(sut.equals_shell_command_driver(CommandDriverForShell('command')),
                                    asrt.equals(['arg'])),
                actual=
                Command(CommandDriverForSystemProgram('command'), ['arg']),
                ),
            NEA('unexpected driver data',
                expected=
                sut.matches_command(
                    sut.equals_system_program_command_driver(CommandDriverForSystemProgram('expected')),
                    asrt.equals([])),
                actual=
                Command(CommandDriverForSystemProgram('unexpected'), []),
                ),
            NEA('unexpected argument',
                expected=
                sut.matches_command(sut.equals_system_program_command_driver(CommandDriverForSystemProgram('command')),
                                    asrt.equals(['expected'])),
                actual=
                Command(CommandDriverForSystemProgram('command'), ['expected', 'unexpected']),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestExecutableFile(unittest.TestCase):
    def test_equals(self):
        cases = [
            NEA('',
                expected=
                sut.equals_executable_file_command(new_primitive(pathlib.Path('expected')),
                                                   ['arg']),
                actual=
                Command(CommandDriverForExecutableFile(new_primitive(pathlib.Path('expected'))),
                        ['arg']),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_equals(self):
        cases = [
            NEA('unexpected file',
                expected=
                sut.equals_executable_file_command(new_primitive(pathlib.Path('expected')),
                                                   []),
                actual=
                Command(CommandDriverForExecutableFile(new_primitive(pathlib.Path('unExpected'))), []),
                ),
            NEA('unexpected driver type',
                expected=
                sut.equals_executable_file_command(new_primitive(pathlib.Path('expected')), []),
                actual=
                Command(CommandDriverForSystemProgram('expected'), []),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestSystemProgram(unittest.TestCase):
    def test_equals(self):
        cases = [
            NEA('',
                expected=
                sut.equals_system_program_command('expected', ['arg']),
                actual=
                Command(CommandDriverForSystemProgram('expected'), ['arg']),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_equals(self):
        cases = [
            NEA('unexpected programn',
                expected=
                sut.equals_system_program_command('expected', []),
                actual=
                Command(CommandDriverForSystemProgram('unExpected'), []),
                ),
            NEA('unexpected driver type',
                expected=
                sut.equals_system_program_command('expected', []),
                actual=
                Command(CommandDriverForExecutableFile(new_primitive(pathlib.Path('expected'))), []),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestShell(unittest.TestCase):
    def test_equals(self):
        cases = [
            NEA('',
                expected=
                sut.equals_shell_command('expected', ['arg']),
                actual=
                Command(CommandDriverForShell('expected'), ['arg']),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_equals(self):
        cases = [
            NEA('unexpected command line',
                expected=
                sut.equals_shell_command('expected', []),
                actual=
                Command(CommandDriverForShell('unExpected'), []),
                ),
            NEA('unexpected driver type',
                expected=
                sut.equals_shell_command('expected', []),
                actual=
                Command(CommandDriverForSystemProgram('expected'), []),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)
