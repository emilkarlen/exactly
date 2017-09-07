import unittest

from exactly_lib.test_case_utils.file_matcher.file_matchers import FileMatcherStructureVisitor, \
    FileMatcherFromSelectors
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_file_matcher(expected: FileMatcherFromSelectors,
                        description: str = '') -> asrt.ValueAssertion:
    """
    :return: A assertion on a :class:`FileMatcher`
    """
    return _EqualsAssertion(expected, description)


class _EqualsAssertion(asrt.ValueAssertion):
    def __init__(self,
                 expected: FileMatcherFromSelectors,
                 description: str):
        self.expected = expected
        self.description = description

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        assert_is_file_selector_type = asrt.is_instance(FileMatcher, self.description)
        assert_is_file_selector_type.apply_with_message(put, value,
                                                        'Value must be a ' + str(FileMatcher))
        assert_is_concrete_file_selector_type = asrt.is_instance(FileMatcherFromSelectors, self.description)
        assert_is_concrete_file_selector_type.apply_with_message(put, value,
                                                                 'Value must be a ' + str(FileMatcherFromSelectors))
        checker = _StructureChecker(put,
                                    message_builder,
                                    self.expected,
                                    self.description
                                    )
        assert isinstance(value, FileMatcherFromSelectors)  # Type info for IDE
        checker.visit(value)


class _StructureChecker(FileMatcherStructureVisitor):
    def __init__(self,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder,
                 expected: FileMatcherFromSelectors,
                 description: str):
        self.put = put
        self.message_builder = message_builder
        self.expected = expected
        self.description = description

    def visit_selectors(self, actual: FileMatcherFromSelectors):
        self.put.assertEqual(self.expected.selectors.name_patterns,
                             actual.selectors.name_patterns,
                             'name patterns')
        self.put.assertEqual(self.expected.selectors.file_types,
                             actual.selectors.file_types,
                             'file types')
