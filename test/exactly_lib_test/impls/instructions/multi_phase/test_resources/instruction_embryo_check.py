import unittest
from typing import Optional
from typing import Sequence, Dict, Generic

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.execution import phase_step
from exactly_lib.impls.instructions.multi_phase.utils.instruction_embryo import InstructionEmbryoParser, \
    InstructionEmbryo, T, MainMethodVisitor, RET, PhaseAgnosticMainMethod, SetupPhaseAwareMainMethod
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.util import functional
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions
from exactly_lib_test.impls.instructions.multi_phase.test_resources.embryo_arr_exp import \
    InstructionApplicationEnvironment, SetupSettingsArr, Arrangement, MainMethodType, ExecutionExpectation, \
    MultiSourceExpectation, Expectation
from exactly_lib_test.impls.types.parse.test_resources import \
    single_line_source_instruction_utils as equivalent_source_variants
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__consume_last_line_2
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case.test_resources import instruction_settings as _instruction_settings
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_case.test_resources.settings_builder_assertions import SettingsBuilderAssertionModel
from exactly_lib_test.test_resources.source import abs_stx_utils
from exactly_lib_test.test_resources.source import layout
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.layout import LayoutSpec
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.test_utils import NArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.util.test_resources import symbol_table_assertions as asrt_sym_tbl


class TestCaseBase(Generic[T], unittest.TestCase):
    def _check(self,
               parser: InstructionEmbryoParser[T],
               source: ParseSource,
               arrangement: Arrangement,
               expectation: Expectation[T]):
        check(self,
              parser,
              source,
              arrangement,
              expectation)


def check(put: unittest.TestCase,
          parser: InstructionEmbryoParser[T],
          source: ParseSource,
          arrangement: Arrangement,
          expectation: Expectation[T]):
    _ParseAndExecutionChecker(put, arrangement, expectation).execute(parser, source)


class Checker(Generic[T]):
    def __init__(self, parser: InstructionEmbryoParser[T]):
        self.parser = parser

    def check(self,
              put: unittest.TestCase,
              source: ParseSource,
              arrangement: Arrangement,
              expectation: Expectation[T],
              ):
        _ParseAndExecutionChecker(put, arrangement, expectation).execute(self.parser, source)

    def check__abs_stx(self,
                       put: unittest.TestCase,
                       source: AbstractSyntax,
                       arrangement: Arrangement,
                       expectation_: Expectation[T],
                       layout: LayoutSpec = LayoutSpec.of_default(),
                       ):
        source = remaining_source(source.tokenization().layout(layout))
        _ParseAndExecutionChecker(put, arrangement, expectation_).execute(self.parser, source)

    def check__abs_stx__std_layouts_and_source_variants(
            self,
            put: unittest.TestCase,
            source: AbstractSyntax,
            arrangement: Arrangement,
            expectation: MultiSourceExpectation[T],
            **sub_test_identifiers
    ):
        self.check__abs_stx__layout_and_source_variants(
            put,
            source,
            arrangement,
            expectation,
            layout.STANDARD_LAYOUT_SPECS,
            **sub_test_identifiers
        )

    def check__abs_stx__multi__std_layouts_and_source_variants(
            self,
            put: unittest.TestCase,
            source: AbstractSyntax,
            symbol_usages: Assertion[Sequence[SymbolUsage]],
            execution_cases: Sequence[NArrEx[Arrangement, ExecutionExpectation[T]]],
            **sub_test_identifiers
    ):
        """This method cannot be used for instructions who's main populate the symbol table
        (ie instructions that define symbols).
        """
        for source_formatting_case in abs_stx_utils.formatting_cases(source):
            source_str = source_formatting_case.value
            for source_case in equivalent_source_variants.consume_last_line__s__nsc(source_str):
                parse_checker = _ParseChecker(put,
                                              symbol_usages,
                                              source_case.expectation)
                instruction = self.parser.parse(ARBITRARY_FS_LOCATION_INFO, source_case.source)
                for arr_exp_case in execution_cases:
                    symbol_table_after_main = asrt_sym_tbl.assert_symbol_table_keys_equals(
                        arr_exp_case.arrangement.symbols.names_set
                    )
                    with put.subTest(_source_variant=source_case.name,
                                     _source_formatting=source_formatting_case.name,
                                     _execution_case=arr_exp_case.name,
                                     **sub_test_identifiers):
                        parse_checker.check(instruction, source_case.source)
                        # ^ Checks same source and sym-refs multiple times.
                        # Bad, but put here to make the check part of the same sub-test.

                        executor = _ExecutionChecker(
                            put,
                            arr_exp_case.arrangement,
                            symbol_usages,
                            symbol_table_after_main,
                            arr_exp_case.expectation)

                        executor.check(instruction)

    def check__abs_stx__layout_and_source_variants(
            self,
            put: unittest.TestCase,
            source: AbstractSyntax,
            arrangement: Arrangement,
            expectation: MultiSourceExpectation[T],
            layouts: Sequence[NameAndValue[LayoutSpec]] = layout.STANDARD_LAYOUT_SPECS,
            **sub_test_identifiers
    ):
        for source_formatting_case in abs_stx_utils.formatting_cases(source, layouts):
            with put.subTest(layout=source_formatting_case.name,
                             **sub_test_identifiers):
                self.check__w_source_variants(put, source_formatting_case.value, arrangement, expectation)

    def check__w_source_variants(self,
                                 put: unittest.TestCase,
                                 source: str,
                                 arrangement: Arrangement,
                                 expectation: MultiSourceExpectation[T],
                                 ):
        for parse_source, source_asrt in equivalent_source_variants__with_source_check__consume_last_line_2(source):
            with put.subTest(remaining_source=parse_source.remaining_source):
                executor = _ParseAndExecutionChecker(put, arrangement, expectation.as_w_source(source_asrt),
                                                     source_asrt)
                executor.execute(self.parser, parse_source)


