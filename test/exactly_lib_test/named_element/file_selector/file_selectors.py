import unittest

from exactly_lib.named_element import file_selectors as sut
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.type_system_values.file_selector import SELECT_ALL_FILES
from exactly_lib.type_system_values.value_type import ElementType
from exactly_lib.util import dir_contents_selection as dcs
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.named_element.test_resources.named_elem_utils import container
from exactly_lib_test.named_element.test_resources.resolver_structure_assertions import matches_reference
from exactly_lib_test.named_element.test_resources.restrictions_assertions import is_element_type_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system_values.test_resources.file_selector_assertions import equals_file_selector


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestConstant),
        unittest.makeSuite(TestReference),
        unittest.makeSuite(TestAnd),
    ])


class TestConstant(unittest.TestCase):
    def test_element_type_SHOULD_be_file_selector(self):
        actual = sut.FileSelectorConstant(sut.FileSelector(dcs.all_files()))
        self.assertIs(actual.element_type,
                      ElementType.FILE_SELECTOR)

    def test_SHOULD_have_no_references(self):
        # ARRANGE #
        expected_value = sut.FileSelector(dcs.all_files())
        resolver = sut.FileSelectorConstant(expected_value)
        # ACT #
        actual = resolver.references
        # ASSERT #
        self.assertEqual([],
                         actual)

    def test_resolve(self):
        # ARRANGE #
        expected_value = sut.FileSelector(dcs.all_files())
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
        expected_value = sut.FileSelector(dcs.all_files())
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


class TestAnd(unittest.TestCase):
    def test_element_type_SHOULD_be_file_selector(self):
        actual = sut.FileSelectorAnd([])
        self.assertIs(actual.element_type,
                      ElementType.FILE_SELECTOR)

    def test_SHOULD_report_references_for_all_combined_resolvers(self):
        # ARRANGE #
        name_1 = 'name 1'
        name_2 = 'name 2'

        cases = [
            (
                'no components',
                [],
                asrt.is_empty_list
            ),
            (
                'single component without references',
                [sut.FileSelectorConstant(SELECT_ALL_FILES)],
                asrt.is_empty_list
            ),
            (
                'single component with reference',
                [sut.FileSelectorReference(name_1)],
                asrt.matches_sequence([is_ref_to_file_sel(name_1)])
            ),
            (
                'multiple components with reference',
                [sut.FileSelectorReference(name_1),
                 sut.FileSelectorConstant(SELECT_ALL_FILES),
                 sut.FileSelectorReference(name_2)],
                asrt.matches_sequence([is_ref_to_file_sel(name_1),
                                       is_ref_to_file_sel(name_2)])
            ),
        ]
        for case_name, component_resolvers, expectation_on_references in cases:
            with self.subTest(case_name=case_name):
                resolver = sut.FileSelectorAnd(component_resolvers)
                # ACT #
                actual = resolver.references
                # ASSERT #
                expectation_on_references.apply_without_message(self, actual)

    def test_resolve(self):
        # ARRANGE #
        name_pattern_1 = 'name pattern 1'
        name_pattern_2 = 'name pattern 2'
        cases = [
            (
                'no components',
                [],
                SELECT_ALL_FILES,
            ),
            (
                'single component',
                [const_name_selector(name_pattern_1)],
                name_selector(name_pattern_1),
            ),
            (
                'components with different kind of property',
                [const_name_selector(name_pattern_1),
                 const_type_selector(FileType.REGULAR)],
                sut.FileSelector(dcs.and_all([dcs.name_matches_pattern(name_pattern_1),
                                              dcs.file_type_is(FileType.REGULAR)])),
            ),
            (
                'multiple components with same kind of property',
                [const_name_selector(name_pattern_1),
                 const_name_selector(name_pattern_2),
                 const_type_selector(FileType.REGULAR)],
                sut.FileSelector(dcs.and_all([dcs.name_matches_pattern(name_pattern_1),
                                              dcs.name_matches_pattern(name_pattern_2),
                                              dcs.file_type_is(FileType.REGULAR)])),
            ),
        ]
        named_elements = empty_symbol_table()
        for case_name, component_resolvers, expected_resolved_file_selector in cases:
            resolver = sut.FileSelectorAnd(component_resolvers)
            # ACT #
            actual = resolver.resolve(named_elements)
            # ASSERT #
            expectation = equals_file_selector(expected_resolved_file_selector)
            expectation.apply_without_message(self, actual)


def is_ref_to_file_sel(name_of_referenced_element: str) -> asrt.ValueAssertion:
    return matches_reference(asrt.equals(name_of_referenced_element),
                             is_element_type_restriction(ElementType.FILE_SELECTOR))


def const_name_selector(name_pattern: str) -> sut.FileSelectorResolver:
    return sut.FileSelectorConstant(
        name_selector(name_pattern))


def name_selector(name_pattern) -> sut.FileSelector:
    return sut.FileSelector(
        dcs.Selectors(name_patterns=frozenset([name_pattern])))


def const_type_selector(file_type: FileType) -> sut.FileSelectorResolver:
    return sut.FileSelectorConstant(
        type_selector(file_type))


def type_selector(file_type) -> sut.FileSelector:
    return sut.FileSelector(
        dcs.Selectors(file_types=frozenset([file_type])))
