import unittest
from typing import List, Sequence, Pattern

from exactly_lib.impls.types.regex import parse_regex
from exactly_lib.impls.types.regex import parse_regex as sut
from exactly_lib.impls.types.regex.regex_ddv import RegexSdv
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.parse.test_resources.source_case import SourceCase
from exactly_lib_test.impls.types.regex.test_resources.assertions import matches_regex_sdv
from exactly_lib_test.section_document.element_parsers.test_resources.parsing \
    import remaining_source, remaining_source_lines
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_assertions import \
    assert_token_stream
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds
from exactly_lib_test.test_resources.arguments.arguments_building import Arguments, here_document
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase, \
    MessageBuilder
from exactly_lib_test.type_val_deps.test_resources.validation import validation
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.type_val_deps.types.path.test_resources.symbol_context import PathDdvSymbolContext
from exactly_lib_test.type_val_deps.types.regex.test_resources.references import is_reference_to__regex_string_part
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringSymbolContext
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes, surrounded_by_hard_quotes


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParse),
        unittest.makeSuite(TestValidRegex),
        unittest.makeSuite(TestFailingValidationDueToInvalidRegexSyntax),

        unittest.makeSuite(TestResolvingOfSymbolReferences),
    ])


class Arrangement:
    def __init__(self, symbols: SymbolTable = None):
        self._symbols = SymbolTable() if symbols is None else symbols

    @property
    def symbols(self) -> SymbolTable:
        return self._symbols


class Expectation:
    def __init__(self,
                 pattern: Assertion[Pattern] = asrt.anything_goes(),
                 token_stream: Assertion[TokenStream] = asrt.anything_goes(),
                 validation: ValidationAssertions = ValidationAssertions.all_passes(),
                 references: Assertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                 ):
        self.pattern = pattern
        self.references = references
        self.validation = validation
        self.token_stream = token_stream

    def matches_regex_sdv(self,
                          symbols: SymbolTable,
                          tcds: TestCaseDs) -> Assertion[RegexSdv]:
        def on_primitive_value(tcds: TestCaseDs) -> Assertion[Pattern]:
            return self.pattern

        return matches_regex_sdv(primitive_value=on_primitive_value,
                                 references=self.references,
                                 validation=self.validation,
                                 tcds=tcds,
                                 symbols=symbols)


class OptionCase:
    def __init__(self,
                 source_prefix: str,
                 expectation: Assertion[Pattern]):
        self.source_prefix = source_prefix
        self.expectation = expectation


def option_case_for_no_option(expectation: Assertion[Pattern]) -> OptionCase:
    return OptionCase('', expectation)


def option_case_for_ignore_case(expectation: Assertion[Pattern]) -> OptionCase:
    return OptionCase(IGNORE_CASE_OPTION_FOLLOWED_BY_SPACE, expectation)


class ExpectationExceptPattern:
    def __init__(self,
                 references: Assertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                 validation: ValidationAssertions = ValidationAssertions.all_passes(),
                 ):
        self.references = references
        self.validation = validation


class TestFailingParse(unittest.TestCase):
    def test_failing_parse(self):
        cases = [
            NameAndValue(
                'no arguments',
                Arguments(''),
            ),
            NameAndValue(
                'invalid quoting of string',
                Arguments('"missing end quote'),
            ),
        ]
        parser = sut.ParserOfRegex()
        for source_case in cases:
            for option in OPTION_CASES:
                arguments = source_case.value.prepend_to_first_line(option)
                with self.subTest(case_name=source_case.name,
                                  option=option):
                    source = remaining_source_lines(arguments.lines)
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse_from_token_parser(source)


