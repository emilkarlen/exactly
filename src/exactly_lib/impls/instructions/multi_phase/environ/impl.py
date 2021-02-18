import enum
import re
from abc import ABC, abstractmethod
from typing import Dict, Mapping
from typing import Sequence, Optional, FrozenSet

from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator, ConstantDdvValidator
from exactly_lib.type_val_deps.dep_variants.sdv import sdv_validation
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator
from exactly_lib.type_val_deps.types.string_.string_ddv import StringDdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.type_val_deps.types.string_source.ddv import StringSourceDdv, StringSourceAdv
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable


class Phase(enum.Enum):
    ACT = 1
    NON_ACT = 2


class Modifier(ABC):
    @abstractmethod
    def modify(self, environ: Dict[str, str]):
        pass


class ModifierDdv(ABC):
    @abstractmethod
    def validator(self) -> DdvValidator:
        pass

    @abstractmethod
    def resolve(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[Modifier]:
        pass


class ModifierSdv(ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> ModifierDdv:
        pass

    @property
    @abstractmethod
    def references(self) -> Sequence[SymbolReference]:
        pass


class ModifierApplier(ABC):
    @abstractmethod
    def apply(self, modifier: ApplicationEnvironmentDependentValue[Modifier]):
        pass


class _ApplierFactory(ABC):
    @abstractmethod
    def applier_for_act(self) -> ModifierApplier:
        pass

    @abstractmethod
    def applier_for_non_act(self) -> ModifierApplier:
        pass


class _AppEnvConstructor:
    def __init__(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 os_services: OsServices,
                 ):
        self._environment = environment
        self._os_services = os_services

    def of(self, environ: Optional[Mapping[str, str]]) -> ApplicationEnvironment:
        return ApplicationEnvironment(
            self._os_services,
            self._proc_exe_settings(environ),
            self._environment.tmp_dir__path_access.paths_access,
            self._environment.mem_buff_size,
        )

    def _proc_exe_settings(self, environ: Optional[Mapping[str, str]]) -> ProcessExecutionSettings:
        return ProcessExecutionSettings(
            self._environment.proc_exe_settings.timeout_in_seconds,
            environ,
        )


class TheInstructionEmbryo(embryo.SetupPhaseAwareInstructionEmbryo[None]):
    def __init__(self, phases: FrozenSet[Phase], executor: ModifierSdv):
        self._phases = phases
        self._modifier = executor

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._modifier.references

    @property
    def validator(self) -> SdvValidator:
        def get_validator(symbols: SymbolTable) -> DdvValidator:
            return self._modifier.resolve(symbols).validator()

        return sdv_validation.SdvValidatorFromDdvValidator(get_validator)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             setup_phase_settings: Optional[SetupSettingsBuilder],
             os_services: OsServices,
             ):
        app_env_constructor = _AppEnvConstructor(environment, os_services)
        applier_factory = self._resolve_applier_factory(settings, app_env_constructor, setup_phase_settings)
        modifier_applier = self._resolve_applier(applier_factory)
        modifier_ddv = self._modifier.resolve(environment.symbols)
        modifier_adv = modifier_ddv.resolve(environment.tcds)
        modifier_applier.apply(modifier_adv)

    @staticmethod
    def _resolve_applier_factory(instruction_settings: InstructionSettings,
                                 app_env_constructor: _AppEnvConstructor,
                                 setup_phase_settings: Optional[SetupSettingsBuilder],
                                 ) -> _ApplierFactory:
        return (
            _ApplierFactoryWSupportForNonSetupPhase(instruction_settings, app_env_constructor)
            if setup_phase_settings is None
            else
            _ApplierFactoryWSupportForSetupAndNonSetupPhases(instruction_settings,
                                                             app_env_constructor,
                                                             setup_phase_settings)
        )

    def _resolve_applier(self, factory: _ApplierFactory) -> ModifierApplier:
        appliers = []
        if Phase.ACT in self._phases:
            appliers.append(factory.applier_for_act())
        if Phase.NON_ACT in self._phases:
            appliers.append(factory.applier_for_non_act())
        return SequenceOfAppliers(appliers)


class _ApplierFactoryWSupportForNonSetupPhase(_ApplierFactory):
    def __init__(self,
                 settings: InstructionSettings,
                 app_env_constructor: _AppEnvConstructor,
                 ):
        self.instruction_settings = settings
        self.app_env_constructor = app_env_constructor

    def applier_for_act(self) -> ModifierApplier:
        return SequenceOfAppliers.empty()

    def applier_for_non_act(self) -> ModifierApplier:
        return ModifierApplierForNonSetupPhase(self.instruction_settings,
                                               self.app_env_constructor)


class _ApplierFactoryWSupportForSetupAndNonSetupPhases(_ApplierFactoryWSupportForNonSetupPhase):
    def __init__(self,
                 instruction_settings: InstructionSettings,
                 app_env_constructor: _AppEnvConstructor,
                 setup_phase_settings: SetupSettingsBuilder,
                 ):
        super().__init__(instruction_settings, app_env_constructor)
        self._setup_phase_settings = setup_phase_settings

    def applier_for_act(self) -> ModifierApplier:
        return ModifierApplierForSetupPhase(self.instruction_settings,
                                            self.app_env_constructor,
                                            self._setup_phase_settings,
                                            )


class ModifierApplierForNonSetupPhase(ModifierApplier):
    def __init__(self,
                 instruction_settings: InstructionSettings,
                 app_env_constructor: _AppEnvConstructor,
                 ):
        self._instruction_settings = instruction_settings
        self._app_env_constructor = app_env_constructor

    def apply(self, modifier: ApplicationEnvironmentDependentValue[Modifier]):
        modifier = modifier.primitive(self._app_env_constructor.of(self._instruction_settings.environ()))
        self._populate_if_is_unpopulated()
        modifier.modify(self._instruction_settings.environ())

    def _populate_if_is_unpopulated(self):
        settings = self._instruction_settings
        if settings.environ() is None:
            settings.set_environ(settings.default_environ_getter())


class ModifierApplierForSetupPhase(ModifierApplier):
    def __init__(self,
                 instruction_settings: InstructionSettings,
                 app_env_constructor: _AppEnvConstructor,
                 setup_phase_settings: SetupSettingsBuilder,
                 ):
        self._instruction_settings = instruction_settings
        self._app_env_constructor = app_env_constructor
        self._setup_phase_settings = setup_phase_settings

    def apply(self, modifier: ApplicationEnvironmentDependentValue[Modifier]):
        modifier = modifier.primitive(self._app_env_constructor.of(self._setup_phase_settings.environ))
        self._populate_if_is_unpopulated()
        modifier.modify(self._setup_phase_settings.environ)

    def _populate_if_is_unpopulated(self):
        settings = self._setup_phase_settings
        if settings.environ is None:
            settings.environ = self._instruction_settings.default_environ_getter()


class SequenceOfAppliers(ModifierApplier):
    def __init__(self, appliers: Sequence[ModifierApplier]):
        self._appliers = appliers

    @staticmethod
    def empty() -> ModifierApplier:
        return SequenceOfAppliers(())

    def apply(self, modifier: ApplicationEnvironmentDependentValue[Modifier]):
        for applier in self._appliers:
            applier.apply(modifier)


class ModifierDdvForSet(ModifierDdv):
    def __init__(self,
                 name: StringDdv,
                 value: StringSourceDdv,
                 ):
        self._name = name
        self._value = value

    def validator(self) -> DdvValidator:
        return self._value.validator

    def resolve(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[Modifier]:
        return ModifierAdvForSet(self._name.value_of_any_dependency(tcds),
                                 self._value.value_of_any_dependency(tcds))


class ModifierAdvForSet(ApplicationEnvironmentDependentValue[Modifier]):
    def __init__(self,
                 name: str,
                 value: StringSourceAdv,
                 ):
        self._name = name
        self._value = value

    def primitive(self, environment: ApplicationEnvironment) -> Modifier:
        string_source = self._value.primitive(environment)
        value_str = string_source.contents().as_str
        return ModifierOfSet(self._name, value_str)


class ModifierOfSet(Modifier):
    def __init__(self,
                 name: str,
                 value: str,
                 ):
        self._name = name
        self._value = value

    def modify(self, environ: Dict[str, str]):
        environ[self._name] = _expand_vars(self._value, environ)


class ModifierSdvOfSet(ModifierSdv):
    def __init__(self,
                 var_name: StringSdv,
                 var_value: StringSourceSdv,
                 ):
        self._var_name = var_name
        self._var_value = var_value
        self._references = tuple(var_name.references) + tuple(var_value.references)

    def resolve(self, symbols: SymbolTable) -> ModifierDdv:
        return ModifierDdvForSet(self._var_name.resolve(symbols),
                                 self._var_value.resolve(symbols))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references


class ModifierDdvForUnset(ModifierDdv):
    def __init__(self, name: StringDdv):
        self._name = name

    def validator(self) -> DdvValidator:
        return ConstantDdvValidator()

    def resolve(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[Modifier]:
        return ModifierAdvForUnset(self._name.value_of_any_dependency(tcds))


class ModifierAdvForUnset(ApplicationEnvironmentDependentValue[Modifier]):
    def __init__(self, name: str):
        self._name = name

    def primitive(self, environment: ApplicationEnvironment) -> Modifier:
        return ModifierUnset(self._name)


class ModifierSdvOfUnset(ModifierSdv):
    def __init__(self, var_name: StringSdv):
        self._var_name = var_name

    def resolve(self, symbols: SymbolTable) -> ModifierDdv:
        return ModifierDdvForUnset(self._var_name.resolve(symbols))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._var_name.references


class ModifierUnset(Modifier):
    def __init__(self, name: str):
        self.name = name

    def modify(self, environ: Dict[str, str]):
        try:
            del environ[self.name]
        except KeyError:
            pass


def _expand_vars(value: str, environ: Dict[str, str]) -> str:
    def substitute(reference: str) -> str:
        var_name = reference[2:-1]
        try:
            return environ[var_name]
        except KeyError:
            return ''

    processed = ''
    remaining = value
    match = _ENV_VAR_REFERENCE.search(remaining)
    while match:
        processed += remaining[:match.start()]
        processed += substitute(remaining[match.start():match.end()])
        remaining = remaining[match.end():]
        match = _ENV_VAR_REFERENCE.search(remaining)
    processed += remaining
    return processed


_ENV_VAR_REFERENCE = re.compile(r'\${[a-zA-Z0-9_]+}')
