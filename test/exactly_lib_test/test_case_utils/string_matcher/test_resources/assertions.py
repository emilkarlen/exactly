from typing import Sequence

from exactly_lib.symbol import sdv_structure
from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeSdv
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.string_matcher import StringMatcher, StringMatcherDdv
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util import symbol_table
from exactly_lib_test.symbol.test_resources.sdv_assertions import is_sdv_of_logic_type
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matches_string_matcher_sdv(primitive_value: ValueAssertion[StringMatcher] = asrt.anything_goes(),
                               references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                               symbols: symbol_table.SymbolTable = None,
                               tcds: Tcds = fake_tcds(),
                               ) -> ValueAssertion[LogicTypeSdv]:
    symbols = symbol_table.symbol_table_from_none_or_value(symbols)

    def resolve_value(sdv: LogicTypeSdv):
        return sdv.resolve(symbols)

    def get_validator(ddv: StringMatcherDdv):
        return ddv.validator

    def resolve_primitive_value(ddv: StringMatcherDdv):
        return ddv.value_of_any_dependency(tcds)

    resolved_value_assertion = asrt.is_instance_with__many(
        StringMatcherDdv,
        [
            asrt.sub_component('validator',
                               get_validator,
                               asrt.is_instance(DdvValidator)
                               ),

            asrt.sub_component('primitive value',
                               resolve_primitive_value,
                               asrt.is_instance_with(StringMatcher,
                                                     primitive_value)),
        ])

    return asrt.is_instance_with(
        StringMatcherSdv,
        asrt.and_([
            is_sdv_of_logic_type(LogicValueType.STRING_MATCHER,
                                 ValueType.STRING_MATCHER),

            asrt.sub_component('references',
                               sdv_structure.get_references,
                               references),

            asrt.sub_component('resolved value',
                               resolve_value,
                               resolved_value_assertion
                               ),
        ])
    )


def matches_string_matcher_attributes(references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                                      ) -> ValueAssertion[LogicTypeSdv]:
    return asrt.is_instance_with(
        StringMatcherSdv,
        asrt.and_([
            is_sdv_of_logic_type(LogicValueType.STRING_MATCHER,
                                 ValueType.STRING_MATCHER),

            asrt.sub_component('references',
                               sdv_structure.get_references,
                               references),
        ])
    )
