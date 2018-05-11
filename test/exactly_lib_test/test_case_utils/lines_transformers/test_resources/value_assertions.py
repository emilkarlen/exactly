import unittest

from exactly_lib.test_case_utils.lines_transformer.transformers import LinesTransformerStructureVisitor, \
    ReplaceStringTransformer, \
    SelectStringTransformer
from exactly_lib.type_system.logic.lines_transformer import StringTransformer, IdentityStringTransformer, \
    SequenceStringTransformer, CustomStringTransformer
from exactly_lib_test.test_case_utils.line_matcher.test_resources import value_assertions as asrt_line_matcher
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_lines_transformer(expected: StringTransformer,
                             description: str = '') -> asrt.ValueAssertion[StringTransformer]:
    """
    :return: A assertion on a :class:`LinesTransformer`
    """
    return _EqualsAssertion(expected, description)


class _EqualsAssertion(asrt.ValueAssertion):
    def __init__(self,
                 expected: StringTransformer,
                 description: str):
        self.expected = expected
        self.description = description

    def apply(self,
              put: unittest.TestCase,
              actual,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        assert_is_lines_transformer_type = asrt.is_instance(StringTransformer, self.description)
        assert_is_lines_transformer_type.apply_with_message(
            put, actual,
            message_builder.apply('Value must be a ' + str(StringTransformer)))
        assert isinstance(actual, StringTransformer)  # Type info for IDE
        checker = _EqualityChecker(put,
                                   message_builder,
                                   actual,
                                   self.description
                                   )
        checker.visit(self.expected)


class _EqualityChecker(LinesTransformerStructureVisitor):
    def __init__(self,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder,
                 actual: StringTransformer,
                 description: str):
        self.put = put
        self.message_builder = message_builder.with_description(description)
        self.actual = actual

    def visit_identity(self, expected: IdentityStringTransformer):
        self.put.assertIsInstance(self.actual,
                                  IdentityStringTransformer,
                                  self.message_builder.apply('class'))

    def visit_replace(self, expected: ReplaceStringTransformer):
        self.put.assertIsInstance(self.actual,
                                  ReplaceStringTransformer,
                                  self.message_builder.apply('class'))
        assert isinstance(self.actual, ReplaceStringTransformer)  # Type info for IDE
        self.put.assertEqual(expected.regex_pattern_string,
                             self.actual.regex_pattern_string,
                             self.message_builder.apply('regex pattern string'))
        self.put.assertEqual(expected.replacement,
                             self.actual.replacement,
                             self.message_builder.apply('replacement'))

    def visit_select(self, expected: SelectStringTransformer):
        self.put.assertIsInstance(self.actual,
                                  SelectStringTransformer,
                                  self.message_builder.apply('class'))
        assert isinstance(self.actual, SelectStringTransformer)  # Type info for IDE
        assertion_on_line_matcher = asrt_line_matcher.equals_line_matcher(expected.line_matcher)
        assertion_on_line_matcher.apply_with_message(self.put, self.actual.line_matcher,
                                                     'line matcher')

    def visit_sequence(self, expected: SequenceStringTransformer):
        self.put.assertIsInstance(self.actual,
                                  SequenceStringTransformer,
                                  self.message_builder.apply('class'))
        assert isinstance(self.actual, SequenceStringTransformer)  # Type info for IDE
        assert_components_equals = asrt.matches_sequence(list(map(equals_lines_transformer,
                                                                  expected.transformers)))
        assert_components_equals.apply_with_message(self.put,
                                                    list(self.actual.transformers),
                                                    'component transformers'
                                                    )

    def visit_custom(self, expected: CustomStringTransformer):
        self.put.assertIsInstance(self.actual,
                                  CustomStringTransformer,
                                  self.message_builder.apply('class'))
        assert isinstance(self.actual, CustomStringTransformer)  # Type info for IDE
