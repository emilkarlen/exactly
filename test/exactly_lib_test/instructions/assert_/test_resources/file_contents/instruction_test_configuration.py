import unittest

from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents.not_operator import NotOperatorInfo
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import \
    home_and_sds_populators as home_or_sds
from exactly_lib_test.test_resources.parse import remaining_source
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
                                 ) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()


class InstructionTestConfigurationForContentsOrEquals(InstructionTestConfiguration):
    def first_line_argument(self, argument_tail: str) -> str:
        raise NotImplementedError()

    def source_for(self, argument_tail: str, following_lines=()) -> ParseSource:
        return remaining_source(self.first_line_argument(argument_tail),
                                following_lines)

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str,
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

    def _check_single_instruction_line_with_source_variants(self,
                                                            instruction_argument: str,
                                                            arrangement: ArrangementPostAct,
                                                            expectation: Expectation):
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
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
    'contains': instruction_options.CONTAINS_ARGUMENT,
    'empty': instruction_options.EMPTY_ARGUMENT,
    'equals': instruction_options.EQUALS_ARGUMENT,
    'not': instruction_options.NOT_ARGUMENT,
    'replace_env_vars_option': long_option_syntax(
        instruction_options.WITH_REPLACED_ENV_VARS_OPTION_NAME.long),
    'rel_home_option': file_ref_texts.REL_HOME_OPTION,
    'rel_cwd_option': file_ref_texts.REL_CWD_OPTION,
    'rel_tmp_option': file_ref_texts.REL_TMP_OPTION,
    'rel_symbol_option': file_ref_texts.REL_symbol_OPTION,
}
