import re
import unittest

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_matcher import file_matchers
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher as sut
from exactly_lib.test_case_utils.file_matcher.impl.file_type import FileMatcherType
from exactly_lib.test_case_utils.file_matcher.impl.name_glob_pattern import FileMatcherNameGlobPattern
from exactly_lib.test_case_utils.file_matcher.impl.name_regex import FileMatcherBaseNameRegExPattern
from exactly_lib.test_case_utils.file_matcher.resolvers import FileMatcherConstantResolver
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.util import symbol_table
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.test_resources.file_matcher import is_file_matcher_reference_to
from exactly_lib_test.test_case_utils.file_matcher.test_resources.argument_syntax import name_glob_pattern_matcher_of, \
    type_matcher_of, name_reg_ex_pattern_matcher_of
from exactly_lib_test.test_case_utils.file_matcher.test_resources.resolver_assertions import \
    resolved_value_equals_file_matcher
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__for_expression_parser
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_case_utils.test_resources import matcher_parse_check
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseFileMatcher),
        unittest.makeSuite(TestNameGlobPattern),
        unittest.makeSuite(TestBaseNameRegExPattern),
        unittest.makeSuite(TestFileType),
    ])


class Configuration(matcher_parse_check.Configuration):
    def parse(self, parser: TokenParser) -> SymbolValueResolver:
        return sut.parse_resolver(parser)

    def resolved_value_equals(self,
                              value: FileMatcher,
                              references: ValueAssertion = asrt.is_empty_sequence,
                              symbols: symbol_table.SymbolTable = None) -> ValueAssertion:
        return resolved_value_equals_file_matcher(
            value,
            references,
            symbols
        )

    def is_reference_to(self, symbol_name: str) -> ValueAssertion:
        return is_file_matcher_reference_to(symbol_name)

    def resolver_of_constant_matcher(self, matcher: FileMatcher) -> SymbolValueResolver:
        return FileMatcherConstantResolver(matcher)

    def constant_matcher(self, result: bool) -> FileMatcher:
        return file_matchers.FileMatcherConstant(result)

    def not_matcher(self, matcher: FileMatcher) -> FileMatcher:
        return file_matchers.FileMatcherNot(matcher)

    def and_matcher(self, matchers: list) -> FileMatcher:
        return file_matchers.FileMatcherAnd(matchers)

    def or_matcher(self, matchers: list) -> FileMatcher:
        return file_matchers.FileMatcherOr(matchers)


NON_MATCHER_ARGUMENTS = 'not_a_matcher argument'

SPACE = '   '

DESCRIPTION_IS_SINGLE_STR = asrt.matches_sequence([asrt.is_instance(str)])


class Expectation:
    def __init__(self,
                 resolver: ValueAssertion,
                 source: ValueAssertion,
                 ):
        self.selector = resolver
        self.source = source


class TestParseFileMatcher(matcher_parse_check.TestParseStandardExpressionsBase):
    _conf = Configuration()

    @property
    def conf(self) -> Configuration:
        return self._conf


class TestCaseBase(unittest.TestCase):
    def _check_parse(self,
                     source: ParseSource,
                     expectation: Expectation):
        parsed_selector_resolver = sut.parse_resolver_from_parse_source(source)

        expectation.selector.apply_with_message(self, parsed_selector_resolver,
                                                'parsed selector resolver')

        expectation.source.apply_with_message(self, source, 'source after parse')


class TestNameGlobPattern(TestCaseBase):
    def test_parse(self):
        pattern = 'include*'
        space = '   '
        cases = [
            SourceCase('single name argument',
                       remaining_source(name_glob_pattern_matcher_of(pattern)),
                       assert_source(is_at_eof=asrt.is_true),
                       ),
            SourceCase('single name argument followed by space, and following lines',
                       remaining_source(name_glob_pattern_matcher_of(pattern) + space,
                                        ['following line']),
                       assert_source(current_line_number=asrt.equals(1),
                                     remaining_part_of_current_line=asrt.equals(space[1:])),
                       ),
            SourceCase('single name argument followed by arguments',
                       remaining_source(name_glob_pattern_matcher_of(pattern) + space + 'following argument',
                                        ['following line']),
                       assert_source(current_line_number=asrt.equals(1),
                                     remaining_part_of_current_line=asrt.equals(space[1:] + 'following argument')),
                       ),
        ]
        for case in cases:
            with self.subTest(case=case.name):
                self._check_parse(
                    case.source,
                    Expectation(
                        resolved_value_equals_file_matcher(FileMatcherNameGlobPattern(pattern)),
                        source=case.source_assertion,
                    )
                )


