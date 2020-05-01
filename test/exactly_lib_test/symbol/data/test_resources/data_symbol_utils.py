from exactly_lib.symbol import sdv_structure
from exactly_lib.symbol.data.data_type_sdv import DataTypeSdv
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.restrictions.value_restrictions import AnyDataTypeRestriction
from exactly_lib.symbol.data.value_restriction import ValueRestriction
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference
from exactly_lib_test.symbol.test_resources.symbol_utils import single_line_sequence


def container(value_sdv: DataTypeSdv,
              line_num: int = 1,
              source_line: str = 'value def line') -> SymbolContainer:
    return SymbolContainer(value_sdv,
                           single_line_sequence(line_num, source_line))


def container_of_builtin(value_sdv: DataTypeSdv) -> SymbolContainer:
    return sdv_structure.container_of_builtin(value_sdv)


def symbol_reference(name: str,
                     value_restriction: ValueRestriction = AnyDataTypeRestriction()) -> SymbolReference:
    return SymbolReference(name, ReferenceRestrictionsOnDirectAndIndirect(value_restriction))
