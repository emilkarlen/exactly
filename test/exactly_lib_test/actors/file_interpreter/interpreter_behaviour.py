import unittest

from exactly_lib.actors import file_interpreter as sut
from exactly_lib.test_case.actor import ParseException
from exactly_lib.test_case_file_structure.path_relativity import RelHdsOptionType
from exactly_lib.test_case_utils.os_services import os_services_access
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.actors.file_interpreter.configuration import TheConfigurationBase, \
    COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE
from exactly_lib_test.actors.test_resources import integration_check
from exactly_lib_test.actors.test_resources import \
    test_validation_for_single_file_rel_hds_act as single_file_rel_home
from exactly_lib_test.actors.test_resources.action_to_check import suite_for_execution
from exactly_lib_test.actors.test_resources.integration_check import PostSdsExpectation
from exactly_lib_test.execution.test_resources import eh_assertions
from exactly_lib_test.instructions.configuration.actor.test_resources import ExecutedCommandAssertion
from exactly_lib_test.symbol.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorThatRecordsArguments
from exactly_lib_test.test_case_file_structure.test_resources.hds_populators import contents_in
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.value_assertions import file_assertions as asrt_path
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources import command_assertions as asrt_command
from exactly_lib_test.util.test_resources.py_program import \
    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes, surrounded_by_soft_quotes


class TheConfiguration(TheConfigurationBase):
    def __init__(self):
        super().__init__(ACTOR_THAT_RUNS_PYTHON_PROGRAM_FILE)


def suite() -> unittest.TestSuite:
    tests = []
    the_configuration = TheConfiguration()

    tests.append(suite_for(the_configuration))
    tests.append(suite_for_execution(the_configuration))

    return unittest.TestSuite(tests)


def suite_for(configuration: TheConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        single_file_rel_home.suite_for(configuration),
        TestFailWhenThereAreArgumentsButTheyAreInvalidlyQuoted(),
        TestFileReferenceCanBeQuoted(),
        TestArgumentsAreParsedAndPassedToExecutor(),
        unittest.makeSuite(TestSymbolUsages),
    ])


class TestFailWhenThereAreArgumentsButTheyAreInvalidlyQuoted(unittest.TestCase):
    def runTest(self):
        act_phase_instructions = [instr(["""valid-file-ref 'quoting missing ending single-quote"""]),
                                  instr([''])]
        with self.assertRaises(ParseException):
            ACTOR_THAT_RUNS_PYTHON_PROGRAM_FILE.parse(act_phase_instructions)


class TestFileReferenceCanBeQuoted(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        expected_file_name = 'quoted file name.src'
        act_phase_instructions = [instr([str(surrounded_by_hard_quotes(expected_file_name))]),
                                  instr([''])]
        executor_that_records_arguments = CommandExecutorThatRecordsArguments()
        arrangement = integration_check.Arrangement(
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT, DirContents([
                File.empty(expected_file_name)])),
            process_execution=ProcessExecutionArrangement(
                os_services=os_services_access.new_for_cmd_exe(executor_that_records_arguments)
            )
        )
        expectation = integration_check.Expectation()
        # ACT #
        integration_check.check_execution(self,
                                          ACTOR_THAT_RUNS_PYTHON_PROGRAM_FILE,
                                          act_phase_instructions,
                                          arrangement, expectation)
        # ASSERT #
        expected_command = asrt_command.matches_command(
            driver=asrt_command.matches_executable_file_command_driver(asrt.anything_goes()),
            arguments=asrt.matches_sequence([
                asrt_path.str_as_path(asrt_path.name_equals(expected_file_name))
            ])
        )
        expected_command.apply_with_message(
            self,
            executor_that_records_arguments.command,
            'command',
        )


class TestArgumentsAreParsedAndPassedToExecutor(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        atc_file_name = 'existing-file.py'
        arg_1 = 'un-quoted'
        arg_2 = 'single quoted'
        arg_3 = 'double quoted'
        act_line_1 = '{} {} {} {}'.format(
            atc_file_name,
            arg_1,
            surrounded_by_hard_quotes(arg_2),
            surrounded_by_soft_quotes(arg_3),
        )
        atc_line_2 = ''
        act_phase_instructions = [instr([act_line_1]),
                                  instr([atc_line_2])]
        executor_that_records_arguments = CommandExecutorThatRecordsArguments()
        arrangement = integration_check.Arrangement(
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT, DirContents([
                File.empty(atc_file_name)])),
            process_execution=ProcessExecutionArrangement(
                os_services=os_services_access.new_for_cmd_exe(executor_that_records_arguments)
            )
        )
        expected_command = asrt_command.matches_command(
            driver=asrt_command.matches_executable_file_command_driver(asrt.anything_goes()),
            arguments=asrt.matches_sequence([
                asrt_path.str_as_path(asrt_path.name_equals(atc_file_name)),
                asrt.equals(arg_1),
                asrt.equals(arg_2),
                asrt.equals(arg_3),
            ])
        )
        expectation = integration_check.Expectation(
            after_execution=ExecutedCommandAssertion(executor_that_records_arguments,
                                                     lambda tcds: expected_command)
        )
        # ACT & ASSERT #
        integration_check.check_execution(self,
                                          ACTOR_THAT_RUNS_PYTHON_PROGRAM_FILE,
                                          act_phase_instructions,
                                          arrangement,
                                          expectation)


class TestSymbolUsages(unittest.TestCase):
    def test_symbol_value_with_space_SHOULD_be_given_as_single_argument_to_program(self):
        symbol = StringConstantSymbolContext('symbol_name', 'symbol value with space')

        expected_output = lines_content([symbol.str_value])

        source_file = 'the-source-file.py'

        command_line = '{source_file} {symbol}'.format(
            source_file=source_file,
            symbol=symbol.name__sym_ref_syntax,
        )

        arrangement = integration_check.Arrangement(
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT, fs.DirContents([
                fs.File(
                    source_file,
                    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
            ])),
            symbol_table=symbol.symbol_table
        )

        expectation = integration_check.Expectation(
            symbol_usages=asrt.matches_sequence(
                [symbol.reference_assertion__any_data_type]
            ),
            execute=eh_assertions.is_exit_code(0),
            post_sds=PostSdsExpectation.constant(
                sub_process_result_from_execute=asrt_pr.stdout(asrt.Equals(expected_output,
                                                                           'CLI arguments, one per line'))
            ),
        )
        integration_check.check_execution(self,
                                          ACTOR_THAT_RUNS_PYTHON_PROGRAM_FILE,
                                          [instr([command_line])],
                                          arrangement,
                                          expectation)


ACTOR_THAT_RUNS_PYTHON_PROGRAM_FILE = sut.actor(COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
