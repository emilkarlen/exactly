"""
Test of test-infrastructure: instruction_check.
"""
import unittest
from typing import Dict

from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.result import sh
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import is_any_data_type
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.execution.test_resources.instruction_test_resources import \
    cleanup_phase_instruction_that
from exactly_lib_test.impls.instructions.cleanup.test_resources import instruction_check as sut
from exactly_lib_test.impls.test_resources.symbol_table_check_help import \
    do_fail_if_symbol_table_does_not_equal, \
    get_symbol_table_from_path_resolving_environment_that_is_first_arg, \
    get_symbol_table_from_instruction_environment_that_is_first_arg
from exactly_lib_test.tcfs.test_resources import non_hds_populator, sds_populator
from exactly_lib_test.tcfs.test_resources.sds_check.sds_contents_check import \
    act_dir_contains_exactly, tmp_user_dir_contains_exactly
from exactly_lib_test.test_case.result.test_resources import sh_assertions, svh_assertions
from exactly_lib_test.test_case.test_resources import instr_settings_assertions as asrt_instr_settings
from exactly_lib_test.test_case.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    sds_2_tcds_assertion
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.data.test_resources import data_symbol_utils
from exactly_lib_test.type_val_deps.data.test_resources.symbol_reference_assertions import \
    matches_data_type_symbol_reference
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.util.process_execution.test_resources import proc_exe_env_assertions as asrt_pes


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestExecution))
    ret_val.addTest(unittest.makeSuite(TestSideEffectsOfMain))
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
    def test_populate_non_hds(self):
        populated_dir_contents = DirContents([File.empty('non-hds-file.txt')])
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            utils.single_line_source(),
            sut.Arrangement(
                non_hds_contents_before_main=non_hds_populator.rel_option(
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
            sut.Arrangement(
                sds_contents_before_main=sds_populator.contents_in(
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
            sut.Arrangement(
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
    cleanup_phase_instruction_that())


class TestSymbols(TestCaseBase):
    def test_that_symbols_from_arrangement_exist_in_environment(self):
        symbol = StringConstantSymbolContext('symbol_name_in_cleanup_phase',
                                             'the symbol value in cleanup phase')
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
            unexpected_symbol_usages = [data_symbol_utils.symbol_reference('symbol_name')]
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
            self._check(
                utils.ParserThatGives(
                    cleanup_phase_instruction_that(
                        symbol_usages=do_return(symbol_usages_of_instruction))),
                utils.single_line_source(),
                sut.Arrangement(),
                sut.Expectation(
                    symbol_usages=asrt.matches_singleton_sequence(
                        matches_data_type_symbol_reference(
                            'symbol_name',
                            is_any_data_type()
                        )
                    )),
            )


class TestExecution(TestCaseBase):
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

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(utils.ParserThatGives(InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot()),
                    utils.single_line_source(),
                    sut.Arrangement(),
                    sut.Expectation(),
                    )


class TestSideEffectsOfMain(TestCaseBase):
    def test_fail_due_to_fail_of_side_effects_on_sds(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                utils.single_line_source(),
                sut.Arrangement(),
                sut.Expectation(main_side_effects_on_sds=act_dir_contains_exactly(
                    DirContents([File.empty('non-existing-file.txt')]))),
            )

    def test_fail_due_to_fail_of_side_effects_on_tcds(self):
        with self.assertRaises(utils.TestError):
            self._check(utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                        utils.single_line_source(),
                        sut.Arrangement(),
                        sut.Expectation(main_side_effects_on_tcds=sds_2_tcds_assertion(
                            act_dir_contains_exactly(
                                DirContents([File.empty('non-existing-file.txt')])))),
                        )

    def test_fail_due_to_fail_of_side_effects_on_proc_exe_settings(self):
        with self.assertRaises(utils.TestError):
            self._check(utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                        utils.single_line_source(),
                        sut.Arrangement(),
                        sut.Expectation(
                            proc_exe_settings=asrt.not_(asrt.is_instance(ProcessExecutionSettings))
                        ),
                        )

    def test_fail_due_to_fail_of_side_effects_on_instruction_settings(self):
        with self.assertRaises(utils.TestError):
            self._check(utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                        utils.single_line_source(),
                        sut.Arrangement(),
                        sut.Expectation(
                            instruction_settings=asrt.not_(asrt.is_instance(InstructionSettings))
                        ),
                        )


SUCCESSFUL_INSTRUCTION = cleanup_phase_instruction_that()


class InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot(CleanupPhaseInstruction):
    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             previous_phase: PreviousPhase) -> sh.SuccessOrHardError:
        utils.raise_test_error_if_cwd_is_not_test_root(environment.sds)
        return sh.new_sh_success()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
