"""
Test of test-infrastructure: instruction_check.
"""
import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib_test.execution.test_resources.instruction_test_resources import \
    cleanup_phase_instruction_that
from exactly_lib_test.instructions.cleanup.test_resources import instruction_check as sut
from exactly_lib_test.instructions.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.instructions.test_resources.symbol_table_check_help import do_fail_if_symbol_table_does_not_equal, \
    get_symbol_table_from_path_resolving_environment_that_is_first_arg, \
    get_symbol_table_from_instruction_environment_that_is_first_arg
from exactly_lib_test.named_element.symbol.test_resources import symbol_utils, symbol_reference_assertions as sym_asrt
from exactly_lib_test.test_case.test_resources import sh_assertions
from exactly_lib_test.test_case_file_structure.test_resources import non_home_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    act_dir_contains_exactly, tmp_user_dir_contains_exactly
from exactly_lib_test.test_case_utils.test_resources import svh_assertions
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    sds_2_home_and_sds_assertion


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestMiscCases))
    ret_val.addTest(unittest.makeSuite(TestPopulate))
    ret_val.addTest(unittest.makeSuite(TestSymbols))
    return ret_val


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.tc = utils.TestCaseWithTestErrorAsFailureException()

    def _check(self,
               parser: InstructionParser,
               source: ParseSource,
               arrangement: sut.Arrangement,
               expectation: sut.Expectation):
        sut.check(self.tc, parser, source, arrangement, expectation)


class TestPopulate(TestCaseBase):
    def test_populate_non_home(self):
        populated_dir_contents = DirContents([empty_file('non-home-file.txt')])
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            utils.single_line_source(),
            sut.Arrangement(
                non_home_contents_before_main=non_home_populator.rel_option(
                    non_home_populator.RelNonHomeOptionType.REL_TMP,
                    populated_dir_contents)),
            sut.Expectation(
                main_side_effects_on_files=tmp_user_dir_contains_exactly(
                    populated_dir_contents)),
        )

    def test_populate_sds(self):
        populated_dir_contents = DirContents([empty_file('sds-file.txt')])
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            utils.single_line_source(),
            sut.Arrangement(
                sds_contents_before_main=sds_populator.contents_in(
                    sds_populator.RelSdsOptionType.REL_TMP,
                    populated_dir_contents)),
            sut.Expectation(
                main_side_effects_on_files=tmp_user_dir_contains_exactly(
                    populated_dir_contents)),
        )


PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION = utils.ParserThatGives(
    cleanup_phase_instruction_that())


class TestSymbols(TestCaseBase):
    def test_that_symbols_from_arrangement_exist_in_environment(self):
        symbol_name = 'symbol_name_in_cleanup_phase'
        symbol_value = 'the symbol value in cleanup phase'
        symbol_table_of_arrangement = symbol_utils.symbol_table_with_single_string_value(symbol_name,
                                                                                         symbol_value)
        expected_symbol_table = symbol_utils.symbol_table_with_single_string_value(symbol_name,
                                                                                   symbol_value)
        assertion_for_validation = do_fail_if_symbol_table_does_not_equal(
            self,
            expected_symbol_table,
            get_symbol_table_from_path_resolving_environment_that_is_first_arg)

        assertion_for_main = do_fail_if_symbol_table_does_not_equal(
            self,
            expected_symbol_table,
            get_symbol_table_from_instruction_environment_that_is_first_arg)

        self._check(
            utils.ParserThatGives(
                cleanup_phase_instruction_that(
                    validate_pre_sds_initial_action=assertion_for_validation,
                    main_initial_action=assertion_for_main,
                )),
            utils.single_line_source(),
            sut.Arrangement(symbols=symbol_table_of_arrangement),
            sut.Expectation(),
        )

    def test_that_default_expectation_assumes_no_symbol_usages(self):
        with self.assertRaises(utils.TestError):
            unexpected_symbol_usages = [symbol_utils.symbol_reference('symbol_name')]
            self._check(
                utils.ParserThatGives(
                    cleanup_phase_instruction_that(
                        symbol_usages=do_return(unexpected_symbol_usages))),
                utils.single_line_source(),
                sut.Arrangement(),
                sut.Expectation(),
            )

    def test_that_fails_due_to_missing_symbol_reference(self):
        with self.assertRaises(utils.TestError):
            symbol_usages_of_instruction = []
            symbol_usages_of_expectation = [symbol_utils.symbol_reference('symbol_name')]
            self._check(
                utils.ParserThatGives(
                    cleanup_phase_instruction_that(
                        symbol_usages=do_return(symbol_usages_of_instruction))),
                utils.single_line_source(),
                sut.Arrangement(),
                sut.Expectation(
                    symbol_usages=sym_asrt.equals_symbol_references(symbol_usages_of_expectation)),
            )


class TestMiscCases(TestCaseBase):
    def test_successful_flow(self):
        self._check(
            utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
            utils.single_line_source(),
            sut.Arrangement(),
            sut.Expectation(),
        )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                utils.single_line_source(),
                sut.Arrangement(),
                sut.Expectation(main_result=sh_assertions.is_hard_error()),
            )

    def test_fail_due_to_unexpected_result_from_validate_pre_sds(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                utils.single_line_source(),
                sut.Arrangement(),
                sut.Expectation(validate_pre_sds_result=svh_assertions.is_hard_error()),
            )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                utils.single_line_source(),
                sut.Arrangement(),
                sut.Expectation(main_side_effects_on_files=act_dir_contains_exactly(
                    DirContents([empty_file('non-existing-file.txt')]))),
            )

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(utils.ParserThatGives(InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot()),
                    utils.single_line_source(),
                    sut.Arrangement(),
                    sut.Expectation(),
                    )

    def test_fail_due_to_side_effects_check(self):
        with self.assertRaises(utils.TestError):
            self._check(utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                        utils.single_line_source(),
                        sut.Arrangement(),
                        sut.Expectation(side_effects_check=sds_2_home_and_sds_assertion(
                            act_dir_contains_exactly(
                                DirContents([empty_file('non-existing-file.txt')])))),
                        )


SUCCESSFUL_INSTRUCTION = cleanup_phase_instruction_that()


class InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot(CleanupPhaseInstruction):
    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             previous_phase: PreviousPhase) -> sh.SuccessOrHardError:
        utils.raise_test_error_if_cwd_is_not_test_root(environment.sds)
        return sh.new_sh_success()


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
