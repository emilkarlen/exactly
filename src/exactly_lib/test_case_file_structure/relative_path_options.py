from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.help_texts.doc_format import syntax_text
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.entity import conf_params as cp
from exactly_lib.help_texts.entity.conf_params import ConfigurationParameterInfo
from exactly_lib.test_case_file_structure import relativity_root
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType, RelNonHomeOptionType, \
    RelHomeOptionType
from exactly_lib.test_case_file_structure.relativity_root import RelOptionType, RelRootResolver, \
    RelHomeRootResolver
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.textformat.structure.core import StringText


class RelOptionInfo:
    def __init__(self,
                 option_name: argument.OptionName,
                 root_resolver: RelRootResolver,
                 informative_name: str):
        self._option_name = option_name
        self._root_resolver = root_resolver
        self._informative_name = informative_name

    @property
    def option_name(self) -> argument.OptionName:
        return self._option_name

    @property
    def option_name_text(self) -> StringText:
        return syntax_text(option_syntax(self._option_name))

    @property
    def root_resolver(self) -> RelRootResolver:
        return self._root_resolver

    @property
    def informative_name(self) -> str:
        return self._informative_name

    @property
    def directory_variable_name(self) -> str:
        raise ValueError('There is no directory that corresponds to this option: ' + self.option_name_text.value)

    @property
    def directory_variable_name_text(self) -> StringText:
        return syntax_text(self.directory_variable_name)


class RelOptionInfoCorrespondingToTcDir(RelOptionInfo):
    def __init__(self,
                 directory_variable_name: str,
                 option_name: argument.OptionName,
                 root_resolver: RelHomeRootResolver,
                 informative_name: str):
        super().__init__(option_name,
                         root_resolver,
                         informative_name)
        self._directory_name = directory_variable_name

    @property
    def directory_variable_name(self) -> str:
        return self._directory_name


class RelHomeOptionInfo(RelOptionInfoCorrespondingToTcDir):
    def __init__(self,
                 directory_variable_name: str,
                 option_name: argument.OptionName,
                 root_resolver: RelHomeRootResolver,
                 cross_ref_info: ConfigurationParameterInfo,
                 informative_name: str):
        super().__init__(directory_variable_name,
                         option_name,
                         root_resolver,
                         informative_name)
        self._cross_ref_info = cross_ref_info
        self._configuration_parameter_name = cross_ref_info.configuration_parameter_name

    @property
    def conf_param_info(self) -> ConfigurationParameterInfo:
        return self._cross_ref_info

    @property
    def configuration_parameter_name(self) -> str:
        return self._configuration_parameter_name


class RelNonHomeOptionInfo(RelOptionInfo):
    pass


class RelCurrentDirectoryOptionInfo(RelOptionInfo):
    def __init__(self):
        super().__init__(
            file_ref_texts.REL_CWD_OPTION_NAME,
            relativity_root.resolver_for_cwd,
            file_ref_texts.RELATIVITY_DESCRIPTION_CWD)

    @property
    def cross_ref_info(self) -> SingularAndPluralNameAndCrossReferenceId:
        return concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO


class RelSdsOptionInfo(RelNonHomeOptionInfo, RelOptionInfoCorrespondingToTcDir):
    pass


REL_CWD_INFO = RelCurrentDirectoryOptionInfo()

REL_SDS_RESULT_INFO = RelSdsOptionInfo(file_ref_texts.EXACTLY_DIR__REL_RESULT, file_ref_texts.REL_RESULT_OPTION_NAME,
                                       relativity_root.resolver_for_result,
                                       file_ref_texts.RELATIVITY_DESCRIPTION_RESULT)

REL_SDS_TMP_INFO = RelSdsOptionInfo(file_ref_texts.EXACTLY_DIR__REL_TMP, file_ref_texts.REL_TMP_OPTION_NAME,
                                    relativity_root.resolver_for_tmp_user, file_ref_texts.RELATIVITY_DESCRIPTION_TMP)

REL_SDS_ACT_INFO = RelSdsOptionInfo(file_ref_texts.EXACTLY_DIR__REL_ACT, file_ref_texts.REL_ACT_OPTION_NAME,
                                    relativity_root.resolver_for_act, file_ref_texts.RELATIVITY_DESCRIPTION_ACT)

REL_HOME_ACT_INFO = RelHomeOptionInfo(file_ref_texts.EXACTLY_DIR__REL_HOME_ACT,
                                      file_ref_texts.REL_HOME_ACT_OPTION_NAME,
                                      relativity_root.resolver_for_home_act,
                                      cp.HOME_ACT_DIRECTORY_CONF_PARAM_INFO,
                                      file_ref_texts.RELATIVITY_DESCRIPTION_HOME_ACT)

REL_HOME_CASE_INFO = RelHomeOptionInfo(file_ref_texts.EXACTLY_DIR__REL_HOME_CASE,
                                       file_ref_texts.REL_HOME_CASE_OPTION_NAME,
                                       relativity_root.resolver_for_home_case,
                                       cp.HOME_CASE_DIRECTORY_CONF_PARAM_INFO,
                                       file_ref_texts.RELATIVITY_DESCRIPTION_HOME_CASE)

REL_HOME_OPTIONS_MAP = {
    RelHomeOptionType.REL_HOME_CASE: REL_HOME_CASE_INFO,
    RelHomeOptionType.REL_HOME_ACT: REL_HOME_ACT_INFO,
}

REL_SDS_OPTIONS_MAP = {
    RelSdsOptionType.REL_ACT: REL_SDS_ACT_INFO,

    RelSdsOptionType.REL_TMP: REL_SDS_TMP_INFO,

    RelSdsOptionType.REL_RESULT: REL_SDS_RESULT_INFO,
}

REL_NON_HOME_OPTIONS_MAP = {
    RelNonHomeOptionType.REL_CWD: REL_CWD_INFO,

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
