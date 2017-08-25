import unittest

from exactly_lib.named_element import restriction as sut
from exactly_lib.named_element.file_selectors import FileSelectorConstant
from exactly_lib.named_element.resolver_structure import ElementType
from exactly_lib.type_system_values.file_selector import SELECT_ALL_FILES
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.named_element.symbol.test_resources import symbol_utils
from exactly_lib_test.named_element.test_resources.named_elem_utils import container


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestElementTypeRestriction),
    ])


class TestElementTypeRestriction(unittest.TestCase):
    type_2_resolver_of_type = {
        ElementType.SYMBOL:
            symbol_utils.string_constant('string value'),

        ElementType.FILE_SELECTOR:
            FileSelectorConstant(SELECT_ALL_FILES),
    }

    def test_satisfied_restriction(self):
        # ARRANGE #
        named_elements = empty_symbol_table()
        for expected_element_type in ElementType:
            container_of_resolver = container(self.type_2_resolver_of_type[expected_element_type])
            with self.subTest(element_type=str(expected_element_type)):
                restriction_to_check = sut.ElementTypeRestriction(expected_element_type)
                # ACT
                error_message = restriction_to_check.is_satisfied_by(named_elements,
                                                                     'name of element',
                                                                     container_of_resolver)
                # ASSERT #
                self.assertIsNone(error_message)

    def test_dissatisfied_restriction(self):
        # ARRANGE #
        cases = {
            ElementType.SYMBOL: ElementType.FILE_SELECTOR,

            ElementType.FILE_SELECTOR: ElementType.SYMBOL,
        }

        named_elements = empty_symbol_table()
        for expected_element_type, unexpected_element_type in cases.items():
            container_of_unexpected = container(self.type_2_resolver_of_type[unexpected_element_type])
            with self.subTest(expected_element_type=str(expected_element_type),
                              unexpected_element_type=str(unexpected_element_type)):
                restriction_to_check = sut.ElementTypeRestriction(expected_element_type)
                # ACT
                error_message = restriction_to_check.is_satisfied_by(named_elements,
                                                                     'name of element',
                                                                     container_of_unexpected)
                # ASSERT #
                self.assertIsNotNone(error_message)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
