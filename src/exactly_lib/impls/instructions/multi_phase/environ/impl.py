import enum
import re
from abc import ABC, abstractmethod
from typing import Sequence, Dict, Set

from exactly_lib.impls.instructions.multi_phase.environ.modifier import Modifier, ModifierApplier
from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.path_resolving_env import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv


class Phase(enum.Enum):
    ACT = 1
    NON_ACT = 2


class ModifierResolver(ABC):
    @abstractmethod
    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Modifier:
        pass

    @property
    @abstractmethod
    def references(self) -> Sequence[SymbolReference]:
        pass


class _ApplierFactory(ABC):
    @abstractmethod
    def for_act(self) -> ModifierApplier:
        pass

    @abstractmethod
    def for_non_act(self) -> ModifierApplier:
        pass


class TheInstructionEmbryo(embryo.PhaseAgnosticInstructionEmbryo[None]):
    def __init__(self, phases: Set[Phase], executor: ModifierResolver):
        self._phases = phases
        self._modifier = executor

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._modifier.references

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             ):
        applier_factory = self._resolve_applier_factory(settings)
        modifier_applier = self._resolve_applier(applier_factory)
        modifier = self._modifier.resolve(environment.path_resolving_environment_pre_or_post_sds)
        modifier_applier.apply(modifier)

    @staticmethod
    def _resolve_applier_factory(settings: InstructionSettings) -> _ApplierFactory:
        return _ApplierFactoryForAllPhases(settings)

    def _resolve_applier(self, factory: _ApplierFactory) -> ModifierApplier:
        appliers = []
        if Phase.ACT in self._phases:
            appliers.append(factory.for_act())
        if Phase.NON_ACT in self._phases:
            appliers.append(factory.for_non_act())
        return SequenceOfAppliers(appliers)


class _ApplierFactoryForAllPhases(_ApplierFactory):
    def __init__(self, settings: InstructionSettings):
        self._settings = settings

    def for_act(self) -> ModifierApplier:
        return SequenceOfAppliers.empty()

    def for_non_act(self) -> ModifierApplier:
        return ModifierApplierForAllPhases(self._settings)


class ModifierApplierForAllPhases(ModifierApplier):
    def __init__(self, instruction_settings: InstructionSettings):
        self._instruction_settings = instruction_settings

    def apply(self, modifier: Modifier):
        settings = self._instruction_settings
        if settings.environ() is None:
            settings.set_environ(settings.default_environ_getter())
        modifier.modify(settings.environ())


class SequenceOfAppliers(ModifierApplier):
    def __init__(self, appliers: Sequence[ModifierApplier]):
        self._appliers = appliers

    @staticmethod
    def empty() -> ModifierApplier:
        return SequenceOfAppliers(())

    def apply(self, modifier: Modifier):
        for applier in self._appliers:
            applier.apply(modifier)


class ModifierResolverOfSet(ModifierResolver):
    def __init__(self,
                 var_name: str,
                 var_value: StringSdv,
                 ):
        self._var_name = var_name
        self._var_value = var_value

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Modifier:
        return _SetModifier(self._var_name,
                            self._var_value.resolve_value_of_any_dependency(environment))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._var_value.references


class ModifierResolverOfUnset(ModifierResolver):
    def __init__(self, var_name: str, ):
        self._var_name = var_name

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Modifier:
        return _UnsetModifier(self._var_name)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()


class _SetModifier(Modifier):
    def __init__(self,
                 name: str,
                 value: str,
                 ):
        self._name = name
        self._value = value

    def modify(self, environ: Dict[str, str]):
        environ[self._name] = _expand_vars(self._value, environ)


class _UnsetModifier(Modifier):
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


_ENV_VAR_REFERENCE = re.compile('\${[a-zA-Z0-9_]+}')
