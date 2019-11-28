import pathlib
import unittest
from typing import List

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_matcher import file_matcher_models
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher as sut
from exactly_lib.test_case_utils.file_matcher.sdvs import FileMatcherConstantSdv
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherModel
from exactly_lib.util.file_utils import TmpDirFileSpaceThatMustNoBeUsed
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.test_resources.file_matcher import is_file_matcher_reference_to
from exactly_lib_test.test_case_utils.file_matcher.test_resources import ddv_assertions as asrt_file_matcher
from exactly_lib_test.test_case_utils.file_matcher.test_resources.argument_syntax import name_glob_pattern_matcher_of, \
    type_matcher_of, name_reg_ex_pattern_matcher_of
from exactly_lib_test.test_case_utils.file_matcher.test_resources.sdv_assertions import \
    resolved_ddv_matches_file_matcher
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__for_expression_parser
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_case_utils.test_resources import matcher_parse_check
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.data.test_resources import described_path


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseFileMatcher),
        unittest.makeSuite(TestNameGlobPattern),
        unittest.makeSuite(TestBaseNameRegExPattern),
        unittest.makeSuite(TestFileType),
    ])


class Configuration(matcher_parse_check.Configuration[FileMatcherModel]):
    def parse(self, parser: TokenParser) -> SymbolDependentValue:
        return sut.parse_sdv(parser)

    def is_reference_to(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_file_matcher_reference_to(symbol_name)

    def sdv_of_constant_matcher(self, matcher: FileMatcher) -> SymbolDependentValue:
        return FileMatcherConstantSdv(matcher)

    def arbitrary_model_that_should_not_be_touched(self) -> FileMatcherModel:
        return file_matcher_models.FileMatcherModelForPrimitivePath(
            TmpDirFileSpaceThatMustNoBeUsed(),
            described_path.new_primitive(pathlib.Path()),
        )

    def constant_matcher(self, result: bool) -> FileMatcher:
        return constant.MatcherWithConstantResult(result)


NON_MATCHER_ARGUMENTS = 'not_a_matcher argument'

SPACE = '   '

DESCRIPTION_IS_SINGLE_STR = asrt.matches_sequence([asrt.is_instance(str)])


class Expectation:
    def __init__(self,
                 sdv: ValueAssertion[SymbolDependentValue],
                 source: ValueAssertion[ParseSource],
                 ):
        self.selector = sdv
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
        parsed_selector_sdv = sut.parse_sdv_from_parse_source(source)

        expectation.selector.apply_with_message(self, parsed_selector_sdv,
                                                'parsed selector sdv')

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
                        resolved_ddv_matches_file_matcher(
                            asrt_file_matcher.matches_file_matcher_ddv__deep(
                                asrt_file_matcher.is_name_glob_pattern(asrt.equals(pattern))
                            )
                        ),
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
        for case in cases:
            with self.subTest(case=case.name):
                self._check_parse(
                    case.source,
                    Expectation(
                        resolved_ddv_matches_file_matcher(
                            asrt_file_matcher.matches_file_matcher_ddv__deep(
                                asrt_file_matcher.is_name_regex(asrt.equals(pattern))
                            )
                        ),
                        source=case.source_assertion,
                    )
                )


class TestFileType(TestCaseBase):
    def test_parse(self):
        space = '   '

        def source_cases(file_type: file_properties.FileType) -> List[SourceCase]:

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
                            resolved_ddv_matches_file_matcher(
                                asrt_file_matcher.matches_file_matcher_ddv__deep(
                                    asrt_file_matcher.is_type_matcher(file_type)
                                )
                            ),
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
                        resolved_ddv_matches_file_matcher(
                            asrt_file_matcher.matches_file_matcher_ddv__deep(
                                asrt_file_matcher.is_type_matcher(file_type)
                            )
                        ),
                        source=asrt.anything_goes(),
                    ),
                )
