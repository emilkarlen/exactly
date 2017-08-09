from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.test_case_utils.parse.shell_syntax import SHELL_KEYWORD

SHELL_COMMAND_MARKER = SHELL_KEYWORD


def relativity_configuration_of_action_to_check(argument_syntax_name: str) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(
        RelOptionsConfiguration(
            PathRelativityVariants({RelOptionType.REL_HOME_ACT},
                                   absolute=True),
            default_option=RelOptionType.REL_HOME_ACT),
        argument_syntax_name=argument_syntax_name,
        path_suffix_is_required=True
    )
