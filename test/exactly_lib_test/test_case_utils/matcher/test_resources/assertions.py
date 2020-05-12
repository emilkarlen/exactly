from typing import Sequence

from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatcherDdv, MatcherAdv, \
    MatchingResult
from exactly_lib.util import symbol_table
from exactly_lib.util.file_utils import TmpDirFileSpaceThatMustNoBeUsed, TmpDirFileSpace
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


def main_result_is_success() -> ValueAssertion[MatchingResult]:
    return asrt_matching_result.matches_value(True)


def main_result_is_failure() -> ValueAssertion[MatchingResult]:
    return asrt_matching_result.matches_value(False)


def matches_matcher_sdv(primitive_value: ValueAssertion[MatcherWTraceAndNegation] = asrt.anything_goes(),
                        references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                        symbols: symbol_table.SymbolTable = None,
                        tcds: Tcds = fake_tcds(),
                        tmp_file_space: TmpDirFileSpace = TmpDirFileSpaceThatMustNoBeUsed(),
                        ) -> ValueAssertion[LogicSdv]:
    symbols = symbol_table.symbol_table_from_none_or_value(symbols)

    def get_references(sdv: LogicSdv):
        return sdv.references

    def resolve_ddv(sdv: LogicSdv):
        return sdv.resolve(symbols)

    def get_validator(ddv: MatcherDdv):
        return ddv.validator

    def resolve_adv(ddv: MatcherDdv):
        return ddv.value_of_any_dependency(tcds)

    def resolve_primitive_value(adv: MatcherAdv):
        return adv.primitive(ApplicationEnvironment(tmp_file_space))

    adv_assertion = asrt.is_instance_with__many(
        MatcherAdv,
        [
            asrt.sub_component('primitive value',
                               resolve_primitive_value,
                               asrt.is_instance_with(MatcherWTraceAndNegation,
                                                     primitive_value)),
        ])

    ddv_assertion = asrt.is_instance_with__many(
        MatcherDdv,
        [
            asrt.sub_component('validator',
                               get_validator,
                               asrt.is_instance(DdvValidator)
                               ),

            asrt.sub_component('resolved adv',
                               resolve_adv,
                               adv_assertion),
        ])

    return asrt.is_instance_with__many(
        MatcherSdv,
        [
            asrt.sub_component('references',
                               get_references,
                               references
                               ),

            asrt.sub_component('resolved ddv',
                               resolve_ddv,
                               ddv_assertion),
        ])
