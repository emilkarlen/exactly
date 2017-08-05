from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.test_case_file_structure import relativity_root
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType, RelNonHomeOptionType, \
    RelHomeOptionType
from exactly_lib.test_case_file_structure.relativity_root import RelOptionType, RelRootResolver, \
    RelSdsRootResolver, RelNonHomeRootResolver, RelHomeRootResolver
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


class RelHomeOptionInfo(tuple):
    def __new__(cls,
                option_name: argument.OptionName,
                root_resolver: RelHomeRootResolver,
                description: str):
        return tuple.__new__(cls, (option_name, root_resolver, description))

    @property
    def option_name(self) -> argument.OptionName:
        return self[0]

    @property
    def root_resolver(self) -> RelHomeRootResolver:
        return self[1]

    @property
    def description(self) -> str:
        return self[2]


class RelSdsOptionInfo(tuple):
    def __new__(cls,
                option_name: argument.OptionName,
                root_resolver: RelSdsRootResolver,
                description: str):
        return tuple.__new__(cls, (option_name, root_resolver, description))

    @property
    def option_name(self) -> argument.OptionName:
        return self[0]

    @property
    def root_resolver(self) -> RelSdsRootResolver:
        return self[1]

    @property
    def description(self) -> str:
        return self[2]


class RelNonHomeOptionInfo(tuple):
    def __new__(cls,
                option_name: argument.OptionName,
                root_resolver: RelNonHomeRootResolver,
                description: str):
        return tuple.__new__(cls, (option_name, root_resolver, description))

    @property
    def option_name(self) -> argument.OptionName:
        return self[0]

    @property
    def root_resolver(self) -> RelNonHomeRootResolver:
        return self[1]

    @property
    def description(self) -> str:
        return self[2]


REL_HOME_OPTIONS_MAP = {
    RelHomeOptionType.REL_HOME: RelHomeOptionInfo(file_ref_texts.REL_HOME_OPTION_NAME,
                                                  relativity_root.resolver_for_home_case,
                                                  file_ref_texts.RELATIVITY_DESCRIPTION_HOME),
}

REL_SDS_OPTIONS_MAP = {
    RelSdsOptionType.REL_ACT: RelSdsOptionInfo(file_ref_texts.REL_ACT_OPTION_NAME,
                                               relativity_root.resolver_for_act,
                                               file_ref_texts.RELATIVITY_DESCRIPTION_ACT),

    RelSdsOptionType.REL_TMP: RelSdsOptionInfo(file_ref_texts.REL_TMP_OPTION_NAME,
                                               relativity_root.resolver_for_tmp_user,
                                               file_ref_texts.RELATIVITY_DESCRIPTION_TMP),

    RelSdsOptionType.REL_RESULT: RelSdsOptionInfo(file_ref_texts.REL_RESULT_OPTION_NAME,
                                                  relativity_root.resolver_for_result,
                                                  file_ref_texts.RELATIVITY_DESCRIPTION_RESULT),
}

REL_NON_HOME_OPTIONS_MAP = {
    RelNonHomeOptionType.REL_CWD: RelNonHomeOptionInfo(file_ref_texts.REL_CWD_OPTION_NAME,
                                                       relativity_root.resolver_for_cwd,
                                                       file_ref_texts.RELATIVITY_DESCRIPTION_CWD),

    RelNonHomeOptionType.REL_ACT: RelNonHomeOptionInfo(file_ref_texts.REL_ACT_OPTION_NAME,
                                                       relativity_root.resolver_for_act,
                                                       file_ref_texts.RELATIVITY_DESCRIPTION_ACT),

    RelNonHomeOptionType.REL_TMP: RelNonHomeOptionInfo(file_ref_texts.REL_TMP_OPTION_NAME,
                                                       relativity_root.resolver_for_tmp_user,
                                                       file_ref_texts.RELATIVITY_DESCRIPTION_TMP),

    RelNonHomeOptionType.REL_RESULT: RelNonHomeOptionInfo(file_ref_texts.REL_RESULT_OPTION_NAME,
                                                          relativity_root.resolver_for_result,
                                                          file_ref_texts.RELATIVITY_DESCRIPTION_RESULT),
}

REL_OPTIONS_MAP = {
    RelOptionType.REL_HOME: RelOptionInfo(file_ref_texts.REL_HOME_OPTION_NAME,
                                          relativity_root.resolver_for_home_case,
                                          file_ref_texts.RELATIVITY_DESCRIPTION_HOME),

    RelOptionType.REL_CWD: RelOptionInfo(file_ref_texts.REL_CWD_OPTION_NAME,
                                         relativity_root.resolver_for_cwd,
                                         file_ref_texts.RELATIVITY_DESCRIPTION_CWD),

    RelOptionType.REL_ACT: RelOptionInfo(file_ref_texts.REL_ACT_OPTION_NAME,
                                         relativity_root.resolver_for_act,
                                         file_ref_texts.RELATIVITY_DESCRIPTION_ACT),

    RelOptionType.REL_TMP: RelOptionInfo(file_ref_texts.REL_TMP_OPTION_NAME,
                                         relativity_root.resolver_for_tmp_user,
                                         file_ref_texts.RELATIVITY_DESCRIPTION_TMP),

    RelOptionType.REL_RESULT: RelOptionInfo(file_ref_texts.REL_RESULT_OPTION_NAME,
                                            relativity_root.resolver_for_result,
                                            file_ref_texts.RELATIVITY_DESCRIPTION_RESULT),
}


def option_for(option_name: argument.OptionName, argument_name: str = None) -> argument.Option:
    return argument.Option(option_name, argument_name)