class TestValidRegex(unittest.TestCase):
    def test_unquoted_tokens(self):
        # ARRANGE #
        regex_str = 'a.*regex'

        matches_for_case_sensitive = ['aBCregex', 'aBCregex and more']

        option_cases = [
            option_case_for_no_option(
                _AssertPattern(regex_str,
                               matching_strings=matches_for_case_sensitive,
                               non_matching_string='AbcREGEX')
            ),

            option_case_for_ignore_case(
                _AssertPattern(regex_str,
                               matching_strings=matches_for_case_insensitive(matches_for_case_sensitive),
                               non_matching_string='Abc')
            ),
        ]

        text_on_following_line = 'text on following line'

        def _arg(format_string: str) -> str:
            return format_string.format(
                regex=regex_str)

        source_cases = [
            SourceCase(
                'REG-EX is only source',
                source=
                Arguments(_arg('{regex}')),
                source_assertion=
                assert_token_stream(is_null=asrt.is_true),
            ),
            SourceCase(
                'REG-EX is followed by a token',
                source=
                Arguments(_arg('{regex} following_token')),
                source_assertion=
                assert_token_stream(
                    is_null=asrt.is_false,
                    remaining_part_of_current_line=asrt.equals('following_token')),
            ),
            SourceCase(
                'REG-EX is only element on current line, but followed by more lines',
                source=
                Arguments(_arg('{regex}'),
                          following_lines=[text_on_following_line]),
                source_assertion=
                assert_token_stream(
                    is_null=asrt.is_false,
                    remaining_part_of_current_line=asrt.equals(''),
                    remaining_source=asrt.equals('\n' + text_on_following_line)),
            ),
        ]
        # ACT & ASSERT #
        check_many(self,
                   Arrangement(),
                   source_cases,
                   ExpectationExceptPattern(
                       validation=ValidationAssertions.all_passes()
                   ),
                   option_cases,
                   )

    def test_quoted_tokens(self):
        # ARRANGE #
        regex_str = '.* regex'

        matches_for_case_sensitive = [' regex', 'before regex after']

        option_cases = [
            option_case_for_no_option(
                _AssertPattern(regex_str,
                               matching_strings=matches_for_case_sensitive,
                               non_matching_string=' REGEX')
            ),

            option_case_for_ignore_case(
                _AssertPattern(regex_str,
                               matching_strings=matches_for_case_insensitive(matches_for_case_sensitive),
                               non_matching_string='regex')
            ),
        ]

        text_on_following_line = 'text on following line'

        source_cases = [
            SourceCase(
                'soft quotes',

                source=
                Arguments('{regex}'.format(
                    regex=surrounded_by_soft_quotes(regex_str),
                )),

                source_assertion=
                assert_token_stream(is_null=asrt.is_true),
            ),
            SourceCase(
                'hard quotes, and text on following line',

                source=
                Arguments('{regex}'.format(
                    regex=surrounded_by_hard_quotes(regex_str),
                ),
                    following_lines=[text_on_following_line]),

                source_assertion=
                assert_token_stream(
                    remaining_source=asrt.equals('\n' + text_on_following_line)),
            ),
        ]
        # ACT & ASSERT #
        check_many(self,
                   Arrangement(),
                   source_cases,
                   ExpectationExceptPattern(
                       validation=ValidationAssertions.all_passes()
                   ),
                   option_cases,
                   )

    def test_here_document(self):
        # ARRANGE #
        star_string_symbol = StringSymbolContext.of_constant('STAR_SYMBOL', '*')

        regex_str = '.*'

        regex_source_line = '.' + symbol_reference_syntax_for_name(star_string_symbol.name)

        arrangement = Arrangement(
            symbols=star_string_symbol.symbol_table
        )

        matches_for_case_sensitive = []

        option_cases = [
            option_case_for_no_option(
                _AssertPattern(regex_str + '\n',
                               matching_strings=matches_for_case_sensitive,
                               non_matching_string='missing new line')
            ),

            option_case_for_ignore_case(
                _AssertPattern(regex_str + '\n',
                               matching_strings=matches_for_case_insensitive(matches_for_case_sensitive),
                               non_matching_string='missing new line')
            ),
        ]

        text_on_following_line = 'text on following line'

        here_doc_argument = here_document([regex_source_line])
        source_cases = [
            SourceCase(
                'end of file after HD',
                source=
                here_doc_argument,

                source_assertion=
                assert_token_stream(remaining_part_of_current_line=asrt.equals(''),
                                    remaining_source=asrt.equals('')),
            ),
            SourceCase(
                'followed by more lines',
                source=
                here_doc_argument.followed_by_lines([text_on_following_line]),

                source_assertion=
                assert_token_stream(remaining_part_of_current_line=asrt.equals(''),
                                    remaining_source=asrt.equals('\n' + text_on_following_line)),
            ),
        ]

        expectation = ExpectationExceptPattern(
            references=asrt.matches_sequence([
                is_reference_to__regex_string_part(star_string_symbol.name),
            ]),
            validation=ValidationAssertions.all_passes(),
        )

        # ACT & ASSERT #

        check_many(self,
                   arrangement,
                   source_cases,
                   expectation,
                   option_cases,
                   )

    def test_symbol_references(self):
        # ARRANGE #
        star_string_symbol = StringSymbolContext.of_constant('STAR_SYMBOL', '* ')

        regex_str = '.* regex'

        regex_arg_str = '.{star}regex'.format(
            star=symbol_reference_syntax_for_name(star_string_symbol.name),
        )

        matches_for_case_sensitive = [' regex', 'before regex after']

        option_cases = [
            option_case_for_no_option(
                _AssertPattern(regex_str,
                               matching_strings=matches_for_case_sensitive,
                               non_matching_string=' REGEX')
            ),

            option_case_for_ignore_case(
                _AssertPattern(regex_str,
                               matching_strings=matches_for_case_insensitive(matches_for_case_sensitive),
                               non_matching_string='regex')
            ),
        ]

        source_cases = [
            SourceCase('single invalid star',
                       Arguments(regex_arg_str),
                       assert_token_stream(is_null=asrt.is_true)
                       ),
            SourceCase('invalid stars at start of regex',
                       Arguments(surrounded_by_soft_quotes(regex_arg_str)),
                       assert_token_stream(is_null=asrt.is_true)
                       ),
        ]

        arrangement = Arrangement(
            symbols=star_string_symbol.symbol_table
        )

        expectation = ExpectationExceptPattern(
            references=asrt.matches_sequence([
                is_reference_to__regex_string_part(star_string_symbol.name),
            ]),
            validation=ValidationAssertions.all_passes(),
        )

        # ACT & ASSERT #

        check_many(self,
                   arrangement,
                   source_cases,
                   expectation,
                   option_cases,
                   )


