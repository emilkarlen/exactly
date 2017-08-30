import pathlib
import unittest

from exactly_lib.named_element.resolver_structure import LinesTransformerResolver
from exactly_lib.test_case_utils.file_selectors.resolvers import FileSelectorConstant
from exactly_lib.test_case_utils.lines_transformers.resolvers import LinesTransformerConstant
from exactly_lib.test_case_utils.lines_transformers.transformers import IdentityLinesTransformer, \
    SequenceLinesTransformer
from exactly_lib.type_system_values.file_selector import FileSelector
from exactly_lib.type_system_values.lines_transformer import LinesTransformer
from exactly_lib.util.symbol_table import singleton_symbol_table_2, SymbolTable
from exactly_lib_test.named_element.symbol.test_resources import symbol_utils
from exactly_lib_test.named_element.test_resources import named_elem_utils
from exactly_lib_test.test_case_utils.lines_transformers.test_resources import resolver_assertions as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestResolvedValueEqualsLinesTransformer),
    ])


class TestResolvedValueEqualsLinesTransformer(unittest.TestCase):
    def test_equals_lines_transformer(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             named_elem_utils.container(ARBITRARY_LINE_TRANSFORMER_RESOLVER),
                         )),

        ]
        actual_and_expected = IdentityLinesTransformer()
        resolver = LinesTransformerConstant(actual_and_expected)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.resolved_value_equals_lines_transformer(actual_and_expected,
                                                                                 symbols=case.value)
                # ACT & ASSERT #
                assertion_to_check.apply_without_message(self, resolver)

    def test_SHOULD_not_equal_lines_transformer_WHEN_actual_is_file_selector(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             named_elem_utils.container(ARBITRARY_LINE_TRANSFORMER_RESOLVER),
                         )),

        ]
        actual = FileSelectorTestImpl()
        expected = IdentityLinesTransformer()

        resolver_of_actual = FileSelectorConstant(actual)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_equals_expected = sut.resolved_value_equals_lines_transformer(expected,
                                                                                        symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_equals_expected, resolver_of_actual)

    def test_SHOULD_not_equal_lines_transformer_WHEN_actual_is_different_lines_transformer(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             named_elem_utils.container(ARBITRARY_LINE_TRANSFORMER_RESOLVER),
                         )),

        ]
        actual = SequenceLinesTransformer([])
        expected = IdentityLinesTransformer()

        resolver_of_actual = LinesTransformerConstant(actual)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_equals_expected = sut.resolved_value_equals_lines_transformer(expected,
                                                                                        symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_equals_expected, resolver_of_actual)

    def test_equals_references(self):
        # ARRANGE #
        actual_reference = symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        actual_resolver = LinesTransformerResolverWithHardCodedValues(
            IdentityLinesTransformer(),
            references=actual_references)
        assertion_to_check = sut.resolved_value_equals_lines_transformer(actual_resolver.resolved_value,
                                                                         references=asrt.matches_sequence([
                                                                             asrt.is_(actual_reference)
                                                                         ]),
                                                                         )
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, actual_resolver)

    def test_not_equals_references(self):
        # ARRANGE #
        actual_reference = symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        actual_resolver = LinesTransformerResolverWithHardCodedValues(
            IdentityLinesTransformer(),
            references=actual_references)

        cases = [
            NameAndValue('assert no references',
                         asrt.is_empty_list),
            NameAndValue('assert single invalid reference',
                         asrt.matches_sequence([
                             asrt.not_(asrt.is_(actual_reference))
                         ])),
        ]

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.resolved_value_equals_lines_transformer(actual_resolver.resolved_value,
                                                                                 references=case.value,
                                                                                 )
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, actual_resolver)


class FileSelectorTestImpl(FileSelector):
    def select_from(self, directory: pathlib.Path) -> iter:
        raise NotImplementedError('should never be used')


class LinesTransformerResolverWithHardCodedValues(LinesTransformerResolver):
    def __init__(self,
                 resolved_value: LinesTransformer,
                 references: list):
        self.resolved_value = resolved_value
        self._references = references

    def resolve(self, named_elements: SymbolTable) -> LinesTransformer:
        return self.resolved_value

    @property
    def references(self) -> list:
        return self._references


ARBITRARY_LINE_TRANSFORMER_RESOLVER = LinesTransformerResolverWithHardCodedValues(IdentityLinesTransformer(), [])

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