class _ParseAndExecutionChecker(Generic[T]):
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: Arrangement,
                 expectation: Expectation[T],
                 extra_source_expectation: Assertion[ParseSource] = asrt.anything_goes(),
                 ):
        self.put = put
        self.arrangement = arrangement
        self.expectation = expectation
        self.message_builder = asrt.MessageBuilder()
        self.extra_source_expectation = extra_source_expectation
        self.parse_checker = _ParseChecker(self.put,
                                           expectation.symbol_usages,
                                           expectation.source,
                                           extra_source_expectation)
        self.execution_checker = _ExecutionChecker(self.put,
                                                   arrangement,
                                                   expectation.symbol_usages,
                                                   expectation.symbols_after_main,
                                                   expectation)

    def execute(self,
                parser: InstructionEmbryoParser,
                source: ParseSource):
        instruction = parser.parse(self.arrangement.fs_location_info, source)
        instruction = self.parse_checker.check(instruction, source)
        self.execution_checker.check(instruction)


class _ParseChecker(Generic[T]):
    def __init__(self,
                 put: unittest.TestCase,
                 symbol_usages_after_parse: Assertion[Sequence[SymbolUsage]],
                 source_expectation: Assertion[ParseSource],
                 extra_source_expectation: Assertion[ParseSource] = asrt.anything_goes(),
                 ):
        self.put = put
        self.symbol_usages_after_parse = symbol_usages_after_parse
        self.source_expectation = source_expectation
        self.extra_source_expectation = extra_source_expectation

    def parse_and_check(self,
                        parser: InstructionEmbryoParser,
                        source: ParseSource,
                        fs_location_info: FileSystemLocationInfo = ARBITRARY_FS_LOCATION_INFO,
                        ) -> InstructionEmbryo[T]:
        instruction = parser.parse(fs_location_info, source)
        return self.check(
            instruction,
            source,
        )

    def check(self,
              instruction,
              source_after_parse: ParseSource,
              ) -> InstructionEmbryo[T]:
        self.source_expectation.apply_with_message(self.put, source_after_parse, 'source')
        self.extra_source_expectation.apply_with_message(self.put, source_after_parse, 'source')

        asrt.is_instance(InstructionEmbryo).apply_with_message(self.put, instruction,
                                                               'Instruction class')

        assert isinstance(instruction, InstructionEmbryo)
        self.symbol_usages_after_parse.apply_with_message(self.put,
                                                          instruction.symbol_usages,
                                                          'symbol-usages after parse')

        return instruction


