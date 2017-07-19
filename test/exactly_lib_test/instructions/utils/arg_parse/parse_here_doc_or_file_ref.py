import unittest

from exactly_lib.instructions.utils.arg_parse import parse_here_doc_or_file_ref as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.type_system_values import file_refs
from exactly_lib.type_system_values.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.type_system_values.file_ref import FileRef
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table
from exactly_lib_test.section_document.test_resources.parse_source import assert_source
from exactly_lib_test.symbol.test_resources.concrete_value_assertions import matches_file_ref_resolver
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestHereDoc),
        unittest.makeSuite(TestFileRef),
    ])


class TestHereDoc(unittest.TestCase):
    def test_without_symbol_references(self):
        expected_contents_line = 'contents'
        source = remaining_source('<<MARKER',
                                  [expected_contents_line] +
                                  ['MARKER',
                                   'Line 4'])
        expectation = ExpectedHereDoc(
            here_doc_value=asrt.equals([expected_contents_line]),
            common=CommonExpectation(
                symbol_references=asrt.is_empty_list,
                source=assert_source(current_line_number=asrt.equals(4),
                                     column_index=asrt.equals(0),
                                     remaining_part_of_current_line=asrt.equals('Line 4')))

        )
        _expect_here_doc(self, source, expectation)

    def test_invalid_syntax(self):
        source = remaining_source('<<marker',
                                  ['contents',
                                   'nonMarker'])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_from_parse_source(source)


class TestFileRef(unittest.TestCase):
    def test_without_symbol_references(self):
        file_name = 'file'
        source = remaining_source('{file_name} following args'.format(file_name=file_name),
                                  ['following line'])
        expectation = ExpectedFileRef(
            file_ref_value=file_refs.of_rel_option(sut.CONFIGURATION.options.default_option,
                                                   PathPartAsFixedPath(file_name)),
            common=CommonExpectation(
                symbol_references=asrt.is_empty_list,

                source=assert_source(current_line_number=asrt.equals(1),
                                     remaining_part_of_current_line=asrt.equals(
                                         'following args')))
        )

        _expect_file_ref(self, source, expectation)


class CommonExpectation:
    def __init__(self,
                 symbol_references: asrt.ValueAssertion,
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
                 here_doc_value: asrt.ValueAssertion,
                 common: CommonExpectation):
        self.here_doc_value = here_doc_value
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
    expected_file_ref_resolver = matches_file_ref_resolver(expectation.file_ref_value,
                                                           expectation.common.symbol_references,
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
    expectation.here_doc_value.apply_with_message(put, actual.here_document,
                                                  'here_document')
    _expect_common(put, source, actual,
                   expectation.common)


def _expect_common(put: unittest.TestCase,
                   actual_source: ParseSource,
                   actual_result: sut.HereDocOrFileRef,
                   expectation: CommonExpectation):
    expectation.symbol_references.apply_with_message(put, actual_result.symbol_usages,
                                                     'symbol_usages')

    expectation.source.apply_with_message(put, actual_source,
                                          'source_after_parse')
