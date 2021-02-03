from typing import Generic, Sequence

from exactly_lib.impls.types.matcher.property_getter import PropertyGetter, PropertyGetterDdv, \
    PropertyGetterSdv, PropertyGetterAdv
from exactly_lib.impls.types.matcher.property_matcher import MODEL, PROP_TYPE
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.util.symbol_table import SymbolTable


class PropertyGetterAdvConstant(PropertyGetterAdv[MODEL, PROP_TYPE]):
    def __init__(self, constant: PropertyGetter[MODEL, PROP_TYPE]):
        self._constant = constant

    def applier(self, environment: ApplicationEnvironment) -> PropertyGetter[MODEL, PROP_TYPE]:
        return self._constant


class PropertyGetterDdvConstant(Generic[MODEL, PROP_TYPE], PropertyGetterDdv[MODEL, PROP_TYPE]):
    def __init__(self, constant: PropertyGetter[MODEL, PROP_TYPE]):
        self._constant = constant

    def structure(self) -> StructureRenderer:
        return self._constant.structure()

    def value_of_any_dependency(self, tcds: TestCaseDs) -> PropertyGetterAdv[MODEL, PROP_TYPE]:
        return PropertyGetterAdvConstant(self._constant)


class PropertyGetterSdvConstant(Generic[MODEL, PROP_TYPE], PropertyGetterSdv[MODEL, PROP_TYPE]):
    def __init__(self, constant: PropertyGetterDdv[MODEL, PROP_TYPE]):
        self._constant = constant

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def resolve(self, symbols: SymbolTable) -> PropertyGetterDdv[MODEL, PROP_TYPE]:
        return self._constant


def sdv_of_constant_primitive(constant: PropertyGetter[MODEL, PROP_TYPE]) -> PropertyGetterSdv[MODEL, PROP_TYPE]:
    return PropertyGetterSdvConstant(
        PropertyGetterDdvConstant(constant)
    )
