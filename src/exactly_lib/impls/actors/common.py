from exactly_lib.impls.types.parse.shell_syntax import SHELL_KEYWORD
from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.tcfs.path_relativity import PathRelativityVariants, RelOptionType

SHELL_COMMAND_MARKER = SHELL_KEYWORD

REL_OPTIONS_CONFIGURATION = RelOptionsConfiguration(
    PathRelativityVariants(
        {RelOptionType.REL_HDS_CASE,
         RelOptionType.REL_HDS_ACT,
         RelOptionType.REL_ACT,
         RelOptionType.REL_TMP,
         RelOptionType.REL_CWD,
         },
        absolute=True),
    default_option=RelOptionType.REL_HDS_ACT
)


def relativity_configuration_of_action_to_check(argument_syntax_name: str) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(
        REL_OPTIONS_CONFIGURATION,
        argument_syntax_name=argument_syntax_name,
        path_suffix_is_required=True
    )
