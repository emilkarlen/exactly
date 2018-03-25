import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.data import list_resolver as lr
from exactly_lib.symbol.data.restrictions import reference_restrictions
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.parse import parse_list as sut
from exactly_lib.util.parse import token as token_syntax
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.data.test_resources.data_symbol_utils import symbol_reference
from exactly_lib_test.symbol.data.test_resources.list_assertions import equals_list_resolver
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()

    ret_val.addTest(unittest.makeSuite(TestInvalidSyntax)),
    ret_val.addTest(unittest.makeSuite(TestEmptyList)),
    ret_val.addTest(unittest.makeSuite(TestSingleElementList)),
    ret_val.addTest(unittest.makeSuite(TestMultipleElementList)),

    return ret_val


class TestInvalidSyntax(unittest.TestCase):
    def test_raise_exception_WHEN_quoting_is_invalid(self):
        cases = [
            remaining_source('"unmatchedDoubleQuote'),
            remaining_source('valid_token \'unmatchedSingleQuote'),
            remaining_source('valid_token \''),
        ]
        for source in cases:
            with self.subTest(source=repr(source.source_string)):
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
                             source=asrt_source.source_is_not_at_end(
                                 current_line_number=asrt.equals(1),
                                 remaining_part_of_current_line=asrt.equals('   '))),
                 ),
            Case('empty line, with following lines',
                 source=
                 remaining_source('', ['contents of following line']),
                 expectation=
                 Expectation(elements=[],
                             source=asrt_source.is_at_end_of_line(1),
                             )
                 ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                _check(self, case)


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
                             [lr.string_element(string_resolvers.string_constant(single_token_value))],
                             source=
                             assert_source(is_at_eof=asrt.is_true)),
                 ),
            Case('single symbol reference, at end of line, on the last line',
                 source=
                 remaining_source(symbol_reference_syntax_for_name(string_symbol.name)),
                 expectation=
                 Expectation(elements=
                             [lr.symbol_element(symbol_reference(string_symbol.name))],
                             source=
                             assert_source(is_at_eof=asrt.is_true)),
                 ),
            Case('complex element (str const and sym-refs), at end of line, on the last line',
                 source=
                 remaining_source(single_token_value +
                                  symbol_reference_syntax_for_name(string_symbol.name)),
                 expectation=
                 Expectation(
                     elements=
                     [
                         lr.string_element(string_resolvers.from_fragments([
                             string_resolvers.ConstantStringFragmentResolver(single_token_value),
                             string_resolvers.SymbolStringFragmentResolver(
                                 SymbolReference(string_symbol.name,
                                                 reference_restrictions.is_any_data_type())
                             ),
                         ]))],
                     source=
                     asrt_source.is_at_end_of_line(1)),
                 ),
            Case('single element, followed by more than one space, on the last line',
                 source=
                 remaining_source(single_token_value + '  ',
                                  []),
                 expectation=
                 Expectation(elements=
                             [lr.string_element(string_resolvers.string_constant(single_token_value))],
                             source=
                             asrt_source.is_at_line(1, ' ')),
                 ),
            Case('single element, followed by single space, on the last line',
                 source=
                 remaining_source(single_token_value + ' ',
                                  []),
                 expectation=
                 Expectation(elements=
                             [lr.string_element(string_resolvers.string_constant(single_token_value))],
                             source=
                             asrt_source.is_at_end_of_line(1)),
                 ),
            Case('single element, followed by space, followed by empty line',
                 source=
                 remaining_source(single_token_value + '  ',
                                  ['']),
                 expectation=
                 Expectation(elements=
                             [lr.string_element(string_resolvers.string_constant(single_token_value))],
                             source=
                             asrt_source.is_at_line(1, ' ')),
                 ),
            Case('single element, at end of line, followed by line with only space',
                 source=
                 remaining_source(single_token_value,
                                  ['   ']),
                 expectation=
                 Expectation(elements=
                             [lr.string_element(string_resolvers.string_constant(single_token_value))],
                             source=
                             asrt_source.is_at_end_of_line(1)),
                 ),
            Case('single element, followed by space, followed by line with only space',
                 source=
                 remaining_source(single_token_value + '  ',
                                  ['   ']),
                 expectation=
                 Expectation(elements=
                             [lr.string_element(string_resolvers.string_constant(single_token_value))],
                             source=
                             asrt_source.is_at_line(1, ' ')),
                 ),
            Case('single element, at end of line, followed by line with invalid quoting',
                 source=
                 remaining_source(single_token_value,
                                  ['"   ']),
                 expectation=
                 Expectation(elements=
                             [lr.string_element(string_resolvers.string_constant(single_token_value))],
                             source=
                             asrt_source.is_at_end_of_line(1)),
                 ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                _check(self, case)


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
                             [lr.string_element(string_resolvers.string_constant(single_token_value_1)),
                              lr.string_element(string_resolvers.string_constant(single_token_value_2))
                              ],
                             source=asrt_source.is_at_end_of_line(1)),
                 ),
            Case('multiple string constants on line that is followed by an empty line',
                 source=
                 remaining_source(single_token_value_1 + ' ' + single_token_value_2,
                                  ['']),
                 expectation=
                 Expectation(elements=
                             [lr.string_element(string_resolvers.string_constant(single_token_value_1)),
                              lr.string_element(string_resolvers.string_constant(single_token_value_2))
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
                             [lr.string_element(string_resolvers.string_constant(single_token_value_1)),
                              lr.string_element(string_resolvers.string_constant(single_token_value_2))
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
                             [lr.symbol_element(symbol_reference(symbol_name)),
                              lr.string_element(
                                  string_resolvers.string_constant(single_token_value))
                              ],
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
                 Expectation(elements=
                 [
                     lr.string_element(string_resolvers.from_fragments([
                         string_resolvers.SymbolStringFragmentResolver(SymbolReference(symbol_name,
                                                                                       reference_restrictions.is_any_data_type())),
                         string_resolvers.ConstantStringFragmentResolver(single_token_value),
                     ])),
                     lr.string_element(
                         string_resolvers.string_constant(single_token_value_1)),
                 ],
                     source=
                     asrt_source.is_at_end_of_line(1)),
                 ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                _check(self, case)


class Expectation:
    def __init__(self,
                 elements: list,
                 source: asrt.ValueAssertion):
        self.elements = elements
        self.source = source


class Case:
    def __init__(self,
                 name: str,
                 source: ParseSource,
                 expectation: Expectation):
        self.name = name
        self.source = source
        self.expectation = expectation


def _check(put: unittest.TestCase, case: Case):
    expected = lr.ListResolver(case.expectation.elements)
    actual = sut.parse_list(case.source)

    assertion = equals_list_resolver(expected)
    assertion.apply_with_message(put, actual, 'list resolver')

    case.expectation.source.apply_with_message(put, case.source, 'source')


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
