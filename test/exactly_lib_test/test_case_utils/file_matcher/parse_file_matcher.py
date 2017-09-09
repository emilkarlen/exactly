import unittest

from exactly_lib.named_element.resolver_structure import NamedElementResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher as sut
from exactly_lib.test_case_utils.file_matcher.file_matchers import FileMatcherFromSelectors, FileMatcherConstant, \
    FileMatcherNot, FileMatcherAnd, FileMatcherOr
from exactly_lib.test_case_utils.file_matcher.resolvers import FileMatcherConstantResolver
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.util import symbol_table
from exactly_lib.util.dir_contents_selection import Selectors
from exactly_lib_test.named_element.test_resources.file_matcher import is_file_matcher_reference_to
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.test_case_utils.file_matcher.test_resources.resolver_assertions import \
    resolved_value_equals_file_matcher
from exactly_lib_test.test_case_utils.parse.test_resources.selection_arguments import name_selector_of, type_selector_of
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_case_utils.test_resources import matcher_parse_check
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseFileMatcher),
        unittest.makeSuite(TestNamePattern),
        unittest.makeSuite(TestFileType),
    ])


class Configuration(matcher_parse_check.Configuration):
    def parse(self, parser: TokenParserPrime) -> NamedElementResolver:
        return sut.parse_resolver(parser)

    def resolved_value_equals(self,
                              value: FileMatcher,
                              references: asrt.ValueAssertion = asrt.is_empty_list,
                              symbols: symbol_table.SymbolTable = None) -> asrt.ValueAssertion:
        return resolved_value_equals_file_matcher(
            value,
            references,
            symbols
        )

    def is_reference_to(self, symbol_name: str) -> asrt.ValueAssertion:
        return is_file_matcher_reference_to(symbol_name)

    def resolver_of_constant_matcher(self, matcher: FileMatcher) -> NamedElementResolver:
        return FileMatcherConstantResolver(matcher)

    def constant_matcher(self, result: bool) -> FileMatcher:
        return FileMatcherConstant(result)

    def not_matcher(self, matcher: FileMatcher) -> FileMatcher:
        return FileMatcherNot(matcher)

    def and_matcher(self, matchers: list) -> FileMatcher:
        return FileMatcherAnd(matchers)

    def or_matcher(self, matchers: list) -> FileMatcher:
        return FileMatcherOr(matchers)


NON_MATCHER_ARGUMENTS = 'not_a_matcher argument'


def expected_matcher(name_patterns: list = (),
                     file_types: list = (),
                     references: asrt.ValueAssertion = asrt.is_empty_list) -> asrt.ValueAssertion:
    expected = file_matcher_of(name_patterns, file_types)
    return resolved_value_equals_file_matcher(expected,
                                              expected_references=references)


def file_matcher_of(name_patterns: list = (),
                    file_types: list = ()) -> sut.FileMatcherFromSelectors:
    return FileMatcherFromSelectors(Selectors(name_patterns=frozenset(name_patterns),
                                              file_types=frozenset(file_types)))


SPACE = '   '

DESCRIPTION_IS_SINGLE_STR = asrt.matches_sequence([asrt.is_instance(str)])


class Expectation:
    def __init__(self,
                 selector: asrt.ValueAssertion,
                 source: asrt.ValueAssertion,
                 ):
        self.selector = selector
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


class TestNamePattern(TestCaseBase):
    def test_parse(self):
        pattern = 'include*'
        space = '   '
        cases = [
            SourceCase('single name argument',
                       remaining_source(name_selector_of(pattern)),
                       assert_source(is_at_eof=asrt.is_true),
                       ),
            SourceCase('single name argument followed by space, and following lines',
                       remaining_source(name_selector_of(pattern) + space,
                                        ['following line']),
                       assert_source(current_line_number=asrt.equals(1),
                                     remaining_part_of_current_line=asrt.equals(space[1:])),
                       ),
            SourceCase('single name argument followed by arguments',
                       remaining_source(name_selector_of(pattern) + space + 'following argument',
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
                        expected_matcher(name_patterns=[pattern],
                                         file_types=[],
                                         ),
                        source=case.source_assertion,
                    )
                )


class TestFileType(TestCaseBase):
    def test_parse(self):
        space = '   '

        def source_cases(file_type: file_properties.FileType) -> list:

            return [
                SourceCase('single name argument',
                           remaining_source(type_selector_of(file_type)),
                           assert_source(is_at_eof=asrt.is_true),
                           ),
                SourceCase('single name argument followed by space, and following lines',
                           remaining_source(type_selector_of(file_type) + space,
                                            ['following line']),
                           assert_source(current_line_number=asrt.equals(1),
                                         remaining_part_of_current_line=asrt.equals(space[1:])),
                           ),
                SourceCase('single name argument followed by arguments',
                           remaining_source(type_selector_of(file_type) + space + name_selector_of('no-matching-file'),
                                            ['following line']),
                           assert_source(current_line_number=asrt.equals(1),
                                         remaining_part_of_current_line=asrt.equals(
                                             space[1:] + name_selector_of('no-matching-file'))),
                           ),
            ]

        for file_type in FileType:
            for source_case in source_cases(file_type):
                with self.subTest(case=source_case.name,
                                  file_type=str(file_type)):
                    self._check_parse(
                        source_case.source,
                        Expectation(
                            expected_matcher(name_patterns=[],
                                             file_types=[file_type])
                            ,
                            source=source_case.source_assertion,
                        ),
                    )
