import unittest

from exactly_lib.symbol.concrete_restrictions import FileRefRelativityRestriction, StringRestriction, \
    NoRestriction, ValueRestrictionVisitor, EitherStringOrFileRefRelativityRestriction, ReferenceRestrictionsVisitor, \
    OrReferenceRestrictions, ReferenceRestrictionsOnDirectAndIndirect, PathOrStringReferenceRestrictions
from exactly_lib.symbol.value_restriction import ValueRestriction, ReferenceRestrictions
from exactly_lib.symbol.value_structure import ValueContainer
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.path_relativity import equals_path_relativity_variants
from exactly_lib_test.test_case_file_structure.test_resources.path_relativity import path_relativity_variants_equals
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


def equals_either_string_or_file_ref_relativity_restriction(expected: EitherStringOrFileRefRelativityRestriction
                                                            ) -> asrt.ValueAssertion:
    return asrt.is_instance_with(
        EitherStringOrFileRefRelativityRestriction,
        asrt.and_([
            asrt.sub_component('string_restriction',
                               EitherStringOrFileRefRelativityRestriction.string_restriction.fget,
                               equals_string_restriction(expected.string_restriction)),

            asrt.sub_component('file_ref_restriction',
                               EitherStringOrFileRefRelativityRestriction.file_ref_restriction.fget,
                               equals_file_ref_relativity_restriction(expected.file_ref_restriction)),

        ]))


def equals_value_restriction(expected: ValueRestriction) -> asrt.ValueAssertion:
    return _EqualsValueRestriction(expected)


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

    def visit_string_or_file_ref_relativity(self, expected: EitherStringOrFileRefRelativityRestriction):
        assertion = equals_either_string_or_file_ref_relativity_restriction(expected)
        assertion.apply(self.put, self.actual, self.message_builder)


def matches_restrictions_on_direct_and_indirect(assertion_on_direct: asrt.ValueAssertion = asrt.anything_goes(),
                                                assertion_on_every: asrt.ValueAssertion = asrt.anything_goes(),
                                                ) -> asrt.ValueAssertion:
    return asrt.is_instance_with(ReferenceRestrictionsOnDirectAndIndirect,
                                 asrt.and_([
                                     asrt.sub_component('direct',
                                                        ReferenceRestrictionsOnDirectAndIndirect.direct.fget,
                                                        assertion_on_direct),
                                     asrt.sub_component('indirect',
                                                        ReferenceRestrictionsOnDirectAndIndirect.indirect.fget,
                                                        assertion_on_every)
                                 ])
                                 )


def equals_reference_restrictions(expected: ReferenceRestrictions) -> asrt.ValueAssertion:
    return _EQUALS_REFERENCE_RESTRICTIONS_VISITOR.visit(expected)


REFERENCES_ARE_UNRESTRICTED = matches_restrictions_on_direct_and_indirect(
    assertion_on_direct=asrt.is_instance(NoRestriction),
    assertion_on_every=asrt.ValueIsNone())


def _equals_or_reference_restrictions(expected: OrReferenceRestrictions) -> asrt.ValueAssertion:
    expected_sub_restrictions = [_equals_reference_restriction_on_direct_and_indirect(sub)
                                 for sub in expected.parts]
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


def equals_path_or_string_reference_restrictions(expected: PathOrStringReferenceRestrictions
                                                 ) -> asrt.ValueAssertion:
    return asrt.is_instance_with(PathOrStringReferenceRestrictions,
                                 asrt.sub_component('accepted_relativities',
                                                    PathOrStringReferenceRestrictions.accepted_relativities.fget,
                                                    path_relativity_variants_equals(expected.accepted_relativities)))


class _EqualsReferenceRestrictionsVisitor(ReferenceRestrictionsVisitor):
    def visit_direct_and_indirect(self, x: ReferenceRestrictionsOnDirectAndIndirect) -> asrt.ValueAssertion:
        return _equals_reference_restriction_on_direct_and_indirect(x)

    def visit_path_or_string(self, x: PathOrStringReferenceRestrictions) -> asrt.ValueAssertion:
        return equals_path_or_string_reference_restrictions(x)

    def visit_or(self, x: OrReferenceRestrictions) -> asrt.ValueAssertion:
        return _equals_or_reference_restrictions(x)


_EQUALS_REFERENCE_RESTRICTIONS_VISITOR = _EqualsReferenceRestrictionsVisitor()


def value_restriction_that_is_unconditionally_satisfied() -> ValueRestriction:
    return ValueRestrictionWithConstantResult(None)


def value_restriction_that_is_unconditionally_unsatisfied() -> ValueRestriction:
    return ValueRestrictionWithConstantResult('error message')


class ValueRestrictionWithConstantResult(ValueRestriction):
    def __init__(self, result):
        self.result = result

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: ValueContainer) -> str:
        return self.result
