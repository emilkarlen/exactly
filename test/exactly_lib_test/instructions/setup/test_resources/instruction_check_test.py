"""
Test of test-infrastructure: instruction_check.
"""
import unittest

import exactly_lib_test.test_resources.parse
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib_test.execution.test_resources.instruction_test_resources import \
    setup_phase_instruction_that
from exactly_lib_test.instructions.setup.test_resources import instruction_check as sut
from exactly_lib_test.instructions.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.instructions.test_resources.symbol_table_check_help import do_fail_if_symbol_table_does_not_equal, \
    get_symbol_table_from_path_resolving_environment_that_is_first_arg, \
    get_symbol_table_from_instruction_environment_that_is_first_arg
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
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestMiscCases))
    ret_val.addTest(unittest.makeSuite(TestPopulate))
    ret_val.addTest(unittest.makeSuite(TestSymbols))
    ret_val.addTest(unittest.makeSuite(TestSettingsBuilder))
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


class TestSettingsBuilder(TestCaseBase):
    def test_type_of_objects_given_to_assertion(self):
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            sut.Arrangement(),
            sut.Expectation(
                settings_builder=asrt.is_instance_with(
                    sut.SettingsBuilderAssertionModel,
                    asrt.and_([
                        asrt.sub_component('SettingsBuilder',
                                           sut.SettingsBuilderAssertionModel.actual.fget,
                                           asrt.is_instance(SetupSettingsBuilder)),
                        asrt.sub_component('environment',
                                           sut.SettingsBuilderAssertionModel.environment.fget,
                                           asrt.is_instance(InstructionEnvironmentForPostSdsStep)),
                    ]))),
        )

    def test_failure(self):
        initial_settings_builder = SetupSettingsBuilder()
        expected_contents = 'expected contents'
        actual_contents = 'actual contents'
        initial_settings_builder.stdin.contents = expected_contents
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(InstructionThatSetsStdinToContents(actual_contents)),
                single_line_source(),
                sut.Arrangement(
                    initial_settings_builder=initial_settings_builder
                ),
                sut.Expectation(
                    settings_builder=asrt.sub_component(
                        'stdin.contents',
                        lambda model: model.actual.stdin.contents,
                        asrt.equals(expected_contents))
                ),
            )


class TestPopulate(TestCaseBase):
    def test_populate_non_home(self):
        populated_dir_contents = DirContents([empty_file('non-home-file.txt')])
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            sut.Arrangement(
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
            single_line_source(),
            sut.Arrangement(
                sds_contents_before_main=sds_populator.contents_in(
                    sds_populator.RelSdsOptionType.REL_TMP,
                    populated_dir_contents)),
            sut.Expectation(
                main_side_effects_on_files=tmp_user_dir_contains_exactly(
                    populated_dir_contents)),
        )


PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION = utils.ParserThatGives(
    setup_phase_instruction_that())


class TestSymbols(TestCaseBase):
    def test_that_symbols_from_arrangement_exist_in_environment(self):
        symbol_name = 'symbol_name_in_setup_phase'
        symbol_value = 'the symbol value in setup phase'
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
                setup_phase_instruction_that(
                    validate_pre_sds_initial_action=assertion_for_validation,
                    validate_post_setup_initial_action=assertion_for_validation,
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
                    setup_phase_instruction_that(
                        symbol_usages=do_return(unexpected_symbol_usages))),
                single_line_source(),
                sut.Arrangement(),
                sut.Expectation(),
            )

    def test_that_fails_due_to_missing_symbol_reference(self):
        with self.assertRaises(utils.TestError):
            symbol_usages_of_instruction = []
            symbol_usages_of_expectation = [symbol_utils.symbol_reference('symbol_name')]
            self._check(
                utils.ParserThatGives(
                    setup_phase_instruction_that(
                        symbol_usages=do_return(symbol_usages_of_instruction))),
                single_line_source(),
                sut.arrangement(),
                sut.Expectation(
                    symbol_usages=sym_asrt.equals_symbol_references(symbol_usages_of_expectation)),
            )


class TestMiscCases(TestCaseBase):
    def test_successful_flow(self):
        self._check(utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                    single_line_source(),
                    sut.Arrangement(),
                    sut.Expectation())

    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                single_line_source(),
                sut.Arrangement(),
                sut.Expectation(pre_validation_result=svh_assertions.is_hard_error())
            )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                single_line_source(),
                sut.Arrangement(),
                sut.Expectation(main_result=sh_assertions.is_hard_error())
            )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(utils.TestError):
            self._check(utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                        single_line_source(),
                        sut.Arrangement(),
                        sut.Expectation(main_side_effects_on_files=act_dir_contains_exactly(
                            DirContents([empty_file('non-existing-file.txt')]))))

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                single_line_source(),
                sut.Arrangement(),
                sut.Expectation(post_validation_result=svh_assertions.is_hard_error())
            )

    def test_fail_due_to_side_effects_check(self):
        with self.assertRaises(utils.TestError):
            self._check(utils.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                        single_line_source(),
                        sut.Arrangement(),
                        sut.Expectation(side_effects_check=asrt.IsInstance(bool))
                        )

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(utils.ParserThatGives(InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot()),
                    single_line_source(),
                    sut.Arrangement(),
                    sut.Expectation()
                    )


def single_line_source() -> ParseSource:
    return exactly_lib_test.test_resources.parse.source4('instruction arguments')


SUCCESSFUL_INSTRUCTION = setup_phase_instruction_that()


class InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot(SetupPhaseInstruction):
    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        utils.raise_test_error_if_cwd_is_not_test_root(environment.sds)
        return sh.new_sh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        utils.raise_test_error_if_cwd_is_not_test_root(environment.sds)
        return svh.new_svh_success()


class InstructionThatSetsStdinToContents(SetupPhaseInstruction):
    def __init__(self, contents: str):
        self.contents = contents

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        settings_builder.stdin.contents = self.contents
        return sh.new_sh_success()


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
