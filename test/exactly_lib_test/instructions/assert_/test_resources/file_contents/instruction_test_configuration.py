from exactly_lib.instructions.assert_.utils.file_contents import parsing
from exactly_lib.instructions.utils.arg_parse import relative_path_options
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_resources.home_and_sds_test import Action
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType


class InstructionTestConfiguration:
    def new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()


class InstructionTestConfigurationForContentsOrEquals(InstructionTestConfiguration):
    def source_for(self, argument_tail: str) -> SingleInstructionParserSource:
        raise NotImplementedError()

    def arrangement_for_contents(self,
                                 actual_contents: str,
                                 post_sds_population_action: Action = Action(),
                                 ) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str,
                                          post_sds_population_action: Action = Action(),
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


def args(arg_str: str, **kwargs) -> str:
    if kwargs:
        format_map = dict(list(_FORMAT_MAP.items()) + list(kwargs.items()))
        return arg_str.format_map(format_map)
    return arg_str.format_map(_FORMAT_MAP)


_FORMAT_MAP = {
    'contains': parsing.CONTAINS_ARGUMENT,
    'equals': parsing.EQUALS_ARGUMENT,
    'replace_env_vars_option': long_option_syntax(parsing.WITH_REPLACED_ENV_VARS_OPTION_NAME.long),
    'rel_home_option': relative_path_options.REL_HOME_OPTION,
    'rel_cwd_option': relative_path_options.REL_CWD_OPTION,
    'rel_tmp_option': relative_path_options.REL_TMP_OPTION,
}
