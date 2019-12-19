from typing import Sequence

from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util import symbol_table
from exactly_lib_test.test_case_utils.test_resources import sdv_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def resolved_value_matches_string_transformer(
        value: ValueAssertion[StringTransformer],
        references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
        symbols: symbol_table.SymbolTable = None
) -> ValueAssertion[LogicTypeSdv]:
    return sdv_assertions.matches_sdv_of_logic_type__w_adv(StringTransformerSdv,
                                                           LogicValueType.STRING_TRANSFORMER,
                                                           ValueType.STRING_TRANSFORMER,
                                                           asrt.is_instance_with(StringTransformer,
                                                                                 value),
                                                           references,
                                                           symbols)
