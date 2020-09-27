import unittest
from typing import List

from exactly_lib.cli.definitions.program_modes.test_case.command_line_options import \
    OPTION_FOR_KEEPING_SANDBOX_DIRECTORY
from exactly_lib.processing import exit_values
from exactly_lib.section_document.syntax import section_header
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.tcfs import sds, tcds_symbols
from exactly_lib.test_case import phase_identifier
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.cli_default.program_modes.test_case.test_resources.utils import remove_if_is_directory, \
    get_printed_sds_or_fail
from exactly_lib_test.cli_default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.cli_default.test_resources.test_case_file_elements import phase_header_line
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndTestActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.main_program.main_program_via_sub_process_utils import contents_of_file
from exactly_lib_test.test_resources.process import SubProcessResultInfo
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, process_result_info_assertions
from exactly_lib_test.test_resources.value_assertions.process_result_info_assertions import \
    process_result_for_exit_value
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(tests_for_setup_without_preprocessor(MISC_TESTS, main_program_runner))
    return ret_val


def suite() -> unittest.TestSuite:
    return suite_for(main_program_runner_with_default_setup__in_same_process())


class EmptyTestCaseShouldPass(SetupWithoutPreprocessorAndTestActor):
    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def test_case(self) -> str:
        return ''


class AllPhasesEmptyShouldPass(SetupWithoutPreprocessorAndTestActor):
    def test_case(self) -> str:
        test_case_lines = [phase_header_line(phase)
                           for phase in phase_identifier.ALL]
        return lines_content(test_case_lines)

    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)


class WhenAPhaseHasInvalidPhaseNameThenExitStatusShouldIndicateThis(SetupWithoutPreprocessorAndTestActor):
    def test_case(self) -> str:
        test_case_lines = [
            section_header('invalid phase name'),
        ]
        return lines_content(test_case_lines)

    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.NO_EXECUTION__SYNTAX_ERROR)


class PathSymbolsAreSetCorrectly(SetupWithoutPreprocessorAndTestActor):
    def additional_arguments(self) -> List[str]:
        return [OPTION_FOR_KEEPING_SANDBOX_DIRECTORY]

    def test_case(self) -> str:
        test_case_source_lines = [
            '[act]',
            'import os',
            _print_symbol_name__equals__symbol_value(tcds_symbols.SYMBOL_HDS_CASE),
            _print_symbol_name__equals__symbol_value(tcds_symbols.SYMBOL_HDS_ACT),
            _print_symbol_name__equals__symbol_value(tcds_symbols.SYMBOL_ACT),
            _print_symbol_name__equals__symbol_value(tcds_symbols.SYMBOL_TMP),
        ]
        return lines_content(test_case_source_lines)

    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return asrt.And([
            process_result_info_assertions.is_process_result_for_exit_code(exit_values.EXECUTION__PASS.exit_code),
            ExpectedTestPathSymbolsAreSetCorrectlyVa(),
        ])


class ExpectedTestPathSymbolsAreSetCorrectlyVa(ValueAssertionBase[SubProcessResultInfo]):
    def _apply(self,
               put: unittest.TestCase,
               value: SubProcessResultInfo,
               message_builder: asrt.MessageBuilder):
        actual_sds_directory = get_printed_sds_or_fail(put, value.sub_process_result)
        the_sds = sds.SandboxDs(actual_sds_directory)
        actually_printed_variables = _get_act_output_to_stdout(the_sds).splitlines()
        expected_printed_variables = [
            '%s=%s' % (tcds_symbols.SYMBOL_HDS_CASE, str(value.file_argument.parent)),
            '%s=%s' % (tcds_symbols.SYMBOL_HDS_ACT, str(value.file_argument.parent)),
            '%s=%s' % (tcds_symbols.SYMBOL_ACT, str(the_sds.act_dir)),
            '%s=%s' % (tcds_symbols.SYMBOL_TMP, str(the_sds.user_tmp_dir)),
        ]
        put.assertEqual(expected_printed_variables,
                        actually_printed_variables,
                        message_builder.apply('Environment variables printed by the act script'))
        remove_if_is_directory(actual_sds_directory)


def _print_symbol_name__equals__symbol_value(variable_name: str) -> str:
    return 'print("%s=" + "%s")' % (variable_name, symbol_reference_syntax_for_name(variable_name))


def _get_act_output_to_stdout(sds: sds.SandboxDs) -> str:
    return contents_of_file(sds.result.stdout_file)


MISC_TESTS = [
    EmptyTestCaseShouldPass(),
    AllPhasesEmptyShouldPass(),

    WhenAPhaseHasInvalidPhaseNameThenExitStatusShouldIndicateThis(),
    PathSymbolsAreSetCorrectly(),
]

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
