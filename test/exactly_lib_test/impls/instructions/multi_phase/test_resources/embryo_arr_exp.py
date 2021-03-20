import enum
import pathlib
from typing import Optional, Mapping, Generic, Dict, Sequence

from exactly_lib.impls.instructions.multi_phase.utils.instruction_embryo import T
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.environ import DefaultEnvironGetter
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.util import functional
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.execution.test_resources.predefined_properties import get_empty_environ
from exactly_lib_test.type_val_deps.test_resources.validation import validation as validation_utils
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationAssertions, ValidationResultAssertion
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.test_case.test_resources.settings_builder_assertions import SettingsBuilderAssertionModel
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


class TcdsExpectation:
    def __init__(self,
                 sds: Assertion[SandboxDs] = asrt.anything_goes(),
                 tcds: Assertion[TestCaseDs] = asrt.anything_goes(),
                 case_home: Assertion[pathlib.Path] = asrt.anything_goes(),
                 ):
        self.sds = sds
        self.tcds = tcds
        self.case_home = case_home


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


class SetupSettingsArr:
    def __init__(self, environ: Optional[Mapping[str, str]]):
        self.environ = environ

    @staticmethod
    def empty() -> 'SetupSettingsArr':
        return SetupSettingsArr(None)

    def as_settings_builder(self) -> SetupSettingsBuilder:
        return SetupSettingsBuilder(
            stdin=None,
            environ=functional.map_optional(dict, self.environ)
        )


class Arrangement:
    def __init__(self,
                 tcds: Optional[TcdsArrangement],
                 os_services: OsServices,
                 process_execution_settings: ProcessExecutionSettings,
                 default_environ_getter: DefaultEnvironGetter,
                 symbols: Optional[SymbolTable],
                 fs_location_info: FileSystemLocationInfo,
                 setup_settings: Optional[SetupSettingsArr],
                 ):
        self.tcds = tcds
        self.os_services = os_services
        self.process_execution_settings = process_execution_settings
        self.setup_settings = setup_settings
        self.symbols = symbol_table_from_none_or_value(symbols)
        self.default_environ_getter = default_environ_getter
        self.fs_location_info = fs_location_info

    @staticmethod
    def phase_agnostic(
            tcds: Optional[TcdsArrangement] = None,
            os_services: OsServices = os_services_access.new_for_current_os(),
            process_execution_settings: ProcessExecutionSettings = proc_exe_env_for_test(),
            default_environ_getter: DefaultEnvironGetter = get_empty_environ,
            symbols: Optional[SymbolTable] = None,
            fs_location_info: FileSystemLocationInfo = ARBITRARY_FS_LOCATION_INFO,
    ) -> 'Arrangement':
        return Arrangement(
            tcds,
            os_services,
            process_execution_settings,
            default_environ_getter,
            symbols,
            fs_location_info,
            None,
        )

    @staticmethod
    def setup_phase_aware(
            tcds: Optional[TcdsArrangement] = None,
            setup_settings: Optional[SetupSettingsArr] = None,
            os_services: OsServices = os_services_access.new_for_current_os(),
            process_execution_settings: ProcessExecutionSettings = proc_exe_env_for_test(),
            default_environ_getter: DefaultEnvironGetter = get_empty_environ,
            symbols: Optional[SymbolTable] = None,
            fs_location_info: FileSystemLocationInfo = ARBITRARY_FS_LOCATION_INFO,
    ) -> 'Arrangement':
        return Arrangement(
            tcds,
            os_services,
            process_execution_settings,
            default_environ_getter,
            symbols,
            fs_location_info,
            setup_settings,
        )


class MainMethodType(enum.Enum):
    PHASE_AGNOSTIC = 1
    SETUP_PHASE_AWARE = 2


