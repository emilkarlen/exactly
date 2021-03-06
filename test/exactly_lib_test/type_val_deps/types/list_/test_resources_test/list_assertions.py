import unittest

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import OrReferenceRestrictions
from exactly_lib.type_val_deps.types.list_ import list_sdv as lr, list_sdvs
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_deps.types.string_.strings_ddvs import string_ddv_of_single_string
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.references import reference_to__on_direct_and_indirect
from exactly_lib_test.type_val_deps.types.list_.test_resources import list_assertions as sut
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsElement),
        unittest.makeSuite(TestEqualsResolver),
        unittest.makeSuite(TestEqualsConstantList),
        unittest.makeSuite(TestMatchesResolver),
    ])


class TestEqualsConstantList(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            (
                list_sdvs.empty(),
                []
            ),
            (
                list_sdvs.from_str_constants(['value 1',
                                              'value 2']),
                ['value 1', 'value 2']
            ),
        ]
        for actual, expected in test_cases:
            with self.subTest(expected=repr(expected)):
                sut.equals_constant_list(expected).apply_without_message(self, actual)

    def test_not_equals(self):
        test_cases = [
            (
                list_sdvs.empty(),
                ['non empty']
            ),
            (
                list_sdvs.from_str_constants(['value 1',
                                              'value 2 actual']),
                ['value 1', 'value 2 expected']
            ),
        ]
        for actual, expected in test_cases:
            assertion = sut.equals_constant_list(expected)
            with self.subTest(expected=repr(expected)):
                assert_that_assertion_fails(assertion, actual)


