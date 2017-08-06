import os
import unittest
from contextlib import contextmanager

from exactly_lib.act_phase_setups import command_line as sut
from exactly_lib.processing.parse.act_phase_source_parser import SourceCodeInstruction
from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.symbol.restrictions.reference_restrictions import no_restrictions
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.act_phase_handling import ParseException
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_utils.parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.line_source import LineSequence
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.act_phase_setups.command_line.test_resources import shell_command_source_line_for
from exactly_lib_test.act_phase_setups.test_resources import \
    test_validation_for_single_line_source as single_line_source
from exactly_lib_test.act_phase_setups.test_resources.act_phase_execution import \
    check_execution, Arrangement, Expectation
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import Configuration, \
    suite_for_execution, TestCaseSourceSetup
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case_file_structure.test_resources.paths import dummy_hds
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.programs import shell_commands
from exactly_lib_test.test_resources.programs.python_program_execution import abs_path_to_interpreter_quoted_for_exactly
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    configuration = TheConfiguration()
    ret_val.addTest(single_line_source.suite_for(configuration))
    ret_val.addTest(unittest.makeSuite(TestParsingAndValidation))
    ret_val.addTest(unittest.makeSuite(TestSymbolReferences))
    ret_val.addTest(suite_for_execution(configuration))
    return ret_val


class TestParsingAndValidation(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.constructor = sut.Constructor()
        self.hds = dummy_hds()
        self.pre_sds_env = InstructionEnvironmentForPreSdsStep(self.hds, dict(os.environ))

    def test_fails_when_command_is_empty(self):
        act_phase_instructions = [instr([shell_command_source_line_for(''), ])]
        with self.assertRaises(ParseException):
            self._do_parse(act_phase_instructions)

    def test_fails_when_command_is_only_space(self):
        act_phase_instructions = [instr([shell_command_source_line_for('    '), ])]
        with self.assertRaises(ParseException):
            self._do_parse(act_phase_instructions)

    def test_succeeds_when_there_is_exactly_one_statement_but_surrounded_by_empty_and_comment_lines(self):
        existing_file = abs_path_to_interpreter_quoted_for_exactly()
        act_phase_instructions = [instr(['',
                                         '             ',
                                         LINE_COMMENT_MARKER + ' line comment text',
                                         shell_command_source_line_for(existing_file),
                                         LINE_COMMENT_MARKER + ' line comment text',
                                         ''])]
        actual = self._do_parse_and_validate(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      actual.status,
                      'Validation result')

    def _do_parse(self, act_phase_instructions: list):
        executor = self.constructor.apply(ACT_PHASE_OS_PROCESS_EXECUTOR, self.pre_sds_env, act_phase_instructions)
        executor.parse(self.pre_sds_env)

    def _do_parse_and_validate(self, act_phase_instructions: list) -> svh.SuccessOrValidationErrorOrHardError:
        executor = self.constructor.apply(ACT_PHASE_OS_PROCESS_EXECUTOR, self.pre_sds_env, act_phase_instructions)
        executor.parse(self.pre_sds_env)
        return executor.validate_pre_sds(self.pre_sds_env)


class TestSymbolReferences(unittest.TestCase):
    def test_symbol_reference_on_command_line_SHOULD_be_reported_and_used_in_execution(self):
        symbol = NameAndValue('symbol_name', 'symbol value')

        string_to_print_template = 'constant and {symbol}'
        expected_output_template = string_to_print_template + '\n'

        shell_source_line = shell_commands.command_that_prints_to_stdout(
            string_to_print_template.format(symbol=symbol_reference_syntax_for_name(symbol.name))
        )
        act_phase_instructions = [instr([shell_command_source_line_for(shell_source_line)])]

        expected_symbol_references = [
            SymbolReference(symbol.name, no_restrictions()),
        ]

        check_execution(
            self,
            sut.Constructor(),
            act_phase_instructions,
            Arrangement(
                symbol_table=SymbolTable({
                    symbol.name: symbol_utils.string_value_constant_container(symbol.value)
                })
            ),
            Expectation(
                symbol_usages=equals_symbol_references(expected_symbol_references),
                sub_process_result_from_execute=
                pr.stdout(asrt.equals(expected_output_template.format(symbol=symbol.value)))
            ),
        )


class TheConfiguration(Configuration):
    def __init__(self):
        super().__init__(sut.Constructor())

    @contextmanager
    def program_that_copes_stdin_to_stdout(self, hds: HomeDirectoryStructure) -> list:
        yield self._instruction_for(shell_commands.command_that_copes_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self,
                                      hds: HomeDirectoryStructure,
                                      string_to_print: str) -> list:
        yield self._instruction_for(shell_commands.command_that_prints_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self,
                                      hds: HomeDirectoryStructure,
                                      string_to_print: str) -> list:
        yield self._instruction_for(shell_commands.command_that_prints_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self,
                                     hds: HomeDirectoryStructure,
                                     exit_code: int) -> list:
        yield self._instruction_for(shell_commands.command_that_exits_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self, hds: HomeDirectoryStructure) -> list:
        yield self._instruction_for(shell_commands.command_that_prints_cwd_line_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self,
                                                                    hds: HomeDirectoryStructure,
                                                                    var_name: str) -> list:
        yield self._instruction_for(
            shell_commands.command_that_prints_value_of_environment_variable_to_stdout(var_name))

    @contextmanager
    def program_that_sleeps_at_least(self, number_of_seconds: int) -> TestCaseSourceSetup:
        yield TestCaseSourceSetup(self._instruction_for(
            shell_commands.program_that_sleeps_at_least(number_of_seconds)))

    @staticmethod
    def _instruction_for(command: str) -> list:
        return [SourceCodeInstruction(LineSequence(1, (shell_command_source_line_for(command),)))]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
