import unittest

from exactly_lib.named_element import file_selectors as sut
from exactly_lib.named_element.resolver_structure import ElementType
from exactly_lib.util import dir_contents_selection
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.named_element.test_resources.named_elem_utils import container
from exactly_lib_test.named_element.test_resources.resolver_structure_assertions import matches_reference
from exactly_lib_test.named_element.test_resources.restrictions_assertions import is_element_type_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestConstant),
        unittest.makeSuite(TestReference),
    ])


class TestConstant(unittest.TestCase):
    def test_element_type_SHOULD_be_file_selector(self):
        actual = sut.FileSelectorConstant(sut.FileSelector(dir_contents_selection.all_files()))
        self.assertIs(actual.element_type,
                      ElementType.FILE_SELECTOR)

    def test_SHOULD_have_no_references(self):
        # ARRANGE #
        expected_value = sut.FileSelector(dir_contents_selection.all_files())
        resolver = sut.FileSelectorConstant(expected_value)
        # ACT #
        actual = resolver.references
        # ASSERT #
        self.assertEqual([],
                         actual)

    def test_resolve(self):
        # ARRANGE #
        expected_value = sut.FileSelector(dir_contents_selection.all_files())
        resolver = sut.FileSelectorConstant(expected_value)
        # ACT #
        actual_value = resolver.resolve(empty_symbol_table())
        # ASSERT #
        self.assertIs(expected_value,
                      actual_value)


class TestReference(unittest.TestCase):
    def test_element_type_SHOULD_be_file_selector(self):
        actual = sut.FileSelectorReference('name of referenced selector')
        self.assertIs(actual.element_type,
                      ElementType.FILE_SELECTOR)

    def test_SHOULD_have_a_single_reference(self):
        # ARRANGE #
        name_of_referenced_resolver = 'name of referenced selector'
        resolver = sut.FileSelectorReference(name_of_referenced_resolver)
        # ACT #
        actual = resolver.references
        # ASSERT #
        assert_single_reference = asrt.matches_sequence([
            matches_reference(asrt.equals(name_of_referenced_resolver),
                              is_element_type_restriction(ElementType.FILE_SELECTOR),
                              )
        ])
        assert_single_reference.apply_without_message(self, actual)

    def test_resolve(self):
        # ARRANGE #
        name_of_referenced_element = 'name of referenced selector'
        expected_value = sut.FileSelector(dir_contents_selection.all_files())
        resolver = sut.FileSelectorReference(name_of_referenced_element)
        # ACT #
        named_elements = SymbolTable({
            name_of_referenced_element:
                container(sut.FileSelectorConstant(expected_value))
        })
        actual_value = resolver.resolve(named_elements)
        # ASSERT #
        self.assertIs(expected_value,
                      actual_value)
