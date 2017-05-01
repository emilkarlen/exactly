from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.test_case_file_structure.relativity_root import RelOptionType, RelRootResolver, \
    resolver_for_tmp_user, resolver_for_cwd, resolver_for_home, resolver_for_act, resolver_for_result
from exactly_lib.util.cli_syntax.elements import argument


class RelOptionInfo(tuple):
    def __new__(cls,
                option_name: argument.OptionName,
                root_resolver: RelRootResolver,
                description: str):
        return tuple.__new__(cls, (option_name, root_resolver, description))

    @property
    def option_name(self) -> argument.OptionName:
        return self[0]

    @property
    def root_resolver(self) -> RelRootResolver:
        return self[1]

    @property
    def description(self) -> str:
        return self[2]


REL_OPTIONS_MAP = {
    RelOptionType.REL_HOME: RelOptionInfo(file_ref_texts.REL_HOME_OPTION_NAME,
                                          resolver_for_home,
                                          file_ref_texts.RELATIVITY_DESCRIPTION_HOME),
    RelOptionType.REL_CWD: RelOptionInfo(file_ref_texts.REL_CWD_OPTION_NAME,
                                         resolver_for_cwd,
                                         file_ref_texts.RELATIVITY_DESCRIPTION_CWD),
    RelOptionType.REL_ACT: RelOptionInfo(file_ref_texts.REL_ACT_OPTION_NAME,
                                         resolver_for_act,
                                         file_ref_texts.RELATIVITY_DESCRIPTION_ACT),
    RelOptionType.REL_TMP: RelOptionInfo(file_ref_texts.REL_TMP_OPTION_NAME,
                                         resolver_for_tmp_user,
                                         file_ref_texts.RELATIVITY_DESCRIPTION_TMP),
    RelOptionType.REL_RESULT: RelOptionInfo(file_ref_texts.REL_RESULT_OPTION_NAME,
                                            resolver_for_result,
                                            file_ref_texts.RELATIVITY_DESCRIPTION_RESULT),
}


def option_for(option_name: argument.OptionName, argument_name: str = None) -> argument.Option:
    return argument.Option(option_name, argument_name)
