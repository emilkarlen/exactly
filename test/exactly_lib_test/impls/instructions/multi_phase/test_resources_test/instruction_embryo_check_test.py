"""
Test of test-infrastructure: instruction_embryo_check.
"""
import pathlib
import unittest
from types import MappingProxyType
from typing import Generic, Dict, Optional, Callable

from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.impls.instructions.multi_phase.utils.instruction_embryo import T
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.tcfs.path_relativity import RelNonHdsOptionType, RelSdsOptionType
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import is_any_data_type
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources.text_doc_assertions import new_single_string_text_for_test
from exactly_lib_test.execution.test_resources.instruction_test_resources import \
    do_return
from exactly_lib_test.impls.instructions.multi_phase.test_resources import instruction_embryo_check as sut
from exactly_lib_test.impls.instructions.multi_phase.test_resources.embryo_arr_exp import \
    InstructionApplicationEnvironment, SetupSettingsArr, Arrangement, ExecutionExpectation, MultiSourceExpectation, \
    Expectation
from exactly_lib_test.impls.instructions.multi_phase.test_resources.instruction_embryo_instruction import \
    instruction_embryo_that__phase_agnostic, instruction_embryo_that__setup_phase_aware
from exactly_lib_test.impls.test_resources.symbol_table_check_help import \
    get_symbol_table_from_path_resolving_environment_that_is_first_arg, \
    get_symbol_table_from_instruction_environment_that_is_first_arg, do_fail_if_symbol_table_does_not_equal
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.tcfs.test_resources import non_hds_populator, sds_populator
from exactly_lib_test.tcfs.test_resources.hds_populators import hds_case_dir_contents
from exactly_lib_test.tcfs.test_resources.sds_check.sds_contents_check import \
    act_dir_contains_exactly, tmp_user_dir_contains_exactly, result_dir_contains_exactly
from exactly_lib_test.test_case.test_resources import instr_settings_assertions as asrt_instr_settings
from exactly_lib_test.test_case.test_resources import settings_builder_assertions as asrt_settings_builder
from exactly_lib_test.test_case.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.test_case.test_resources.test_of_test_framework_utils import single_line_source
from exactly_lib_test.test_resources.actions import do_raise
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.source.abstract_syntax_impls import CustomAbsStx
from exactly_lib_test.test_resources.test_utils import NArrEx
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import AssertionBase, MessageBuilder, Assertion
from exactly_lib_test.type_val_deps.data.test_resources import data_symbol_utils
from exactly_lib_test.type_val_deps.data.test_resources.symbol_reference_assertions import \
    matches_data_type_symbol_reference
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.util.process_execution.test_resources import proc_exe_env_assertions as asrt_pes


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestExecution),
        unittest.makeSuite(TestMainMethodTypeOfPhaseAgnostic),
        unittest.makeSuite(TestMainMethodTypeOfSetupPhaseAware),
        unittest.makeSuite(TestSideEffectsOfMain),
        unittest.makeSuite(TestArgumentTypesGivenToAssertions),
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
               arrangement: Arrangement,
               expectation: Expectation):
        sut.check(self.tc, parser, source, arrangement, expectation)

    def _check_source_and_exe_variants__failing_assertions(self,
                                                           parser: embryo.InstructionEmbryoParser[T],
                                                           arrangement: Arrangement,
                                                           expectation: MultiSourceExpectation[T],
                                                           **sub_test_identifiers
                                                           ):
        """Runs check methods for both single and multi-source.

        Source consumption is assumed to be correct (and is not tested by this method).

        :param parser: Must not consume any source.
        """
        checker = sut.Checker(ParserThatConsumesCurrentLine(parser))

        with self.subTest(_execution='single', **sub_test_identifiers):
            with self.assertRaises(utils.TestError):
                checker.check(self.tc,
                              remaining_source('irrelevant source'),
                              arrangement,
                              expectation.as_w_source(asrt.anything_goes()),
                              )

        with self.subTest(_execution='w source variants', **sub_test_identifiers):
            with self.assertRaises(utils.TestError):
                checker.check__w_source_variants(
                    self.tc,
                    'irrelevant source',
                    arrangement,
                    expectation,
                )

        with self.subTest(_execution='multi execution', **sub_test_identifiers):
            with self.assertRaises(utils.TestError):
                checker.check__abs_stx__multi__std_layouts_and_source_variants(
                    self.tc,
                    CustomAbsStx.of_str('irrelevant source'),
                    symbol_usages=expectation.symbol_usages,
                    execution_cases=[
                        NArrEx(
                            'the one and only case',
                            arrangement,
                            expectation,
                        ),
                    ]
                )

    def _check_source_and_exe_variants(self,
                                       parser: embryo.InstructionEmbryoParser[T],
                                       arrangement: Arrangement,
                                       expectation: MultiSourceExpectation[T],
                                       **sub_test_identifiers
                                       ):
        """Runs check methods for both single and multi-source.

        Source consumption is assumed to be correct (and is not tested by this method).

        :param parser: Must not consume any source.
        """
        checker = sut.Checker(ParserThatConsumesCurrentLine(parser))

        with self.subTest(_execution='single', **sub_test_identifiers):
            checker.check(self.tc,
                          remaining_source('irrelevant source'),
                          arrangement,
                          expectation.as_w_source(asrt.anything_goes()),
                          )

        with self.subTest(_execution='w source variants', **sub_test_identifiers):
            checker.check__w_source_variants(
                self.tc,
                'irrelevant source',
                arrangement,
                expectation,
            )
        with self.subTest(_execution='multi execution', **sub_test_identifiers):
            checker.check__abs_stx__multi__std_layouts_and_source_variants(
                self.tc,
                CustomAbsStx.of_str('irrelevant source'),
                symbol_usages=expectation.symbol_usages,
                execution_cases=[
                    NArrEx(
                        'the one and only case',
                        arrangement,
                        expectation,
                    ),
                ]
            )