class TestFailingValidationDueToInvalidRegexSyntax(unittest.TestCase):
    STAR_STRING_SYMBOL = StringSymbolContext.of_constant('STAR_SYMBOL', '*')

    def test_no_symbol_references(self):
        # ARRANGE #
        option_cases = [
            option_case_for_no_option(asrt.anything_goes()),
            option_case_for_ignore_case(asrt.anything_goes()),
        ]

        source_cases = [
            SourceCase('single invalid star',
                       Arguments('*'),
                       assert_token_stream(is_null=asrt.is_true)
                       ),
            SourceCase('invalid stars inside valid regex',
                       Arguments('before**after'),
                       assert_token_stream(is_null=asrt.is_true)
                       ),
        ]
        # ACT & ASSERT #
        check_many(self,
                   Arrangement(),
                   source_cases,
                   ExpectationExceptPattern(
                       validation=validation.ValidationAssertions.pre_sds_fails__w_any_msg(),
                   ),
                   option_cases,
                   )

    def test_symbol_references_without_dir_dependencies(self):
        # ARRANGE #

        option_cases = [
            option_case_for_no_option(asrt.anything_goes()),
            option_case_for_ignore_case(asrt.anything_goes()),
        ]

        sym_ref_to_star = symbol_reference_syntax_for_name(self.STAR_STRING_SYMBOL.name)

        source_cases = [
            SourceCase('single invalid star',
                       Arguments(sym_ref_to_star),
                       assert_token_stream(is_null=asrt.is_true)
                       ),
            SourceCase('invalid stars at start of regex',
                       Arguments(sym_ref_to_star +
                                 'after'),
                       assert_token_stream(is_null=asrt.is_true)
                       ),
        ]

        arrangement = Arrangement(
            symbols=self.STAR_STRING_SYMBOL.symbol_table
        )

        expectation = ExpectationExceptPattern(
            references=asrt.matches_sequence([
                is_reference_to__regex_string_part(self.STAR_STRING_SYMBOL.name),
            ]),
            validation=validation.ValidationAssertions.pre_sds_fails__w_any_msg(),
        )

        # ACT & ASSERT #

        check_many(self,
                   arrangement,
                   source_cases,
                   expectation,
                   option_cases,
                   )

    def test_concatenation_of_symbol_references_makes_up_invalid_regex(self):
        # ARRANGE #

        option_cases = [
            option_case_for_no_option(asrt.anything_goes()),
            option_case_for_ignore_case(asrt.anything_goes()),
        ]

        sym_ref_to_star = symbol_reference_syntax_for_name(self.STAR_STRING_SYMBOL.name)

        source_cases = [
            SourceCase('invalid stars in middle of regex',
                       Arguments('before' +
                                 sym_ref_to_star +
                                 sym_ref_to_star +
                                 'after'),
                       assert_token_stream(is_null=asrt.is_true)
                       ),
        ]

        arrangement = Arrangement(
            symbols=self.STAR_STRING_SYMBOL.symbol_table
        )

        expectation = ExpectationExceptPattern(
            references=asrt.matches_sequence([
                is_reference_to__regex_string_part(self.STAR_STRING_SYMBOL.name),
                is_reference_to__regex_string_part(self.STAR_STRING_SYMBOL.name),
            ]),
            validation=validation.ValidationAssertions.pre_sds_fails__w_any_msg(),
        )

        # ACT & ASSERT #

        check_many(self,
                   arrangement,
                   source_cases,
                   expectation,
                   option_cases,
                   )

    def test_symbol_references_with_dir_dependencies(self):
        # ARRANGE #

        path_symbol_name = 'PATH_SYMBOL'

        regex_source_string = (symbol_reference_syntax_for_name(self.STAR_STRING_SYMBOL.name) +
                               symbol_reference_syntax_for_name(path_symbol_name))

        expectation = Expectation(
            references=asrt.matches_sequence([
                is_reference_to__regex_string_part(self.STAR_STRING_SYMBOL.name),
                is_reference_to__regex_string_part(path_symbol_name),
            ]),
            validation=ValidationAssertions.post_sds_fails__w_any_msg(),
            token_stream=assert_token_stream(is_null=asrt.is_true),
        )

        rel_opt_cases = [
            RelOptionType.REL_HDS_CASE,
            RelOptionType.REL_CWD,
            RelOptionType.REL_ACT,
        ]

        for rel_opt in rel_opt_cases:
            path_symbol = PathDdvSymbolContext.of_no_suffix(path_symbol_name, rel_opt)

            arrangement = Arrangement(
                symbols=SymbolContext.symbol_table_of_contexts([
                    self.STAR_STRING_SYMBOL,
                    path_symbol,
                ])
            )

            # ACT & ASSERT #

            self._check(regex_source_string,
                        arrangement,
                        expectation,
                        )

    def _check(self,
               regex_source_string: str,
               arrangement: Arrangement,
               expectation: Expectation):
        for option_str in OPTION_CASES:
            with self.subTest(option_str=option_str):
                source = remaining_source(option_str + regex_source_string)
                _check(self, source, arrangement, expectation)


