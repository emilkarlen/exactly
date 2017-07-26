import unittest

from exactly_lib.instructions.utils.arg_parse import parse_here_doc_or_file_ref as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.type_system_values import file_refs
from exactly_lib.type_system_values.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.type_system_values.file_ref import FileRef
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table
from exactly_lib_test.section_document.test_resources.parse_source import assert_source, is_at_beginning_of_line, \
    source_is_at_end
from exactly_lib_test.symbol.test_resources import here_doc_assertion_utils as hd
from exactly_lib_test.symbol.test_resources.concrete_value_assertions import matches_file_ref_resolver
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.symbol.test_resources.symbol_utils import symbol_table_with_string_values_from_name_and_value
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFileRef),
        unittest.makeSuite(TestHereDoc),
    ])


class TestHereDoc(unittest.TestCase):
    def test_invalid_syntax(self):
        source = remaining_source('<<marker',
                                  ['contents',
                                   'nonMarker'])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_from_parse_source(source)

    def test_without_symbol_references(self):
        expected_contents_line = 'contents'
        source = remaining_source('<<MARKER',
                                  [expected_contents_line] +
                                  ['MARKER',
                                   'Line 4'])
        expectation = ExpectedHereDoc(
            resolved_here_doc_lines=[expected_contents_line],
            common=CommonExpectation(
                symbol_references=[],
                source=is_at_beginning_of_line(4))

        )
        _expect_here_doc(self, source, expectation)

    def test_without_symbol_references__without_following_line(self):
        expected_contents_line = 'contents'
        source = remaining_source('<<MARKER',
                                  [expected_contents_line,
                                   'MARKER',
                                   ])
        expectation = ExpectedHereDoc(
            resolved_here_doc_lines=[expected_contents_line],
            common=CommonExpectation(
                symbol_references=[],
                source=source_is_at_end)

        )
        _expect_here_doc(self, source, expectation)

    def test_with_symbol_references(self):
        symbol1 = NameAndValue('symbol_1_name', 'symbol 1 value')
        line_with_sym_ref_template = 'before symbol {symbol} after symbol'
        source = remaining_source('<<MARKER',
                                  [
                                      line_with_sym_ref_template.format(
                                          symbol=symbol_reference_syntax_for_name(symbol1.name)),
                                      'MARKER',
                                      'Line 4'
                                  ])
        expectation = ExpectedHereDoc(
            resolved_here_doc_lines=[
                line_with_sym_ref_template.format(
                    symbol=symbol1.value)
            ],
            common=CommonExpectation(
                symbol_references=[
                    hd.reference_to(symbol1),
                ],
                symbol_table=symbol_table_with_string_values_from_name_and_value([
                    symbol1,
                ]),
                source=is_at_beginning_of_line(4),
            )

        )
        _expect_here_doc(self, source, expectation)


class TestFileRef(unittest.TestCase):
    def test_without_symbol_references(self):
        file_name = 'file'
        source = remaining_source('{file_name} following args'.format(file_name=file_name),
                                  ['following line'])
        expectation = ExpectedFileRef(
            file_ref_value=file_refs.of_rel_option(sut.CONFIGURATION.options.default_option,
                                                   PathPartAsFixedPath(file_name)),
            common=CommonExpectation(
                symbol_references=[],

                source=assert_source(current_line_number=asrt.equals(1),
                                     remaining_part_of_current_line=asrt.equals(
                                         'following args')))
        )

        _expect_file_ref(self, source, expectation)


class CommonExpectation:
    def __init__(self,
                 symbol_references: list,
                 source: asrt.ValueAssertion,
                 symbol_table: SymbolTable = None):
        self.symbol_references = symbol_references
        self.source = source
        self.symbol_table = empty_symbol_table() if symbol_table is None else symbol_table


class ExpectedFileRef:
    def __init__(self,
                 file_ref_value: FileRef,
                 common: CommonExpectation):
        self.file_ref_value = file_ref_value
        self.common = common


class ExpectedHereDoc:
    def __init__(self,
                 resolved_here_doc_lines: list,
                 common: CommonExpectation):
        self.resolved_here_doc_lines = resolved_here_doc_lines
        self.common = common


def _expect_file_ref(put: unittest.TestCase,
                     source: ParseSource,
                     expectation: ExpectedFileRef):
    # ACT #
    actual = sut.parse_from_parse_source(source)
    # ASSERT #
    put.assertTrue(actual.is_file_ref,
                   'is_file_ref')
    put.assertFalse(actual.is_here_document,
                    'is_here_document')
    symbol_references_assertion = equals_symbol_references(expectation.common.symbol_references)
    expected_file_ref_resolver = matches_file_ref_resolver(expectation.file_ref_value,
                                                           symbol_references_assertion,
                                                           symbol_table=expectation.common.symbol_table)
    expected_file_ref_resolver.apply_with_message(put, actual.file_reference_resolver,
                                                  'file_reference_resolver')
    _expect_common(put, source, actual,
                   expectation.common)


def _expect_here_doc(put: unittest.TestCase,
                     source: ParseSource,
                     expectation: ExpectedHereDoc):
    # ACT #
    actual = sut.parse_from_parse_source(source)
    # ASSERT #
    put.assertTrue(actual.is_here_document,
                   'is_here_document')
    put.assertFalse(actual.is_file_ref,
                    'is_file_ref')
    assertion_on_here_doc = hd.matches_resolved_value(expectation.resolved_here_doc_lines,
                                                      expectation.common.symbol_references,
                                                      expectation.common.symbol_table)
    assertion_on_here_doc.apply_with_message(put, actual.here_document,
                                             'here_document')
    _expect_common(put, source, actual,
                   expectation.common)


def _expect_common(put: unittest.TestCase,
                   actual_source: ParseSource,
                   actual_result: sut.HereDocOrFileRef,
                   expectation: CommonExpectation):
    symbol_references_assertion = equals_symbol_references(expectation.symbol_references)
    symbol_references_assertion.apply_with_message(put, actual_result.symbol_usages,
                                                   'symbol_usages of FileRefOrHereDoc')

    expectation.source.apply_with_message(put, actual_source,
                                          'source_after_parse')
