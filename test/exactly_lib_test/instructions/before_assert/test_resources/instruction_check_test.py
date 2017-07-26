"""
Test of test-infrastructure: instruction_check.
"""
import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.execution.test_resources.instruction_test_resources import \
    before_assert_phase_instruction_that
from exactly_lib_test.instructions.before_assert.test_resources import instruction_check as sut
from exactly_lib_test.instructions.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.symbol_table_check_help import \
    get_symbol_table_from_path_resolving_environment_that_is_first_arg, \
    get_symbol_table_from_instruction_environment_that_is_first_arg, do_fail_if_symbol_table_does_not_equal
from exactly_lib_test.instructions.test_resources.test_of_test_framework_utils import single_line_source
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as sym_asrt
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case_file_structure.test_resources import non_home_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    act_dir_contains_exactly, tmp_user_dir_contains_exactly
from exactly_lib_test.test_case_utils.test_resources import svh_assertions, sh_assertions
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMiscCases),
        unittest.makeSuite(TestPopulate),
        unittest.makeSuite(TestSymbols),
    ])


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.tc = utils.TestCaseWithTestErrorAsFailureException()

    def _check(self,
               parser: InstructionParser,
               source: ParseSource,
               arrangement: ArrangementPostAct,
               expectation: sut.Expectation):
        sut.check(self.tc, parser, source, arrangement, expectation)


class TestPopulate(TestCaseBase):
    def test_populate_non_home(self):
        populated_dir_contents = DirContents([empty_file('non-home-file.txt')])
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            utils.single_line_source(),
            sut.arrangement(
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
            sut.arrangement(
                sds_contents_before_main=sds_populator.contents_in(
                    sds_populator.RelSdsOptionType.REL_TMP,
                    populated_dir_contents)),
            sut.Expectation(
                main_side_effects_on_files=tmp_user_dir_contains_exactly(
                    populated_dir_contents)),
        )


PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION = utils.ParserThatGives(
    before_assert_phase_instruction_that())


class TestSymbols(TestCaseBase):
    def test_that_default_expectation_assumes_no_symbol_usages(self):
        with self.assertRaises(utils.TestError):
            unexpected_symbol_usages = [symbol_utils.symbol_reference('symbol_name')]
            self._check(
                utils.ParserThatGives(
                    before_assert_phase_instruction_that(
                        symbol_usages=do_return(unexpected_symbol_usages))),
                single_line_source(),
                sut.arrangement(),
                sut.Expectation(),
            )

    def test_that_fails_due_to_missing_symbol_reference(self):
        with self.assertRaises(utils.TestError):
            symbol_usages_of_instruction = []
            symbol_usages_of_expectation = [symbol_utils.symbol_reference('symbol_name')]
            self._check(
                utils.ParserThatGives(
                    before_assert_phase_instruction_that(
                        symbol_usages=do_return(symbol_usages_of_instruction))),
                single_line_source(),
                sut.arrangement(),
                sut.Expectation(
                    symbol_usages=sym_asrt.equals_symbol_references(symbol_usages_of_expectation)),
            )

    def test_that_symbols_from_arrangement_exist_in_environment(self):
        symbol_name = 'symbol_name'
        symbol_value = 'the symbol value'
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
                before_assert_phase_instruction_that(
                    validate_pre_sds_initial_action=assertion_for_validation,
                    validate_post_setup_initial_action=assertion_for_validation,
                    main_initial_action=assertion_for_main,
                )),
            utils.single_line_source(),
            sut.arrangement(symbols=symbol_table_of_arrangement),
            sut.Expectation(),
        )


class TestMiscCases(TestCaseBase):
    def test_successful_flow(self):
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            sut.arrangement(),
            sut.is_success())

    def test_fail_due_to_unexpected_result_from__validate_pre_sds(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_source(),
                sut.arrangement(),
                sut.Expectation(validation_pre_sds=svh_assertions.is_hard_error()),
            )

    def test_fail_due_to_unexpected_result_from__validate_post_setup(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_source(),
                sut.arrangement(),
                sut.Expectation(validation_post_setup=svh_assertions.is_hard_error()),
            )

    def test_fail_due_to_unexpected_result__from_main(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_source(),
                sut.arrangement(),
                sut.Expectation(main_result=sh_assertions.is_hard_error()),
            )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_source(),
                sut.arrangement(),
                sut.Expectation(main_side_effects_on_files=act_dir_contains_exactly(
                    DirContents([empty_file('non-existing-file.txt')]))),
            )

    def test_that_cwd_for_main__and__validate_post_setup_is_act_dir(self):
        self._check(
            utils.ParserThatGives(InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot()),
            single_line_source(),
            sut.arrangement(),
            sut.is_success())

    def test_fail_due_to_side_effects_check(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_source(),
                sut.arrangement(),
                sut.Expectation(home_and_sds=asrt.IsInstance(bool)),
            )


PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION = utils.ParserThatGives(before_assert_phase_instruction_that())


class InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot(BeforeAssertPhaseInstruction):
    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        utils.raise_test_error_if_cwd_is_not_test_root(environment.sds)
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> sh.SuccessOrHardError:
        utils.raise_test_error_if_cwd_is_not_test_root(environment.sds)
        return sh.new_sh_success()


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