class TestResolvingOfSymbolReferences(unittest.TestCase):
    def test_resolving_object_with_different_symbol_values_SHOULD_give_different_values(self):
        # ARRANGE #

        STRING_SYMBOL_NAME = 'STRING_SYMBOL'

        single_sym_ref_source = remaining_source(symbol_reference_syntax_for_name(STRING_SYMBOL_NAME))

        parser = sut.ParserOfRegex()
        # ACT #
        actual_sdv = parser.parse_from_token_parser(single_sym_ref_source)

        non_matching_string = '0'

        for symbol_value in ['A', 'B']:
            with self.subTest(symbol_value=symbol_value):
                string_symbol = StringSymbolContext.of_constant(STRING_SYMBOL_NAME, symbol_value)
                symbols = string_symbol.symbol_table

                # ASSERT #

                self._assert_resolved_pattern_has_pattern_string(
                    actual_sdv,
                    expected_pattern_string=symbol_value,
                    matching_string=symbol_value,
                    non_matching_string=non_matching_string,
                    symbols=symbols,
                )

    def _assert_resolved_pattern_has_pattern_string(self,
                                                    actual_sdv: RegexSdv,
                                                    expected_pattern_string: str,
                                                    matching_string: str,
                                                    non_matching_string: str,
                                                    symbols: SymbolTable):
        def equals_expected_pattern_string(tcds: TestCaseDs) -> Assertion[Pattern]:
            return _AssertPattern(
                pattern_string=expected_pattern_string,
                matching_strings=[matching_string],
                non_matching_string=non_matching_string,
            )

        resolved_value_has_expected_pattern_string = matches_regex_sdv(
            primitive_value=equals_expected_pattern_string,
            references=asrt.anything_goes(),
            symbols=symbols,
        )

        resolved_value_has_expected_pattern_string.apply_without_message(self, actual_sdv)


