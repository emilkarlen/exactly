import unittest
from typing import List, Sequence

from exactly_lib.definitions.test_case import reserved_words
from exactly_lib.impls.types.list_ import parse_list as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions
from exactly_lib.type_val_deps.types.list_ import defs
from exactly_lib.type_val_deps.types.list_ import list_sdv as lr, list_sdvs
from exactly_lib.type_val_deps.types.list_.list_sdv import ElementSdv
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse import token as token_syntax
from exactly_lib_test.impls.types.parse.test_resources.invalid_source_tokens import TOKENS_WITH_INVALID_SYNTAX
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions as asrt_data_rest
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.references import reference_to__on_direct_and_indirect
from exactly_lib_test.type_val_deps.types.list_.test_resources.list_assertions import equals_list_sdv


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()

    ret_val.addTest(unittest.makeSuite(TestInvalidSyntax)),
    ret_val.addTest(unittest.makeSuite(TestEmptyList)),
    ret_val.addTest(unittest.makeSuite(TestSingleElementList)),
    ret_val.addTest(unittest.makeSuite(TestMultipleElementList)),

    return ret_val


class TestInvalidSyntax(unittest.TestCase):
    def test_raise_exception_WHEN_quoting_of_first_token_is_invalid(self):
        for case in TOKENS_WITH_INVALID_SYNTAX:
            with self.subTest(name=case.name,
                              source=case.value):
                source = remaining_source(case.value)
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_list(source)

    def test_raise_exception_WHEN_quoting_of_second_token_is_invalid(self):
        for case in TOKENS_WITH_INVALID_SYNTAX:
            source = remaining_source('valid' + ' ' + case.value)
            with self.subTest(name=case.name,
                              source=case.value):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_list(source)

    def test_raise_exception_WHEN_element_is_a_reserved_word_that_is_not_r_paren(self):
        for illegal_string in set(reserved_words.RESERVED_TOKENS).difference(reserved_words.PAREN_END):
            source = remaining_source(illegal_string)
            with self.subTest(illegal_string):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_list(source)


class TestEmptyList(unittest.TestCase):
    def test(self):
        cases = [
            Case('empty line with no following lines',
                 source=
                 remaining_source(''),
                 expectation=
                 Expectation(elements=[],
                             source=asrt_source.is_at_end_of_line(1)),
                 ),
            Case('only white space on current line, with no following lines',
                 source=
                 remaining_source('   '),
                 expectation=
                 Expectation(elements=[],
                             source=asrt_source.is_at_end_of_line(1)),
                 ),
            Case('empty line, with following lines',
                 source=
                 remaining_source('', ['contents of following line']),
                 expectation=
                 Expectation(elements=[],
                             source=asrt_source.is_at_end_of_line(1),
                             )
                 ),
            Case('line with r-paren',
                 source=
                 remaining_source(reserved_words.PAREN_END, ['contents of following line']),
                 expectation=
                 Expectation(elements=[],
                             source=asrt_source.source_is_not_at_end(
                                 current_line_number=asrt.equals(1),
                                 remaining_part_of_current_line=asrt.equals(reserved_words.PAREN_END)),
                             )
                 ),
            Case('line with continuation-token, followed by empty line',
                 source=
                 remaining_source(defs.CONTINUATION_TOKEN, ['']),
                 expectation=
                 Expectation(elements=[],
                             source=asrt_source.is_at_end_of_line(2),
                             )
                 ),
            Case('line with continuation-token (followed by space), followed by empty line',
                 source=
                 remaining_source(defs.CONTINUATION_TOKEN + '  ', ['']),
                 expectation=
                 Expectation(elements=[],
                             source=asrt_source.is_at_end_of_line(2),
                             )
                 ),
        ]
        # ACT & ASSERT #
        _test_cases(self, cases)


