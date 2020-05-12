from typing import Sequence, Type

from exactly_lib.symbol import sdv_structure
from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.util import symbol_table
from exactly_lib.util.file_utils import TmpDirFileSpaceThatMustNoBeUsed
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matches_sdv_of_logic_type__w_adv(sdv_type: Type[LogicSdv],
                                     primitive_value: ValueAssertion = asrt.anything_goes(),
                                     references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                                     symbols: symbol_table.SymbolTable = None,
                                     tcds: Tcds = fake_tcds(),
                                     ) -> ValueAssertion[LogicSdv]:
    symbols = symbol_table.symbol_table_from_none_or_value(symbols)

    ae = ApplicationEnvironment(TmpDirFileSpaceThatMustNoBeUsed())

    def get_primitive_value(sdv: LogicSdv):
        return sdv.resolve(symbols).value_of_any_dependency(tcds).primitive(ae)

    return asrt.is_instance_with(sdv_type,
                                 asrt.and_([
                                     asrt.sub_component('references',
                                                        sdv_structure.get_references,
                                                        references),

                                     asrt.sub_component('primitive value',
                                                        get_primitive_value,
                                                        primitive_value),
                                 ]))
