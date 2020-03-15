from exactly_lib.definitions import instruction_arguments
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionsConfiguration, \
    RelOptionArgumentConfiguration

ALL_REL_OPTIONS = set(RelOptionType) - {RelOptionType.REL_RESULT}

ALL_REL_OPTION_VARIANTS = PathRelativityVariants(ALL_REL_OPTIONS, True)

ALL_REL_OPTIONS_WITH_TARGETS_INSIDE_SANDBOX = ALL_REL_OPTIONS - {RelOptionType.REL_HDS_CASE}

ALL_REL_OPTION_VARIANTS_WITH_TARGETS_INSIDE_SANDBOX = PathRelativityVariants(
    ALL_REL_OPTIONS_WITH_TARGETS_INSIDE_SANDBOX,
    False)

ALL_REL_OPTION_VARIANTS_WITH_TARGETS_INSIDE_SANDBOX_OR_ABSOLUTE = PathRelativityVariants(
    ALL_REL_OPTIONS_WITH_TARGETS_INSIDE_SANDBOX,
    True)

REL_OPTIONS_CONFIGURATION = RelOptionsConfiguration(PathRelativityVariants(ALL_REL_OPTIONS,
                                                                           True),
                                                    RelOptionType.REL_HDS_CASE)


def all_rel_options_config(argument_syntax_name: str,
                           path_suffix_is_required: bool = True) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(REL_OPTIONS_CONFIGURATION,
                                          argument_syntax_name,
                                          path_suffix_is_required)


ALL_REL_OPTIONS_CONFIG = all_rel_options_config(instruction_arguments.PATH_SYNTAX_ELEMENT_NAME)

STANDARD_NON_HDS_RELATIVITY_VARIANTS = PathRelativityVariants(
    ALL_REL_OPTIONS - {RelOptionType.REL_HDS_CASE},
    True)

STANDARD_NON_HDS_OPTIONS = RelOptionsConfiguration(STANDARD_NON_HDS_RELATIVITY_VARIANTS,
                                                   RelOptionType.REL_CWD)


def non_hds_config(argument_syntax_name: str,
                   path_suffix_is_required: bool = True) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(STANDARD_NON_HDS_OPTIONS,
                                          argument_syntax_name,
                                          path_suffix_is_required)


NON_HDS_CONFIG = non_hds_config(instruction_arguments.PATH_SYNTAX_ELEMENT_NAME)
