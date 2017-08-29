import unittest

from exactly_lib.type_system_values.lines_transformer import LinesTransformer, LinesTransformerStructureVisitor, \
    CustomLinesTransformer, IdentityLinesTransformer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_lines_transformer(expected: LinesTransformer,
                             description: str = '') -> asrt.ValueAssertion:
    """
    :return: A assertion on a :class:`FileSelector`
    """
    return _EqualsAssertion(expected, description)


class _EqualsAssertion(asrt.ValueAssertion):
    def __init__(self,
                 expected: LinesTransformer,
                 description: str):
        self.expected = expected
        self.description = description

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        assert_is_file_selector_type = asrt.is_instance(LinesTransformer, self.description)
        assert_is_file_selector_type.apply_with_message(put, value,
                                                        'Value must be a ' + str(LinesTransformer))
        assert isinstance(value, LinesTransformer)  # Type info for IDE
        checker = _EqualityChecker(put,
                                   message_builder,
                                   value,
                                   self.description
                                   )
        checker.visit(self.expected)


class _EqualityChecker(LinesTransformerStructureVisitor):
    def __init__(self,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder,
                 actual: LinesTransformer,
                 description: str):
        self.put = put
        self.message_builder = message_builder
        self.actual = actual
        self.description = description

    def visit_custom(self, expected: CustomLinesTransformer):
        builder_with_description = self.message_builder.with_description(self.description)
        self.put.assertIsInstance(self.actual,
                                  CustomLinesTransformer,
                                  builder_with_description.apply('class'))
        assert isinstance(self.actual, CustomLinesTransformer)  # Type info for IDE
        self.put.assertEqual(expected.name,
                             self.actual.name,
                             builder_with_description.apply('name'))

    def visit_identity(self, expected: IdentityLinesTransformer):
        builder_with_description = self.message_builder.with_description(self.description)
        self.put.assertIsInstance(self.actual,
                                  IdentityLinesTransformer,
                                  builder_with_description.apply('class'))
