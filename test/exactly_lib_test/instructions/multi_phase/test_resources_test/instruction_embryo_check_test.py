"""
Test of test-infrastructure: instruction_embryo_check.
"""
import pathlib
import unittest
from typing import Generic

from exactly_lib.appl_env.os_services import OsServices
from exactly_lib.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.instructions.multi_phase.utils.instruction_embryo import T
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.tcfs.path_relativity import RelNonHdsOptionType, RelSdsOptionType
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import is_any_data_type
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.process_execution import execution_elements
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources.text_doc_assertions import new_single_string_text_for_test
from exactly_lib_test.execution.test_resources.instruction_test_resources import \
    do_return
from exactly_lib_test.instructions.multi_phase.test_resources import instruction_embryo_check as sut
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import \
    InstructionApplicationEnvironment
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_instruction import \
    instruction_embryo_that
from exactly_lib_test.tcfs.test_resources import non_hds_populator, sds_populator
from exactly_lib_test.tcfs.test_resources.hds_populators import hds_case_dir_contents
from exactly_lib_test.tcfs.test_resources.sds_check.sds_contents_check import \
    act_dir_contains_exactly, tmp_user_dir_contains_exactly, result_dir_contains_exactly
from exactly_lib_test.test_case.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case.test_resources.test_of_test_framework_utils import single_line_source
from exactly_lib_test.test_case_utils.test_resources.symbol_table_check_help import \
    get_symbol_table_from_path_resolving_environment_that_is_first_arg, \
    get_symbol_table_from_instruction_environment_that_is_first_arg, do_fail_if_symbol_table_does_not_equal
from exactly_lib_test.test_resources.actions import do_raise
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.data.test_resources import data_symbol_utils
from exactly_lib_test.type_val_deps.data.test_resources.symbol_reference_assertions import \
    matches_data_type_symbol_reference
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestArgumentTypesGivenToAssertions),
        unittest.makeSuite(TestMiscCases),
        unittest.makeSuite(TestSymbols),
        unittest.makeSuite(TestHdsDirHandling),
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
            sut.Expectation(main_side_effects_on_sds=asrt.IsInstance(SandboxDs)),
        )

    def test_tcds(self):
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation(side_effects_on_tcds=asrt.IsInstance(TestCaseDs)),
        )

    def test_hds(self):
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation(side_effects_on_hds=asrt.IsInstance(pathlib.Path)),
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

    def test_assertion_on_instruction_environment(self):
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation(
                assertion_on_instruction_environment=
                asrt.is_instance_with__many(
                    InstructionApplicationEnvironment,
                    [
                        asrt.sub_component(
                            'InstructionEnvironmentForPostSdsStep',
                            InstructionApplicationEnvironment.instruction.fget,
                            asrt.is_instance(InstructionEnvironmentForPostSdsStep),
                        ),
                        asrt.sub_component(
                            'OsServices',
                            InstructionApplicationEnvironment.os_service.fget,
                            asrt.is_instance(OsServices),
                        ),
                    ]
                )),
        )


class TestSymbols(TestCaseBase):
    def test_that_default_expectation_assumes_no_symbol_usages(self):
        with self.assertRaises(utils.TestError):
            unexpected_symbol_usages = [data_symbol_utils.symbol_reference('symbol_name')]
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
            self._check(
                ParserThatGives(
                    instruction_embryo_that(
                        symbol_usages=do_return(symbol_usages_of_instruction))),
                single_line_source(),
                ArrangementWithSds(),
                sut.Expectation(
                    symbol_usages=asrt.matches_singleton_sequence(
                        matches_data_type_symbol_reference(
                            'symbol_name',
                            is_any_data_type()
                        )
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
        symbol = StringConstantSymbolContext('symbol_name', 'const string')

        def add_symbol_to_symbol_table(environment: InstructionEnvironmentForPostSdsStep,
                                       *args, **kwargs):
            environment.symbols.put(symbol.name,
                                    symbol.symbol_table_container)

        self._check(
            ParserThatGives(
                instruction_embryo_that(
                    main_initial_action=add_symbol_to_symbol_table)),
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation(
                symbols_after_main=asrt.sub_component('names_set',
                                                      SymbolTable.names_set.fget,
                                                      asrt.equals({symbol.name}))),
        )


class TestHdsDirHandling(TestCaseBase):
    def test_fail_due_to_side_effects_on_hds(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_source(),
                ArrangementWithSds(),
                sut.Expectation(side_effects_on_hds=f_asrt.dir_contains_at_least(
                    DirContents([File.empty('file-name.txt')]))),
            )

    def test_arrangement_and_expectation_of_hds_dir_contents(self):
        home_dir_contents = DirContents([File.empty('file-name.txt')])
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            ArrangementWithSds(
                hds_contents=hds_case_dir_contents(home_dir_contents)),
            sut.Expectation(
                side_effects_on_hds=f_asrt.dir_contains_exactly(home_dir_contents)),
        )


class TestPopulate(TestCaseBase):
    def test_populate_non_hds(self):
        populated_dir_contents = DirContents([File.empty('non-hds-file.txt')])
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            ArrangementWithSds(
                non_hds_contents=non_hds_populator.rel_option(RelNonHdsOptionType.REL_TMP,
                                                              populated_dir_contents)),
            sut.Expectation(
                main_side_effects_on_sds=tmp_user_dir_contains_exactly(
                    populated_dir_contents)),
        )

    def test_populate_sds(self):
        populated_dir_contents = DirContents([File.empty('sds-file.txt')])
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

    def test_fail_due_to_unexpected_hard_error_exception(self):
        with self.assertRaises(utils.TestError):
            self._check(
                ParserThatGives(instruction_embryo_that(
                    main=do_raise(HardErrorException(new_single_string_text_for_test('hard error message'))))
                ),
                single_line_source(),
                ArrangementWithSds(),
                sut.Expectation(main_result=asrt.anything_goes()),
            )

    def test_succeed_due_to_expected_hard_error_exception(self):
        self._check(
            ParserThatGives(instruction_embryo_that(
                main=do_raise(HardErrorException(new_single_string_text_for_test('hard error message'))))
            ),
            single_line_source(),
            ArrangementWithSds(),
            sut.Expectation(main_raises_hard_error=True),
        )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_source(),
                ArrangementWithSds(),
                sut.Expectation(main_side_effects_on_sds=act_dir_contains_exactly(
                    DirContents([File.empty('non-existing-file.txt')]))),
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
                sut.Expectation(side_effects_on_tcds=asrt.IsInstance(bool)),
            )

    def test_fail_due_to_assertion_on_instruction_environment(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
                single_line_source(),
                ArrangementWithSds(),
                sut.Expectation(assertion_on_instruction_environment=asrt.fail('unconditional failure')),
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
                process_execution_settings=execution_elements.with_environ(environ_of_arrangement)),
            sut.Expectation(
                main_side_effect_on_environment_variables=
                asrt.equals(expected_environment_variables)),
        )


class ParserThatGives(Generic[T], embryo.InstructionEmbryoParser[T]):
    def __init__(self, instruction: embryo.InstructionEmbryo[T]):
        self.instruction = instruction

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> embryo.InstructionEmbryo[T]:
        return self.instruction


PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION = ParserThatGives(instruction_embryo_that())


class InstructionThatSetsEnvironmentVariable(embryo.InstructionEmbryo[None]):
    def __init__(self, variable: NameAndValue):
        self.variable = variable

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             ):
        variable = self.variable
        environment.proc_exe_settings.environ[variable.name] = variable.value


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