class TestSingleElementList(unittest.TestCase):
    def test(self):
        single_token_value = 'single_token_value'
        string_symbol = NameAndValue('string_symbol_name', 'string symbol value')
        cases = [
            Case('single string constant, at end of line, on the last line',
                 source=
                 remaining_source(single_token_value),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element(single_token_value)],
                             source=
                             assert_source(is_at_eof=asrt.is_true)),
                 ),
            Case('single symbol reference, at end of line, on the last line',
                 source=
                 remaining_source(symbol_reference_syntax_for_name(string_symbol.name)),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.symbol_element(reference_to__on_direct_and_indirect(string_symbol.name))],
                             source=
                             assert_source(is_at_eof=asrt.is_true),
                             references=
                             asrt.matches_sequence([asrt_sym_ref.matches_reference_2(
                                 string_symbol.name,
                                 asrt_data_rest.is__w_str_rendering())
                             ])),
                 ),
            Case('complex element (str const and sym-refs), at end of line, on the last line',
                 source=
                 remaining_source(single_token_value +
                                  symbol_reference_syntax_for_name(string_symbol.name)),
                 expectation=
                 Expectation(
                     elements=
                     [
                         list_sdvs.string_element(string_sdvs.from_fragments([
                             string_sdvs.str_fragment(single_token_value),
                             string_sdvs.symbol_fragment(
                                 SymbolReference(
                                     string_symbol.name,
                                     reference_restrictions.is_any_type_w_str_rendering(),
                                 )
                             ),
                         ]))],
                     references=
                     asrt.matches_sequence([asrt_sym_ref.matches_reference_2(
                         string_symbol.name,
                         asrt_data_rest.is__w_str_rendering())
                     ]),
                     source=
                     asrt_source.is_at_end_of_line(1)),
                 ),
            Case('single element, followed by more than one space, on the last line',
                 source=
                 remaining_source(single_token_value + '  ',
                                  []),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element(single_token_value)],
                             source=
                             asrt_source.is_at_end_of_line(1)),
                 ),
            Case('single element, followed by single space, on the last line',
                 source=
                 remaining_source(single_token_value + ' ',
                                  []),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element(single_token_value)],
                             source=
                             asrt_source.is_at_end_of_line(1)),
                 ),
            Case('single element, followed by space, followed by empty line',
                 source=
                 remaining_source(single_token_value + '  ',
                                  ['']),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element(single_token_value)],
                             source=
                             asrt_source.is_at_end_of_line(1)),
                 ),
            Case('single element, at end of line, followed by line with only space',
                 source=
                 remaining_source(single_token_value,
                                  ['   ']),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element(single_token_value)],
                             source=
                             asrt_source.is_at_end_of_line(1)),
                 ),
            Case('single element, followed by space, followed by line with only space',
                 source=
                 remaining_source(single_token_value + '  ',
                                  ['   ']),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element(single_token_value)],
                             source=
                             asrt_source.is_at_end_of_line(1)),
                 ),
            Case('single element, at end of line, followed by line with invalid quoting',
                 source=
                 remaining_source(single_token_value,
                                  ['"   ']),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element(single_token_value)],
                             source=
                             asrt_source.is_at_end_of_line(1)),
                 ),
            Case('continuation token, followed by line with single element',
                 source=
                 remaining_source(defs.CONTINUATION_TOKEN,
                                  [single_token_value]),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element(single_token_value)],
                             source=
                             asrt_source.is_at_end_of_line(2)),
                 ),
            Case('single element, followed by continuation token, followed by empty line',
                 source=
                 remaining_source(single_token_value + ' ' + defs.CONTINUATION_TOKEN,
                                  ['']),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element(single_token_value)],
                             source=
                             asrt_source.is_at_end_of_line(2)),
                 ),
            Case('single element, followed by r-paren and more',
                 source=
                 remaining_source(' '.join((single_token_value, reserved_words.PAREN_END, 'const_str')),
                                  ['"   ']),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element(single_token_value)],
                             source=
                             asrt_source.source_is_not_at_end(
                                 current_line_number=asrt.equals(1),
                                 remaining_part_of_current_line=asrt.equals(
                                     ' '.join((reserved_words.PAREN_END, 'const_str')))
                             )
                             ),
                 ),
        ]
        # ACT & ASSERT #
        _test_cases(self, cases)


