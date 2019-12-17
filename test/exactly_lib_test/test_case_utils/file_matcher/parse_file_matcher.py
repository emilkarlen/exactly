import unittest

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher as sut
from exactly_lib.test_case_utils.file_matcher.sdvs import file_matcher_constant_sdv
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherModel
from exactly_lib_test.symbol.test_resources.file_matcher import is_file_matcher_reference_to
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.test_resources import matcher_parse_check
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseFileMatcher),
    ])


class Configuration(matcher_parse_check.Configuration[FileMatcherModel]):
    def parse(self, parser: TokenParser) -> FileMatcherSdv:
        return sut.parse_sdv(parser)

    def is_reference_to(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_file_matcher_reference_to(symbol_name)

    def sdv_of_constant_matcher(self, matcher: FileMatcher) -> FileMatcherSdv:
        return file_matcher_constant_sdv(matcher)

    def arbitrary_model_that_should_not_be_touched(self) -> FileMatcherModel:
        return integration_check.ARBITRARY_MODEL

    def constant_matcher(self, result: bool) -> FileMatcher:
        return constant.MatcherWithConstantResult(result)


class TestParseFileMatcher(matcher_parse_check.TestParseStandardExpressionsBase):
    _conf = Configuration()

    @property
    def conf(self) -> Configuration:
        return self._conf
