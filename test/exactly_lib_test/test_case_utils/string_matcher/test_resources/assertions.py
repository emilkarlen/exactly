from typing import Sequence

from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeStv
from exactly_lib.symbol.logic.string_matcher import StringMatcherStv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.string_matcher import StringMatcher
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib.util import symbol_table
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_case_utils.matcher.test_resources import assertions as asrt_matcher
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matches_string_matcher_sdv(primitive_value: ValueAssertion[StringMatcher] = asrt.anything_goes(),
                               references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                               symbols: symbol_table.SymbolTable = None,
                               tcds: Tcds = fake_tcds(),
                               ) -> ValueAssertion[LogicTypeStv]:
    return asrt_matcher.matches_matcher_stv(
        StringMatcherStv,
        LogicValueType.STRING_MATCHER,
        primitive_value,
        references,
        symbols,
        tcds
    )
