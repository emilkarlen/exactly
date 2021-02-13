import enum
import pathlib
import unittest
from typing import Optional
from typing import Sequence, Dict, Generic

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.execution import phase_step
from exactly_lib.impls.instructions.multi_phase.utils.instruction_embryo import InstructionEmbryoParser, \
    InstructionEmbryo, T, MainMethodVisitor, RET, PhaseAgnosticMainMethod, SetupPhaseAwareMainMethod
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import DefaultEnvironGetter
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.util import functional
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.util.symbol_table import symbol_table_from_none_or_value
from exactly_lib_test.common.test_resources import text_doc_assertions
from exactly_lib_test.execution.test_resources.predefined_properties import get_empty_environ
from exactly_lib_test.impls.test_resources.validation import validation as validation_utils
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions, ValidationResultAssertion
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__consume_last_line_2
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.tcfs.test_resources import non_hds_populator, hds_populators, \
    tcds_populators, sds_populator
from exactly_lib_test.test_case.test_resources import instruction_settings as _instruction_settings
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_resources.source import layout
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.layout import LayoutSpec
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


class PostActionCheck:
    def apply(self,
              put: unittest.TestCase,
              tcds: TestCaseDs):
        pass


class InstructionApplicationEnvironment:
    def __init__(self,
                 os_service: OsServices,
                 instruction: InstructionEnvironmentForPostSdsStep,
                 settings: InstructionSettings,
                 ):
        self._os_service = os_service
        self._instruction = instruction
        self._settings = settings

    @property
    def os_service(self) -> OsServices:
        return self._os_service

    @property
    def instruction(self) -> InstructionEnvironmentForPostSdsStep:
        return self._instruction

    @property
    def settings(self) -> InstructionSettings:
        return self._settings


class MainMethodType(enum.Enum):
    PHASE_AGNOSTIC = 1
    SETUP_PHASE_AWARE = 2


class Arrangement(ArrangementWithSds):
    def __init__(self,
                 pre_contents_population_action: TcdsAction = TcdsAction(),
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
                 non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                 tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                 os_services: OsServices = os_services_access.new_for_current_os(),
                 process_execution_settings: ProcessExecutionSettings = proc_exe_env_for_test(),
                 default_environ_getter: DefaultEnvironGetter = get_empty_environ,
                 post_sds_population_action: TcdsAction = TcdsAction(),
                 symbols: SymbolTable = None,
                 fs_location_info: FileSystemLocationInfo = ARBITRARY_FS_LOCATION_INFO,
                 setup_settings: Optional[SetupSettingsBuilder] = None,
                 ):
        super().__init__(hds_contents=hds_contents,
                         process_execution_settings=process_execution_settings,
                         default_environ_getter=default_environ_getter)
        self.pre_contents_population_action = pre_contents_population_action
        self.sds_contents = sds_contents
        self.non_hds_contents = non_hds_contents
        self.tcds_contents = tcds_contents
        self.post_sds_population_action = post_sds_population_action
        self.os_services = os_services
        self.process_execution_settings = process_execution_settings
        self.setup_settings = setup_settings
        self.symbols = symbol_table_from_none_or_value(symbols)
        self.fs_location_info = fs_location_info

    @staticmethod
    def phase_agnostic(
            pre_contents_population_action: TcdsAction = TcdsAction(),
            hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
            sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
            non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
            tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
            os_services: OsServices = os_services_access.new_for_current_os(),
            process_execution_settings: ProcessExecutionSettings = proc_exe_env_for_test(),
            default_environ_getter: DefaultEnvironGetter = get_empty_environ,
            post_sds_population_action: TcdsAction = TcdsAction(),
            symbols: SymbolTable = None,
            fs_location_info: FileSystemLocationInfo = ARBITRARY_FS_LOCATION_INFO,
    ) -> 'Arrangement':
        return Arrangement(
            pre_contents_population_action,
            hds_contents,
            sds_contents,
            non_hds_contents,
            tcds_contents,
            os_services,
            process_execution_settings,
            default_environ_getter,
            post_sds_population_action,
            symbols,
            fs_location_info,
            None,
        )

    @staticmethod
    def setup_phase_aware(
            pre_contents_population_action: TcdsAction = TcdsAction(),
            hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
            sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
            non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
            tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
            setup_settings: Optional[SetupSettingsBuilder] = None,
            os_services: OsServices = os_services_access.new_for_current_os(),
            process_execution_settings: ProcessExecutionSettings = proc_exe_env_for_test(),
            default_environ_getter: DefaultEnvironGetter = get_empty_environ,
            post_sds_population_action: TcdsAction = TcdsAction(),
            symbols: SymbolTable = None,
            fs_location_info: FileSystemLocationInfo = ARBITRARY_FS_LOCATION_INFO,
    ) -> 'Arrangement':
        return Arrangement(
            pre_contents_population_action,
            hds_contents,
            sds_contents,
            non_hds_contents,
            tcds_contents,
            os_services,
            process_execution_settings,
            default_environ_getter,
            post_sds_population_action,
            symbols,
            fs_location_info,
            setup_settings,
        )