class _ExecutionChecker(Generic[T]):
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: Arrangement,
                 symbols_after_parse: Assertion[Sequence[SymbolUsage]],
                 symbols_after_main: Assertion[SymbolTable],
                 expectation: ExecutionExpectation[T],
                 ):
        self.put = put
        self.arrangement = arrangement
        self.symbols_after_parse = symbols_after_parse
        self.symbols_after_main = symbols_after_main
        self.expectation = expectation
        self.message_builder = asrt.MessageBuilder()

    def check(self, instruction: InstructionEmbryo[T]):
        with tcds_with_act_as_curr_dir(
                pre_contents_population_action=self.arrangement.pre_contents_population_action,
                hds_contents=self.arrangement.hds_contents,
                sds_contents=self.arrangement.sds_contents,
                non_hds_contents=self.arrangement.non_hds_contents,
                tcds_contents=self.arrangement.tcds_contents,
                symbols=self.arrangement.symbols) as path_resolving_environment:
            tcds = path_resolving_environment.tcds
            self.arrangement.post_sds_population_action.apply(path_resolving_environment)

            environment_builder = InstructionEnvironmentPostSdsBuilder.new_tcds(
                tcds,
                self.arrangement.symbols,
                ProcessExecutionSettings.from_non_immutable(
                    timeout_in_seconds=self.arrangement.process_execution_settings.timeout_in_seconds,
                    environ=self.arrangement.process_execution_settings.environ,
                ),
            )

            environment = environment_builder.build_pre_sds()
            validate_result = self._execute_validate_pre_sds(environment, instruction)
            self.symbols_after_parse.apply_with_message(self.put,
                                                        instruction.symbol_usages,
                                                        'symbol-usages after ' +
                                                        phase_step.STEP__VALIDATE_PRE_SDS)
            if validate_result is not None:
                return
            environment = environment_builder.build_post_sds()
            validate_result = self._execute_validate_post_setup(environment, instruction)
            self.symbols_after_parse.apply_with_message(self.put,
                                                        instruction.symbol_usages,
                                                        'symbol-usages after ' +
                                                        phase_step.STEP__VALIDATE_POST_SETUP)
            if validate_result is not None:
                return

            instr_settings = _instruction_settings.from_proc_exe_settings(self.arrangement.process_execution_settings,
                                                                          self.arrangement.default_environ_getter)
            setup_settings = self._setup_settings_from_arrangement()

            result_of_main = self._execute_main(environment, instr_settings, setup_settings, instruction)

            self.expectation.main_side_effect_on_environment_variables.apply_with_message(
                self.put,
                instr_settings.environ(),
                'main side effects on environment variables')
            self.symbols_after_parse.apply_with_message(self.put,
                                                        instruction.symbol_usages,
                                                        'symbol-usages after ' +
                                                        phase_step.STEP__MAIN)
            self.symbols_after_main.apply_with_message(self.put,
                                                       environment.symbols,
                                                       'symbols in symbol table after ' +
                                                       phase_step.STEP__MAIN)
            self.expectation.proc_exe_settings.apply_with_message(self.put, environment.proc_exe_settings,
                                                                  'proc exe settings')
            self.expectation.instruction_settings.apply_with_message(self.put, instr_settings,
                                                                     'instruction settings')
            self.expectation.setup_settings.apply_with_message(self.put,
                                                               self._setup_settings_assertion_model(
                                                                   setup_settings,
                                                                   environment,
                                                               ),
                                                               'setup settings')
            self.expectation.main_side_effects_on_sds.apply_with_message(self.put, tcds.sds,
                                                                         'side_effects_on_files')
            self.expectation.side_effects_on_tcds.apply_with_message(self.put, tcds,
                                                                     'side_effects_on_tcds')
            self.expectation.side_effects_on_hds.apply_with_message(self.put, tcds.hds.case_dir,
                                                                    'side_effects_on_home')

            application_environment = InstructionApplicationEnvironment(
                self.arrangement.os_services,
                environment,
                instr_settings,
            )
            self.expectation.instruction_application_environment.apply_with_message(self.put,
                                                                                    application_environment,
                                                                                    'assertion_on_environment')
            self.expectation.main_result.apply_with_message(self.put, result_of_main,
                                                            'result of main (wo access to TCDS)')

    def _execute_validate_pre_sds(
            self,
            environment: InstructionEnvironmentForPreSdsStep,
            instruction: InstructionEmbryo[T]) -> Optional[TextRenderer]:
        result = instruction.validator.validate_pre_sds_if_applicable(environment.path_resolving_environment)
        self.expectation.validation.pre_sds.apply_with_message(self.put, result,
                                                               'validation_pre_sds')
        return result

    def _execute_validate_post_setup(
            self,
            environment: InstructionEnvironmentForPostSdsStep,
            instruction: InstructionEmbryo[T]) -> Optional[TextRenderer]:
        result = instruction.validator.validate_post_sds_if_applicable(environment.path_resolving_environment)
        self.expectation.validation.post_sds.apply_with_message(self.put, result,
                                                                'validation_post_sds')
        return result

    def _execute_main(self,
                      environment: InstructionEnvironmentForPostSdsStep,
                      settings: InstructionSettings,
                      setup_settings: Optional[SetupSettingsBuilder],
                      instruction: InstructionEmbryo[T]) -> T:
        executor = _MainMethodExecutor(self.put,
                                       self.expectation.main_method_type,
                                       environment,
                                       settings,
                                       self.arrangement.os_services,
                                       setup_settings)
        try:
            result = instruction.main_method().accept(executor)
        except HardErrorException as ex:
            if self.expectation.main_raises_hard_error:
                text_doc_assertions.assert_is_valid_text_renderer(self.put, ex.error)
                return
            else:
                self.put.fail('unexpected {} from main'.format(HardErrorException))
                return

        if self.expectation.main_raises_hard_error:
            self.put.fail('main does not raise ' + str(HardErrorException))

        return result

    def _setup_settings_from_arrangement(self) -> Optional[SetupSettingsBuilder]:
        return functional.map_optional(SetupSettingsArr.as_settings_builder,
                                       self.arrangement.setup_settings)

    def _setup_settings_assertion_model(self,
                                        settings_builder: Optional[SetupSettingsBuilder],
                                        environment: InstructionEnvironmentForPostSdsStep,
                                        ) -> Optional[SettingsBuilderAssertionModel]:
        return (
            None
            if settings_builder is None
            else SettingsBuilderAssertionModel(
                settings_builder,
                environment,
                self.arrangement.os_services,
            )

        )


