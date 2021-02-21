from typing import List, Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib_test.impls.types.string_transformer.test_resources import integration_check, freeze_check
from exactly_lib_test.impls.types.string_transformer.test_resources.integration_check import StExpectation, \
    StMultiSourceExpectation
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def expectation_of_successful_replace_execution(
        output_lines: List[str],
        symbol_references: Assertion[Sequence[SymbolReference]] = asrt.anything_goes(),
        may_depend_on_external_resources: bool = False,
) -> StExpectation:
    return integration_check.expectation_of_successful_execution_2(
        output_lines,
        may_depend_on_external_resources,
        symbol_references,
        False,
        adv=freeze_check.first_invoked_method_of_source_model__is_freeze,
    )


def expectation_of_successful_replace_execution__multi(
        output_lines: List[str],
        symbol_references: Assertion[Sequence[SymbolReference]] = asrt.anything_goes(),
        may_depend_on_external_resources: bool = False,
) -> StMultiSourceExpectation:
    return integration_check.expectation_of_successful_execution__multi(
        output_lines,
        may_depend_on_external_resources,
        symbol_references,
        False,
        adv=freeze_check.first_invoked_method_of_source_model__is_freeze,
    )
