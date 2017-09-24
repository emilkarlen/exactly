import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref as sut
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.test_case_utils.parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.parse.token import SOFT_QUOTE_CHAR
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table, singleton_symbol_table_2
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source_lines
from exactly_lib_test.symbol.data.test_resources import here_doc_assertion_utils as asrt_hd
from exactly_lib_test.symbol.data.test_resources import references
from exactly_lib_test.symbol.data.test_resources import string_assertions as asrt_string
from exactly_lib_test.symbol.data.test_resources.concrete_value_assertions import matches_file_ref_resolver
from exactly_lib_test.symbol.data.test_resources.data_symbol_utils import string_constant_container
from exactly_lib_test.symbol.data.test_resources.data_symbol_utils import \
    symbol_table_with_string_values_from_name_and_value, file_ref_constant_container
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case_utils.parse.parse_file_ref import file_ref_reference_restrictions
from exactly_lib_test.test_case_utils.parse.test_resources import relativity_arguments
from exactly_lib_test.test_case_utils.test_resources.relativity_options import \
    OptionStringConfigurationForRelativityOption
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.data.test_resources import concrete_path_parts
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes_str


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestString),
        unittest.makeSuite(TestHereDoc),
        unittest.makeSuite(TestFileRef),
    ])


class TestString(unittest.TestCase):
    def test_invalid_syntax(self):
        cases = [
            NameAndValue('missing end quote',
                         [
                             '{soft_quote} some text'.format(soft_quote=SOFT_QUOTE_CHAR),
                         ]),
            # Case with missing  start quote is not handled - it is a bug
            # The lookahead of TokenParser is the cause.
        ]
        for case in cases:
            source = remaining_source_lines(case.value)
            with self.subTest(case_name=case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_from_parse_source(source)

    def test_valid_syntax_without_symbol_references(self):
        single_string_token_value = 'singleStringTokenValue'
        multiple_tokens_string_value = 'multiple tokens string value'
        following_arg_token = 'singleToken'
        cases = [
            NameAndValue('non-quoted string-token on single line',
                         (
                             [
                                 single_string_token_value,
                             ],
                             ExpectedString(single_string_token_value,
                                            CommonExpectation(
                                                symbol_references=[],
                                                source=asrt_source.is_at_end_of_line(1)))
                         )
                         ),
            NameAndValue('non-quoted string-token on single line, followed by arguments on same line',
                         (
                             [
                                 '{string_token} {following_argument}'.format(
                                     string_token=single_string_token_value,
                                     following_argument=following_arg_token,
                                 )
                             ],
                             ExpectedString(single_string_token_value,
                                            CommonExpectation(
                                                symbol_references=[],
                                                source=asrt_source.assert_source(
                                                    current_line_number=asrt.equals(1),
                                                    remaining_part_of_current_line=asrt.equals(
                                                        following_arg_token))))
                         )
                         ),
            NameAndValue('quoted string-token on single line',
                         (
                             [
                                 surrounded_by_soft_quotes_str(multiple_tokens_string_value),
                             ],
                             ExpectedString(multiple_tokens_string_value,
                                            CommonExpectation(
                                                symbol_references=[],
                                                source=asrt_source.is_at_end_of_line(1)))
                         )
                         ),
        ]
        for case in cases:
            source_lines, expected_string = case.value
            source = remaining_source_lines(source_lines)
            with self.subTest(case_name=case.name):
                _expect_string(self, source, expected_string)

    def test_valid_syntax_with_symbol_references(self):
        symbol = NameAndValue('symbol_name', 'symbol value')
        before_symbol = 'text before symbol'
        after_symbol = 'text after symbol'
        following_arg_token = 'singleToken'
        cases = [
            NameAndValue('single unquoted symbol reference',
                         (
                             [
                                 symbol_reference_syntax_for_name(symbol.name),
                             ],
                             ExpectedString(symbol.value,
                                            CommonExpectation(
                                                symbol_references=[
                                                    references.reference_to_any_data_type_value(symbol.name),
                                                ],
                                                source=asrt_source.is_at_end_of_line(1),
                                                symbol_table=singleton_symbol_table_2(symbol.name,
                                                                                      string_constant_container(
                                                                                          symbol.value)),
                                            )
                                            )
                         )
                         ),
            NameAndValue('single unquoted symbol reference followed by args on same line',
                         (
                             [
                                 '{sym_ref} {following_argument}'.format(
                                     sym_ref=symbol_reference_syntax_for_name(symbol.name),
                                     following_argument=following_arg_token,
                                 ),
                             ],
                             ExpectedString(symbol.value,
                                            CommonExpectation(
                                                symbol_references=[
                                                    references.reference_to_any_data_type_value(symbol.name),
                                                ],
                                                source=asrt_source.assert_source(
                                                    current_line_number=asrt.equals(1),
                                                    remaining_part_of_current_line=asrt.equals(
                                                        following_arg_token)),
                                                symbol_table=singleton_symbol_table_2(symbol.name,
                                                                                      string_constant_container(
                                                                                          symbol.value)),
                                            ),
                                            )
                         )
                         ),
            NameAndValue('reference embedded in quoted string',
                         (
                             [
                                 '{soft_quote}{before_sym_ref}{sym_ref}{after_sym_ref}{soft_quote}'.format(
                                     soft_quote=SOFT_QUOTE_CHAR,
                                     sym_ref=symbol_reference_syntax_for_name(symbol.name),
                                     before_sym_ref=before_symbol,
                                     after_sym_ref=after_symbol,
                                 )
                             ],
                             ExpectedString(before_symbol + symbol.value + after_symbol,
                                            CommonExpectation(
                                                symbol_references=[
                                                    references.reference_to_any_data_type_value(symbol.name),
                                                ],
                                                source=asrt_source.is_at_end_of_line(1),
                                                symbol_table=singleton_symbol_table_2(symbol.name,
                                                                                      string_constant_container(
                                                                                          symbol.value)),
                                            )
                                            )
                         )
                         ),
        ]
        for case in cases:
            source_lines, expected_string = case.value
            source = remaining_source_lines(source_lines)
            with self.subTest(case_name=case.name):
                _expect_string(self, source, expected_string)


class TestHereDoc(unittest.TestCase):
    def test_invalid_syntax(self):
        source = remaining_source_lines(['<<marker',
                                         'contents',
                                         'nonMarker',
                                         ])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_from_parse_source(source)

    def test_without_symbol_references(self):
        expected_contents_line = 'contents'
        source = remaining_source_lines(['<<MARKER',
                                         expected_contents_line,
                                         'MARKER',
                                         'Line 4',
                                         ])
        expectation = ExpectedHereDoc(
            resolved_here_doc_lines=[expected_contents_line],
            common=CommonExpectation(
                symbol_references=[],
                source=asrt_source.is_at_beginning_of_line(4))

        )
        _expect_here_doc(self, source, expectation)

    def test_without_symbol_references__without_following_line(self):
        expected_contents_line = 'contents'
        source = remaining_source_lines(['<<MARKER',
                                         expected_contents_line,
                                         'MARKER',
                                         ])
        expectation = ExpectedHereDoc(
            resolved_here_doc_lines=[expected_contents_line],
            common=CommonExpectation(
                symbol_references=[],
                source=asrt_source.source_is_at_end)

        )
        _expect_here_doc(self, source, expectation)

    def test_with_symbol_references(self):
        symbol1 = NameAndValue('symbol_1_name', 'symbol 1 value')
        line_with_sym_ref_template = 'before symbol {symbol} after symbol'
        source = remaining_source_lines(['<<MARKER',
                                         line_with_sym_ref_template.format(
                                             symbol=symbol_reference_syntax_for_name(symbol1.name)),
                                         'MARKER',
                                         'Line 4',
                                         ]
                                        )
        expectation = ExpectedHereDoc(
            resolved_here_doc_lines=[
                line_with_sym_ref_template.format(
                    symbol=symbol1.value)
            ],
            common=CommonExpectation(
                symbol_references=[
                    references.reference_to_any_data_type_value(symbol1.name),
                ],
                symbol_table=symbol_table_with_string_values_from_name_and_value([
                    symbol1,
                ]),
                source=asrt_source.is_at_beginning_of_line(4),
            )

        )
        _expect_here_doc(self, source, expectation)


class TestFileRef(unittest.TestCase):
    def test_without_symbol_references(self):
        file_name = 'file'
        source = remaining_source_lines(
            ['{file_option} {file_name} following args'.format(
                file_option=option_syntax(sut.FILE_ARGUMENT_OPTION),
                file_name=file_name,
            ),
                'following line',
            ])
        expectation = ExpectedFileRef(
            file_ref_value=file_refs.of_rel_option(sut.CONFIGURATION.options.default_option,
                                                   concrete_path_parts.fixed_path_parts(file_name)),
            common=CommonExpectation(
                symbol_references=[],

                source=asrt_source.assert_source(current_line_number=asrt.equals(1),
                                                 remaining_part_of_current_line=asrt.equals(
                                                     'following args')))
        )

        _expect_file_ref(self, source, expectation)

    def test_parse_SHOULD_fail_WHEN_relativity_is_not_accepted(self):
        accepted_option_type = RelOptionType.REL_TMP
        unaccepted_option_type_string_conf = OptionStringConfigurationForRelativityOption(RelOptionType.REL_RESULT)
        accepted_path_relativity_variants = PathRelativityVariants({accepted_option_type},
                                                                   absolute=False)
        rel_opt_arg_conf = RelOptionArgumentConfiguration(
            RelOptionsConfiguration(accepted_path_relativity_variants,
                                    accepted_option_type),
            'ARG_SYNTAX_NAME',
            False
        )
        file_name = 'file'
        source = remaining_source_lines(
            ['{file_option} {unaccepted_rel_option} {file_name}'.format(
                file_option=option_syntax(sut.FILE_ARGUMENT_OPTION),
                unaccepted_rel_option=unaccepted_option_type_string_conf.option_string,
                file_name=file_name,
            ),
                'following line',
            ])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_from_parse_source(source, rel_opt_arg_conf)

    def test_with_symbol_references(self):
        # ARRANGE #
        symbol_relativity = RelOptionType.REL_TMP
        default_relativity = RelOptionType.REL_RESULT
        accepted_path_relativity_variants = PathRelativityVariants({default_relativity,
                                                                    symbol_relativity},
                                                                   absolute=False)
        rel_opt_arg_conf = RelOptionArgumentConfiguration(
            RelOptionsConfiguration(accepted_path_relativity_variants,
                                    default_relativity),
            'ARG_SYNTAX_NAME',
            False
        )
        symbol_path_suffix = 'symbol-path-suffix'
        symbol = NameAndValue('path_symbol',
                              file_refs.of_rel_option(
                                  symbol_relativity,
                                  concrete_path_parts.fixed_path_parts(symbol_path_suffix)))
        file_name = 'file'
        source = remaining_source_lines(
            ['{file_option} {rel_symbol_option} {file_name} following args'.format(
                rel_symbol_option=relativity_arguments.rel_symbol_arg_str(symbol.name),
                file_option=option_syntax(sut.FILE_ARGUMENT_OPTION),
                file_name=file_name,
            ),
                'following line',
            ])
        # EXPECTATION #
        expectation = ExpectedFileRef(
            file_ref_value=file_refs.of_rel_option(symbol_relativity,
                                                   concrete_path_parts.fixed_path_parts([symbol_path_suffix,
                                                                                         file_name])),
            common=CommonExpectation(
                symbol_references=[SymbolReference(symbol.name,
                                                   file_ref_reference_restrictions(
                                                             accepted_path_relativity_variants))],

                source=asrt_source.assert_source(current_line_number=asrt.equals(1),
                                                 remaining_part_of_current_line=asrt.equals(
                                                     'following args')),
                symbol_table=singleton_symbol_table_2(symbol.name,
                                                      file_ref_constant_container(symbol.value)))
        )
        # ACT & ASSERT #
        _expect_file_ref(self, source, expectation,
                         rel_opt_arg_conf)


class CommonExpectation:
    def __init__(self,
                 symbol_references: list,
                 source: asrt.ValueAssertion,
                 symbol_table: SymbolTable = None):
        self.symbol_references = symbol_references
        self.source = source
        self.symbol_table = empty_symbol_table() if symbol_table is None else symbol_table


class ExpectedString:
    def __init__(self,
                 resolved_str: str,
                 common: CommonExpectation):
        self.resolved_str = resolved_str
        self.common = common


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
                     expectation: ExpectedFileRef,
                     rel_opt_arg_conf: RelOptionArgumentConfiguration = sut.CONFIGURATION,
                     ):
    # ACT #
    actual = sut.parse_from_parse_source(source, rel_opt_arg_conf)
    # ASSERT #
    put.assertIs(sut.SourceType.PATH,
                 actual.source_type,
                 'source type')
    put.assertTrue(actual.is_file_ref,
                   'is_file_ref')
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
    put.assertIs(sut.SourceType.HERE_DOC,
                 actual.source_type,
                 'source type')
    put.assertFalse(actual.is_file_ref,
                    'is_file_ref')
    assertion_on_here_doc = asrt_hd.matches_resolved_value(expectation.resolved_here_doc_lines,
                                                           expectation.common.symbol_references,
                                                           expectation.common.symbol_table)
    assertion_on_here_doc.apply_with_message(put, actual.string_resolver,
                                             'here_document')
    _expect_common(put, source, actual,
                   expectation.common)


def _expect_string(put: unittest.TestCase,
                   source: ParseSource,
                   expectation: ExpectedString):
    # ACT #
    actual = sut.parse_from_parse_source(source)
    # ASSERT #
    put.assertIs(sut.SourceType.STRING,
                 actual.source_type,
                 'source type')
    put.assertFalse(actual.is_file_ref,
                    'is_file_ref')
    assertion_on_here_doc = asrt_string.matches_primitive_string(asrt.equals(expectation.resolved_str),
                                                                 expectation.common.symbol_references,
                                                                 expectation.common.symbol_table)
    assertion_on_here_doc.apply_with_message(put, actual.string_resolver,
                                             'string_resolver')
    _expect_common(put, source, actual,
                   expectation.common)


def _expect_common(put: unittest.TestCase,
                   actual_source: ParseSource,
                   actual_result: sut.StringResolverOrFileRef,
                   expectation: CommonExpectation):
    symbol_references_assertion = equals_symbol_references(expectation.symbol_references)
    symbol_references_assertion.apply_with_message(put, actual_result.symbol_usages,
                                                   'symbol_usages of FileRefOrHereDoc')

    expectation.source.apply_with_message(put, actual_source,
                                          'source_after_parse')
