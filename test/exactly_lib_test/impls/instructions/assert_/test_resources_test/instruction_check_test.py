"""
Test of test-infrastructure: instruction_check.
"""
import unittest
from typing import Dict

from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.result import pfh, svh
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.execution.test_resources.instruction_test_resources import \
    assert_phase_instruction_that
from exactly_lib_test.impls.instructions.assert_.test_resources import instruction_check as sut
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import is_pass, \
    Expectation
from exactly_lib_test.impls.test_resources.symbol_table_check_help import \
    get_symbol_table_from_path_resolving_environment_that_is_first_arg, \
    get_symbol_table_from_instruction_environment_that_is_first_arg, do_fail_if_symbol_table_does_not_equal
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.tcfs.test_resources import non_hds_populator, sds_populator
from exactly_lib_test.tcfs.test_resources.sds_check.sds_contents_check import \
    act_dir_contains_exactly, tmp_user_dir_contains_exactly
from exactly_lib_test.test_case.result.test_resources import pfh_assertions, svh_assertions
from exactly_lib_test.test_case.test_resources import instr_settings_assertions as asrt_instr_settings
from exactly_lib_test.test_case.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    sds_2_tcds_assertion
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import references as data_references
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.symbol_reference_assertions import \
    matches_data_type_symbol_reference
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext
from exactly_lib_test.util.process_execution.test_resources import proc_exe_env_assertions as asrt_pes


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestExecution))
    ret_val.addTest(unittest.makeSuite(TestSideEffectsOfMain))
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
    def test_populate_non_hds(self):
        populated_dir_contents = DirContents([File.empty('non-hds-file.txt')])
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            utils.single_line_source(),
            sut.ArrangementPostAct(
                non_hds_contents=non_hds_populator.rel_option(
                    non_hds_populator.RelNonHdsOptionType.REL_TMP,
                    populated_dir_contents)),
            sut.Expectation(
                main_side_effects_on_sds=tmp_user_dir_contains_exactly(
                    populated_dir_contents)),
        )

    def test_populate_sds(self):
        populated_dir_contents = DirContents([File.empty('sds-file.txt')])
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            utils.single_line_source(),
            sut.ArrangementPostAct(
                sds_contents=sds_populator.contents_in(
                    sds_populator.RelSdsOptionType.REL_TMP,
                    populated_dir_contents)),
            sut.Expectation(
                main_side_effects_on_sds=tmp_user_dir_contains_exactly(
                    populated_dir_contents)),
        )

    def test_populate_environ(self):
        default_from_default_getter = {'default': 'value of default'}
        default_environs = {'in_environs': 'value of var in environs'}

        def default_environ_getter() -> Dict[str, str]:
            return default_from_default_getter

        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            utils.single_line_source(),
            sut.ArrangementPostAct(
                default_environ_getter=default_environ_getter,
                process_execution_settings=ProcessExecutionSettings.from_non_immutable(environ=default_environs),
            ),
            sut.Expectation(
                instruction_settings=asrt_instr_settings.matches(
                    environ=asrt.equals(default_environs),
                    return_value_from_default_getter=asrt.equals(default_from_default_getter)
                ),
                proc_exe_settings=asrt_pes.matches(
                    environ=asrt.equals(default_environs)
                )
            ),
        )


PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION = utils.ParserThatGives(
    assert_phase_instruction_that())


class TestSymbolUsages(TestCaseBase):
    def test_that_default_expectation_assumes_no_symbol_usages(self):
        with self.assertRaises(utils.TestError):
            unexpected_symbol_usages = [
                data_references.reference_to__on_direct_and_indirect('symbol_name')]
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
            self._check(
                utils.ParserThatGives(
                    assert_phase_instruction_that(
                        symbol_usages=do_return(symbol_usages_of_instruction))),
                utils.single_line_source(),
                sut.ArrangementPostAct(),
                sut.Expectation(
                    symbol_usages=asrt.matches_singleton_sequence(
                        matches_data_type_symbol_reference('symbol_name',
                                                           reference_restrictions.is_any_type_w_str_rendering())
                    )),
            )

    def test_that_symbols_from_arrangement_exist_in_environment(self):
        symbol = StringConstantSymbolContext('symbol_name', 'the symbol value')
        symbol_table_of_arrangement = symbol.symbol_table
        expected_symbol_table = symbol.symbol_table
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


class TestParse(TestCaseBase):
    def test_fail_due_to_unexpected_source_after_parse(self):
        with self.assertRaises(utils.TestError):
            self._check(utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                        utils.single_line_source(),
                        sut.ArrangementPostAct(),
                        Expectation(
                            source=asrt_source.is_at_beginning_of_line(10),
                        )
                        )


class TestExecution(TestCaseBase):
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
                    main_result=pfh_assertions.is_fail__with_arbitrary_message()),
            )

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(
            utils.ParserThatGives(InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot()),
            utils.single_line_source(),
            sut.ArrangementPostAct(),
            is_pass())


class TestSideEffectsOfMain(TestCaseBase):
    def test_fail_due_to_fail_of_side_effects_on_sds(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                utils.single_line_source(),
                sut.ArrangementPostAct(),
                Expectation(
                    main_side_effects_on_sds=act_dir_contains_exactly(
                        DirContents([File.empty('non-existing-file.txt')]))),
            )

    def test_fail_due_to_fail_of_side_effects_on_tcds(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                utils.single_line_source(),
                sut.ArrangementPostAct(),
                Expectation(
                    main_side_effects_on_tcds=sds_2_tcds_assertion(
                        act_dir_contains_exactly(
                            DirContents([File.empty('non-existing-file.txt')])))),
            )

    def test_fail_due_to_fail_of_side_effects_on_proc_exe_settings(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                utils.single_line_source(),
                sut.ArrangementPostAct(),
                Expectation(
                    proc_exe_settings=asrt.not_(asrt.is_instance(ProcessExecutionSettings))),
            )

    def test_fail_due_to_fail_of_side_effects_on_instruction_settings(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                utils.single_line_source(),
                sut.ArrangementPostAct(),
                Expectation(
                    instruction_settings=asrt.not_(asrt.is_instance(InstructionSettings))),
            )


_SUCCESSFUL_INSTRUCTION = assert_phase_instruction_that()


class InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot(AssertPhaseInstruction):
    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        utils.raise_test_error_if_cwd_is_not_test_root(environment.sds)
        return svh.new_svh_success()

    def main(self, environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        utils.raise_test_error_if_cwd_is_not_test_root(environment.sds)
        return pfh.new_pfh_pass()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
