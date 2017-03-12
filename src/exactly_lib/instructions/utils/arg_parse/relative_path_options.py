from exactly_lib.instructions.utils.relativity_root import RelOptionType, RelRootResolver, resolver_for_tmp_user, \
    resolver_for_cwd, resolver_for_home, \
    resolver_for_act, resolver_for_result
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax


class RelOptionInfo(tuple):
    def __new__(cls,
                option_name: argument.OptionName,
                root_resolver: RelRootResolver):
        return tuple.__new__(cls, (option_name, root_resolver))

    @property
    def option_name(self) -> argument.OptionName:
        return self[0]

    @property
    def root_resolver(self) -> RelRootResolver:
        return self[1]


REL_TMP_OPTION_NAME = argument.OptionName(long_name='rel-tmp')
REL_ACT_OPTION_NAME = argument.OptionName(long_name='rel-act')
REL_RESULT_OPTION_NAME = argument.OptionName(long_name='rel-result')
REL_CWD_OPTION_NAME = argument.OptionName(long_name='rel-cd')
REL_HOME_OPTION_NAME = argument.OptionName(long_name='rel-home')

REL_VARIABLE_DEFINITION_OPTION_NAME = argument.OptionName(long_name='rel')

REL_OPTIONS_MAP = {
    RelOptionType.REL_HOME: RelOptionInfo(REL_HOME_OPTION_NAME, resolver_for_home),
    RelOptionType.REL_CWD: RelOptionInfo(REL_CWD_OPTION_NAME, resolver_for_cwd),
    RelOptionType.REL_ACT: RelOptionInfo(REL_ACT_OPTION_NAME, resolver_for_act),
    RelOptionType.REL_TMP: RelOptionInfo(REL_TMP_OPTION_NAME, resolver_for_tmp_user),
    RelOptionType.REL_RESULT: RelOptionInfo(REL_RESULT_OPTION_NAME, resolver_for_result),
}

REL_TMP_OPTION = long_option_syntax(REL_TMP_OPTION_NAME.long)
REL_ACT_OPTION = long_option_syntax(REL_ACT_OPTION_NAME.long)
REL_RESULT_OPTION = long_option_syntax(REL_RESULT_OPTION_NAME.long)
REL_CWD_OPTION = long_option_syntax(REL_CWD_OPTION_NAME.long)
REL_HOME_OPTION = long_option_syntax(REL_HOME_OPTION_NAME.long)


def option_for(option_name: argument.OptionName, argument_name: str = None) -> argument.Option:
    return argument.Option(option_name, argument_name)