class TestBaseNameRegExPattern(TestCaseBase):
    def test_parse(self):
        pattern = 'include.*'
        space = '   '
        cases = [
            SourceCase('single name reg-ex argument',
                       remaining_source(name_reg_ex_pattern_matcher_of(pattern)),
                       assert_source(is_at_eof=asrt.is_true),
                       ),
            SourceCase('single name reg-ex argument, including ignore-case option',
                       remaining_source(name_reg_ex_pattern_matcher_of(pattern,
                                                                       ignore_case=True)),
                       assert_source(is_at_eof=asrt.is_true),
                       ),
            SourceCase('single name reg-ex argument followed by space, and following lines',
                       remaining_source(name_reg_ex_pattern_matcher_of(pattern) + space,
                                        ['following line']),
                       assert_source(current_line_number=asrt.equals(1),
                                     remaining_part_of_current_line=asrt.equals(space[1:])),
                       ),
            SourceCase('single name reg-ex argument followed by arguments',
                       remaining_source(name_reg_ex_pattern_matcher_of(pattern) + space + 'following argument',
                                        ['following line']),
                       assert_source(current_line_number=asrt.equals(1),
                                     remaining_part_of_current_line=asrt.equals(space[1:] + 'following argument')),
                       ),
        ]
        expected = FileMatcherBaseNameRegExPattern(re.compile(pattern))
        for case in cases:
            with self.subTest(case=case.name):
                self._check_parse(
                    case.source,
                    Expectation(
                        resolved_value_equals_file_matcher(expected),
                        source=case.source_assertion,
                    )
                )


class TestFileType(TestCaseBase):
    def test_parse(self):
        space = '   '

        def source_cases(file_type: file_properties.FileType) -> list:

            return [
                SourceCase('single name argument',
                           remaining_source(type_matcher_of(file_type)),
                           assert_source(is_at_eof=asrt.is_true),
                           ),
                SourceCase('single name argument followed by space, and following lines',
                           remaining_source(type_matcher_of(file_type) + space,
                                            ['following line']),
                           assert_source(current_line_number=asrt.equals(1),
                                         remaining_part_of_current_line=asrt.equals(space[1:])),
                           ),
                SourceCase('single name argument followed by arguments, and following lines',
                           remaining_source(type_matcher_of(file_type) + space +
                                            name_glob_pattern_matcher_of('no-matching-file'),
                                            ['following line']),
                           assert_source(current_line_number=asrt.equals(1),
                                         remaining_part_of_current_line=asrt.equals(
                                             space[1:] + name_glob_pattern_matcher_of('no-matching-file'))),
                           ),
            ]

        for file_type in FileType:
            for source_case in source_cases(file_type):
                with self.subTest(case=source_case.name,
                                  file_type=str(file_type)):
                    self._check_parse(
                        source_case.source,
                        Expectation(
                            resolved_value_equals_file_matcher(FileMatcherType(file_type)),
                            source=source_case.source_assertion,
                        ),
                    )

    def test_parse_with_the_predefined_source_variants(self):
        file_type = FileType.REGULAR
        for source in equivalent_source_variants__with_source_check__for_expression_parser(
                self, Arguments(type_matcher_of(file_type))):
            with self.subTest(file_type=str(file_type)):
                self._check_parse(
                    source,
                    Expectation(
                        resolved_value_equals_file_matcher(FileMatcherType(file_type)),
                        source=asrt.anything_goes(),
                    ),
                )