class TestArgumentTypesGivenToAssertions(TestCaseBase):
    def test_source(self):
        self._check(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            single_line_source(),
            Arrangement.phase_agnostic(),
            Expectation.phase_agnostic(source=asrt.IsInstance(ParseSource)),
        )

    def test_side_effects_on_files(self):
        self._check_source_and_exe_variants(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                main_side_effects_on_sds=asrt.IsInstance(SandboxDs)
            ),
        )

    def test_tcds(self):
        self._check_source_and_exe_variants(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                side_effects_on_tcds=asrt.IsInstance(TestCaseDs)
            ),
        )

    def test_hds(self):
        self._check_source_and_exe_variants(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                side_effects_on_hds=asrt.IsInstance(pathlib.Path)
            ),
        )

    def test_environment_variables__is_copy_from_proc_exe_settings(self):
        self._check_source_and_exe_variants(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(
                process_execution_settings=ProcessExecutionSettings.with_environ({})
            ),
            MultiSourceExpectation.phase_agnostic(
                main_side_effect_on_environment_variables=asrt.equals({})
            ),
        )

    def test_symbols_after_main(self):
        self._check_source_and_exe_variants(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                symbols_after_main=asrt.is_instance(SymbolTable)
            ),
        )

    def test_assertion_on_instruction_environment(self):
        self._check_source_and_exe_variants(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                instruction_environment=
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
        unexpected_symbol_usages = [data_symbol_utils.symbol_reference('symbol_name')]
        self._check_source_and_exe_variants__failing_assertions(
            ParserThatGives(
                instruction_embryo_that__phase_agnostic(
                    symbol_usages=do_return(unexpected_symbol_usages))),
            Arrangement.phase_agnostic(),
            Expectation.phase_agnostic(),
        )

    def test_that_fails_due_to_missing_symbol_reference(self):
        symbol_usages_of_instruction = []
        self._check_source_and_exe_variants__failing_assertions(
            ParserThatGives(
                instruction_embryo_that__phase_agnostic(
                    symbol_usages=do_return(symbol_usages_of_instruction))),
            Arrangement.phase_agnostic(),
            Expectation.phase_agnostic(
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

        self._check_source_and_exe_variants(
            ParserThatGives(
                instruction_embryo_that__phase_agnostic(
                    validate_pre_sds_initial_action=assertion_for_validation,
                    validate_post_sds_initial_action=assertion_for_validation,
                    main_initial_action=assertion_for_main,
                )),
            Arrangement.phase_agnostic(symbols=symbol_table_of_arrangement),
            MultiSourceExpectation.phase_agnostic(),
        )

    def test_symbols_populated_by_main_SHOULD_appear_in_symbol_table_given_to_symbols_after_main(self):
        symbol = StringConstantSymbolContext('symbol_name', 'const string')

        def add_symbol_to_symbol_table(environment: InstructionEnvironmentForPostSdsStep, *args):
            environment.symbols.put(symbol.name,
                                    symbol.symbol_table_container)

        self._check_source_and_exe_variants(
            ParserThatGives(
                instruction_embryo_that__phase_agnostic(
                    main_initial_action=add_symbol_to_symbol_table)),
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                symbols_after_main=asrt.sub_component('names_set',
                                                      SymbolTable.names_set.fget,
                                                      asrt.equals({symbol.name}))),
        )


class TestHdsDirHandling(TestCaseBase):
    def test_fail_due_to_side_effects_on_hds(self):
        self._check_source_and_exe_variants__failing_assertions(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                side_effects_on_hds=f_asrt.dir_contains_at_least(
                    DirContents([File.empty('file-name.txt')]))
            ),
        )

    def test_arrangement_and_expectation_of_hds_dir_contents(self):
        home_dir_contents = DirContents([File.empty('file-name.txt')])
        self._check_source_and_exe_variants(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(
                hds_contents=hds_case_dir_contents(home_dir_contents)),
            MultiSourceExpectation.phase_agnostic(
                side_effects_on_hds=f_asrt.dir_contains_exactly(home_dir_contents)),
        )


class TestPopulate(TestCaseBase):
    def test_populate_non_hds(self):
        populated_dir_contents = DirContents([File.empty('non-hds-file.txt')])
        self._check_source_and_exe_variants(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(
                non_hds_contents=non_hds_populator.rel_option(RelNonHdsOptionType.REL_TMP,
                                                              populated_dir_contents)),
            MultiSourceExpectation.phase_agnostic(
                main_side_effects_on_sds=tmp_user_dir_contains_exactly(
                    populated_dir_contents)),
        )

    def test_populate_sds(self):
        populated_dir_contents = DirContents([File.empty('sds-file.txt')])
        self._check_source_and_exe_variants(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(
                sds_contents=sds_populator.contents_in(RelSdsOptionType.REL_RESULT,
                                                       populated_dir_contents)),
            MultiSourceExpectation.phase_agnostic(
                main_side_effects_on_sds=result_dir_contains_exactly(
                    populated_dir_contents)),
        )


class TestExecution(TestCaseBase):
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

        def recording_of(s: str) -> Callable[[InstructionEnvironmentForPostSdsStep,
                                              InstructionSettings,
                                              OsServices],
                                             None]:
            def ret_val(*args):
                recorder.append(s)

            return ret_val

        instruction_that_records_steps = instruction_embryo_that__phase_agnostic(
            validate_pre_sds_initial_action=recording_of(validate_pre_sds),
            validate_post_sds_initial_action=recording_of(validate_post_sds),
            main_initial_action=recording_of(main))
        self._check(
            ParserThatGives(instruction_that_records_steps),
            single_line_source(),
            Arrangement.phase_agnostic(),
            Expectation.phase_agnostic())

        self.assertEqual(expected_recordings,
                         recorder,
                         'step execution sequence')

    def test_successful_flow(self):
        self._check_source_and_exe_variants(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(),
        )

    def test_fail_due_to_unexpected_result_from__validate_pre_sds(self):
        self._check_source_and_exe_variants__failing_assertions(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                validation=ValidationAssertions.pre_sds_fails()
            ),
        )

    def test_fail_due_to_unexpected_result_from__validate_post_sds(self):
        self._check_source_and_exe_variants__failing_assertions(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                validation=ValidationAssertions.post_sds_fails()
            ),
        )

    def test_fail_due_to_unexpected_result__from_main(self):
        self._check_source_and_exe_variants__failing_assertions(
            ParserThatGives(instruction_embryo_that__phase_agnostic(main=do_return('actual'))),
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                main_result=asrt.equals('different-from-actual'),
            ),
        )

    def test_fail_due_to_unexpected_hard_error_exception(self):
        self._check_source_and_exe_variants__failing_assertions(
            ParserThatGives(instruction_embryo_that__phase_agnostic(
                main=do_raise(HardErrorException(new_single_string_text_for_test('hard error message'))))
            ),
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                main_result=asrt.anything_goes()
            ),
        )

    def test_succeed_due_to_expected_hard_error_exception(self):
        self._check_source_and_exe_variants(
            ParserThatGives(instruction_embryo_that__phase_agnostic(
                main=do_raise(HardErrorException(new_single_string_text_for_test('hard error message'))))
            ),
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                main_raises_hard_error=True
            ),
        )

    def test_that_cwd_for_main__and__validate_post_setup_is_act_dir(self):
        instruction_that_raises_exception_if_unexpected_state = instruction_embryo_that__phase_agnostic(
            main_initial_action=utils.raise_test_error_if_cwd_is_not_act_root__env,
            validate_post_sds_initial_action=utils.raise_test_error_if_cwd_is_not_act_root__env,
        )
        self._check_source_and_exe_variants(
            ParserThatGives(instruction_that_raises_exception_if_unexpected_state),
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(),
        )


