import unittest

from exactly_lib.named_element import restriction as sut
from exactly_lib.type_system_values.value_type import ElementType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.named_element.symbol.test_resources import symbol_utils
from exactly_lib_test.named_element.test_resources.file_selector import FileSelectorResolverConstantTestImpl
from exactly_lib_test.named_element.test_resources.named_elem_utils import container
from exactly_lib_test.type_system_values.test_resources.file_selector import FileSelectorThatSelectsAllFilesTestImpl


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestElementTypeRestriction),
    ])


class TestElementTypeRestriction(unittest.TestCase):
    type_2_resolver_of_type = {
        ElementType.SYMBOL:
            symbol_utils.string_constant('string value'),

        ElementType.LOGIC:
            FileSelectorResolverConstantTestImpl(FileSelectorThatSelectsAllFilesTestImpl()),
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
            ElementType.SYMBOL: ElementType.LOGIC,

            ElementType.LOGIC: ElementType.SYMBOL,
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
