"""
Test of test-infrastructure: instruction_embryo_check.
"""
import pathlib
import unittest

from exactly_lib.instructions.multi_phase_instructions.utils import instruction_embryo as embryo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import RelNonHomeOptionType, RelSdsOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.process_execution import os_process_execution
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.execution.test_resources.instruction_test_resources import \
    do_return
from exactly_lib_test.instructions.multi_phase_instructions.test_resources import instruction_embryo_check as sut
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_instruction import \
    instruction_embryo_that
from exactly_lib_test.instructions.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.instructions.test_resources.symbol_table_check_help import \
    get_symbol_table_from_path_resolving_environment_that_is_first_arg, \
    get_symbol_table_from_instruction_environment_that_is_first_arg, do_fail_if_symbol_table_does_not_equal
from exactly_lib_test.instructions.test_resources.test_of_test_framework_utils import single_line_source
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as sym_asrt
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case_file_structure.test_resources import non_home_populator
from exactly_lib_test.test_case_file_structure.test_resources.home_populators import case_home_dir_contents
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    act_dir_contains_exactly, tmp_user_dir_contains_exactly, result_dir_contains_exactly
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestArgumentTypesGivenToAssertions),
        unittest.makeSuite(TestMiscCases),
        unittest.makeSuite(TestSymbols),
        unittest.makeSuite(TestHomeDirHandling),
        unittest.makeSuite(TestPopulate),
    ])


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.tc = utils.TestCaseWithTestErrorAsFailureException()

    def _check(self,
               parser: embryo.InstructionEmbryoParser,
               source: ParseSource,
               arrangement: ArrangementWithSds,
               expectation: sut.Expectation):
        sut.check(self.tc, parser, source, arrangement, expectation)


class TestArgumentTypesGivenToAssertions(TestCaseBase):
    def test_source(self):
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation(source=asrt.IsInstance(ParseSource)),
        )

    def test_side_effects_on_files(self):
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation(main_side_effects_on_sds=asrt.IsInstance(SandboxDirectoryStructure)),
        )

    def test_home_and_sds(self):
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation(side_effects_on_home_and_sds=asrt.IsInstance(HomeAndSds)),
        )

    def test_home(self):
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation(side_effects_on_home=asrt.IsInstance(pathlib.Path)),
        )

    def test_environment_variables__is_an_empty_dict(self):
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation(main_side_effect_on_environment_variables=asrt.equals({})),
        )

    def test_symbols_after_main(self):
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation(symbols_after_main=asrt.is_instance(SymbolTable)),
        )


class TestSymbols(TestCaseBase):
    def test_that_default_expectation_assumes_no_symbol_usages(self):
        with self.assertRaises(utils.TestError):
            unexpected_symbol_usages = [symbol_utils.symbol_reference('symbol_name')]
            self._check(
                ParserThatGives(
                    instruction_embryo_that(
                        symbol_usages=do_return(unexpected_symbol_usages))),
                single_line_source(),
                ArrangementWithSds(),
                sut.Expectation(),
            )

    def test_that_fails_due_to_missing_symbol_reference(self):
        with self.assertRaises(utils.TestError):
            symbol_usages_of_instruction = []
            symbol_usages_of_expectation = [symbol_utils.symbol_reference('symbol_name')]
            self._check(
                ParserThatGives(
                    instruction_embryo_that(
                        symbol_usages=do_return(symbol_usages_of_instruction))),
                single_line_source(),
                ArrangementWithSds(),
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
            ParserThatGives(
                instruction_embryo_that(
                    validate_pre_sds_initial_action=assertion_for_validation,
                    validate_post_sds_initial_action=assertion_for_validation,
                    main_initial_action=assertion_for_main,
                )),
            single_line_source(),
            ArrangementWithSds(symbols=symbol_table_of_arrangement),
            sut.Expectation(),
        )

    def test_symbols_populated_by_main_SHOULD_appear_in_symbol_table_given_to_symbols_after_main(self):
        symbol_name = 'symbol_name'

        def add_symbol_to_symbol_table(environment: InstructionEnvironmentForPostSdsStep,
                                       *args, **kwargs):
            environment.symbols.put(symbol_name,
                                    symbol_utils.string_value_constant_container('const string'))

        self._check(
            ParserThatGives(
                instruction_embryo_that(
                    main_initial_action=add_symbol_to_symbol_table)),
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation(
                symbols_after_main=asrt.sub_component('names_set',
                                                      SymbolTable.names_set.fget,
                                                      asrt.equals({symbol_name}))),
        )


class TestHomeDirHandling(TestCaseBase):
    def test_fail_due_to_side_effects_on_home(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_source(),
                ArrangementWithSds(),
                sut.Expectation(side_effects_on_home=f_asrt.dir_contains_at_least(
                    DirContents([empty_file('file-name.txt')]))),
            )

    def test_arrangement_and_expectation_of_home_dir_contents(self):
        home_dir_contents = DirContents([empty_file('file-name.txt')])
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            ArrangementWithSds(
                hds_contents=case_home_dir_contents(home_dir_contents)),
            sut.Expectation(
                side_effects_on_home=f_asrt.dir_contains_exactly(home_dir_contents)),
        )


