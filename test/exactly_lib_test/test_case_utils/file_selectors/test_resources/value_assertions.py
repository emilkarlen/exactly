import unittest

from exactly_lib.test_case_utils.file_selectors.file_selectors import FileSelectorStructureVisitor, \
    FileSelectorFromSelectors
from exactly_lib.type_system.file_selector import FileSelector
from exactly_lib.util import dir_contents_selection
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_file_selector(expected: FileSelectorFromSelectors,
                         description: str = '') -> asrt.ValueAssertion:
    """
    :return: A assertion on a :class:`FileSelector`
    """
    return _EqualsAssertion(expected, description)


class _EqualsAssertion(asrt.ValueAssertion):
    def __init__(self,
                 expected: FileSelectorFromSelectors,
                 description: str):
        self.expected = expected
        self.description = description

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        assert_is_file_selector_type = asrt.is_instance(FileSelector, self.description)
        assert_is_file_selector_type.apply_with_message(put, value,
                                                        'Value must be a ' + str(FileSelector))
        assert_is_concrete_file_selector_type = asrt.is_instance(FileSelectorFromSelectors, self.description)
        assert_is_concrete_file_selector_type.apply_with_message(put, value,
                                                                 'Value must be a ' + str(FileSelectorFromSelectors))
        checker = _StructureChecker(put,
                                    message_builder,
                                    self.expected,
                                    self.description
                                    )
        assert isinstance(value, FileSelectorFromSelectors)  # Type info for IDE
        checker.visit(value)


class _StructureChecker(FileSelectorStructureVisitor):
    def __init__(self,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder,
                 expected: FileSelectorFromSelectors,
                 description: str):
        self.put = put
        self.message_builder = message_builder
        self.expected = expected
        self.description = description

    def visit_selectors(self, actual: dir_contents_selection.Selectors):
        self.put.assertEqual(self.expected.selectors.name_patterns,
                             actual.name_patterns,
                             'name patterns')
        self.put.assertEqual(self.expected.selectors.file_types,
                             actual.file_types,
                             'file types')