class TestEqualsElement(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            list_sdvs.str_element('value'),
            list_sdvs.symbol_element(reference_to__on_direct_and_indirect('symbol_name')),
        ]
        for element in test_cases:
            with self.subTest(msg=str(element)):
                sut.equals_list_sdv_element(element).apply_without_message(self, element)

    def test_string_not_equals_symbol_ref(self):
        # ARRANGE #
        string_element = list_sdvs.str_element('value')
        symbol_reference_element = list_sdvs.symbol_element(reference_to__on_direct_and_indirect('symbol_name'))
        assertion = sut.equals_list_sdv_element(string_element)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, symbol_reference_element)

    def test_symbol_ref_not_equals_string(self):
        # ARRANGE #
        string_element = list_sdvs.str_element('value')
        symbol_reference_element = list_sdvs.symbol_element(reference_to__on_direct_and_indirect('symbol_name'))
        assertion = sut.equals_list_sdv_element(symbol_reference_element)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, string_element)

    def test_string_not_equals_string_with_different_value(self):
        # ARRANGE #
        expected = list_sdvs.str_element('expected value')
        actual = list_sdvs.str_element('actual value')
        assertion = sut.equals_list_sdv_element(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_symbol_ref_not_equals_symbol_ref_with_different_symbol_name(self):
        # ARRANGE #
        expected = list_sdvs.symbol_element(reference_to__on_direct_and_indirect('expected_symbol_name'))
        actual = list_sdvs.symbol_element(reference_to__on_direct_and_indirect('actual_symbol_name'))
        assertion = sut.equals_list_sdv_element(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)


class TestEqualsResolver(unittest.TestCase):
    def test_equals(self):
        cases = [
            list_sdvs.from_str_constants(['value']),
            list_sdvs.from_elements([list_sdvs.symbol_element(reference_to__on_direct_and_indirect('symbol_name'))]),
        ]
        for sdv in cases:
            with self.subTest(msg=str(sdv)):
                sut.equals_list_sdv(sdv).apply_without_message(self, sdv)

    def test_not_equals(self):
        string_symbol = StringConstantSymbolContext('string_symbol_name',
                                                    'string symbol value')
        cases = [
            Case('different number of elements',
                 expected=
                 list_sdvs.empty(),
                 actual=
                 list_sdvs.from_str_constants(['value']),
                 ),
            Case('different value of single string',
                 expected=
                 list_sdvs.from_str_constants(['expected value']),
                 actual=
                 list_sdvs.from_str_constants(['actual value']),
                 ),
            Case('different element types, but same resolved value',
                 expected=
                 list_sdvs.from_str_constants([string_symbol.str_value]),
                 actual=
                 list_sdvs.from_elements([list_sdvs.symbol_element(string_symbol.reference__w_str_rendering)]),
                 symbols=
                 string_symbol.symbol_table,
                 ),
        ]
        for case in cases:
            with self.subTest(msg=case.name):
                assertion = sut.equals_list_sdv(case.expected, case.symbols)
                assert_that_assertion_fails(assertion, case.actual)


class TestMatchesResolver(unittest.TestCase):
    def test_equals(self):
        string_symbol = StringConstantSymbolContext('string_symbol_name', 'string symbol value')
        cases = [
            MatchesCase('empty list of fragments',
                        expected=
                        lr.ListDdv([]),
                        expected_references=
                        asrt.is_empty_sequence,
                        actual=
                        list_sdvs.empty(),
                        ),
            MatchesCase('single fragment',
                        expected=
                        lr.ListDdv([string_ddv_of_single_string('expected value')]),
                        expected_references=
                        asrt.is_empty_sequence,
                        actual=
                        list_sdvs.from_str_constants(['expected value']),
                        ),
            MatchesCase('symbol reference',
                        expected=
                        lr.ListDdv([string_ddv_of_single_string(string_symbol.str_value)]),
                        expected_references=
                        asrt.matches_sequence([string_symbol.reference_assertion__w_str_rendering]),
                        actual=
                        list_sdvs.from_elements([list_sdvs.string_element(
                            string_sdvs.symbol_reference(string_symbol.reference__w_str_rendering)
                        )]),
                        symbols=
                        string_symbol.symbol_table,
                        ),
        ]
        for case in cases:
            with self.subTest(msg=case.name):
                assertion = sut.matches_list_sdv(case.expected, case.expected_references, case.symbols)
                assertion.apply_without_message(self, case.actual)

    def test_not_equals(self):
        string_symbol = StringConstantSymbolContext('string_symbol_name', 'string symbol value')
        cases = [
            MatchesCase('different number of elements',
                        expected=
                        lr.ListDdv([]),
                        expected_references=
                        asrt.is_empty_sequence,
                        actual=
                        list_sdvs.from_str_constants(['value']),
                        ),
            MatchesCase('different value of single string',
                        expected=
                        lr.ListDdv([string_ddv_of_single_string('expected value')]),
                        expected_references=
                        asrt.is_empty_sequence,
                        actual=
                        list_sdvs.from_str_constants(['actual value']),
                        ),
            MatchesCase('different references',
                        expected=
                        lr.ListDdv([string_ddv_of_single_string(string_symbol.str_value)]),
                        expected_references=
                        asrt.matches_sequence([string_symbol.reference_assertion__w_str_rendering]),
                        actual=
                        list_sdvs.from_elements([list_sdvs.string_element(
                            string_sdvs.symbol_reference(
                                SymbolReference(string_symbol.name,
                                                OrReferenceRestrictions([])),
                            ))]),
                        symbols=
                        string_symbol.symbol_table,
                        ),
        ]
        for case in cases:
            with self.subTest(msg=case.name):
                assertion = sut.matches_list_sdv(case.expected, case.expected_references, case.symbols)
                assert_that_assertion_fails(assertion, case.actual)


class Case:
    def __init__(self,
                 name: str,
                 expected: list_sdvs.ListSdv,
                 actual: list_sdvs.ListSdv,
                 symbols: SymbolTable = None):
        self.name = name
        self.expected = expected
        self.actual = actual
        self.symbols = symbols


class MatchesCase:
    def __init__(self,
                 name: str,
                 expected: lr.ListDdv,
                 expected_references: Assertion,
                 actual: lr.ListSdv,
                 symbols: SymbolTable = None):
        self.name = name
        self.expected = expected
        self.expected_references = expected_references
        self.actual = actual
        self.symbols = symbols
