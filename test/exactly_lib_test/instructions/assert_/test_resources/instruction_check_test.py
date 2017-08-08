"""
Test of test-infrastructure: instruction_check.
"""
import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.execution.test_resources.instruction_test_resources import \
    assert_phase_instruction_that
from exactly_lib_test.instructions.assert_.test_resources import instruction_check as sut
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import is_pass, \
    Expectation
from exactly_lib_test.instructions.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.instructions.test_resources.symbol_table_check_help import \
    get_symbol_table_from_path_resolving_environment_that_is_first_arg, \
    get_symbol_table_from_instruction_environment_that_is_first_arg, do_fail_if_symbol_table_does_not_equal
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as sym_asrt
from exactly_lib_test.symbol.test_resources import symbol_utils
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
    ret_val.addTest(unittest.makeSuite(TestSymbolUsages))
    return ret_val


class TestCaseBase(utils.TestCaseBase):
    def setUp(self):
        self.tc = utils.TestCaseWithTestErrorAsFailureException()

    def _check(self,
               parser: InstructionParser,
               source: ParseSource,
               arrangement: sut.ArrangementPostAct,
               expectation: sut.Expectation):
        sut.check(self.tc, parser, source, arrangement, expectation)


class TestPopulate(TestCaseBase):
    def test_populate_non_home(self):
        populated_dir_contents = DirContents([empty_file('non-home-file.txt')])
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            utils.single_line_source(),
            sut.ArrangementPostAct(
                non_home_contents=non_home_populator.rel_option(
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
            sut.ArrangementPostAct(
                sds_contents=sds_populator.contents_in(
                    sds_populator.RelSdsOptionType.REL_TMP,
                    populated_dir_contents)),
            sut.Expectation(
                main_side_effects_on_files=tmp_user_dir_contains_exactly(
                    populated_dir_contents)),
        )


PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION = utils.ParserThatGives(
    assert_phase_instruction_that())


class TestSymbolUsages(TestCaseBase):
    def test_that_default_expectation_assumes_no_symbol_usages(self):
        with self.assertRaises(utils.TestError):
            unexpected_symbol_usages = [symbol_utils.symbol_reference('symbol_name')]
            self._check(
                utils.ParserThatGives(
                    assert_phase_instruction_that(
                        symbol_usages=do_return(unexpected_symbol_usages))),
                utils.single_line_source(),
                sut.ArrangementPostAct(),
                sut.Expectation(),
            )

    def test_that_fails_due_to_missing_symbol_reference(self):
        with self.assertRaises(utils.TestError):
            symbol_usages_of_instruction = []
            symbol_usages_of_expectation = [symbol_utils.symbol_reference('symbol_name')]
            self._check(
                utils.ParserThatGives(
                    assert_phase_instruction_that(
                        symbol_usages=do_return(symbol_usages_of_instruction))),
                utils.single_line_source(),
                sut.ArrangementPostAct(),
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
                assert_phase_instruction_that(
                    validate_pre_sds_initial_action=assertion_for_validation,
                    validate_post_setup_initial_action=assertion_for_validation,
                    main_initial_action=assertion_for_main,
                )),
            utils.single_line_source(),
            sut.ArrangementPostAct(
                symbols=symbol_table_of_arrangement),
            sut.Expectation(),
        )


class TestMiscCases(TestCaseBase):
    def test_successful_flow(self):
        self._check(
            utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
            utils.single_line_source(),
            sut.ArrangementPostAct(),
            is_pass())

    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                        utils.single_line_source(),
                        sut.ArrangementPostAct(),
                        Expectation(
                            validation_pre_sds=svh_assertions.is_hard_error()),
                        )

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                        utils.single_line_source(),
                        sut.ArrangementPostAct(),
                        Expectation(
                            validation_post_sds=svh_assertions.is_hard_error()),
                        )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                utils.single_line_source(),
                sut.ArrangementPostAct(),
                Expectation(
                    main_result=pfh_check.is_fail()),
            )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                utils.single_line_source(),
                sut.ArrangementPostAct(),
                Expectation(
                    main_side_effects_on_files=act_dir_contains_exactly(
                        DirContents([empty_file('non-existing-file.txt')]))),
            )

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(
            utils.ParserThatGives(InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot()),
            utils.single_line_source(),
            sut.ArrangementPostAct(),
            is_pass())

    def test_fail_due_to_side_effects_check(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                utils.single_line_source(),
                sut.ArrangementPostAct(),
                Expectation(
                    side_effects_check=sds_2_home_and_sds_assertion(
                        act_dir_contains_exactly(
                            DirContents([empty_file('non-existing-file.txt')])))),
            )


_SUCCESSFUL_INSTRUCTION = assert_phase_instruction_that()


class InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot(AssertPhaseInstruction):
    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        utils.raise_test_error_if_cwd_is_not_test_root(environment.sds)
        return svh.new_svh_success()

    def main(self, environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        utils.raise_test_error_if_cwd_is_not_test_root(environment.sds)
        return pfh.new_pfh_pass()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
