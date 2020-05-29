import unittest
from typing import Optional, Sequence

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.data.restrictions.reference_restrictions import DataTypeReferenceRestrictionsVisitor, \
    OrReferenceRestrictions, ReferenceRestrictionsOnDirectAndIndirect, FailureOfDirectReference, \
    FailureOfIndirectReference, OrRestrictionPart, is_any_data_type
from exactly_lib.symbol.data.restrictions.value_restrictions import AnyDataTypeRestriction, \
    StringRestriction, \
    PathRelativityRestriction, ValueRestrictionVisitor
from exactly_lib.symbol.data.value_restriction import ErrorMessageWithFixTip, ValueRestriction
from exactly_lib.symbol.restriction import DataTypeReferenceRestrictions
from exactly_lib.symbol.sdv_structure import SymbolContainer, Failure, ReferenceRestrictions
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.symbol.data.test_resources.path_relativity import equals_path_relativity_variants
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase

is_any_data_type_restriction = asrt.is_instance(AnyDataTypeRestriction)

is_string_value_restriction = asrt.is_instance(StringRestriction)


def equals_string_restriction(expected: StringRestriction) -> ValueAssertion[ValueRestriction]:
    return is_string_value_restriction


def equals_path_relativity_restriction(expected: PathRelativityRestriction) -> ValueAssertion[ValueRestriction]:
    return asrt.is_instance_with(PathRelativityRestriction,
                                 asrt.sub_component('accepted',
                                                    PathRelativityRestriction.accepted.fget,
                                                    equals_path_relativity_variants(expected.accepted)))


def equals_value_restriction(expected: ValueRestriction) -> ValueAssertion[ValueRestriction]:
    return _EqualsValueRestriction(expected)


def is_value_failure(message: ValueAssertion[TextRenderer]) -> ValueAssertion[ErrorMessageWithFixTip]:
    return asrt.is_instance_with(
        ErrorMessageWithFixTip,
        asrt.and_([
            asrt.sub_component('message',
                               ErrorMessageWithFixTip.message.fget,
                               message),
            asrt.sub_component('how_to_fix',
                               ErrorMessageWithFixTip.how_to_fix.fget,
                               asrt.is_none_or_instance_with(Renderer, asrt_text_doc.is_any_text())),
        ])
    )


def is_failure_of_direct_reference(message: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text()
                                   ) -> ValueAssertion[Failure]:
    return asrt.is_instance_with(
        FailureOfDirectReference,
        asrt.sub_component('error',
                           FailureOfDirectReference.error.fget,
                           is_value_failure(message)))


def is_failure_of_indirect_reference(
        failing_symbol: ValueAssertion[str] = asrt.is_instance(str),
        path_to_failing_symbol: ValueAssertion[Sequence[str]] = asrt.is_instance(list),
        error_message: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text(),
        meaning_of_failure: ValueAssertion[Optional[TextRenderer]] =
        asrt.is_none_or_instance_with(SequenceRenderer, asrt_text_doc.is_any_text()),
) -> ValueAssertion:
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
                                                        is_value_failure(error_message)),
                                     asrt.sub_component('meaning_of_failure',
                                                        FailureOfIndirectReference.meaning_of_failure.fget,
                                                        meaning_of_failure),
                                 ]))


class _EqualsValueRestriction(ValueAssertionBase[ValueRestriction]):
    def __init__(self, expected: ValueRestriction):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        _EqualsValueRestrictionVisitor(value, put, message_builder).visit(self.expected)


class _EqualsValueRestrictionVisitor(ValueRestrictionVisitor):
    def __init__(self,
                 actual,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.message_builder = message_builder
        self.actual = actual
        self.put = put

    def visit_none(self, expected: AnyDataTypeRestriction):
        is_any_data_type_restriction.apply(self.put, self.actual, self.message_builder)

    def visit_string(self, expected: StringRestriction):
        equals_string_restriction(expected).apply(self.put, self.actual, self.message_builder)

    def visit_path_relativity(self, expected: PathRelativityRestriction):
        equals_path_relativity_restriction(expected).apply(self.put, self.actual, self.message_builder)


def matches_restrictions_on_direct_and_indirect(
        assertion_on_direct: ValueAssertion[ValueRestriction] = asrt.anything_goes(),
        assertion_on_every: ValueAssertion[ValueRestriction] = asrt.anything_goes(),
) -> ValueAssertion[ReferenceRestrictions]:
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


def equals_data_type_reference_restrictions(expected: DataTypeReferenceRestrictions
                                            ) -> ValueAssertion[ReferenceRestrictions]:
    return _EQUALS_REFERENCE_RESTRICTIONS_VISITOR.visit(expected)


def is_any_data_type_reference_restrictions() -> ValueAssertion[ReferenceRestrictions]:
    return equals_data_type_reference_restrictions(is_any_data_type())


REFERENCES_ARE_UNRESTRICTED = matches_restrictions_on_direct_and_indirect(
    assertion_on_direct=asrt.is_instance(AnyDataTypeRestriction),
    assertion_on_every=asrt.ValueIsNone())


def equals_or_reference_restrictions(expected: OrReferenceRestrictions) -> ValueAssertion:
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


def _equals_reference_restriction_on_direct_and_indirect(expected: ReferenceRestrictionsOnDirectAndIndirect
                                                         ) -> ValueAssertion[ReferenceRestrictions]:
    return matches_restrictions_on_direct_and_indirect(
        assertion_on_direct=equals_value_restriction(expected.direct),
        assertion_on_every=asrt.is_none if expected.indirect is None else equals_value_restriction(expected.indirect)
    )


class _EqualsDataTypeReferenceRestrictionsVisitor(DataTypeReferenceRestrictionsVisitor):
    def visit_direct_and_indirect(self, x: ReferenceRestrictionsOnDirectAndIndirect) -> ValueAssertion:
        return _equals_reference_restriction_on_direct_and_indirect(x)

    def visit_or(self, x: OrReferenceRestrictions) -> ValueAssertion:
        return equals_or_reference_restrictions(x)


_EQUALS_REFERENCE_RESTRICTIONS_VISITOR = _EqualsDataTypeReferenceRestrictionsVisitor()


def value_restriction_that_is_unconditionally_satisfied() -> ValueRestriction:
    return ValueRestrictionWithConstantResult(None)


def value_restriction_that_is_unconditionally_unsatisfied(msg: str = 'error message') -> ValueRestriction:
    return ValueRestrictionWithConstantResult(ErrorMessageWithFixTip(
        asrt_text_doc.new_single_string_text_for_test(msg))
    )


def is_string_made_up_of_just_strings_reference_restrictions() -> ValueAssertion[ReferenceRestrictions]:
    return matches_restrictions_on_direct_and_indirect(
        assertion_on_direct=asrt.is_instance(StringRestriction),
        assertion_on_every=asrt.is_instance(StringRestriction)
    )


class ValueRestrictionWithConstantResult(ValueRestriction):
    def __init__(self, result: ErrorMessageWithFixTip):
        self.result = result

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> Optional[ErrorMessageWithFixTip]:
        return self.result