class Expectation(Generic[T]):
    def __init__(self,
                 main_method_type: MainMethodType,
                 validation_pre_sds: ValidationResultAssertion = asrt.is_none,
                 validation_post_sds: ValidationResultAssertion = asrt.is_none,
                 main_result: Assertion[T] = asrt.anything_goes(),
                 main_raises_hard_error: bool = False,
                 symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                 symbols_after_main: Assertion[SymbolTable] = asrt.anything_goes(),
                 main_side_effects_on_sds: Assertion[SandboxDs] = asrt.anything_goes(),
                 side_effects_on_tcds: Assertion[TestCaseDs] = asrt.anything_goes(),
                 side_effects_on_hds: Assertion[pathlib.Path] = asrt.anything_goes(),
                 source: Assertion[ParseSource] = asrt.anything_goes(),
                 main_side_effect_on_environment_variables: Assertion[Dict[str, str]] = asrt.anything_goes(),
                 proc_exe_settings: Assertion[ProcessExecutionSettings]
                 = asrt.is_instance(ProcessExecutionSettings),
                 instruction_settings: Assertion[InstructionSettings]
                 = asrt.is_instance(InstructionSettings),
                 assertion_on_instruction_environment:
                 Assertion[InstructionApplicationEnvironment] = asrt.anything_goes(),
                 setup_settings: Assertion[Optional[SetupSettingsBuilder]] = asrt.is_none,
                 ):
        self.main_method_type = main_method_type
        self.validation_pre_sds = validation_pre_sds
        self.validation_post_sds = validation_post_sds
        self.main_result = main_result
        self.main_raises_hard_error = main_raises_hard_error
        self.instruction_settings = instruction_settings
        self.proc_exe_settings = proc_exe_settings
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.side_effects_on_tcds = side_effects_on_tcds
        self.side_effects_on_hds = side_effects_on_hds
        self.source = source
        self.symbol_usages = symbol_usages
        self.symbols_after_main = symbols_after_main
        self.main_side_effect_on_environment_variables = main_side_effect_on_environment_variables
        self.instruction_application_environment = assertion_on_instruction_environment
        self.setup_settings = setup_settings

    @staticmethod
    def phase_agnostic(
            validation_pre_sds: ValidationResultAssertion = asrt.is_none,
            validation_post_sds: ValidationResultAssertion = asrt.is_none,
            main_result: Assertion[T] = asrt.anything_goes(),
            main_raises_hard_error: bool = False,
            symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
            symbols_after_main: Assertion[SymbolTable] = asrt.anything_goes(),
            main_side_effects_on_sds: Assertion[SandboxDs] = asrt.anything_goes(),
            side_effects_on_tcds: Assertion[TestCaseDs] = asrt.anything_goes(),
            side_effects_on_hds: Assertion[pathlib.Path] = asrt.anything_goes(),
            source: Assertion[ParseSource] = asrt.anything_goes(),
            main_side_effect_on_environment_variables: Assertion[Dict[str, str]] = asrt.anything_goes(),
            proc_exe_settings: Assertion[ProcessExecutionSettings]
            = asrt.is_instance(ProcessExecutionSettings),
            instruction_settings: Assertion[InstructionSettings]
            = asrt.is_instance(InstructionSettings),
            instruction_environment: Assertion[InstructionApplicationEnvironment] = asrt.anything_goes(),
    ) -> 'Expectation[T]':
        return Expectation(
            MainMethodType.PHASE_AGNOSTIC,
            validation_pre_sds,
            validation_post_sds,
            main_result,
            main_raises_hard_error,
            symbol_usages,
            symbols_after_main,
            main_side_effects_on_sds,
            side_effects_on_tcds,
            side_effects_on_hds,
            source,
            main_side_effect_on_environment_variables,
            proc_exe_settings,
            instruction_settings,
            instruction_environment,
            asrt.is_none,
        )

    @staticmethod
    def phase_agnostic_2(
            validation: ValidationAssertions = validation_utils.ValidationAssertions.all_passes(),
            main_result: Assertion[T] = asrt.anything_goes(),
            main_raises_hard_error: bool = False,
            symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
            symbols_after_main: Assertion[SymbolTable] = asrt.anything_goes(),
            main_side_effects_on_sds: Assertion[SandboxDs] = asrt.anything_goes(),
            side_effects_on_tcds: Assertion[TestCaseDs] = asrt.anything_goes(),
            side_effects_on_home: Assertion[pathlib.Path] = asrt.anything_goes(),
            source: Assertion[ParseSource] = asrt.anything_goes(),
            main_side_effect_on_environment_variables: Assertion[Dict[str, str]] = asrt.anything_goes(),
            proc_exe_settings: Assertion[ProcessExecutionSettings]
            = asrt.is_instance(ProcessExecutionSettings),
            instruction_settings: Assertion[InstructionSettings]
            = asrt.is_instance(InstructionSettings),
            assertion_on_instruction_environment:
            Assertion[InstructionApplicationEnvironment] = asrt.anything_goes(),
    ) -> 'Expectation[T]':
        return Expectation(
            MainMethodType.PHASE_AGNOSTIC,
            validation_pre_sds=validation.pre_sds,
            validation_post_sds=validation.post_sds,
            main_result=main_result,
            main_raises_hard_error=main_raises_hard_error,
            symbol_usages=symbol_usages,
            symbols_after_main=symbols_after_main,
            main_side_effects_on_sds=main_side_effects_on_sds,
            side_effects_on_tcds=side_effects_on_tcds,
            side_effects_on_hds=side_effects_on_home,
            source=source,
            proc_exe_settings=proc_exe_settings,
            instruction_settings=instruction_settings,
            main_side_effect_on_environment_variables=main_side_effect_on_environment_variables,
            assertion_on_instruction_environment=assertion_on_instruction_environment,
            setup_settings=asrt.is_none,
        )

    @staticmethod
    def setup_phase_aware(
            validation_pre_sds: ValidationResultAssertion = asrt.is_none,
            validation_post_sds: ValidationResultAssertion = asrt.is_none,
            main_result: Assertion[T] = asrt.anything_goes(),
            main_raises_hard_error: bool = False,
            symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
            symbols_after_main: Assertion[SymbolTable] = asrt.anything_goes(),
            main_side_effects_on_sds: Assertion[SandboxDs] = asrt.anything_goes(),
            side_effects_on_tcds: Assertion[TestCaseDs] = asrt.anything_goes(),
            side_effects_on_hds: Assertion[pathlib.Path] = asrt.anything_goes(),
            source: Assertion[ParseSource] = asrt.anything_goes(),
            main_side_effect_on_environment_variables: Assertion[Dict[str, str]] = asrt.anything_goes(),
            proc_exe_settings: Assertion[ProcessExecutionSettings]
            = asrt.is_instance(ProcessExecutionSettings),
            instruction_settings: Assertion[InstructionSettings]
            = asrt.is_instance(InstructionSettings),
            instruction_environment: Assertion[InstructionApplicationEnvironment] = asrt.anything_goes(),
            setup_settings: Assertion[Optional[SetupSettingsBuilder]] = asrt.is_none,
    ) -> 'Expectation[T]':
        return Expectation(
            MainMethodType.SETUP_PHASE_AWARE,
            validation_pre_sds,
            validation_post_sds,
            main_result,
            main_raises_hard_error,
            symbol_usages,
            symbols_after_main,
            main_side_effects_on_sds,
            side_effects_on_tcds,
            side_effects_on_hds,
            source,
            main_side_effect_on_environment_variables,
            proc_exe_settings,
            instruction_settings,
            instruction_environment,
            setup_settings,
        )