class ExecutionExpectation(Generic[T]):
    def __init__(self,
                 main_method_type: MainMethodType,
                 validation: ValidationAssertions = ValidationAssertions.all_passes(),
                 main_result: Assertion[T] = asrt.anything_goes(),
                 main_raises_hard_error: bool = False,
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
                 setup_settings: Assertion[Optional[SettingsBuilderAssertionModel]] = asrt.is_none,
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
        self.main_side_effect_on_environment_variables = main_side_effect_on_environment_variables
        self.instruction_application_environment = instruction_environment
        self.setup_settings = setup_settings

    @staticmethod
    def phase_agnostic(
            validation: ValidationAssertions = ValidationAssertions.all_passes(),
            main_result: Assertion[T] = asrt.anything_goes(),
            main_raises_hard_error: bool = False,
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
    ) -> 'ExecutionExpectation[T]':
        return ExecutionExpectation(
            MainMethodType.PHASE_AGNOSTIC,
            validation,
            main_result,
            main_raises_hard_error,
            main_side_effects_on_sds,
            side_effects_on_tcds,
            side_effects_on_hds,
            main_side_effect_on_environment_variables,
            proc_exe_settings,
            instruction_settings,
            instruction_environment,
            asrt.is_none,
        )

    @staticmethod
    def setup_phase_aware(
            validation: ValidationAssertions = ValidationAssertions.all_passes(),
            main_result: Assertion[T] = asrt.anything_goes(),
            main_raises_hard_error: bool = False,
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
            setup_settings: Assertion[Optional[SettingsBuilderAssertionModel]] = asrt.is_none,
    ) -> 'ExecutionExpectation[T]':
        return ExecutionExpectation(
            MainMethodType.SETUP_PHASE_AWARE,
            validation,
            main_result,
            main_raises_hard_error,
            main_side_effects_on_sds,
            side_effects_on_tcds,
            side_effects_on_hds,
            main_side_effect_on_environment_variables,
            proc_exe_settings,
            instruction_settings,
            instruction_environment,
            setup_settings,
        )


class MultiSourceExpectation(Generic[T], ExecutionExpectation[T]):
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
                 setup_settings: Assertion[Optional[SettingsBuilderAssertionModel]] = asrt.is_none,
                 ):
        super().__init__(
            main_method_type,
            validation,
            main_result,
            main_raises_hard_error,
            main_side_effects_on_sds,
            side_effects_on_tcds,
            side_effects_on_hds,
            main_side_effect_on_environment_variables,
            proc_exe_settings,
            instruction_settings,
            instruction_environment,
            setup_settings,

        )
        self.symbol_usages = symbol_usages
        self.symbols_after_main = symbols_after_main

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
            asrt.is_none,
        )

    @staticmethod
    def phase_agnostic_2(
            validation: ValidationAssertions = ValidationAssertions.all_passes(),
            main_result: Assertion[T] = asrt.anything_goes(),
            main_raises_hard_error: bool = False,
            symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
            symbols_after_main: Assertion[SymbolTable] = asrt.anything_goes(),
            main_side_effects_on_files: TcdsExpectation = TcdsExpectation(),
            main_side_effect_on_environment_variables: Assertion[Dict[str, str]] = asrt.anything_goes(),
            proc_exe_settings: Assertion[ProcessExecutionSettings]
            = asrt.is_instance(ProcessExecutionSettings),
            instruction_settings: Assertion[InstructionSettings]
            = asrt.is_instance(InstructionSettings),
            instruction_environment:
            Assertion[InstructionApplicationEnvironment] = asrt.anything_goes(),
    ) -> 'MultiSourceExpectation[T]':
        return MultiSourceExpectation.phase_agnostic(
            validation,
            main_result,
            main_raises_hard_error,
            symbol_usages,
            symbols_after_main,
            main_side_effects_on_files.sds,
            main_side_effects_on_files.tcds,
            main_side_effects_on_files.case_home,
            main_side_effect_on_environment_variables,
            proc_exe_settings,
            instruction_settings,
            instruction_environment,
        )

    @staticmethod
    def setup_phase_aware(
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
            setup_settings: Assertion[Optional[SettingsBuilderAssertionModel]] = asrt.is_none,
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
            setup_settings,
        )

    def as_w_source(self, source: Assertion[ParseSource]) -> 'Expectation[T]':
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
            self.setup_settings,
        )


class Expectation(Generic[T], MultiSourceExpectation[T]):
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
                 setup_settings: Assertion[Optional[SettingsBuilderAssertionModel]] = asrt.is_none,
                 ):
        super().__init__(
            main_method_type,
            ValidationAssertions(validation_pre_sds,
                                 validation_post_sds),
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
            assertion_on_instruction_environment,
            setup_settings,
        )
        self.source = source

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
    def phase_agnostic_3(
            validation: ValidationAssertions = validation_utils.ValidationAssertions.all_passes(),
            main_result: Assertion[T] = asrt.anything_goes(),
            main_raises_hard_error: bool = False,
            symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
            symbols_after_main: Assertion[SymbolTable] = asrt.anything_goes(),
            main_side_effects_on_files: TcdsExpectation = TcdsExpectation(),
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
            main_side_effects_on_sds=main_side_effects_on_files.sds,
            side_effects_on_tcds=main_side_effects_on_files.tcds,
            side_effects_on_hds=main_side_effects_on_files.case_home,
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
            setup_settings: Assertion[Optional[SettingsBuilderAssertionModel]] = asrt.is_none,
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