class TestMainMethodTypeOfPhaseAgnostic(TestCaseBase):
    def test_fail_if_instruction_is_not_phase_agnostic(self):
        with self.assertRaises(utils.TestError):
            self._check(
                ParserThatGives(instruction_embryo_that__setup_phase_aware()),
                single_line_source(),
                Arrangement.phase_agnostic(),
                Expectation.phase_agnostic(),
            )

    def test_fail_if_instruction_is_not_phase_agnostic__variants(self):
        self._check_source_and_exe_variants__failing_assertions(
            ParserThatGives(instruction_embryo_that__setup_phase_aware()),
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(),
        )

    def test_main_method_arguments(self):
        # ARRANGE #
        the_environ = MappingProxyType({'the_env_var': 'the env var value'})
        the_timeout = 69
        the_os_services = os_services_access.new_for_current_os()

        def main_action_that_checks_arguments(environment: InstructionEnvironmentForPostSdsStep,
                                              instruction_settings: InstructionSettings,
                                              os_services: OsServices):
            self.assertIs(os_services, the_os_services, 'os_services')

            self.assertEqual(the_environ, environment.proc_exe_settings.environ,
                             'proc exe settings/environment')

            self.assertEqual(the_timeout, environment.proc_exe_settings.timeout_in_seconds,
                             'proc exe settings/timeout')

            self.assertEqual(the_environ, instruction_settings.environ(),
                             'instruction settings/environment')

        # ACT & ASSERT #
        self._check_source_and_exe_variants(
            ParserThatGives(instruction_embryo_that__phase_agnostic(
                main_initial_action=main_action_that_checks_arguments
            )),
            Arrangement.phase_agnostic(
                process_execution_settings=ProcessExecutionSettings(the_timeout, the_environ),
                os_services=the_os_services,
            ),
            MultiSourceExpectation.phase_agnostic(),
        )


