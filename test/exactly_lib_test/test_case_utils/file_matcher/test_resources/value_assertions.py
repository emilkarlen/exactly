import unittest

from exactly_lib.test_case_utils.file_matcher import file_matchers
from exactly_lib.test_case_utils.file_matcher.file_matchers import FileMatcherStructureVisitor, \
    FileMatcherFromSelectors
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_file_matcher(expected: FileMatcher,
                        description: str = '') -> asrt.ValueAssertion:
    """
    :return: A assertion on a :class:`FileMatcher`
    """
    return _EqualsAssertion(expected, description)


class _EqualsAssertion(asrt.ValueAssertion):
    def __init__(self,
                 expected: FileMatcher,
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
        checker = _StructureChecker(put,
                                    message_builder,
                                    self.expected,
                                    self.description
                                    )
        checker.visit(value)


class _StructureChecker(FileMatcherStructureVisitor):
    def __init__(self,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder,
                 expected: FileMatcher,
                 description: str):
        self.put = put
        self.message_builder = message_builder
        self.expected = expected
        self.description = description

    def _common(self, actual: file_matchers.FileMatcher):
        self.put.assertIsInstance(actual,
                                  type(self.expected),
                                  'class')
        self.put.assertEqual(actual.option_description,
                             self.expected.option_description,
                             'option_description')

    def visit_name_glob_pattern(self, actual: file_matchers.FileMatcherNameGlobPattern):
        self._common(actual)
        assert isinstance(self.expected, file_matchers.FileMatcherNameGlobPattern)  # Type info for IDE
        self.put.assertEqual(self.expected.glob_pattern,
                             actual.glob_pattern,
                             'glob_pattern')

    def visit_constant(self, actual: file_matchers.FileMatcherConstant):
        self._common(actual)
        assert isinstance(self.expected, file_matchers.FileMatcherConstant)  # Type info for IDE
        self.put.assertEqual(self.expected.result_constant,
                             actual.result_constant,
                             'result_constant')

    def visit_type(self, actual: file_matchers.FileMatcherType):
        self._common(actual)
        assert isinstance(self.expected, file_matchers.FileMatcherType)  # Type info for IDE
        self.put.assertEqual(self.expected.file_type,
                             actual.file_type,
                             'file_type')

    def visit_selectors(self, actual: FileMatcherFromSelectors):
        self._common(actual)
        assert isinstance(self.expected, FileMatcherFromSelectors)  # Type info for IDE
        self.put.assertEqual(self.expected.selectors.name_patterns,
                             actual.selectors.name_patterns,
                             'name patterns')
        self.put.assertEqual(self.expected.selectors.file_types,
                             actual.selectors.file_types,
                             'file types')