class MultiSourceExpectation(Generic[T]):
    def __init__(self,
                 main_method_type: MainMethodType,
                 validation: ValidationAssertions = ValidationAssertions.all_passes(),
                 main_result: Assertion[T] = asrt.anything_goes(),
                 main_raises_hard_error: bool = False,
                 symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                 symbols_after_main: Assertion[SymbolTable] = asrt.anything_goes(),
                 main_side_effects_on_sds: Assertion[SandboxDs] = asrt.anything_goes(),
                 side_effects_on_tcds: Assertion[TestCaseDs] = asrt.anything_goes(),
                 side_effects_on_hds: Assertion[pathlib.Path] = asrt.anything_goes(),
                 main_side_effect_on_environment_variables: Assertion[Dict[str, str]] = asrt.anything_goes(),
                 proc_exe_settings: Assertion[ProcessExecutionSettings]
                 = asrt.is_instance(ProcessExecutionSettings),
                 instruction_settings: Assertion[InstructionSettings]
                 = asrt.is_instance(InstructionSettings),
                 instruction_environment:
                 Assertion[InstructionApplicationEnvironment] = asrt.anything_goes(),
                 ):
        self.main_method_type = main_method_type
        self.validation = validation
        self.main_result = main_result
        self.main_raises_hard_error = main_raises_hard_error
        self.proc_exe_settings = proc_exe_settings
        self.instruction_settings = instruction_settings
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.side_effects_on_tcds = side_effects_on_tcds
        self.side_effects_on_hds = side_effects_on_hds
        self.symbol_usages = symbol_usages
        self.symbols_after_main = symbols_after_main
        self.main_side_effect_on_environment_variables = main_side_effect_on_environment_variables
        self.instruction_application_environment = instruction_environment

    @staticmethod
    def phase_agnostic(
            validation: ValidationAssertions = ValidationAssertions.all_passes(),
            main_result: Assertion[T] = asrt.anything_goes(),
            main_raises_hard_error: bool = False,
            symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
            symbols_after_main: Assertion[SymbolTable] = asrt.anything_goes(),
            main_side_effects_on_sds: Assertion[SandboxDs] = asrt.anything_goes(),
            side_effects_on_tcds: Assertion[TestCaseDs] = asrt.anything_goes(),
            side_effects_on_hds: Assertion[pathlib.Path] = asrt.anything_goes(),
            main_side_effect_on_environment_variables: Assertion[Dict[str, str]] = asrt.anything_goes(),
            proc_exe_settings: Assertion[ProcessExecutionSettings]
            = asrt.is_instance(ProcessExecutionSettings),
            instruction_settings: Assertion[InstructionSettings]
            = asrt.is_instance(InstructionSettings),
            instruction_environment:
            Assertion[InstructionApplicationEnvironment] = asrt.anything_goes(),
    ) -> 'MultiSourceExpectation[T]':
        return MultiSourceExpectation(
            MainMethodType.PHASE_AGNOSTIC,
            validation,
            main_result,
            main_raises_hard_error,
            symbol_usages,
            symbols_after_main,
            main_side_effects_on_sds,
            side_effects_on_tcds,
            side_effects_on_hds,
            main_side_effect_on_environment_variables,
            proc_exe_settings,
            instruction_settings,
            instruction_environment,
        )

    @staticmethod
    def phase_setup_phase_aware(
            validation: ValidationAssertions = ValidationAssertions.all_passes(),
            main_result: Assertion[T] = asrt.anything_goes(),
            main_raises_hard_error: bool = False,
            symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
            symbols_after_main: Assertion[SymbolTable] = asrt.anything_goes(),
            main_side_effects_on_sds: Assertion[SandboxDs] = asrt.anything_goes(),
            side_effects_on_tcds: Assertion[TestCaseDs] = asrt.anything_goes(),
            side_effects_on_hds: Assertion[pathlib.Path] = asrt.anything_goes(),
            main_side_effect_on_environment_variables: Assertion[Dict[str, str]] = asrt.anything_goes(),
            proc_exe_settings: Assertion[ProcessExecutionSettings]
            = asrt.is_instance(ProcessExecutionSettings),
            instruction_settings: Assertion[InstructionSettings]
            = asrt.is_instance(InstructionSettings),
            instruction_environment:
            Assertion[InstructionApplicationEnvironment] = asrt.anything_goes(),
    ) -> 'MultiSourceExpectation[T]':
        return MultiSourceExpectation(
            MainMethodType.SETUP_PHASE_AWARE,
            validation,
            main_result,
            main_raises_hard_error,
            symbol_usages,
            symbols_after_main,
            main_side_effects_on_sds,
            side_effects_on_tcds,
            side_effects_on_hds,
            main_side_effect_on_environment_variables,
            proc_exe_settings,
            instruction_settings,
            instruction_environment,
        )

    def as_w_source(self, source: Assertion[ParseSource]) -> Expectation[T]:
        return Expectation(
            self.main_method_type,
            self.validation.pre_sds,
            self.validation.post_sds,
            self.main_result,
            self.main_raises_hard_error,
            self.symbol_usages,
            self.symbols_after_main,
            self.main_side_effects_on_sds,
            self.side_effects_on_tcds,
            self.side_effects_on_hds,
            source,
            self.main_side_effect_on_environment_variables,
            self.proc_exe_settings,
            self.instruction_settings,
            self.instruction_application_environment,
        )


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
    Executor(put, arrangement, expectation).execute(parser, source)


