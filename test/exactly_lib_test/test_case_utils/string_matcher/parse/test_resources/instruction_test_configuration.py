import unittest

from typing import Callable
from typing import List

from exactly_lib.instructions.assert_ import contents_of_file as sut
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.test_resources.arrangements import ActEnvironment, ActResultProducer
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_file_structure.test_resources import home_and_sds_populators as home_or_sds, \
    sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_populators import \
    HomeOrSdsPopulator
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__multi_line
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_matcher.test_resources.integration_check import Expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    pfh_expectation_type_config
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.process import SubProcessResult
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
                                 ) -> integration_check.ArrangementPostAct:
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
                                          ) -> integration_check.ArrangementPostAct:
        raise NotImplementedError()


class InstructionTestConfigurationForEquals(InstructionTestConfigurationForContentsOrEquals):
    def arrangement_for_actual_and_expected(self,
                                            actual_contents: str,
                                            expected: HomeOrSdsPopulator,
                                            post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                            symbols: SymbolTable = None,
                                            ) -> integration_check.ArrangementPostAct:
        raise NotImplementedError()


class TestConfigurationForMatcher(InstructionTestConfigurationForEquals):
    FILE_NAME_REL_ACT = 'actual.txt'
    FILE_NAME_REL_CWD = '../actual.txt'

    def new_parser(self) -> InstructionParser:
        return sut.parser('the-instruction-name')

    def arguments_for(self, additional_arguments: str) -> Arguments:
        return Arguments(self.FILE_NAME_REL_CWD + ' ' + additional_arguments)

    def arrangement_for_contents(self,
                                 actual_contents: str,
                                 post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                 symbols: SymbolTable = None,
                                 ) -> integration_check.ArrangementPostAct:
        return integration_check.ArrangementPostAct(
            sds_contents=self._populator_for_actual(actual_contents),
            post_sds_population_action=post_sds_population_action,
            symbols=symbols,
        )

    def arrangement_for_contents_from_fun(self,
                                          home_and_sds_2_str: Callable[[HomeAndSds], str],
                                          home_or_sds_contents: home_or_sds.HomeOrSdsPopulator = home_or_sds.empty(),
                                          post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                          symbols: SymbolTable = None,
                                          ) -> integration_check.ArrangementPostAct:
        act_result_producer = _ActResultProducer(home_and_sds_2_str, self.FILE_NAME_REL_ACT)
        return integration_check.ArrangementPostAct(
            act_result_producer=act_result_producer,
            home_or_sds_contents=home_or_sds_contents,
            post_sds_population_action=post_sds_population_action,
            symbols=symbols,
        )

    def arrangement_for_actual_and_expected(self,
                                            actual_contents: str,
                                            expected: HomeOrSdsPopulator,
                                            post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                            symbols: SymbolTable = None,
                                            ) -> integration_check.ArrangementPostAct:
        return integration_check.ArrangementPostAct(
            sds_contents=self._populator_for_actual(actual_contents),
            home_or_sds_contents=expected,
            post_sds_population_action=post_sds_population_action,
            symbols=symbols,
        )

    def _populator_for_actual(self, actual_contents) -> sds_populator.SdsPopulator:
        return sds_populator.contents_in(RelSdsOptionType.REL_ACT,
                                         DirContents([
                                             File(self.FILE_NAME_REL_ACT, actual_contents)
                                         ]))


class _ActResultProducer(ActResultProducer):
    def __init__(self,
                 home_and_sds_2_str: Callable[[HomeAndSds], str],
                 file_name: str):
        self.home_and_sds_2_str = home_and_sds_2_str
        self.file_name = file_name

    def apply(self, act_environment: ActEnvironment) -> SubProcessResult:
        self._populate_act_dir(act_environment)
        return SubProcessResult()

    def _populate_act_dir(self, act_environment: ActEnvironment):
        actual_contents = self.home_and_sds_2_str(act_environment.home_and_sds)
        sds_pop = sds_populator.contents_in(RelSdsOptionType.REL_ACT,
                                            DirContents([
                                                File(self.file_name, actual_contents)
                                            ]))
        sds_pop.populate_sds(act_environment.home_and_sds.sds)


class TestWithConfigurationBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, configuration: InstructionTestConfiguration):
        super().__init__(configuration)
        self.configuration = configuration

    def _check(self,
               source: ParseSource,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        integration_check.check(self, self.configuration.new_parser(), source, arrangement, expectation)

    def _check_with_source_variants(self,
                                    instruction_argument: Arguments,
                                    arrangement: ArrangementPostAct,
                                    expectation: Expectation):
        for source in equivalent_source_variants__with_source_check__multi_line(self, instruction_argument):
            integration_check.check(self, self.configuration.new_parser(), source, arrangement, expectation)


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
