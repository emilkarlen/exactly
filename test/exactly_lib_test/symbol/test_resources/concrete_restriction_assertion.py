import unittest

from exactly_lib.symbol.concrete_restrictions import FileRefRelativityRestriction, StringRestriction, \
    NoRestriction, ValueRestrictionVisitor, EitherStringOrFileRefRelativityRestriction
from exactly_lib.symbol.value_restriction import ValueRestriction
from exactly_lib_test.symbol.test_resources.path_relativity import equals_path_relativity_variants
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