class _MainMethodExecutor(Generic[RET], MainMethodVisitor[RET, RET]):
    def __init__(self,
                 put: unittest.TestCase,
                 expected_main_method_type: MainMethodType,
                 environment: InstructionEnvironmentForPostSdsStep,
                 settings: InstructionSettings,
                 os_services: OsServices,
                 setup_settings: Optional[SetupSettingsBuilder],
                 ):
        self.put = put
        self.expected_main_method_type = expected_main_method_type
        self._environment = environment
        self._settings = settings
        self._os_services = os_services
        self._setup_settings = setup_settings

    def visit_phase_agnostic(self, main_method: PhaseAgnosticMainMethod[T]) -> RET:
        if self.expected_main_method_type is not MainMethodType.PHASE_AGNOSTIC:
            self.put.fail('Unexpected main method type: ' + str(self.expected_main_method_type))

        return main_method.main(self._environment, self._settings, self._os_services)

    def visit_setup_phase_aware(self, main_method: SetupPhaseAwareMainMethod[T]) -> RET:
        if self.expected_main_method_type is not MainMethodType.SETUP_PHASE_AWARE:
            self.put.fail('Unexpected main method type: ' + str(self.expected_main_method_type))

        return main_method.main(self._environment, self._settings, self._setup_settings, self._os_services)


def _initial_environment_variables_dict(arrangement: Arrangement) -> Dict[str, str]:
    return functional.map_optional(dict, arrangement.process_execution_settings.environ)
