import unittest

from exactly_lib.named_element import file_selector as sut
from exactly_lib.named_element.resolver_structure import ElementType
from exactly_lib.util import dir_contents_selection
from exactly_lib.util.symbol_table import empty_symbol_table


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
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
