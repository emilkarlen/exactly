from typing import Optional, Sequence

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.sdv_structure import Failure, ReferenceRestrictions
from exactly_lib.type_val_deps.sym_ref.data import reference_restrictions
from exactly_lib.type_val_deps.sym_ref.data.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import FailureOfDirectReference, \
    FailureOfIndirectReference, ReferenceRestrictionsOnDirectAndIndirect, OrReferenceRestrictions, OrRestrictionPart
from exactly_lib.type_val_deps.sym_ref.data.value_restrictions import AnyDataTypeRestriction, StringRestriction
from exactly_lib.type_val_deps.sym_ref.restrictions import DataTypeReferenceRestrictions
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.data.data_type_reference_visitor import \
    DataTypeReferenceRestrictionsVisitor
from exactly_lib_test.type_val_deps.test_resources.data.value_restriction import \
    equals_value_restriction, matches_value_restriction_failure


def is_failure__of_direct_reference(message: Assertion[TextRenderer] = asrt_text_doc.is_any_text()
                                    ) -> Assertion[Failure]:
    return asrt.is_instance_with(
        FailureOfDirectReference,
        asrt.sub_component('error',
                           FailureOfDirectReference.error.fget,
                           matches_value_restriction_failure(message)))


def is_failure__of_indirect_reference(
        failing_symbol: Assertion[str] = asrt.is_instance(str),
        path_to_failing_symbol: Assertion[Sequence[str]] = asrt.is_instance(list),
        error_message: Assertion[TextRenderer] = asrt_text_doc.is_any_text(),
        meaning_of_failure: Assertion[Optional[TextRenderer]] =
        asrt.is_none_or_instance_with(SequenceRenderer, asrt_text_doc.is_any_text()),
) -> Assertion[Failure]:
    return asrt.is_instance_with(FailureOfIndirectReference,
                                 asrt.and_([
                                     asrt.sub_component('failing_symbol',
                                                        FailureOfIndirectReference.failing_symbol.fget,
                                                        failing_symbol),
                                     asrt.sub_component('path_to_failing_symbol',
                                                        FailureOfIndirectReference.path_to_failing_symbol.fget,
                                                        path_to_failing_symbol),
                                     asrt.sub_component('error',
                                                        FailureOfIndirectReference.error.fget,
                                                        matches_value_restriction_failure(error_message)),
                                     asrt.sub_component('meaning_of_failure',
                                                        FailureOfIndirectReference.meaning_of_failure.fget,
                                                        meaning_of_failure),
                                 ]))


def is_reference_restrictions__on_direct_and_indirect(
        assertion_on_direct: Assertion[ValueRestriction] = asrt.anything_goes(),
        assertion_on_every: Assertion[ValueRestriction] = asrt.anything_goes(),
) -> Assertion[ReferenceRestrictions]:
    return asrt.is_instance_with(
        ReferenceRestrictionsOnDirectAndIndirect,
        asrt.and_([
            asrt.sub_component('direct',
                               ReferenceRestrictionsOnDirectAndIndirect.direct.fget,
                               assertion_on_direct),
            asrt.sub_component('indirect',
                               ReferenceRestrictionsOnDirectAndIndirect.indirect.fget,
                               assertion_on_every),
        ])
    )


def equals_reference_restrictions__convertible_to_string(expected: DataTypeReferenceRestrictions
                                                         ) -> Assertion[ReferenceRestrictions]:
    return _EQUALS_REFERENCE_RESTRICTIONS_VISITOR.visit(expected)


def is_reference_restrictions__convertible_to_string() -> Assertion[ReferenceRestrictions]:
    return equals_reference_restrictions__convertible_to_string(reference_restrictions.is_type_convertible_to_string())


def is_reference_restrictions__string_made_up_of_just_strings() -> Assertion[ReferenceRestrictions]:
    return is_reference_restrictions__on_direct_and_indirect(
        assertion_on_direct=asrt.is_instance(StringRestriction),
        assertion_on_every=asrt.is_instance(StringRestriction)
    )


def equals_reference_restrictions__or(expected: OrReferenceRestrictions) -> Assertion:
    expected_sub_restrictions = [
        asrt.is_instance_with(OrRestrictionPart,
                              asrt.and_([
                                  asrt.sub_component('selector',
                                                     OrRestrictionPart.selector.fget,
                                                     asrt.equals(part.selector)),
                                  asrt.sub_component('restriction',
                                                     OrRestrictionPart.restriction.fget,
                                                     _equals_reference_restriction_on_direct_and_indirect(
                                                         part.restriction)),
                              ])
                              )
        for part in expected.parts]
    return asrt.is_instance_with(OrReferenceRestrictions,
                                 asrt.sub_component('parts',
                                                    OrReferenceRestrictions.parts.fget,
                                                    asrt.matches_sequence(expected_sub_restrictions)))


REFERENCES_ARE_UNRESTRICTED = is_reference_restrictions__on_direct_and_indirect(
    assertion_on_direct=asrt.is_instance(AnyDataTypeRestriction),
    assertion_on_every=asrt.ValueIsNone())


def _equals_reference_restriction_on_direct_and_indirect(expected: ReferenceRestrictionsOnDirectAndIndirect
                                                         ) -> Assertion[ReferenceRestrictions]:
    return is_reference_restrictions__on_direct_and_indirect(
        assertion_on_direct=equals_value_restriction(expected.direct),
        assertion_on_every=asrt.is_none if expected.indirect is None else equals_value_restriction(expected.indirect)
    )


class _EqualsDataTypeReferenceRestrictionsVisitor(DataTypeReferenceRestrictionsVisitor):
    def visit_direct_and_indirect(self, x: ReferenceRestrictionsOnDirectAndIndirect) -> Assertion:
        return _equals_reference_restriction_on_direct_and_indirect(x)

    def visit_or(self, x: OrReferenceRestrictions) -> Assertion:
        return equals_reference_restrictions__or(x)


_EQUALS_REFERENCE_RESTRICTIONS_VISITOR = _EqualsDataTypeReferenceRestrictionsVisitor()
