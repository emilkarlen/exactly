import unittest

from exactly_lib.instructions.assert_.utils.file_contents import parsing
from exactly_lib.instructions.utils.arg_parse import relative_path_options
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents.not_operator import NotOperatorInfo
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_resources.execution.home_and_sds_check import home_or_sds_populator as home_or_sds
from exactly_lib_test.test_resources.execution.home_and_sds_check.home_and_sds_utils import HomeAndSdsAction
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType


class InstructionTestConfiguration:
    def new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()

    def arrangement_for_contents(self,
                                 actual_contents: str,
                                 post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                 ) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()


class InstructionTestConfigurationForContentsOrEquals(InstructionTestConfiguration):
    def source_for(self, argument_tail: str, following_lines=()) -> SingleInstructionParserSource:
        raise NotImplementedError()

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str,
                                          home_or_sds_contents: home_or_sds.HomeOrSdsPopulator = home_or_sds.empty(),
                                          post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                          ) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()


class TestWithConfigurationBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, configuration: InstructionTestConfiguration):
        super().__init__(configuration)
        self.configuration = configuration

    def _check(self,
               source: SingleInstructionParserSource,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        instruction_check.check(self, self.configuration.new_parser(), source, arrangement, expectation)


class TestWithConfigurationAndNegationArgumentBase(TestWithConfigurationBase):
    def __init__(self,
                 configuration: InstructionTestConfiguration,
                 is_negated: bool):
        super().__init__(configuration)
        self.maybe_not = NotOperatorInfo(is_negated)

    def shortDescription(self):
        return (str(type(self)) + ' /\n' +
                str(type(self.configuration)) + ' /\n' +
                'is_negated=' + str(self.maybe_not.is_negated)
                )


def suite_for__conf__not_argument(configuration: InstructionTestConfiguration,
                                  test_cases: list) -> unittest.TestSuite:
    return unittest.TestSuite([tc(configuration, False) for tc in test_cases] +
                              [tc(configuration, True) for tc in test_cases])


def args(arg_str: str, **kwargs) -> str:
    if kwargs:
        format_map = dict(list(_FORMAT_MAP.items()) + list(kwargs.items()))
        return arg_str.format_map(format_map)
    return arg_str.format_map(_FORMAT_MAP)


_FORMAT_MAP = {
    'contains': parsing.CONTAINS_ARGUMENT,
    'empty': parsing.EMPTY_ARGUMENT,
    'equals': parsing.EQUALS_ARGUMENT,
    'not': parsing.NOT_ARGUMENT,
    'replace_env_vars_option': long_option_syntax(parsing.WITH_REPLACED_ENV_VARS_OPTION_NAME.long),
    'rel_home_option': relative_path_options.REL_HOME_OPTION,
    'rel_cwd_option': relative_path_options.REL_CWD_OPTION,
    'rel_tmp_option': relative_path_options.REL_TMP_OPTION,
}
