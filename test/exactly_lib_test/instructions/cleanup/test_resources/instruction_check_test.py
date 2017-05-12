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
    cleanup_phase_instruction_that, do_return
from exactly_lib_test.instructions.cleanup.test_resources import instruction_check as sut
from exactly_lib_test.instructions.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.instructions.test_resources.assertion_utils import sh_check, svh_check
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as sym_asrt
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    act_dir_contains_exactly
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    sds_2_home_and_sds_assertion


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestMiscCases))
    ret_val.addTest(unittest.makeSuite(TestSymbolUsages))
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


class TestSymbolUsages(TestCaseBase):
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
                sut.Expectation(main_result=sh_check.is_hard_error()),
            )

    def test_fail_due_to_unexpected_result_from_validate_pre_sds(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                utils.single_line_source(),
                sut.Arrangement(),
                sut.Expectation(validate_pre_sds_result=svh_check.is_hard_error()),
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