class TestMainMethodTypeOfSetupPhaseAware(TestCaseBase):
    def test_fail_if_instruction_is_not_setup_phase_aware(self):
        with self.assertRaises(utils.TestError):
            self._check(
                ParserThatGives(instruction_embryo_that__phase_agnostic()),
                single_line_source(),
                Arrangement.setup_phase_aware(),
                Expectation.setup_phase_aware(),
            )

    def test_fail_if_instruction_is_not_setup_phase_aware__source_variant(self):
        self._check_source_and_exe_variants__failing_assertions(
            ParserThatGives(instruction_embryo_that__phase_agnostic()),
            Arrangement.setup_phase_aware(),
            MultiSourceExpectation.setup_phase_aware(),
        )

    def test_fail_if_instruction_is_not_phase_agnostic__multi(self):
        with self.assertRaises(utils.TestError):
            checker = sut.Checker(ParserThatGives(instruction_embryo_that__phase_agnostic()))
            checker.check__abs_stx__multi__std_layouts_and_source_variants(
                self.tc,
                CustomAbsStx.empty(),
                symbol_usages=asrt.is_empty_sequence,
                execution_cases=[
                    NArrEx(
                        'the one and only case',
                        Arrangement.setup_phase_aware(),
                        ExecutionExpectation.setup_phase_aware(),
                    )
                ]
            )

    def test_main_method_arguments(self):
        # ARRANGE #
        the_environ = MappingProxyType({'an_env_var': 'an env var value'})

        the_timeout = 72
        the_os_services = os_services_access.new_for_current_os()

        setup_settings_cases = [
            NArrEx(
                'none',
                None,
                asrt.is_none,
            ),
            NArrEx(
                'not none',
                SetupSettingsArr(the_environ),
                _IsSettingsBuilderWoStdinWEnviron(asrt.equals(the_environ)),
            ),
        ]

        for setup_settings_case in setup_settings_cases:
            def main_action_that_checks_arguments(environment: InstructionEnvironmentForPostSdsStep,
                                                  instruction_settings: InstructionSettings,
                                                  settings_builder: Optional[SetupSettingsBuilder],
                                                  os_services: OsServices):
                self.assertIs(os_services, the_os_services, 'os_services')

                self.assertEqual(the_environ, environment.proc_exe_settings.environ,
                                 'proc exe settings/environment')

                self.assertEqual(the_timeout, environment.proc_exe_settings.timeout_in_seconds,
                                 'proc exe settings/timeout')

                self.assertEqual(the_environ, instruction_settings.environ(),
                                 'instruction settings/environment')

                setup_settings_case.expectation.apply_with_message(self, settings_builder,
                                                                   'setup settings passed to main')

            # ACT & ASSERT #
            self._check_source_and_exe_variants(
                ParserThatGives(instruction_embryo_that__setup_phase_aware(
                    main_initial_action=main_action_that_checks_arguments
                )),
                Arrangement.setup_phase_aware(
                    process_execution_settings=ProcessExecutionSettings(the_timeout, the_environ),
                    setup_settings=setup_settings_case.arrangement,
                    os_services=the_os_services,
                ),
                MultiSourceExpectation.setup_phase_aware(
                    setup_settings=asrt.anything_goes(),
                ),
            )

    def test_assertion_on_setup_settings(self):
        # ARRANGE #
        environ__actual = {'actual_var': 'actual value'}
        environ__expected = {}
        the_setup_settings = SetupSettingsArr(environ=environ__actual)

        setup_settings_cases = [
            NArrEx(
                'none',
                None,
                asrt.is_not_none,
            ),
            NArrEx(
                'not none',
                the_setup_settings,
                asrt_settings_builder.matches(
                    environ=asrt.equals(environ__expected),
                    stdin=asrt.is_none,
                ),
            ),
        ]

        for setup_settings_case in setup_settings_cases:
            # ACT & ASSERT #
            self._check_source_and_exe_variants__failing_assertions(
                ParserThatGives(instruction_embryo_that__setup_phase_aware()),
                Arrangement.setup_phase_aware(
                    setup_settings=setup_settings_case.arrangement,
                ),
                MultiSourceExpectation.setup_phase_aware(
                    setup_settings=setup_settings_case.expectation,
                ),
                setup_settings=setup_settings_case.name,
            )


