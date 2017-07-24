from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType


def relativity_configuration_of_action_to_check(argument_syntax_name: str) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(
        RelOptionsConfiguration(
            PathRelativityVariants({RelOptionType.REL_HOME},
                                   absolute=True),
            is_rel_symbol_option_accepted=False,
            default_option=RelOptionType.REL_HOME),
        argument_syntax_name=argument_syntax_name,
        path_suffix_is_required=True
    )
