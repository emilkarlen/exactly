from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.test_case_file_structure import relativity_root
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType, RelNonHomeOptionType, \
    RelHomeOptionType
from exactly_lib.test_case_file_structure.relativity_root import RelOptionType, RelRootResolver, \
    RelHomeRootResolver
from exactly_lib.util.cli_syntax.elements import argument


class RelOptionInfo:
    def __init__(self,
                 option_name: argument.OptionName,
                 root_resolver: RelRootResolver,
                 description: str):
        self._option_name = option_name
        self._root_resolver = root_resolver
        self._description = description

    @property
    def option_name(self) -> argument.OptionName:
        return self._option_name

    @property
    def root_resolver(self) -> RelRootResolver:
        return self._root_resolver

    @property
    def description(self) -> str:
        return self._description


class RelOptionInfoCorrespondingToTcDir(RelOptionInfo):
    def __init__(self,
                 directory_variable_name: str,
                 option_name: argument.OptionName,
                 root_resolver: RelHomeRootResolver,
                 description: str):
        super().__init__(option_name,
                         root_resolver,
                         description)
        self._directory_name = directory_variable_name

    @property
    def directory_variable_name(self) -> str:
        return self._directory_name


class RelHomeOptionInfo(RelOptionInfoCorrespondingToTcDir):
    pass


class RelNonHomeOptionInfo(RelOptionInfo):
    pass


class RelSdsOptionInfo(RelNonHomeOptionInfo, RelOptionInfoCorrespondingToTcDir):
    pass


REL_HOME_OPTIONS_MAP = {
    RelHomeOptionType.REL_HOME_CASE: RelHomeOptionInfo(file_ref_texts.EXACTLY_DIR__REL_HOME_CASE,
                                                       file_ref_texts.REL_HOME_CASE_OPTION_NAME,
                                                       relativity_root.resolver_for_home_case,
                                                       file_ref_texts.RELATIVITY_DESCRIPTION_HOME_CASE),
    RelHomeOptionType.REL_HOME_ACT: RelHomeOptionInfo(file_ref_texts.EXACTLY_DIR__REL_HOME_ACT,
                                                      file_ref_texts.REL_HOME_ACT_OPTION_NAME,
                                                      relativity_root.resolver_for_home_act,
                                                      file_ref_texts.RELATIVITY_DESCRIPTION_HOME_ACT),
}

REL_SDS_OPTIONS_MAP = {
    RelSdsOptionType.REL_ACT: RelSdsOptionInfo(file_ref_texts.EXACTLY_DIR__REL_ACT,
                                               file_ref_texts.REL_ACT_OPTION_NAME,
                                               relativity_root.resolver_for_act,
                                               file_ref_texts.RELATIVITY_DESCRIPTION_ACT),

    RelSdsOptionType.REL_TMP: RelSdsOptionInfo(file_ref_texts.EXACTLY_DIR__REL_TMP,
                                               file_ref_texts.REL_TMP_OPTION_NAME,
                                               relativity_root.resolver_for_tmp_user,
                                               file_ref_texts.RELATIVITY_DESCRIPTION_TMP),

    RelSdsOptionType.REL_RESULT: RelSdsOptionInfo(file_ref_texts.EXACTLY_DIR__REL_RESULT,
                                                  file_ref_texts.REL_RESULT_OPTION_NAME,
                                                  relativity_root.resolver_for_result,
                                                  file_ref_texts.RELATIVITY_DESCRIPTION_RESULT),
}

REL_NON_HOME_OPTIONS_MAP = {
    RelNonHomeOptionType.REL_CWD: RelNonHomeOptionInfo(file_ref_texts.REL_CWD_OPTION_NAME,
                                                       relativity_root.resolver_for_cwd,
                                                       file_ref_texts.RELATIVITY_DESCRIPTION_CWD),

    RelNonHomeOptionType.REL_ACT: REL_SDS_OPTIONS_MAP[RelSdsOptionType.REL_ACT],

    RelNonHomeOptionType.REL_TMP: REL_SDS_OPTIONS_MAP[RelSdsOptionType.REL_TMP],

    RelNonHomeOptionType.REL_RESULT: REL_SDS_OPTIONS_MAP[RelSdsOptionType.REL_RESULT],
}

REL_OPTIONS_MAP = {
    RelOptionType.REL_HOME_CASE: REL_HOME_OPTIONS_MAP[RelHomeOptionType.REL_HOME_CASE],

    RelOptionType.REL_HOME_ACT: REL_HOME_OPTIONS_MAP[RelHomeOptionType.REL_HOME_ACT],

    RelOptionType.REL_CWD: REL_NON_HOME_OPTIONS_MAP[RelNonHomeOptionType.REL_CWD],

    RelOptionType.REL_ACT: REL_NON_HOME_OPTIONS_MAP[RelNonHomeOptionType.REL_ACT],

    RelOptionType.REL_TMP: REL_NON_HOME_OPTIONS_MAP[RelNonHomeOptionType.REL_TMP],

    RelOptionType.REL_RESULT: REL_NON_HOME_OPTIONS_MAP[RelNonHomeOptionType.REL_RESULT],
}


def option_for(option_name: argument.OptionName, argument_name: str = None) -> argument.Option:
    return argument.Option(option_name, argument_name)
