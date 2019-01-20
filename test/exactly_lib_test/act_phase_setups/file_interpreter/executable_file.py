import sys
import unittest

import pathlib

from exactly_lib.act_phase_setups import file_interpreter as sut
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.actor import ParseException
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType
from exactly_lib.util.process_execution.commands import executable_file_command
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.act_phase_setups.file_interpreter import common_tests
from exactly_lib_test.act_phase_setups.file_interpreter.configuration import TheConfigurationBase
from exactly_lib_test.act_phase_setups.test_resources import act_phase_execution
from exactly_lib_test.act_phase_setups.test_resources import \
    test_validation_for_single_file_rel_home_act as single_file_rel_home
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import Configuration, \
    suite_for_execution
from exactly_lib_test.act_phase_setups.test_resources.test_validation_for_single_line_source import \
    TestCaseForConfigurationForValidation
from exactly_lib_test.execution.test_resources import eh_assertions
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils as su
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case.actor.test_resources.act_phase_os_process_executor import \
    ActPhaseOsProcessExecutorThatRecordsArguments
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case_file_structure.test_resources.home_populators import contents_in
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.py_program import \
    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES

COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE = executable_file_command(sys.executable, [])


class TheConfiguration(TheConfigurationBase):
    def __init__(self):
        super().__init__(sut.parser(COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE))


def suite() -> unittest.TestSuite:
    tests = []
    the_configuration = TheConfiguration()

    tests.append(suite_for(the_configuration))
    tests.append(suite_for_execution(the_configuration))

    tests.append(common_tests.suite_for(COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE))

    return unittest.TestSuite(tests)


def suite_for(configuration: TheConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        single_file_rel_home.suite_for(configuration),
        custom_suite_for(configuration),
        other_custom_suite(),
    ])


def other_custom_suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestSymbolUsages)


def custom_suite_for(conf: TheConfiguration) -> unittest.TestSuite:
    test_cases = [
        TestFailWhenThereAreArgumentsButTheyAreInvalidlyQuoted,
        TestFileReferenceCanBeQuoted,
        TestArgumentsAreParsedAndPassedToExecutor,
    ]
    return unittest.TestSuite([tc(conf) for tc in test_cases])


class TestFailWhenThereAreArgumentsButTheyAreInvalidlyQuoted(TestCaseForConfigurationForValidation):
    def runTest(self):
        act_phase_instructions = [instr(["""valid-file-ref 'quoting missing ending single-quote"""]),
                                  instr([''])]
        with self.assertRaises(ParseException):
            self._do_parse(act_phase_instructions)


class TestFileReferenceCanBeQuoted(unittest.TestCase):
    def __init__(self, configuration: Configuration):
        super().__init__()
        self.configuration = configuration

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.configuration))

    def runTest(self):
        act_phase_instructions = [instr(["""'quoted file name.src'"""]),
                                  instr([''])]
        executor_that_records_arguments = ActPhaseOsProcessExecutorThatRecordsArguments()
        arrangement = act_phase_execution.Arrangement(
            hds_contents=contents_in(RelHomeOptionType.REL_HOME_ACT, DirContents([
                empty_file('quoted file name.src')])),
            act_phase_process_executor=executor_that_records_arguments)
        expectation = act_phase_execution.Expectation()
        act_phase_execution.check_execution(self,
                                            self.configuration.sut,
                                            act_phase_instructions,
                                            arrangement, expectation)
        self.assertFalse(executor_that_records_arguments.command.shell,
                         'Should not be executed as a shell command')
        self.assertEqual(2,
                         len(executor_that_records_arguments.command.args),
                         'Number of command-and-arguments, including interpreter')


class TestArgumentsAreParsedAndPassedToExecutor(unittest.TestCase):
    def __init__(self, configuration: Configuration):
        super().__init__()
        self.configuration = configuration

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.configuration))

    def runTest(self):
        act_phase_instructions = [instr(["""existing-file.src un-quoted 'single quoted' "double quoted" """]),
                                  instr([''])]
        executor_that_records_arguments = ActPhaseOsProcessExecutorThatRecordsArguments()
        arrangement = act_phase_execution.Arrangement(
            hds_contents=contents_in(RelHomeOptionType.REL_HOME_ACT, DirContents([
                empty_file('existing-file.src')])),
            act_phase_process_executor=executor_that_records_arguments)
        expectation = act_phase_execution.Expectation()
        act_phase_execution.check_execution(self,
                                            self.configuration.sut,
                                            act_phase_instructions,
                                            arrangement, expectation)
        self.assertFalse(executor_that_records_arguments.command.shell,
                         'Should not be executed as a shell command')
        self.assertEqual(5,
                         len(executor_that_records_arguments.command.args),
                         'Number of command-and-arguments, including interpreter')
        self.assertListEqual(['un-quoted', 'single quoted', 'double quoted'],
                             executor_that_records_arguments.command.args[2:])


class TestSymbolUsages(unittest.TestCase):
    def test_symbol_value_with_space_SHOULD_be_given_as_single_argument_to_program(self):
        symbol = NameAndValue('symbol_name', 'symbol value with space')

        expected_output = lines_content([symbol.value])

        source_file = 'the-source-file.py'

        command_line = '{source_file} {symbol}'.format(
            source_file=source_file,
            symbol=symbol_reference_syntax_for_name(symbol.name),
        )

        arrangement = act_phase_execution.Arrangement(
            hds_contents=contents_in(RelHomeOptionType.REL_HOME_ACT, fs.DirContents([
                fs.File(
                    source_file,
                    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
            ])),
            symbol_table=SymbolTable({
                symbol.name:
                    su.string_constant_container(symbol.value),
            })
        )

        expectation = act_phase_execution.Expectation(
            result_of_execute=eh_assertions.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                  'CLI arguments, one per line')),
            symbol_usages=equals_symbol_references(
                [SymbolReference(symbol.name,
                                 is_any_data_type())]
            )
        )
        act_phase_execution.check_execution(self,
                                            sut.parser(COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE),
                                            [instr([command_line])],
                                            arrangement,
                                            expectation)


def _instructions_for_file_in_home_dir(home_dir_path: pathlib.Path, statements: list) -> list:
    with open(str(home_dir_path / 'sut.py'), 'w') as f:
        f.write(lines_content(statements))
    return [instr(['sut.py'])]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
