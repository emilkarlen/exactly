from typing import Sequence, Callable

from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv, StringTransformerAdv
from exactly_lib.util.symbol_table import SymbolTable


class Sdv(StringTransformerSdv):
    def __init__(self,
                 references: Sequence[SymbolReference],
                 mk_ddv: Callable[[SymbolTable], StringTransformerDdv],
                 ):
        self._references = references
        self._mk_ddv = mk_ddv

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        return self._mk_ddv(symbols)


class Ddv(StringTransformerDdv):
    def __init__(self,
                 structure: StructureRenderer,
                 validator: DdvValidator,
                 mk_adv: Callable[[Tcds], StringTransformerAdv],
                 ):
        self._structure = structure
        self._validator = validator
        self._mk_adv = mk_adv

    def structure(self) -> StructureRenderer:
        return self._structure

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformerAdv:
        return self._mk_adv(tcds)
