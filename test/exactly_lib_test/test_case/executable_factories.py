import pathlib
import unittest

from exactly_lib.appl_env import executable_factories as sut
from exactly_lib.type_system.logic.program.command import Command
from exactly_lib.type_system.logic.program.commands import CommandDriverForShell, \
    CommandDriverForSystemProgram, \
    CommandDriverForExecutableFile
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.type_val_deps.types.path.test_resources.described_path import new_primitive


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestExecutableFactoryForPosix),
        unittest.makeSuite(TestExecutableFactoryForWindows),
    ])


class TestExecutableFactoryForPosix(unittest.TestCase):
    factory = sut.ExecutableFactoryForPosix()

    def test_shell(self):
        # ARRANGE #
        command_line = 'command line'
        cases = [
            NIE('without arguments',
                expected_value=command_line,
                input_value=[],
                ),
            NIE('with arguments',
                expected_value=command_line + ' arg1 arg2',
                input_value=['arg1', 'arg2'],
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                command = Command(CommandDriverForShell(command_line),
                                  case.input_value)
                # ACT #
                actual = self.factory.make(command)
                # ASSERT #
                self.assertTrue(actual.is_shell)

                self.assertIsInstance(actual.arg_list_or_str, str)

                self.assertEqual(case.expected_value, actual.arg_list_or_str)

    def test_system_program(self):
        # ARRANGE #
        program_name = 'program_name'
        cases = [
            NIE('without arguments',
                expected_value=[program_name],
                input_value=[],
                ),
            NIE('with arguments',
                expected_value=[program_name, 'arg1', 'arg2'],
                input_value=['arg1', 'arg2'],
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                command = Command(CommandDriverForSystemProgram(program_name),
                                  case.input_value)
                # ACT #
                actual = self.factory.make(command)
                # ASSERT #
                self.assertFalse(actual.is_shell)

                self.assertIsInstance(actual.arg_list_or_str, list)

                self.assertEqual(case.expected_value, actual.arg_list_or_str)

    def test_executable_file(self):
        # ARRANGE #
        the_file = pathlib.Path('the dir') / 'the file'
        cases = [
            NIE('without arguments',
                expected_value=[str(the_file)],
                input_value=[],
                ),
            NIE('with arguments',
                expected_value=[str(the_file), 'arg1', 'arg2'],
                input_value=['arg1', 'arg2'],
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                command = Command(CommandDriverForExecutableFile(new_primitive(the_file)),
                                  case.input_value)
                # ACT #
                actual = self.factory.make(command)
                # ASSERT #
                self.assertFalse(actual.is_shell)

                self.assertIsInstance(actual.arg_list_or_str, list)

                self.assertEqual(case.expected_value, actual.arg_list_or_str)


class TestExecutableFactoryForWindows(unittest.TestCase):
    factory = sut.ExecutableFactoryForWindows()

    def test_shell(self):
        # ARRANGE #
        command_line = 'command line'
        cases = [
            NIE('without arguments',
                expected_value=command_line,
                input_value=[],
                ),
            NIE('with arguments',
                expected_value=command_line + ' arg1 arg2',
                input_value=['arg1', 'arg2'],
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                command = Command(CommandDriverForShell(command_line),
                                  case.input_value)
                # ACT #
                actual = self.factory.make(command)
                # ASSERT #
                self.assertTrue(actual.is_shell)

                self.assertIsInstance(actual.arg_list_or_str, str)

                self.assertEqual(case.expected_value, actual.arg_list_or_str)

    def test_system_program(self):
        # ARRANGE #
        program_name = 'program_name'
        cases = [
            NIE('without arguments',
                expected_value=[program_name],
                input_value=[],
                ),
            NIE('with arguments',
                expected_value=[program_name, 'arg1', 'arg2'],
                input_value=['arg1', 'arg2'],
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                command = Command(CommandDriverForSystemProgram(program_name),
                                  case.input_value)
                # ACT #
                actual = self.factory.make(command)
                # ASSERT #
                self.assertFalse(actual.is_shell)

                self.assertIsInstance(actual.arg_list_or_str, list)

                self.assertEqual(case.expected_value, actual.arg_list_or_str)

    def test_executable_file(self):
        # ARRANGE #
        the_file = pathlib.Path('the dir') / 'the file'
        cases = [
            NIE('without arguments',
                expected_value=[str(the_file)],
                input_value=[],
                ),
            NIE('with arguments',
                expected_value=[str(the_file), 'arg1', 'arg2'],
                input_value=['arg1', 'arg2'],
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                command = Command(CommandDriverForExecutableFile(new_primitive(the_file)),
                                  case.input_value)
                # ACT #
                actual = self.factory.make(command)
                # ASSERT #
                self.assertFalse(actual.is_shell)

                self.assertIsInstance(actual.arg_list_or_str, list)

                self.assertEqual(case.expected_value, actual.arg_list_or_str)
