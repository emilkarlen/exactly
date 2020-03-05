from typing import TypeVar, Sequence

from exactly_lib.symbol import sdv_structure
from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_system.logic.logic_base_class import LogicDdv
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

PRIMITIVE = TypeVar('PRIMITIVE')


def matches_logic_sdv(references: ValueAssertion[Sequence[SymbolReference]],
                      ddv: ValueAssertion[LogicDdv[PRIMITIVE]],
                      symbols: SymbolTable = None,
                      ) -> ValueAssertion[LogicSdv[PRIMITIVE]]:
    def get_ddv(sdv: LogicSdv[PRIMITIVE]):
        return sdv.resolve(symbol_table_from_none_or_value(symbols))

    return asrt.is_instance_with__many(
        LogicSdv,
        [
            asrt.sub_component(
                'references',
                sdv_structure.get_references__sdv,
                asrt.and_([
                    asrt.is_sequence_of(asrt.is_instance(SymbolReference)),
                    references,
                ]),
            ),
            asrt.sub_component(
                'ddv',
                get_ddv,
                asrt.is_instance_with(LogicDdv, ddv)
            )
        ]
    )
