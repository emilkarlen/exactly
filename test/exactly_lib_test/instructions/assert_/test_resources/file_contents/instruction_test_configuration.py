import unittest

from typing import List, Callable

from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_file_structure.test_resources import home_and_sds_populators as home_or_sds
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__multi_line
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    pfh_expectation_type_config
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction


class InstructionTestConfiguration:
    def new_parser(self) -> InstructionParser:
        raise NotImplementedError()

    def arrangement_for_contents(self,
                                 actual_contents: str,
                                 post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                 symbols: SymbolTable = None,
                                 ) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()


class InstructionTestConfigurationForContentsOrEquals(InstructionTestConfiguration):
    def arguments_for(self, additional_arguments: str) -> Arguments:
        raise NotImplementedError()

    def source_for_lines(self, argument_lines: List[str]) -> ParseSource:
        return self.source_for(argument_lines[0], argument_lines[1:])

    def source_for(self, argument_tail: str, following_lines=()) -> ParseSource:
        return self.arguments_for(argument_tail).followed_by_lines(following_lines).as_remaining_source

    def arrangement_for_contents_from_fun(self,
                                          home_and_sds_2_str: Callable[[HomeAndSds], str],
                                          home_or_sds_contents: home_or_sds.HomeOrSdsPopulator = home_or_sds.empty(),
                                          post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                          symbols: SymbolTable = None,
                                          ) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()


class TestWithConfigurationBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, configuration: InstructionTestConfiguration):
        super().__init__(configuration)
        self.configuration = configuration

    def _check(self,
               source: ParseSource,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        instruction_check.check(self, self.configuration.new_parser(), source, arrangement, expectation)

    def _check_with_source_variants(self,
                                    instruction_argument: Arguments,
                                    arrangement: ArrangementPostAct,
                                    expectation: Expectation):
        for source in equivalent_source_variants__with_source_check__multi_line(self, instruction_argument):
            instruction_check.check(self, self.configuration.new_parser(), source, arrangement, expectation)


class TestWithConfigurationAndNegationArgumentBase(TestWithConfigurationBase):
    def __init__(self,
                 configuration: InstructionTestConfiguration,
                 expectation_type: ExpectationType):
        super().__init__(configuration)
        self.maybe_not = pfh_expectation_type_config(expectation_type)

    def shortDescription(self):
        return (str(type(self)) + ' /\n' +
                str(type(self.configuration)) + ' /\n' +
                str(self.maybe_not)
                )


def suite_for__conf__not_argument(configuration: InstructionTestConfiguration,
                                  test_cases: List[TestWithConfigurationAndNegationArgumentBase]) -> unittest.TestSuite:
    return unittest.TestSuite(
        [tc(configuration, ExpectationType.POSITIVE) for tc in test_cases] +
        [tc(configuration, ExpectationType.NEGATIVE) for tc in test_cases])
