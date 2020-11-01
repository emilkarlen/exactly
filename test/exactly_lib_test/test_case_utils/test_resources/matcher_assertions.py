from typing import Optional, Sequence

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


def is_arbitrary_matching_failure() -> ValueAssertion[MatchingResult]:
    """Matcher on the resolved error message"""
    return asrt_matching_result.matches_value(False)


def is_matching_success() -> ValueAssertion[MatchingResult]:
    return asrt_matching_result.matches_value(True)


def is_hard_error(error_message: ValueAssertion[str] = asrt.anything_goes()) -> Optional[ValueAssertion[TextRenderer]]:
    return asrt_text_doc.is_string_for_test(asrt.is_instance_with(str, error_message))


class Expectation:
    def __init__(
            self,
            validation_post_sds: ValueAssertion[Optional[TextRenderer]] = asrt.is_none,

            validation_pre_sds: ValueAssertion[Optional[TextRenderer]] = asrt.is_none,

            main_result: ValueAssertion[MatchingResult] = asrt_matching_result.matches_value(True),
            is_hard_error: Optional[ValueAssertion[str]] = None,

            symbol_usages: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
            main_side_effects_on_sds: ValueAssertion[SandboxDs] = asrt.anything_goes(),
            main_side_effects_on_tcds: ValueAssertion[TestCaseDs] = asrt.anything_goes(),
            source: ValueAssertion[ParseSource] = asrt.anything_goes(),
    ):
        self.validation_post_sds = validation_post_sds
        self.validation_pre_sds = validation_pre_sds
        self.main_result = main_result
        self.is_hard_error = is_hard_error
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.main_side_effects_on_tcds = main_side_effects_on_tcds
        self.source = source
        self.symbol_usages = symbol_usages


is_pass = Expectation
