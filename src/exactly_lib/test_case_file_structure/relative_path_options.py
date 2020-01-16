from exactly_lib.definitions import path as path_texts
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.definitions.doc_format import syntax_text
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity import conf_params as cp
from exactly_lib.definitions.entity.conf_params import ConfigurationParameterInfo
from exactly_lib.symbol import symbol_syntax
from exactly_lib.test_case_file_structure import relativity_root
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType, RelNonHdsOptionType, \
    RelHdsOptionType
from exactly_lib.test_case_file_structure.relativity_root import RelOptionType, RelRootResolver, \
    RelHdsRootResolver
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
    def directory_name(self) -> str:
        raise ValueError('There is no directory that corresponds to this option: ' + self.option_name_text.value)

    @property
    def directory_symbol_name_text(self) -> StringText:
        return syntax_text(self.directory_name)


class RelOptionInfoCorrespondingToTcDir(RelOptionInfo):
    def __init__(self,
                 directory_symbol_name: str,
                 option_name: argument.OptionName,
                 root_resolver: RelHdsRootResolver,
                 informative_name: str):
        super().__init__(option_name,
                         root_resolver,
                         informative_name)
        self._directory_name = directory_symbol_name

    @property
    def directory_name(self) -> str:
        return self._directory_name

    @property
    def directory_symbol_reference(self) -> str:
        return symbol_syntax.symbol_reference_syntax_for_name(self._directory_name)


class RelHdsOptionInfo(RelOptionInfoCorrespondingToTcDir):
    def __init__(self,
                 directory_name: str,
                 option_name: argument.OptionName,
                 root_resolver: RelHdsRootResolver,
                 cross_ref_info: ConfigurationParameterInfo,
                 informative_name: str):
        super().__init__(directory_name,
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


class RelNonHdsOptionInfo(RelOptionInfo):
    pass


class RelCurrentDirectoryOptionInfo(RelOptionInfo):
    def __init__(self):
        super().__init__(
            path_texts.REL_CWD_OPTION_NAME,
            relativity_root.resolver_for_cwd,
            path_texts.RELATIVITY_DESCRIPTION_CWD)

    @property
    def cross_ref_info(self) -> SingularAndPluralNameAndCrossReferenceId:
        return concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO


class RelSdsOptionInfo(RelNonHdsOptionInfo, RelOptionInfoCorrespondingToTcDir):
    pass


REL_CWD_INFO = RelCurrentDirectoryOptionInfo()

REL_SDS_RESULT_INFO = RelSdsOptionInfo(path_texts.EXACTLY_DIR__REL_RESULT, path_texts.REL_RESULT_OPTION_NAME,
                                       relativity_root.resolver_for_result,
                                       path_texts.RELATIVITY_DESCRIPTION_RESULT)

REL_SDS_TMP_INFO = RelSdsOptionInfo(path_texts.EXACTLY_DIR__REL_TMP, path_texts.REL_TMP_OPTION_NAME,
                                    relativity_root.resolver_for_tmp_user, path_texts.RELATIVITY_DESCRIPTION_TMP)

REL_SDS_ACT_INFO = RelSdsOptionInfo(path_texts.EXACTLY_DIR__REL_ACT, path_texts.REL_ACT_OPTION_NAME,
                                    relativity_root.resolver_for_act, path_texts.RELATIVITY_DESCRIPTION_ACT)

REL_HDS_ACT_INFO = RelHdsOptionInfo(path_texts.EXACTLY_DIR__REL_HDS_ACT,
                                    path_texts.REL_HDS_ACT_OPTION_NAME,
                                    relativity_root.resolver_for_hds_act,
                                    cp.HDS_ACT_DIRECTORY_CONF_PARAM_INFO,
                                    path_texts.RELATIVITY_DESCRIPTION_HDS_ACT)

REL_HDS_CASE_INFO = RelHdsOptionInfo(path_texts.EXACTLY_DIR__REL_HDS_CASE,
                                     path_texts.REL_HDS_CASE_OPTION_NAME,
                                     relativity_root.resolver_for_hds_case,
                                     cp.HDS_CASE_DIRECTORY_CONF_PARAM_INFO,
                                     path_texts.RELATIVITY_DESCRIPTION_HDS_CASE)

REL_HDS_OPTIONS_MAP = {
    RelHdsOptionType.REL_HDS_CASE: REL_HDS_CASE_INFO,
    RelHdsOptionType.REL_HDS_ACT: REL_HDS_ACT_INFO,
}

REL_SDS_OPTIONS_MAP = {
    RelSdsOptionType.REL_ACT: REL_SDS_ACT_INFO,

    RelSdsOptionType.REL_TMP: REL_SDS_TMP_INFO,

    RelSdsOptionType.REL_RESULT: REL_SDS_RESULT_INFO,
}

REL_NON_HDS_OPTIONS_MAP = {
    RelNonHdsOptionType.REL_CWD: REL_CWD_INFO,

    RelNonHdsOptionType.REL_ACT: REL_SDS_OPTIONS_MAP[RelSdsOptionType.REL_ACT],

    RelNonHdsOptionType.REL_TMP: REL_SDS_OPTIONS_MAP[RelSdsOptionType.REL_TMP],

    RelNonHdsOptionType.REL_RESULT: REL_SDS_OPTIONS_MAP[RelSdsOptionType.REL_RESULT],
}

REL_OPTIONS_MAP = {
    RelOptionType.REL_HDS_CASE: REL_HDS_OPTIONS_MAP[RelHdsOptionType.REL_HDS_CASE],

    RelOptionType.REL_HDS_ACT: REL_HDS_OPTIONS_MAP[RelHdsOptionType.REL_HDS_ACT],

    RelOptionType.REL_CWD: REL_NON_HDS_OPTIONS_MAP[RelNonHdsOptionType.REL_CWD],

    RelOptionType.REL_ACT: REL_NON_HDS_OPTIONS_MAP[RelNonHdsOptionType.REL_ACT],

    RelOptionType.REL_TMP: REL_NON_HDS_OPTIONS_MAP[RelNonHdsOptionType.REL_TMP],

    RelOptionType.REL_RESULT: REL_NON_HDS_OPTIONS_MAP[RelNonHdsOptionType.REL_RESULT],
}


def option_for(option_name: argument.OptionName, argument_name: str = None) -> argument.Option:
    return argument.Option(option_name, argument_name)
