import unittest
from typing import Sequence, Optional

from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolDependentValue
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase


def matches_sdv(sdv_type: ValueAssertion[SymbolDependentValue],
                references: ValueAssertion[Sequence[SymbolReference]],
                resolved_value: ValueAssertion[DirDependentValue],
                custom: ValueAssertion[SymbolDependentValue] = asrt.anything_goes(),
                symbols: Optional[SymbolTable] = None) -> ValueAssertion[SymbolDependentValue]:
    return _MatchesSdv(sdv_type,
                       references,
                       resolved_value,
                       custom,
                       symbol_table_from_none_or_value(symbols))


class _MatchesSdv(ValueAssertionBase[SymbolDependentValue]):
    """Implements as class to make it possible to set break points"""

    def __init__(self,
                 sdv_type: ValueAssertion[SymbolDependentValue],
                 references: ValueAssertion[Sequence[SymbolReference]],
                 ddv: ValueAssertion[DirDependentValue],
                 custom: ValueAssertion[SymbolDependentValue],
                 symbols: SymbolTable):
        self.sdv_type = sdv_type
        self.references = references
        self.custom = custom
        self.ddv = ddv
        self.symbols = symbols

    def _apply(self,
               put: unittest.TestCase,
               value: SymbolDependentValue,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, SymbolDependentValue,
                             message_builder.apply("SDV type"))

        self.sdv_type.apply(put, value, message_builder)

        references__actual = value.references
        references__message_builder = message_builder.for_sub_component('references')

        asrt.is_sequence_of(asrt.is_instance(SymbolReference)).apply(
            put,
            references__actual,
            references__message_builder
        )
        self.references.apply(put, references__actual,
                              references__message_builder)

        self.custom.apply(put, value, message_builder)

        ddv = value.resolve(self.symbols)

        self.ddv.apply(put, ddv,
                       message_builder.for_sub_component('ddv'))
