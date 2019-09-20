import unittest
from typing import List

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.test_case_utils.string_matcher.parse import parse_string_matcher as sut
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_file_structure.test_resources import home_and_sds_populators as home_or_sds
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_populators import \
    HomeOrSdsPopulator
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__following_content_on_last_line_accepted
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_matcher.test_resources.model_construction import ModelBuilder
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    expectation_type_config__non_is_success, ExpectationTypeConfigForNoneIsSuccess
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction


class TestConfiguration:
    def new_parser(self) -> Parser[StringMatcherResolver]:
        return sut.string_matcher_parser()

    def arrangement_for_contents(self,
                                 home_or_sds_contents: home_or_sds.HomeOrSdsPopulator = home_or_sds.empty(),
                                 post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                 symbols: SymbolTable = None,
                                 ) -> integration_check.ArrangementPostAct:
        return integration_check.ArrangementPostAct(
            home_or_sds_contents=home_or_sds_contents,
            post_sds_population_action=post_sds_population_action,
            symbols=symbols,
        )

    def arguments_for(self, additional_arguments: str, following_lines=()) -> Arguments:
        return Arguments(additional_arguments, following_lines)

    def source_for_lines(self, argument_lines: List[str]) -> ParseSource:
        return self.source_for(argument_lines[0], argument_lines[1:])

    def source_for(self, argument_tail: str, following_lines=()) -> ParseSource:
        return self.arguments_for(argument_tail).followed_by_lines(following_lines).as_remaining_source


class TestConfigurationForEquals(TestConfiguration):
    def arrangement_for_expected(self,
                                 expected: HomeOrSdsPopulator,
                                 post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                 symbols: SymbolTable = None,
                                 ) -> integration_check.ArrangementPostAct:
        return integration_check.ArrangementPostAct(
            home_or_sds_contents=expected,
            post_sds_population_action=post_sds_population_action,
            symbols=symbols,
        )


class TestConfigurationForMatcher(TestConfigurationForEquals):
    pass


class TestCaseBase(unittest.TestCase):
    _CONF = TestConfigurationForMatcher()

    @property
    def configuration(self) -> TestConfigurationForMatcher:
        return self._CONF

    def _check(self,
               source: ParseSource,
               model: ModelBuilder,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        integration_check.check(self, self.configuration.new_parser(), source, model, arrangement, expectation)

    def _check_with_source_variants(self,
                                    instruction_argument: Arguments,
                                    model: ModelBuilder,
                                    arrangement: ArrangementPostAct,
                                    expectation: Expectation):
        for source in equivalent_source_variants__with_source_check__following_content_on_last_line_accepted(
                self, instruction_argument):
            integration_check.check(self, self.configuration.new_parser(), source, model, arrangement, expectation)


class TestWithNegationArgumentBase(TestCaseBase):
    def runTest(self):
        for expectation_type in ExpectationType:
            with self.subTest(expectation_type=expectation_type):
                self._doTest(expectation_type_config__non_is_success(expectation_type))

    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        raise NotImplementedError('abstract method')