class Checker(Generic[T]):
    def __init__(self, parser: InstructionEmbryoParser[T]):
        self.parser = parser

    def check(self,
              put: unittest.TestCase,
              source: ParseSource,
              arrangement: Arrangement,
              expectation: Expectation[T],
              ):
        Executor(put, arrangement, expectation).execute(self.parser, source)

    def check__abs_stx(self,
                       put: unittest.TestCase,
                       source: AbstractSyntax,
                       arrangement: Arrangement,
                       expectation_: Expectation[T],
                       layout: LayoutSpec = LayoutSpec.of_default(),
                       ):
        source = remaining_source(source.tokenization().layout(layout))
        Executor(put, arrangement, expectation_).execute(self.parser, source)

    def check__abs_stx__std_layouts_and_source_variants(
            self,
            put: unittest.TestCase,
            source: AbstractSyntax,
            arrangement: Arrangement,
            expectation: MultiSourceExpectation[T],
            **sub_test_identifiers,
    ):
        self.check__abs_stx__layout_and_source_variants(
            put,
            source,
            arrangement,
            expectation,
            layout.STANDARD_LAYOUT_SPECS,
            **sub_test_identifiers,
        )

    def check__abs_stx__layout_and_source_variants(
            self,
            put: unittest.TestCase,
            source: AbstractSyntax,
            arrangement: Arrangement,
            expectation: MultiSourceExpectation[T],
            layouts: Sequence[NameAndValue[LayoutSpec]] = layout.STANDARD_LAYOUT_SPECS,
            **sub_test_identifiers,
    ):
        self.check__token_sequence__layout_and_source_variants(
            put,
            source.tokenization(),
            arrangement,
            expectation,
            layouts,
            **sub_test_identifiers,
        )

    def check__token_sequence__layout_and_source_variants(
            self,
            put: unittest.TestCase,
            source: TokenSequence,
            arrangement: Arrangement,
            expectation: MultiSourceExpectation[T],
            layouts: Sequence[NameAndValue[LayoutSpec]],
            **sub_test_identifiers,
    ):
        for layout_ in layouts:
            with put.subTest(layout=layout_.name,
                             **sub_test_identifiers):
                source_str = source.layout(layout_.value)
                self.check__w_source_variants(put, source_str, arrangement, expectation)

    def check__w_source_variants(self,
                                 put: unittest.TestCase,
                                 source: str,
                                 arrangement: Arrangement,
                                 expectation: MultiSourceExpectation[T],
                                 ):
        for parse_source, source_asrt in equivalent_source_variants__with_source_check__consume_last_line_2(source):
            with put.subTest(remaining_source=parse_source.remaining_source):
                executor = Executor(put, arrangement, expectation.as_w_source(source_asrt), source_asrt)
                executor.execute(self.parser, parse_source)