class TestSideEffectsOfMain(TestCaseBase):
    def test_fail_due_to_fail_of_side_effects_on_files(self):
        self._check_source_and_exe_variants__failing_assertions(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                main_side_effects_on_sds=act_dir_contains_exactly(
                    DirContents([File.empty('non-existing-file.txt')]))
            ),
        )

    def test_fail_due_to_side_effects_check(self):
        self._check_source_and_exe_variants__failing_assertions(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                side_effects_on_tcds=asrt.not_(asrt.is_instance(TestCaseDs))
            ),
        )

    def test_populate_environ(self):
        default_from_default_getter = {'default': 'value of default'}
        default_environs = {'in_environs': 'value of var in environs'}

        def default_environ_getter() -> Dict[str, str]:
            return dict(default_from_default_getter)

        self._check_source_and_exe_variants(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(
                default_environ_getter=default_environ_getter,
                process_execution_settings=ProcessExecutionSettings.from_non_immutable(environ=default_environs),
            ),
            MultiSourceExpectation.phase_agnostic(
                instruction_settings=asrt_instr_settings.matches(
                    environ=asrt.equals(default_environs),
                    return_value_from_default_getter=asrt.equals(default_from_default_getter)
                ),
                proc_exe_settings=asrt_pes.matches(
                    environ=asrt.equals(default_environs)
                )
            ),
        )

    def test_fail_due_to_fail_of_side_effects_on_proc_exe_settings(self):
        self._check_source_and_exe_variants__failing_assertions(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                proc_exe_settings=asrt.not_(asrt.is_instance(ProcessExecutionSettings)),
            ),
        )

    def test_fail_due_to_fail_of_side_effects_on_instruction_settings(self):
        self._check_source_and_exe_variants__failing_assertions(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                instruction_settings=asrt.not_(asrt.is_instance(InstructionSettings)),
            ),
        )

    def test_fail_due_to_assertion_on_instruction_environment(self):
        self._check_source_and_exe_variants__failing_assertions(
            PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION,
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                instruction_environment=asrt.fail('unconditional failure')
            ),
        )

    def test_manipulation_of_environment_variables(self):
        env_var = NameAndValue('env_var_name', 'env var value')
        expected_environment_variables = {
            env_var.name: env_var.value
        }
        instruction = InstructionThatSetsEnvironmentVariable(env_var)

        self._check_source_and_exe_variants(
            ParserThatGives(instruction),
            Arrangement.phase_agnostic(
                process_execution_settings=ProcessExecutionSettings.with_environ({})
            ),
            MultiSourceExpectation.phase_agnostic(
                main_side_effect_on_environment_variables=asrt.equals(expected_environment_variables)
            ),
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

        self._check_source_and_exe_variants(
            ParserThatGives(instruction),
            Arrangement.phase_agnostic(
                process_execution_settings=ProcessExecutionSettings.with_environ(environ_of_arrangement)),
            MultiSourceExpectation.phase_agnostic(
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


class ParserThatConsumesCurrentLine(Generic[T], embryo.InstructionEmbryoParser[T]):
    def __init__(self, parser_that_do_not_consume_any_source: embryo.InstructionEmbryoParser[T]):
        self.parser_that_do_not_consume_any_source = parser_that_do_not_consume_any_source

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> embryo.InstructionEmbryo[T]:
        ret_val = self.parser_that_do_not_consume_any_source.parse(fs_location_info, source)
        source.consume_current_line()
        return ret_val


PARSER_THAT_GIVES_SUCCESSFUL_INSTRUCTION = ParserThatGives(instruction_embryo_that__phase_agnostic())


class InstructionThatSetsEnvironmentVariable(embryo.PhaseAgnosticInstructionEmbryo[None]):
    def __init__(self, variable: NameAndValue):
        self.variable = variable

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             ):
        variable = self.variable
        settings.environ()[variable.name] = variable.value


class _IsSettingsBuilderWoStdinWEnviron(AssertionBase[SetupSettingsBuilder]):
    def __init__(self, environ: Assertion[Optional[Dict[str, str]]]):
        self._environ = environ

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: MessageBuilder,
               ):
        put.assertIsInstance(value, SetupSettingsBuilder,
                             message_builder.apply('object should be instance of ' + str(type(SetupSettingsBuilder)))
                             )
        assert isinstance(value, SetupSettingsBuilder)  # Type info for IDE
        put.assertIsNone(value.stdin, message_builder.apply('stdin'))
        self._environ.apply(put, value.environ, message_builder.for_sub_component('environ'))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
