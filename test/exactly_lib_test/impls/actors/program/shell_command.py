import os
import unittest
from contextlib import contextmanager
from typing import ContextManager

from exactly_lib.impls.actors.program import actor as sut
from exactly_lib.processing.parse.act_phase_source_parser import SourceCodeInstruction
from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.test_case.actor import ParseException
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.result import svh
from exactly_lib.util.line_source import LineSequence
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.impls.actors.program.test_resources import shell_command_source_line_for
from exactly_lib_test.impls.actors.test_resources import \
    test_validation_for_single_line_source as single_line_source
from exactly_lib_test.impls.actors.test_resources.action_to_check import Configuration, \
    suite_for_execution, TestCaseSourceSetup
from exactly_lib_test.impls.actors.test_resources.integration_check import \
    check_execution, Arrangement, Expectation, PostSdsExpectation
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_hds
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.programs import shell_commands
from exactly_lib_test.test_resources.programs.python_program_execution import abs_path_to_interpreter_quoted_for_exactly
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext


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
        self.constructor = sut.actor()
        self.hds = fake_hds()
        self.pre_sds_env = InstructionEnvironmentForPreSdsStep(
            self.hds,
            ProcessExecutionSettings.with_environ(dict(os.environ)),
        )

    def test_parse_fails_when_command_is_empty(self):
        act_phase_instructions = [instr([shell_command_source_line_for(''), ])]
        with self.assertRaises(ParseException):
            self._do_parse(act_phase_instructions)

    def test_parse_fails_when_command_is_only_space(self):
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
        self.constructor.parse(act_phase_instructions)

    def _do_parse_and_validate(self, act_phase_instructions: list) -> svh.SuccessOrValidationErrorOrHardError:
        executor = self.constructor.parse(act_phase_instructions)
        return executor.validate_pre_sds(self.pre_sds_env)


class TestSymbolReferences(unittest.TestCase):
    def test_symbol_reference_on_command_line_SHOULD_be_reported_and_used_in_execution(self):
        symbol = StringConstantSymbolContext('symbol_name', 'symbol value')

        string_to_print_template = 'constant and {symbol}'
        expected_output_template = string_to_print_template + '\n'

        shell_source_line = shell_commands.command_that_prints_to_stdout(
            string_to_print_template.format(symbol=symbol.name__sym_ref_syntax)
        )
        act_phase_instructions = [instr([shell_command_source_line_for(shell_source_line)])]

        check_execution(
            self,
            sut.actor(),
            act_phase_instructions,
            Arrangement(
                symbol_table=symbol.symbol_table
            ),
            Expectation(
                symbol_usages=asrt.matches_singleton_sequence(symbol.reference_assertion__any_data_type),
                post_sds=PostSdsExpectation.constant(
                    sub_process_result_from_execute=
                    pr.stdout(asrt.equals(expected_output_template.format(symbol=symbol.str_value)))
                )
            ),
        )


class TheConfiguration(Configuration):
    def __init__(self):
        super().__init__(sut.actor())

    def program_that_copes_stdin_to_stdout(self) -> ContextManager[TestCaseSourceSetup]:
        return self._instruction_for(shell_commands.command_that_copes_stdin_to_stdout())

    def program_that_prints_to_stdout(self,
                                      string_to_print: str) -> ContextManager[TestCaseSourceSetup]:
        return self._instruction_for(shell_commands.command_that_prints_to_stdout(string_to_print))

    def program_that_prints_to_stderr(self,
                                      string_to_print: str) -> ContextManager[TestCaseSourceSetup]:
        return self._instruction_for(shell_commands.command_that_prints_to_stderr(string_to_print))

    def program_that_prints_value_of_environment_variable_to_stdout(
            self, var_name: str
    ) -> ContextManager[TestCaseSourceSetup]:
        return self._instruction_for(
            shell_commands.command_that_prints_value_of_environment_variable_to_stdout(var_name))

    def program_that_prints_cwd_to_stdout(self) -> ContextManager[TestCaseSourceSetup]:
        return self._instruction_for(shell_commands.command_that_prints_cwd_line_to_stdout())

    def program_that_exits_with_code(self,
                                     exit_code: int) -> ContextManager[TestCaseSourceSetup]:
        return self._instruction_for(shell_commands.command_that_exits_with_code(exit_code))

    def program_that_sleeps_at_least(self, number_of_seconds: int) -> ContextManager[TestCaseSourceSetup]:
        return self._instruction_for(
            shell_commands.program_that_sleeps_at_least(number_of_seconds)
        )

    @staticmethod
    @contextmanager
    def _instruction_for(command: str) -> ContextManager[TestCaseSourceSetup]:
        yield TestCaseSourceSetup(
            act_phase_instructions=[
                SourceCodeInstruction(LineSequence(1, [shell_command_source_line_for(command)]))
            ]
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