class TestMultipleElementList(unittest.TestCase):
    def test(self):
        single_token_value = 'single_token_value'
        single_token_value_1 = 'single_token_value_1'
        single_token_value_2 = 'single_token_value_2'
        symbol_name = 'a_symbol_name'
        cases = [
            Case('multiple string constants on line that is the last line',
                 source=
                 remaining_source(single_token_value_1 + ' ' + single_token_value_2),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element(single_token_value_1),
                              list_sdvs.str_element(single_token_value_2)
                              ],
                             source=asrt_source.is_at_end_of_line(1)),
                 ),
            Case('multiple string constants on line that is followed by an empty line',
                 source=
                 remaining_source(single_token_value_1 + ' ' + single_token_value_2,
                                  ['']),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element(single_token_value_1),
                              list_sdvs.str_element(single_token_value_2)
                              ],
                             source=
                             asrt_source.is_at_end_of_line(1)),
                 ),
            Case('multiple string constants on line that is followed by a non-empty line',
                 source=
                 remaining_source(single_token_value_1 + ' ' + single_token_value_2,
                                  ['  ']),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element(single_token_value_1),
                              list_sdvs.str_element(single_token_value_2)
                              ],
                             source=
                             asrt_source.is_at_end_of_line(1)),
                 ),
            Case('symbol-reference and string constant on first line',
                 source=
                 remaining_source('{sym_ref} {string_constant}'.format(
                     sym_ref=symbol_reference_syntax_for_name(symbol_name),
                     string_constant=single_token_value)),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.symbol_element(reference_to__on_direct_and_indirect(symbol_name)),
                              list_sdvs.str_element(single_token_value)
                              ],
                             references=
                             asrt.matches_sequence([asrt_sym_ref.matches_reference_2(
                                 symbol_name,
                                 asrt_data_rest.is__w_str_rendering())
                             ]),
                             source=
                             asrt_source.is_at_end_of_line(1)),
                 ),
            Case('complex element (sym-ref and str const) and string constant, '
                 'followed by space, '
                 'followed by non-empty line',
                 source=
                 remaining_source(symbol_reference_syntax_for_name(symbol_name) +
                                  single_token_value +
                                  ' ' +
                                  single_token_value_1,
                                  ['   ']),
                 expectation=
                 Expectation(
                     elements=
                     [
                         list_sdvs.string_element(string_sdvs.from_fragments([
                             string_sdvs.symbol_fragment(SymbolReference(
                                 symbol_name,
                                 reference_restrictions.is_any_type_w_str_rendering()),
                             ),
                             string_sdvs.str_fragment(single_token_value),
                         ])),
                         list_sdvs.str_element(single_token_value_1),
                     ],
                     references=
                     asrt.matches_sequence([asrt_sym_ref.matches_reference_2(
                         symbol_name,
                         asrt_data_rest.is__w_str_rendering())
                     ]),
                     source=
                     asrt_source.is_at_end_of_line(1)),
                 ),
            Case('multiple string constants on line followed by r-paren',
                 source=
                 remaining_source(' '.join((single_token_value_1,
                                            single_token_value_2,
                                            reserved_words.PAREN_END,
                                            'constant')),
                                  ['  ']),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element(single_token_value_1),
                              list_sdvs.str_element(single_token_value_2)
                              ],
                             source=
                             asrt_source.source_is_not_at_end(
                                 current_line_number=asrt.equals(1),
                                 remaining_part_of_current_line=asrt.equals(
                                     ' '.join((reserved_words.PAREN_END, 'constant')))
                             )
                             ),
                 ),
            Case('1st string on first line, followed by continuation-token, followed by line with 2nd string',
                 source=
                 remaining_source(single_token_value_1 + ' ' + defs.CONTINUATION_TOKEN,
                                  [single_token_value_2]),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element(single_token_value_1),
                              list_sdvs.str_element(single_token_value_2)
                              ],
                             source=
                             asrt_source.is_at_end_of_line(2)),
                 ),
            Case('multiple elements on two lines, separated by continuation token',
                 source=
                 remaining_source('a b ' + defs.CONTINUATION_TOKEN,
                                  ['  c d  ']),
                 expectation=
                 Expectation(elements=
                             [list_sdvs.str_element('a'),
                              list_sdvs.str_element('b'),
                              list_sdvs.str_element('c'),
                              list_sdvs.str_element('d'),
                              ],
                             source=
                             asrt_source.is_at_end_of_line(2)
                             ),
                 ),
        ]
        # ACT & ASSERT #
        _test_cases(self, cases)


class Expectation:
    def __init__(self,
                 elements: List[ElementSdv],
                 source: Assertion[ParseSource],
                 references: Assertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                 ):
        self.elements = elements
        self.source = source
        self.references = references


class Case:
    def __init__(self,
                 name: str,
                 source: ParseSource,
                 expectation: Expectation):
        self.name = name
        self.source = source
        self.expectation = expectation


def _test_cases(put: unittest.TestCase, cases: Sequence[Case]):
    for case in cases:
        with put.subTest(case.name):
            _test_case(put, case)


def _test_case(put: unittest.TestCase, case: Case):
    # ACT #
    actual = sut.parse_list(case.source)

    # ASSERT #
    check_elements(put, case.expectation.elements,
                   actual)
    case.expectation.references.apply_with_message(put,
                                                   actual.references,
                                                   'symbol references')
    case.expectation.source.apply_with_message(put, case.source, 'source')


def check_elements(put: unittest.TestCase,
                   expected_elements: List[ElementSdv],
                   actual: lr.ListSdv):
    expected = lr.ListSdv(expected_elements)
    assertion = equals_list_sdv(expected)
    assertion.apply_with_message(put, actual, 'list sdv')


def _src(s: str,
         **kwargs) -> str:
    if not kwargs:
        return s.format_map(_STD_FORMAT_MAP)
    else:
        formats = dict(_STD_FORMAT_MAP, **kwargs)
        return s.format_map(formats)


_STD_FORMAT_MAP = {
    'soft_quote': token_syntax.SOFT_QUOTE_CHAR,
    'hard_quote': token_syntax.HARD_QUOTE_CHAR,
}