OPTION_CASES = [
    '',
    parse_regex.IGNORE_CASE_OPTION + ' ',
]

IGNORE_CASE_OPTION_FOLLOWED_BY_SPACE = parse_regex.IGNORE_CASE_OPTION + ' '


def check_many(put: unittest.TestCase,
               arrangement: Arrangement,
               source_cases: List[SourceCase],
               expectation: ExpectationExceptPattern,
               option_cases: List[OptionCase],
               ):
    for source_case in source_cases:
        source_without_options = source_case.source
        for option_case in option_cases:
            expectation = Expectation(
                references=expectation.references,
                validation=expectation.validation,
                pattern=option_case.expectation,
                token_stream=source_case.source_assertion,
            )
            with put.subTest(source_case=source_case.name,
                             options=option_case.source_prefix):
                arguments_with_option = source_without_options.prepend_to_first_line(option_case.source_prefix)
                source_with_options = remaining_source_lines(arguments_with_option.lines)
                _check(put,
                       source_with_options,
                       arrangement,
                       expectation)


def _check(put: unittest.TestCase,
           source: TokenParser,
           arrangement: Arrangement,
           expectation: Expectation):
    # ARRANGE #
    parser = sut.ParserOfRegex()
    tcds = fake_tcds()

    # ACT #
    actual_sdv = parser.parse_from_token_parser(source)
    # ASSERT #
    expectation.token_stream.apply_with_message(put,
                                                source.token_stream,
                                                'token stream')

    sdv_assertion = expectation.matches_regex_sdv(arrangement.symbols, tcds)

    sdv_assertion.apply_with_message(put,
                                     actual_sdv,
                                     'sdv')


def matches_for_case_insensitive(matches_for_case_sensitive: List[str]) -> List[str]:
    return matches_for_case_sensitive + [
        str.upper(s)
        for s in matches_for_case_sensitive
    ]


class _AssertPattern(AssertionBase[Pattern]):
    def __init__(self,
                 pattern_string: str,
                 matching_strings: List[str],
                 non_matching_string: str,
                 ):
        self.pattern_string = pattern_string
        self.non_matching_string = non_matching_string
        self.matching_string_list = matching_strings

    def _apply(self,
               put: unittest.TestCase,
               actual: Pattern,
               message_builder: MessageBuilder):
        put.assertEqual(self.pattern_string,
                        actual.pattern,
                        'regex pattern string')
        for matching_string in self.matching_string_list:
            put.assertTrue(bool(actual.search(matching_string)),
                           'reg-ex should match "{}"'.format(matching_string))

        put.assertFalse(bool(actual.search(self.non_matching_string)),
                        'reg-ex should not match "{}"'.format(self.non_matching_string))
