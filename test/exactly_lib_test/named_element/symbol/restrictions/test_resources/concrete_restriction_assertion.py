import unittest

from exactly_lib.named_element.resolver_structure import NamedValueContainer
from exactly_lib.named_element.restriction import ReferenceRestrictions
from exactly_lib.named_element.symbol.restrictions.reference_restrictions import SymbolReferenceRestrictionsVisitor, \
    OrReferenceRestrictions, ReferenceRestrictionsOnDirectAndIndirect, FailureOfDirectReference, \
    FailureOfIndirectReference, OrRestrictionPart
from exactly_lib.named_element.symbol.restrictions.value_restrictions import NoRestriction, StringRestriction, \
    FileRefRelativityRestriction, ValueRestrictionVisitor
from exactly_lib.named_element.symbol.value_restriction import ValueRestrictionFailure, ValueRestriction
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.named_element.symbol.test_resources.path_relativity import equals_path_relativity_variants
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt

is_no_restriction = asrt.is_instance(NoRestriction)

is_string_value_restriction = asrt.is_instance(StringRestriction)


def equals_string_restriction(expected: StringRestriction) -> asrt.ValueAssertion:
    return is_string_value_restriction


def equals_file_ref_relativity_restriction(expected: FileRefRelativityRestriction) -> asrt.ValueAssertion:
    return asrt.is_instance_with(FileRefRelativityRestriction,
                                 asrt.sub_component('accepted',
                                                    FileRefRelativityRestriction.accepted.fget,
                                                    equals_path_relativity_variants(expected.accepted)))


def equals_value_restriction(expected: ValueRestriction) -> asrt.ValueAssertion:
    return _EqualsValueRestriction(expected)


def is_value_failure(message: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.is_instance_with(
        ValueRestrictionFailure,
        asrt.and_([
            asrt.sub_component('message',
                               ValueRestrictionFailure.message.fget,
                               message),
            asrt.sub_component('message',
                               ValueRestrictionFailure.how_to_fix.fget,
                               asrt.is_instance(str)),
        ])
    )


def is_failure_of_direct_reference(message: asrt.ValueAssertion = asrt.is_instance(str)) -> asrt.ValueAssertion:
    return asrt.is_instance_with(
        FailureOfDirectReference,
        asrt.sub_component('error',
                           FailureOfDirectReference.error.fget,
                           is_value_failure(message)))


def is_failure_of_indirect_reference(
        failing_symbol: asrt.ValueAssertion = asrt.is_instance(str),
        path_to_failing_symbol: asrt.ValueAssertion = asrt.is_instance(list),
        error_message: asrt.ValueAssertion = asrt.is_instance(str),
        meaning_of_failure: asrt.ValueAssertion = asrt.is_instance(str)) -> asrt.ValueAssertion:
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
                                     asrt.sub_component('meaning_of_failure_of_indirect_reference',
                                                        FailureOfIndirectReference.meaning_of_failure.fget,
                                                        meaning_of_failure),
                                 ]))


class _EqualsValueRestriction(asrt.ValueAssertion):
    def __init__(self, expected: ValueRestriction):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        _EqualsValueRestrictionVisitor(value, put, message_builder).visit(self.expected)


class _EqualsValueRestrictionVisitor(ValueRestrictionVisitor):
    def __init__(self,
                 actual,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.message_builder = message_builder
        self.actual = actual
        self.put = put

    def visit_none(self, expected: NoRestriction):
        is_no_restriction.apply(self.put, self.actual, self.message_builder)

    def visit_string(self, expected: StringRestriction):
        equals_string_restriction(expected).apply(self.put, self.actual, self.message_builder)

    def visit_file_ref_relativity(self, expected: FileRefRelativityRestriction):
        equals_file_ref_relativity_restriction(expected).apply(self.put, self.actual, self.message_builder)


def matches_restrictions_on_direct_and_indirect(
        assertion_on_direct: asrt.ValueAssertion = asrt.anything_goes(),
        assertion_on_every: asrt.ValueAssertion = asrt.anything_goes(),
        meaning_of_failure_of_indirect_reference: asrt.ValueAssertion = asrt.is_instance(str),
) -> asrt.ValueAssertion:
    return asrt.is_instance_with(
        ReferenceRestrictionsOnDirectAndIndirect,
        asrt.and_([
            asrt.sub_component('direct',
                               ReferenceRestrictionsOnDirectAndIndirect.direct.fget,
                               assertion_on_direct),
            asrt.sub_component('indirect',
                               ReferenceRestrictionsOnDirectAndIndirect.indirect.fget,
                               assertion_on_every),
            asrt.sub_component('meaning_of_failure_of_indirect_reference',
                               ReferenceRestrictionsOnDirectAndIndirect.meaning_of_failure_of_indirect_reference.fget,
                               meaning_of_failure_of_indirect_reference)
        ])
    )


def equals_reference_restrictions(expected: ReferenceRestrictions) -> asrt.ValueAssertion:
    return _EQUALS_REFERENCE_RESTRICTIONS_VISITOR.visit(expected)


REFERENCES_ARE_UNRESTRICTED = matches_restrictions_on_direct_and_indirect(
    assertion_on_direct=asrt.is_instance(NoRestriction),
    assertion_on_every=asrt.ValueIsNone())


def equals_or_reference_restrictions(expected: OrReferenceRestrictions) -> asrt.ValueAssertion:
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
                                                         ) -> asrt.ValueAssertion:
    return matches_restrictions_on_direct_and_indirect(
        assertion_on_direct=equals_value_restriction(expected.direct),
        assertion_on_every=asrt.is_none if expected.indirect is None else equals_value_restriction(expected.indirect)
    )


class _EqualsSymbolReferenceRestrictionsVisitor(SymbolReferenceRestrictionsVisitor):
    def visit_direct_and_indirect(self, x: ReferenceRestrictionsOnDirectAndIndirect) -> asrt.ValueAssertion:
        return _equals_reference_restriction_on_direct_and_indirect(x)

    def visit_or(self, x: OrReferenceRestrictions) -> asrt.ValueAssertion:
        return equals_or_reference_restrictions(x)


_EQUALS_REFERENCE_RESTRICTIONS_VISITOR = _EqualsSymbolReferenceRestrictionsVisitor()


def value_restriction_that_is_unconditionally_satisfied() -> ValueRestriction:
    return ValueRestrictionWithConstantResult(None)


def value_restriction_that_is_unconditionally_unsatisfied(msg: str = 'error message') -> ValueRestriction:
    return ValueRestrictionWithConstantResult(ValueRestrictionFailure(msg))


class ValueRestrictionWithConstantResult(ValueRestriction):
    def __init__(self, result: ValueRestrictionFailure):
        self.result = result

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: NamedValueContainer) -> ValueRestrictionFailure:
        return self.result
