from exactly_lib.instructions.assert_.utils.file_contents import parsing
from exactly_lib.instructions.utils.arg_parse import relative_path_options
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.test_resources.execution.home_or_sds_populator import HomeOrSdsPopulator


class TestConfiguration:
    def new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()

    def source_for(self, argument_tail: str) -> SingleInstructionParserSource:
        raise NotImplementedError()

    def empty_arrangement(self) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct()

    def arrangement_for_contents(self, actual_contents: str) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()

    def arrangement_for_actual_and_expected(self,
                                            actual_contents: str,
                                            expected: HomeOrSdsPopulator) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()


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