class TestPopulate(TestCaseBase):
    def test_populate_non_home(self):
        populated_dir_contents = DirContents([empty_file('non-home-file.txt')])
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            ArrangementWithSds(
                non_home_contents=non_home_populator.rel_option(RelNonHomeOptionType.REL_TMP,
                                                                populated_dir_contents)),
            sut.Expectation(
                main_side_effects_on_sds=tmp_user_dir_contains_exactly(
                    populated_dir_contents)),
        )

    def test_populate_sds(self):
        populated_dir_contents = DirContents([empty_file('sds-file.txt')])
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            ArrangementWithSds(
                sds_contents=sds_populator.contents_in(RelSdsOptionType.REL_RESULT,
                                                       populated_dir_contents)),
            sut.Expectation(
                main_side_effects_on_sds=result_dir_contains_exactly(
                    populated_dir_contents)),
        )


class TestMiscCases(TestCaseBase):
    def test_successful_step_sequence(self):
        validate_pre_sds = 'validate_pre_sds'
        validate_post_sds = 'validate_post_sds'
        main = 'main'

        expected_recordings = [
            validate_pre_sds,
            validate_post_sds,
            main,
        ]
        recorder = []

        def recording_of(s: str):
            def ret_val(*args, **kwargs):
                recorder.append(s)

            return ret_val

        instruction_that_records_steps = instruction_embryo_that(
            validate_pre_sds_initial_action=recording_of(validate_pre_sds),
            validate_post_sds_initial_action=recording_of(validate_post_sds),
            main_initial_action=recording_of(main))
        self._check(
            ParserThatGives(instruction_that_records_steps),
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation())

        self.assertEqual(expected_recordings,
                         recorder,
                         'step execution sequence')

    def test_successful_flow(self):
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation())

    def test_fail_due_to_unexpected_result_from__validate_pre_sds(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_source(),
                ArrangementWithSds(),
                sut.Expectation(validation_pre_sds=asrt.is_not_none),
            )

    def test_fail_due_to_unexpected_result_from__validate_post_sds(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_source(),
                ArrangementWithSds(),
                sut.Expectation(validation_post_sds=asrt.is_not_none),
            )

    def test_fail_due_to_unexpected_result__from_main(self):
        with self.assertRaises(utils.TestError):
            self._check(
                ParserThatGives(instruction_embryo_that(main=do_return('actual'))),
                single_line_source(),
                ArrangementWithSds(),
                sut.Expectation(main_result=asrt.equals('different-from-actual')),
            )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_source(),
                ArrangementWithSds(),
                sut.Expectation(main_side_effects_on_sds=act_dir_contains_exactly(
                    DirContents([empty_file('non-existing-file.txt')]))),
            )

    def test_that_cwd_for_main__and__validate_post_setup_is_act_dir(self):
        instruction_that_raises_exception_if_unexpected_state = instruction_embryo_that(
            main_initial_action=utils.raise_test_error_if_cwd_is_not_act_root__env,
            validate_post_sds_initial_action=utils.raise_test_error_if_cwd_is_not_act_root__env,
        )
        self._check(
            ParserThatGives(instruction_that_raises_exception_if_unexpected_state),
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation())

    def test_fail_due_to_side_effects_check(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_source(),
                ArrangementWithSds(),
                sut.Expectation(side_effects_on_home_and_sds=asrt.IsInstance(bool)),
            )

    def test_manipulate_environment_variables(self):
        env_var = NameAndValue('env_var_name', 'env var value')
        expected_environment_variables = {
            env_var.name: env_var.value
        }
        instruction = InstructionThatSetsEnvironmentVariable(env_var)

        self._check(
            ParserThatGives(instruction),
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation(main_side_effect_on_environment_variables=asrt.equals(expected_environment_variables)),
        )

    def test_propagate_environment_variables_from_arrangement(self):
        env_var_in_arrangement = NameAndValue('env_var_in_arr_name', 'env var in arr value')
        env_var_to_set = NameAndValue('env_var_name', 'env var value')

        environ_of_arrangement = {
            env_var_in_arrangement.name: env_var_in_arrangement.value,
        }

        expected_environment_variables = {
            env_var_in_arrangement.name: env_var_in_arrangement.value,
            env_var_to_set.name: env_var_to_set.value
        }
        instruction = InstructionThatSetsEnvironmentVariable(env_var_to_set)

        self._check(
            ParserThatGives(instruction),
            single_line_source(),
            ArrangementWithSds(
                process_execution_settings=os_process_execution.with_environ(environ_of_arrangement)),
            sut.Expectation(
                main_side_effect_on_environment_variables=
                asrt.equals(expected_environment_variables)),
        )


class ParserThatGives(embryo.InstructionEmbryoParser):
    def __init__(self,
                 instruction: embryo.InstructionEmbryo):
        self.instruction = instruction

    def parse(self, source: ParseSource) -> embryo.InstructionEmbryo:
        return self.instruction


PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION = ParserThatGives(instruction_embryo_that())


class InstructionThatSetsEnvironmentVariable(embryo.InstructionEmbryo):
    def __init__(self, variable: NameAndValue):
        self.variable = variable

    def main(self, environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices):
        variable = self.variable
        environment.environ[variable.name] = variable.value


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