class Executor(Generic[T]):
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

    def execute(self,
                parser: InstructionEmbryoParser,
                source: ParseSource):
        instruction = parser.parse(self.arrangement.fs_location_info, source)
        asrt.is_instance(InstructionEmbryo).apply_with_message(self.put, instruction,
                                                               'Instruction class')
        self.expectation.source.apply_with_message(self.put, source, 'source')
        self.extra_source_expectation.apply_with_message(self.put, source, 'source')

        assert isinstance(instruction, InstructionEmbryo)
        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          instruction.symbol_usages,
                                                          'symbol-usages after parse')
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
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_PRE_SDS)
            if validate_result is not None:
                return
            environment = environment_builder.build_post_sds()
            validate_result = self._execute_validate_post_setup(environment, instruction)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_POST_SETUP)
            if validate_result is not None:
                return

            instr_settings = _instruction_settings.from_proc_exe_settings(self.arrangement.process_execution_settings,
                                                                          self.arrangement.default_environ_getter)

            result_of_main = self._execute_main(environment, instr_settings, instruction)

            self.expectation.main_side_effect_on_environment_variables.apply_with_message(
                self.put,
                instr_settings.environ(),
                'main side effects on environment variables')
            self.expectation.symbols_after_main.apply_with_message(
                self.put,
                environment.symbols,
                'symbols_after_main')
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)
            self.expectation.proc_exe_settings.apply_with_message(self.put, environment.proc_exe_settings,
                                                                  'proc exe settings')
            self.expectation.instruction_settings.apply_with_message(self.put, instr_settings,
                                                                     'instruction settings')
            self.expectation.setup_settings.apply_with_message(self.put, self.arrangement.setup_settings,
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
        self.expectation.validation_pre_sds.apply_with_message(self.put, result,
                                                               'validation_pre_sds')
        return result

    def _execute_validate_post_setup(
            self,
            environment: InstructionEnvironmentForPostSdsStep,
            instruction: InstructionEmbryo[T]) -> Optional[TextRenderer]:
        result = instruction.validator.validate_post_sds_if_applicable(environment.path_resolving_environment)
        self.expectation.validation_post_sds.apply_with_message(self.put, result,
                                                                'validation_post_sds')
        return result

    def _execute_main(self,
                      environment: InstructionEnvironmentForPostSdsStep,
                      settings: InstructionSettings,
                      instruction: InstructionEmbryo[T]) -> T:
        executor = _MainMethodExecutor(self.put,
                                       self.expectation.main_method_type,
                                       environment,
                                       settings,
                                       self.arrangement.os_services,
                                       self.arrangement.setup_settings)
        try:
            result = instruction.main_method().accept(executor)
        except HardErrorException as ex:
            if self.expectation.main_raises_hard_error:
                text_doc_assertions.assert_is_valid_text_renderer(self.put, ex.error)
                return
            else:
                self.put.fail('unexpected {} from main'.format(HardErrorException))

        if self.expectation.main_raises_hard_error:
            self.put.fail('main does not raise ' + str(HardErrorException))

        return result


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
