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
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import arrangement, is_pass, \
    Expectation
from exactly_lib_test.instructions.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.instructions.test_resources.assertion_utils import svh_check, pfh_check
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    act_dir_contains_exactly
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    sds_2_home_and_sds_assertion


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
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


class TestCases(TestCaseBase):
    def test_successful_flow(self):
        self._check(
            utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
            utils.single_line_source(),
            arrangement(),
            is_pass())

    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                        utils.single_line_source(),
                        arrangement(),
                        Expectation(validation_pre_sds=svh_check.is_hard_error()),
                        )

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                        utils.single_line_source(),
                        arrangement(),
                        Expectation(validation_post_sds=svh_check.is_hard_error()),
                        )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                utils.single_line_source(),
                arrangement(),
                Expectation(main_result=pfh_check.is_fail()),
            )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                utils.single_line_source(),
                arrangement(),
                Expectation(main_side_effects_on_files=act_dir_contains_exactly(
                    DirContents([empty_file('non-existing-file.txt')]))),
            )

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(
            utils.ParserThatGives(InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot()),
            utils.single_line_source(),
            arrangement(),
            is_pass())

    def test_fail_due_to_side_effects_check(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                utils.single_line_source(),
                arrangement(),
                Expectation(side_effects_check=sds_2_home_and_sds_assertion(
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
