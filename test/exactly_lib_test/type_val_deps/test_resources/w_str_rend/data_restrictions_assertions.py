from typing import Optional, Sequence

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.sdv_structure import Failure, ReferenceRestrictions
from exactly_lib.type_val_deps.sym_ref.restrictions import WithStrRenderingTypeRestrictions
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import FailureOfDirectReference, \
    FailureOfIndirectReference, ReferenceRestrictionsOnDirectAndIndirect, OrReferenceRestrictions, OrRestrictionPart
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import \
    ArbitraryValueWStrRenderingRestriction
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import value_restriction_assertions as asrt_val_rest
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.data_type_reference_visitor import \
    TypeWithStrRenderingReferenceRestrictionsVisitor


def is_failure__of_direct_reference(message: Assertion[TextRenderer] = asrt_text_doc.is_any_text()
                                    ) -> Assertion[Failure]:
    return asrt.is_instance_with(
        FailureOfDirectReference,
        asrt.sub_component('error',
                           FailureOfDirectReference.error.fget,
                           asrt_val_rest.matches_value_restriction_failure(message)))


def is_failure__of_indirect_reference(
        failing_symbol: Assertion[str] = asrt.is_instance(str),
        path_to_failing_symbol: Assertion[Sequence[str]] = asrt.is_instance(list),
        error_message: Assertion[TextRenderer] = asrt_text_doc.is_any_text(),
        meaning_of_failure: Assertion[Optional[TextRenderer]] =
        asrt.is_none_or_instance_with(SequenceRenderer, asrt_text_doc.is_any_text()),
) -> Assertion[Failure]:
    return asrt.is_instance_with(
        FailureOfIndirectReference,
        asrt.and_([
            asrt.sub_component('failing_symbol',
                               FailureOfIndirectReference.failing_symbol.fget,
                               failing_symbol),
            asrt.sub_component('path_to_failing_symbol',
                               FailureOfIndirectReference.path_to_failing_symbol.fget,
                               path_to_failing_symbol),
            asrt.sub_component('error',
                               FailureOfIndirectReference.error.fget,
                               asrt_val_rest.matches_value_restriction_failure(error_message)),
            asrt.sub_component('meaning_of_failure',
                               FailureOfIndirectReference.meaning_of_failure.fget,
                               meaning_of_failure),
        ]))


def matches__on_direct_and_indirect(
        assertion_on_direct: Assertion[ValueRestriction] = asrt.anything_goes(),
        assertion_on_indirect: Assertion[ValueRestriction] = asrt.anything_goes(),
) -> Assertion[ReferenceRestrictions]:
    return asrt.is_instance_with(
        ReferenceRestrictionsOnDirectAndIndirect,
        asrt.and_([
            asrt.sub_component('direct',
                               ReferenceRestrictionsOnDirectAndIndirect.direct.fget,
                               assertion_on_direct),
            asrt.sub_component('indirect',
                               ReferenceRestrictionsOnDirectAndIndirect.indirect.fget,
                               assertion_on_indirect),
        ])
    )


def equals__w_str_rendering(expected: WithStrRenderingTypeRestrictions
                            ) -> Assertion[ReferenceRestrictions]:
    return _EQUALS_REFERENCE_RESTRICTIONS_VISITOR.visit(expected)


def is__w_str_rendering() -> Assertion[ReferenceRestrictions]:
    return equals__w_str_rendering(reference_restrictions.is_any_type_w_str_rendering())


def is__string__w_all_indirect_refs_are_strings() -> Assertion[ReferenceRestrictions]:
    return matches__on_direct_and_indirect(
        assertion_on_direct=asrt_val_rest.is__string(),
        assertion_on_indirect=asrt_val_rest.is__string()
    )


def equals__or(expected: OrReferenceRestrictions) -> Assertion:
    expected_sub_restrictions = [
        asrt.is_instance_with(OrRestrictionPart,
                              asrt.and_([
                                  asrt.sub_component('selector',
                                                     OrRestrictionPart.selector.fget,
                                                     asrt.equals(part.selector)),
                                  asrt.sub_component('restriction',
                                                     OrRestrictionPart.restriction.fget,
                                                     _equals_on_direct_and_indirect(
                                                         part.restriction)),
                              ])
                              )
        for part in expected.parts]
    return asrt.is_instance_with(OrReferenceRestrictions,
                                 asrt.sub_component('parts',
                                                    OrReferenceRestrictions.parts.fget,
                                                    asrt.matches_sequence(expected_sub_restrictions)))


REFERENCES_ARE_UNRESTRICTED = matches__on_direct_and_indirect(
    assertion_on_direct=asrt.is_instance(ArbitraryValueWStrRenderingRestriction),
    assertion_on_indirect=asrt.ValueIsNone())


def _equals_on_direct_and_indirect(expected: ReferenceRestrictionsOnDirectAndIndirect
                                   ) -> Assertion[ReferenceRestrictions]:
    return matches__on_direct_and_indirect(
        assertion_on_direct=asrt_val_rest.equals(expected.direct),
        assertion_on_indirect=(
            asrt.is_none
            if expected.indirect is None
            else
            asrt_val_rest.equals(expected.indirect)
        )
    )


class _EqualsDataTypeReferenceRestrictionsVisitor(TypeWithStrRenderingReferenceRestrictionsVisitor):
    def visit_direct_and_indirect(self, x: ReferenceRestrictionsOnDirectAndIndirect) -> Assertion:
        return _equals_on_direct_and_indirect(x)

    def visit_or(self, x: OrReferenceRestrictions) -> Assertion:
        return equals__or(x)


_EQUALS_REFERENCE_RESTRICTIONS_VISITOR = _EqualsDataTypeReferenceRestrictionsVisitor()
