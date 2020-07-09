from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Sequence, Callable

from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure import ddv_validation
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.details_structured import WithDetailsDescription
from exactly_lib.type_system.logic.description import DetailsDescription
from exactly_lib.type_system.logic.impls.advs import ConstantAdv
from exactly_lib.type_system.logic.logic_base_class import LogicDdv, \
    ApplicationEnvironmentDependentValue
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable

PRIMITIVE = TypeVar('PRIMITIVE')


class LogicWithDetailsDescriptionDdv(Generic[PRIMITIVE],
                                     LogicDdv[PRIMITIVE],
                                     WithDetailsDescription,
                                     ABC):
    @property
    def describer(self) -> DetailsRenderer:
        return details.empty()

    def description(self) -> DetailsDescription:
        return _DetailsDescriptionOfDdvWDetails(self)


class LogicWithDetailsDescriptionSdv(Generic[PRIMITIVE], LogicSdv[PRIMITIVE], ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> LogicWithDetailsDescriptionDdv[PRIMITIVE]:
        pass


class ConstantDdv(Generic[PRIMITIVE], LogicWithDetailsDescriptionDdv[PRIMITIVE]):
    def __init__(self, adv: ApplicationEnvironmentDependentValue[PRIMITIVE]):
        self._adv = adv

    def value_of_any_dependency(self, tcds: Tcds) -> ApplicationEnvironmentDependentValue[PRIMITIVE]:
        return self._adv


class DdvFromParts(Generic[PRIMITIVE], LogicWithDetailsDescriptionDdv[PRIMITIVE]):
    def __init__(self,
                 make_adv: Callable[[Tcds], ApplicationEnvironmentDependentValue[PRIMITIVE]],
                 validator: DdvValidator = ddv_validation.constant_success_validator(),
                 describer: DetailsRenderer = details.empty(),
                 ):
        self._validator = validator
        self._describer = describer
        self._make_adv = make_adv

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    @property
    def describer(self) -> DetailsRenderer:
        return self._describer

    def value_of_any_dependency(self, tcds: Tcds) -> ApplicationEnvironmentDependentValue[PRIMITIVE]:
        return self._make_adv(tcds)


class ConstantSdv(Generic[PRIMITIVE], LogicWithDetailsDescriptionSdv[PRIMITIVE]):
    def __init__(self, ddv: LogicWithDetailsDescriptionDdv[PRIMITIVE]):
        self._ddv = ddv

    def resolve(self, symbols: SymbolTable) -> LogicWithDetailsDescriptionDdv[PRIMITIVE]:
        return self._ddv


class SdvFromParts(Generic[PRIMITIVE], LogicWithDetailsDescriptionSdv[PRIMITIVE]):
    def __init__(self,
                 make_ddv: Callable[[SymbolTable], LogicWithDetailsDescriptionDdv[PRIMITIVE]],
                 symbol_references: Sequence[SymbolReference] = (),
                 ):
        self._make_ddv = make_ddv
        self._symbol_references = symbol_references

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._symbol_references

    def resolve(self, symbols: SymbolTable) -> LogicWithDetailsDescriptionDdv[PRIMITIVE]:
        return self._make_ddv(symbols)


def sdv_of_constant_primitive(primitive: PRIMITIVE) -> LogicWithDetailsDescriptionSdv[PRIMITIVE]:
    return ConstantSdv(
        ConstantDdv(
            ConstantAdv(primitive)
        )
    )


class _DetailsDescriptionOfDdvWDetails(DetailsDescription):
    def __init__(self, with_details_description: WithDetailsDescription):
        self._with_details_description = with_details_description

    def details(self) -> DetailsRenderer:
        return self._with_details_description.describer
