import unittest

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependencies, DirDependentValue
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherStructureVisitor, LineMatcherConstant, \
    LineMatcherRegex, LineMatcherNot, LineMatcherAnd, LineMatcherOr, LineMatcherLineNumber
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherValue
from exactly_lib_test.test_case_file_structure.test_resources import dir_dep_value_assertions as asrt_dir_dep_val
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase


def equals_line_matcher(expected: LineMatcher,
                        description: str = '') -> ValueAssertion[LineMatcher]:
    return _EqualsAssertion(expected, description)


def value_equals_line_matcher(expected: LineMatcher,
                              description: str = '') -> ValueAssertion[LineMatcherValue]:
    return _EqualsAssertionValue(expected, description)


def value_matches_line_matcher(expected: ValueAssertion[LineMatcher],
                               dir_dependencies: DirDependencies = DirDependencies.NONE,
                               ) -> ValueAssertion[DirDependentValue[LineMatcher]]:
    return asrt_dir_dep_val.matches_multi_dir_dependent_value(
        dir_dependencies,
        lambda tcds: expected,
    )


class _EqualsAssertion(ValueAssertionBase[LineMatcher]):
    def __init__(self,
                 expected: LineMatcher,
                 description: str):
        self.expected = expected
        self.description = description

    def _apply(self,
               put: unittest.TestCase,
               actual,
               message_builder: asrt.MessageBuilder):
        assert_is_line_matcher_type = asrt.is_instance(LineMatcher, self.description)
        assert_is_line_matcher_type.apply_with_message(put, actual,
                                                       'Value must be a ' + str(LineMatcher))
        assert isinstance(actual, LineMatcher)  # Type info for IDE
        checker = _EqualityChecker(put,
                                   message_builder,
                                   actual,
                                   self.description
                                   )
        checker.visit(self.expected)


class _EqualsAssertionValue(ValueAssertionBase[LineMatcherValue]):
    TCDS = fake_home_and_sds()

    def __init__(self,
                 expected: LineMatcher,
                 description: str):
        self.expected = expected
        self.description = description

    def _apply(self,
               put: unittest.TestCase,
               actual,
               message_builder: asrt.MessageBuilder):
        assert_is_file_selector_type = asrt.is_instance(LineMatcherValue, self.description)
        assert_is_file_selector_type.apply_with_message(put, actual,
                                                        'Value must be a ' + str(LineMatcherValue))
        assert isinstance(actual, LineMatcherValue)

        assertion_on_primitive_value = equals_line_matcher(self.expected, self.description)
        assertion_on_primitive_value.apply(put,
                                           actual.value_of_any_dependency(self.TCDS),
                                           message_builder)


class _EqualityChecker(LineMatcherStructureVisitor):
    def __init__(self,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder,
                 actual: LineMatcher,
                 description: str):
        self.put = put
        self.actual = actual
        self.message_builder = message_builder.with_description(description)

    def _common(self, expected: LineMatcher):
        self.put.assertIsInstance(self.actual,
                                  type(expected),
                                  self.message_builder.apply('class'))

    def visit_constant(self, expected: LineMatcherConstant):
        self._common(expected)
        assert isinstance(self.actual, LineMatcherConstant)
        self.put.assertEqual(expected.result_constant,
                             self.actual.result_constant,
                             'result constant')

    def visit_regex(self, expected: LineMatcherRegex):
        self._common(expected)
        assert isinstance(self.actual, LineMatcherRegex)
        self.put.assertEqual(expected.regex_pattern_string,
                             self.actual.regex_pattern_string,
                             'regex pattern string')

    def visit_line_number(self, matcher: LineMatcherLineNumber):
        raise ValueError('Line number matcher is unsupported at the moment')

    def visit_not(self, expected: LineMatcherNot):
        self._common(expected)
        assert isinstance(self.actual, LineMatcherNot)
        assertion_on_negated_matcher = equals_line_matcher(expected.negated_matcher)
        assertion_on_negated_matcher.apply_with_message(self.put, self.actual.negated_matcher,
                                                        'negated matcher')

    def visit_and(self, expected: LineMatcherAnd):
        self._common(expected)
        assert isinstance(self.actual, LineMatcherAnd)
        assertion_on_negated_matcher = asrt.matches_sequence(list(map(equals_line_matcher, expected.matchers)))
        assertion_on_negated_matcher.apply_with_message(self.put, self.actual.matchers,
                                                        'matchers')

    def visit_or(self, expected: LineMatcherOr):
        self._common(expected)
        assert isinstance(self.actual, LineMatcherOr)
        assertion_on_negated_matcher = asrt.matches_sequence(list(map(equals_line_matcher, expected.matchers)))
        assertion_on_negated_matcher.apply_with_message(self.put, self.actual.matchers,
                                                        'matchers')
