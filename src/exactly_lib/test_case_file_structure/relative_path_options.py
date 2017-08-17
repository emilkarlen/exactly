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
                directory_name: str,
                option_name: argument.OptionName,
                root_resolver: RelHomeRootResolver,
                description: str):
        return tuple.__new__(cls, (directory_name, option_name, root_resolver, description))

    @property
    def directory_name(self) -> str:
        return self[0]

    @property
    def option_name(self) -> argument.OptionName:
        return self[1]

    @property
    def root_resolver(self) -> RelHomeRootResolver:
        return self[2]

    @property
    def description(self) -> str:
        return self[3]

    @property
    def as_rel_any(self) -> RelOptionInfo:
        return RelOptionInfo(self.option_name,
                             self.root_resolver,
                             self.description)


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

    @property
    def as_rel_any(self) -> RelOptionInfo:
        return RelOptionInfo(self.option_name,
                             self.root_resolver,
                             self.description)


class RelSdsOptionInfo(tuple):
    def __new__(cls,
                directory_name: str,
                option_name: argument.OptionName,
                root_resolver: RelSdsRootResolver,
                description: str):
        return tuple.__new__(cls, (directory_name, option_name, root_resolver, description))

    @property
    def directory_name(self) -> str:
        return self[0]

    @property
    def option_name(self) -> argument.OptionName:
        return self[1]

    @property
    def root_resolver(self) -> RelSdsRootResolver:
        return self[2]

    @property
    def description(self) -> str:
        return self[3]

    @property
    def as_rel_non_home(self) -> RelNonHomeOptionInfo:
        return RelNonHomeOptionInfo(self.option_name,
                                    self.root_resolver,
                                    self.description)

    @property
    def as_rel_any(self) -> RelOptionInfo:
        return RelOptionInfo(self.option_name,
                             self.root_resolver,
                             self.description)


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

    RelNonHomeOptionType.REL_ACT: REL_SDS_OPTIONS_MAP[RelSdsOptionType.REL_ACT].as_rel_non_home,

    RelNonHomeOptionType.REL_TMP: REL_SDS_OPTIONS_MAP[RelSdsOptionType.REL_TMP].as_rel_non_home,

    RelNonHomeOptionType.REL_RESULT: REL_SDS_OPTIONS_MAP[RelSdsOptionType.REL_RESULT].as_rel_non_home,
}

REL_OPTIONS_MAP = {
    RelOptionType.REL_HOME_CASE: REL_HOME_OPTIONS_MAP[RelHomeOptionType.REL_HOME_CASE].as_rel_any,

    RelOptionType.REL_HOME_ACT: REL_HOME_OPTIONS_MAP[RelHomeOptionType.REL_HOME_ACT].as_rel_any,

    RelOptionType.REL_CWD: REL_NON_HOME_OPTIONS_MAP[RelNonHomeOptionType.REL_CWD].as_rel_any,

    RelOptionType.REL_ACT: REL_NON_HOME_OPTIONS_MAP[RelNonHomeOptionType.REL_ACT].as_rel_any,

    RelOptionType.REL_TMP: REL_NON_HOME_OPTIONS_MAP[RelNonHomeOptionType.REL_TMP].as_rel_any,

    RelOptionType.REL_RESULT: REL_NON_HOME_OPTIONS_MAP[RelNonHomeOptionType.REL_RESULT].as_rel_any,
}


def option_for(option_name: argument.OptionName, argument_name: str = None) -> argument.Option:
    return argument.Option(option_name, argument_name)
